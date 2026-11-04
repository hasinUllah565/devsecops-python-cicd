# DevSecOps End-to-End CI/CD Pipeline

An automated CI/CD pipeline integrating Jenkins, SonarQube, OWASP, 
Trivy, and Docker to build, scan, secure, and deploy applications.

![DevSecOps Architecture](images/image1.jpeg)
![DevSecOps End-to-End CI/CD Pipeline](images/devops_end_to_pend_pipelines.png)

## Prerequisites – Required Tools explanation
1. GitHub: Source code management and repository hosting.
2. Docker: Containerization and application image building.
3. Jenkins: CI/CD pipeline automation.
4. SonarQube: Code quality analysis and security checks.
5. OWASP Dependency-Check: Dependency vulnerability scanning.
6. Trivy: Docker image vulnerability scanning.
7. Docker Hub: Store and publish Docker images.
Operating System: Ubuntu Linux.

## Prerequisites to Implement This Project

- Ubuntu Linux (AWS EC2 or local machine).
- GitHub account and repository.
- Docker and Docker Compose installed.
- Jenkins installed and configured.
- SonarQube installed.
- OWASP Dependency-Check configured.
- Trivy installed.
- Docker Hub account.



# 1. Installation of Docker and Docker Compose

### Step 1: Update Ubuntu packages

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

### Step 4: Allow Docker without sudo

#### it will show permission error 
```bash
docker ps
```
#### then you need to run this command to add docker in current user group

```bash
sudo usermod -aG docker $USER

docker reboot

docker ps
```

Log out and log back in for the group change to take effect.

### Step 6: Verify installation

```bash
docker --version
docker compose version
docker run hello-world
```

**Official Documentation:** https://docs.docker.com/engine/install/ubuntu/

--------------------------------------------
# Jendkins installation 
## Jenkins Installation

Install Jenkins on Ubuntu using the official documentation:

[Official Jenkins Installation Guide](https://www.jenkins.io/doc/book/installing/linux/)


