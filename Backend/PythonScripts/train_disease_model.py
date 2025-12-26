import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import joblib
import os
import json
import matplotlib.pyplot as plt

class DiseasePredictor:
    def __init__(self, dataset_path='dataset.csv'):
        self.dataset_path = dataset_path
        self.model = None
        self.label_encoder = None
        self.symptom_columns = None
        self.disease_info = {}
        
    def load_data(self):
        """Load and preprocess the dataset"""
        print("Loading dataset...")
        
        # Load main dataset
        df = pd.read_csv(self.dataset_path)
        
        print(f" Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        print(f" Columns: {list(df.columns)}")
        
        # The Kaggle dataset has Disease column and Symptom_1 to Symptom_17 columns
        # We need to convert this to binary format
        
        # Get all unique symptoms
        all_symptoms = set()
        symptom_cols = [col for col in df.columns if col.startswith('Symptom_')]
        
        for col in symptom_cols:
            symptoms = df[col].dropna().unique()
            all_symptoms.update([s.strip() for s in symptoms if pd.notna(s)])
        
        # Remove empty string if present
        all_symptoms.discard('')
        all_symptoms = sorted(list(all_symptoms))
        
        print(f" Found {len(all_symptoms)} unique symptoms")
        print(f" Found {df['Disease'].nunique()} unique diseases")
        
        # Create binary feature matrix
        binary_df = pd.DataFrame(0, index=df.index, columns=all_symptoms)
        
        for idx, row in df.iterrows():
            for col in symptom_cols:
                symptom = row[col]
                if pd.notna(symptom) and symptom.strip() in all_symptoms:
                    binary_df.at[idx, symptom.strip()] = 1
        
        # Add disease column
        binary_df['Disease'] = df['Disease'].values
        
        self.symptom_columns = all_symptoms
        
        return binary_df
    
    def load_additional_info(self):
        """Load symptom severity, descriptions, and precautions"""
        try:
            severity_df = pd.read_csv('Symptom-severity.csv')
            self.symptom_severity = dict(zip(severity_df['Symptom'], severity_df['weight']))
            print(f" Loaded symptom severity data")
        except:
            print(" Symptom severity file not found, using default weights")
            self.symptom_severity = {}
        
        try:
            desc_df = pd.read_csv('symptom_Description.csv')
            self.disease_descriptions = dict(zip(desc_df['Disease'], desc_df['Description']))
            print(f" Loaded disease descriptions")
        except:
            print(" Disease description file not found")
            self.disease_descriptions = {}
        
        try:
            precaution_df = pd.read_csv('symptom_precaution.csv')
            self.disease_precautions = {}
            for _, row in precaution_df.iterrows():
                disease = row['Disease']
                precautions = [row[f'Precaution_{i}'] for i in range(1, 5) 
                              if pd.notna(row.get(f'Precaution_{i}'))]
                self.disease_precautions[disease] = precautions
            print(f" Loaded disease precautions")
        except:
            print(" Precaution file not found")
            self.disease_precautions = {}
    
    def train_model(self, df):
        """Train the ML model"""
        print("\n Training AI Model...")
        
        # Prepare features and target
        X = df[self.symptom_columns]
        y = df['Disease']
        
        # Encode disease labels
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Train Random Forest model
        print("Training Random Forest Classifier...")
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n Model Training Complete!")
        print(f" Training Accuracy: {accuracy * 100:.2f}%")
        
        # Cross-validation score
        cv_scores = cross_val_score(self.model, X, y_encoded, cv=5)
        print(f"✅ Cross-Validation Accuracy: {cv_scores.mean() * 100:.2f}% (+/- {cv_scores.std() * 2 * 100:.2f}%)")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'symptom': self.symptom_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n Top 10 Most Important Symptoms:")
        for idx, row in feature_importance.head(10).iterrows():
            print(f"   {row['symptom']}: {row['importance']:.4f}")
        
        return accuracy, feature_importance
    
    def save_model(self):
        """Save trained model and metadata"""
        print("\n Saving model...")
        
        # Save model
        joblib.dump(self.model, 'disease_model.pkl')
        
        # Save label encoder
        joblib.dump(self.label_encoder, 'label_encoder.pkl')
        
        # Save symptom columns
        with open('symptom_columns.json', 'w') as f:
            json.dump(self.symptom_columns, f)
        
        # Save disease info
        disease_info = {
            'diseases': list(self.label_encoder.classes_),
            'num_symptoms': len(self.symptom_columns),
            'descriptions': self.disease_descriptions,
            'precautions': self.disease_precautions,
            'severity': self.symptom_severity
        }
        
        with open('disease_info.json', 'w') as f:
            json.dump(disease_info, f, indent=2)
        
        print(" Model saved successfully!")
        print("   - disease_model.pkl")
        print("   - label_encoder.pkl")
        print("   - symptom_columns.json")
        print("   - disease_info.json")
    
    def create_visualizations(self, feature_importance):
        """Create visualization charts"""
        print("\n📊 Creating visualizations...")
        
        try:
            # Feature importance chart
            plt.figure(figsize=(12, 8))
            top_features = feature_importance.head(15)
            plt.barh(top_features['symptom'], top_features['importance'], color='#1a5276')
            plt.xlabel('Importance Score', fontsize=12)
            plt.ylabel('Symptoms', fontsize=12)
            plt.title('Top 15 Most Important Symptoms for Disease Prediction', fontsize=14, fontweight='bold')
            plt.tight_layout()
            plt.savefig('feature_importance.png', dpi=150, bbox_inches='tight')
            print(" Saved: feature_importance.png")
            plt.close()
        except Exception as e:
            print(f" Could not create visualizations: {e}")

def main():
    """Main training pipeline"""
    print("=" * 60)
    print(" DISEASE PREDICTION MODEL TRAINING")
    print("=" * 60)
    
    # Initialize predictor
    predictor = DiseasePredictor()
    
    # Load data
    df = predictor.load_data()
    
    # Load additional information
    predictor.load_additional_info()
    
    # Train model
    accuracy, feature_importance = predictor.train_model(df)
    
    # Save model
    predictor.save_model()
    
    # Create visualizations
    predictor.create_visualizations(feature_importance)
    
    print("\n" + "=" * 60)
    print(" TRAINING COMPLETE!")
    print(f" Final Model Accuracy: {accuracy * 100:.2f}%")
    print("=" * 60)

if __name__ == "__main__":
    main()