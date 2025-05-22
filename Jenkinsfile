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
            set -eux

            # Load Minikube docker environment variables
            . ./minikube_docker_env.sh

            echo "[DEBUG] WORKSPACE=$WORKSPACE"
            REPORT_DIR="${WORKSPACE}/reports"
            echo "[DEBUG] REPORT_DIR=$REPORT_DIR"

            echo "[DEBUG] Listing reports dir before scan:"
            ls -la "$REPORT_DIR" || echo "[DEBUG] Reports directory does not exist yet"

            # Create reports directory with permissions
            echo "[INFO] Creating report dir at: $REPORT_DIR"
            mkdir -p "$REPORT_DIR"
            chmod -R 777 "$REPORT_DIR"
            ls -la "$REPORT_DIR"

            echo "[INFO] Running Trivy scan on ${BACKEND_IMAGE}..."
            docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
              -v "$REPORT_DIR":/report aquasec/trivy image --format json -o /report/backend-report.json ${BACKEND_IMAGE}

            echo "[DEBUG] Listing reports dir after scan:"
            ls -la "$REPORT_DIR"

            REPORT_PATH="$REPORT_DIR/backend-report.json"
            echo "[INFO] Report file contents:"
            cat "$REPORT_PATH" || echo "[ERROR] Report not found!"

            PAYLOAD="/tmp/splunk_backend_payload.json"
            jq -n --slurpfile report "$REPORT_PATH" \\
              --arg sourcetype "trivy" --arg source "backend-scan" --arg host "jenkins" \\
              '{event: $report[0], sourcetype: $sourcetype, source: $source, host: $host}' > $PAYLOAD

            echo "[INFO] Posting to Splunk at ${SPLUNK_HEC_URL}"
            curl -v -k -X POST "${SPLUNK_HEC_URL}" \\
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

    // You can add similar logging for frontend scan later if needed

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
