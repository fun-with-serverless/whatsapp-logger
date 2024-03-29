const { PutObjectCommand } = require('@aws-sdk/client-s3')
const { Client, LocalAuth } = require('whatsapp-web.js')
const { PublishCommand } = require('@aws-sdk/client-sns')

const qrcode = require('qrcode')
const fs = require('fs-extra')
const { getEnv, sendStatusUpdate } = require('./utils')

const pino = require('pino')()

class WhatsAppClient {
  constructor ({ sns, s3, eventbridge, eventBridgeArn }) {
    this.intervalId = null

    this.sns = sns
    this.s3 = s3
    this.eventbridge = eventbridge
    this.eventBridgeArn = eventBridgeArn
  }

  async startListening () {
    this.qrBucketName = getEnv('QR_BUCKET_NAME')
    this.sendMessageToSNSARN = getEnv('WHATAPP_SNS_TOPIC_ARN')
    this.efsPath = getEnv('PERSISTANCE_STORAGE_MOUNT_POINT')
    this.efsCache = `${this.efsPath}/local_auth`

    try {
      await fs.ensureDir(this.efsCache, 775)
      await fs.copy(this.efsCache, './local_auth')
    } catch (err) {
      pino.error(
        `Unable to copy efs cache dir, if it's the first run, then this error is valid. ERR - ${err.message}`
      )
    }
    this.client = new Client({
      puppeteer: {
        args: ['--no-sandbox']
      },
      authStrategy: new LocalAuth({ dataPath: './local_auth' })
    })

    this.client.on('qr', this.onQr.bind(this))
    this.client.on('ready', this.onReady.bind(this))
    this.client.on('message', this.onMessage.bind(this))

    pino.info('Starting')

    this.client.initialize()
  }

  async sendMeMessage (message) {
    const meId = this.client.info.wid
    await this.client.sendMessage(`${meId.user}@${meId.server}`, message)
    pino.info('Message successfuly sent to self')
  }

  async sendGroupMessage (message, groupId) {
    await this.client.sendMessage(`${groupId}@g.us`, message)
    pino.info('Message successfuly sent to group')
  }

  async onQr (qr) {
    pino.info('QR code generated.')
    await sendStatusUpdate({
      eventbridge: this.eventbridge,
      eventbridgeArn: this.eventBridgeArn,
      detailsType: 'Disconnected'
    })
    await qrcode.toFile('./file.png', qr, async (qrcode) => {
      const qrImageFile = fs.createReadStream('./file.png')
      const command = new PutObjectCommand({
        Bucket: this.qrBucketName,
        Key: 'qr.png',
        Body: qrImageFile
      })
      await this.s3.send(command)
      pino.info('Uploaded QR code')
    })
  }

  async onReady () {
    await sendStatusUpdate({
      eventbridge: this.eventbridge,
      eventbridgeArn: this.eventBridgeArn,
      detailsType: 'Connected'
    })

    try {
      await fs.copy('./local_auth', `${this.efsPath}/local_auth`)
      pino.info('Copied')
    } catch (err) {
      pino.error(
        `Unable to copy local cache  to efs, ignoring. ERR - ${err.message}`
      )
    }

    pino.info('Client is ready!')
  }

  async onMessage (message) {
    try {
      pino.info(this.client.info.wid)
      pino.info(message.from)
      const chat = await message.getChat()
      const contact = await message.getContact()
      let quotedMessage = null
      let quotedMessageContactName = null
      let quotedParticipantHandle = null
      let quotedMessageTime = null
      if (message.hasQuotedMsg) {
        const quotedMessageObj = await message.getQuotedMessage()
        const quotedContact = await quotedMessageObj.getContact()
        quotedMessage = quotedMessageObj.body
        quotedMessageContactName = quotedContact.name
        quotedParticipantHandle = quotedContact.pushname
        quotedMessageTime = quotedMessageObj.timestamp
      }

      message = {
        group_name: chat.name,
        group_id: chat.id.user,
        time: message.timestamp,
        participant_id: contact.id.user,
        participant_handle: contact.pushname,
        participant_number: contact.number,
        participant_contact_name: contact.name,
        message: message.body,
        has_media: message.hasMedia,
        quoted_message: quotedMessage,
        quoted_message_participant_contact_name: quotedMessageContactName,
        quoted_message_participant_handle: quotedParticipantHandle,
        quoted_message_time: quotedMessageTime
      }
      pino.info(chat.id)
      pino.info(message)

      const command = new PublishCommand({
        TopicArn: this.sendMessageToSNSARN,
        Message: JSON.stringify(message)
      })

      await this.sns.send(command)
    } catch (error) {
      pino.error(error)
    }
  }

  async logout () {
    pino.info('Logging out')
    this.client.authStrategy.logout()
    this.client.destroy()
    fs.remove(this.efsCache)
    await sendStatusUpdate({
      eventbridge: this.eventbridge,
      eventbridgeArn: this.eventBridgeArn,
      detailsType: 'Disconnected'
    })
    this.startListening()
    pino.info('Logged out')
  }
}

module.exports = WhatsAppClient
