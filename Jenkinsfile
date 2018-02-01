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
        sh '''virtualenv -p python3 venv
./venv/bin/pip install -r requirements
pwd
cp ../*.csv .
ls
./venv/bin/python3 triggered_solver.py -w combined_per_day_1.csv -p results.csv -d 1 -o output_dat_1.csv
./venv/bin/python3 verify_path.py -p output_dat_1.csv -i insitu_201712_per_day_1.csv'''
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