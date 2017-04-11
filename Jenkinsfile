// -*- mode: groovy -*-

stage('Test') {
  
  node('xenial-server') {
    checkout scm
    sh 'tox'
  }
}
