const dotenv = require('dotenv')
const WhatsAppClient = require('./client')
const WhatsAppEventHandler = require('./eventsExecuter')
const { pollQueue, getEnv } = require('./utils')
const AWS = require('aws-sdk')

dotenv.config();

(async () => {
  const eventsURL = getEnv('SQS_EVENT_URL')
  const sqs = new AWS.SQS()
  const client = new WhatsAppClient()
  const eventsHandler = new WhatsAppEventHandler(client)
  pollQueue(eventsURL, sqs, eventsHandler)

  await client.startListening()
})()
