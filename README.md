<div align="center">
    <a href="https://moja.global/"><img src="https://github.com/moja-global.png" width="18%" height="18%"></a>
    <h1>FLINT.Cloud</h1>
    <p>
    The project aims to build a continuous deployment pipeline to offer FLINT on cloud resources. The project also aims to simplify the process of installation by supporting a single command or step installation process. This is not offered as a service (Saas) but rather provides deployment templates for new users to install on common infrastructure architectures.        
    </p>
</div>

<hr>
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
        <a href="#technology-stack">Technology Stack</a>
    </li>
    <li>
      <a href="#layered-architecture-setup-on-google-cloud">Layered Architecture Setup on Google Cloud</a>
      <ul>
        <li><a href="#deploying">Deploying</a></li>
        <li><a href="#disabling">Disabling</a></li>
        <li><a href="#flask-example-rest-api-setup">Flask example REST API Setup</a>
        <li><a href="#flask-gcbm-rest-api-setup">Flask-GCBM REST API Setup</a>
      </ul>
    </li>
    <li><a href="#faq-and-other-questions">FAQ and Other Questions</a></li>
    <li><a href="#contributors">Contributors</a></li>
    <li><a href="#maintainers-reviewers-ambassadors-coaches">Maintainers Reviewers Ambassadors Coaches</a></li>
  </ol>
  </br>
</details>


## Technology Stack

