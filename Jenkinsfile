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
        mail(subject: 'hi there', body: 'Hi there', from: 'eddie your shipboard computer', replyTo: 'gavin.brebner@hpe.com', to: 'gavin.brebner@hpe.com')
      }
    }
  }
}