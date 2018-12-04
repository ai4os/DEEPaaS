#!/usr/bin/groovy

@Library(['github.com/indigo-dc/jenkins-pipeline-library']) _

pipeline {
    agent {
        label 'python'
    }
    
    environment {
        dockerhub_repo = "indigodatacloud/deepaas"
        dockerhub_image_id = ""
    }

    stages {
        stage('Code fetching') {
            steps {
                checkout scm
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

        stage('Docker build') {
            when {
                anyOf {
                    branch 'master'
                    branch 'jenkins_integration_testing'
                    buildingTag()
                }
            }
            agent {
                label 'docker-build'
            }
            steps {
                checkout scm
                script {
                    env.dockerhub_image_id = DockerBuild(dockerhub_repo, env.BRANCH_NAME)
                }
            }
            post {
                failure {
                    DockerClean()
                }
                always {
                    cleanWs()
                }
            }
    }

        stage('Functional testing') {
            agent {
                label 'functional-testing'
            }
            steps {
                dir("integration_testing") {
                  sh 'docker run -d --name ${docker_image_name} -p 5000:5000 ${env.dockerhub_image_id}'
                }
            }
            post {
                always {
                  sh 'docker kill ${docker_image_name}'
                  sh 'docker rm ${docker_image_name}'
                }

            }
		}

        stage('Dependency check') {
            agent {
                label 'docker-build'
            }
            steps {
                checkout scm
                OWASPDependencyCheckRun("$WORKSPACE/DEEPaaS/deepaas", project="DEEPaaS")
            }
            post {
                always {
                    OWASPDependencyCheckPublish()
                    HTMLReport('DEEPaaS', 'dependency-check-report.html', 'OWASP Dependency Report')
                    deleteDir()
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
                    DockerPush(dockerhub_image_id)
                }
                failure {
                    DockerClean()
                }
                always {
                    cleanWs()
                }
            }
        }

        stage('PyPI delivery') {
            when {
                anyOf {
                    branch 'master'
                    buildingTag()
                }
            }
            steps {
                PyPIDeploy('deepaas', 'indigobot')
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
                    "Check new artifacts at:\n\t- Docker image: [${dockerhub_image_id}:${env.BRANCH_NAME}|https://hub.docker.com/r/${dockerhub_image_id}/tags/]\n",
                    ['wp3', 'preview-testbed', "DEEPaaS-${env.BRANCH_NAME}"],
                    'Task',
                    'mariojmdavid'
                )
            }
        }
    }
}
