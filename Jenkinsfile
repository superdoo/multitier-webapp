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

    stage('Build Frontend Image') {
      steps {
        sh """
          . ./minikube_docker_env.sh
          docker build -t ${FRONTEND_IMAGE} ${FRONTEND_PATH}
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
            --namespace ${FRONTEND_IMAGE} --create-namespace
        """
      }
    }

    stage('Deploy Database via Helm') {
      steps {
        sh """
          helm upgrade --install mt-database ${DATABASE_PATH} \\
            --namespace mt-database --create-namespace
        """
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
