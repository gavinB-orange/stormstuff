pipeline {
  agent any
  stages {
    stage('check_1') {
      steps {
        git(url: 'https://github.com/gavinB-orange/stormstuff.git', branch: 'master')
      }
    }
    stage('check_2') {
      steps {
        echo 'Hello world'
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