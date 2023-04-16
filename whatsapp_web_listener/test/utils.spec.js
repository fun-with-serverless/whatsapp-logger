const { pollQueue } = require('../src/utils')

const {
  ReceiveMessageCommand,
  DeleteMessageCommand
} = require('@aws-sdk/client-sqs')

jest.mock('@aws-sdk/client-sqs')

describe('pollQueue', () => {
  let sqsClient
  let eventsExecuter

  beforeEach(() => {
    // Mock dependencies
    sqsClient = {
      send: jest.fn()
    }
    eventsExecuter = {
      handle: jest.fn()
    }
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('should poll the queue, handle and delete the message', async () => {
    const queueUrl = 'https://test-queue-url.com'
    const messageBody = JSON.stringify({
      event: 'test-event',
      data: 'test-data'
    })

    // Set up mocked ReceiveMessageCommand response
    sqsClient.send.mockImplementationOnce((command) => {
      if (command instanceof ReceiveMessageCommand) {
        return Promise.resolve({
          Messages: [
            {
              Body: messageBody,
              ReceiptHandle: 'test-receipt-handle'
            }
          ]
        })
      } else {
        return Promise.reject(new Error('ReceiveMessageCommand error'))
      }
    })

    // Set up mocked DeleteMessageCommand response
    sqsClient.send.mockImplementationOnce((command) => {
      if (command instanceof DeleteMessageCommand) {
        return Promise.resolve()
      } else {
        return Promise.reject(new Error('DeleteMessageCommand error'))
      }
    })

    // Call pollQueue function
    const intervalId = await pollQueue(queueUrl, sqsClient, eventsExecuter)
    clearTimeout(intervalId)

    // Verify interactions
    expect(sqsClient.send).toHaveBeenCalledTimes(2)
    expect(eventsExecuter.handle).toHaveBeenCalledWith(JSON.parse(messageBody))
  })
})
