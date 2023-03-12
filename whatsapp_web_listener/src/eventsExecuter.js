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
          if (event.detail.send_to === 'Myself') {
            await this.whatsAppClient.sendMeMessage(
              `🏁 ${groupName} summary:\n${message}`
            )
          } else if (event.detail.send_to === 'Original_Group') {
            await this.whatsAppClient.sendGroupMessage(
              `🏁 ${groupName} summary:\n${message}`,
              event.detail.group_id
            )
          } else if (event.detail.send_to === 'Other') {
            await this.whatsAppClient.sendGroupMessage(
              `🏁 ${groupName} summary:\n${message}`,
              event.detail.send_to_group_id
            )
          } else {
            pino.error(`Invalid send_to option - ${event.detail.send_to}`)
          }
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
