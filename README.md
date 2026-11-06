# Secure Task Management System

A modern, responsive task manager built with **Flask**, **SQLAlchemy** and **SQLite**.
It is the application source for a DevSecOps CI/CD project (`devsecops-python-cicd`).

## Features

- **Authentication**: registration, login, logout, hashed passwords, secure sessions, form validation
- **Dashboard**: totals, completed / in-progress / pending counts, completion donut chart,
  open-task priority meters, recent tasks, upcoming deadlines, overdue count
- **Tasks**: create, view, edit, delete, mark completed, priorities (Low / Medium / High),
  deadlines, descriptions, filtering by status and priority, search, sorting, pagination
- **UI**: SaaS-style layout with sidebar, top bar, light and dark mode, mobile-friendly offcanvas menu

## Project structure

```text
devsecops-python-cicd/
├── app/
│   ├── __init__.py        # application factory, security headers, error handlers
│   ├── models.py          # User and Task models
│   ├── auth.py            # register / login / logout blueprint
│   ├── routes.py          # dashboard and task blueprint
│   ├── forms.py           # validated WTForms
│   ├── templates/         # Jinja2 templates
│   └── static/            # css/, js/, images/
├── tests/                 # pytest suite
├── config.py              # environment-driven configuration
├── run.py                 # development entry point
├── requirements.txt
├── pytest.ini
├── .env.example
└── .gitignore
```

## Run locally on Ubuntu

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip -y

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Generate a secret key and paste it into .env as SECRET_KEY:
python3 -c "import secrets; print(secrets.token_hex(32))"

python run.py
```

Open <http://127.0.0.1:5000>. The SQLite database (`instance/app.db`) is created automatically on first start.

## Run the tests

```bash
pytest -v
```

The suite covers registration, login, invalid logins, authentication protection, task create /
update / delete, filtering and search, dashboard statistics, and cross-user authorization.

## Configuration

All settings come from environment variables (see `.env.example`). Nothing secret is hardcoded.

| Variable | Purpose | Default |
| --- | --- | --- |
| `SECRET_KEY` | Signs sessions and CSRF tokens | random per start (sessions reset on restart) |
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///instance/app.db` |
| `SESSION_COOKIE_SECURE` | Send cookies over HTTPS only (`1` behind HTTPS) | `0` |
| `FLASK_DEBUG` | Debug mode for `run.py` (`1` to enable) | `0` |
| `HOST` / `PORT` | Bind address | `127.0.0.1` / `5000` |

Always set a fixed `SECRET_KEY` for anything beyond local development, and never run with `FLASK_DEBUG=1` in production.

## Security measures

- Passwords hashed with Werkzeug (salted); plain text is never stored or logged
- CSRF protection on every form and state-changing request (Flask-WTF); logout, delete and complete are POST-only
- SQL injection prevented by SQLAlchemy ORM with bound parameters; search wildcards are escaped and filter values are whitelisted
- Server-side validation and cleaning of all input; Jinja auto-escaping prevents stored XSS
- Per-user data isolation: every task lookup checks ownership, and another user's task returns `404` so its existence is not revealed
- Generic login error and equalised timing to avoid account enumeration; open-redirect protection on `next`
- Hardened sessions (`HttpOnly`, `SameSite=Lax`, optional `Secure`, 2-hour lifetime, `strong` session protection)
- Security headers: Content-Security-Policy, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`
- No inline scripts or styles, so the CSP stays strict; error pages never expose stack traces

## Notes

- Bootstrap and Font Awesome load from public CDNs (allowed in the CSP). For fully offline or air-gapped
  environments, vendor those files into `app/static/` and adjust the CSP in `app/__init__.py`.
- `requirements.txt` uses pinned versions so dependency scanners give reproducible results. Update the pins
  as new releases and advisories appear.
- Application source lives in `app/`, so analysis tools can target that directory.


# 3. SonarQube Integration with Jenkins

SonarQube is integrated with Jenkins to automatically analyze application code, detect bugs, security vulnerabilities, and check code quality during the CI/CD pipeline.

This integration is divided into two parts:

- **Part 1:** Configure SonarQube, generate an authentication token, create a project, and configure the Jenkins webhook.
- **Part 2:** Configure Jenkins, connect it to SonarQube, run code analysis, and check the Quality Gate result.

## Part 1: SonarQube Configuration

### Step 1: Open SonarQube Dashboard

1. Open SonarQube in your browser.
2. Log in using your administrator account.
3. Make sure SonarQube is running properly.

### Step 2: Create a SonarQube Project

1. Open the SonarQube Dashboard.

2. Click **Create Project**.

3. Select **Manually**.

4. Enter the project name:

   `devsecops-python-cicd`

5. Set the project key:

   `devsecops-python-cicd`

6. Click **Create Project**.

### Step 3: Generate SonarQube Authentication Token

1. Open SonarQube.

2. Go to **Administration → Security → Users**.

3. Open your user account.

4. Find the **Tokens** section.

5. Enter a token name, for example:

   `jenkins-token`

6. Generate the token.

7. Copy and securely save the token.

**Important:** Save the token securely. You will add it to Jenkins as a credential.

### Step 4: Configure Jenkins Webhook in SonarQube

A webhook allows SonarQube to send the Quality Gate result back to Jenkins after code analysis is completed.

1. Log in to SonarQube as an administrator.
2. Go to **Administration → Configuration → Webhooks**.
3. Click **Create** or **Create Webhook**.
4. Enter the following details:

| Setting | Value                                          |
| ------- | ---------------------------------------------- |
| Name    | Jenkins                                        |
| URL     | `http://192.168.15.18:8080/sonarqube-webhook/` |

