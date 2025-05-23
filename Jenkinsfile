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
























stage('Send Trivy Logs to Splunk') {
  steps {
    withCredentials([string(credentialsId: 'SPLUNK_HEC_TOKEN', variable: 'SPLUNK_HEC_TOKEN')]) {
      sh """
        echo "=== Trivy Report Files Location Check ==="
        echo "Expected file: reports/trivy-backend-lowmed.json"
        echo "Expected file: reports/trivy-backend-highcrit.json"
        echo "Current directory:"
        pwd
        echo "Listing workspace contents:"
        ls -lh
        echo "Listing reports/ directory contents:"
        ls -lh reports/

        if [ ! -f "reports/trivy-backend-lowmed.json" ]; then
          echo "ERROR: reports/trivy-backend-lowmed.json not found!"
          exit 1
        fi

        if [ ! -f "reports/trivy-backend-highcrit.json" ]; then
          echo "ERROR: reports/trivy-backend-highcrit.json not found!"
          exit 1
        fi

        echo "=== Displaying first 10 lines of each file ==="
        echo "--- reports/trivy-backend-lowmed.json ---"
        head -n 10 reports/trivy-backend-lowmed.json

        echo "--- reports/trivy-backend-highcrit.json ---"
        head -n 10 reports/trivy-backend-highcrit.json

        echo "=== Sending to Splunk ==="

        # Low/Medium
        curl -k http://192.168.49.2:31002/services/collector \\
          -H "Authorization: Splunk $SPLUNK_HEC_TOKEN" \\
          -H "Content-Type: application/json" \\
          --data-binary "@reports/trivy-backend-lowmed.json"

        # High/Critical
        curl -k http://192.168.49.2:31002/services/collector \\
          -H "Authorization: Splunk $SPLUNK_HEC_TOKEN" \\
          -H "Content-Type: application/json" \\
          --data-binary "@reports/trivy-backend-highcrit.json"
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

    // stage('Scan Frontend Image with Trivy') {
    //   steps {
    //     sh """
    //       . ./minikube_docker_env.sh
    //       docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image --exit-code 0 --severity LOW,MEDIUM ${FRONTEND_IMAGE}
    //       docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image --exit-code 0 --severity HIGH,CRITICAL ${FRONTEND_IMAGE}
    //     """
    //   }
    // }

    // stage('Scan Helm Charts (Trivy Config)') {
    //   steps {
    //     dir("${env.WORKSPACE}") {
    //       sh """
    //         docker run --rm -v "\$PWD":/project -w /project aquasec/trivy config ${BACKEND_PATH}
    //         docker run --rm -v "\$PWD":/project -w /project aquasec/trivy config ${FRONTEND_PATH}
    //         docker run --rm -v "\$PWD":/project -w /project aquasec/trivy config ${DATABASE_PATH}
    //       """
    //     }
    //   }
    // }

    // stage('Scan Secrets in Project') {
    //   steps {
    //     dir("${env.WORKSPACE}") {
    //       sh """
    //         docker run --rm -v "\$PWD":/project -w /project aquasec/trivy fs . --scanners secret
    //       """
    //     }
    //   }
    // }

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
