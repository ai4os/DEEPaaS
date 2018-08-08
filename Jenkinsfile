pipeline {
    agent any
    
	environment {
        docker_alias = "docker -H tcp://127.0.0.1:2376"
        docker_repo = "indigodatacloud/deepaas"
    }

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
                    echo 'Parsing pep8 logs..'
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
                echo 'Computing unit testing coverage..'
                sh 'tox -e cover'

                echo 'Generating HTML report..'
                publishHTML([allowMissing: false,
                             alwaysLinkToLastBuild: false,
                             keepAll: false,
                             reportDir: 'cover',
                             reportFiles: 'index.html',
                             reportName: 'Coverage report',
                             reportTitles: ''])

                echo 'Generating Cobertura report..'
                writeFile file: 'tox.ini.cobertura', text: '''[tox]
envlist = cobertura

[testenv]
usedevelop = True
install_command = pip install -U {opts} {packages}
setenv =
   VIRTUAL_ENV={envdir}
deps = pytest-cov
       nose
       -r{toxinidir}/requirements.txt
       -r{toxinidir}/test-requirements.txt
commands = py.test --cov=deepaas --cov-report=xml --cov-report=term-missing deepaas/tests'''
                sh 'tox -c tox.ini.cobertura'
                cobertura autoUpdateHealth: false,
                          autoUpdateStability: false,
                          coberturaReportFile: '**/coverage.xml',
                          conditionalCoverageTargets: '70, 0, 0',
                          failUnhealthy: false,
                          failUnstable: false,
                          lineCoverageTargets: '80, 0, 0',
                          maxNumberOfBuilds: 0,
                          methodCoverageTargets: '80, 0, 0',
                          onlyStable: false,
                          sourceEncoding: 'ASCII',
                          zoomCoverageChart: false
            }
        }
        
        stage('Build and Push Docker image/s') {
            when {
                anyOf {
                    branch 'master'
                    buildingTag()
                }
            }
            agent {
                label 'docker-build'
            }
            steps {
                checkout scm
                script {
                    if (env.BRANCH_NAME == 'master') {
                        IMAGE_ID = env.docker_repo + ':latest'
                    }
                    else {
                        IMAGE_ID = env.docker_repo + ':' + env.TAG_NAME
                    }
                }
                sh "${docker_alias} build --force-rm -t $IMAGE_ID ./docker"
            }
            post {
                success {
                    echo "Pushing Docker image ${IMAGE_ID}.."
                    withDockerRegistry([credentialsId: 'indigobot', url: '']) {
                        sh "${docker_alias} push $IMAGE_ID"
                    }
                }
                failure {
                    echo 'Docker image building failed, removing dangling images..'
                    sh '${docker_alias} rmi \$(\${docker_alias} images -f "dangling=true" -q)'
                }
                always {
                    cleanWs()
                }
            }
        } // docker stage

    }
}
