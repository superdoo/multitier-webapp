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

    stage('Scan Backend Image with Trivy') {
      steps {
        sh """
          . ./minikube_docker_env.sh
          docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image --exit-code 0 --severity LOW,MEDIUM ${BACKEND_IMAGE}
          docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image --exit-code 0 --severity HIGH,CRITICAL ${BACKEND_IMAGE}
        """
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

    stage('Scan Frontend Image with Trivy') {
      steps {
        sh """
          . ./minikube_docker_env.sh
          docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image --exit-code 0 --severity LOW,MEDIUM ${FRONTEND_IMAGE}
          docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image --exit-code 0 --severity HIGH,CRITICAL ${FRONTEND_IMAGE}
        """
      }
    }

    stage('Scan Helm Charts (Trivy Config)') {
      steps {
        sh """
          docker run --rm -v "$PWD":/project -w /project aquasec/trivy config ${BACKEND_PATH}
          docker run --rm -v "$PWD":/project -w /project aquasec/trivy config ${FRONTEND_PATH}
          docker run --rm -v "$PWD":/project -w /project aquasec/trivy config ${DATABASE_PATH}
        """
      }
    }

    stage('Scan Secrets in Project') {
      steps {
        sh """
          docker run --rm -v "$PWD":/project -w /project aquasec/trivy fs . --scanners secret
        """
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
