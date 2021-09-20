"""
Relay incoming SNS messages to a Microsoft Teams webhook
"""
import os
import urllib3 
import json

http = urllib3.PoolManager() 
url = os.environ['WEBHOOK_URL']
def handler(event, context): 
    msg = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": event['Records'][0]['Sns']['Subject'],
        "themeColor": "17a2b8",
        "text": event['Records'][0]['Sns']['Message'],
        "title": event['Records'][0]['Sns']['Subject'],
        "potentialAction": []        
    }
    encoded_msg = json.dumps(msg).encode('utf-8')
    resp = http.request('POST',url, body=encoded_msg)
    print({
        "message": event['Records'][0]['Sns']['Message'], 
        "status_code": resp.status, 
        "response": resp.data
    })
