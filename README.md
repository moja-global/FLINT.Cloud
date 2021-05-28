# FLINT.Cloud
[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square)](#contributors)

The project aims to build a continuous deployment pipeline to offer FLINT as a SaaS over cloud. The project also aims to simplify the process of installation by supporting a single command or step installation process.

### Layered Architecture Setup on Google Cloud

#### Deploying

1. Create a service account with project owner permissions in your project. This is used by Terraform to provision all the necessary resources.
2. Copy `main.tf` from the `layered` directory of this repository to your Cloud Console machine.
3. In `main.tf`, change the `project` variable to your project ID. Change any other variables if necessary. 
4. Download the key for the service account created in step 1 (in JSON format) to your project's Cloud Console machine. Rename it as `service_account.json`.
5. Run `terraform apply`. After this command finishes, it should output the URL to FLINT Cloud (ingress).

#### Disabling

1. In the same directory as where `main.tf` is present, run `terraform destroy`. In case this fails, simply run it again.     

### Flask.example REST API Setup  

In order to run the REST API, please follow the following steps: - 

1. `docker build -t FLINT-api .`
2. `docker run --rm -p 8080:8080 FLINT-api`

Currently the REST API has the following endpoints available for access:-

- **\help\all**: This endpoint produces a help message with information on all options for moja.CLI.
- **\help\arg**: This endpoint produces a help message with information on option **arg** for moja.CLI.
- **\version**: This endpoint outputs the version number of moja.CLI.
- **\point**: This endpoint runs point example and outputs point_example.csv as an attachment to be downloaded. Parameters (multipart-form data) `file` for point_example can be passed to override the default configurations.
- **\rothc**: This endpoint runs rothc example and outputs point_rothc_example.csv as an attachment to be downloaded. Parameters (multipart-form data) `file` for rothc_example can be passed to override the default configurations.


This REST API is built using the `flask-restful` package and has been containerized using `Docker`.  

### Flask-GCBM REST API Setup  

In order to run the REST API, please follow the following steps: - 

1. `docker build --build-arg BUILD_TYPE=RELEASE --build-arg NUM_CPU=4 -t gcbm-api .`
2. `docker run -v /home/kalilinux/Documents/GCBM:/gcbm_files --rm -p 8080:8080 gcbm-api`
  

In the point 2 as you can see we have mounted the GCBM folder as gcbm_files onto our container. The zipped GCBM folder is available in the root of this repository for setup and use.  

Currently the REST API has the following endpoints available for access:-

- **\help\all**: This endpoint produces a help message with information on all options for moja.CLI.
- **\help\arg**: This endpoint produces a help message with information on option **arg** for moja.CLI.
- **\version**: This endpoint outputs the version number of moja.CLI.
- **\gcbm**: This endpoint runs flint-gcbm and outputs some files in the output directory along with the output db. Parameters (multipart-form data) `file` for gcbm_config and `input_db` for input sqlite db can be passed to override the default configurations.

This REST API is built using the `flask-restful` package and has been containerized using `Docker`.

## How to Get Involved?  

This project will be open for applications from Jan 30 to Feb 12, 2021 - please see the [LFX Mentorship Program proposal](https://mentorship.lfx.linuxfoundation.org/project/d70e1f9e-abde-403f-8389-52a122301500) to apply.

Feel free to [join our Slack community](https://join.slack.com/t/mojaglobal/shared_invite/zt-lf2290hy-CGqpUvHFfGsqoIZnO8MXKQ) and get to know everyone, or get help with your application.

If you would like to volunteer as a mentor, or for any other questions, please contact andrew@moja.global. We'd love to have you involved.

  
## FAQ and Other Questions  

* You can find FAQs on the [Wiki](https://github.com/moja.global/.github/wiki).  
* If you have a question about the code, submit [user feedback](https://github.com/moja-global/About-moja-global/blob/master/Contributing/How-to-Provide-User-Feedback.md) in the relevant repository  
* If you have a general question about a project or repository or moja global, [join moja global](https://github.com/moja-global/About-moja-global/blob/master/Contributing/How-to-Join-moja-global.md) and 
    * [submit a discussion](https://help.github.com/en/articles/about-team-discussions) to the project, repository or moja global [team](https://github.com/orgs/moja-global/teams)
    * [submit a message](https://get.slack.help/hc/en-us/categories/200111606#send-messages) to the relevant channel on [moja global's Slack workspace](mojaglobal.slack.com). 
* If you have other questions, please write to info@moja.global   
  

## Contributors

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore -->
<table><tr><td align="center"><a href="http://moja.global"><img src="https://avatars1.githubusercontent.com/u/19564969?v=4" width="100px;" alt="moja global"/><br /><sub><b>moja global</b></sub></a><br /><a href="#projectManagement-moja-global" title="Project Management">📆</a></td></tr></table>

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!


## Maintainers Reviewers Ambassadors Coaches

The following people are Maintainers Reviewers Ambassadors or Coaches  
<table><tr><td align="center"><a href="http://moja.global"><img src="https://avatars1.githubusercontent.com/u/19564969?v=4" width="100px;" alt="moja global"/><br /><sub><b>moja global</b></sub></a><br /><a href="#projectManagement-moja-global" title="Project Management">📆</a></td></tr></table>


**Maintainers** review and accept proposed changes  
**Reviewers** check proposed changes before they go to the Maintainers  
**Ambassadors** are available to provide training related to this repository  
**Coaches** are available to provide information to new contributors to this repository  
