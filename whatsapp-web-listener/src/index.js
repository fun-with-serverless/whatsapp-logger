const dotenv = require("dotenv");
const WhatsAppClient = require("./client");

dotenv.config();

(async () => {
  const client = new WhatsAppClient();
  await client.startListening();
})();
