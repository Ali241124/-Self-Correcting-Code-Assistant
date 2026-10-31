# 🛠️ Self-Correcting Code Assistant

An AI-powered Python debugging application that detects programming errors, analyzes problems using a local Large Language Model (LLM), generates corrected code, executes the solution, and validates it through automated tests.

Built with **Python, Streamlit, Ollama, Docker, SQLite, and Pytest**, this project demonstrates how AI agents can automate software debugging and code validation while keeping execution isolated in Docker containers.

## 🚀 Features

### 🤖 AI-Powered Code Debugging
- Analyzes Python execution errors and tracebacks.
- Uses a locally hosted Ollama model to diagnose problems.
- Generates corrected Python code.
- Provides explanations of detected issues and suggested corrections.

### 🔄 Automatic Self-Correction
- Automatically retries failed code.
- Supports configurable AI correction attempts.
- Rejects empty or unchanged AI-generated corrections.
- Tracks correction attempts and debugging history.

### 🐳 Docker-Based Code Execution
- Executes submitted Python code inside Docker containers.
- Disables network access for execution containers.
- Uses non-root container users.
- Applies CPU, memory, and process limits.
- Uses a read-only root filesystem.
- Provides execution timeout protection.

### 🧪 Automated Code Validation
- Checks Python syntax before execution.
- Runs user-provided pytest test cases.
- Identifies logical errors through failed tests.
- Validates corrected code before accepting it as successful.

### 📊 Streamlit Dashboard
- Interactive code editor.
- Configurable AI correction attempts.
- Optional automated testing.
- Displays execution output and errors.
- Shows corrected code and validation results.
- Provides previous debugging sessions and correction history.

### 🗄️ SQLite Debugging History
- Saves debugging sessions.
- Stores original and corrected code.
- Records execution results and correction status.
- Allows users to review previous debugging sessions.

### 🐙 GitHub Integration
- Fetches Python files from GitHub repositories.
- Analyzes repository code using the AI debugger.
- Compares original and corrected code.
- Supports reviewing proposed changes before committing them.

## 🏗️ Architecture

```text
                 User
                  |
                  v
          Streamlit Dashboard
                  |
                  v
        Self-Correction Engine
                  |
          +-------+-------+
          |               |
          v               v
     Ollama LLM       Code Validator
          |               |
          v               v
     Error Analysis    Pytest
          |               |
          +-------+-------+
                  |
                  v
          Docker Executor
                  |
                  v
        Isolated Python Runtime
                  |
                  v
          Execution Results
                  |
          +-------+-------+
          |               |
          v               v
       SQLite          GitHub
       History        Integration
```

## 🧰 Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11 | Core application development |
| Ollama | Local LLM inference |
| Qwen2.5-Coder | AI-powered debugging |
| Streamlit | Interactive dashboard |
| Docker | Isolated code execution |
| Pytest | Automated testing |
| SQLite | Debugging session storage |
| Git & GitHub | Version control and integration |

## 📁 Project Structure

```text
Self-Correcting-Code-Assistant/
│
├── core/
│   ├── __init__.py
│   ├── code_executor.py
│   ├── docker_executor.py
│   ├── docker_validator.py
│   ├── ai_debugger.py
│   ├── self_corrector.py
│   └── code_validator.py
│
├── database/
│   ├── __init__.py
│   └── history.py
│
├── integrations/
│   └── github_client.py
│
├── prompts/
│   └── debugging_prompts.py
│
├── tests/
│   ├── test_executor.py
│   ├── test_validator.py
│   └── test_self_corrector.py
│
├── workspace/
│
├── app.py
├── requirements.txt
├── Dockerfile.sandbox
├── test_ai_debugger.py
├── test_self_corrector.py
├── test_database.py
├── test_github.py
├── test_docker_executor.py
├── test_docker_validator.py
├── test_docker_security.py
├── README.md
└── .gitignore
```

*Additional files may exist as the project evolves.*

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Ali241124/-Self-Correcting-Code-Assistant.git
cd -Self-Correcting-Code-Assistant
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and configure Ollama

Download Ollama from:

https://ollama.com/

Pull the debugging model:

```bash
ollama pull qwen2.5-coder:1.5b
```

Start Ollama:

```bash
ollama serve
```

The application uses the local Ollama API, normally available at:

```text
http://localhost:11434
```

### 5. Install Docker Desktop

Download Docker Desktop:

https://www.docker.com/products/docker-desktop/

Start Docker Desktop and verify the installation:

```bash
docker --version
docker info
```

Pull the Python sandbox image:

```bash
docker pull python:3.11-slim
```

### 6. Build the pytest sandbox image

From the project root:

```bash
docker build -f Dockerfile.sandbox -t self-correcting-python-sandbox:latest .
```

### 7. Launch the application

```bash
streamlit run app.py
```

Open the local dashboard:

```text
http://localhost:8501
```

## 💻 Example: Automatic Code Correction

### Original code

The following code contains a logical error:

```python
def add(a, b):
    return a - b

print(add(10, 20))
```

### Expected corrected code

The AI debugger identifies the incorrect operation and suggests:

```python
def add(a, b):
    return a + b

print(add(10, 20))
```

### Expected output

```text
30
```

### Automated test cases

```python
from solution import add

def test_add_positive_numbers():
    assert add(10, 20) == 30

def test_add_negative_numbers():
    assert add(-5, -5) == -10

def test_add_zero():
    assert add(10, 0) == 10
```

The corrected implementation should pass all three tests.

## 🧪 Running Tests

Run the main project test suite:

```bash
python -m pytest tests/ -v
```

Test Docker code execution:

```bash
python test_docker_executor.py
```

Test Docker-based pytest validation:

```bash
python test_docker_validator.py
```

Run Docker security checks:

```bash
python test_docker_security.py
```

## 🔐 Security Considerations

The Docker execution environment uses several restrictions:

- Network access disabled.
- Non-root execution.
- Read-only root filesystem.
- Read-only source-code mount.
- Limited CPU and memory resources.
- Restricted process count.
- Execution timeout protection.

**Important:** Docker isolation reduces execution risks but does not guarantee complete security. This project is still a development-stage application and should not be exposed to arbitrary untrusted submissions without further security hardening, including output limits, robust container lifecycle management, and additional isolation controls.

GitHub credentials and other secrets should be stored in environment variables rather than committed to the repository.

## 🎯 Project Objectives

This project explores the practical application of AI in software engineering by combining:

- Large Language Models (LLMs).
- Automated debugging and error analysis.
- Iterative self-correction.
- Automated software testing.
- Containerized code execution.
- Persistent debugging history.
- GitHub-based development workflows.

## 🔮 Future Improvements

- Multi-language debugging support.
- More advanced agentic debugging workflows.
- Improved code quality and static analysis.
- Streaming AI debugging responses.
- Resource and output monitoring.
- Dedicated remote sandbox service.
- Cloud deployment.
- Advanced GitHub Pull Request automation.

## 👨‍💻 Author

**Syed Ali Hassan**

Software Engineer | AI / GenAI Engineer

- GitHub: https://github.com/Ali241124
- Portfolio: https://syedalihassan-portfolio.vercel.app
- LinkedIn: https://www.linkedin.com/in/syedalihassan24/

---

⭐ If you find this project interesting, consider giving it a star on GitHub.
