[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

<!-- PROJECT LOGO -->
<br />
<div align="center">
    <img width="256" height="256" src="https://user-images.githubusercontent.com/110536677/216813972-ea76373f-bfaa-4875-bdfa-5c93bd91acb7.png" alt="A 3d art showing whatsapp application turning into small water drops that fall">

<h3 align="center">WhatsApp Group Manager</h3>

  <p align="center">
   Introducing a new application that helps you keep track of your WhatsApp group discussions. If you have several WhatsApp groups, you may sometimes find it challenging to keep up with the conversations and discussions, especially if you are a new member. This application solves this problem by saving the content of your WhatsApp groups in a Google Sheet.

With this application, new members can easily review previous discussions, even if they weren't a part of the group when the discussions took place. The Google Sheet acts as a database of all the discussions, allowing new members to search for relevant information using keywords or specific dates.

In the future, we plan to add daily summaries of the discussions, providing a quick and easy way to stay up-to-date on the latest happenings in your WhatsApp groups. Additionally, we will provide access to any media shared in the group, such as images, videos, and audio clips. With these features, you will have all the information you need at your fingertips, making it easier than ever to stay connected with your WhatsApp groups.
    <br />
    <br />
    <a href="https://github.com/aws-hebrew-book/reminders/issues">Report Bug</a>
    ·
    <a href="https://github.com/aws-hebrew-book/reminders/issues">Request Feature</a>
  </p>
</div>


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#high-level-architecture">High level architecture</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#logo">Logo</a></li>
  </ol>
</details>


## High level architecture

<div align="center">
    <img src="https://user-images.githubusercontent.com/110536677/217332241-6a4eb1f5-67bc-42bc-b88d-4e79f5eae935.png" alt="Architecture diagram">
</div>

TBD


## Getting started
### Prerequisites
* Make sure to have the [latest CDK version installed](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html#getting_started_install) (V2).
* An AWS enviornment.
* Python 3.9 (I highly recommend using [pyenv](https://github.com/pyenv/pyenv#installation)).
* [Python Poetry](https://python-poetry.org/docs/#installation)


### Installation
* Clone this repository.
* The application uses CDK as IaC framework. 
* Go to the cdk folder run `poetry install` to install relevant dependencies.
* Next run the `poetry poe deploy`. It will run the CDK deployment script. Approve the deployment of the various stacks. Sit tight, it will take a couple of minutes.
* When the installation is complete you should get two links - 1. to the admin dashboard and 2. to the admin password stored in AWS.
Picture
* Get the secret password, by going to the secret manager, scroll down and click `unhide`
* Go to the admin dashboard, the user name is `admin`and the password is the one you have copied.

### Setting up Google
* Create a new spreadsheet in google sheet.
* In case you want to save yur whatsapp chats into google sheets, you need to configure a google cloud account.
* Head to [Google Developers Console](https://console.cloud.google.com/apis/dashboard?project=serverless-demo-210412) and create a new project (or select the one you already have).
* In the box labeled "Search for APIs and Services", search for “Google Drive API” and enable it.
* In the box labeled "Search for APIs and Services", search for “Google Sheets API” and enable it.

Service account is a special type of Google account intended to represent a non-human user that needs to authenticate and be authorized to access data in Google APIs.

Since it’s a separate account, by default it does not have access to any spreadsheet until you share it with this account. Just like any other Google account.

Here’s how to get one:
* Enable API Access for a Project if you haven’t done it yet.
* Go to “APIs & Services > Credentials” and choose “Create credentials > Service account key”.
* Fill out the form
* Click “Create” and “Done”.
* Press “Manage service accounts” above Service Accounts.
* Press on ⋮ near recently created service account and select “Manage keys” and then click on “ADD KEY > Create new key”.
* Select JSON key type and press “Create”.
* You will automatically download a JSON file with credentials. It may look like this:
```
{
    "type": "service_account",
    "project_id": "api-project-XXX",
    "private_key_id": "2cd … ba4",
    "private_key": "-----BEGIN PRIVATE KEY-----\nNrDyLw … jINQh/9\n-----END PRIVATE KEY-----\n",
    "client_email": "473000000000-yoursisdifferent@developer.gserviceaccount.com",
    "client_id": "473 … hd.apps.googleusercontent.com",
    ...
}
```
* Remember the path to the downloaded credentials file. Also, in the next step you’ll need the value of client_email from this file.
* Very important! Go to your spreadsheet and share it with a client_email from the step above. Just like you do with any other Google account.
* Now go to the admin dashboard from the previous section.
* Paste the json into the `Google Secret` text box.
* Copy the the spreadsheet url you created in step one and paste it into the `Sheet URL` text box.
* Click save and you are done.

### Connecting WhatsApps
* Behind the scenes this application uses WhatsApp web to pull chat content.
* In order to connect to WhatsApp you need to scan a QR code with your **Real WhatsApp instance**, that is, the one that runs on a real phone.
* Pay attention this is experimental process, and WhatsApp may detect it as a bot and disconnect the number. It's better to use an expandible number.
* In the admin dashboard click on `Show QR code`, and scan the image with your WhatsApp app.
* You are good to go. See your spreadsheet gets updated.

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


<!-- LICENSE -->
## License

Distributed under the Apache License Version 2.0 License. See `LICENSE` for more information.

<!-- CONTACT -->
## Contact

Efi Merdler-Kravitz - [@TServerless](https://twitter.com/TServerless)



## Logo
The project's logo was created by Dall-E 2 with the following description _A hand drawn sketch of a sticky note floating on a cloud_


<p align="right">(<a href="#readme-top">back to top</a>)</p>



TODO:
- [ ] Write unit tests for whatsapp client
- [ ] Create github actions
- [ ] Add observability
- [x] Use layers
- [x] Write utests to lambda code
- [ ] Improve container size
- [ ] Use cheap NAT in the VPC
