"""
Relay incoming SNS messages to Microsoft Teams webhooks
See https://github.com/CU-CommunityApps/cu-aws-cloudformation/tree/main/sns-teams-relay
"""
import os
import urllib3
import json
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

http = urllib3.PoolManager()
webhook_url_normal = os.environ['WEBHOOK_URL_NORMAL']
webhook_url_alert = os.environ['WEBHOOK_URL_ALERT']
strftime_format = os.environ.get('STRFTIME_FORMAT', '%Y-%m-%d %H:%M UTC')

# If an alarm comes from these topics, use the "normal" teams webhook.
alarm_sns_topics_normal = os.environ.get('ALARM_SNS_TOPICS_NORMAL', None)
alarm_sns_topics_normal = [] if not alarm_sns_topics_normal else alarm_sns_topics_normal.split(',')

# If an alarm comes from these topics, use the "alert" teams webhook.
alarm_sns_topics_alert = os.environ.get('ALARM_SNS_TOPICS_ALERT', None)
alarm_sns_topics_alert = [] if not alarm_sns_topics_alert else alarm_sns_topics_alert.split(',')

# If an unclassified message comes from these topics, use the "normal" teams webhook.
generic_sns_topics_normal = os.environ.get('GENERIC_SNS_TOPICS_NORMAL', None)
generic_sns_topics_normal = [] if not generic_sns_topics_normal else generic_sns_topics_normal.split(',')

# If an unclassified message comes from these topics, use the "alert" teams webhook.
generic_sns_topics_alert = os.environ.get('GENERIC_SNS_TOPICS_ALERT', None)
generic_sns_topics_alert = [] if not generic_sns_topics_alert else generic_sns_topics_alert.split(',')

# Contextual colors
info_color = '1919ff'
failure_color = 'b20000'
success_color = '007300'
warning_color = 'ffcc00'
default_color = info_color

# Map STATES/STATUS/CODES to colors and urls based

alarm_state_map = {
    "OK": {"color": success_color, "url": webhook_url_normal},
    "ALARM": {"color": failure_color, "url": webhook_url_alert},
    "INSUFFICIENT_DATA": {"color": warning_color, "url": webhook_url_normal},
}

codebuild_build_state_map = {
    "IN_PROGRESS": {"color": info_color, "url": webhook_url_normal},
    "SUCCEEDED": {"color": success_color, "url": webhook_url_normal},
    "FAILED": {"color": failure_color, "url": webhook_url_alert},
    "STOPPED": {"color": warning_color, "url": webhook_url_normal},
}

codebuild_build_phase_map = {
    "TIMED_OUT": {"color": failure_color, "url": webhook_url_alert},
    "STOPPED": {"color": warning_color, "url": webhook_url_normal},
    "FAILED": {"color": failure_color, "url": webhook_url_alert},
    "SUCCEEDED": {"color": success_color, "url": webhook_url_normal},
    "FAULT": {"color": failure_color, "url": webhook_url_alert},
    "CLIENT_ERROR": {"color": failure_color, "url": webhook_url_alert},
}

codepipeline_pipeline_execution_state_map = {
    "CANCELED": {"color": warning_color, "url": webhook_url_normal},
    "FAILED": {"color": failure_color, "url": webhook_url_alert},
    "RESUMED": {"color": info_color, "url": webhook_url_normal},
    "STARTED": {"color": info_color, "url": webhook_url_normal},
    "STOPPED": {"color": warning_color, "url": webhook_url_normal},
    "STOPPING": {"color": warning_color, "url": webhook_url_normal},
    "SUCCEEDED": {"color": success_color, "url": webhook_url_normal},
    "SUPERSEDED": {"color": warning_color, "url": webhook_url_normal},
}

