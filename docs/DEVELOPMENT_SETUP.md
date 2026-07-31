# DEVELOPMENT_SETUP.md

# Institutional Learning Analytics Dashboard (ILAD)

## Development Environment Setup

Version: 1.0

---

# Purpose

This document explains how to prepare a local development environment for the Institutional Learning Analytics Dashboard (ILAD).

The project uses Python, Streamlit, and a modular analytics architecture.

---

# System Requirements

Operating System

- Windows 10/11
- Linux
- macOS

Python

Recommended

```
Python 3.14+
```

Git

Latest stable version

Editor

Recommended

- Visual Studio Code

Optional

- PyCharm

---

# Clone Repository

```bash
git clone https://github.com/<username>/ilad.git

cd ilad
```

---

# Create Virtual Environment

Windows

```bash
python -m venv venv
```

Activate

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Current Project Dependencies

```
pandas
numpy
scipy
streamlit
plotly
matplotlib
openpyxl
pytest
```

---

# Verify Installation

```bash
python --version

pip list
```

Expected packages include

- pandas
- numpy
- scipy
- streamlit
- pytest

---

# Project Structure

```
ilad/

app.py

analytics/

config/

core/

pages/

tests/

docs/

assets/

data/
```

---

# Running Unit Tests

Run all tests

```bash
pytest
```

Run a single test

```bash
pytest tests/test_rpi.py
```

Verbose output

```bash
pytest -v
```

---

# Running the Dashboard

```bash
streamlit run app.py
```

The application will be available at

```
http://localhost:8501
```

---

# Development Workflow

For every new sprint:

1. Read sprint documentation.
2. Review architecture documents.
3. Discuss implementation.
4. Implement one module only.
5. Run unit tests.
6. Fix failures.
7. Commit to Git.
8. Push to GitHub.

---

# Git Workflow

Check status

```bash
git status
```

Stage files

```bash
git add .
```

Commit

```bash
git commit -m "feat: implement statistics module"
```

Push

```bash
git push origin main
```

---

# AI-assisted Development Workflow

The project follows a documentation-first approach.

Workflow

```
Idea

↓

Architecture Discussion

↓

Documentation

↓

Implementation Plan

↓

Codex Implementation

↓

Pytest

↓

Code Review

↓

Git Commit
```

No implementation should begin before the sprint documentation has been reviewed.

---

# Coding Principles

The project follows these principles:

- Layered Architecture
- Modular Design
- Single Responsibility Principle (SRP)
- Separation of Concerns
- Documentation First
- Test-Driven Mindset
- Clean Code

Business logic must never be implemented inside Streamlit pages.

---

# Troubleshooting

## ModuleNotFoundError

Install missing packages

```bash
pip install <package-name>
```

Example

```bash
pip install scipy
```

---

## Run all dependencies again

```bash
pip install -r requirements.txt
```

---

## Recreate virtual environment

Delete

```
venv/
```

Create again

```bash
python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt
```

---

# Notes

The RPI implementation must always follow the published reference notebook.

Any modification to the mathematical methodology should be treated as a research change, not merely a software refactor.
