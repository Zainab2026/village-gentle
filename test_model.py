from transformers import pipeline
print("Testing HuggingFace model download...")
classifier = pipeline("image-classification", model="linkan/plant-disease-image-classification")
print("Model loaded successfully!")