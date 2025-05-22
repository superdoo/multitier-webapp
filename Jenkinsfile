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
    REPORT_DIR = "/home/reports"
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

            mkdir -p ${REPORT_DIR}
            BACKEND_REPORT="${REPORT_DIR}/backend-report.json"
            BACKEND_PAYLOAD="/tmp/splunk_backend_payload.json"

            docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
              -v ${REPORT_DIR}:/reports aquasec/trivy image \\
              --format json -o /reports/backend-report.json ${BACKEND_IMAGE}

            echo "📄 Trivy backend scan result:"
            cat $BACKEND_REPORT

            jq -n --slurpfile report $BACKEND_REPORT \\
              --arg sourcetype "trivy" --arg source "backend-scan" --arg host "jenkins" \\
              '{event: $report[0], sourcetype: $sourcetype, source: $source, host: $host}' > $BACKEND_PAYLOAD

            echo "📦 Sending to Splunk:"
            cat $BACKEND_PAYLOAD

            curl -v -k -X POST "${SPLUNK_HEC_URL}" \\
              -H "Authorization: Splunk ${SPLUNK_TOKEN}" \\
              -H "Content-Type: application/json" \\
              -d @$BACKEND_PAYLOAD
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

            mkdir -p ${REPORT_DIR}
            FRONTEND_REPORT="${REPORT_DIR}/frontend-report.json"
            FRONTEND_PAYLOAD="/tmp/splunk_frontend_payload.json"

            docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
              -v ${REPORT_DIR}:/reports aquasec/trivy image \\
              --format json -o /reports/frontend-report.json ${FRONTEND_IMAGE}

            echo "📄 Trivy frontend scan result:"
            cat $FRONTEND_REPORT

            jq -n --slurpfile report $FRONTEND_REPORT \\
              --arg sourcetype "trivy" --arg source "frontend-scan" --arg host "jenkins" \\
              '{event: $report[0], sourcetype: $sourcetype, source: $source, host: $host}' > $FRONTEND_PAYLOAD

            echo "📦 Sending to Splunk:"
            cat $FRONTEND_PAYLOAD

            curl -v -k -X POST "${SPLUNK_HEC_URL}" \\
              -H "Authorization: Splunk ${SPLUNK_TOKEN}" \\
              -H "Content-Type: application/json" \\
              -d @$FRONTEND_PAYLOAD
          '''
        }
      }
    }

    stage('Scan Helm Charts (Trivy Config)') {
      steps {
        dir("${env.WORKSPACE}") {
          sh '''#!/bin/bash
            docker run --rm -v "$PWD":/project -w /project aquasec/trivy config ${BACKEND_PATH}
            docker run --rm -v "$PWD":/project -w /project aquasec/trivy config ${FRONTEND_PATH}
            docker run --rm -v "$PWD":/project -w /project aquasec/trivy config ${DATABASE_PATH}
          '''
        }
      }
    }

    stage('Scan Secrets in Project') {
      steps {
        dir("${env.WORKSPACE}") {
          sh '''#!/bin/bash
            docker run --rm -v "$PWD":/project -w /project aquasec/trivy fs . --scanners secret
          '''
        }
      }
    }

    stage('Deploy Backend via Helm') {
      steps {
        sh '''#!/bin/bash
          helm upgrade --install ${BACKEND_IMAGE} ${BACKEND_PATH} \\
            --namespace ${BACKEND_IMAGE} --create-namespace \\
            -f ${BACKEND_PATH}/values.yaml
        '''
      }
    }

    stage('Deploy Frontend via Helm') {
      steps {
        sh '''#!/bin/bash
          helm upgrade --install ${FRONTEND_IMAGE} ${FRONTEND_PATH} \\
            --namespace ${FRONTEND_IMAGE} --create-namespace \\
            -f ${FRONTEND_PATH}/values.yaml
        '''
      }
    }

    stage('Deploy Database via Helm') {
      steps {
        sh '''#!/bin/bash
          helm upgrade --install mt-database ${DATABASE_PATH} \\
            --namespace mt-database --create-namespace \\
            -f ${DATABASE_PATH}/values.yaml
        '''
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
