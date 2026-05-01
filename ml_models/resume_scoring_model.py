"""
Machine Learning Model for Resume Scoring
Predicts match score between resume and job role
"""
import pandas as pd
import numpy as np
import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import LabelEncoder
import re

class ResumeScoringModel:
    """ML model to predict match score between resume and job role"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=2000, ngram_range=(1, 2))
        self.model = GradientBoostingRegressor(n_estimators=150, random_state=42)
        self.role_encoder = LabelEncoder()
        self.skill_list = []
        
    def load_skills(self, skills_path='data/skills.json'):
        """Load skill list"""
        with open(skills_path, 'r') as f:
            self.skill_list = json.load(f)
        print(f"✅ Loaded {len(self.skill_list)} skills")
    
    def load_job_roles(self, job_roles_path='data/job_roles.json'):
        """Load job roles"""
        with open(job_roles_path, 'r') as f:
            self.job_roles = json.load(f)
        print(f"✅ Loaded {len(self.job_roles)} job roles")
    
    def calculate_match_score(self, resume_text, job_role):
        """Calculate actual match score (for training labels)"""
        resume_text_lower = resume_text.lower()
        
        # Get required and optional skills for job role
        role_data = self.job_roles.get(job_role, {})
        required_skills = role_data.get('required_skills', [])
        optional_skills = role_data.get('optional_skills', [])
        
        # Count matched skills
        matched_required = sum(
            1 for skill in required_skills
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', resume_text_lower)
        )
        
        matched_optional = sum(
            1 for skill in optional_skills
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', resume_text_lower)
        )
        
        # Calculate score
        if len(required_skills) > 0:
            required_score = (matched_required / len(required_skills)) * 70
        else:
            required_score = 0
        
        if len(optional_skills) > 0:
            optional_score = (matched_optional / len(optional_skills)) * 30
        else:
            optional_score = 0
        
        total_score = required_score + optional_score
        
        return min(100, max(0, total_score))
    
    def prepare_training_data(self, resume_df):
        """Prepare training data from resume dataset"""
        print("\n📊 Preparing training data...")
        
        X_text = []  # Resume texts
        X_role = []  # Job roles
        y = []  # Match scores
        
        job_role_names = list(self.job_roles.keys())
        
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
            
            if len(resume_text) < 50:  # Skip very short resumes
                continue
            
            # Generate training samples for each job role
            for job_role in job_role_names:
                match_score = self.calculate_match_score(resume_text, job_role)
                
                X_text.append(resume_text.lower())
                X_role.append(job_role)
                y.append(match_score)
            
            if (idx + 1) % 500 == 0:
                print(f"  Processed {idx + 1} resumes...")
        
        print(f"✅ Prepared {len(X_text)} training samples")
        
        return np.array(X_text), np.array(X_role), np.array(y)
    
    def create_features(self, X_text, X_role):
        """Create feature matrix combining text and role"""
        # Vectorize text
        X_text_vec = self.vectorizer.transform(X_text)
        
        # Encode roles
        X_role_encoded = self.role_encoder.transform(X_role).reshape(-1, 1)
        
        # Combine features
        from scipy.sparse import hstack, csr_matrix
        X_combined = hstack([X_text_vec, csr_matrix(X_role_encoded)])
        
        return X_combined
    
    def train(self, resume_csv_path='data/archive/resume_data.csv', sample_size=2000):
        """Train the resume scoring model"""
        print("\n" + "="*60)
        print("TRAINING RESUME SCORING MODEL")
        print("="*60)
        
        # Load skills and job roles
        self.load_skills()
        self.load_job_roles()
        
        # Load resume dataset
        print("\n📂 Loading resume dataset...")
        df = pd.read_csv(resume_csv_path)
        
        # Sample for faster training (optional)
        if sample_size and len(df) > sample_size:
            df = df.sample(n=sample_size, random_state=42)
            print(f"✅ Sampled {len(df)} resumes for training")
        else:
            print(f"✅ Loaded {len(df)} resumes")
        
        # Prepare training data
        X_text, X_role, y = self.prepare_training_data(df)
        
        # Encode roles
        print("\n🔢 Encoding job roles...")
        self.role_encoder.fit(X_role)
        
        # Vectorize text (fit on all data)
        print("\n🔤 Vectorizing text with TF-IDF...")
        self.vectorizer.fit(X_text)
        
        # Split data
        print("\n✂️  Splitting data (80% train, 20% test)...")
        X_text_train, X_text_test, X_role_train, X_role_test, y_train, y_test = train_test_split(
            X_text, X_role, y, test_size=0.2, random_state=42
        )
        print(f"  Training samples: {len(X_text_train)}")
        print(f"  Testing samples: {len(X_text_test)}")
        
        # Create feature matrices
        print("\n🔧 Creating feature matrices...")
        X_train = self.create_features(X_text_train, X_role_train)
        X_test = self.create_features(X_text_test, X_role_test)
        print(f"  Feature dimensions: {X_train.shape[1]}")
        
        # Train model
        print("\n🤖 Training Gradient Boosting Regressor...")
        print("  This may take several minutes...")
        self.model.fit(X_train, y_train)
        print("✅ Model training complete!")
        
        # Evaluate
        print("\n📈 Evaluating model...")
        y_pred = self.model.predict(X_test)
        
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"\n📊 Model Performance:")
        print(f"  RMSE: {rmse:.4f}")
        print(f"  MAE: {mae:.4f}")
        print(f"  R² Score: {r2:.4f}")
        
        # Show sample predictions
        print("\n🔍 Sample Predictions:")
        sample_indices = np.random.choice(len(y_test), 5, replace=False)
        for idx in sample_indices:
            print(f"  Actual: {y_test[idx]:.2f}% | Predicted: {y_pred[idx]:.2f}%")
        
        return {
            'rmse': rmse,
            'mae': mae,
            'r2': r2
        }
    
    def predict(self, resume_text, job_role):
        """Predict match score for resume and job role"""
        # Create feature matrix
        X_text = np.array([resume_text.lower()])
        X_role = np.array([job_role])
        
        X_features = self.create_features(X_text, X_role)
        
        # Predict
        score = self.model.predict(X_features)[0]
        
        # Clip to valid range
        score = min(100, max(0, score))
        
        return round(score, 2)
    
    def save_model(self, path='ml_models/saved/resume_scoring_model.pkl'):
        """Save trained model"""
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        model_data = {
            'vectorizer': self.vectorizer,
            'model': self.model,
            'role_encoder': self.role_encoder,
            'skill_list': self.skill_list,
            'job_roles': self.job_roles
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"\n💾 Model saved to: {path}")
    
    def load_model(self, path='ml_models/saved/resume_scoring_model.pkl'):
        """Load trained model"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.vectorizer = model_data['vectorizer']
        self.model = model_data['model']
        self.role_encoder = model_data['role_encoder']
        self.skill_list = model_data['skill_list']
        self.job_roles = model_data['job_roles']
        
        print(f"✅ Model loaded from: {path}")


if __name__ == '__main__':
    # Train the model
    model = ResumeScoringModel()
    metrics = model.train(sample_size=2000)  # Use 2000 resumes for faster training
    model.save_model()
    
    print("\n" + "="*60)
    print("✅ RESUME SCORING MODEL TRAINING COMPLETE!")
    print("="*60)
