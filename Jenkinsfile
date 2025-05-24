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


pipeline {
  agent any

  environment {
    SONAR_HOST_URL = 'http://localhost:9000'
  }

  stages {
    stage('SonarQube Scan') {
      steps {
        withCredentials([string(credentialsId: 'multitierwebapp', variable: 'SONAR_TOKEN')]) {
          sh """
            sonar-scanner \
              -Dsonar.projectKey=multitier-web-app \
              -Dsonar.sources=. \
              -Dsonar.host.url=${SONAR_HOST_URL} \
              -Dsonar.login=${SONAR_TOKEN}
          """
        }
      }
    }
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
              echo "Preparing and sending structured Splunk logs"

              for file in reports/trivy-*.json; do
                echo "Processing $file"

                jq -c '.Results[]?.Vulnerabilities[]? | {
                  event: {
                    Target: .Target,
                    VulnerabilityID: .VulnerabilityID,
                    PkgName: .PkgName,
                    InstalledVersion: .InstalledVersion,
                    FixedVersion: .FixedVersion,
                    Severity: .Severity,
                    Title: .Title,
                    Description: .Description
                  }
                }' "$file" > reports/tmp-splunk-events.json || true

                if [ -s reports/tmp-splunk-events.json ]; then
                  echo "Sending logs from $file to Splunk"
                  while IFS= read -r line; do
                    curl -k http://192.168.49.2:31002/services/collector \
                      -H "Authorization: Splunk $SPLUNK_HEC_TOKEN" \
                      -H "Content-Type: application/json" \
                      --data-binary "$line"
                  done < reports/tmp-splunk-events.json
                else
                  echo "No vulnerabilities to send from $file"
                fi
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
