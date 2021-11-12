"""
Relay incoming SNS messages to Microsoft Teams webhooks
"""
import os
import urllib3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

http = urllib3.PoolManager()
webhook_url_normal = os.environ['WEBHOOK_URL_NORMAL']
webhook_url_alert = os.environ['WEBHOOK_URL_ALERT']

# Contextual colors
info_color = '1919ff'
failure_color = 'b20000'
success_color = '007300'
warning_color = 'ffcc00'
default_color = info_color

# Map STATES/STATUS/CODES to colors and urls based

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

    try:
        data = json.loads(message)
    except ValueError:
        # not valid JSON
        data = {}

    msg_type = data.get('detailType', None)
    is_approval = "approval" in data

    if is_approval:
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
        msg, url = handle_unknown_event(event, context)

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


def handle_unknown_event(event, context):
    sns_message = event['Records'][0]['Sns']['Message']
    sns_subject = event['Records'][0]['Sns']['Subject']
    summary = f"AWS SNS Teams Relay: {sns_subject}"
    return {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": summary,
        "themeColor": default_color,
        "text": f"Message: [{sns_message}]<br />Relayed by {context.invoked_function_arn}",
        "title": summary,
        "potentialAction": []
    }, webhook_url_normal


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
