pipeline {
  agent any

  environment {
    BACKEND_IMAGE = "mt-backend"
    FRONTEND_IMAGE = "mt-frontend"
    BACKEND_PATH = "helm/backend"
    FRONTEND_PATH = "helm/frontend"
    KUBECONFIG = "${HOME}/.kube/config"
  }

  stages {
    stage('Use Minikube Docker Daemon') {
      steps {
        script {
          // Prepare Minikube Docker environment in Jenkins shell
          env.MINIKUBE_DOCKER_ENV = sh(script: 'minikube docker-env --shell bash', returnStdout: true).trim()
        }
      }
    }

    stage('Build Backend Image') {
      steps {
        sh '''
        eval "$MINIKUBE_DOCKER_ENV"
        docker build -t mt-backend ${BACKEND_PATH}
        '''
      }
    }

    stage('Build Frontend Image') {
      steps {
        sh '''
        eval "$MINIKUBE_DOCKER_ENV"
        docker build -t mt-frontend ${FRONTEND_PATH}
        '''
      }
    }

    stage('Deploy Backend via Helm') {
      steps {
        sh '''
        helm upgrade --install mt-backend ${BACKEND_PATH} --namespace mt-backend --create-namespace
        '''
      }
    }

    stage('Deploy Frontend via Helm') {
      steps {
        sh '''
        helm upgrade --install mt-frontend ${FRONTEND_PATH} --namespace mt-frontend --create-namespace
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
