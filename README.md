# Bone Tumor Detection 🦴

AI-powered bone tumor detection and analysis system using deep learning. This application provides instant X-ray analysis with comprehensive medical reports, tumor classification, and visualization.

## 📋 Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16 or higher** - [Download Node.js](https://nodejs.org/)
- **npm** (comes with Node.js)
- **Git** (optional, for cloning)

---

## 🚀 Project Setup

### 1. Clone or Extract the Project

```bash
# If using Git
git clone <repository-url>
cd "Bone Tumor X"

# Or simply extract the ZIP file and navigate to the directory
cd "Bone Tumor X"
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

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

> **Note**: You should see `(venv)` prefix in your terminal when activated.

### Step 4: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **⚠️ Important**: This may take 5-10 minutes as it installs TensorFlow, PyTorch, and other ML libraries.

### Step 5: Verify Backend Setup

Check that all dependencies are installed:
```bash
pip list
```

You should see packages like:
- Flask
- tensorflow
- torch
- transformers
- Pillow
- opencv-python

---

## 🎨 Frontend Setup

### Step 1: Navigate to Frontend Directory

```bash
# From project root
cd frontend

# Or from backend directory
cd ../frontend
```

### Step 2: Install Node Dependencies

```bash
npm install
```

> **⚠️ Important**: This may take 3-5 minutes to download all packages.

### Step 3: Verify Frontend Setup

Check that `node_modules` folder was created:
```bash
# Windows
dir node_modules

# macOS/Linux
ls node_modules
```

---

## ▶️ Running the Application

You need to run **both** backend and frontend servers simultaneously.

### Terminal 1: Start Backend Server

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment (if not already activated)
# Windows:
.\venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# Start the Flask server
python app.py
```

**Expected Output:**
```
🚀 Starting Bone Cancer Detection API...
📍 Server starting instantly on port 5000...
✅ Server ready! X-ray checker first; multitask used if available.
🔗 Endpoints:
   - GET  /health - Check server and model status
   - POST /predict - Upload image for analysis
   - POST /report - Generate LLaMA text report
   - POST /cleanup_files - Clean temporary files
```

Backend will be running at: **http://localhost:5000**

### Terminal 2: Start Frontend Server

**Open a NEW terminal window/tab**

```bash
# Navigate to frontend directory
cd frontend

# Start the Vite development server
npm run dev
```

**Expected Output:**
```
VITE v5.4.2  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

Frontend will be running at: **http://localhost:5173**

---

## 🌐 Accessing the Application

1. Open your web browser
2. Navigate to: **http://localhost:5173**
3. You should see the purple-themed landing page
4. Click "Start Analysis" to begin using the application

---

## 📁 Project Structure

```
Bone Tumor X/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration settings
│   ├── requirements.txt       # Python dependencies
│   ├── models/                # ML model handlers
│   │   ├── xray_checker.py
│   │   ├── multitask_handler.py
│   │   └── llama_report_handler.py
│   ├── static/                # Static files (generated)
│   │   ├── uploads/           # Uploaded images
│   │   └── heatmaps/          # Generated visualizations
│   └── venv/                  # Python virtual environment (create this)
│
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── LandingPage.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── PredictionApp.tsx
│   │   │   ├── UploadSection.tsx
│   │   │   ├── ResultsSection.tsx
│   │   │   ├── ProcessingAnimation.tsx
│   │   │   └── Footer.tsx
│   │   ├── types/             # TypeScript types
│   │   ├── App.tsx            # Main app component
│   │   ├── index.css          # Global styles
│   │   └── main.tsx           # Entry point
│   ├── public/                # Public assets
│   ├── package.json           # Node dependencies
│   ├── tailwind.config.js     # Tailwind configuration
│   ├── vite.config.ts         # Vite configuration
│   └── node_modules/          # Node packages (create this)
│
└── README.md                  # This file
```

---

## 🛠️ Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'flask'`
- **Solution**: Make sure virtual environment is activated and run `pip install -r requirements.txt`

**Problem**: Port 5000 already in use
- **Solution**: Change port in `app.py` (last line): `app.run(debug=True, port=5001, use_reloader=False)`

