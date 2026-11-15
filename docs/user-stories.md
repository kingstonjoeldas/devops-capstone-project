# Product Backlog — User Stories

All stories use the template in `.github/ISSUE_TEMPLATE/user-story.md`.
Labels: **technical debt** for work with no direct customer value, **enhancement** for new features.
Story points use the Fibonacci scale (1, 2, 3, 5, 8, 13).

| # | Title | Label | Points | Sprint |
|---|-------|-------|--------|--------|
| 1 | Set up the development environment | technical debt | 3 | 1 |
| 2 | Read an account from the service | enhancement | 3 | 1 |
| 3 | List all accounts in the service | enhancement | 3 | 1 |
| 4 | Update an account in the service | enhancement | 3 | 1 |
| 5 | Delete an account from the service | enhancement | 3 | 1 |
| 6 | Need the ability to automate continuous integration checks | technical debt | 5 | 2 |
| 7 | Add security headers and CORS policies | technical debt | 3 | 2 |
| 8 | Containerize microservice using Docker | enhancement | 3 | 3 |
| 9 | Deploy your Docker image to Kubernetes | enhancement | 5 | 3 |
| 10 | Create a CD pipeline to automate deployment to Kubernetes | technical debt | 8 | 3 |

---

## 1. Set up the development environment

**As a** developer
**I need** a consistent development environment
**So that** I can develop the accounts microservice with the right tools

### Details and Assumptions
* Python 3.9, a virtual environment, and a PostgreSQL database in Docker
* Linting (flake8) and testing (nose + coverage) configured in `setup.cfg`

### Acceptance Criteria
```gherkin
Given the project repository
When I run the setup script and `make tests`
Then the existing tests pass against a running PostgreSQL database
```

## 2. Read an account from the service

**As a** customer account manager
**I need** the ability to read an account from the service
**So that** I can view a customer's account details

### Details and Assumptions
* `GET /accounts/{id}` returns the account as JSON
* Returns 404 Not Found if the account does not exist

### Acceptance Criteria
```gherkin
Given an account with id 1 exists
When I send a GET request to /accounts/1
Then I receive 200 OK and the account data as JSON
```

## 3. List all accounts in the service

**As a** customer account manager
**I need** the ability to list all accounts in the service
**So that** I can see every customer account at once

### Details and Assumptions
* `GET /accounts` returns a JSON array of accounts
* Returns an empty array (not 404) when there are no accounts

### Acceptance Criteria
```gherkin
Given 5 accounts exist
When I send a GET request to /accounts
Then I receive 200 OK and a list of 5 accounts
```

## 4. Update an account in the service

**As a** customer account manager
**I need** the ability to update an account in the service
**So that** I can keep customer details current

### Details and Assumptions
* `PUT /accounts/{id}` with a JSON body replaces the account fields
* Returns 404 if not found, 400 for invalid data, 415 for a non-JSON body

### Acceptance Criteria
```gherkin
Given an account with id 1 exists
When I send a PUT request to /accounts/1 with a new name
Then I receive 200 OK and the account shows the new name
```

## 5. Delete an account from the service

**As a** customer account manager
**I need** the ability to delete an account from the service
**So that** I can remove customers who closed their accounts

### Details and Assumptions
* `DELETE /accounts/{id}` returns 204 No Content
* Deleting an account that does not exist also returns 204 (idempotent)

### Acceptance Criteria
```gherkin
Given an account with id 1 exists
When I send a DELETE request to /accounts/1
Then I receive 204 No Content and the account can no longer be read
```

## 6. Need the ability to automate continuous integration checks

**As a** developer
**I need** automated CI checks on every push and pull request
**So that** broken or badly formatted code never reaches main

### Details and Assumptions
* GitHub Actions workflow `.github/workflows/ci-build.yaml`
* Runs in `python:3.9-slim` with a `postgres:alpine` service
* Steps: install dependencies, lint with flake8, run tests with nose
* README shows the build status badge

### Acceptance Criteria
```gherkin
Given code is pushed to main or a pull request is opened against main
When the CI workflow runs
Then linting and all unit tests pass and the badge shows passing
```

## 7. Add security headers and CORS policies

**As a** service provider
**I need** security headers and CORS policies on every response
**So that** the service is protected from common web attacks

### Details and Assumptions
* Flask-Talisman adds X-Frame-Options, X-Content-Type-Options, Content-Security-Policy, Referrer-Policy
* Flask-Cors adds Access-Control-Allow-Origin

### Acceptance Criteria
```gherkin
Given the accounts service is running
When I request the root URL
Then the response contains the security headers and the CORS header
```

## 8. Containerize microservice using Docker

**As a** developer
**I need** the accounts microservice packaged as a Docker image
**So that** it runs the same way in every environment

### Details and Assumptions
* `Dockerfile` based on `python:3.9-slim`, runs as a non-root user
* gunicorn listens on port 8080

### Acceptance Criteria
```gherkin
Given the Dockerfile
When I build the image and run it with a database
Then the service answers on port 8080 with its name and version
```

## 9. Deploy your Docker image to Kubernetes

**As a** service provider
**I need** the accounts service deployed to Kubernetes
**So that** it can scale and be reached by other services

### Details and Assumptions
* PostgreSQL deployed from the `postgresql-ephemeral` template
* `deploy/deployment.yaml` (3 replicas, DB credentials from the `postgresql` secret) and `deploy/service.yaml`

### Acceptance Criteria
```gherkin
Given the image is in the cluster registry
When I apply the manifests in deploy/
Then 3 accounts pods are running and the service responds through its route
```

## 10. Create a CD pipeline to automate deployment to Kubernetes

**As a** developer
**I need** a Tekton pipeline that deploys on every change
**So that** new code reaches the cluster without manual steps

### Details and Assumptions
* Tasks: cleanup, git-clone, flake8, nose, buildah, openshift-client
* Defined in `tekton/tasks.yaml` and `tekton/pipeline.yaml`

### Acceptance Criteria
```gherkin
Given the pipeline is installed in the cluster
When I start a pipeline run for the main branch
Then the code is linted, tested, built into an image, and deployed
```
