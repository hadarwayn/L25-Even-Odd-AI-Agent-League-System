# PROJECT-GUIDELINES.md
# Professional AI Development - Complete Standards Guide

**Version:** 4.0  
**Last Updated:** November 2025  
**Target Audience:** AI Assistants (LLMs) & Students (15+ years old)

---

## 📋 Table of Contents

1. [Project Workflow - The Sacred Order](#project-workflow)
2. [Development Environment](#development-environment)
3. [Virtual Environment (UV) - MANDATORY](#virtual-environment)
4. [Phase 1: Planning Documents](#phase-1-planning)
5. [Phase 2: Implementation](#phase-2-implementation)
6. [Directory Structure](#directory-structure)
7. [Code Requirements](#code-requirements)
8. [Relative Code & Package Structure](#relative-code)
9. [Professional Standards](#professional-standards)
10. [Logging System - Ring Buffer](#logging-system)
11. [Cache Management](#cache-management)
12. [Required Files](#required-files)
13. [README.md Standards](#readme-standards)
14. [Results & Visualization](#results-visualization)
15. [Machine Learning Project Requirements](#ml-requirements)
16. [Testing & Quality Assurance](#testing-qa)
17. [Git & Version Control](#git-version-control)
18. [Documentation Standards](#documentation-standards)
19. [Success Checklist](#success-checklist)

---

## 🔴 PROJECT WORKFLOW - THE SACRED ORDER {#project-workflow}

### **This order is MANDATORY. Never skip steps!**

```
┌─────────────────────────────────────────┐
│  PHASE 1: PLANNING (Documents Only)    │
│  1. Create PRD.md                       │
│  2. Create tasks.json                   │
│  3. ⚠️  STOP - Wait for approval        │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  PHASE 2: IMPLEMENTATION                │
│  1. Create directory structure          │
│  2. Set up UV virtual environment       │
│  3. Write code (following all rules)    │
│  4. Generate results (minimum 3 runs)   │
│  5. Create visualizations & graphs      │
│  6. Write README.md                     │
│  7. Test everything                     │
│  8. Prepare for GitHub upload           │
└─────────────────────────────────────────┘
```

**WHY THIS ORDER?**
- Planning first = clear direction, no wasted effort
- Approval step = ensure we're building the right thing
- Implementation last = efficient, focused work

---

---

## 🖥️ DEVELOPMENT ENVIRONMENT {#development-environment}

### **Overview: Student's Development Setup**

This section defines the specific development environment used by the student. All AI assistants and documentation must account for these tools and provide instructions compatible with this setup.

### **1. Primary Development Platforms**

#### **Google AI Studio (formerly Google Antigravity)**

**What it is:** A web-based development environment provided by Google where students can write and test code with AI assistance.

**AI Assistant:** Gemini 3 (or current version)

**When to use:**
- Quick prototyping
- Testing ideas
- Learning new concepts
- Simple projects

**Characteristics:**
- Cloud-based (no local installation needed)
- Integrated AI assistance
- May have execution time limits
- Good for experimentation

**Important Notes for AI Assistants:**
- When the student is using Google AI Studio, provide code that works in that environment
- Be aware of any platform-specific limitations
- Consider that file persistence may differ from local development

#### **Visual Studio Code (VSCode)**

**What it is:** A powerful, free code editor that runs on the student's local machine.

**AI Assistant:** Claude Code (Anthropic's coding assistant)

**When to use:**
- Serious project development
- Projects requiring local file system access
- When version control (Git) is needed
- Projects with multiple files and complex structure
- Projects that will be uploaded to GitHub

**Characteristics:**
- Full local file system access
- Integrated terminal
- Extension ecosystem
- Git integration
- Claude Code provides inline AI assistance

**Important Notes for AI Assistants:**
- Provide detailed file paths appropriate for local development
- Include terminal commands for VSCode's integrated terminal
- Consider the student may be switching between AI assistants

---

### **2. Execution Environments**

#### **Windows Subsystem for Linux (WSL) - PRIMARY**

**What it is:** WSL allows running a Linux environment directly on Windows 11, giving access to Linux command-line tools.

**When to use:**
- Running Python scripts
- Using UV or pip for package management
- Git operations
- Most development tasks

**Setup Instructions:**
```powershell
# In Windows PowerShell (as Administrator):
wsl --install

# After restart, set up your Linux distribution (Ubuntu recommended)
# Then in WSL terminal:
sudo apt update
sudo apt upgrade
```

**Commands in WSL:**
```bash
# Navigate to Windows files
cd /mnt/c/Users/YourUsername/Projects/project-name

# Activate virtual environment
source .venv/bin/activate

# Run Python
python main.py

# Git commands
git status
git add .
git commit -m "message"
```

**Critical Path Considerations:**
```bash
# Windows path: C:\Users\YourName\Projects\my-project
# WSL path:     /mnt/c/Users/YourName/Projects/my-project

# When in documentation, show BOTH paths when relevant
```

#### **Windows PowerShell**

**What it is:** Windows' built-in command-line shell.

**When to use:**
- Installing UV on Windows
- Quick Windows-native operations
- When WSL is not available or needed
- Some Git operations

**Commands in PowerShell:**
```powershell
# Install UV
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Navigate to project
cd C:\Users\YourUsername\Projects\project-name

# Activate virtual environment (Windows-style)
.venv\Scripts\activate

# Run Python
python main.py

# Git commands (same as bash)
git status
git add .
git commit -m "message"
```

---

### **3. Environment-Specific Instructions Template**

**Every project README must include instructions for BOTH environments:**

```markdown
## Installation & Running

### Option A: WSL (Recommended)

1. Open WSL terminal
2. Navigate to project:
   ```bash
   cd /mnt/c/Users/YourName/path/to/project
   ```
3. Create virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```
5. Run the project:
   ```bash
   python main.py
   ```

### Option B: Windows PowerShell

1. Open PowerShell
2. Navigate to project:
   ```powershell
   cd C:\Users\YourName\path\to\project
   ```
3. Create virtual environment:
   ```powershell
   uv venv
   .venv\Scripts\activate
   ```
4. Install dependencies:
   ```powershell
   uv pip install -r requirements.txt
   ```
5. Run the project:
   ```powershell
   python main.py
   ```
```

---

### **4. Tool Version Requirements**

**Document these in every project:**

| Tool | Minimum Version | Check Command |
|------|-----------------|---------------|
| Python | 3.10+ | `python --version` |
| UV | Latest | `uv --version` |
| Git | 2.30+ | `git --version` |
| Node.js | 18+ (if needed) | `node --version` |

**Installation Verification Script:**
```bash
#!/bin/bash
# verify_environment.sh - Run this to check your setup

echo "Checking development environment..."

echo -n "Python: "
python --version 2>/dev/null || echo "Not installed"

echo -n "UV: "
uv --version 2>/dev/null || echo "Not installed"

echo -n "Git: "
git --version 2>/dev/null || echo "Not installed"

echo -n "Node.js: "
node --version 2>/dev/null || echo "Not installed (optional)"

echo "Environment check complete"
```

---

### **5. AI Assistant Context Switching**

**When switching between AI assistants:**

The student may start a project in one environment and continue in another. AI assistants should:

1. **Ask about the current environment** when unclear:
   - "Are you working in Google AI Studio, VSCode, or another environment?"
   - "Will you run this in WSL or PowerShell?"

2. **Provide cross-compatible code** when possible:
   - Use `pathlib.Path` instead of hardcoded path separators
   - Avoid platform-specific commands without alternatives

3. **Document environment dependencies** clearly:
   - Which commands are for WSL vs PowerShell
   - Which features require specific tools

**Example of cross-compatible path handling:**
```python
from pathlib import Path

# GOOD - Works on Windows and Linux
project_root = Path(__file__).parent
data_dir = project_root / "data"
output_file = data_dir / "results.csv"

# BAD - Platform-specific
data_dir = "/mnt/c/Users/Name/project/data"  # WSL only
data_dir = "C:\\Users\\Name\\project\\data"   # Windows only
```

---

### **6. Common Environment Issues & Solutions**

#### **Issue: "python not found" in WSL**
```bash
# Solution: Use python3 explicitly
python3 main.py

# Or create an alias
echo "alias python=python3" >> ~/.bashrc
source ~/.bashrc
```

#### **Issue: UV not found after installation**
```bash
# Solution: Add to PATH
export PATH="$HOME/.cargo/bin:$PATH"
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
```

#### **Issue: Permission denied when running scripts**
```bash
# Solution: Add execute permission
chmod +x script.sh
```

#### **Issue: Line ending problems (Windows to Linux)**
```bash
# Solution: Configure Git
git config --global core.autocrlf input
```

---

## 🌐 VIRTUAL ENVIRONMENT (UV) - MANDATORY {#virtual-environment}

### **Overview**

Every project MUST use UV (Ultra-fast Python package manager) for virtual environment management. UV provides:
- 10-100x faster package installation than pip
- Parallel downloads (multi-processing)
- Better dependency resolution
- Reproducible environments

### **1. UV Installation**

#### **Linux/Mac/WSL:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### **Windows PowerShell:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### **2. Virtual Environment Setup**

```bash
# Navigate to project root
cd /path/to/project

# Create virtual environment
uv venv

# This creates .venv/ folder with:
# - .venv/bin/ (Linux/Mac) or .venv/Scripts/ (Windows)
# - .venv/lib/
# - .venv/pyvenv.cfg
```

### **3. Activation Commands**

**WSL/Linux/Mac:**
```bash
source .venv/bin/activate
```

**Windows PowerShell:**
```powershell
.venv\Scripts\activate
```

**Windows CMD:**
```cmd
.venv\Scripts\activate.bat
```

### **4. Package Installation**

```bash
# Install from requirements.txt
uv pip install -r requirements.txt

# Install single package
uv pip install numpy

# Install with exact version
uv pip install numpy==1.24.3

# Generate requirements.txt from current environment
uv pip freeze > requirements.txt
```

### **5. MANDATORY: venv Folder in GitHub Repository**

**CRITICAL:** The `venv/` folder structure must be included in your GitHub repository to show the virtual environment setup. 

**Directory Structure:**
```
project-root/
├── venv/                    # Virtual environment indicator folder
│   └── .gitkeep            # File that marks this as a venv location
├── .venv/                  # Actual virtual environment (in .gitignore)
├── README.md
├── main.py
└── ...
```

**Create the venv folder with .gitkeep:**
```bash
# Create venv folder (indicator for virtual environment)
mkdir -p venv

# Create .gitkeep file to ensure folder is tracked by Git
touch venv/.gitkeep

# Add explanatory content to .gitkeep
echo "# This folder indicates a virtual environment should be created here" > venv/.gitkeep
echo "# Run: uv venv" >> venv/.gitkeep
echo "# Then activate:" >> venv/.gitkeep
echo "# WSL/Linux/Mac: source .venv/bin/activate" >> venv/.gitkeep
echo "# Windows: .venv\Scripts\activate" >> venv/.gitkeep
```

**The venv/.gitkeep file content:**
```
# This folder indicates a virtual environment should be created here
# Run: uv venv
# Then activate:
# WSL/Linux/Mac: source .venv/bin/activate
# Windows: .venv\Scripts\activate
```

### **6. README.md Virtual Environment Section**

**Every README.md MUST include this section:**

```markdown
## 🌐 Virtual Environment Setup (REQUIRED)

This project uses **UV** for fast, reliable package management.

### Step 1: Install UV (if not installed)

**Linux/Mac/WSL:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows PowerShell:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Step 2: Create Virtual Environment

```bash
# Navigate to project root
cd project-name

# Create virtual environment
uv venv
```

### Step 3: Activate Virtual Environment

**WSL/Linux/Mac:**
```bash
source .venv/bin/activate
```

**Windows PowerShell:**
```powershell
.venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
uv pip install -r requirements.txt
```

### Step 5: Verify Installation

```bash
python --version
# Should show Python 3.10+

python -c "import numpy; print(f'NumPy: {numpy.__version__}')"
# Should show installed NumPy version
```

### Deactivate When Done

```bash
deactivate
```
```

### **7. .gitignore Virtual Environment Configuration**

**Add to .gitignore:**
```gitignore
# Virtual Environments - DO NOT commit actual venv
.venv/
env/
.uv/
miniconda/
conda/

# Note: venv/ folder with .gitkeep IS committed (indicator only)
```

---

## 📝 PHASE 1: PLANNING DOCUMENTS {#phase-1-planning}

### **Document 1: PRD.md (Product Requirements Document)**

**Location:** `docs/PRD.md`

**Must include these exact sections:**

#### 1.1 Project Overview
```markdown
## Project Overview
- **Project Name:** [Clear, descriptive name]
- **One-Line Description:** What does this do?
- **Problem Statement:** What problem are we solving?
- **Why This Matters:** Real-world impact
```

#### 1.2 Target Users & Applications
```markdown
## Target Users
- **Primary Users:** Who will use this?
- **Use Cases:** 3-5 real-world scenarios
- **Example Applications:**
  1. Scenario 1: [Detailed description]
  2. Scenario 2: [Detailed description]
  3. Scenario 3: [Detailed description]
```

#### 1.3 Functional Requirements
```markdown
## Functional Requirements
1. **Core Features:**
   - Feature 1: [What it does]
   - Feature 2: [What it does]
   
2. **Input Requirements:**
   - What data/input does it need?
   - Format specifications
   
3. **Output Requirements:**
   - What results does it produce?
   - Format specifications
   
4. **User Interactions:**
   - How do users interact with it?
```

#### 1.4 Technical Requirements
```markdown
## Technical Requirements

### Environment
- **Python Version:** 3.10+ (specify exact version)
- **Virtual Environment:** UV (MANDATORY)
- **Operating Systems:** Windows (WSL), Linux, macOS

### Core Technologies
- **Primary Library:** NumPy (mandatory for array operations)
- **Additional Libraries:** [List with reasons]
- **No Basic Python Loops:** Use NumPy vectorization

### Performance Requirements
- **Speed:** Target execution time
- **Memory:** Maximum memory usage
- **Scalability:** How it handles larger inputs

### Security Requirements
- API key management (.env file)
- Input validation
- Safe file operations
- No hardcoded secrets
```

#### 1.5 Success Criteria
```markdown
## Success Criteria

### Functional Success
- [ ] All core features work correctly
- [ ] Handles edge cases gracefully
- [ ] Produces accurate results

### Performance Benchmarks
- Execution time: < [X] seconds for standard input
- Memory usage: < [X] MB
- Accuracy: > [X]% (if applicable)

### Quality Metrics
- Code coverage: > 80%
- Documentation completeness: 100%
- All files under 150 lines
```

#### 1.6 Constraints & Assumptions
```markdown
## Constraints
- Technical limitations
- Resource constraints
- Time constraints

## Assumptions
- What we're assuming about users
- What we're assuming about the environment
- Dependencies on external services
```

#### 1.7 Learning Objectives
```markdown
## Learning Objectives
This project demonstrates:
1. [Learning goal 1]
2. [Learning goal 2]
3. [Learning goal 3]

Parameter variations to explore:
- Parameter 1: [What happens when we change this?]
- Parameter 2: [What happens when we change this?]
- Parameter 3: [What happens when we change this?]
```

---

### **Document 2: tasks.json**

**Location:** `docs/tasks.json`

**Structure:**
```json
{
  "project_name": "Your Project Name",
  "total_estimated_hours": 0,
  "phases": [
    {
      "phase": "1_setup",
      "tasks": [
        {
          "id": "1.1",
          "name": "Create directory structure",
          "priority": "critical",
          "estimated_hours": 0.5,
          "dependencies": [],
          "files_to_create": [
            "README.md",
            "main.py",
            "requirements.txt",
            ".gitignore"
          ]
        }
      ]
    },
    {
      "phase": "2_core_implementation",
      "tasks": [
        {
          "id": "2.1",
          "name": "Implement main algorithm",
          "priority": "critical",
          "estimated_hours": 3,
          "dependencies": ["1.1"],
          "files_to_create": ["src/algorithm.py"]
        }
      ]
    },
    {
      "phase": "3_results_visualization",
      "tasks": [
        {
          "id": "3.1",
          "name": "Generate result graphs",
          "priority": "high",
          "estimated_hours": 2,
          "dependencies": ["2.1"],
          "files_to_create": ["src/visualizer.py"]
        }
      ]
    },
    {
      "phase": "4_documentation",
      "tasks": [
        {
          "id": "4.1",
          "name": "Write comprehensive README",
          "priority": "high",
          "estimated_hours": 2,
          "dependencies": ["3.1"]
        }
      ]
    },
    {
      "phase": "5_testing",
      "tasks": [
        {
          "id": "5.1",
          "name": "Run minimum 3 test cases",
          "priority": "critical",
          "estimated_hours": 1,
          "dependencies": ["4.1"]
        }
      ]
    }
  ],
  "file_structure": {
    "root": ["README.md", "main.py", "requirements.txt", ".gitignore"],
    "src": ["List all .py files here"],
    "docs": ["PRD.md", "tasks.json"],
    "results": ["examples/"],
    "config": ["List config files if needed"]
  }
}
```

---

## 🚀 PHASE 2: IMPLEMENTATION {#phase-2-implementation}

### **Only start this phase after PRD and tasks.json are approved!**

---

## 📁 DIRECTORY STRUCTURE {#directory-structure}

### **Standard Structure (MANDATORY)**

```
project-root/
├── README.md                 # The showcase document (explained below)
├── main.py                   # Single entry point to run everything
├── requirements.txt          # All dependencies with EXACT versions
├── .gitignore               # Protect secrets and cache
├── .env.example             # Template for environment variables
│
├── venv/                    # Virtual environment indicator
│   └── .gitkeep            # Instructions for venv setup
│
├── src/                     # ALL source code goes here
│   ├── __init__.py          # Makes it a Python package (REQUIRED)
│   ├── algorithm.py         # Core algorithm implementation
│   ├── data_processor.py    # Data handling
│   ├── visualizer.py        # Graph and chart generation
│   └── utils/               # Helper functions
│       ├── __init__.py      # REQUIRED for package structure
│       ├── validators.py    # Input validation
│       └── helpers.py       # Utility functions
│
├── docs/                    # ALL documentation
│   ├── PRD.md              # Product Requirements Document
│   ├── tasks.json          # Implementation tasks
│   └── API.md              # API documentation (if applicable)
│
├── results/                 # ALL output files (VISUAL RESULTS)
│   ├── examples/           # Example outputs (minimum 3)
│   │   ├── run_1/         # First test run
│   │   │   ├── output.png
│   │   │   ├── data.csv
│   │   │   └── metrics.json
│   │   ├── run_2/         # Second test run
│   │   └── run_3/         # Third test run
│   ├── graphs/             # Generated visualizations
│   │   ├── parameter_comparison.png
│   │   ├── performance_chart.png
│   │   └── convergence_plot.png
│   └── tables/             # Result tables (if applicable)
│
├── logs/                    # Logging output (Ring Buffer)
│   ├── config/             # Log configuration
│   │   └── log_config.json # Ring buffer settings
│   └── .gitkeep            # Keep folder in git
│
├── tests/                   # Unit tests (optional but recommended)
│   ├── __init__.py         # REQUIRED for package structure
│   └── test_algorithm.py
│
└── config/                  # Configuration files (if needed)
    └── settings.yaml
```

### **Rules (STRICT)**

1. **Root directory contains ONLY:**
   - README.md
   - main.py
   - requirements.txt
   - .gitignore
   - .env.example (if needed)

2. **All code in `src/`** - with `__init__.py` files

3. **All documentation in `docs/`**

4. **All outputs in `results/`** - with visual results (images, graphs, tables)

5. **Each file max 150 lines** - split if longer!

6. **Every folder must have `__init__.py`** - for package structure

---

## 💻 CODE REQUIREMENTS {#code-requirements}

### **1. Technology Stack**

#### **MANDATORY: NumPy for Array Operations**
```python
# ❌ WRONG - Basic Python loop
total = 0
for i in range(len(data)):
    total += data[i]

# ✅ CORRECT - NumPy vectorization
import numpy as np
total = np.sum(data)
```

#### **Virtual Environment: UV (MANDATORY)**
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Activate (Linux/Mac)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

**Why UV?**
- Parallel package downloads (multi-processing)
- 10-100x faster than pip
- Better dependency resolution

---

### **2. Code Quality Standards**

#### **2.1 Maximum File Length: 150 LINES**

**CRITICAL RULE:** No Python file may exceed **150 lines of code**.

**Why 150 lines?**
- Forces modular, focused code
- Easier to understand and maintain
- Each file has ONE clear purpose
- Makes debugging simpler

**What to do when exceeding 150 lines:**
1. Identify logical groupings of functions
2. Create new files for each group
3. Use proper imports between files
4. Update `__init__.py` to expose public functions

**Example of splitting a large file:**

```python
# BEFORE: algorithm.py (200+ lines) - TOO LONG!

# AFTER: Split into focused modules

# src/algorithm/__init__.py
from .core import train_model, predict
from .metrics import compute_loss, compute_accuracy
from .optimization import gradient_descent, adam_optimizer

# src/algorithm/core.py (50 lines)
# src/algorithm/metrics.py (40 lines)
# src/algorithm/optimization.py (60 lines)
```

#### **2.2 README Code Files Table (MANDATORY)**

**Every README.md MUST include a table listing all code files:**

```markdown
## 📁 Code Files Summary

| File | Description | Lines |
|------|-------------|-------|
| `main.py` | Entry point - runs the entire pipeline | 45 |
| `src/algorithm.py` | Core machine learning algorithm | 120 |
| `src/data_processor.py` | Data loading and preprocessing | 85 |
| `src/visualizer.py` | Creates all graphs and charts | 95 |
| `src/utils/validators.py` | Input validation functions | 60 |
| `src/utils/helpers.py` | General utility functions | 45 |
| `src/utils/logger.py` | Ring buffer logging system | 130 |

**Total Code Lines:** 580
**Average Lines per File:** 83
**Maximum Allowed:** 150 lines per file ✅
```

#### **2.3 Type Hints (MANDATORY)**
```python
from typing import List, Tuple, Optional
import numpy as np

def process_data(
    input_array: np.ndarray,
    threshold: float = 0.5,
    normalize: bool = True
) -> Tuple[np.ndarray, dict]:
    """
    Process input data with specified parameters.
    
    Args:
        input_array: Input data as NumPy array
        threshold: Cutoff value for filtering (default: 0.5)
        normalize: Whether to normalize output (default: True)
    
    Returns:
        Tuple of (processed_array, metadata_dict)
    
    Example:
        >>> data = np.array([1, 2, 3, 4, 5])
        >>> result, info = process_data(data, threshold=2.5)
    """
    # Implementation here
    pass
```

#### **2.4 Comments (Explain like to a 15-year-old)**
```python
# ❌ BAD COMMENT
# Calculate mean
mean = np.mean(data)

# ✅ GOOD COMMENT
# Calculate the average value of all numbers in our data.
# For example, if data = [2, 4, 6], mean = (2+4+6)/3 = 4
mean = np.mean(data)

# ✅ EXCELLENT COMMENT WITH WHY
# We calculate the mean (average) because we need to center our data
# around zero. This makes it easier to compare different datasets.
# Think of it like adjusting everyone's height relative to the average height.
mean = np.mean(data)
```

#### **2.5 Error Handling**
```python
def safe_divide(a: float, b: float) -> Optional[float]:
    """
    Safely divide two numbers, handling division by zero.
    
    Returns None if division is not possible.
    """
    try:
        if b == 0:
            print("⚠️ Warning: Cannot divide by zero! Returning None.")
            return None
        return a / b
    except Exception as e:
        print(f"❌ Error during division: {e}")
        return None
```

#### **2.6 Modular Functions (Single Responsibility)**
```python
# ❌ BAD - One function does everything
def process_everything(data):
    # Load data
    # Clean data
    # Analyze data
    # Visualize data
    # Save results
    pass

# ✅ GOOD - Each function has one job
def load_data(filepath: str) -> np.ndarray:
    """Load data from file."""
    pass

def clean_data(data: np.ndarray) -> np.ndarray:
    """Remove outliers and handle missing values."""
    pass

def analyze_data(data: np.ndarray) -> dict:
    """Perform statistical analysis."""
    pass

def visualize_results(data: np.ndarray, output_path: str) -> None:
    """Create and save visualization."""
    pass
```

---

### **3. Performance Optimization**

#### **3.1 Use NumPy Vectorization**
```python
# ❌ SLOW - Python loop
def slow_calculation(data):
    result = []
    for i in range(len(data)):
        result.append(data[i] ** 2 + 2 * data[i] + 1)
    return result

# ✅ FAST - NumPy vectorization
def fast_calculation(data: np.ndarray) -> np.ndarray:
    return data**2 + 2*data + 1
```

#### **3.2 Measure Performance**
```python
import time

def benchmark_function(func, *args, **kwargs):
    """Measure how long a function takes to run."""
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    
    execution_time = end_time - start_time
    print(f"⏱️ Function '{func.__name__}' took {execution_time:.4f} seconds")
    
    return result, execution_time
```

---

### **4. Security Requirements**

#### **4.1 Environment Variables**
```python
# .env file (NEVER commit this!)
API_KEY=your_secret_key_here
DATABASE_URL=your_database_url

# .env.example (Safe to commit - template only)
API_KEY=your_api_key_here
DATABASE_URL=your_database_url_here
```

```python
# Load environment variables
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file

API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("❌ API_KEY not found! Create a .env file.")
```

#### **4.2 Input Validation**
```python
def validate_input(data: np.ndarray, min_length: int = 1) -> bool:
    """
    Check if input data is valid.
    
    Args:
        data: Input array to validate
        min_length: Minimum required length
    
    Returns:
        True if valid, raises ValueError if invalid
    """
    if not isinstance(data, np.ndarray):
        raise TypeError("❌ Input must be a NumPy array!")
    
    if len(data) < min_length:
        raise ValueError(f"❌ Input too short! Need at least {min_length} elements.")
    
    if np.any(np.isnan(data)):
        raise ValueError("❌ Input contains NaN (missing) values!")
    
    return True
```

---

## 🔗 RELATIVE CODE & PACKAGE STRUCTURE {#relative-code}

### **Overview: Why Relative Code Matters**

**CRITICAL RULE:** All code MUST use **RELATIVE paths**, never **ABSOLUTE paths**.

**Why?**
- Code works on ANY computer, not just yours
- Project can be moved to different folders
- Works across Windows, Mac, and Linux
- Essential for GitHub sharing

### **1. The Golden Rule: pathlib.Path**

```python
from pathlib import Path

# ✅ CORRECT - RELATIVE path using Path
project_root = Path(__file__).parent.parent  # Go up to project root
data_dir = project_root / "data"
results_dir = project_root / "results"
config_file = project_root / "config" / "settings.yaml"

# ❌ WRONG - ABSOLUTE path (only works on YOUR computer!)
data_dir = "/home/username/projects/my-project/data"
data_dir = "C:\\Users\\Username\\Projects\\my-project\\data"
data_dir = "/mnt/c/Users/Username/Projects/my-project/data"
```

### **2. Package Structure with __init__.py**

**EVERY folder containing Python code MUST have an `__init__.py` file.**

**Why `__init__.py`?**
- Makes the folder a Python "package"
- Enables proper imports between files
- Controls what's exposed publicly
- Essential for relative imports

**Structure:**
```
project-root/
├── main.py
├── src/
│   ├── __init__.py          # REQUIRED
│   ├── algorithm.py
│   ├── visualizer.py
│   └── utils/
│       ├── __init__.py      # REQUIRED
│       ├── validators.py
│       └── helpers.py
└── tests/
    ├── __init__.py          # REQUIRED
    └── test_algorithm.py
```

### **3. __init__.py Contents**

#### **src/__init__.py**
```python
"""
Source package for the project.

This file makes 'src' a Python package and exposes public modules.
"""

from .algorithm import train_model, predict
from .visualizer import create_graph, save_figure
from .data_processor import load_data, preprocess

# Define what's available when someone does: from src import *
__all__ = [
    'train_model',
    'predict',
    'create_graph',
    'save_figure',
    'load_data',
    'preprocess'
]
```

#### **src/utils/__init__.py**
```python
"""
Utility functions package.

Contains helper functions for validation, file operations, and logging.
"""

from .validators import validate_input, check_data_format
from .helpers import format_output, calculate_metrics
from .logger import setup_logger, RingBufferHandler

__all__ = [
    'validate_input',
    'check_data_format',
    'format_output',
    'calculate_metrics',
    'setup_logger',
    'RingBufferHandler'
]
```

### **4. Correct Import Patterns**

#### **From main.py (root level):**
```python
# main.py
from src import train_model, create_graph
from src.utils import validate_input, setup_logger

# Or import entire modules
from src import algorithm, visualizer
from src.utils import validators
```

#### **From within src/ (relative imports):**
```python
# src/algorithm.py
from .utils import validate_input  # Relative import within package
from .visualizer import create_graph

# Or using absolute imports (also valid)
from src.utils import validate_input
from src.visualizer import create_graph
```

#### **From within src/utils/:**
```python
# src/utils/validators.py
from .helpers import format_error_message  # Relative import
```

### **5. Standard Path Resolution Template**

**Put this in a file like `src/utils/paths.py`:**

```python
"""
Path utilities for the project.

This module provides consistent path resolution across the entire project.
All paths are RELATIVE - the code works on ANY computer!
"""

from pathlib import Path


def get_project_root() -> Path:
    """
    Get the absolute path to the project root directory.
    
    Works from any file in the project by navigating up from this file.
    
    Returns:
        Path object pointing to project root
    
    Example:
        >>> root = get_project_root()
        >>> print(root)
        /home/user/projects/my-project  # On Linux
        C:\\Users\\User\\Projects\\my-project  # On Windows
    """
    # This file is in: project/src/utils/paths.py
    # So project root is 3 levels up
    return Path(__file__).resolve().parent.parent.parent


def get_data_dir() -> Path:
    """Get path to data directory."""
    return get_project_root() / "data"


def get_results_dir() -> Path:
    """Get path to results directory."""
    results = get_project_root() / "results"
    results.mkdir(exist_ok=True)  # Create if doesn't exist
    return results


def get_logs_dir() -> Path:
    """Get path to logs directory."""
    logs = get_project_root() / "logs"
    logs.mkdir(exist_ok=True)
    return logs


def get_config_path(config_name: str = "settings.yaml") -> Path:
    """Get path to a config file."""
    return get_project_root() / "config" / config_name


# Example usage and verification
if __name__ == "__main__":
    print(f"Project root: {get_project_root()}")
    print(f"Data dir: {get_data_dir()}")
    print(f"Results dir: {get_results_dir()}")
    print(f"Logs dir: {get_logs_dir()}")
```

### **6. Common Mistakes to Avoid**

```python
# ❌ WRONG - Hardcoded absolute path
DATA_PATH = "/home/hadar/projects/ml-project/data/train.csv"

# ❌ WRONG - Assuming current working directory
DATA_PATH = "data/train.csv"  # Breaks if script run from different folder

# ❌ WRONG - Using os.path with string concatenation
DATA_PATH = os.path.join("/home/user", "data")

# ✅ CORRECT - Relative to file location
DATA_PATH = Path(__file__).parent.parent / "data" / "train.csv"

# ✅ CORRECT - Using path utility
from src.utils.paths import get_data_dir
DATA_PATH = get_data_dir() / "train.csv"
```

---

## ⭐ PROFESSIONAL STANDARDS {#professional-standards}

### **Overview: Top Professional Quality**

This section defines the professional quality standards that ALL projects must meet. The goal is to produce work that:
- Could be shown to employers in a portfolio
- Demonstrates mastery of concepts
- Is understandable by anyone, including a 15-year-old student
- Meets industry security and performance standards

---

### **1. Code Professionalism**

#### **1.1 Every Function Must Explain WHY**

```python
# UNPROFESSIONAL - Only explains WHAT
def normalize(data):
    """Normalize the data."""
    return (data - np.min(data)) / (np.max(data) - np.min(data))

# PROFESSIONAL - Explains WHAT, WHY, and HOW
def normalize(data: np.ndarray) -> np.ndarray:
    """
    Normalize data to a 0-1 range using min-max scaling.
    
    WHY we do this:
    Different features often have different scales (e.g., age 0-100, 
    salary 30,000-200,000). Machine learning algorithms work better 
    when all features are on the same scale because otherwise, 
    features with larger numbers dominate the learning.
    
    HOW it works:
    1. Find the minimum value (the "floor")
    2. Subtract the minimum from all values (now minimum is 0)
    3. Divide by the range (max - min) to scale everything to 0-1
    
    Real-world analogy:
    Imagine converting all temperatures to a 0-100 scale where:
    - 0 = coldest temperature you measured
    - 100 = hottest temperature you measured
    Now all temperatures are comparable regardless of original units!
    
    Args:
        data: Array of numbers to normalize
    
    Returns:
        Array with all values between 0 and 1
    
    Example:
        >>> temps = np.array([32, 50, 68, 86, 104])  # Fahrenheit
        >>> normalize(temps)
        array([0.   , 0.25 , 0.5  , 0.75 , 1.   ])
    
    Note:
        Returns all zeros if all values are identical (division by zero protection)
    """
    data_range = np.max(data) - np.min(data)
    if data_range == 0:
        return np.zeros_like(data)
    return (data - np.min(data)) / data_range
```

#### **1.2 Variable Names Must Be Self-Documenting**

```python
# UNPROFESSIONAL - Cryptic names
def calc(d, lr, e):
    for i in range(e):
        g = compute_g(d)
        w = w - lr * g
    return w

# PROFESSIONAL - Clear, descriptive names
def train_model(
    training_data: np.ndarray,
    learning_rate: float,
    num_epochs: int
) -> np.ndarray:
    """Train a model using gradient descent optimization."""
    weights = initialize_weights(training_data.shape[1])
    
    for epoch_number in range(num_epochs):
        gradient = compute_gradient(training_data, weights)
        weights = weights - learning_rate * gradient
    
    return weights
```

#### **1.3 Magic Numbers Must Be Named Constants**

```python
# UNPROFESSIONAL - Magic numbers everywhere
def process(data):
    if len(data) < 10:
        return None
    threshold = 0.5
    result = data[data > 0.001]
    return result[:100]

# PROFESSIONAL - Named constants with explanations
# Constants at top of file
MINIMUM_SAMPLE_SIZE = 10      # Statistical significance requires at least 10 samples
CLASSIFICATION_THRESHOLD = 0.5  # Probability above 50% = positive class
NUMERICAL_STABILITY_EPSILON = 0.001  # Prevents division by zero
MAX_RESULTS_TO_RETURN = 100   # Limit output for performance

def process(data: np.ndarray) -> Optional[np.ndarray]:
    """Process data with explained thresholds."""
    if len(data) < MINIMUM_SAMPLE_SIZE:
        print(f"Warning: Need at least {MINIMUM_SAMPLE_SIZE} samples")
        return None
    
    result = data[data > NUMERICAL_STABILITY_EPSILON]
    return result[:MAX_RESULTS_TO_RETURN]
```

---

### **2. Documentation Professionalism**

#### **2.1 The "15-Year-Old Test"**

**Every explanation must pass this test:**
> "Could a smart 15-year-old with no programming experience understand this?"

**Techniques to achieve this:**

1. **Use analogies from everyday life:**
   ```markdown
   ## What is Gradient Descent?
   
   Imagine you're blindfolded on a hilly landscape and want to find the lowest 
   point (a valley). You can't see, but you can feel which direction slopes 
   downward by moving your foot around.
   
   Strategy: Take a step in the steepest downward direction. Repeat until 
   you stop going down.
   
   In machine learning:
   - The "landscape" is the error surface
   - The "lowest point" is where our model makes fewest mistakes
   - "Feeling the slope" is computing the gradient
   - "Taking a step" is updating our parameters
   ```

2. **Build concepts step by step:**
   ```markdown
   ## Understanding Probability (0 to 1)
   
   Level 1 - Basic understanding:
   - 0 means "impossible" (like rolling a 7 on a normal die)
   - 1 means "certain" (like the sun rising tomorrow)
   - 0.5 means "50-50 chance" (like flipping a fair coin)
   
   Level 2 - Connecting to percentages:
   - Probability 0.7 = 70% chance = 7 out of 10 times
   - Probability 0.25 = 25% chance = 1 out of 4 times
   
   Level 3 - In our model:
   - Output 0.8 means: "I'm 80% confident this is a yes"
   - Output 0.2 means: "I'm 80% confident this is a no"
   ```

3. **Show the "why" before the "how":**
   ```markdown
   ## Why Do We Normalize Data?
   
   THE PROBLEM (without normalization):
   Imagine you're comparing how important age and salary are for getting a loan.
   - Age: ranges from 18 to 80 (difference of 62)
   - Salary: ranges from $30,000 to $200,000 (difference of 170,000)
   
   If we just use these numbers, the algorithm will think salary is 2,700 times 
   more important than age simply because the numbers are bigger!
   
   THE SOLUTION (normalization):
   We convert both to 0-1 scale:
   - Age 18 -> 0, Age 80 -> 1
   - Salary $30,000 -> 0, Salary $200,000 -> 1
   
   Now both features compete fairly!
   ```

---

### **3. Performance & Security Professionalism**

#### **3.1 Performance Benchmarking is MANDATORY**

Every project must include performance measurements:

```python
import time
import tracemalloc
import numpy as np
from typing import Callable, Dict, Any

def comprehensive_benchmark(
    func: Callable,
    *args,
    num_runs: int = 3,
    **kwargs
) -> Dict[str, Any]:
    """
    Run comprehensive performance benchmarks on a function.
    
    Measures:
    - Execution time (average over multiple runs)
    - Memory usage (peak)
    - Consistency (standard deviation of times)
    """
    times = []
    
    # Warm-up run (not counted)
    _ = func(*args, **kwargs)
    
    # Timed runs
    for _ in range(num_runs):
        tracemalloc.start()
        
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        times.append(end_time - start_time)
    
    return {
        'function_name': func.__name__,
        'num_runs': num_runs,
        'avg_time_seconds': np.mean(times),
        'std_time_seconds': np.std(times),
        'min_time_seconds': np.min(times),
        'max_time_seconds': np.max(times),
        'peak_memory_mb': peak / 1024 / 1024,
    }
```

#### **3.2 Security Checklist (MANDATORY)**

Every project must pass this security audit:

- No hardcoded API keys or passwords
- .env file in .gitignore
- Input validation on all user inputs
- Safe file operations (no arbitrary path access)
- No SQL injection vulnerabilities (if applicable)

---

### **4. Industry-Standard Practices**

#### **4.1 Logging Instead of Print (for larger projects)**

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_data(data: np.ndarray) -> np.ndarray:
    """Process data with proper logging."""
    logger.info(f"Starting data processing - {len(data)} samples")
    
    try:
        result = actual_processing(data)
        logger.info(f"Processing complete - {len(result)} results")
        return result
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise
```

#### **4.2 Configuration Management**

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ModelConfig:
    """
    Configuration for the machine learning model.
    All 'magic numbers' are defined here with explanations.
    """
    learning_rate: float = 0.001  # How big each learning step is
    max_iterations: int = 1000    # Maximum training rounds
    convergence_threshold: float = 1e-6  # When to stop
    train_test_split: float = 0.8  # 80% training, 20% testing
    random_seed: int = 42          # For reproducibility
```

---

## 📝 LOGGING SYSTEM - RING BUFFER {#logging-system}

### **Overview: Why Ring Buffer Logging?**

A **Ring Buffer** logging system prevents logs from consuming unlimited disk space by:
- Limiting maximum lines per log file
- Limiting maximum number of log files
- Automatically rotating (deleting oldest when limit reached)
- Preserving recent logs for debugging

### **1. Ring Buffer Configuration**

**Create file: `logs/config/log_config.json`**

```json
{
    "ring_buffer": {
        "max_lines_per_file": 1000,
        "max_log_files": 5,
        "log_directory": "logs",
        "log_filename_pattern": "app_{timestamp}.log",
        "log_level": "INFO",
        "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        "date_format": "%Y-%m-%d %H:%M:%S"
    },
    "status_display": {
        "show_file_count": true,
        "show_total_lines": true,
        "show_total_size_kb": true
    }
}
```

### **2. Ring Buffer Logger Implementation**

**Create file: `src/utils/logger.py`** (under 150 lines!)

```python
"""
Ring Buffer Logging System.

This module provides a logging system that:
- Limits log file size (max lines per file)
- Limits number of log files (deletes oldest when exceeded)
- Shows status: file count, total lines, total KB

WHY Ring Buffer?
Logs can grow infinitely, filling up disk space. Ring buffer keeps
only the most recent logs, like a circular buffer that overwrites
the oldest data when full.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class RingBufferHandler(logging.Handler):
    """
    A logging handler that implements ring buffer behavior.
    
    Features:
    - Creates new log file when max lines reached
    - Deletes oldest log file when max files reached
    - Tracks and displays logging statistics
    """
    
    def __init__(
        self,
        log_dir: Path,
        max_lines: int = 1000,
        max_files: int = 5,
        filename_pattern: str = "app_{timestamp}.log"
    ):
        """
        Initialize the ring buffer handler.
        
        Args:
            log_dir: Directory to store log files
            max_lines: Maximum lines per log file before rotation
            max_files: Maximum number of log files to keep
            filename_pattern: Pattern for log filenames
        """
        super().__init__()
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_lines = max_lines
        self.max_files = max_files
        self.filename_pattern = filename_pattern
        
        self.current_file: Optional[Path] = None
        self.current_line_count = 0
        self.file_handle = None
        
        # Start new log file
        self._rotate_file()
    
    def _get_new_filename(self) -> str:
        """Generate new filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.filename_pattern.replace("{timestamp}", timestamp)
    
    def _rotate_file(self) -> None:
        """Create new log file and manage file count."""
        # Close current file if open
        if self.file_handle:
            self.file_handle.close()
        
        # Create new file
        new_filename = self._get_new_filename()
        self.current_file = self.log_dir / new_filename
        self.file_handle = open(self.current_file, 'w', encoding='utf-8')
        self.current_line_count = 0
        
        # Check and delete oldest files if exceeded
        self._cleanup_old_files()
    
    def _cleanup_old_files(self) -> None:
        """Delete oldest log files if max_files exceeded."""
        log_files = sorted(
            self.log_dir.glob("*.log"),
            key=lambda f: f.stat().st_mtime
        )
        
        while len(log_files) > self.max_files:
            oldest = log_files.pop(0)
            oldest.unlink()
    
    def emit(self, record: logging.LogRecord) -> None:
        """Write log record to file."""
        try:
            msg = self.format(record) + '\n'
            self.file_handle.write(msg)
            self.file_handle.flush()
            self.current_line_count += 1
            
            # Rotate if max lines reached
            if self.current_line_count >= self.max_lines:
                self._rotate_file()
                
        except Exception:
            self.handleError(record)
    
    def get_status(self) -> dict:
        """Get current logging status."""
        log_files = list(self.log_dir.glob("*.log"))
        total_lines = 0
        total_size = 0
        
        for f in log_files:
            total_size += f.stat().st_size
            with open(f, 'r') as file:
                total_lines += sum(1 for _ in file)
        
        return {
            'file_count': len(log_files),
            'total_lines': total_lines,
            'total_size_kb': round(total_size / 1024, 2),
            'max_lines_per_file': self.max_lines,
            'max_files': self.max_files
        }
    
    def close(self) -> None:
        """Clean up resources."""
        if self.file_handle:
            self.file_handle.close()
        super().close()


def setup_logger(
    name: str = "app",
    config_path: Optional[Path] = None
) -> logging.Logger:
    """
    Set up a logger with ring buffer handler.
    
    Args:
        name: Logger name
        config_path: Path to log_config.json (optional)
    
    Returns:
        Configured logger instance
    """
    # Load config or use defaults
    if config_path and config_path.exists():
        with open(config_path) as f:
            config = json.load(f)['ring_buffer']
    else:
        config = {
            'max_lines_per_file': 1000,
            'max_log_files': 5,
            'log_directory': 'logs',
            'log_level': 'INFO',
            'format': '%(asctime)s - %(levelname)s - %(message)s'
        }
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config['log_level']))
    
    # Add ring buffer handler
    handler = RingBufferHandler(
        log_dir=Path(config['log_directory']),
        max_lines=config['max_lines_per_file'],
        max_files=config['max_log_files']
    )
    handler.setFormatter(logging.Formatter(config['format']))
    logger.addHandler(handler)
    
    return logger


def print_log_status(logger: logging.Logger) -> None:
    """Print current logging status."""
    for handler in logger.handlers:
        if isinstance(handler, RingBufferHandler):
            status = handler.get_status()
            print("\n📊 Log Status:")
            print(f"  Files: {status['file_count']}/{status['max_files']}")
            print(f"  Total Lines: {status['total_lines']}")
            print(f"  Total Size: {status['total_size_kb']} KB")
            break
```

### **3. Using the Logger**

**In main.py or any module:**

```python
from src.utils.logger import setup_logger, print_log_status
from pathlib import Path

# Setup logger with config
config_path = Path("logs/config/log_config.json")
logger = setup_logger("my_app", config_path)

# Log messages
logger.info("Application started")
logger.info(f"Processing {len(data)} samples")
logger.warning("Low memory detected")
logger.error("Failed to load file")

# Show status
print_log_status(logger)
# Output:
# 📊 Log Status:
#   Files: 2/5
#   Total Lines: 1523
#   Total Size: 45.67 KB
```

### **4. Directory Structure for Logs**

```
project-root/
├── logs/
│   ├── config/
│   │   └── log_config.json    # Ring buffer configuration
│   ├── app_20241129_100523.log  # Current log file
│   ├── app_20241128_143012.log  # Previous log file
│   └── .gitkeep               # Keep folder in git
```

### **5. .gitignore for Logs**

```gitignore
# Logs - Keep config but not actual logs
logs/*.log
!logs/config/
!logs/.gitkeep
```

---

## 🗄️ CACHE MANAGEMENT {#cache-management}

### **Overview: __pycache__ Management**

Python creates `__pycache__` folders containing compiled `.pyc` files. These:
- Speed up subsequent runs
- Can cause issues with old code
- Should NOT be committed to Git

### **1. How __pycache__ Works**

```
project-root/
├── src/
│   ├── algorithm.py              # Your Python source code
│   ├── __pycache__/             # Auto-created by Python
│   │   ├── algorithm.cpython-310.pyc  # Compiled bytecode
│   │   └── __init__.cpython-310.pyc
```

**When Python compiles:**
- First run: Creates `.pyc` from `.py`
- Subsequent runs: Uses `.pyc` if `.py` unchanged
- Problem: If `.py` changes but timestamp doesn't update, old `.pyc` may run!

### **2. Clear Cache When Code Updates**

**Create utility script: `scripts/clear_cache.py`**

```python
#!/usr/bin/env python3
"""
Clear all __pycache__ directories and .pyc files.

Run this script after updating code to ensure fresh compilation.

Usage:
    python scripts/clear_cache.py
"""

import shutil
from pathlib import Path


def clear_pycache(root_dir: Path = None) -> int:
    """
    Remove all __pycache__ directories recursively.
    
    Args:
        root_dir: Starting directory (default: project root)
    
    Returns:
        Number of cache directories removed
    """
    if root_dir is None:
        root_dir = Path(__file__).parent.parent
    
    removed_count = 0
    
    for pycache_dir in root_dir.rglob("__pycache__"):
        print(f"🗑️  Removing: {pycache_dir}")
        shutil.rmtree(pycache_dir)
        removed_count += 1
    
    # Also remove .pyc files outside __pycache__
    for pyc_file in root_dir.rglob("*.pyc"):
        print(f"🗑️  Removing: {pyc_file}")
        pyc_file.unlink()
        removed_count += 1
    
    return removed_count


def main():
    print("🧹 Clearing Python cache...\n")
    
    count = clear_pycache()
    
    if count > 0:
        print(f"\n✅ Removed {count} cache items")
    else:
        print("\n✅ No cache to clear")
    
    print("💡 Run your code again to recompile fresh")


if __name__ == "__main__":
    main()
```

### **3. Command Line Cache Clearing**

**Linux/Mac/WSL:**
```bash
# Clear all __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Clear all .pyc files
find . -name "*.pyc" -delete
```

**Windows PowerShell:**
```powershell
# Clear all __pycache__ directories
Get-ChildItem -Path . -Include __pycache__ -Recurse -Directory | Remove-Item -Recurse -Force

# Clear all .pyc files  
Get-ChildItem -Path . -Include *.pyc -Recurse | Remove-Item -Force
```

### **4. .gitignore for Cache**

```gitignore
# Python cache - NEVER commit
__pycache__/
*.py[cod]
*$py.class
*.so

# Compiled Python
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
```

### **5. Prevent Cache Issues: Run with -B Flag**

```bash
# Run Python WITHOUT creating __pycache__
python -B main.py

# Or set environment variable
export PYTHONDONTWRITEBYTECODE=1
python main.py
```

### **6. When to Clear Cache**

Clear cache when:
- ✅ After updating any `.py` file
- ✅ After pulling from Git
- ✅ Before running tests
- ✅ When experiencing "weird" behavior
- ✅ Before creating final release

---

## 📄 REQUIRED FILES {#required-files}

### **1. requirements.txt**

**Format: package==exact.version.number**

```txt
# Core dependencies
numpy==1.24.3
matplotlib==3.7.1
pandas==2.0.2

# Visualization
seaborn==0.12.2
plotly==5.14.1

# Utilities
python-dotenv==1.0.0
pyyaml==6.0

# Optional but recommended
pytest==7.3.1
black==23.3.0
```

**How to generate:**
```bash
# After installing packages in your virtual environment
uv pip freeze > requirements.txt
```

---

### **2. .gitignore**

```gitignore
# Secrets & API Keys
.env
config/secrets.json
*.key
*api_key*
*secret*
*.pem

# Virtual Environments - DO NOT commit actual venv
.venv/
env/
.uv/
miniconda/
conda/

# Python cache
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Testing
.pytest_cache/
.coverage
htmlcov/

# Results (optional - decide based on file size)
results/temp/
results/large_outputs/

# Jupyter Notebooks
.ipynb_checkpoints/
*.ipynb

# Logs (keep config, not actual logs)
logs/*.log
!logs/config/
!logs/.gitkeep
```

---

### **3. .env.example**

```bash
# API Keys (Get these from [service name])
API_KEY=your_api_key_here

# Database (if applicable)
DATABASE_URL=your_database_url_here

# Configuration
DEBUG_MODE=False
LOG_LEVEL=INFO
```

---

### **4. main.py (Entry Point)**

```python
#!/usr/bin/env python3
"""
Project Name - Main Entry Point

This script runs the entire project pipeline:
1. Load and validate data
2. Process data
3. Generate results
4. Create visualizations
5. Save outputs

Usage:
    python main.py
    python main.py --config config/settings.yaml
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from src import algorithm, visualizer
from src.utils.logger import setup_logger, print_log_status
import argparse


def main():
    """
    Main function - orchestrates the entire project workflow.
    """
    # Setup logging
    logger = setup_logger("main")
    
    print("=" * 60)
    print("🚀 Starting Project Name")
    print("=" * 60)
    
    logger.info("Application started")
    
    # Step 1: Setup
    print("\n📁 Step 1: Loading configuration...")
    logger.info("Loading configuration")
    # Your code here
    
    # Step 2: Process
    print("\n⚙️ Step 2: Processing data...")
    logger.info("Processing data")
    # Your code here
    
    # Step 3: Visualize
    print("\n📊 Step 3: Creating visualizations...")
    logger.info("Creating visualizations")
    # Your code here
    
    # Step 4: Save
    print("\n💾 Step 4: Saving results...")
    logger.info("Saving results")
    # Your code here
    
    print("\n" + "=" * 60)
    print("✅ Project completed successfully!")
    print("📂 Check the results/ directory for outputs")
    print("=" * 60)
    
    logger.info("Application completed successfully")
    print_log_status(logger)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the project")
    parser.add_argument(
        "--config",
        type=str,
        default="config/settings.yaml",
        help="Path to configuration file"
    )
    args = parser.parse_args()
    
    main()
```

---

## 📖 README.md STANDARDS {#readme-standards}

### **DUAL PURPOSE: Documentation + Learning Guide**

**Every README.md must serve TWO objectives:**

1. **📄 Full Project Documentation** - Complete guide to understand, install, and run the project
2. **📚 Machine Learning Learning Guide** - Educational resource that teaches the concepts used

### **Structure (EXACT ORDER)**

```markdown
# Project Title

*One-line description that immediately tells what this does*

![Project Banner](results/banner.png) <!-- Optional but impressive -->

## 📋 Abstract

2-3 sentences explaining:
- What problem this solves
- How it solves it
- Why it matters

## 🎯 Applications & Use Cases

Real-world scenarios where this is useful:

1. **Use Case 1: [Name]**
   - Who uses it: [Target user]
   - Scenario: [Detailed description]
   - Benefit: [What they gain]

2. **Use Case 2: [Name]**
   - [Same structure]

3. **Use Case 3: [Name]**
   - [Same structure]

## ✨ Features

- 🔹 Feature 1: Brief description
- 🔹 Feature 2: Brief description
- 🔹 Feature 3: Brief description
- 🔹 What makes it unique

## 📊 Dataset

- **Source:** Where the data comes from
- **Features:** What input variables are used
- **Target:** What we're predicting/classifying
- **Samples:** How many data points

## 🧮 Mathematical Foundations

### [Algorithm/Method Name]

**What it is:**
[Simple explanation]

**How it works:**
[Step-by-step explanation with analogies]

**The Math (simplified):**
[Key formulas with plain-English explanations]

**Real-world analogy:**
[Something a 15-year-old would understand]

## 🖥️ Environment & Requirements

### System Requirements
- **Operating System:** Windows (WSL), Linux, or macOS
- **Python Version:** 3.10 or higher
- **Memory:** Minimum 4GB RAM
- **Storage:** 500MB free space

### Virtual Environment
This project uses **UV** for fast dependency management:
- UV is 10-100x faster than pip
- Uses parallel downloads
- Better dependency resolution

## 🌐 Virtual Environment Setup (REQUIRED)

### Step 1: Install UV (if not installed)

**Linux/Mac/WSL:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows PowerShell:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Step 2: Create Virtual Environment

```bash
cd project-name
uv venv
```

### Step 3: Activate Virtual Environment

**WSL/Linux/Mac:**
```bash
source .venv/bin/activate
```

**Windows PowerShell:**
```powershell
.venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
uv pip install -r requirements.txt
```

## 🚀 Installation Instructions

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/project-name.git
cd project-name
```

### Step 2: Set Up Virtual Environment
(See Virtual Environment Setup section above)

### Step 3: Set Up Environment Variables (if needed)
```bash
cp .env.example .env
# Edit .env with your actual values
```

## 📂 How to Run

### Basic Usage
```bash
python main.py
```

### With Custom Configuration
```bash
python main.py --config config/custom_settings.yaml
```

### Expected Output
When you run the program, you should see:
1. Loading message with configuration details
2. Progress updates for each step
3. Final success message
4. Location of result files

## 📁 Project Structure

```
project-name/
├── README.md              # This file
├── main.py                # Run this to start the program
├── requirements.txt       # List of required packages
├── .gitignore            # Files Git should ignore
├── venv/                 # Virtual environment indicator
│   └── .gitkeep         # Setup instructions
│
├── src/                  # All code files
│   ├── __init__.py      # Package marker
│   ├── algorithm.py     # Core algorithm
│   └── utils/           # Helper functions
│       └── __init__.py
│
├── docs/                # Documentation
│   ├── PRD.md          # Project requirements
│   └── tasks.json      # Implementation plan
│
├── results/            # Output files
│   ├── examples/      # Example results from test runs
│   ├── graphs/        # Generated visualizations
│   └── tables/        # Data tables
│
└── logs/              # Logging output
    └── config/        # Log configuration
```

## 📁 Code Files Summary

| File | Description | Lines |
|------|-------------|-------|
| `main.py` | Entry point - runs the entire pipeline | 45 |
| `src/algorithm.py` | Core machine learning algorithm | 120 |
| `src/data_processor.py` | Data loading and preprocessing | 85 |
| `src/visualizer.py` | Creates all graphs and charts | 95 |
| `src/utils/validators.py` | Input validation functions | 60 |
| `src/utils/helpers.py` | General utility functions | 45 |
| `src/utils/logger.py` | Ring buffer logging system | 130 |

**Total Code Lines:** 580
**Average Lines per File:** 83
**Maximum Allowed:** 150 lines per file ✅

## 📊 Results & Examples

### Run 1: [Description]

**Parameters:**
- Parameter 1: value
- Parameter 2: value

![Result 1](results/examples/run_1/output.png)

**Explanation:**
[Detailed explanation of what this graph shows]

**Key Observations:**
- Observation 1
- Observation 2

**Metrics:**
| Metric | Value |
|--------|-------|
| Execution Time | X.XX seconds |
| Accuracy | XX% |
| Memory Used | XXX MB |

---

### Run 2: [Description]

[Same structure as Run 1]

---

### Run 3: [Description]

[Same structure as Run 1]

## 📈 Results Comparison

### Visual Comparison

![Parameter Comparison](results/graphs/parameter_comparison.png)

### Metrics Table

| Run | Parameter X | Accuracy | Time (s) | Memory (MB) |
|-----|-------------|----------|----------|-------------|
| 1   | 0.001       | 95.2%    | 2.34     | 128         |
| 2   | 0.01        | 94.8%    | 1.87     | 125         |
| 3   | 0.1         | 89.3%    | 0.92     | 122         |

### Analysis

[Explanation of what these results mean and why]

## 🔬 Learning Demonstration

### Experiment 1: Effect of [Parameter]

[Show how changing a parameter affects results]

### Experiment 2: Performance Scaling

[Show how performance changes with data size]

## 🎓 What I Learned

### Technical Insights
1. [Key learning 1]
2. [Key learning 2]
3. [Key learning 3]

### Real-World Applications
- Application 1
- Application 2

## 🐛 Troubleshooting

### Common Issues

**Issue 1: "Module not found" error**
```
Solution: Make sure virtual environment is activated
```

**Issue 2: [Description]**
```
Solution: [Steps to fix]
```

## 📞 Contact & Support

**Author:** [Your Name]
**Email:** [your.email@example.com]
**GitHub:** [https://github.com/yourusername]

## 📄 License

This project is open source and available for anyone to use.

## 🙏 Acknowledgments

- Built as part of the AI Developer Expert course
- [Any other acknowledgments]

---

*Made with ❤️ and Python*
```

---

## 📊 RESULTS & VISUALIZATION {#results-visualization}

### **CRITICAL: Results Must Be VISUAL**

**Every project MUST include visual results in the README:**
- Images (PNG, JPG)
- Graphs and charts
- Tables
- Diagrams

**Results folder structure:**
```
results/
├── examples/           # Test run outputs
│   ├── run_1/
│   │   ├── output.png
│   │   ├── metrics.json
│   │   └── data.csv
│   ├── run_2/
│   └── run_3/
├── graphs/            # Visualization images
│   ├── convergence_plot.png
│   ├── parameter_comparison.png
│   ├── performance_chart.png
│   └── confusion_matrix.png
└── tables/            # Data tables (if needed)
    └── results_summary.csv
```

### **1. Graph Requirements**

Every graph/chart MUST include:

```python
import matplotlib.pyplot as plt
import numpy as np

def create_explanatory_graph(data, title, xlabel, ylabel, output_path):
    """
    Create a graph with comprehensive explanations.
    
    This function makes it easy to understand results by:
    - Using clear labels
    - Adding helpful annotations
    - Choosing appropriate colors
    - Saving high-quality images
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot data
    ax.plot(data, linewidth=2, color='#2E86AB', label='Our Results')
    
    # Add title and labels
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    
    # Add grid for easier reading
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add legend
    ax.legend(fontsize=10)
    
    # Highlight important points
    max_idx = np.argmax(data)
    ax.annotate(
        f'Highest: {data[max_idx]:.2f}',
        xy=(max_idx, data[max_idx]),
        xytext=(10, 10),
        textcoords='offset points',
        fontsize=10,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0')
    )
    
    # Save with high quality
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Graph saved to: {output_path}")
```

### **2. Required Visualizations**

**Minimum 3 different types:**

1. **Line Graph** - Show trends over time/iterations
2. **Bar Chart** - Compare different parameters/runs
3. **Scatter Plot** - Show relationships between variables

### **3. Result Explanation Template**

For EVERY result, include:

```markdown
## Result [Number]: [Descriptive Title]

### Quick Summary
In one sentence: [What did we find?]

### The Graph Explained
![Graph](results/graphs/result_1.png)

**What you're looking at:**
- **X-axis (horizontal):** [What this represents - use simple words]
- **Y-axis (vertical):** [What this represents - use simple words]
- **The line/bars/points:** [What the visual elements show]

### Breaking It Down (Like You're 15)

**Imagine this scenario:** [Use a real-world analogy]

**What we did:**
1. Step 1: [Simple explanation]
2. Step 2: [Simple explanation]
3. Step 3: [Simple explanation]

**What happened:**
- First observation: [What + numbers + why interesting]
- Second observation: [What + numbers + why it matters]
- Third observation: [What + numbers + what we learned]

### The Numbers

| Metric | Value | What This Means |
|--------|-------|-----------------|
| Execution Time | 2.34 seconds | How long it took |
| Accuracy | 95.6% | How correct results were |
| Memory Used | 128 MB | RAM needed |

### Real-World Connection

**Where could you use this?**
- Application 1
- Application 2
- Application 3
```

---

## 🔬 MACHINE LEARNING PROJECT REQUIREMENTS {#ml-requirements}

### **⚠️ CRITICAL: Metric Selection for ML Projects**

**This section is MANDATORY for any machine learning, optimization, or gradient descent project.**

#### **The Problem: Wrong Metrics Lead to Misleading Results**

```python
# ❌ WRONG - Using binary classification error for convergence plot
def train_model(X, y):
    for iteration in range(max_iterations):
        predictions = (probabilities >= 0.5).astype(int)
        error = np.mean(predictions != y)  # Binary 0/1 error
        error_history.append(error)
    # Problem: For well-separated data, error = 0% from iteration 1

# ✅ CORRECT - Using cross-entropy loss for convergence plot
def train_model(X, y):
    for iteration in range(max_iterations):
        p_clipped = np.clip(probabilities, 1e-15, 1 - 1e-15)
        loss = -np.mean(y * np.log(p_clipped) + (1-y) * np.log(1-p_clipped))
        loss_history.append(loss)
    # Cross-entropy loss shows actual learning progress!
```

### **Required Metrics**

1. **PRIMARY: Cross-Entropy Loss** - Shows smooth learning progress
2. **SECONDARY: Log-Likelihood** - For dual-axis plots
3. **EVALUATION: Binary Error** - Final performance only

### **Parameter Selection for Meaningful Results**

```python
# ❌ WRONG - Causes instant learning (flat curves)
learning_rate = 0.3        # Too high
max_iterations = 100       # Too few

# ✅ CORRECT - Shows gradual learning (smooth curves)
learning_rate = 0.001      # Small enough to show progression
max_iterations = 1000      # Enough to show full convergence
```

---

## 🧪 TESTING & QUALITY ASSURANCE {#testing-qa}

### **1. Minimum Testing Requirements**

**MUST have at least:**
- 3 complete test runs with different parameters
- 3 different visualizations
- Performance benchmarks
- Edge case testing

### **2. Manual Testing Checklist**

```markdown
## Testing Checklist

### Functionality Tests
- [ ] Program runs without errors
- [ ] All features work as described
- [ ] Results are accurate and reproducible

### Performance Tests
- [ ] Runs in acceptable time
- [ ] Memory usage is reasonable
- [ ] Can handle expected input sizes

### Documentation Tests
- [ ] README instructions work on fresh system
- [ ] All file paths are correct
- [ ] All graphs display correctly
- [ ] Installation steps are complete

### Code Quality Tests
- [ ] All files under 150 lines
- [ ] No hardcoded secrets
- [ ] Type hints present
- [ ] __init__.py in all folders

### Results Tests
- [ ] 3 runs completed successfully
- [ ] Results saved in results/
- [ ] Visual results (graphs, tables) included
- [ ] Explanations are beginner-friendly
```

---

## 🔧 GIT & VERSION CONTROL {#git-version-control}

### **1. Initial Git Setup**

```bash
# Step 1: Initialize repository
cd project-root
git init

# Step 2: Add all files
git add .

# Step 3: Make first commit
git commit -m "Initial commit: Project structure and documentation"

# Step 4: Connect to GitHub
git remote add origin https://github.com/yourusername/your-repo-name.git

# Step 5: Push to GitHub
git branch -M main
git push -u origin main
```

### **2. Commit Message Standards**

```bash
# Types:
# - feat: New feature
# - fix: Bug fix
# - docs: Documentation changes
# - style: Code formatting
# - refactor: Code restructuring
# - test: Adding tests
# - chore: Maintenance

# Examples:
git commit -m "feat: Add parameter comparison visualization"
git commit -m "fix: Correct NumPy array dimension handling"
git commit -m "docs: Update README with Run 3 results"
```

### **3. Pre-Push Checklist**

```markdown
- [ ] All secrets removed (.env in .gitignore)
- [ ] venv/ folder with .gitkeep present
- [ ] All __init__.py files in place
- [ ] All tests pass
- [ ] README is up to date
- [ ] No large files (> 100MB)
- [ ] No __pycache__ directories
- [ ] requirements.txt is current
```

---

## 📚 DOCUMENTATION STANDARDS {#documentation-standards}

### **1. Code Documentation**

**Every function must have:**

```python
def function_name(param1: type, param2: type) -> return_type:
    """
    One-line summary of what this function does.
    
    Longer explanation if needed. Explain:
    - What problem does this solve?
    - How does it work (high level)?
    - When should you use it?
    
    Args:
        param1: What is this parameter? What values are valid?
        param2: What is this parameter? What values are valid?
    
    Returns:
        What does this function return? What format?
    
    Raises:
        ValueError: When does this happen?
        TypeError: When does this happen?
    
    Example:
        >>> data = np.array([1, 2, 3, 4, 5])
        >>> result = function_name(data, threshold=2.5)
        >>> print(result)
        array([3, 4, 5])
    
    Note:
        Any important information or warnings.
    """
    # Implementation
    pass
```

### **2. README Documentation Rules**

**Language:**
- Write for someone with NO technical background
- Avoid jargon; if you must use it, explain it
- Use analogies and real-world examples
- Break complex ideas into simple steps

**Structure:**
- Use headers (##, ###) to organize
- Use bullet points for lists
- Use code blocks for commands
- Use tables for comparisons
- Use images for visual explanations

**Tone:**
- Friendly and encouraging
- Assume the reader wants to learn
- Explain WHY, not just WHAT

---

## ✅ SUCCESS CHECKLIST {#success-checklist}

### **Phase 1: Planning (Before Coding)**

```markdown
- [ ] PRD.md created with all sections
- [ ] tasks.json created with all tasks
- [ ] File structure planned
- [ ] Student/instructor approval received
```

### **Phase 2: Implementation**

```markdown
### Directory Structure
- [ ] Correct folder structure created
- [ ] README.md in root
- [ ] main.py in root
- [ ] requirements.txt in root
- [ ] .gitignore in root
- [ ] venv/ folder with .gitkeep
- [ ] src/ directory with __init__.py
- [ ] docs/ directory
- [ ] results/ directory with visual outputs
- [ ] logs/ directory with config/

### Code Quality
- [ ] All files under 150 lines
- [ ] Every folder has __init__.py
- [ ] All code uses RELATIVE paths
- [ ] NumPy used (no basic Python loops)
- [ ] Type hints on all functions
- [ ] Docstrings on all functions
- [ ] Comments explain WHY
- [ ] Error handling implemented
- [ ] Ring buffer logging implemented

### Files
- [ ] requirements.txt with exact versions
- [ ] .gitignore protects secrets and cache
- [ ] Code files table in README
- [ ] All imports work correctly

### Testing
- [ ] 3 test runs completed
- [ ] Different parameters each run
- [ ] All results saved in results/
- [ ] Cache cleared before final test

### Results & Visualization
- [ ] Minimum 3 different graphs
- [ ] All graphs saved in results/graphs/
- [ ] README includes visual results
- [ ] Each result explained thoroughly
- [ ] Results comparison table included

### Documentation
- [ ] README serves DUAL purpose (docs + learning guide)
- [ ] Virtual environment setup section
- [ ] Code files summary table
- [ ] Installation instructions tested
- [ ] All images load correctly
```

### **Phase 3: Final Review**

```markdown
- [ ] Ran on fresh virtual environment
- [ ] All installation steps work
- [ ] Project runs without errors
- [ ] Results match documentation
- [ ] Ready to share publicly
- [ ] Proud to put in portfolio
```

---

## 🎯 FINAL WORDS

### **For AI Assistants (LLMs)**

When working on a project using these guidelines:

1. **ALWAYS follow the two-phase workflow**
   - Phase 1: Create PRD and tasks.json, then STOP
   - Phase 2: Only after approval, implement everything

2. **NEVER compromise on quality**
   - Every file under 150 lines (split if needed)
   - Every function documented
   - Every result explained thoroughly
   - Every folder has __init__.py

3. **ALWAYS use UV virtual environment**
   - Include venv/ folder with .gitkeep
   - Document activation in README

4. **ALWAYS use RELATIVE paths**
   - Use pathlib.Path
   - Never hardcode absolute paths

5. **ALWAYS include visual results**
   - Graphs in results/graphs/
   - Tables in README
   - Explanations for 15-year-olds

6. **IMPLEMENT Ring Buffer logging**
   - Configure max lines and files
   - Show status in output

### **For Students**

When starting a new project:

1. **Follow the structure exactly**
   - Don't skip planning
   - Don't exceed 150 lines per file
   - Include all required folders and files

2. **Document as you go**
   - Don't wait until the end
   - Capture insights immediately

3. **Test thoroughly**
   - Run 3+ different configurations
   - Clear cache between major changes
   - Verify on fresh environment

---

## 📖 APPENDIX: Quick Reference

### **Essential Commands**

```bash
# Virtual Environment (UV)
uv venv                          # Create environment
source .venv/bin/activate        # Activate (Linux/Mac)
.venv\Scripts\activate           # Activate (Windows)
uv pip install -r requirements.txt  # Install dependencies

# Clear Cache
find . -type d -name "__pycache__" -exec rm -rf {} +
python scripts/clear_cache.py

# Run Project
python main.py

# Git Commands
git init
git add .
git commit -m "message"
git push origin main
```

### **File Size Limits**

| Item | Maximum Size | Why |
|------|-------------|-----|
| Python file | **150 lines** | Maintainability |
| Single function | 50 lines | Single responsibility |
| README.md | No limit | More = better |
| Git commit | 100 MB | GitHub restriction |
| Image file | 5 MB | Loading speed |

---

**END OF GUIDELINES**

*Remember: Quality over speed. Professional over quick. Learning over finishing.*

*These guidelines ensure every project is portfolio-worthy and demonstrates true mastery.*

---

**Version:** 4.0  
**Last Updated:** November 2025  
**Maintained by:** AI Developer Expert Course  
**License:** Open for educational use
