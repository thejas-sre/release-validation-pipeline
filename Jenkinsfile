pipeline {
    agent any

    environment {
        API_URL = 'http://localhost:8000'
        REDIS_HOST = 'localhost'
        REDIS_PORT = '6379'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo 'Code checked out from develop branch'
            }
        }

        stage('Security Scan') {
            steps {
                echo 'Running Trivy container image security scan...'
                sh '''
                    bash security/trivy_scan.sh thejas-sre/trade-signal-api:latest || {
                        echo "CRITICAL vulnerabilities found — pipeline blocked"
                        exit 1
                    }
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/trivy_scan_*.json', allowEmptyArchive: true
                }
            }
        }

        stage('Redis Health Checks') {
            steps {
                echo 'Validating Redis connectivity and performance...'
                sh '''
                    pip install redis -q
                    python3 -c "
from validation.check_redis import run_redis_checks
import json, sys
results = run_redis_checks()
failed = [r for r in results if r['status'] == 'failed']
print(json.dumps(results, indent=2))
if failed:
    print(f'FAIL: {len(failed)} Redis checks failed')
    sys.exit(1)
print(f'PASS: All {len(results)} Redis checks passed')
"
                '''
            }
        }

        stage('API Health Checks') {
            steps {
                echo 'Validating trade-signal-api endpoints...'
                sh '''
                    pip install requests -q
                    python3 -c "
from validation.check_api import run_api_checks
import json, sys
results = run_api_checks()
failed = [r for r in results if r['status'] == 'failed']
print(json.dumps(results, indent=2))
if failed:
    print(f'FAIL: {len(failed)} API checks failed')
    sys.exit(1)
print(f'PASS: All {len(results)} API checks passed')
"
                '''
            }
        }

        stage('Kubernetes Health Checks') {
            steps {
                echo 'Validating Kubernetes pod readiness...'
                sh '''
                    python3 -c "
from validation.check_kubernetes import run_kubernetes_checks
import json, sys
results = run_kubernetes_checks()
failed = [r for r in results if r['status'] == 'failed']
print(json.dumps(results, indent=2))
if failed:
    print(f'FAIL: {len(failed)} Kubernetes checks failed')
    sys.exit(1)
print(f'PASS: All Kubernetes checks passed or skipped')
"
                '''
            }
        }

        stage('Config Parity Checks') {
            steps {
                echo 'Validating configuration parity...'
                sh '''
                    python3 -c "
from validation.check_config import run_config_checks
import json, sys
results = run_config_checks()
failed = [r for r in results if r['status'] == 'failed']
print(json.dumps(results, indent=2))
if failed:
    print(f'FAIL: {len(failed)} config checks failed')
    sys.exit(1)
print(f'PASS: All config checks passed')
"
                '''
            }
        }

        stage('Audit Log') {
            steps {
                echo 'Writing structured audit log...'
                sh '''
                    python3 validation/health_checks.py
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/validation_run_*.json', allowEmptyArchive: true
                }
            }
        }

        stage('Deploy Gate') {
            steps {
                echo 'All checks passed — release approved'
                echo 'Proceeding with deployment...'
            }
        }
    }

    post {
        failure {
            echo 'Pipeline failed — release blocked. Check archived reports for details.'
        }
        success {
            echo 'Pipeline passed — release approved and deployed.'
        }
    }
}