codepipeline_action_execution_state_map = {
    "ABANDONED": {"color": warning_color, "url": webhook_url_normal},
    "CANCELED": {"color": warning_color, "url": webhook_url_normal},
    "FAILED": {"color": failure_color, "url": webhook_url_alert},
    "STARTED": {"color": info_color, "url": webhook_url_normal},
    "SUCCEEDED": {"color": success_color, "url": webhook_url_normal},
}

def handler(event, context):
    logger.debug("Received event: " + json.dumps(event, indent=2))
    message = event['Records'][0]['Sns']['Message']
    topic_arn = event['Records'][0]['Sns']['TopicArn']

    try:
        data = json.loads(message)
    except ValueError:
        # not valid JSON
        data = {}

    msg_type = data.get('detailType', None)
    is_approval = "approval" in data
    is_alarm = data.get('AlarmName',None) != None

    if is_alarm:
        msg, url = handle_alarm(data, topic_arn)
    elif is_approval:
        msg, url = handle_codepipeline_approval(data, event)
    elif msg_type == "CodeBuild Build State Change":
        msg, url = handle_codebuild_build_state_change(data)
    elif msg_type == "CodeBuild Build Phase Change":
        msg, url = handle_codebuild_build_phase_change(data)
    elif msg_type == "CodePipeline Pipeline Execution State Change":
        msg, url = handle_codepipeline_pipeline_execution_state_change(data)
    elif msg_type == "CodePipeline Action Execution State Change":
        msg, url = handle_codepipeline_action_execution_state_change(data)
    else:
        msg, url = handle_unknown_event(event, topic_arn, context)

    encoded_msg = json.dumps(msg).encode('utf-8')
    logger.info("Sending message:")
    logger.info(encoded_msg)
    resp = http.request('POST', url, body=encoded_msg)

    logger.info("Response:")
    logger.info({
        "status_code": resp.status,
        "response": resp.data
    })
    return None

def utc_timestamp_to_human_readable(timestamp):
    """
    Converts 'StateChangeTime' field from Alarms to something more human readable
    """
    utc_dt = datetime.fromisoformat(timestamp.split(".", 1)[0])
    return utc_dt.strftime(strftime_format)

def get_alarm_webhook_url(topic_arn, state):
    if topic_arn in alarm_sns_topics_alert:
        return webhook_url_alert
    if topic_arn in alarm_sns_topics_normal:
        return webhook_url_normal
    return alarm_state_map[state]['url']

def get_generic_webhook_url(topic_arn):
    if topic_arn in generic_sns_topics_alert:
        return webhook_url_alert
    if topic_arn in generic_sns_topics_normal:
        return webhook_url_normal
    return webhook_url_normal

def handle_alarm(data, topic_arn):
    account_id = data['AWSAccountId']
    alarm_name = data['AlarmName']
    alarm_arn = data['AlarmArn']
    new_state = data['NewStateValue']
    region = alarm_arn.split(':')[3]
    alarm_url = f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#alarmsV2:alarm/{alarm_name}"
    utc_dt_str = utc_timestamp_to_human_readable(data['StateChangeTime'])

    summary = f"AWS Alarm | {region} | {data['AWSAccountId']}"
    text = (
        f"<b>Alarm:</b> <b><a href='{alarm_url}'>{alarm_name}</a></b><br />"
        f"<b>Description:</b> {data['AlarmDescription']}<br />"
        f"<b>Current state:</b> {new_state} (was {data['OldStateValue']})<br />"
        f"<b>Reason:</b> {data['NewStateReason']}<br />"
        f"<b>Timestamp:</b> {utc_dt_str}<br />"
    )
    return {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": summary,
        "themeColor": alarm_state_map[new_state]['color'],
        "text": text,
        "title": summary,
        "potentialAction": []
    }, get_alarm_webhook_url(topic_arn, new_state)

