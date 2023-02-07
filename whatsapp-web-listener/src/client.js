const AWS = require('aws-sdk')
const { Client, LocalAuth } = require('whatsapp-web.js')
const qrcode = require('qrcode')
const fs = require('fs-extra')
const { getEnv, sendEmail, getEnvOrDefault } = require('./utils')
const pino = require('pino')()
const { setIntervalAsync, clearIntervalAsync } = require('set-interval-async')

const ONE_HOUR = 3600000
class WhatsAppClient {
  constructor () {
    this.intervalId = null

    this.sns = new AWS.SNS()
    this.ses = new AWS.SES()
    this.s3 = new AWS.S3()
  }

  async startListening () {
    this.qrBucketName = getEnv('QR_BUCKET_NAME')
    this.sendMailTo = getEnvOrDefault('SEND_QR_TO', null)
    this.sendMessageToSNSARN = getEnv('WHATAPP_SNS_TOPIC_ARN')
    this.efsPath = getEnv('PERSISTANCE_STORAGE_MOUNT_POINT')
    this.linkUrl = getEnv('URL_IN_MAIL')

    try {
      await fs.ensureDir(`${this.efsPath}/local_auth`, 775)
      await fs.copy(`${this.efsPath}/local_auth`, './local_auth')
    } catch (err) {
      pino.error(
        `Unable to copy efs cache dir, if it's the first run, then this error is valid. ERR - ${err.message}`
      )
    }
    this.client = new Client({
      puppeteer: {
        args: ['--no-sandbox']
      },
      authStrategy: new LocalAuth('./local_auth')
    })

    this.client.on('qr', this.onQr.bind(this))
    this.client.on('ready', this.onReady.bind(this))
    this.client.on('message', this.onMessage.bind(this))

    pino.info('Starting')

    this.client.initialize()
  }

  async onQr (qr) {
    pino.info('QR code generated.')
    await qrcode.toFile('./file.png', qr, async (qrcode) => {
      const qrImageFile = fs.createReadStream('./file.png')
      const params = {
        Bucket: this.qrBucketName,
        Key: 'qr.png',
        Body: qrImageFile
      }
      await this.s3.upload(params).promise()
      pino.info('Uploaded QR code')
      if (this.intervalId === null) {
        await this.asyncSendMail(
          this.ses,
          this.sendMailTo,
          this.sendMailTo,
          this.linkUrl
        )
        this.intervalId = setIntervalAsync(async () => {
          await this.asyncSendMail(
            this.ses,
            this.sendMailTo,
            this.sendMailTo,
            this.linkUrl
          )
        }, ONE_HOUR)
      } else {
        pino.info('Email sent, skipping')
      }
    })
  }

  async onReady () {
    try {
      await fs.copy('./local_auth', `${this.efsPath}/local_auth`)
    } catch (err) {
      pino.error(
        `Unable to copy local cache  to efs, ignoring. ERR - ${err.message}`
      )
    }
    if (this.intervalId !== null) {
      clearIntervalAsync(this.intervalId)
    }
    pino.info('Client is ready!')
  }

  async onMessage (message) {
    try {
      const chat = await message.getChat()
      const contact = await message.getContact()
      message = {
        group_name: chat.name,
        group_id: chat.id.user,
        time: message.timestamp,
        participant_id: contact.id.user,
        participant_handle: contact.pushname,
        participant_number: contact.number,
        participant_contact_name: contact.name,
        message: message.body
      }

      pino.info(message)

      await this.sns
        .publish({
          TopicArn: this.sendMessageToSNSARN,
          Message: JSON.stringify(message)
        })
        .promise()
    } catch (error) {
      pino.error(error)
    }
  }

  async asyncSendMail (ses, source, to, imageUrl) {
    if (source === null) {
      pino.info('Email is not configured. Skipping...')
      return
    }
    try {
      await sendEmail(ses, source, to, imageUrl)
      pino.info(`Sent email with QR details to ${to}`)
    } catch (err) {
      pino.error(`Failed sending QR email. ERR - ${err.message}`)
    }
  }
}

module.exports = WhatsAppClient
