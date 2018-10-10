#!/usr/bin/groovy

@Library(['github.com/indigo-dc/jenkins-pipeline-library']) _

pipeline {
    agent {
        label 'python'
    }
    
    environment {
        dockerhub_repo = "indigodatacloud/deepaas"
        dockerhub_image_id = ""
        tox_envs = """
[testenv:cobertura]
commands = py.test --cov=deepaas --cov-report=xml --cov-report=term-missing deepaas/tests
[testenv:bandit-report]
commands = 
    - mkdir /tmp/bandit
    - bandit -r deepaas -x tests -s B110,B410 -f html -o /tmp/bandit/index.html"""
    }

    stages {
        stage('Code fetching') {
            steps {
                checkout scm
            }
        }

        stage('Environment setup') {
            steps {
                PipRequirements(['pytest', 'pytest-cov'], 'test-requirements.txt')
                ToxConfig(tox_envs)
            }
            post {
                always {
                    archiveArtifacts artifacts: '*requirements.txt,*tox*.ini'
                }
            }
        }

        stage('Style analysis') {
            steps {
                ToxEnvRun('pep8')
            }
            post {
                always {
                    WarningsReport('Pep8')
                }
            }
        }

        stage('Unit testing coverage') {
            steps {
                ToxEnvRun('cover')
                ToxEnvRun('cobertura')
            }
            post {
                success {
                    HTMLReport('cover', 'index.html', 'coverage.py report')
                    CoberturaReport('**/coverage.xml')
                }
            }
        }

        stage('Metrics gathering') {
            agent {
                label 'sloc'
            }
            steps {
                checkout scm
                SLOCRun()
            }
            post {
                success {
                    SLOCPublish()
                }
            }
        }

        stage('Security scanner') {
            steps {
                ToxEnvRun('bandit-report')
                script {
                    if (currentBuild.result == 'FAILURE') {
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
            post {
                always {
                    HTMLReport("/tmp/bandit", 'index.html', 'Bandit report')
                }
            }
        }

        stage('DockerHub delivery') {
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
                    dockerhub_image_id = DockerBuild(dockerhub_repo, env.BRANCH_NAME)
                }
            }
            post {
                success {
                    DockerPush(image_id)
                }
                failure {
                    DockerClean()
                }
                always {
                    cleanWs()
                }
            }
        }

        stage('Notifications') {
            when {
                buildingTag()
            }
	    steps {
                JiraIssueNotification(
                    'DEEP',
                    'DPM',
                    '10204',
                    "[preview-testbed] New DEEP-as-a-Service version ${env.BRANCH_NAME} available",
                    'Check new artifacts at:\n\t- Docker image: ${dockerhub_image_id}\n',
                    ['wp3', 'preview-testbed', "DEEPaaS-${env.BRANCH_NAME}"],
		    'Task',
		    'mariojmdavid'
                )
            }
        }
    }
}
