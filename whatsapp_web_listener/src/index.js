const dotenv = require('dotenv')
const WhatsAppClient = require('./client')
const WhatsAppEventHandler = require('./eventsExecuter')
const { pollQueue, getEnv } = require('./utils')
const { EventBridge } = require('@aws-sdk/client-eventbridge')
const { S3 } = require('@aws-sdk/client-s3')
const { SNS } = require('@aws-sdk/client-sns')
const { SQS } = require('@aws-sdk/client-sqs')

dotenv.config();

(async () => {
  const eventsURL = getEnv('SQS_EVENT_URL')
  const eventBridgeArn = getEnv('EVENTBRIDGE_ARN')
  const sqs = new SQS()
  const sns = new SNS()
  const s3 = new S3()
  const eventbridge = new EventBridge()
  const client = new WhatsAppClient({ sns, s3, eventbridge, eventBridgeArn })
  const eventsHandler = new WhatsAppEventHandler(
    client,
    eventbridge,
    eventBridgeArn
  )
  pollQueue(eventsURL, sqs, eventsHandler)

  await client.startListening()
})()
