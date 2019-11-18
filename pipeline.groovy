currentBuild.description = "LanitBusScheduleBot deploy #${BUILD_NUMBER}, branch:" + params.BRANCH_NAME + " token:" + params.TELEGRAM_TOKEN
pipeline {
    agent any
    
    stages {
        stage('Removing old files'){
            steps {
                echo 'Removing old files...'
                sh label: '', script: 'rm -rf $JENKINS_HOME/LanitBusScheduleBot-' + params.TELEGRAM_TOKEN
                echo 'Removing old files complete'
            }
        }
        stage('Building project'){
            steps {
                withCredentials([string(credentialsId: params.TELEGRAM_TOKEN, variable: 'TOKEN')]) {
                    echo 'Building project ...'
                    sh label: '', script: 'git clone --single-branch --branch ' + params.BRANCH_NAME + ' https://github.com/32-52/LanitBusScheduleBot.git $JENKINS_HOME/LanitBusScheduleBot-' + params.TELEGRAM_TOKEN
                    sh label: '', script: 'cd $JENKINS_HOME/LanitBusScheduleBot-' + params.TELEGRAM_TOKEN
                    sh label: '', script: 'sudo -S docker build -t lanitbusschedulebot:' + params.TELEGRAM_TOKEN + ' $JENKINS_HOME/LanitBusScheduleBot-' + params.TELEGRAM_TOKEN
                    echo 'Building project complete'
                }
            }
        }
        stage('Stopping and prune old container project'){
            steps {
                withCredentials([string(credentialsId: params.TELEGRAM_TOKEN, variable: 'TOKEN')]) {
                    echo 'Stopping old container project ...'
                    catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                        sh label: '', script: 'sudo -S docker stop ' + 'lanitbusschedulebot-' + params.TELEGRAM_TOKEN
                        sh label: '', script: 'sudo -S docker rm ' + 'lanitbusschedulebot-' + params.TELEGRAM_TOKEN 
                    }
                    sh label: '', script: 'sudo -S docker container prune'
                    sh label: '', script: '(echo "y") | sudo -S docker system prune'
                    echo 'Stopping old container project complete'
                }
            }
        }
        stage('Run project'){
            steps {
                withCredentials([string(credentialsId: params.TELEGRAM_TOKEN, variable: 'TOKEN')]) {
                    echo 'Running project ...'
                    sh label: '', script: 'BUILD_ID=dontKillMe sudo docker run -d -e TELEGRAM_TOKEN=$TOKEN -e DEBUG_MODE=$DEBUG_MODE --restart unless-stopped --name lanitbusschedulebot-' + params.TELEGRAM_TOKEN + ' lanitbusschedulebot:' + params.TELEGRAM_TOKEN
                    echo 'Running project complete'
                }
            }
        }
    }
}