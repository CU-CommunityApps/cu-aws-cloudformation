"""
Relay incoming SNS messages to a Microsoft Teams webhook
"""
import os
import urllib3 
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

http = urllib3.PoolManager() 
url = os.environ['WEBHOOK_URL']

info_color = '1919ff'
# Contextual colors to be implemented later...
# failure_color = 'b20000'
# success_color = '007300'
# warning_color = 'ffcc00',
default_color = info_color

def handler(event, context):

  logger.debug("Received event: " + json.dumps(event, indent=2))
  message = event['Records'][0]['Sns']['Message']
  
  try:
    data = json.loads(message)
  except ValueError:
    # not valid JSON
    data = {}
  
  msg_type = data.get('detailType', 'UNKNOWN')
  
  if msg_type == "CodeBuild Build State Change":
    msg = handle_codebuild_state_change(data)
  elif msg_type == "CodeBuild Build Phase Change":
    msg = handle_codebuild_phase_change(data)
  else:
    msg = handle_unknown_event(event, context)
  
  encoded_msg = json.dumps(msg).encode('utf-8')
  logger.info("Sending message:")
  logger.info(encoded_msg)
  resp = http.request('POST',url, body=encoded_msg)
  
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
  }

def handle_codebuild_state_change(data):
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
      "themeColor": default_color,
      "text": text,
      "title": summary,
      "potentialAction": []        
  }

def handle_codebuild_phase_change(data):
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
      "themeColor": default_color,
      "text": text,
      "title": summary,
      "potentialAction": []        
  }

def get_logs_url(detail):
  return detail.get('additional-information', {}).get('logs',{}).get('deep-link', '#')