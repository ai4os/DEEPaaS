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
    }
}