5. Click **Create** to save the webhook.

**Important:** Replace `192.168.15.18` with your actual Jenkins server IP address if it is different. SonarQube must be able to reach this address. The trailing slash `/` at the end of `/sonarqube-webhook/` is mandatory.

If you are using a private IP address, make sure both servers can communicate over the network.

## Part 2: Jenkins Configuration

### Step 5: Install SonarQube Scanner Plugin

1. Open Jenkins Dashboard.
2. Go to **Manage Jenkins → Plugins → Available Plugins**.
3. Search for **SonarQube Scanner**.
4. Install the plugin.

### Step 6: Add SonarQube Credentials in Jenkins

1. Open **Manage Jenkins → Credentials**.

2. Select **System → Global credentials**.

3. Click **Add Credentials**.

4. Select **Secret Text**.

5. Paste your SonarQube authentication token.

6. Give it an ID:

   `sonarqube-token`

7. Click **Create** or **Save**.

### Step 7: Configure SonarQube Server in Jenkins

1. Go to **Manage Jenkins → System**.
2. Find the **SonarQube Servers** section.
3. Click **Add SonarQube**.
4. Enter the following details:

| Setting                     | Value                     |
| --------------------------- | ------------------------- |
| Name                        | SonarQube                 |
| Server URL                  | `http://YOUR-EC2-IP:9000` |
| Server Authentication Token | `sonarqube-token`         |

5. Select the Jenkins credential with ID `sonarqube-token`.
6. Click **Save**.

### Step 8: Configure SonarQube Scanner

1. Go to **Manage Jenkins → Tools**.

2. Find **SonarQube Scanner installations**.

3. Click **Add SonarQube Scanner**.

4. Enter the name:

   `SonarScanner`

5. Select automatic installation if required.

6. Save the configuration.

add here the process of dependecy check owasp

### Step 9: Add SonarQube Analysis Stage to Jenkinsfile

Add the following stage to your Jenkins pipeline:

```groovy
stage('SonarQube Analysis') {
    steps {
        withSonarQubeEnv('SonarQube') {
            sh '''
                sonar-scanner \
                -Dsonar.projectKey=devsecops-python-cicd \
                -Dsonar.sources=app
            '''
        }
    }
}
```

**Explanation:**

- `withSonarQubeEnv('SonarQube')`: Connects Jenkins with the configured SonarQube server.
- `sonar-scanner`: Starts the code analysis.
- `sonar.projectKey`: Identifies the SonarQube project.
- `sonar.sources=app`: Specifies the application source directory to analyze.

### Step 10: Add Quality Gate Stage to Jenkinsfile

After the SonarQube Analysis stage, add the following Quality Gate stage:

```groovy
stage('Quality Gate') {
    steps {
        timeout(time: 1, unit: 'HOURS') {
            waitForQualityGate abortPipeline: true
        }
    }
}
```

**Explanation:**

- `waitForQualityGate`: Waits for SonarQube to complete the code analysis and return the Quality Gate result.
- `abortPipeline: true`: Stops the Jenkins pipeline if the Quality Gate fails.
- `timeout`: Prevents the pipeline from waiting indefinitely.

**Important:** The SonarQube webhook configured in Part 1 is required for `waitForQualityGate` to receive the result.

### Step 11: Verify SonarQube and Jenkins Integration

1. Commit and push your project code to GitHub.
2. Run your Jenkins pipeline.
3. Open the Jenkins Console Output.
4. Check that the SonarQube Analysis stage completes successfully.
5. Open your SonarQube Dashboard.
6. Check the project analysis results.
7. Check the Quality Gate status in Jenkins.

**Expected Result:**

- Jenkins sends the application code to SonarQube.
- SonarQube analyzes the code.
- SonarQube calculates the Quality Gate result.
- SonarQube sends the result to Jenkins through the webhook.
- Jenkins continues if the Quality Gate passes.
- Jenkins stops if the Quality Gate fails.

### Official References

- [SonarQube Official Jenkins Integration Guide](https://docs.sonarsource.com/sonarqube-server/analyzing-source-code/ci-integration/jenkins-integration/)
- [SonarQube Pipeline Pause and Quality Gate](https://docs.sonarsource.com/sonarqube-server/analyzing-source-code/ci-integration/jenkins-integration/pipeline-pause)
- [Jenkins SonarQube Scanner Documentation](https://www.jenkins.io/doc/pipeline/steps/sonar/)

