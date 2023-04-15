const dotenv = require('dotenv')
const WhatsAppClient = require('./client')
const WhatsAppEventHandler = require('./eventsExecuter')
const { pollQueue, getEnv } = require('./utils')
const AWS = require('aws-sdk')

dotenv.config();

(async () => {
  const eventsURL = getEnv('SQS_EVENT_URL')
  const eventBridgeArn = getEnv('EVENTBRIDGE_ARN')
  const sqs = new AWS.SQS()
  const sns = new AWS.SNS()
  const s3 = new AWS.S3()
  const eventbridge = new AWS.EventBridge()
  const client = new WhatsAppClient({ sns, s3, eventbridge, eventBridgeArn })
  const eventsHandler = new WhatsAppEventHandler(
    client,
    eventbridge,
    eventBridgeArn
  )
  pollQueue(eventsURL, sqs, eventsHandler)

  await client.startListening()
})()
