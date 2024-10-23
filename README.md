# Smart Vision Quality Control System

![Project Banner](https://via.placeholder.com/900x300.png?text=Smart+Vision+Quality+Control+System)

## 🎥 YouTube Demo

[![Watch the video]](https://www.youtube.com/watch?v=_Qf_MK-I3Dk)

Click the image above to watch the demo of our project on YouTube.

---

## 📖 Project Overview

The **Smart Vision Quality Control System** is an AI-powered automated quality control and inventory management system designed for conveyor belt applications. It uses a tri-camera setup, infrared sensor, and custom AI models to inspect product quality in real-time. The system assesses packaging defects, product labels, MRP, expiration dates, and even freshness for perishable goods.

### Key Features:
- **Tri-Camera Setup**: Captures top, left, and right views of products for comprehensive inspection.
- **Text Recognition**: Uses Azure OCR and SpaCy NER to extract MRP, expiry, and brand information.
- **Freshness Detection**: Analyzes fruits and vegetables using a custom YOLOv8 model to predict shelf life.
- **Data Logging**: Real-time logging of inspection results and Excel report generation for analysis.

![System Overview](https://via.placeholder.com/800x400.png?text=System+Overview)

---

## 🛠️ Technology Stack

- **Hardware**: 
  - ESP32 
  - Infrared Sensor 
  - 12v DC Motors
  - Tri-Camera Setup
- **Software**: 
  - YOLOv8 (Object Detection)
  - Azure OCR (Text Detection)
  - SpaCy NER (Named Entity Recognition)
  - BERT (Language Model)
  - Python (UI and Excel Report Generation)
  - Arduino IDE

---

## 🚀 How It Works

1. **Product Detection**: The IR sensor detects when a product is on the conveyor belt.
2. **Camera Activation**: The ESP32 triggers the cameras to capture images from multiple angles.
3. **Image Processing**: Captured images are processed to detect labels, freshness, and defects.
4. **Data Logging**: Results are stored in real-time, and an Excel report is generated.

---

## 📷 Screenshots

### 1. Tri-Camera Setup Capturing Images
![Tri-Camera Setup](https://via.placeholder.com/800x400.png?text=Tri-Camera+Setup)

### 2. Freshness Detection with Custom Model
![Freshness Detection](https://via.placeholder.com/800x400.png?text=Freshness+Detection)

### 3. Excel Report Generated with Inspection Results
![Excel Report](https://via.placeholder.com/800x400.png?text=Excel+Report)

---

## 📂 Project Structure

```bash
SmartVisionQC/
├── hardware/                # ESP32, sensor, motor control setup
├── software/
│   ├── yolo_model/          # YOLOv8 model for defect and freshness detection
│   ├── azure_ocr/           # OCR script for text detection (MRP, expiry)
│   ├── spacy_ner/           # NER script for label information extraction
│   ├── excel_report/        # Python script for generating Excel reports
│   └── ...
├── data/                    # Datasets used for model training and testing
└── README.md


## 📈 Model Performance

| Feature              | Model        | Accuracy  |
|----------------------|--------------|-----------|
| Product Label Detection | Custom YOLOv8  | 71.39%    |
| Freshness Detection  | Custom YOLOv8  | 88.56%    |
| Text Detection (OCR) | Azure OCR    | 95%       |
| Label Info Extraction | SpaCy NER    | 88%       |

---

## 📦 Installation

### Prerequisites:
- ESP32 with sensors and camera setup
- Python 3.x
- Arduino IDE
- Required Python libraries: 
  ```bash
  pip install opencv-python torch azure-cognitiveservices-vision-computervision spacy pandas openpyxl
