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
        sh '''export http_proxy=http://web-proxy-hpe.houston.hpecorp.net:8080
export https_proxy=http://web-proxy-hpe.houston.hpecorp.net:8080
apk add --update python3
python3 -m pip install -r requirements.txt
pwd
cp ../*.csv .
ls
python3 triggered_solver.py -w combined_per_day_1.csv -p results.csv -d 1 -o output_dat_1.csv
python3 verify_path.py -p output_dat_1.csv -i insitu_201712_per_day_1.csv'''
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