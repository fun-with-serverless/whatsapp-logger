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
        <li><a href="#testing">Testing</a></li>
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
    <img src="https://user-images.githubusercontent.com/110536677/216052857-23976f95-5846-4ea5-8cb8-0eeb2532c370.png" alt="Architecture diagram">
</div>

TBD

<!--
## Getting started
### Prerequisites
* Make sure your machine is ready to work with [AWS SAM](https://aws.amazon.com/serverless/sam/)

### Installation
* Clone this repository.
* Run `sam build` and then `sam deploy --guided`. Accept the default values, except for 
    * _Parameter Email - Send a reminder to this email. 


### Testing
* You can test the application manully by executing the `RemindMeFunction` Lambda directly from the console. It accepts a json with the following structure:
```
{
  "content": "Hello my friend",
  "when": "2022-11-12T23:20",
  "timezone": "Asia/Bangkok"
}
```
-->
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
- [ ] Write unit tests
- [ ] Create github actions
- [ ] Add observability
- [x] Use layers
- [ ] Improve container size
- [ ] Use cheap NAT in the VPC
