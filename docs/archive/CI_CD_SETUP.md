# Archived: CI/CD examples

This file was moved to `docs/archive/` to keep the repository concise for the live demo.

Original content:

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
                sh 'pip install robotframework cantools python-can pytest'
            }
        }
        
        stage('Run Demo Suite') {
            steps {
                echo 'Running demo...'
                sh 'robot tests/network_stack.robot'
            }
        }
    }
}
```


