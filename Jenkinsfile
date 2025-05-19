pipeline {
  agent any

  environment {
    BACKEND_IMAGE = "mt-backend"
    FRONTEND_IMAGE = "mt-frontend"
    BACKEND_PATH = "helm/backend"
    FRONTEND_PATH = "helm/frontend"
    KUBECONFIG = "${HOME}/.kube/config"
    MINIKUBE_DOCKER_ENV = ''
  }

  stages {
    stage('Use Minikube Docker Daemon') {
      steps {
        script {
          try {
            // Try to get minikube docker environment setup commands
            def dockerEnvOutput = sh(script: 'minikube docker-env --shell bash', returnStdout: true).trim()
            env.MINIKUBE_DOCKER_ENV = dockerEnvOutput
            echo "Minikube docker-env loaded successfully."
          } catch (Exception e) {
            echo "⚠️ Warning: Failed to get minikube docker-env. Docker build stages may fail if Docker is not accessible."
            env.MINIKUBE_DOCKER_ENV = ''
          }
        }
      }
    }

    stage('Build Backend Image') {
      steps {
        script {
          if (env.MINIKUBE_DOCKER_ENV) {
            sh '''
              eval "$MINIKUBE_DOCKER_ENV"
              docker build -t ${BACKEND_IMAGE} ${BACKEND_PATH}
            '''
          } else {
            echo "Skipping Docker build for backend: Minikube Docker environment not set."
          }
        }
      }
    }

    stage('Build Frontend Image') {
      steps {
        script {
          if (env.MINIKUBE_DOCKER_ENV) {
            sh '''
              eval "$MINIKUBE_DOCKER_ENV"
              docker build -t ${FRONTEND_IMAGE} ${FRONTEND_PATH}
            '''
          } else {
            echo "Skipping Docker build for frontend: Minikube Docker environment not set."
          }
        }
      }
    }

    stage('Deploy Backend via Helm') {
      steps {
        sh '''
          helm upgrade --install ${BACKEND_IMAGE} ${BACKEND_PATH} --namespace mt-backend --create-namespace
        '''
      }
    }

    stage('Deploy Frontend via Helm') {
      steps {
        sh '''
          helm upgrade --install ${FRONTEND_IMAGE} ${FRONTEND_PATH} --namespace mt-frontend --create-namespace
        '''
      }
    }
  }

  post {
    success {
      echo '✅ Multi-tier app successfully built and deployed via Helm.'
    }
    failure {
      echo '❌ CI/CD pipeline failed.'
    }
  }
}
