pipeline {
    agent any
    
    stages {
        stage('Style') {
            steps {
                checkout scm
                echo 'Running flake8..'
                sh 'tox -e pep8'
            }
        }
    }
}
