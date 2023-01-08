const AWS = require('aws-sdk')
const { Client, LocalAuth } = require('whatsapp-web.js')
const qrcode = require('qrcode-terminal')
const dotenv = require('dotenv')
const { getEnv } = require('./utils')

dotenv.config()

const client = new Client({
  puppeteer: {
    args: ['--no-sandbox']
  },
  authStrategy: new LocalAuth()
})

const s3 = new AWS.S3()
const QR_BUCKET_NAME = getEnv('QR_BUCKET_NAME')

client.on('qr', async (qr) => {
  qrcode.generate(qr, { small: true }, async (qrcode) => {
    const params = {
      Bucket: QR_BUCKET_NAME,
      Key: 'qr.txt',
      Body: qrcode
    }
    console.info('Uploading QR code to S3')
    await s3.putObject(params).promise()
  })
})

client.on('ready', async () => {
  console.log('Client is ready!')
})

client.on('message', async (message) => {
  try {
    const chat = await message.getChat()
    const date = new Date(message.timestamp * 1000)

    if (chat.isGroup) {
      console.log(`[${chat.name}]${date.toISOString()}:${message.author}:${message.body}`)
    } else {
      console.log(`[${chat.name}]${date.toISOString()}:${message.body}`)
    }
  } catch (error) {
    console.error(error)
  }
})

client.initialize()
