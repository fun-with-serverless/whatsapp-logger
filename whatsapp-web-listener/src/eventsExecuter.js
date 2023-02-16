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
