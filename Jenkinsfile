pipeline {
    agent any
    
    stages {
		stage('Fetch code') {
        	steps {
				checkout scm
			}
		}

        stage('Style Analysis') {
            steps {
                echo 'Running flake8..'
                sh 'tox -e pep8'
				//timeout(time: 5, unit: 'MINUTES') {
				//	sh 'bin/code-analysis' step([$class: 'WarningsPublisher',
				//		parserConfigurations: [[
				//			parserName: 'Pep8', pattern: 'parts/code-analysis/flake8.log'
				//		]], unstableTotalAll: '0', usePreviousBuildAsReference: true

				//	])
				//}
            }
        }
        stage('Unit tests') {
            steps {
                checkout scm
                echo 'Computing coverage..'
            }
        }
    }
}
