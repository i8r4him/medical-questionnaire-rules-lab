pipeline {
    agent any
    options {
        timeout(time: 10, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    stages {
        stage('Umgebung') {
            steps {
                sh 'python3 -m venv .venv'
                sh '.venv/bin/python -m pip install -r requirements-dev.txt'
                sh 'rm -rf reports/unit reports/acceptance reports/demo.json'
            }
        }
        stage('Regel- und Integrationstests') {
            steps {
                sh '.venv/bin/python -m xmlrunner discover -s tests -o reports/unit -v'
            }
            post {
                always { junit 'reports/unit/*.xml' }
            }
        }
        stage('Abnahmetests') {
            steps {
                sh '.venv/bin/python -m behave --junit --junit-directory reports/acceptance'
            }
            post {
                always { junit 'reports/acceptance/*.xml' }
            }
        }
        stage('Demo') {
            steps {
                sh '.venv/bin/python -m health_rules data/cases.json --output reports/demo.json'
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'reports/**/*.xml,reports/demo.json', allowEmptyArchive: true
        }
    }
}
