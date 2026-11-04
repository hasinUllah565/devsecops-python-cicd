# DevSecOps End-to-End CI/CD Pipeline

An automated CI/CD pipeline integrating Jenkins, SonarQube, OWASP, Trivy, and Docker to build, scan, secure, and deploy applications.

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

After we will use Jenkins for automating pipelines .
so no let's install other prerequisite 

----------------------

---

## SonarQube Installation

SonarQube is used to analyze source code, detect bugs, identify security vulnerabilities, and maintain code quality.

Follow the official documentation to install SonarQube:

[Official SonarQube Documentation](https://docs.sonarsource.com/sonarqube-server/latest/setup-and-upgrade/install-the-server/)


### SonarQube Login ,Dashboard and Configuration

- Open SonarQube in your browser using port **9000**.
- Default username: `admin`
- Default password: `admin`
- Change the default password after your first login.
- Create a project and generate an authentication token for Jenkins integration.

**Note:** If using AWS EC2, allow inbound traffic on port **9000** in the Security Group.

![SonarQube Dashboard](images/sonarqube_dashboard.jpeg)

---------------



