const pino = require('pino')()
const {
  ReceiveMessageCommand,
  DeleteMessageCommand
} = require('@aws-sdk/client-sqs')
const { PutEventsCommand } = require('@aws-sdk/client-eventbridge')

function getEnv (name) {
  const env = process.env[name]
  if (!env) {
    throw new Error(`Environment variable ${name} is not defined`)
  }
  return env
}

function getEnvOrDefault (name, defaultValue) {
  const env = process.env[name]
  if (!env) {
    return defaultValue
  }
  return env
}

/**
 * pollQueue
 *
 * @desc A function to poll messages from an SQS queue and execute events based on the message body.
 *
 * @param {string} queueUrl - The URL of the SQS queue to poll
 * @param {Object} sqsClient - The SQS client to use for making requests
 * @param {WhatsAppEventHandler} eventsExecuter - The object responsible for executing events based on the message body
 *
 *
 * @returns {void}
 */
const pollQueue = async (queueUrl, sqsClient, eventsExecuter) => {
  pino.info('Polling queue...')
  try {
    const receiveMessageCommand = new ReceiveMessageCommand({
      QueueUrl: queueUrl,
      MaxNumberOfMessages: 1,
      WaitTimeSeconds: 20,
      VisibilityTimeout: 20
    })
    const receiveMessageResponse = await sqsClient.send(receiveMessageCommand)

    if (receiveMessageResponse.Messages) {
      receiveMessageResponse.Messages.forEach(async (message) => {
        pino.info(`Received message: ${message.Body}`)
        const body = JSON.parse(message.Body)
        pino.info(body)
        eventsExecuter.handle(body)
        const deleteMessageCommand = new DeleteMessageCommand({
          QueueUrl: queueUrl,
          ReceiptHandle: message.ReceiptHandle
        })
        await sqsClient.send(deleteMessageCommand)
      })
    }
  } catch (err) {
    pino.error(`Unable to pull messages from queue. ERR - ${err.message}`)
  }
  const intervalId = setTimeout(async () => {
    await pollQueue(queueUrl, sqsClient, eventsExecuter)
  }, 60000)
  return intervalId
}

/**
 * Sends a status update to the AWS EventBridge.
 *
 * @param {Object} options - The options object.
 * @param {Object} options.eventbridge - The AWS EventBridge instance.
 * @param {string} options.eventbridgeArn - The ARN of the EventBridge.
 * @param {string} options.detailsType - The detail type of the status update.
 * @return {Promise} - Returns a Promise that resolves when the status update is sent to the AWS EventBridge.
 */
const sendStatusUpdate = async ({
  eventbridge,
  eventbridgeArn,
  detailsType
}) => {
  const command = new PutEventsCommand({
    Entries: [
      {
        EventBusName: eventbridgeArn,
        Source: 'whatsapp-client',
        DetailType: 'status-change',
        Detail: JSON.stringify({ status: detailsType })
      }
    ]
  })
  await eventbridge.send(command)
}

module.exports = {
  getEnv,
  getEnvOrDefault,
  pollQueue,
  sendStatusUpdate
}
