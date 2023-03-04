const pino = require('pino')()

class WhatsAppEventHandler {
  constructor (whatsAppClient) {
    this.whatsAppClient = whatsAppClient
  }

  async handle (event) {
    try {
      const detailsType = event['detail-type']
      switch (detailsType) {
        case 'logout':
          await this.whatsAppClient.logout()
          break
        case 'summary': {
          const message = event.detail.content
          const groupName = event.detail.group_name
          await this.whatsAppClient.sendMeMessage(
            `🏁 ${groupName} summary:\n${message}`
          )
          break
        }
        default:
          pino.error('Invalid option selected')
          break
      }
    } catch (err) {
      pino.error(
        `Failed to dispatch message. ERR - ${err.message}\n${err.stack}`
      )
    }
  }
}

module.exports = WhatsAppEventHandler