def handle_unknown_event(event, topic_arn, context):
    sns_message = event['Records'][0]['Sns']['Message']
    sns_subject = event['Records'][0]['Sns']['Subject']
    summary = f"AWS SNS Teams Relay: {sns_subject}"
    return {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": summary,
        "themeColor": default_color,
        # The \n\n<br /> tries to ensure that the "Relayed" message starts on a new line.
        "text": f"{sns_message}\n\n<br />Relayed by {context.invoked_function_arn}",
        "title": summary,
        "potentialAction": []
    }, get_generic_webhook_url(topic_arn)

def handle_codepipeline_approval(data, event):
    summary = event['Records'][0]['Sns'].get('Subject', "SUBJECT_IS_MISSING")
    account = event['Records'][0]['Sns']['TopicArn'].split(":")[4]
    approval = data['approval']
    text = (
        f"AWS CodePipeline Approval | {data['region']} | {account}<br />"
        f"Pipeline <b><a href=\"{data['consoleLink']}\">{approval['pipelineName']}</a></b><br />"
        f"Stage name <b>{approval['stageName']}</b><br />"
        f"Action name <b>{approval['actionName']}</b><br />"
        f"<b><a href=\"{approval['approvalReviewLink']}\">Approve or Reject</a></b>"
    )
    return {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": summary,
        "themeColor": warning_color,
        "text": text,
        "title": summary,
        "potentialAction": []
    }, webhook_url_normal


def handle_codebuild_build_state_change(data):
    detail = data['detail']
    logs_url = get_logs_url(detail)
    summary = f"AWS CodeBuild Notification | {data['region']} | {data['account']}"
    text = (
        f"Project <b>{detail['project-name']}</b> (<a href=\"{logs_url}\">logs</a>)<br />"
        f"CodeBuild build state <b>{detail['build-status']}</b><br />"
    )
    return {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": summary,
        "themeColor": codebuild_build_state_map[detail['build-status']]['color'],
        "text": text,
        "title": summary,
        "potentialAction": []
    }, codebuild_build_state_map[detail['build-status']]['url']


def handle_codebuild_build_phase_change(data):
    detail = data['detail']
    logs_url = get_logs_url(detail)
    summary = f"AWS CodeBuild Notification | {data['region']} | {data['account']}"
    text = (
        f"Project <b>{detail['project-name']}</b> (<a href=\"{logs_url}\">logs</a>)<br />"
        f"CodeBuild phase <b>{detail['completed-phase']}</b><br />"
        f"Codebuild status <b>{detail['completed-phase-status']}</b>"
    )
    return {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": summary,
        "themeColor": codebuild_build_phase_map[detail['completed-phase-status']]['color'],
        "text": text,
        "title": summary,
        "potentialAction": []
    }, codebuild_build_phase_map[detail['completed-phase-status']]['url']


def get_logs_url(detail):
    return detail.get('additional-information', {}).get('logs', {}).get('deep-link', '#')


def handle_codepipeline_pipeline_execution_state_change(data):
    detail = data['detail']
    summary = f"AWS CodePipeline Notification | {data['region']} | {data['account']}"
    text = (
        f"Pipeline <b>{detail['pipeline']}</b><br />"
        f"CodePipeline state <b>{detail['state']}</b><br />"
    )
    return {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": summary,
        "themeColor": codepipeline_pipeline_execution_state_map[detail['state']]['color'],
        "text": text,
        "title": summary,
        "potentialAction": []
    }, codepipeline_pipeline_execution_state_map[detail['state']]['url']


def handle_codepipeline_action_execution_state_change(data):
    detail = data['detail']
    summary = f"AWS CodePipeline Notification | {data['region']} | {data['account']}"
    text = (
        f"Pipeline <b>{detail['pipeline']}</b><br />"
        f"CodePipeline stage <b>{detail['stage']}</b><br />"
        f"CodePipeline state <b>{detail['state']}</b>"
    )
    return {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": summary,
        "themeColor": codepipeline_action_execution_state_map[detail['state']]['color'],
        "text": text,
        "title": summary,
        "potentialAction": []
    }, codepipeline_action_execution_state_map[detail['state']]['url']
