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
    REPORTS_DIR = "${WORKSPACE}/reports"
  }

  stages {
    stage('Prepare Report Directory') {
      steps {
        sh '''
          mkdir -p ${REPORTS_DIR}
          chmod -R 777 ${REPORTS_DIR}
        '''
      }
    }

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
        sh '''#!/bin/bash
          . ./minikube_docker_env.sh
          docker build -t ${BACKEND_IMAGE} ${BACKEND_PATH}
        '''
      }
    }

    stage('Scan Backend Image with Trivy + Send to Splunk') {
      steps {
        withCredentials([string(credentialsId: 'SPLUNK_HEC_TOKEN', variable: 'SPLUNK_TOKEN')]) {
          sh '''#!/bin/bash
            . ./minikube_docker_env.sh

            REPORT_PATH="${REPORTS_DIR}/backend-report.json"
            PAYLOAD="/tmp/splunk_backend_payload.json"

            docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
              -v ${REPORTS_DIR}:/report aquasec/trivy image --format json -o /report/backend-report.json ${BACKEND_IMAGE}

            jq -n --slurpfile report "$REPORT_PATH" \\
              --arg sourcetype "trivy" --arg source "backend-scan" --arg host "jenkins" \\
              '{event: $report[0], sourcetype: $sourcetype, source: $source, host: $host}' > $PAYLOAD

            curl -s -k -X POST "${SPLUNK_HEC_URL}" \\
              -H "Authorization: Splunk ${SPLUNK_TOKEN}" \\
              -H "Content-Type: application/json" \\
              -d @$PAYLOAD
          '''
        }
      }
    }

    stage('Build Frontend Image') {
      steps {
        sh '''#!/bin/bash
          . ./minikube_docker_env.sh
          docker build -t ${FRONTEND_IMAGE} ${FRONTEND_PATH}
        '''
      }
    }

    stage('Scan Frontend Image with Trivy + Send to Splunk') {
      steps {
        withCredentials([string(credentialsId: 'SPLUNK_HEC_TOKEN', variable: 'SPLUNK_TOKEN')]) {
          sh '''#!/bin/bash
            . ./minikube_docker_env.sh

            REPORT_PATH="${REPORTS_DIR}/frontend-report.json"
            PAYLOAD="/tmp/splunk_frontend_payload.json"

            docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
              -v ${REPORTS_DIR}:/report aquasec/trivy image --format json -o /report/frontend-report.json ${FRONTEND_IMAGE}

            jq -n --slurpfile report "$REPORT_PATH" \\
              --arg sourcetype "trivy" --arg source "frontend-scan" --arg host "jenkins" \\
              '{event: $report[0], sourcetype: $sourcetype, source: $source, host: $host}' > $PAYLOAD

            curl -s -k -X POST "${SPLUNK_HEC_URL}" \\
              -H "Authorization: Splunk ${SPLUNK_TOKEN}" \\
              -H "Content-Type: application/json" \\
              -d @$PAYLOAD
          '''
        }
      }
    }

    // (Keep the rest of your original stages unchanged)
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
