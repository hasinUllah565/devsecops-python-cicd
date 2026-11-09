pipeline {
    agent any

    environment {
        SONAR_HOME = tool "Sonar"
    }

    stages {
        stage("Code Clone from Github") {
            steps {
                git url: "https://github.com/hasinUllah565/devsecops-python-cicd.git", branch: "main"
            }
        }

        stage("SonarQube Quality Analysis") {
            steps {
                withSonarQubeEnv("Sonar") {
                    sh "$SONAR_HOME/bin/sonar-scanner -Dsonar.projectName=devsecops-python-cicd -Dsonar.projectKey=devsecops-python-cicd"
                }
            }
        }

        stage("OWASP Dependency check") {
            steps {
                dependencyCheck additionalArguments: "--scan ./", odcInstallation: 'dc'
                dependencyCheckPublisher pattern: "**/dependency-check-report.xml"
            }
        }

        stage("Sonar Quality Scan") {
            steps {
                timeout(time: 2, unit: "MINUTES") {
                    waitForQualityGate abortPipeline: false
                }
            }
        }

        stage("Trivy security scanner") {
            steps {
                sh "trivy fs --format table -o trivy-fs-report.html ."
            }
        }
                // NEW DEPLOYMENT STAGE
        stage("Deploy Flask Application") {
            steps {
                sh '''
                    docker compose down --remove-orphans
                    docker compose up -d --build
                '''
            }
        }
    }
}
