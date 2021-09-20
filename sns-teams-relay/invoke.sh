#!/bin/bash
#
# Script to invoke the sns-teams-relay with a simulated SNS event.
# 
ENV=${ENV:-dev}

aws lambda invoke \
    --function-name sns-teams-relay-${ENV} \
    --payload file://sample-event.json \
    --log-type Tail \
    --cli-binary-format raw-in-base64-out \
    response.out.json