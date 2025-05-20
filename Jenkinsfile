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
    stage('Build Backend Image') {
      steps {
        sh '''
          eval $(minikube docker-env)
          docker build -t ${BACKEND_IMAGE}:latest ${BACKEND_PATH}
        '''
      }
    }

    stage('Build Frontend Image') {
      steps {
        sh '''
          eval $(minikube docker-env)
          docker build -t ${FRONTEND_IMAGE}:latest ${FRONTEND_PATH}
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
