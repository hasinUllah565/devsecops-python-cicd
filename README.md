# DevSecOps End-to-End CI/CD Pipeline

An automated CI/CD pipeline integrating Jenkins, SonarQube, OWASP, 
Trivy, and Docker to build, scan, secure, and deploy applications.

![DevSecOps Architecture](images/image1.jpeg)
![DevSecOps End-to-End CI/CD Pipeline](images/devops_end_to_pend_pipelines.png)

## Prerequisites – Required Tools
1. GitHub: Source code management and repository hosting.
2. Docker: Containerization and application image building.
3. Jenkins: CI/CD pipeline automation.
4. SonarQube: Code quality analysis and security checks.
5. OWASP Dependency-Check: Dependency vulnerability scanning.
6. Trivy: Docker image vulnerability scanning.
7. Docker Hub: Store and publish Docker images.
Operating System: Ubuntu Linux.


# 1. Installation of Docker and Docker Compose

### Step 1: Update Ubuntu packages

```bash
sudo apt update
sudo apt upgrade -y
```

### Step 2: Install required dependencies

```bash
sudo apt install ca-certificates curl gnupg -y
```

### Step 3: Add Docker's official GPG key

```bash
sudo install -m 0755 -d /etc/apt/keyrings

sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
-o /etc/apt/keyrings/docker.asc

sudo chmod a+r /etc/apt/keyrings/docker.asc
```

### Step 4: Add Docker repository

```bash
echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### Step 5: Install Docker Engine and Docker Compose

```bash
sudo apt update

sudo apt install docker-ce docker-ce-cli containerd.io \
docker-buildx-plugin docker-compose-plugin -y
```

### Step 6: Enable Docker

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

### Step 7: Allow Docker without sudo

```bash
sudo usermod -aG docker $USER
```

Log out and log back in for the group change to take effect.

### Step 8: Verify installation

```bash
docker --version
docker compose version
docker run hello-world
```

**Official Documentation:** https://docs.docker.com/engine/install/ubuntu/


