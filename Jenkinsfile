#!/usr/bin/groovy

@Library(['github.com/indigo-dc/jenkins-pipeline-library@1.4.0']) _

pipeline {
    agent {
        label 'python3.8'
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
                ToxEnvRun('flake8')
            }
            post {
                always {
                    recordIssues(tools: [flake8()])
                }
            }
        }

        stage('Unit testing coverage') {
            steps {
                ToxEnvRun('cover')
                ToxEnvRun('cobertura')
            }
            // post {
            //     success {
            //         HTMLReport('cover', 'index.html', 'coverage.py report')
            //         CoberturaReport('**/coverage.xml')
            //     }
            // }
        }

        stage('Dependency check') {
            steps {
                ToxEnvRun('pip-missing-reqs')
            }
        }

        // stage('DockerHub delivery') {
        //     when {
        //         anyOf {
        //             branch 'master'
        //             buildingTag()
        //         }
        //     }
        //     agent {
        //         label 'docker-build'
        //     }
        //     steps {
        //         checkout scm
        //         script {
        //             dockerhub_image_id = DockerBuild(dockerhub_repo,
        //                                              tag: env.BRANCH_NAME)
        //         }
        //     }
        //     post {
        //         success {
        //             DockerPush(dockerhub_image_id)
        //         }
        //         failure {
        //             DockerClean()
        //         }
        //         always {
        //             cleanWs()
        //         }
        //     }
        // }

        // stage('PyPI delivery') {
        //     when {
        //         anyOf {
        //             buildingTag()
        //         }
        //     }
        //     steps {
        //         PyPIDeploy('deepaas', 'indigobot-pypi')
        //     }
        // }

    }
}
