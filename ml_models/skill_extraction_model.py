"""
Machine Learning Model for Skill Extraction
Uses NER (Named Entity Recognition) to extract skills from resume text
"""
import pandas as pd
import numpy as np
import json
import pickle
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score
import re

class SkillExtractionModel:
    """ML model to extract skills from resume text"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 3))
        self.model = MultiOutputClassifier(RandomForestClassifier(n_estimators=100, random_state=42))
        self.skill_list = []
        self.label_encoder = {}
        
    def load_skills(self, skills_path='data/skills.json'):
        """Load skill list"""
        with open(skills_path, 'r') as f:
            self.skill_list = json.load(f)
        print(f"✅ Loaded {len(self.skill_list)} skills")
        
    def prepare_training_data(self, resume_df):
        """
        Prepare training data from resume dataset
        Creates labels for each skill (present/absent in resume)
        """
        print("\n📊 Preparing training data...")
        
        X = []  # Resume texts
        y = []  # Skill labels (binary matrix)
        
        for idx, row in resume_df.iterrows():
            # Combine all text fields to create resume text
            text_parts = []
            
            # Add career objective
            if pd.notna(row.get('career_objective')):
                text_parts.append(str(row['career_objective']))
            
            # Add skills
            if pd.notna(row.get('skills')):
                text_parts.append(str(row['skills']))
            
            # Add responsibilities
            if pd.notna(row.get('responsibilities')):
                text_parts.append(str(row['responsibilities']))
            
            # Add related skills in job
            if pd.notna(row.get('related_skils_in_job')):
                text_parts.append(str(row['related_skils_in_job']))
            
            resume_text = ' '.join(text_parts).lower()
            
            if len(resume_text) < 50:  # Skip very short resumes
                continue
            
            X.append(resume_text)
            
            # Create binary labels for each skill
            skill_labels = []
            for skill in self.skill_list:
                # Check if skill is present in resume
                skill_pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                is_present = 1 if re.search(skill_pattern, resume_text) else 0
                skill_labels.append(is_present)
            
            y.append(skill_labels)
            
            if (idx + 1) % 1000 == 0:
                print(f"  Processed {idx + 1} resumes...")
        
        print(f"✅ Prepared {len(X)} training samples")
        return np.array(X), np.array(y)
    
    def train(self, resume_csv_path='data/archive/resume_data.csv'):
        """Train the skill extraction model"""
        print("\n" + "="*60)
        print("TRAINING SKILL EXTRACTION MODEL")
        print("="*60)
        
        # Load skills
        self.load_skills()
        
        # Load resume dataset
        print("\n📂 Loading resume dataset...")
        df = pd.read_csv(resume_csv_path)
        print(f"✅ Loaded {len(df)} resumes")
        
        # Prepare training data
        X, y = self.prepare_training_data(df)
        
        # Split data
        print("\n✂️  Splitting data (80% train, 20% test)...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        print(f"  Training samples: {len(X_train)}")
        print(f"  Testing samples: {len(X_test)}")
        
        # Vectorize text
        print("\n🔤 Vectorizing text with TF-IDF...")
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        print(f"  Feature dimensions: {X_train_vec.shape[1]}")
        
        # Train model
        print("\n🤖 Training Random Forest model...")
        print("  This may take several minutes...")
        self.model.fit(X_train_vec, y_train)
        print("✅ Model training complete!")
        
        # Evaluate
        print("\n📈 Evaluating model...")
        y_pred = self.model.predict(X_test_vec)
        
        # Calculate metrics
        f1_micro = f1_score(y_test, y_pred, average='micro')
        f1_macro = f1_score(y_test, y_pred, average='macro')
        
        print(f"\n📊 Model Performance:")
        print(f"  F1 Score (Micro): {f1_micro:.4f}")
        print(f"  F1 Score (Macro): {f1_macro:.4f}")
        
        # Calculate accuracy per skill
        skill_accuracies = []
        for i in range(len(self.skill_list)):
            accuracy = np.mean(y_test[:, i] == y_pred[:, i])
            skill_accuracies.append(accuracy)
        
        avg_accuracy = np.mean(skill_accuracies)
        print(f"  Average Skill Accuracy: {avg_accuracy:.4f}")
        
        return {
            'f1_micro': f1_micro,
            'f1_macro': f1_macro,
            'avg_accuracy': avg_accuracy
        }
    
    def predict(self, resume_text):
        """Predict skills from resume text"""
        # Vectorize
        text_vec = self.vectorizer.transform([resume_text.lower()])
        
        # Predict
        predictions = self.model.predict(text_vec)[0]
        
        # Get predicted skills
        predicted_skills = [
            self.skill_list[i] for i in range(len(predictions))
            if predictions[i] == 1
        ]
        
        return predicted_skills
    
    def save_model(self, path='ml_models/saved/skill_extraction_model.pkl'):
        """Save trained model"""
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        model_data = {
            'vectorizer': self.vectorizer,
            'model': self.model,
            'skill_list': self.skill_list
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"\n💾 Model saved to: {path}")
    
    def load_model(self, path='ml_models/saved/skill_extraction_model.pkl'):
        """Load trained model"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.vectorizer = model_data['vectorizer']
        self.model = model_data['model']
        self.skill_list = model_data['skill_list']
        
        print(f"✅ Model loaded from: {path}")


if __name__ == '__main__':
    # Train the model
    model = SkillExtractionModel()
    metrics = model.train()
    model.save_model()
    
    print("\n" + "="*60)
    print("✅ SKILL EXTRACTION MODEL TRAINING COMPLETE!")
    print("="*60)