**Problem**: TensorFlow installation fails
- **Solution**: Try installing with specific version: `pip install tensorflow==2.15.0`

### Frontend Issues

**Problem**: `npm: command not found`
- **Solution**: Install Node.js from [nodejs.org](https://nodejs.org/)

**Problem**: Port 5173 already in use
- **Solution**: Kill the process or Vite will automatically use next available port

**Problem**: `Cannot find module` errors
- **Solution**: Delete `node_modules` and `package-lock.json`, then run `npm install` again

### General Issues

**Problem**: CORS errors in browser console
- **Solution**: Ensure backend is running on port 5000 and frontend on 5173

**Problem**: Images not uploading
- **Solution**: Check that `static/uploads` and `static/heatmaps` directories exist in backend

---

## 📦 Dependencies

### Backend (Python)

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | Latest | Web framework |
| Flask-CORS | Latest | Cross-origin requests |
| TensorFlow | 2.x | Deep learning framework |
| PyTorch | Latest | ML framework |
| torchxrayvision | Latest | X-ray validation |
| Pillow | Latest | Image processing |
| opencv-python | Latest | Computer vision |
| transformers | Latest | LLaMA model |
| numpy | Latest | Numerical computing |

### Frontend (Node.js)

| Package | Version | Purpose |
|---------|---------|---------|
| React | 18.3 | UI framework |
| TypeScript | 5.5 | Type safety |
| Vite | 5.4 | Build tool |
| Tailwind CSS | 3.4 | Styling |
| Framer Motion | 12.x | Animations |
| Axios | 1.11 | HTTP requests |
| Lucide React | Latest | Icons |

---

## 🎯 Usage Guide

### 1. Upload X-Ray Image
- Click "Start Analysis" on landing page
- Drag & drop or browse for X-ray image
- Supported formats: JPG, PNG, JPEG

### 2. Analyze
- Click "Analyze Image" button
- Wait for AI processing (10-30 seconds)
- X-ray validation happens automatically

### 3. View Results
- **Classification**: Benign/Malignant/Normal
- **Tumor Type**: Specific tumor subtype
- **Pathology**: Detected abnormalities
- **Visualizations**: Heatmaps and overlays
- **AI Report**: Detailed text analysis (if LLaMA available)

### 4. New Analysis
- Click "New Scan" to analyze another image

---

## 🔒 API Endpoints

### `GET /health`
Check server and model status

### `POST /predict`
Upload image for analysis
- **Input**: Multipart form with `image` file
- **Output**: JSON with predictions and visualizations

### `POST /report`
Generate LLaMA text report
- **Input**: JSON with prediction data
- **Output**: JSON with detailed report text

### `POST /cleanup_files`
Clean temporary files
- **Output**: JSON with deletion statistics

---

## 🎨 Theme & Design

- **Color Scheme**: Purple/Violet gradients
- **Style**: Modern, glassmorphism effects
- **Layout**: Square corners, clean lines
- **Responsive**: Works on desktop and mobile

---

## 📝 Notes

- **First Run**: Backend may take 1-2 minutes to load ML models on first startup
- **GPU**: TensorFlow will use GPU if available (CUDA-enabled)
- **Memory**: Requires ~4GB RAM minimum, 8GB recommended
- **Models**: ML models are loaded on-demand to save memory
- **Storage**: Generated files are stored in `static/` directories

---

## 🤝 Contributing

This is a medical AI project. When contributing:
1. Test thoroughly with various X-ray images
2. Maintain code quality and documentation
3. Follow existing code style
4. Update README if adding features

---

## 📄 License

This project is for educational and research purposes.

---

## 👨‍💻 Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Verify all dependencies are installed correctly
3. Ensure both servers are running
4. Check browser console for errors
5. Check terminal output for backend errors

---

## 🚀 Quick Start Summary

```bash
# Backend Setup
cd backend
python -m venv venv
.\venv\Scripts\activate          # Windows
source venv/bin/activate         # macOS/Linux
pip install -r requirements.txt
python app.py

# Frontend Setup (New Terminal)
cd frontend
npm install
npm run dev

# Access: http://localhost:5173
```

---

**Built with ❤️ for fighting Bone Cancer**

*AI-Powered Bone Tumor Detection System*
