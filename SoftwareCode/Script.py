import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import matplotlib.pyplot as plt
import re
import time
from ultralytics import YOLO
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from PIL import Image, ImageTk

# Azure Computer Vision subscription key and endpoint
subscription_key = 'd7a12cb5ee7a43579e7ddf66ce15bd10'
endpoint = 'https://om1532.cognitiveservices.azure.com/'

# Initialize the ComputerVisionClient
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

# Load the YOLO models
model_fruit_veg = YOLO('yolov8n.pt')  # YOLOv8 Nano model for fruit/veg detection
model_product = YOLO(r"d:\NewGrid\train.pt")  # Model for extracting product details
model_fresh = YOLO(r"d:\NewGrid\fresh.pt")  # Freshness detection model

# Define a simple category mapping for fruits and vegetables
fruit_veg_classes = {
    'apple': 'fruit',
    'banana': 'fruit',
    'orange': 'fruit',
    'tomato': 'vegetable',
    'carrot': 'vegetable',
    'broccoli': 'vegetable',
}

# Function to classify objects into 'fruit', 'vegetable', or 'other'
def classify_object(label):
    return fruit_veg_classes.get(label, 'other')

# Function to extract expiry date, MRP, and manufacturing date using regex
def extract_product_details(text):
    expiry_pattern = r'(?i)(exp\s*(iry)?\.?\s*date|use before)[:\-\s]*([\d]{2}[./\-][\d]{2}[./\-][\d]{4}|[\d]+\s*months)'
    manufacturing_pattern = r'(?i)(prod|manufacturing|mfg|manuf|production)\.?\s*(date)?[:\-\s]*(\b[\w]+\s[\d]{4}|\b[\d]{2}[./\-][\d]{2}[./\-][\d]{4})'
    mrp_pattern = r'(?i)(mrp|price|mrp ₹)[:\-\s]₹?\s([\d.,]+)'

    expiry_date = re.search(expiry_pattern, text)
    manufacturing_date = re.search(manufacturing_pattern, text)
    mrp = re.search(mrp_pattern, text)

    return {
        'Expiry Date': expiry_date.group(3) if expiry_date else None,
        'Manufacturing Date': manufacturing_date.group(3) if manufacturing_date else None,
        'MRP': mrp.group(2) if mrp else None
    }

# Function to perform OCR on a local image region
def extract_text_from_image_region(image_region):
    roi_path = "temp_roi.jpg"
    cv2.imwrite(roi_path, image_region)

    with open(roi_path, 'rb') as image_stream:
        ocr_result = computervision_client.read_in_stream(image_stream, raw=True)

    operation_location = ocr_result.headers['Operation-Location']
    operation_id = operation_location.split('/')[-1]
    result = computervision_client.get_read_result(operation_id)

    while result.status not in ['succeeded', 'failed']:
        time.sleep(5)
        result = computervision_client.get_read_result(operation_id)

    if result.status == 'succeeded':
        text_lines = []
        for page in result.analyze_result.read_results:
            for line in page.lines:
                text_lines.append(line.text)
        return ' '.join(text_lines)

    return None

# Function to detect brands using Azure Computer Vision
def detect_brands_local(image_region):
    roi_path = "temp_roi_brand.jpg"
    cv2.imwrite(roi_path, image_region)
    
    with open(roi_path, "rb") as image_stream:
        analysis = computervision_client.analyze_image_in_stream(image_stream, visual_features=["Brands"])

    if analysis.brands:
        brand_info = []
        for brand in analysis.brands:
            brand_info.append(f"{brand.name} ({brand.confidence * 100:.2f}%)")
        return ', '.join(brand_info)
    return "No brands detected."

# Function to estimate service days based on confidence
def estimate_service_days(confidence, is_rotten=False):
    if is_rotten:  # Rotten fruit will always have 1 or fewer days of service
        return 1
    if confidence >= 0.80:  # High confidence
        return 7  # 7 days of service life
    elif confidence >= 0.60:  # Medium confidence
        return 3  # 3 days of service life
    else:  # Low confidence
        return 1  # 1 day of service life

