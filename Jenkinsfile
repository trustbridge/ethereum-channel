#!groovy

// Testing pipeline

pipeline {
    agent {
        label 'hamlet-latest'
    }
    options {
        timestamps ()
        buildDiscarder(
            logRotator(
                numToKeepStr: '10'
            )
        )
        disableConcurrentBuilds()
        durabilityHint('PERFORMANCE_OPTIMIZED')
        parallelsAlwaysFailFast()
    }

    stages {

        stage('Setup') {
            steps {
                sh '''#!/bin/bash
                    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
                    source $HOME/.poetry/env
                    poetry --version
                '''
            }
        }

        stage('API Test') {
            steps {
                dir('channel-api/') {
                    sh '''#!/bin/bash
                        poetry install
                        poetry run pytest --junitxml=tests/junit.xml
                    '''
                }
            }

            post {
                always {
                    junit 'channel-api/tests/junit.xml'
                }
            }
        }

        stage('API Build') {
            steps {
                dir('channel-api/') {
                    sh '''#!/bin/bash
                    npm ci

                    sls package --package dist/
                    '''
                }
            }

            post {
                success {
                    dir('channel-api/') {
                        archiveArtifacts artifacts: 'dist/channel-api.zip', fingerprint: true
                    }
                }
            }
        }
    }

    post {
        cleanup {
            cleanWs()
        }
    }
}
