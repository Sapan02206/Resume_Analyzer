"""
Machine Learning Model for Job Classification
Predicts which job role best fits a resume
"""
import pandas as pd
import numpy as np
import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import re

class JobClassificationModel:
    """ML model to classify resumes into job roles"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=3000, ngram_range=(1, 2))
        self.model = GradientBoostingClassifier(n_estimators=200, random_state=42)
        self.label_encoder = LabelEncoder()
        self.job_role_mapping = {}
        
    def map_categories_to_roles(self):
        """Map Kaggle dataset categories to our job roles"""
        # Mapping from Kaggle categories to our job roles
        self.job_role_mapping = {
            'Data Science': 'Data Scientist',
            'HR': 'Backend Developer',  # Generic mapping
            'Advocate': 'Backend Developer',
            'Arts': 'UI/UX Designer',
            'Web Designing': 'Frontend Developer',
            'Mechanical Engineer': 'Backend Developer',
            'Sales': 'Backend Developer',
            'Health and fitness': 'Backend Developer',
            'Civil Engineer': 'Backend Developer',
            'Java Developer': 'Backend Developer',
            'Business Analyst': 'Data Scientist',
            'SAP Developer': 'Backend Developer',
            'Automation Testing': 'DevOps Engineer',
            'Electrical Engineering': 'Backend Developer',
            'Operations Manager': 'DevOps Engineer',
            'Python Developer': 'Backend Developer',
            'DevOps Engineer': 'DevOps Engineer',
            'Network Security Engineer': 'DevOps Engineer',
            'PMO': 'Backend Developer',
            'Database': 'Backend Developer',
            'Hadoop': 'Data Scientist',
            'ETL Developer': 'Data Scientist',
            'DotNet Developer': 'Backend Developer',
            'Blockchain': 'Backend Developer',
            'Testing': 'DevOps Engineer'
        }
        
        # Our target job roles
        self.target_roles = [
            'Frontend Developer',
            'Backend Developer',
            'Full Stack Developer',
            'Data Scientist',
            'DevOps Engineer',
            'Mobile Developer',
            'UI/UX Designer'
        ]
    
    def prepare_training_data(self, resume_df):
        """Prepare training data from resume dataset"""
        print("\n📊 Preparing training data...")
        
        X = []  # Resume texts
        y = []  # Job roles
        
        for idx, row in resume_df.iterrows():
            # Combine all text fields to create resume text
            text_parts = []
            
            if pd.notna(row.get('career_objective')):
                text_parts.append(str(row['career_objective']))
            if pd.notna(row.get('skills')):
                text_parts.append(str(row['skills']))
            if pd.notna(row.get('responsibilities')):
                text_parts.append(str(row['responsibilities']))
            if pd.notna(row.get('related_skils_in_job')):
                text_parts.append(str(row['related_skils_in_job']))
            
            resume_text = ' '.join(text_parts)
            
            # Get position as category
            position = str(row.get('positions', 'Backend Developer'))
            
            if len(resume_text) < 50:  # Skip very short resumes
                continue
            
            # Map position to our job role
            job_role = self.map_position_to_role(position)
            
            X.append(resume_text.lower())
            y.append(job_role)
            
            if (idx + 1) % 1000 == 0:
                print(f"  Processed {idx + 1} resumes...")
        
        print(f"✅ Prepared {len(X)} training samples")
        
        # Show distribution
        print("\n📊 Job Role Distribution:")
        role_counts = pd.Series(y).value_counts()
        for role, count in role_counts.items():
            print(f"  {role}: {count}")
        
        return np.array(X), np.array(y)
    
    def map_position_to_role(self, position):
        """Map position string to our job roles"""
        position_lower = position.lower()
        
        if any(word in position_lower for word in ['data', 'analyst', 'scientist', 'ml', 'ai']):
            return 'Data Scientist'
        elif any(word in position_lower for word in ['frontend', 'front-end', 'react', 'angular', 'vue']):
            return 'Frontend Developer'
        elif any(word in position_lower for word in ['devops', 'sre', 'infrastructure', 'cloud']):
            return 'DevOps Engineer'
        elif any(word in position_lower for word in ['mobile', 'android', 'ios', 'flutter']):
            return 'Mobile Developer'
        elif any(word in position_lower for word in ['ui', 'ux', 'design']):
            return 'UI/UX Designer'
        elif any(word in position_lower for word in ['full stack', 'fullstack']):
            return 'Full Stack Developer'
        else:
            return 'Backend Developer'  # Default
    
    def train(self, resume_csv_path='data/archive/resume_data.csv'):
        """Train the job classification model"""
        print("\n" + "="*60)
        print("TRAINING JOB CLASSIFICATION MODEL")
        print("="*60)
        
        # Setup mappings
        self.map_categories_to_roles()
        
        # Load resume dataset
        print("\n📂 Loading resume dataset...")
        df = pd.read_csv(resume_csv_path)
        print(f"✅ Loaded {len(df)} resumes")
        
        # Prepare training data
        X, y = self.prepare_training_data(df)
        
        # Encode labels
        print("\n🔢 Encoding job role labels...")
        y_encoded = self.label_encoder.fit_transform(y)
        print(f"  Number of classes: {len(self.label_encoder.classes_)}")
        print(f"  Classes: {list(self.label_encoder.classes_)}")
        
        # Split data
        print("\n✂️  Splitting data (80% train, 20% test)...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        print(f"  Training samples: {len(X_train)}")
        print(f"  Testing samples: {len(X_test)}")
        
        # Vectorize text
        print("\n🔤 Vectorizing text with TF-IDF...")
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        print(f"  Feature dimensions: {X_train_vec.shape[1]}")
        
        # Train model
        print("\n🤖 Training Gradient Boosting model...")
        print("  This may take several minutes...")
        self.model.fit(X_train_vec, y_train)
        print("✅ Model training complete!")
        
        # Evaluate
        print("\n📈 Evaluating model...")
        y_pred = self.model.predict(X_test_vec)
        
        accuracy = accuracy_score(y_test, y_pred)
        print(f"\n📊 Model Performance:")
        print(f"  Accuracy: {accuracy:.4f}")
        
        # Classification report
        print("\n📋 Classification Report:")
        print(classification_report(
            y_test, y_pred,
            target_names=self.label_encoder.classes_,
            zero_division=0
        ))
        
        # Cross-validation
        print("\n🔄 Cross-validation (5-fold)...")
        cv_scores = cross_val_score(self.model, X_train_vec, y_train, cv=5)
        print(f"  CV Scores: {cv_scores}")
        print(f"  Mean CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        return {
            'accuracy': accuracy,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        }
    
    def predict(self, resume_text):
        """Predict job role from resume text"""
        # Vectorize
        text_vec = self.vectorizer.transform([resume_text.lower()])
        
        # Predict
        prediction = self.model.predict(text_vec)[0]
        probabilities = self.model.predict_proba(text_vec)[0]
        
        # Decode label
        job_role = self.label_encoder.inverse_transform([prediction])[0]
        
        # Get top 3 predictions
        top_3_indices = np.argsort(probabilities)[-3:][::-1]
        top_3_roles = [
            {
                'role': self.label_encoder.inverse_transform([idx])[0],
                'probability': probabilities[idx]
            }
            for idx in top_3_indices
        ]
        
        return {
            'predicted_role': job_role,
            'confidence': probabilities[prediction],
            'top_3_predictions': top_3_roles
        }
    
    def save_model(self, path='ml_models/saved/job_classification_model.pkl'):
        """Save trained model"""
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        model_data = {
            'vectorizer': self.vectorizer,
            'model': self.model,
            'label_encoder': self.label_encoder,
            'job_role_mapping': self.job_role_mapping,
            'target_roles': self.target_roles
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"\n💾 Model saved to: {path}")
    
    def load_model(self, path='ml_models/saved/job_classification_model.pkl'):
        """Load trained model"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.vectorizer = model_data['vectorizer']
        self.model = model_data['model']
        self.label_encoder = model_data['label_encoder']
        self.job_role_mapping = model_data['job_role_mapping']
        self.target_roles = model_data['target_roles']
        
        print(f"✅ Model loaded from: {path}")


if __name__ == '__main__':
    # Train the model
    model = JobClassificationModel()
    metrics = model.train()
    model.save_model()
    
    print("\n" + "="*60)
    print("✅ JOB CLASSIFICATION MODEL TRAINING COMPLETE!")
    print("="*60)
