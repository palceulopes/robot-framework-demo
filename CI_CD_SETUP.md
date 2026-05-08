# Continuous Integration / Continuous Deployment

## GitHub Actions Example

Create `.github/workflows/tests.yml`:

```yaml
name: Automotive Framework Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.12']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install robotframework cantools python-can pytest
    
    - name: Run tests
      run: |
        robot --outputdir ./results tests/
    
    - name: Upload results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: robot-results
        path: results/
    
    - name: Publish test report
      if: always()
      uses: dorny/test-reporter@v1
      with:
        name: Robot Test Report
        path: 'results/output.xml'
        reporter: 'java-junit'
```

## Jenkins Pipeline Example

Create `Jenkinsfile`:

```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                echo 'Setting up environment...'
                sh 'python setup_project.py'
                sh 'pip install robotframework cantools python-can'
            }
        }
        
        stage('Run Smoke Tests') {
            steps {
                echo 'Running smoke tests...'
                sh 'robot tests/smoke_tests.robot'
            }
        }
        
        stage('Run Integration Tests') {
            steps {
                echo 'Running integration tests...'
                sh 'robot tests/integration_tests.robot'
            }
        }
        
        stage('Generate Reports') {
            steps {
                echo 'Generating test reports...'
                sh 'robot --outputdir ./results tests/'
            }
        }
    }
    
    post {
        always {
            echo 'Archiving test results...'
            archiveArtifacts artifacts: 'results/**', allowEmptyArchive: true
            junit 'results/*.xml'
        }
        success {
            echo 'All tests passed!'
        }
        failure {
            echo 'Tests failed!'
        }
    }
}
```

## GitLab CI Example

Create `.gitlab-ci.yml`:

```yaml
stages:
  - setup
  - test
  - report

variables:
  PYTHON_VERSION: "3.12"

setup:
  stage: setup
  image: python:3.12
  script:
    - python -m pip install --upgrade pip
    - pip install robotframework cantools python-can
    - python setup_project.py
  artifacts:
    paths:
      - .venv/

test_smoke:
  stage: test
  image: python:3.12
  dependencies:
    - setup
  script:
    - robot tests/smoke_tests.robot
  artifacts:
    paths:
      - results/
    when: always

test_integration:
  stage: test
  image: python:3.12
  dependencies:
    - setup
  script:
    - robot tests/integration_tests.robot
  artifacts:
    paths:
      - results/
    when: always

report:
  stage: report
  image: python:3.12
  script:
    - echo "Tests completed"
  artifacts:
    paths:
      - results/
    when: always
```

## Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

echo "Running pre-commit checks..."

# Check Python syntax
python -m py_compile libraries/automotive_lib.py
if [ $? -ne 0 ]; then
    echo "Syntax check failed"
    exit 1
fi

# Run linting
if command -v flake8 &> /dev/null; then
    flake8 libraries/ --max-line-length=88
    if [ $? -ne 0 ]; then
        echo "Linting failed"
        exit 1
    fi
fi

echo "Pre-commit checks passed"
exit 0
```

## Test Coverage Example

Add to your CI/CD:

```bash
# With pytest
pytest --cov=libraries --cov-report=html
coverage report

# Generate coverage badge
coverage-badge -o coverage.svg
```

## Performance Benchmarking

```python
# benchmarks/can_performance.py
import time
from libraries.automotive_lib import CanBusManager

def benchmark_signal_injection():
    manager = CanBusManager("resources/vehicle_signals.dbc")
    
    start = time.time()
    for i in range(1000):
        manager.inject_speed_signal(100)
    elapsed = time.time() - start
    
    print(f"1000 signals in {elapsed:.2f}s")
    print(f"Average: {(elapsed/1000)*1000:.2f}ms per signal")
    
    manager.close()
```

## Docker Support

Create `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install robotframework cantools python-can

CMD ["robot", "tests/"]
```

Build and run:

```bash
docker build -t automotive-tests:latest .
docker run automotive-tests:latest
```

## Slack Notifications

Add to Jenkins:

```groovy
post {
    always {
        slackSend(
            channel: '#tests',
            color: currentBuild.result == 'SUCCESS' ? 'good' : 'danger',
            message: "Test run: ${currentBuild.result}\n${BUILD_URL}"
        )
    }
}
```

## Best Practices for CI/CD

1. **Parallel Execution**
   ```bash
   robot --parallelization all tests/
   ```

2. **Timeout Management**
   ```bash
   robot --timeout 60s tests/
   ```

3. **Test Isolation**
   - Use Suite Setup/Teardown
   - Clean state between tests
   - Mock all external dependencies

4. **Artifact Management**
   - Archive test results
   - Keep log history
   - Generate reports

5. **Notifications**
   - Alert on failures
   - Track performance trends
   - Report coverage metrics

6. **Security**
   - Don't commit credentials
   - Use environment variables
   - Scan dependencies

---

**Recommended CI/CD Workflow:**

1. Developer pushes code
2. Linting checks (flake8, black)
3. Run smoke tests (fast feedback)
4. Run integration tests
5. Generate coverage report
6. Archive results
7. Notify team
8. Deploy if all pass

---

See `.github/`, `Jenkinsfile`, and `.gitlab-ci.yml` for complete examples.
