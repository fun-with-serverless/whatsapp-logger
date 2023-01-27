function getEnv(name) {
  const env = process.env[name];
  if (!env) {
    throw new Error(`Environment variable ${name} is not defined`);
  }
  return env;
}

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
              <p>Please approve the QR code <a href="${imageUrl}">by scanning this image</a></p>
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
  sendEmail,
};
