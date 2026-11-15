# devops-capstone-project

[![CI Build](https://github.com/kingstonjoeldas/devops-capstone-project/actions/workflows/ci-build.yaml/badge.svg)](https://github.com/kingstonjoeldas/devops-capstone-project/actions/workflows/ci-build.yaml)
[![Python 3.9](https://img.shields.io/badge/Python-3.9-green.svg)](https://shields.io/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A customer **Accounts microservice** with a REST API, built with Test Driven Development
and delivered with CI (GitHub Actions) and CD (Tekton on OpenShift). This is the
IBM DevOps and Software Engineering capstone project.

## REST API

| Method | URL | Description | Success | Errors |
|--------|-----|-------------|---------|--------|
| GET | `/` | Service name, version and link to `/accounts` | 200 | |
| GET | `/health` | Health check | 200 | |
| POST | `/accounts` | Create an account (JSON body) | 201 + `Location` header | 400, 415 |
| GET | `/accounts` | List all accounts | 200 (empty list if none) | |
| GET | `/accounts/{id}` | Read an account | 200 | 404 |
| PUT | `/accounts/{id}` | Update an account (JSON body) | 200 | 400, 404, 415 |
| DELETE | `/accounts/{id}` | Delete an account (idempotent) | 204 | |

Example body:

```json
{"name": "John Doe", "email": "john@doe.com", "address": "123 Main St.", "phone_number": "555-1212"}
```

Every response carries security headers from **Flask-Talisman** (`X-Frame-Options`,
`X-Content-Type-Options`, `Content-Security-Policy`, `Referrer-Policy`) and a CORS
header from **Flask-Cors**. HTTP-to-HTTPS redirect is opt-in with `FORCE_HTTPS=true`,
because TLS is terminated by the OpenShift router in front of the pods.

## Running the tests

```bash
make db        # start PostgreSQL in Docker
make lint      # flake8
make tests     # nose with coverage (>= 95%)
```

## Running the service in Docker

```bash
docker build -t accounts:1 .
docker run --rm -p 8080:8080 -e DATABASE_URI=postgresql://postgres:postgres@<db-host>:5432/postgres accounts:1
curl http://localhost:8080/
```

## Deploying to OpenShift (Kubernetes)

```bash
oc create -f postgresql-ephemeral-template.json   # only if the template is not in the cluster
oc new-app postgresql-ephemeral                    # creates the postgresql service and secret
export IMAGE=<registry>/<namespace>/accounts:1     # registry path from the lab instructions
docker tag accounts:1 $IMAGE && docker push $IMAGE
sed "s|IMAGE_NAME_HERE|$IMAGE|g" deploy/deployment.yaml | oc apply -f -
oc apply -f deploy/service.yaml
oc expose service accounts
oc get all -l app=accounts
```

## CD pipeline (Tekton)

```bash
oc apply -f tekton/pvc.yaml
oc apply -f tekton/tasks.yaml                       # cleanup, nose
tkn hub install task git-clone
tkn hub install task flake8
oc apply -f tekton/pipeline.yaml
tkn pipeline start cd-pipeline   -p repo-url="https://github.com/kingstonjoeldas/devops-capstone-project.git"   -p branch=main   -p build-image=image-registry.openshift-image-registry.svc:5000/$SN_ICR_NAMESPACE/accounts:1   -w name=pipeline-workspace,claimName=pipelinerun-pvc   -s pipeline --showlog
tkn pipelinerun logs --last > pipelinerun.txt
```

Pipeline: `init` (cleanup) -> `clone` -> `lint` + `tests` (in parallel) -> `build` (buildah) -> `deploy` (oc apply).

## Development Environment

These labs are designed to be executed in the IBM Developer Skills Network Cloud IDE with OpenShift. Please use the links provided in the Coursera Capstone project to access the lab environment.

Once you are in the lab environment, you can initialize it with `bin/setup.sh` by sourcing it. (*Note: DO NOT run this program as a bash script. It sets environment variable and so must be sourced*):

```bash
source bin/setup.sh
```

This will install Python 3.9, make it the default, modify the bash prompt, create a Python virtual environment and activate it.

After sourcing it you prompt should look like this:

```bash
(venv) theia:project$
```

## Useful commands

Under normal circumstances you should not have to run these commands. They are performed automatically at setup but may be useful when things go wrong:

### Activate the Python 3.9 virtual environment

You can activate the Python 3.9 environment with:

```bash
source ~/venv/bin/activate
```

### Installing Python dependencies

These dependencies are installed as part of the setup process but should you need to install them again, first make sure that the Python 3.9 virtual environment is activated and then use the `make install` command:

```bash
make install
```

### Starting the Postgres Docker container

The labs use Postgres running in a Docker container. If for some reason the service is not available you can start it with:

```bash
make db
```

You can use the `docker ps` command to make sure that postgres is up and running.

## Project layout

The code for the microservice is contained in the `service` package. All of the test are in the `tests` folder. The code follows the **Model-View-Controller** pattern with all of the database code and business logic in the model (`models.py`), and all of the RESTful routing on the controller (`routes.py`).

```text
├── deploy          <- Kubernetes manifests
├── docs            <- user stories / backlog
├── service         <- microservice package
│   ├── common/     <- common log and error handlers
│   ├── config.py   <- Flask configuration object
│   ├── models.py   <- code for the persistent model
│   └── routes.py   <- code for the REST API routes
├── setup.cfg       <- tools setup config
├── tekton          <- Tekton tasks, pipeline and PVC
├── Dockerfile      <- container image
└── tests                       <- folder for all of the tests
    ├── factories.py            <- test factories
    ├── test_cli_commands.py    <- CLI tests
    ├── test_models.py          <- model unit tests
    └── test_routes.py          <- route unit tests
```

## Data Model

The Account model contains the following fields:

| Name | Type | Optional |
|------|------|----------|
| id | Integer| False |
| name | String(64) | False |
| email | String(64) | False |
| address | String(256) | False |
| phone_number | String(32) | True |
| date_joined | Date | False |

## Your Task

Complete this microservice by implementing REST API's for `READ`, `UPDATE`, `DELETE`, and `LIST` while maintaining **95%** code coverage. In true **Test Driven Development** fashion, first write tests for the code you "wish you had", and then write the code to make them pass.

## Local Kubernetes Development

This repo can also be used for local Kubernetes development. It is not advised that you run these commands in the Cloud IDE environment. The purpose of these commands are to simulate the Cloud IDE environment locally on your computer. 

At a minimum, you will need [Docker Desktop](https://www.docker.com/products/docker-desktop) installed on your computer. For the full development environment, you will also need [Visual Studio Code](https://code.visualstudio.com) with the [Remote Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension from the Visual Studio Marketplace. All of these can be installed manually by clicking on the links above or you can use a package manager like **Homebrew** on Mac of **Chocolatey** on Windows.

Please only use these commands for working stand-alone on your own computer with the VSCode Remote Container environment provided.

1. Bring up a local K3D Kubernetes cluster

    ```bash
    $ make cluster
    ```

2. Install Tekton

    ```bash
    $ make tekton
    ```

3. Install the ClusterTasks that the Cloud IDE has

    ```bash
    $ make clustertasks
    ```

You can now perform Tekton development locally, just like in the Cloud IDE lab environment.

## Author

[John Rofrano](https://www.coursera.org/instructor/johnrofrano), Senior Technical Staff Member, DevOps Champion, @ IBM Research, and Instructor @ Coursera

## License

Licensed under the Apache License. See [LICENSE](LICENSE)

## <h3 align="center"> © IBM Corporation 2022. All rights reserved. <h3/>
