pipeline {
  agent any
  stages {
    stage('check_1') {
      steps {
        sh '''date
echo "OK"'''
      }
    }
    stage('check_2') {
      steps {
        echo 'Hello world'
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