import json
import sys
import os
import numpy as np
import joblib
from collections import Counter

class DiseasePredictorSystem:
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.symptom_columns = None
        self.disease_info = None
        self.load_model()
    
    def load_model(self):
        """Load trained model and metadata"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Load model
            model_path = os.path.join(script_dir, 'disease_model.pkl')
            self.model = joblib.load(model_path)
            
            # Load label encoder
            encoder_path = os.path.join(script_dir, 'label_encoder.pkl')
            self.label_encoder = joblib.load(encoder_path)
            
            # Load symptom columns
            symptoms_path = os.path.join(script_dir, 'symptom_columns.json')
            with open(symptoms_path, 'r') as f:
                self.symptom_columns = json.load(f)
            
            # Load disease info
            info_path = os.path.join(script_dir, 'disease_info.json')
            with open(info_path, 'r') as f:
                self.disease_info = json.load(f)
            
        except Exception as e:
            raise Exception(f"Failed to load model: {e}")
    
    def normalize_symptom(self, symptom):
        """Normalize symptom name for matching"""
        # Convert to lowercase and replace spaces with underscores
        normalized = symptom.lower().replace(' ', '_').replace('-', '_')
        return normalized
    
    def match_symptoms(self, user_symptoms):
        """Match user symptoms to dataset symptom names"""
        matched_symptoms = []
        
        # Normalize user symptoms
        normalized_user = [self.normalize_symptom(s) for s in user_symptoms]
        
        # Try to match with dataset symptoms
        for symptom in self.symptom_columns:
            normalized_col = self.normalize_symptom(symptom)
            if normalized_col in normalized_user:
                matched_symptoms.append(symptom)
        
        return matched_symptoms
    
    def create_feature_vector(self, symptoms):
        """Create feature vector from symptoms"""
        feature_vector = np.zeros(len(self.symptom_columns))
        
        for i, symptom in enumerate(self.symptom_columns):
            if symptom in symptoms:
                feature_vector[i] = 1
        
        return feature_vector.reshape(1, -1)
    
    def predict(self, symptoms):
        """Predict disease from symptoms"""
        if not symptoms:
            return self.get_error_result("No symptoms provided")
        
        # Match symptoms to dataset
        matched_symptoms = self.match_symptoms(symptoms)
        
        if not matched_symptoms:
            return self.get_error_result("No matching symptoms found in database")
        
        # Create feature vector
        feature_vector = self.create_feature_vector(matched_symptoms)
        
        # Get predictions with probabilities
        prediction = self.model.predict(feature_vector)[0]
        probabilities = self.model.predict_proba(feature_vector)[0]
        
        # Get disease name
        disease = self.label_encoder.inverse_transform([prediction])[0]
        confidence = probabilities[prediction] * 100
        
        # Get top 5 predictions
        top_indices = np.argsort(probabilities)[::-1][:5]
        other_predictions = []
        
        for idx in top_indices[1:]:  # Skip first (already got it)
            other_disease = self.label_encoder.inverse_transform([idx])[0]
            other_prob = probabilities[idx] * 100
            if other_prob > 1:  # Only show if probability > 1%
                other_predictions.append({
                    "disease": other_disease,
                    "probability": round(other_prob, 1)
                })
        
        # Get disease details
        description = self.disease_info.get('descriptions', {}).get(disease, "No description available")
        precautions = self.disease_info.get('precautions', {}).get(disease, [])
        
        # Map to specialist
        specialist = self.get_specialist(disease)
        department = self.get_department(disease)
        
        # Calculate severity score
        severity_score = self.calculate_severity(matched_symptoms)
        
        return {
            "success": True,
            "top_disease": disease,
            "confidence": round(confidence, 1),
            "specialist": specialist,
            "department": department,
            "description": description,
            "precautions": precautions,
            "severity_score": severity_score,
            "matched_symptoms": matched_symptoms,
            "total_symptoms_analyzed": len(matched_symptoms),
            "other_predictions": other_predictions
        }
    
    def calculate_severity(self, symptoms):
        """Calculate severity score based on symptoms"""
        severity_map = self.disease_info.get('severity', {})
        total_severity = 0
        
        for symptom in symptoms:
            total_severity += severity_map.get(symptom, 3)  # Default severity = 3
        
        if not symptoms:
            return 0
        
        avg_severity = total_severity / len(symptoms)
        return round(avg_severity, 1)
    
    def get_specialist(self, disease):
        """Map disease to specialist"""
        specialist_map = {
            "Fungal infection": "Dermatologist",
            "Allergy": "Allergist",
            "GERD": "Gastroenterologist",
            "Chronic cholestasis": "Hepatologist",
            "Drug Reaction": "Toxicologist",
            "Peptic ulcer diseae": "Gastroenterologist",
            "AIDS": "Infectious Disease Specialist",
            "Diabetes": "Endocrinologist",
            "Gastroenteritis": "Gastroenterologist",
            "Bronchial Asthma": "Pulmonologist",
            "Hypertension": "Cardiologist",
            "Migraine": "Neurologist",
            "Cervical spondylosis": "Orthopedic Surgeon",
            "Paralysis (brain hemorrhage)": "Neurologist",
            "Jaundice": "Hepatologist",
            "Malaria": "Infectious Disease Specialist",
            "Chicken pox": "General Practitioner",
            "Dengue": "Infectious Disease Specialist",
            "Typhoid": "Infectious Disease Specialist",
            "hepatitis A": "Hepatologist",
            "Hepatitis B": "Hepatologist",
            "Hepatitis C": "Hepatologist",
            "Hepatitis D": "Hepatologist",
            "Hepatitis E": "Hepatologist",
            "Alcoholic hepatitis": "Hepatologist",
            "Tuberculosis": "Pulmonologist",
            "Common Cold": "General Practitioner",
            "Pneumonia": "Pulmonologist",
            "Dimorphic hemmorhoids(piles)": "General Surgeon",
            "Heart attack": "Cardiologist",
            "Varicose veins": "Vascular Surgeon",
            "Hypothyroidism": "Endocrinologist",
            "Hyperthyroidism": "Endocrinologist",
            "Hypoglycemia": "Endocrinologist",
            "Osteoarthristis": "Rheumatologist",
            "Arthritis": "Rheumatologist",
            "(vertigo) Paroymsal  Positional Vertigo": "ENT Specialist",
            "Acne": "Dermatologist",
            "Urinary tract infection": "Urologist",
            "Psoriasis": "Dermatologist",
            "Impetigo": "Dermatologist"
        }
        
        return specialist_map.get(disease, "General Practitioner")
    
    def get_department(self, disease):
        """Map disease to hospital department"""
        dept_map = {
            "Fungal infection": "Dermatology",
            "Allergy": "Allergy & Immunology",
            "GERD": "Gastroenterology",
            "Chronic cholestasis": "Hepatology",
            "Drug Reaction": "Emergency Medicine",
            "Peptic ulcer diseae": "Gastroenterology",
            "AIDS": "Infectious Diseases",
            "Diabetes": "Endocrinology",
            "Gastroenteritis": "Gastroenterology",
            "Bronchial Asthma": "Pulmonology",
            "Hypertension": "Cardiology",
            "Migraine": "Neurology",
            "Cervical spondylosis": "Orthopedics",
            "Paralysis (brain hemorrhage)": "Neurology",
            "Jaundice": "Hepatology",
            "Malaria": "Infectious Diseases",
            "Chicken pox": "General Medicine",
            "Dengue": "Infectious Diseases",
            "Typhoid": "Infectious Diseases",
            "hepatitis A": "Hepatology",
            "Hepatitis B": "Hepatology",
            "Hepatitis C": "Hepatology",
            "Hepatitis D": "Hepatology",
            "Hepatitis E": "Hepatology",
            "Alcoholic hepatitis": "Hepatology",
            "Tuberculosis": "Pulmonology",
            "Common Cold": "General Medicine",
            "Pneumonia": "Pulmonology",
            "Dimorphic hemmorhoids(piles)": "General Surgery",
            "Heart attack": "Cardiology",
            "Varicose veins": "Vascular Surgery",
            "Hypothyroidism": "Endocrinology",
            "Hyperthyroidism": "Endocrinology",
            "Hypoglycemia": "Endocrinology",
            "Osteoarthristis": "Rheumatology",
            "Arthritis": "Rheumatology",
            "(vertigo) Paroymsal  Positional Vertigo": "ENT",
            "Acne": "Dermatology",
            "Urinary tract infection": "Urology",
            "Psoriasis": "Dermatology",
            "Impetigo": "Dermatology"
        }
        
        return dept_map.get(disease, "General Medicine")
    
    def get_error_result(self, error_message):
        """Return error result structure"""
        return {
            "success": False,
            "error": error_message,
            "top_disease": "Unknown",
            "confidence": 0,
            "specialist": "General Practitioner",
            "department": "General Medicine",
            "description": "",
            "precautions": [],
            "severity_score": 0,
            "matched_symptoms": [],
            "total_symptoms_analyzed": 0,
            "other_predictions": []
        }

def main():
    try:
        # Read input
        script_dir = os.path.dirname(os.path.abspath(__file__))
        input_file = os.path.join(script_dir, "disease_input.json")
        
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        symptoms = data.get('symptoms', [])
        
        # Initialize predictor
        predictor = DiseasePredictorSystem()
        
        # Make prediction
        result = predictor.predict(symptoms)
        
        # Output JSON
        print(json.dumps(result))
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "top_disease": "Error",
            "confidence": 0,
            "specialist": "N/A",
            "department": "N/A",
            "description": "",
            "precautions": [],
            "severity_score": 0,
            "matched_symptoms": [],
            "total_symptoms_analyzed": 0,
            "other_predictions": []
        }
        print(json.dumps(error_result))
        sys.exit(1)

if __name__ == "__main__":
    main()