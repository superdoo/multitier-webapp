pipeline {
    agent any

    environment {
        IMAGE_TAG = "latest"
        BACKEND_IMAGE = "mt-backend:${IMAGE_TAG}"
        FRONTEND_IMAGE = "mt-frontend:${IMAGE_TAG}"
        REPORTS_DIR = "${WORKSPACE}/reports"
        SPLUNK_HEC_TOKEN = credentials('splunk-hec-token')
        SPLUNK_HEC_URL = 'http://localhost:31001/services/collector'
    }

    stages {
        stage('Clone Repo') {
            steps {
                git url: 'https://github.com/your-repo/multi-tier-web-app.git', branch: 'main'
            }
        }

        stage('Build Backend Image') {
            steps {
                dir('backend') {
                    sh 'docker build -t ${BACKEND_IMAGE} .'
                }
            }
        }

        stage('Build Frontend Image') {
            steps {
                dir('frontend') {
                    sh 'docker build -t ${FRONTEND_IMAGE} .'
                }
            }
        }

        stage('Security Scan Backend') {
            steps {
                sh '''
                mkdir -p ${REPORTS_DIR}
                trivy image --format json --output ${REPORTS_DIR}/backend_trivy_report.json ${BACKEND_IMAGE}
                cat ${REPORTS_DIR}/backend_trivy_report.json
                '''
            }
        }

        stage('Send Backend Report to Splunk') {
            steps {
                sh '''
                curl -k -s -o /dev/null -w "%{http_code}\\n" -X POST ${SPLUNK_HEC_URL} \
                -H "Authorization: Splunk ${SPLUNK_HEC_TOKEN}" \
                -H "Content-Type: application/json" \
                -d @${REPORTS_DIR}/backend_trivy_report.json
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/*.json', fingerprint: true
        }
    }
}
