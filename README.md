# Tuberculosis Detection 🫁

AI-powered tuberculosis detection and analysis system using deep learning. This application provides instant Chest X-ray analysis with comprehensive medical reports, disease classification, and visualization.

## 📋 Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16 or higher** - [Download Node.js](https://nodejs.org/)
- **npm** (comes with Node.js)

---

## 🚀 Project Setup

### 1. Clone or Extract the Project

```bash
# If using Git
git clone <repository-url>
cd "Bone-Tumor-X"

# Or simply extract the ZIP file and navigate to the directory
cd "Bone-Tumor-X"
```

---

## 🔧 Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Create Python Virtual Environment

**Windows:**
```powershell
python -m venv venv
```

**macOS/Linux:**
```bash
python3 -m venv venv
```

### Step 3: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Step 4: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **⚠️ Important**: This may take 5-10 minutes as it installs TensorFlow, PyTorch, and other ML libraries.

### Step 5: Place Model File

Ensure your trained Tuberculosis model file is placed in `backend/models/`. Supported names:
- `tuberculosis_model.keras`
- `multitask_tb_model.keras`
- `multitask_tb_savedmodel.keras`

---

## 🎨 Frontend Setup

### Step 1: Navigate to Frontend Directory

```bash
# Open a new terminal
cd frontend
```

### Step 2: Install Node Dependencies

```bash
npm install
```

---

## ▶️ Running the Application

You need to run **both** backend and frontend servers simultaneously.

### Terminal 1: Start Backend Server

```bash
cd backend
.\venv\Scripts\activate  # Activate venv first!
python app.py
```

**Expected Output:**
```
🚀 Starting Tuberculosis Detection API...
📍 Server starting instantly on port 5000...
✅ Server ready!
```

### Terminal 2: Start Frontend Server

```bash
cd frontend
npm run dev
```

**Expected Output:**
```
VITE v5.4.2  ready in XXX ms
➜  Local:   http://localhost:5173/
```

---

## 🌐 Accessing the Application

1. Open your web browser
2. Navigate to: **http://localhost:5173**
3. Upload a Chest X-ray image for analysis.

---

## 🚀 Quick Start Summary

```bash
# Backend Setup
cd backend
python -m venv venv
.\venv\Scripts\activate          # Windows
pip install -r requirements.txt
# Place model file in backend/models/
python app.py

# Frontend Setup (New Terminal)
cd frontend
npm install
npm run dev

# Access: http://localhost:5173
```

---

**Built with ❤️ for fighting Tuberculosis**

