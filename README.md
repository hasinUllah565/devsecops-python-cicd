# DevSecOps End-to-End CI/CD Pipeline

An automated CI/CD pipeline integrating Jenkins, SonarQube, OWASP, Trivy, and Docker to build, scan, secure, and deploy applications.

## Table of Contents

1. [Project Architecture](#project-architecture)
2. [Prerequisites – Required Tools](#prerequisites--required-tools-and-their-explanations)
3. [Prerequisites to Implement This Project](#prerequisites-to-implement-this-project)
4. [Installation of Docker and Docker Compose](#1-installation-of-docker-and-docker-compose)
5. [Jenkins Installation](#jenkins-installation)
   - [Why Do We Use Jenkins?](#why-do-we-use-jenkins)
   - [Jenkins Configuration](#jenkins-configuration)
   - [Access Jenkins Through Browser](#access-jenkins-through-browser)
   - [Initial Administrator Password](#initial-administrator-password)
   - [Install Suggested Plugins](#install-suggested-plugins)
   - [Jenkins Homepage](#jenkins-homepage)
6. [Jenkins Plugins Installation](#2-jenkins-plugins-installation)
7. [SonarQube Installation](#sonarqube-installation)
   - [SonarQube Login, Dashboard and Configuration](#sonarqube-login-dashboard-and-configuration)
   - [SonarQube Integration with Jenkins](#sonarqube-integration-with-jenkins)
8. [Trivy Installation](#trivy-installation)
9. [Trivy Important Commands](#trivy-important-commands)
10. [SonarQube Integration with Jenkins – Practical Implementation](#3-sonarqube-integration-with-jenkins)

---

## Project Architecture

![DevSecOps Architecture](images/image1.jpeg)

![DevSecOps End-to-End CI/CD Pipeline](images/devops_end_to_pend_pipelines.png)

## Prerequisites – Required Tools and Their Explanations

1. **GitHub:** Source code management and repository hosting.
2. **Docker:** Containerization and application image building.
3. **Jenkins:** CI/CD pipeline automation.
4. **SonarQube:** Code quality analysis and security checks.
5. **OWASP Dependency-Check:** Dependency vulnerability scanning.
6. **Trivy:** Docker image vulnerability scanning.
7. **Docker Hub:** Store and publish Docker images.

**Operating System:** Ubuntu Linux.

## Prerequisites to Implement This Project

- Ubuntu Linux (AWS EC2 or local machine).
- GitHub account and repository.
- Docker and Docker Compose installed.
- Jenkins installed and configured.
- SonarQube installed.
- OWASP Dependency-Check configured.
- Trivy installed.
- Docker Hub account.

---

# 1. Installation of Docker and Docker Compose

### Step 1: Update Ubuntu Packages

```bash
sudo apt update
```

### Step 2: Install Docker and Docker Compose

```bash
sudo apt install docker.io -y
sudo apt install docker-compose-v2 -y
```

### Step 3: Enable Docker

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

### Step 4: Allow Docker Without Sudo

#### First, check Docker permissions:

```bash
docker ps
```

If you get a permission error, run this command to add your current user to the Docker group:

```bash
sudo usermod -aG docker $USER
```

Restart your system:

```bash
sudo reboot
```

After restarting, verify Docker:

```bash
docker ps
```

Log out and log back in for the group change to take effect.

### Step 5: Verify Installation

```bash
docker --version
docker compose version
docker run hello-world
```

**Official Documentation:** https://docs.docker.com/engine/install/ubuntu/

---

## Jenkins Installation

Install Jenkins on Ubuntu using the official documentation.

First, install Java because Jenkins requires Java to run. Follow the official documentation linked below for installation instructions.

[Official Jenkins Installation Guide](https://www.jenkins.io/doc/book/installing/linux/)

### Why Do We Use Jenkins?

Jenkins is used to automate the CI/CD pipeline, including application building, testing, security scanning, and deployment.

### Jenkins Configuration

- Jenkins runs on port **8080** by default.
- If you are using an AWS EC2 instance, allow inbound traffic on port **8080** in the Security Group.
- Start Jenkins:

```bash
sudo systemctl start jenkins
```

- Check Jenkins service status:

```bash
sudo systemctl status jenkins
```

### Access Jenkins Through Browser

Allow port **8080** in your EC2 instance's Security Group.

![Allow port 8080](./images/security_group_image.jpeg)

Open Jenkins in your browser using your EC2 public IP or your local IP.

```text
http://YOUR-EC2-PUBLIC-IP:8080
```

### Initial Administrator Password

Open the terminal of your local machine or AWS EC2 instance and run the following command to retrieve the initial administrator password:

```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

Copy the displayed password and paste it into the **Administrator Password** field on the Jenkins setup page to unlock Jenkins.

![Jenkins access through browser](./images/jenkins_on_browser.jpeg)

Enter this password on the Jenkins setup page to unlock Jenkins.

### Install Suggested Plugins

![Install suggested plugins](./images/Install_suggest_plugins.jpeg)

### Jenkins Homepage

The Jenkins Dashboard is the main interface for managing CI/CD pipelines and automation jobs.

Important components:

- **New Item:** Create a new Jenkins job or pipeline.
- **Build History:** View previous and current builds.
- **Manage Jenkins:** Configure Jenkins settings, plugins, credentials, and security.
- **My Views:** Organize and manage Jenkins jobs.
- **Build Executor Status:** Check available executors and running builds.
- **People:** View Jenkins users.

![Jenkins home page](./images/using_jenkisn.jpeg)

After this, we will use Jenkins to automate our pipelines.

Now, let's install the other prerequisites.

---

## 2. Jenkins Plugins Installation

Go to **Manage Jenkins → Plugins → Available Plugins** and install the following plugins required for our DevSecOps CI/CD pipeline:

1. **SonarQube Scanner** (Version 2.16.1)
2. **Sonar Quality Gates** (Version 1.3.1)
3. **OWASP Dependency-Check** (Version 5.4.3)
4. **Docker** (Version 1.5)

![Jenkins Plugins Installation](./images/jenkins_plugins.png)

These plugins enable Jenkins to integrate with SonarQube, perform dependency vulnerability scanning, and manage Docker operations.

---

## SonarQube Installation

SonarQube is used to analyze source code, detect bugs, identify security vulnerabilities, and maintain code quality.

### Run SonarQube Using Docker

```bash
docker run -itd --name sonarqube -p 9000:9000 sonarqube:lts-community
```

Check the running container:

```bash
docker ps
```

![SonarQube run](./images/sonarqube_1.png)

### Access SonarQube Through Browser

```text
http://YOUR-EC2-PUBLIC-IP:9000
```

### SonarQube Login, Dashboard and Configuration

- Open SonarQube in your browser using port **9000**.
- Default username: `admin`
- Default password: `admin`
- Change the default password after your first login.
- Create a project and generate an authentication token for Jenkins integration.

**Note:** If using AWS EC2, allow inbound traffic on port **9000** in the Security Group.

### Short Definition

SonarQube is a tool that checks our code, finds mistakes and security problems, and helps us write clean, secure, and better-quality code.

![SonarQube Dashboard](./images/sonarqube_dashboard.png)

### SonarQube Integration with Jenkins

1. Install the SonarQube Scanner plugin in Jenkins.
2. Add your SonarQube server URL in Jenkins configuration.
3. Generate a SonarQube authentication token and add it to Jenkins Credentials.
4. Configure the SonarQube Scanner in your Jenkins pipeline using a Jenkinsfile.
5. Jenkins will automatically send your application code to SonarQube for quality and security analysis.

![SonarQube integration with Jenkins](./images/jenkin_sonarqube_integ.jpeg)

---

## Trivy Installation

Trivy is a security scanner used to detect vulnerabilities in Docker images, dependencies, and file systems.

### Install Trivy on Ubuntu

```bash
sudo apt-get install wget gnupg -y

wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | sudo tee /usr/share/keyrings/trivy.gpg > /dev/null

echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | sudo tee -a /etc/apt/sources.list.d/trivy.list

sudo apt-get update

sudo apt-get install trivy -y
```

### Verify Trivy Installation

```bash
trivy --version
```

### Official Documentation

[Trivy Official Installation Guide](https://www.trivy.dev/docs/latest/getting-started/installation/)

---

## Trivy Important Commands

Trivy is used to scan Docker images, filesystems, and configurations to identify security vulnerabilities.

### 1. Check Trivy Version

```bash
trivy --version
```

### 2. Scan a Docker Image

```bash
trivy image nginx:latest
```

### 3. Scan High and Critical Vulnerabilities

```bash
trivy image --severity HIGH,CRITICAL nginx:latest
```

### 4. Scan Project Files

```bash
trivy fs .
```

### 5. Scan Dockerfile Configuration

```bash
trivy config Dockerfile
```

### 6. Generate a JSON Report

```bash
trivy image --format json -o trivy-report.json nginx:latest
```

**Purpose:** Trivy helps us identify security vulnerabilities before deploying our applications.

**Official Documentation:** https://trivy.dev/docs/latest/

---
=================================

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

![Sonarkube tokens.png ](./images/sonarkube_tokens.png)

### Step 4: Configure Jenkins Webhook in SonarQube

A webhook allows SonarQube to send the Quality Gate result back to Jenkins after code analysis is completed.

1. Log in to SonarQube as an administrator.
2. Go to **Administration → Configuration → Webhooks**.
3. Click **Create** or **Create Webhook**.
4. Enter the following details:
5. Click **Create** to save the webhook.


| Setting | Value |
|---|---|
| Name | Jenkins |
| URL | `http://192.168.15.18:8080/sonarqube-webhook/` |

![Jenkins webhook in sonarqube ](./images/jenkins_webhook.png)

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

| Setting | Value |
|---|---|
| Name | SonarQube |
| Server URL | `http://YOUR-EC2-IP:9000` |
| Server Authentication Token | `sonarqube-token` |

5. Select the Jenkins credential with ID `sonarqube-token`.
6. Click **Save**.

![Sonarqube add in jenkins](./images/sonarqube_add_in_jenkins.png)


### Step 8: Configure SonarQube Scanner

1. Go to **Manage Jenkins → Tools**.
2. Find **SonarQube Scanner installations**.
3. Click **Add SonarQube Scanner**.
4. Enter the name:

   `SonarScanner`

5. Select automatic installation if required.
6. Save the configuration.

![Sonarqube scanner installation ](./images/sonarqube_scanner_installation.png)

### 9: Configure Dependency-Check Tool in Jenkins

1. After installing the plugin, configure the Dependency-Check CLI tool.
2. **Go to `Manage Jenkins` → `Tools`.**
3. **Find the `Dependency-Check`section.**
4. **Click `Add Dependency-Check`**
5. **Enter the installation name:**
    **`DP-Check`**
6. **Select `Install automatically`.**
7. **Select the `available stable version`.**
8.  **`Save`the configuration.**
9. Jenkins will automatically download and install the Dependency-Check `CLI` tool when required.
![owasp dependece check installation ](./images/dependency_check.png)

### Step 10: Add SonarQube Analysis Stage to Jenkinsfile

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

### Step 11: Add Quality Gate Stage to Jenkinsfile

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

### Step 12: Verify SonarQube and Jenkins Integration

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

