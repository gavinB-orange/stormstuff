pipeline {
  agent any
  stages {
    stage('checkout') {
      steps {
        git(url: 'https://github.com/gavinB-orange/stormstuff.git', branch: 'master')
      }
    }
    stage('run_check') {
      steps {
        sh '''pwd
ls
'''
      }
    }
    stage('check_3') {
      steps {
        echo 'do something exciting'
      }
    }
    stage('email-status') {
      steps {
        sh 'df -h'
        mail(subject: 'Hi there', body: 'Hi there', from: 'gavin.brebner@hpe.com', replyTo: 'gavin.brebner@hpe.com', to: 'gavin.brebner@hpe.com')
      }
    }
  }
}