- [Python](https://www.python.org/)
- [Google Cloud Platform](https://cloud.google.com/)
- [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- [Terraform](https://www.terraform.io/)
- [Sphinx](https://www.sphinx-doc.org/en/master/)

## Production Setup - Layered Architecture Setup on Google Cloud
#### Deploying

1. Create a service account with project owner permissions in your project. This is used by Terraform to provision all the necessary resources.
2. Copy `main.tf` from the `layered` directory of this repository to your Cloud Console machine.
3. In `main.tf`, change the `project` variable to your project ID. Change any other variables if necessary. 
4. Download the key for the service account created in step 1 (in JSON format) to your project's Cloud Console machine. Rename it as `service_account.json`.
5. Run `terraform apply`. After this command finishes, it should output the URL to FLINT Cloud (ingress).

#### Disabling

1. In the same directory as where `main.tf` is present, run `terraform destroy`. In case this fails, simply run it again.     


## Local Setup 

These steps can be followed to locally setup the API endpoints. This is independent of the above mentioned production setup.

### Flask example REST API Setup  

In order to run the REST API, navigate to the `local/rest_api_flint.example` folder.
Follow these steps: - 

1. `docker build -t flint-api .`
2. `docker run --rm -p 8080:8080 flint-api`

Currently the REST API has the following endpoints available for access:-

| Endpoint       |  Functionality            |
| :--------------| :------------------------ |
| **/help/all**  | Produces a help message with information on all options for moja.CLI. |
| **/help/arg**  | Produces a help message with information on option **arg** for moja.CLI. |
| **/version**   | Outputs the version number of moja.CLI. |
| **/point**     | Runs point example and outputs point_example.csv as an attachment to be downloaded.  Parameters (multipart-form data) `file` for point_example can be passed to override the default configurations. |
| **/rothc**    | Runs rothc example and outputs point_rothc_example.csv as an attachment to be downloaded. Parameters (multipart-form data) `file` for rothc_example can be passed to override the default configurations.

This REST API is built using the `flask-restful` package and has been containerized using `Docker`.  

### Flask GCBM REST API Setup  

In order to run the Flask GCBM API, navigate to the `local/rest_api_gcbm` please follow the following steps: - 

1. `docker build --build-arg BUILD_TYPE=RELEASE --build-arg NUM_CPU=4 -t gcbm-api .`
2. `docker run --rm -p 8080:8080 gcbm-api`

Currently the REST API has the following endpoints available for access:-

| Endpoint      | Functionality     |
| :------------ | :-----------------|
| **/help/all** | Produces a help message with information on all options for moja.CLI. |
| **/help/arg** | Produces a help message with information on option **arg** for moja.CLI.|
| **/version**  | Outputs the version number of moja.CLI.|
| **/gcbm/new**| This endpoint is used to create new simulation with the suitable title.|
| **/gcbm/upload**| This endpoint is used to upload all the input files that needs to run the GCBM simulation.| 
| **/gcbm/dynamic**| This endpoint is used to execute the simulation process.|
| **/gcbm/status**| This endpoint is used to check the status of the simulation process, whether the simulation is completed or not.|
| **/gcbm/download**| This endpoint is used to download a simulation output in the zip format.|
| **/gcbm/list**| This endpoint is used to check the available simulation currently present.| 


This REST API is built using the `flask-restful` package and has been containerized using `Docker`.

## Contributing

### Commit Convention

Before you create a Pull Request, please check whether your commits comply with
the commit conventions used in this repository.

When you create a commit we kindly ask you to follow the convention
`category(scope or module): message` in your commit message while using one of
the following categories:

- `feat / feature`: all changes that introduce completely new code or new
  features
- `fix`: changes that fix a bug (ideally you will additionally reference an
  issue if present)
- `refactor`: any code related change that is not a fix nor a feature
- `docs`: changing existing or creating new documentation (i.e. README, docs for
  usage of a lib or cli usage)
- `build`: all changes regarding the build of the software, changes to
  dependencies or the addition of new dependencies
- `test`: all changes regarding tests (adding new tests or changing existing
  ones)
- `ci`: all changes regarding the configuration of continuous integration (i.e.
  github actions, ci system)
- `chore`: all changes to the repository that do not fit into any of the above
  categories

If you are interested in the detailed specification you can visit
https://www.conventionalcommits.org/

The project is configured with [husky](https://typicode.github.io/husky/#/) git-hook which on every successive commits checks for linting errors in the codebase and commit convention.

To ease writing conventional commit messages, this repository contains [commitizen](https://github.com/commitizen/cz-cli) that assists with that. To commit your changes, run `yarn commit` in the root of the repository.

### Branch-name Convention

We follow the convention `[type/scope]`. For example `fix/lint-error` or `docs/component-api`. `type` can be either `docs`, `fix`, `feat`, `build`, or any other conventional commit type. `scope` is just a short id that describes the scope of work.

### Development notes

For the developer environment setup, project structure, best practices etc. you can go through the Development Notes [here.](https://github.com/moja-global/FLINT-UI/blob/master/docs/DevelopmentGuide/DevelopmentNotes.rst).

### Read More

Find more comprehensive details about Moja Global Contributing Guidelines [here.](https://github.com/moja-global/About_moja_global/tree/master/Contributing#community-contributions).

## How to Get Involved?  

<!--This project will be open for applications from Jan 30 to Feb 12, 2021 - please see the [LFX Mentorship Program proposal](https://mentorship.lfx.linuxfoundation.org/project/d70e1f9e-abde-403f-8389-52a122301500) to apply.-->

Feel free to [join our Slack community](https://join.slack.com/t/mojaglobal/shared_invite/zt-lf2290hy-CGqpUvHFfGsqoIZnO8MXKQ) and get to know everyone.

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

<table><tr><td align="center"><a href="http://moja.global"><img src="https://avatars1.githubusercontent.com/u/19564969?v=4" width="100px;" alt="moja global"/><br /><sub><b>moja global</b></sub></a><br /><a href="#projectManagement-moja-global" title="Project Management">📆</a></td></tr></table>

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

## Maintainers Reviewers Ambassadors Coaches

The following people are Maintainers Reviewers Ambassadors or Coaches  
<table><tr><td align="center"><a href="http://moja.global"><img src="https://avatars1.githubusercontent.com/u/19564969?v=4" width="100px;" alt="moja global"/><br /><sub><b>moja global</b></sub></a><br /><a href="#projectManagement-moja-global" title="Project Management">📆</a></td></tr></table>


**Maintainers** review and accept proposed changes  
**Reviewers** check proposed changes before they go to the Maintainers  
**Ambassadors** are available to provide training related to this repository  
**Coaches** are available to provide information to new contributors to this repository  

## License 

This project is released under the [Mozilla Public License Version 2.0](https://github.com/moja-global/FLINT-UI/blob/master/LICENSE).
