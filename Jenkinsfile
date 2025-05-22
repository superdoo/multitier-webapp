pipeline {
  agent any

  environment {
    BACKEND_IMAGE = "mt-backend"
    FRONTEND_IMAGE = "mt-frontend"
    BACKEND_PATH = "helm/backend"
    FRONTEND_PATH = "helm/frontend"
    DATABASE_PATH = "helm/postgresql"
    KUBECONFIG = "${HOME}/.kube/config"
    SPLUNK_HEC_URL = "http://192.168.49.2:31002/services/collector/event"
  }

  stages {
    stage('Use Minikube Docker Daemon') {
      steps {
        script {
          sh 'minikube status || minikube start'
          sh 'minikube docker-env --shell bash > minikube_docker_env.sh'
        }
      }
    }

    stage('Build Backend Image') {
      steps {
        sh """
          . ./minikube_docker_env.sh
          docker build -t ${BACKEND_IMAGE} ${BACKEND_PATH}
        """
      }
    }

    stage('Scan Backend Image with Trivy + Send to Splunk') {
      steps {
        withCredentials([string(credentialsId: 'SPLUNK_HEC_TOKEN', variable: 'SPLUNK_TOKEN')]) {
          sh """
            . ./minikube_docker_env.sh

            docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
              -v \$PWD:/report aquasec/trivy image --format json -o /report/backend-report.json ${BACKEND_IMAGE}

            echo '{"event":'\\\$(cat /report/backend-report.json)', "sourcetype": "trivy", "source": "backend-scan", "host": "jenkins"}' > /tmp/splunk_payload.json

            curl -s -k -X POST "\\${SPLUNK_HEC_URL}" \\
              -H "Authorization: Splunk \\$SPLUNK_TOKEN" \\
              -H "Content-Type: application/json" \\
              -d @/tmp/splunk_payload.json
          """
        }
      }
    }

    stage('Build Frontend Image') {
      steps {
        sh """
          . ./minikube_docker_env.sh
          docker build -t ${FRONTEND_IMAGE} ${FRONTEND_PATH}
        """
      }
    }

    stage('Scan Frontend Image with Trivy + Send to Splunk') {
      steps {
        withCredentials([string(credentialsId: 'SPLUNK_HEC_TOKEN', variable: 'SPLUNK_TOKEN')]) {
          sh """
            . ./minikube_docker_env.sh

            docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
              -v \$PWD:/report aquasec/trivy image --format json -o /report/frontend-report.json ${FRONTEND_IMAGE}

            echo '{"event":'\\\$(cat /report/frontend-report.json)', "sourcetype": "trivy", "source": "frontend-scan", "host": "jenkins"}' > /tmp/splunk_payload.json

            curl -s -k -X POST "\\${SPLUNK_HEC_URL}" \\
              -H "Authorization: Splunk \\$SPLUNK_TOKEN" \\
              -H "Content-Type: application/json" \\
              -d @/tmp/splunk_payload.json
          """
        }
      }
    }

    stage('Scan Helm Charts (Trivy Config)') {
      steps {
        dir("${env.WORKSPACE}") {
          sh """
            docker run --rm -v "\$PWD":/project -w /project aquasec/trivy config ${BACKEND_PATH}
            docker run --rm -v "\$PWD":/project -w /project aquasec/trivy config ${FRONTEND_PATH}
            docker run --rm -v "\$PWD":/project -w /project aquasec/trivy config ${DATABASE_PATH}
          """
        }
      }
    }

    stage('Scan Secrets in Project') {
      steps {
        dir("${env.WORKSPACE}") {
          sh """
            docker run --rm -v "\$PWD":/project -w /project aquasec/trivy fs . --scanners secret
          """
        }
      }
    }

    stage('Deploy Backend via Helm') {
      steps {
        sh """
          helm upgrade --install ${BACKEND_IMAGE} ${BACKEND_PATH} \\
            --namespace ${BACKEND_IMAGE} --create-namespace \\
            -f ${BACKEND_PATH}/values.yaml
        """
      }
    }

    stage('Deploy Frontend via Helm') {
      steps {
        sh """
          helm upgrade --install ${FRONTEND_IMAGE} ${FRONTEND_PATH} \\
            --namespace ${FRONTEND_IMAGE} --create-namespace \\
            -f ${FRONTEND_PATH}/values.yaml
        """
      }
    }

    stage('Deploy Database via Helm') {
      steps {
        sh """
          helm upgrade --install mt-database ${DATABASE_PATH} \\
            --namespace mt-database --create-namespace \\
            -f ${DATABASE_PATH}/values.yaml
        """
      }
    }
  }

  post {
    success {
      echo '✅ Multi-tier app successfully built, scanned, deployed, and logs sent to Splunk.'
    }
    failure {
      echo '❌ CI/CD pipeline failed.'
    }
  }
}
