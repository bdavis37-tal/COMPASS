# 🏦 Wells Fargo Compass

**Internal Communications Workbench** — An AI-powered Streamlit application for drafting, reviewing, and approving internal corporate communications with built-in compliance checking.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)

---

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [Usage Guide](#-usage-guide)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

- **AI-Powered Draft Generation** — Generate professional internal communications using OpenAI GPT-4 or demo mode
- **Dual Role System** — Switch between Associate (Writer) and VP (Approver) roles
- **Real-Time Compliance Checking** — Automatic detection of regulatory red-flag keywords
- **Quick Scenario Templates** — Pre-built templates for common communication scenarios:
  - Crisis communications (weather closures)
  - Executive updates (quarterly results)
  - Policy announcements (hybrid work)
- **Approval Workflow** — Submit drafts for review, approve, or request changes
- **Wells Fargo Branding** — Custom theming with corporate colors and styling

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

| Requirement | Version | Installation |
|-------------|---------|--------------|
| **Python** | 3.8 or higher | [Download Python](https://www.python.org/downloads/) |
| **pip** | Latest | Comes with Python |
| **Git** (optional) | Any | [Download Git](https://git-scm.com/downloads) |

To verify your Python installation:

```bash
python --version
```

---

## 🛠️ Installation

### Step 1: Clone or Download the Repository

```bash
# Navigate to your desired directory
cd /path/to/your/projects

# Clone the repository (if using Git)
git clone <repository-url>
cd WFCOMMS

# Or simply download and extract the ZIP file
```

### Step 2: Create a Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `streamlit` — Web application framework
- `openai` — OpenAI API client for AI generation
- `pandas` — Data manipulation (optional utilities)

---

## ⚙️ Configuration

### Demo Mode (Default)

The application works out-of-the-box in **Demo Mode** with pre-configured mock responses. No API key required.

### Live Mode (OpenAI Integration)

To enable live AI generation:

1. Obtain an OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. In the application sidebar, switch to **"Live (OpenAI)"** mode
3. Enter your API key in the password field

> **Note:** Your API key is never stored and is only used for the current session.

---

## 🚀 Running the Application

### Start the Streamlit Server

```bash
streamlit run app.py
```

### Access the Application

Once running, the application will automatically open in your default browser. If not, navigate to:

```
http://localhost:8501
```

### Stopping the Server

Press `Ctrl + C` in the terminal to stop the server.

---

## 📖 Usage Guide

### For Writers (Associate Role)

1. Select **"Associate (Writer)"** in the sidebar
2. Enter your communication topic in the text area, or use a **Quick Scenario** button
3. Click **"✨ Generate Draft"** to create an AI-powered draft
4. Review and edit the generated content
5. Check the compliance status (green = passed, red = issues found)
6. Click **"🚀 Submit for Approval"** to send to a supervisor

### For Approvers (VP Role)

1. Select **"VP (Approver)"** in the sidebar
2. Review pending drafts in the approval queue
3. Read the content and compliance status
4. Click **"✅ Approve & Publish"** or **"❌ Request Changes"**

### Compliance Keywords

The following words trigger compliance warnings:
- guarantee, promise, always, ensure, never, risk-free, certainly

---

## 📁 Project Structure

```
WFCOMMS/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── background.png      # Application background image
├── header.png          # Header banner image
└── wf_box_logo.png     # Wells Fargo logo
```

---

## 🔧 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'streamlit'` | Run `pip install -r requirements.txt` |
| Port 8501 already in use | Run `streamlit run app.py --server.port 8502` |
| Images not loading | Ensure `background.png`, `header.png`, and `wf_box_logo.png` are in the same directory as `app.py` |
| OpenAI API errors | Verify your API key is valid and has available credits |

### Getting Help

If you encounter issues:
1. Check that all dependencies are installed correctly
2. Ensure Python 3.8+ is being used
3. Verify all image assets are present in the project directory

---

## 📝 License

This project is for internal use only.

---

**Built with ❤️ using Streamlit**
