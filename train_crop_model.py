import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import urllib.request
import os

def main():
    print("Downloading Crop Recommendation dataset...")
    # This dataset is commonly used for agricultural ML projects
    url = "https://raw.githubusercontent.com/Gladiator07/Harvestify/master/Data-processed/crop_recommendation.csv"
    dataset_path = "crop_recommendation.csv"
    
    if not os.path.exists(dataset_path):
        urllib.request.urlretrieve(url, dataset_path)
        print("Dataset downloaded successfully.")
    else:
        print("Dataset already exists locally.")
        
    print("Loading and preparing data...")
    df = pd.read_csv(dataset_path)
    
    # The columns are N, P, K, temperature, humidity, ph, rainfall, label
    X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
    y = df['label']
    
    # Split into 80% training and 20% testing
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Classifier...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    
    print("Evaluating Model Accuracy...")
    y_pred = rf_model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print("="*50)
    print(f"Model Training Complete. Validation Accuracy: {acc * 100:.2f}%")
    print("="*50)
    
    # Save the model into a dedicated models directory
    os.makedirs("models", exist_ok=True)
    model_path = "models/crop_recommendation_model.pkl"
    joblib.dump(rf_model, model_path)
    print(f"✅ Model successfully saved to {model_path} - Ready for Streamlit integration!")

if __name__ == "__main__":
    main()