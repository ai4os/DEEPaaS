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
				timeout(time: 5, unit: 'MINUTES') {
					sh 'tox -e pep8' 
                    step([$class: 'WarningsPublisher',
						parserConfigurations: [[
							parserName: 'Pep8', pattern: '.tox/pep8/log/*.log'
						]], unstableTotalAll: '0', usePreviousBuildAsReference: true

					])
				}
            }
        }
        stage('Unit tests') {
            steps {
                echo 'Computing coverage..'
            }
        }
    }
}
