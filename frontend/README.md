# Bone Cancer Detection System

A comprehensive AI-powered web application for bone cancer detection and analysis using deep learning and medical imaging.

## 🏥 Overview

This system provides:
- **AI-Powered Analysis**: Uses ResNet50-based CNN for 3-class tumor classification (Normal, Benign, Malignant)
- **Visual Analysis**: Grad-CAM heatmap generation to highlight suspicious regions
- **Medical Reporting**: Automated PDF report generation with findings and recommendations
- **Professional UI**: Medical-themed interface with smooth animations and professional styling

## 🛠 Technology Stack

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **React Dropzone** for file upload
- **Axios** for API communication

### Backend
- **Flask** with Python 3.10+
- **TensorFlow/Keras** for AI model
- **OpenCV** for image processing
- **FPDF** for PDF report generation
- **Grad-CAM** implementation for heatmap visualization

## 📁 Project Structure

```
bone-cancer-detection/
├── src/                          # React frontend
│   ├── components/
│   │   ├── Header.tsx
│   │   ├── UploadSection.tsx
│   │   ├── ProcessingAnimation.tsx
│   │   ├── ResultsSection.tsx
│   │   └── Footer.tsx
│   ├── types/
│   │   └── index.ts
│   ├── App.tsx
│   └── main.tsx
├── backend/                      # Flask API
│   ├── app.py                   # Main Flask application
│   ├── requirements.txt         # Python dependencies
│   ├── models/                  # AI model files
│   └── static/                  # Generated files
│       ├── heatmaps/           # Grad-CAM visualizations
│       └── reports/            # PDF reports
└── README.md
```

## 🚀 Installation & Setup

### Prerequisites
- Node.js 18+
- Python 3.10+
- pip

### Backend Setup
1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Flask server:**
   ```bash
   python app.py
   ```
   Server runs on `http://localhost:5000`

### Frontend Setup
1. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```
   Application runs on `http://localhost:5173`

## 🔬 Model Information

The system uses a **ResNet50-based CNN** fine-tuned for bone cancer classification:

- **Input**: 224x224 RGB medical images (X-ray/MRI)
- **Classes**: 3 categories (Normal, Benign, Malignant)
- **Preprocessing**: Image normalization and resizing
- **Visualization**: Grad-CAM heatmaps from last convolutional layer

### Model Training (For Development)
```python
# Example training setup (not included in demo)
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model

base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation='relu')(x)
predictions = Dense(3, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=predictions)
# Compile and train with your bone cancer dataset
```

## 📊 API Endpoints

### POST `/predict`
Analyzes uploaded medical image and returns classification results.

**Request**: Multipart form data with image file
**Response**:
```json
{
  "prediction": "benign",
  "confidence": 0.87,
  "explanation": "Analysis detected a benign bone tumor...",
  "heatmap_url": "/static/heatmaps/heatmap_20250101_120000.jpg"
}
```

### POST `/report`
Generates downloadable PDF report with analysis results.

**Request**: JSON with prediction data
**Response**: PDF file download

## 🎨 UI Features

### Professional Medical Design
- Classic medical color scheme (whites, soft greys, subtle greens)
- Professional typography optimized for medical applications
- Responsive design for all device sizes

### Smooth Animations
- Fade-in animations for content sections
- Hover effects on interactive elements
- Loading animations during AI processing
- Smooth page transitions

### User Experience
- Drag-and-drop image upload
- Real-time upload preview
- Processing status indicators
- Clear result visualization
- One-click PDF report download

## 🔐 Security & Privacy

- Images processed locally and not permanently stored
- Secure file handling with validation
- CORS enabled for development
- Medical data privacy considerations

## ⚠️ Important Disclaimers

This system is designed for **research and educational purposes only**:

- ❌ Not intended for actual medical diagnosis
- ❌ Should not replace professional medical consultation
- ❌ Requires validation with real medical datasets
- ✅ Demonstrates AI/ML capabilities in medical imaging
- ✅ Educational tool for understanding medical AI

## 📈 Future Enhancements

- [ ] Integration with real trained models
- [ ] DICOM file format support
- [ ] Multi-model ensemble predictions
- [ ] Advanced visualization features
- [ ] User authentication system
- [ ] Medical professional dashboard
- [ ] Integration with hospital systems

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🆘 Support

For questions or support:
- Create an issue in the repository
- Review the documentation
- Check the troubleshooting section

---

**Made with ❤️ for advancing medical AI technology**