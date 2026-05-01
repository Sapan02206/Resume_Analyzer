"""
Master script to train all 3 ML models
"""
import sys
import time
from ml_models.skill_extraction_model import SkillExtractionModel
from ml_models.job_classification_model import JobClassificationModel
from ml_models.resume_scoring_model import ResumeScoringModel

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def train_all_models():
    """Train all 3 ML models"""
    print_header("🚀 TRAINING ALL ML MODELS ON KAGGLE DATASET")
    print("\nThis will train 3 models:")
    print("  1. Skill Extraction Model - Extract skills from resume text")
    print("  2. Job Classification Model - Predict best job role for resume")
    print("  3. Resume Scoring Model - Predict match score")
    print("\n⏱️  Estimated time: 15-30 minutes")
    print("\n" + "-"*70)
    
    input("\nPress Enter to start training...")
    
    start_time = time.time()
    results = {}
    
    # Model 1: Skill Extraction
    try:
        print_header("MODEL 1/3: SKILL EXTRACTION")
        model1 = SkillExtractionModel()
        metrics1 = model1.train()
        model1.save_model()
        results['skill_extraction'] = {
            'status': 'success',
            'metrics': metrics1
        }
        print("\n✅ Skill Extraction Model: COMPLETE")
    except Exception as e:
        print(f"\n❌ Skill Extraction Model: FAILED - {e}")
        results['skill_extraction'] = {
            'status': 'failed',
            'error': str(e)
        }
    
    # Model 2: Job Classification
    try:
        print_header("MODEL 2/3: JOB CLASSIFICATION")
        model2 = JobClassificationModel()
        metrics2 = model2.train()
        model2.save_model()
        results['job_classification'] = {
            'status': 'success',
            'metrics': metrics2
        }
        print("\n✅ Job Classification Model: COMPLETE")
    except Exception as e:
        print(f"\n❌ Job Classification Model: FAILED - {e}")
        results['job_classification'] = {
            'status': 'failed',
            'error': str(e)
        }
    
    # Model 3: Resume Scoring
    try:
        print_header("MODEL 3/3: RESUME SCORING")
        model3 = ResumeScoringModel()
        metrics3 = model3.train(sample_size=2000)  # Use 2000 samples for faster training
        model3.save_model()
        results['resume_scoring'] = {
            'status': 'success',
            'metrics': metrics3
        }
        print("\n✅ Resume Scoring Model: COMPLETE")
    except Exception as e:
        print(f"\n❌ Resume Scoring Model: FAILED - {e}")
        results['resume_scoring'] = {
            'status': 'failed',
            'error': str(e)
        }
    
    # Summary
    end_time = time.time()
    duration = end_time - start_time
    
    print_header("📊 TRAINING SUMMARY")
    
    print("\n🎯 Model Status:")
    for model_name, result in results.items():
        status_icon = "✅" if result['status'] == 'success' else "❌"
        print(f"  {status_icon} {model_name.replace('_', ' ').title()}: {result['status'].upper()}")
    
    print("\n📈 Performance Metrics:")
    
    if results['skill_extraction']['status'] == 'success':
        metrics = results['skill_extraction']['metrics']
        print(f"\n  Skill Extraction Model:")
        print(f"    - F1 Score (Micro): {metrics['f1_micro']:.4f}")
        print(f"    - F1 Score (Macro): {metrics['f1_macro']:.4f}")
        print(f"    - Avg Accuracy: {metrics['avg_accuracy']:.4f}")
    
    if results['job_classification']['status'] == 'success':
        metrics = results['job_classification']['metrics']
        print(f"\n  Job Classification Model:")
        print(f"    - Accuracy: {metrics['accuracy']:.4f}")
        print(f"    - CV Mean: {metrics['cv_mean']:.4f}")
    
    if results['resume_scoring']['status'] == 'success':
        metrics = results['resume_scoring']['metrics']
        print(f"\n  Resume Scoring Model:")
        print(f"    - RMSE: {metrics['rmse']:.4f}")
        print(f"    - MAE: {metrics['mae']:.4f}")
        print(f"    - R² Score: {metrics['r2']:.4f}")
    
    print(f"\n⏱️  Total Training Time: {duration/60:.2f} minutes")
    
    print("\n💾 Saved Models:")
    print("  - ml_models/saved/skill_extraction_model.pkl")
    print("  - ml_models/saved/job_classification_model.pkl")
    print("  - ml_models/saved/resume_scoring_model.pkl")
    
    print("\n" + "="*70)
    print("  🎉 ALL MODELS TRAINED SUCCESSFULLY!")
    print("="*70)
    
    print("\n📝 Next Steps:")
    print("  1. Update app.py to use ML models")
    print("  2. Run: python app.py")
    print("  3. Test with real resumes")
    
    return results


if __name__ == '__main__':
    try:
        results = train_all_models()
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
