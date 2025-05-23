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
        sh """
          . ./minikube_docker_env.sh
          docker build -t ${BACKEND_IMAGE} ${BACKEND_PATH}
        """
      }
    }

    stage('Trivy Scan Backend') {
  steps {
    script {
      sh 'mkdir -p reports image-exports'

      sh """
        . ./minikube_docker_env.sh
        docker save -o image-exports/mt-backend.tar ${BACKEND_IMAGE}:latest
      """

      // High and Critical severity scan
      sh """
        docker run --rm \
          -v \$(pwd)/image-exports:/images \
          -v \$(pwd)/reports:/reports \
          aquasec/trivy:latest image --input /images/mt-backend.tar --format json --severity HIGH,CRITICAL -o /reports/trivy-backend-highcrit.json
      """

      // Low and Medium severity scan
      sh """
        docker run --rm \
          -v \$(pwd)/image-exports:/images \
          -v \$(pwd)/reports:/reports \
          aquasec/trivy:latest image --input /images/mt-backend.tar --format json --severity LOW,MEDIUM -o /reports/trivy-backend-lowmed.json
      """

      sh 'ls -lh reports'
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



    stage('Trivy Scan Frontend') {
      steps {
        script {
          sh 'mkdir -p reports image-exports'

          sh """
            . ./minikube_docker_env.sh
            docker save -o image-exports/mt-frontend.tar ${FRONTEND_IMAGE}:latest
          """

          // High and Critical severity scan
          sh """
            docker run --rm \
              -v \$(pwd)/image-exports:/images \
              -v \$(pwd)/reports:/reports \
              aquasec/trivy:latest image --input /images/mt-frontend.tar --format json --severity HIGH,CRITICAL -o /reports/trivy-frontend-highcrit.json
          """

          // Low and Medium severity scan
          sh """
            docker run --rm \
              -v \$(pwd)/image-exports:/images \
              -v \$(pwd)/reports:/reports \
              aquasec/trivy:latest image --input /images/mt-frontend.tar --format json --severity LOW,MEDIUM -o /reports/trivy-frontend-lowmed.json
          """

          sh 'ls -lh reports'
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
            sh """
              docker run --rm \\
                -v "\$PWD":/project \\
                -w /project \\
                aquasec/trivy config ${chart.path} \\
                --format json \\
                -o reports/trivy-config-${chart.name}.json
            """
          }
        }
      }
    }









stage('Scan Database Helm Chart (Trivy Config)') {
  steps {
    dir("${env.WORKSPACE}") {
      sh """
        docker run --rm -v "\$PWD":/project -w /project aquasec/trivy config ${DATABASE_PATH} \
          --format json -o reports/trivy-db-config.json
      """
    }
  }
}



    stage('Scan Secrets in Project') {
      steps {
        script {
          sh 'mkdir -p reports'

          sh """
            docker run --rm \\
              -v "\$PWD":/project \\
              -w /project \\
              aquasec/trivy fs /project \\
              --scanners secret \\
              --format json \\
              -o reports/trivy-secrets.json
          """
        }
      }
    }










  
    







    stage('Send Trivy Logs to Splunk') {
  steps {
    withCredentials([string(credentialsId: 'SPLUNK_HEC_TOKEN', variable: 'SPLUNK_HEC_TOKEN')]) {
      script {
        sh '''
          echo "Preparing Splunk payloads"

          # Backend
          jq -Rs '{event: .}' < reports/trivy-backend-lowmed.json > reports/splunk-backend-lowmed.json
          jq -Rs '{event: .}' < reports/trivy-backend-highcrit.json > reports/splunk-backend-highcrit.json

          # Frontend
          jq -Rs '{event: .}' < reports/trivy-frontend-lowmed.json > reports/splunk-frontend-lowmed.json
          jq -Rs '{event: .}' < reports/trivy-frontend-highcrit.json > reports/splunk-frontend-highcrit.json

          # Config scans
          jq -Rs '{event: .}' < reports/trivy-config-backend.json > reports/splunk-config-backend.json
          jq -Rs '{event: .}' < reports/trivy-config-frontend.json > reports/splunk-config-frontend.json
          jq -Rs '{event: .}' < reports/trivy-config-database.json > reports/splunk-config-database.json
          echo "Preparing Splunk payload for database config report"
          jq -Rs '{event: .}' < reports/trivy-db-config.json > reports/splunk-db-config.json

          # Secrets scan
          jq -Rs '{event: .}' < reports/trivy-secrets.json > reports/splunk-secrets.json

          echo "Sending all reports to Splunk"

          for file in reports/splunk-*.json; do
            echo "Sending $file"
            curl -k http://192.168.49.2:31002/services/collector \\
              -H "Authorization: Splunk $SPLUNK_HEC_TOKEN" \\
              -H "Content-Type: application/json" \\
              --data-binary @$file
          done
        '''
      }
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
      echo '✅ Multi-tier app successfully built, scanned, and deployed via Helm.'
    }
    failure {
      echo '❌ CI/CD pipeline failed.'
    }
  }
}
