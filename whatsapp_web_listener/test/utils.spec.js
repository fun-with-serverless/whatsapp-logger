const {
  SQS
} = require('@aws-sdk/client-sqs')
const { pollQueue } = require('../src/utils')

describe('pollQueue', () => {
  let sqsClient
  let eventsExecuter

  beforeEach(() => {
    sqsClient = new SQS()
    sqsClient.receiveMessage = jest.fn().mockReturnValue({
      promise: jest.fn().mockResolvedValue({
        Messages: [
          {
            Body: JSON.stringify({
              event: 'logout'
            }),
            ReceiptHandle: 'test-receipt-handle'
          }
        ]
      })
    })
    sqsClient.deleteMessage = jest.fn().mockReturnValue({
      promise: jest.fn().mockResolvedValue()
    })
    eventsExecuter = {
      handle: jest.fn()
    }
  })

  afterEach(() => {
    jest.resetAllMocks()
  })

  it('should poll the queue and handle events', async () => {
    const intervalId = await pollQueue('queue-url', sqsClient, eventsExecuter)
    expect(sqsClient.receiveMessage).toHaveBeenCalledWith({
      QueueUrl: 'queue-url',
      MaxNumberOfMessages: 1,
      WaitTimeSeconds: 20,
      VisibilityTimeout: 20
    })
    expect(eventsExecuter.handle).toHaveBeenCalledWith({
      event: 'logout'
    })
    expect(sqsClient.deleteMessage).toHaveBeenCalledWith({
      QueueUrl: 'queue-url',
      ReceiptHandle: 'test-receipt-handle'
    })
    clearTimeout(intervalId)
  })

  it('should log an error if unable to pull messages from queue', async () => {
    sqsClient.receiveMessage.mockReturnValue({
      promise: jest.fn().mockRejectedValue(new Error('Unable to pull messages'))
    })
    const intervalId = await pollQueue('queue-url', sqsClient, eventsExecuter)
    expect(sqsClient.deleteMessage).not.toHaveBeenCalledWith({
      QueueUrl: 'queue-url',
      ReceiptHandle: 'test-receipt-handle'
    })
    clearTimeout(intervalId)
  })
})
