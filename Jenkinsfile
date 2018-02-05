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
        sh '''set -e
export http_proxy=http://web-proxy-hpe.houston.hpecorp.net:8080
export https_proxy=http://web-proxy-hpe.houston.hpecorp.net:8080
apk add --update python3
python3 -m pip install -r requirements.txt
pwd
cp ../*.csv .
ls
rm -f output_da*csv
python3 triggered_solver.py -w combined_per_day_1.csv -p results.csv -d 1 -o output_day_1.csv
python3 verify_path.py -p output_day_1.csv -i insitu_201712_per_day_1.csv | tee gavin_verified_output
python3 triggered_solver.py -w combined_per_day_2.csv -p results.csv -d 2 -o output_day_2.csv
python3 verify_path.py -p output_day_2.csv -i insitu_201712_per_day_2.csv | tee -a gavin_verified_output
python3 triggered_solver.py -w combined_per_day_3.csv -p results.csv -d 3 -o output_day_3.csv
python3 verify_path.py -p output_day_3.csv -i insitu_201712_per_day_3.csv | tee -a gavin_verified_output
python3 triggered_solver.py -w combined_per_day_4.csv -p results.csv -d 4 -o output_day_4.csv
python3 verify_path.py -p output_day_4.csv -i insitu_201712_per_day_4.csv | tee -a gavin_verified_output
python3 triggered_solver.py -w combined_per_day_5.csv -p results.csv -d 5 -o output_day_5.csv
python3 verify_path.py -p output_day_5.csv -i insitu_201712_per_day_5.csv | tee -a gavin_verified_output
'''
      }
    }
    stage('check_3') {
      steps {
        sh 'grep Total gavin_verified_output'
      }
    }
    stage('email-status') {
      steps {
        sh 'df -h'
        mail(subject: 'Hi there', body: 'stormstuff / master run OK', from: 'gavin.brebner@hpe.com', replyTo: 'gavin.brebner@hpe.com', to: 'gavin.brebner@hpe.com')
      }
    }
  }
}