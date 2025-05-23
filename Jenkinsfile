pipeline {
  agent any

  environment {
    BACKEND_IMAGE = "mt-backend"
    FRONTEND_IMAGE = "mt-frontend"
    BACKEND_PATH = "helm/backend"
    FRONTEND_PATH = "helm/frontend"
    DATABASE_PATH = "helm/postgresql"
    KUBECONFIG = "${HOME}/.kube/config"
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
        sh '''
          echo "\n==== Building Backend Docker Image ===="
          . ./minikube_docker_env.sh
          docker build -t ${BACKEND_IMAGE} ${BACKEND_PATH}
        '''
      }
    }

    stage('Trivy Scan Backend') {
      steps {
        script {
          sh 'mkdir -p reports image-exports logs'

          sh '''
            echo "\n==== Saving Backend Image ===="
            . ./minikube_docker_env.sh
            docker save -o image-exports/mt-backend.tar ${BACKEND_IMAGE}:latest

            echo "\n==== Trivy Scan: HIGH/CRITICAL ===="
            docker run --rm \
              -v $(pwd)/image-exports:/images \
              -v $(pwd)/reports:/reports \
              aquasec/trivy:latest image --input /images/mt-backend.tar \
              --format json --severity HIGH,CRITICAL -o /reports/trivy-backend-highcrit.json | tee logs/trivy-backend-highcrit.log

            echo "\n==== Trivy Scan: LOW/MEDIUM ===="
            docker run --rm \
              -v $(pwd)/image-exports:/images \
              -v $(pwd)/reports:/reports \
              aquasec/trivy:latest image --input /images/mt-backend.tar \
              --format json --severity LOW,MEDIUM -o /reports/trivy-backend-lowmed.json | tee logs/trivy-backend-lowmed.log
          '''
        }
      }
    }

    stage('Build Frontend Image') {
      steps {
        sh '''
          echo "\n==== Building Frontend Docker Image ===="
          . ./minikube_docker_env.sh
          docker build -t ${FRONTEND_IMAGE} ${FRONTEND_PATH}
        '''
      }
    }

    stage('Trivy Scan Frontend') {
      steps {
        script {
          sh 'mkdir -p reports image-exports logs'

          sh '''
            echo "\n==== Saving Frontend Image ===="
            . ./minikube_docker_env.sh
            docker save -o image-exports/mt-frontend.tar ${FRONTEND_IMAGE}:latest

            echo "\n==== Trivy Scan: HIGH/CRITICAL ===="
            docker run --rm \
              -v $(pwd)/image-exports:/images \
              -v $(pwd)/reports:/reports \
              aquasec/trivy:latest image --input /images/mt-frontend.tar \
              --format json --severity HIGH,CRITICAL -o /reports/trivy-frontend-highcrit.json | tee logs/trivy-frontend-highcrit.log

            echo "\n==== Trivy Scan: LOW/MEDIUM ===="
            docker run --rm \
              -v $(pwd)/image-exports:/images \
              -v $(pwd)/reports:/reports \
              aquasec/trivy:latest image --input /images/mt-frontend.tar \
              --format json --severity LOW,MEDIUM -o /reports/trivy-frontend-lowmed.json | tee logs/trivy-frontend-lowmed.log
          '''
        }
      }
    }

    stage('Scan Helm Charts (Trivy Config)') {
      steps {
        script {
          sh 'mkdir -p reports'
          def charts = [
            [name: "backend", path: "${BACKEND_PATH}"],
            [name: "frontend", path: "${FRONTEND_PATH}"],
            [name: "database", path: "${DATABASE_PATH}"]
          ]
          charts.each { chart ->
            sh '''
              echo "\n==== Trivy Config Scan: ${chart.name} ===="
              docker run --rm \
                -v "$PWD":/project \
                -w /project \
                aquasec/trivy config ${chart.path} \
                --format json -o reports/trivy-config-${chart.name}.json | tee logs/trivy-config-${chart.name}.log
            '''
          }
        }
      }
    }

    stage('Scan Secrets in Project') {
      steps {
        script {
          sh 'mkdir -p reports'
          sh '''
            echo "\n==== Trivy Secret Scan ===="
            docker run --rm \
              -v "$PWD":/project \
              -w /project \
              aquasec/trivy fs /project \
              --scanners secret \
              --format json -o reports/trivy-secrets.json | tee logs/trivy-secrets.log
          '''
        }
      }
    }

    stage('Send Trivy Logs to Splunk') {
      steps {
        withCredentials([string(credentialsId: 'SPLUNK_HEC_TOKEN', variable: 'SPLUNK_HEC_TOKEN')]) {
          script {
            sh '''
              echo "\n==== Preparing JSON Payloads for Splunk ===="
              for f in reports/*.json; do
                out="reports/splunk-$(basename $f)"
                jq -Rs '{event: .}' < "$f" > "$out"
              done

              echo "\n==== Sending Payloads to Splunk ===="
              for f in reports/splunk-*.json; do
                echo "Sending $f"
                curl -s -o /dev/null -w "%{http_code}\n" -k http://192.168.49.2:31002/services/collector \
                  -H "Authorization: Splunk $SPLUNK_HEC_TOKEN" \
                  -H "Content-Type: application/json" \
                  --data-binary @$f
              done
            '''
          }
        }
      }
    }

    stage('Deploy Backend via Helm') {
      steps {
        sh '''
          echo "\n==== Deploying Backend ===="
          helm upgrade --install ${BACKEND_IMAGE} ${BACKEND_PATH} \
            --namespace ${BACKEND_IMAGE} --create-namespace \
            -f ${BACKEND_PATH}/values.yaml
        '''
      }
    }

    stage('Deploy Frontend via Helm') {
      steps {
        sh '''
          echo "\n==== Deploying Frontend ===="
          helm upgrade --install ${FRONTEND_IMAGE} ${FRONTEND_PATH} \
            --namespace ${FRONTEND_IMAGE} --create-namespace \
            -f ${FRONTEND_PATH}/values.yaml
        '''
      }
    }

    stage('Deploy Database via Helm') {
      steps {
        sh '''
          echo "\n==== Deploying Database ===="
          helm upgrade --install mt-database ${DATABASE_PATH} \
            --namespace mt-database --create-namespace \
            -f ${DATABASE_PATH}/values.yaml
        '''
      }
    }
  }

  post {
    success {
      echo '✅ Multi-tier app successfully built, scanned, and deployed via Helm.'
    }
    failure {
      echo '❌ CI/CD pipeline failed.'
    }
  }
}
