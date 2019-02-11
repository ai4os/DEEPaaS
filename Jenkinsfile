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
                    HTMLReport(
                        "$WORKSPACE/DEEPaaS/deepaas",
                        'dependency-check-report.html',
                        'OWASP Dependency Report')
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
                    'mariojmdavid',
                    ['wgcastell',
                     'vkozlov',
                     'dlugo',
                     'keiichiito',
                     'laralloret',
                     'ignacioheredia']
                )
            }
        }
    }
}