# Main class for the Tkinter application
class DetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Product Detection App")
        self.root.geometry("700x700")

        # Frames
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=10)

        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(pady=10)

        # Input Image Label
        self.image_label = tk.Label(self.top_frame, text="Select an image to analyze:", font=("Arial", 12))
        self.image_label.grid(row=0, column=0, pady=10)

        # Buttons
        self.select_button = tk.Button(self.top_frame, text="Select Image", command=self.select_image, font=("Arial", 12), bg="lightblue")
        self.select_button.grid(row=0, column=1, padx=10)

        self.detect_button = tk.Button(self.top_frame, text="Run Detection", command=self.run_detection, state=tk.DISABLED, font=("Arial", 12), bg="green", fg="white")
        self.detect_button.grid(row=0, column=2, padx=10)

        # Input Image Display
        self.image_canvas = tk.Canvas(self.root, width=400, height=300, bg="lightgray")
        self.image_canvas.pack(pady=10)

        # Result Text
        self.result_text = tk.Text(self.bottom_frame, height=10, width=70, font=("Arial", 10))
        self.result_text.pack()

    def select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.image_path = file_path
            self.detect_button.config(state=tk.NORMAL)
            self.display_image(file_path)
            messagebox.showinfo("Selected Image", f"Selected image: {file_path}")

    def display_image(self, file_path):
        image = Image.open(file_path)
        image = image.resize((400, 300), Image.Resampling.LANCZOS)  # Updated for Pillow version 10+
        self.tk_image = ImageTk.PhotoImage(image)
        self.image_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.image_canvas.image = self.tk_image  # Prevent image from being garbage collected

    def run_detection(self):
        self.result_text.delete(1.0, tk.END)
        detected_product_details = {
            'MRP': None,
            'Manufacturing Date': None,
            'Expiry Date': None,
            'Brand': None
        }
        detected_fruits_vegetables = set()
        
        results_fruit_veg = model_fruit_veg(self.image_path)
        image = cv2.imread(self.image_path)

        for result in results_fruit_veg:
            boxes = result.boxes

            for box in boxes:
                bbox = box.xyxy[0].cpu().numpy().astype(int)
                confidence = box.conf[0].cpu().item()
                class_id = int(box.cls[0].cpu().item())
                class_name = model_fruit_veg.names[class_id]
                object_classification = classify_object(class_name)

                if object_classification == 'other':
                    roi = image[bbox[1]:bbox[3], bbox[0]:bbox[2]]
                    extracted_text = extract_text_from_image_region(roi)

                    if extracted_text:
                        product_details = extract_product_details(extracted_text)
                        for key, value in product_details.items():
                            if value and detected_product_details[key] is None:
                                detected_product_details[key] = value

                    detected_product_details['Brand'] = detect_brands_local(roi)

                else:
                    if class_name not in detected_fruits_vegetables:
                        detected_fruits_vegetables.add(class_name)
                        self.result_text.insert(tk.END, f"Detected {object_classification}: {class_name}\n")

                        roi_fresh = image[bbox[1]:bbox[3], bbox[0]:bbox[2]]
                        results_fresh = model_fresh(roi_fresh)

                        fresh_count = 0
                        rotten_count = 0
                        service_days = {}

                        for result in results_fresh:
                            boxes_fresh = result.boxes

                            for box in boxes_fresh:
                                class_id = int(box.cls[0].cpu().item())
                                class_name_fresh = model_fresh.names[class_id]
                                confidence_fresh = box.conf[0].cpu().item()
                                is_rotten = class_name_fresh.lower() == "rotten"

                                if is_rotten:
                                    rotten_count += 1
                                else:
                                    fresh_count += 1

                                service_days[class_name_fresh] = estimate_service_days(confidence_fresh, is_rotten)

                        self.result_text.insert(tk.END, f"Service life: {service_days}\n")

        for key, value in detected_product_details.items():
            self.result_text.insert(tk.END, f"{key}: {value}\n")

# Run the app
root = tk.Tk()
app = DetectionApp(root)
root.mainloop()