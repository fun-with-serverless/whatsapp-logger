function getEnv(name) {
  const env = process.env[name];
  if (!env) {
    throw new Error(`Environment variable ${name} is not defined`);
  }
  return env;
}

function getEnvOrDefault(name, defaultValue) {
  const env = process.env[name];
  if (!env) {
    return defaultValue
  }
  return env;
}

/**
 * Sends an email using the Amazon Simple Email Service (SES) client
 * 
 * @param {Object} ses - The Amazon SES client
 * @param {string} source - The email address the email will be sent from.
 * @param {string} to - The email address the email will be sent to
 * @param {string} imageUrl - The URL of an image to be included in the email
 * 
 */
const sendEmail = async (ses, source, to, imageUrl) => {
  // Create the email parameters
  const params = {
    Destination: {
      ToAddresses: [to],
    },
    Message: {
      Body: {
        Html: {
          Charset: "UTF-8",
          Data: `<html>
            <body>
              <p>Application is ready.<br/> <a href="${imageUrl}">Admin portal</a></p>
            </body>
          </html>`,
        },
      },
      Subject: {
        Charset: "UTF-8",
        Data: "Access WhatsApp QR code",
      },
    },
    Source: source,
  };

  // Send the email

  await ses.sendEmail(params).promise();
};

module.exports = {
  getEnv,
  getEnvOrDefault,
  sendEmail,
};
