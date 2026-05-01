import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.utils import secure_filename
from config import Config
from models import db, Resume
from modules.parser import ResumeParser
from modules.skill_extractor import SkillExtractor
from modules.matcher import SkillMatcher
from modules.recommender import SkillRecommender
from modules.dataset_processor import DatasetProcessor

app = Flask(__name__)
app.config.from_object(Config)

# Configure session
app.secret_key = app.config['SECRET_KEY']

# Initialize PostgreSQL database
db.init_app(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize modules
skill_extractor = SkillExtractor(app.config['SKILLS_DATA_PATH'])
skill_matcher = SkillMatcher(
    app.config['JOB_ROLES_DATA_PATH'],
    app.config['REQUIRED_SKILL_WEIGHT'],
    app.config['OPTIONAL_SKILL_WEIGHT']
)
skill_recommender = SkillRecommender()

# Initialize dataset processor for Kaggle data
try:
    dataset_processor = DatasetProcessor()
    dataset_processor.load_datasets()
    print("✅ Kaggle datasets loaded successfully!")
except Exception as e:
    dataset_processor = None
    print(f"⚠️  Kaggle datasets not loaded: {e}")

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """Render main upload page"""
    job_roles = skill_matcher.get_available_roles()
    return render_template('index.html', job_roles=job_roles)

@app.route('/career-dashboard')
def career_dashboard():
    """Render career dashboard page"""
    return render_template('career_dashboard.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """Process resume and redirect to career dashboard"""
    try:
        # Check if file was uploaded
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        job_role = request.form.get('job_role')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not job_role:
            return jsonify({'error': 'No job role selected'}), 400
        
        if file and allowed_file(file.filename):
            # Save uploaded file
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Extract text from resume
            raw_text = ResumeParser.extract_text(file_path)
            print(f"DEBUG ANALYZE: Raw text length: {len(raw_text) if raw_text else 0}")
            print(f"DEBUG ANALYZE: Raw text first 200 chars: {raw_text[:200] if raw_text else 'NONE'}")
            
            if not raw_text:
                os.remove(file_path)
                return jsonify({'error': 'Failed to extract text from resume'}), 400
            
            # Clean text
            cleaned_text = ResumeParser.clean_text(raw_text)
            print(f"DEBUG ANALYZE: Cleaned text length: {len(cleaned_text)}")
            print(f"DEBUG ANALYZE: Cleaned text first 200 chars: {cleaned_text[:200]}")
            
            # Clean up uploaded file
            os.remove(file_path)
            
            # Store in session for dashboard
            session['resume_text'] = cleaned_text
            print(f"DEBUG ANALYZE: Stored in session, length: {len(session.get('resume_text', ''))}")
            session['target_role'] = job_role
            session['filename'] = filename
            
            # Set target role in database
            user_session = get_or_create_session()
            user_session.target_role = job_role
            db.session.commit()
            
            # Redirect to career dashboard
            return redirect(url_for('career_dashboard'))
        
        else:
            return jsonify({'error': 'Invalid file format. Only PDF and DOCX allowed'}), 400
    
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/api/roles', methods=['GET'])
def get_roles():
    """API endpoint to get all job roles"""
    roles = skill_matcher.get_available_roles()
    return jsonify({'roles': roles})

@app.route('/api/role/<role_name>', methods=['GET'])
def get_role_details(role_name):
    """API endpoint to get details for a specific role"""
    details = skill_matcher.get_role_details(role_name)
    if details:
        return jsonify(details)
    else:
        return jsonify({'error': 'Role not found'}), 404

@app.route('/compare-all', methods=['POST'])
def compare_all_roles():
    """Compare resume against all available job roles"""
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Save and process file
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Extract and process
            raw_text = ResumeParser.extract_text(file_path)
            cleaned_text = ResumeParser.clean_text(raw_text)
            extracted_skills = skill_extractor.extract_skills(cleaned_text)
            
            # Compare against all roles
            all_matches = skill_matcher.compare_multiple_roles(extracted_skills)
            
            # Clean up
            os.remove(file_path)
            
            return jsonify({
                'extracted_skills': extracted_skills,
                'role_matches': all_matches
            })
        
        else:
            return jsonify({'error': 'Invalid file format'}), 400
    
    except Exception as e:
        return jsonify({'error': f'Comparison failed: {str(e)}'}), 500

@app.route('/demo')
def demo():
    """Demo page to test with Kaggle dataset resumes"""
    if dataset_processor is None:
        return jsonify({'error': 'Kaggle datasets not loaded'}), 500
    
    job_roles = skill_matcher.get_available_roles()
    
    # Get sample positions from Kaggle dataset
    kaggle_positions = dataset_processor.get_all_job_positions()[:10]
    
    return render_template('demo.html', 
                         job_roles=job_roles,
                         kaggle_positions=kaggle_positions,
                         total_resumes=len(dataset_processor.resume_df))

@app.route('/analyze-kaggle', methods=['POST'])
def analyze_kaggle():
    """Analyze a random resume from Kaggle dataset"""
    try:
        if dataset_processor is None:
            return jsonify({'error': 'Kaggle datasets not loaded'}), 500
        
        job_role = request.form.get('job_role')
        position_filter = request.form.get('position_filter', None)
        
        if not job_role:
            return jsonify({'error': 'No job role selected'}), 400
        
        # Get resume from dataset
        if position_filter and position_filter != 'random':
            sample_resume = dataset_processor.get_resume_by_position(position_filter, 1)
            if len(sample_resume) == 0:
                sample_resume = dataset_processor.get_random_resume(1)
        else:
            sample_resume = dataset_processor.get_random_resume(1)
        
        resume_row = sample_resume.iloc[0]
        
        # Extract skills from Kaggle resume
        extracted_skills = dataset_processor.extract_resume_skills(resume_row)
        
        # Create resume text for display
        resume_text = dataset_processor.create_resume_text(resume_row)
        
        # Categorize skills
        categorized_skills = skill_extractor.categorize_skills(extracted_skills)
        
        # Match against job role
        match_results = skill_matcher.match_skills(extracted_skills, job_role)
        
        # Generate recommendations
        recommendations = skill_recommender.generate_recommendations(match_results)
        
        # Prepare response
        analysis_results = {
            'resume_text': resume_text,
            'extracted_skills': extracted_skills,
            'categorized_skills': categorized_skills,
            'match_results': match_results,
            'recommendations': recommendations,
            'source': 'Kaggle Dataset',
            'dataset_position': resume_row.get('positions', 'N/A')
        }
        
        return render_template('results.html', results=analysis_results, is_demo=True)
    
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/kaggle-stats', methods=['GET'])
def kaggle_stats():
    """Get statistics about Kaggle dataset"""
    if dataset_processor is None:
        return jsonify({'error': 'Kaggle datasets not loaded'}), 500
    
    stats = dataset_processor.get_dataset_statistics()
    return jsonify(stats)

@app.route('/api/kaggle-positions', methods=['GET'])
def kaggle_positions():
    """Get all job positions from Kaggle dataset"""
    if dataset_processor is None:
        return jsonify({'error': 'Kaggle datasets not loaded'}), 500
    
    positions = dataset_processor.get_all_job_positions()
    return jsonify({'positions': positions, 'total': len(positions)})

@app.route('/history')
def history():
    """View analysis history from database"""
    try:
        # Get all resume records, ordered by most recent
        resumes = Resume.query.order_by(Resume.created_at.desc()).limit(50).all()
        return render_template('history.html', resumes=resumes)
    except Exception as e:
        return jsonify({'error': f'Failed to load history: {str(e)}'}), 500

@app.route('/api/history', methods=['GET'])
def api_history():
    """API endpoint to get analysis history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        resumes = Resume.query.order_by(Resume.created_at.desc()).limit(limit).all()
        return jsonify({
            'total': Resume.query.count(),
            'resumes': [resume.to_dict() for resume in resumes]
        })
    except Exception as e:
        return jsonify({'error': f'Failed to load history: {str(e)}'}), 500

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """API endpoint to get statistics"""
    try:
        total_analyses = Resume.query.count()
        avg_match_score = db.session.query(db.func.avg(Resume.match_score)).scalar() or 0
        
        # Most analyzed job roles
        role_stats = db.session.query(
            Resume.job_role,
            db.func.count(Resume.id).label('count')
        ).group_by(Resume.job_role).order_by(db.text('count DESC')).limit(5).all()
        
        return jsonify({
            'total_analyses': total_analyses,
            'average_match_score': round(avg_match_score, 2),
            'top_job_roles': [{'role': role, 'count': count} for role, count in role_stats]
        })
    except Exception as e:
        return jsonify({'error': f'Failed to load stats: {str(e)}'}), 500

# ============================================================================
# PHASE 2 MVP ROUTES - Career Readiness Platform
# ============================================================================

from modules.readiness_calculator import ReadinessCalculator
from models import UserSession, ReadinessSnapshot, UserProject
from datetime import datetime, date
import uuid

# Initialize readiness calculator
readiness_calculator = ReadinessCalculator()

def get_or_create_session():
    """Get or create user session"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    session_id = session['session_id']
    
    # Get or create UserSession in database
    user_session = UserSession.query.filter_by(session_id=session_id).first()
    if not user_session:
        user_session = UserSession(session_id=session_id)
        db.session.add(user_session)
        db.session.commit()
    else:
        # Update last_active
        user_session.last_active = datetime.utcnow()
        db.session.commit()
    
    return user_session


@app.route('/set-target-role', methods=['POST'])
def set_target_role():
    """
    Set target role for user session
    
    Request Body:
    {
        "target_role": "Backend Developer",
        "email": "user@example.com"  // optional
    }
    
    Response:
    {
        "success": true,
        "session_id": "abc-123",
        "target_role": "Backend Developer"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'target_role' not in data:
            return jsonify({'error': 'target_role is required'}), 400
        
        target_role = data['target_role']
        email = data.get('email')
        
        # Validate target role exists
        available_roles = skill_matcher.get_available_roles()
        if target_role not in available_roles:
            return jsonify({'error': f'Invalid target_role. Must be one of: {", ".join(available_roles)}'}), 400
        
        # Get or create session
        user_session = get_or_create_session()
        
        # Update target role
        user_session.target_role = target_role
        if email:
            user_session.email = email
        db.session.commit()
        
        return jsonify({
            'success': True,
            'session_id': user_session.session_id,
            'target_role': user_session.target_role
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to set target role: {str(e)}'}), 500


@app.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Get career readiness dashboard data
    
    Handles both first-time users (with resume_text in session) 
    and returning users (loads from cache)
    """
    try:
        # Get or create session
        user_session = get_or_create_session()
        
        # DEBUG: Print session data
        print(f"DEBUG: Session ID: {user_session.session_id}")
        print(f"DEBUG: Session keys: {list(session.keys())}")
        print(f"DEBUG: Target role in session: {session.get('target_role')}")
        print(f"DEBUG: Target role in DB: {user_session.target_role}")
        print(f"DEBUG: Resume text exists: {bool(session.get('resume_text'))}")
        print(f"DEBUG: Resume text length: {len(session.get('resume_text', ''))}")
        print(f"DEBUG: Resume text type: {type(session.get('resume_text'))}")
        print(f"DEBUG: Resume text first 100 chars: {str(session.get('resume_text', ''))[:100]}")
        
        # Get target role from session or database
        target_role = session.get('target_role') or user_session.target_role
        
        if not target_role:
            print("DEBUG: No target role found!")
            return jsonify({
                'error': 'No target role set. Please upload a resume first.',
                'redirect': '/'
            }), 400
        
        # Get resume text from session
        resume_text = session.get('resume_text')
        
        # If no resume text, try to get from latest snapshot
        if not resume_text:
            latest_snapshot = ReadinessSnapshot.query.filter_by(
                session_id=user_session.session_id
            ).order_by(ReadinessSnapshot.created_at.desc()).first()
            
            if latest_snapshot and latest_snapshot.snapshot_data:
                # Get enriched skills and match results from cached snapshot
                enriched_skills = latest_snapshot.snapshot_data.get('enriched_skills', [])
                match_results = latest_snapshot.snapshot_data.get('match_results', {})
                
                if not enriched_skills or not match_results:
                    return jsonify({
                        'error': 'No resume data found. Please upload a resume first.',
                        'redirect': '/'
                    }), 400
                
                # ALWAYS recalculate with current projects (don't use cached evidence score)
                projects = UserProject.query.filter_by(session_id=user_session.session_id).all()
                projects_list = [p.to_dict() for p in projects]
                
                # Recalculate readiness with current projects
                readiness_data = readiness_calculator.calculate_readiness(
                    enriched_skills,
                    match_results,
                    projects_list
                )
                
                # Save new snapshot with updated scores
                new_snapshot = ReadinessSnapshot(
                    session_id=user_session.session_id,
                    target_role=target_role,
                    overall_score=readiness_data['overall_score'],
                    skill_match_score=readiness_data['skill_match_score'],
                    experience_score=readiness_data['experience_score'],
                    evidence_score=readiness_data['evidence_score'],
                    snapshot_data={
                        'breakdown': readiness_data['breakdown'],
                        'gap_analysis': readiness_data['gap_analysis'],
                        'recommendations': readiness_data['recommendations'],
                        'enriched_skills': enriched_skills,
                        'match_results': match_results
                    }
                )
                db.session.add(new_snapshot)
                db.session.commit()
                
                # Return recalculated data
                return jsonify({
                    'readiness': {
                        'overall_score': readiness_data['overall_score'],
                        'skill_match_score': readiness_data['skill_match_score'],
                        'experience_score': readiness_data['experience_score'],
                        'evidence_score': readiness_data['evidence_score'],
                        'breakdown': readiness_data['breakdown']
                    },
                    'gap_analysis': readiness_data['gap_analysis'],
                    'recommendations': readiness_data['recommendations'],
                    'target_role': target_role,
                    'session_id': user_session.session_id,
                    'cached': False
                })
            else:
                return jsonify({
                    'error': 'No resume data found. Please upload a resume first.',
                    'redirect': '/'
                }), 400
        
        # Extract skills with experience
        enriched_skills = skill_extractor.extract_skills_with_experience(resume_text)
        
        # Extract basic skills for matching
        basic_skills = [s['skill'] for s in enriched_skills]
        
        # Match against target role
        match_results = skill_matcher.match_skills(basic_skills, target_role)
        
        # Get user projects
        projects = UserProject.query.filter_by(session_id=user_session.session_id).all()
        projects_list = [p.to_dict() for p in projects]
        
        # Calculate readiness
        readiness_data = readiness_calculator.calculate_readiness(
            enriched_skills,
            match_results,
            projects_list
        )
        
        # Save snapshot
        snapshot = ReadinessSnapshot(
            session_id=user_session.session_id,
            target_role=target_role,
            overall_score=readiness_data['overall_score'],
            skill_match_score=readiness_data['skill_match_score'],
            experience_score=readiness_data['experience_score'],
            evidence_score=readiness_data['evidence_score'],
            snapshot_data={
                'breakdown': readiness_data['breakdown'],
                'gap_analysis': readiness_data['gap_analysis'],
                'recommendations': readiness_data['recommendations'],
                'enriched_skills': enriched_skills,
                'match_results': match_results
            }
        )
        db.session.add(snapshot)
        db.session.commit()
        
        # Clear resume_text from session after first use (keep target_role)
        session.pop('resume_text', None)
        
        return jsonify({
            'readiness': {
                'overall_score': readiness_data['overall_score'],
                'skill_match_score': readiness_data['skill_match_score'],
                'experience_score': readiness_data['experience_score'],
                'evidence_score': readiness_data['evidence_score'],
                'breakdown': readiness_data['breakdown']
            },
            'gap_analysis': readiness_data['gap_analysis'],
            'recommendations': readiness_data['recommendations'],
            'target_role': target_role,
            'session_id': user_session.session_id,
            'cached': False
        })
    
    except Exception as e:
        return jsonify({'error': f'Dashboard failed: {str(e)}'}), 500


@app.route('/api/projects', methods=['GET', 'POST'])
def manage_projects():
    """
    Manage user projects
    
    GET - List all projects for session
    Response:
    {
        "projects": [
            {
                "id": 1,
                "title": "E-commerce API",
                "description": "...",
                "skills_used": ["Python", "Django"],
                "start_date": "2024-01-01",
                "end_date": "2024-03-01",
                "project_url": "https://..."
            }
        ],
        "total": 3
    }
    
    POST - Add new project
    Request Body:
    {
        "title": "E-commerce API",
        "description": "Built REST API with Django",
        "skills_used": ["Python", "Django", "PostgreSQL"],
        "start_date": "2024-01-01",  // optional
        "end_date": "2024-03-01",    // optional
        "project_url": "https://..."  // optional
    }
    
    Response:
    {
        "success": true,
        "project": {...},
        "message": "Project added successfully"
    }
    """
    try:
        # Get or create session
        user_session = get_or_create_session()
        
        if request.method == 'GET':
            # List projects
            projects = UserProject.query.filter_by(session_id=user_session.session_id).all()
            return jsonify({
                'projects': [p.to_dict() for p in projects],
                'total': len(projects)
            })
        
        elif request.method == 'POST':
            # Add new project
            data = request.get_json()
            
            if not data or 'title' not in data:
                return jsonify({'error': 'title is required'}), 400
            
            # Parse dates
            start_date = None
            end_date = None
            
            if data.get('start_date'):
                try:
                    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': 'start_date must be in YYYY-MM-DD format'}), 400
            
            if data.get('end_date'):
                try:
                    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': 'end_date must be in YYYY-MM-DD format'}), 400
            
            # Create project
            project = UserProject(
                session_id=user_session.session_id,
                title=data['title'],
                description=data.get('description'),
                skills_used=data.get('skills_used', []),
                start_date=start_date,
                end_date=end_date,
                project_url=data.get('project_url')
            )
            
            db.session.add(project)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'project': project.to_dict(),
                'message': 'Project added successfully'
            }), 201
    
    except Exception as e:
        return jsonify({'error': f'Project management failed: {str(e)}'}), 500


@app.route('/api/progress', methods=['GET'])
def get_progress():
    """
    Get progress timeline (historical readiness scores)
    
    Response:
    {
        "timeline": [
            {
                "date": "2024-01-15T10:30:00",
                "overall_score": 45.0,
                "skill_match_score": 60.0,
                "experience_score": 40.0,
                "evidence_score": 0.0
            },
            {
                "date": "2024-02-20T14:20:00",
                "overall_score": 52.0,
                "skill_match_score": 60.0,
                "experience_score": 40.0,
                "evidence_score": 25.0
            }
        ],
        "total_snapshots": 5,
        "improvement": 25.0,
        "target_role": "Backend Developer"
    }
    """
    try:
        # Get or create session
        user_session = get_or_create_session()
        
        # Get all snapshots for this session
        snapshots = ReadinessSnapshot.query.filter_by(
            session_id=user_session.session_id
        ).order_by(ReadinessSnapshot.created_at.asc()).all()
        
        if not snapshots:
            return jsonify({
                'timeline': [],
                'total_snapshots': 0,
                'improvement': 0,
                'target_role': user_session.target_role
            })
        
        # Build timeline
        timeline = []
        for snapshot in snapshots:
            timeline.append({
                'date': snapshot.created_at.isoformat(),
                'overall_score': snapshot.overall_score,
                'skill_match_score': snapshot.skill_match_score,
                'experience_score': snapshot.experience_score,
                'evidence_score': snapshot.evidence_score
            })
        
        # Calculate improvement
        first_score = snapshots[0].overall_score
        latest_score = snapshots[-1].overall_score
        improvement = latest_score - first_score
        
        return jsonify({
            'timeline': timeline,
            'total_snapshots': len(snapshots),
            'improvement': round(improvement, 2),
            'target_role': user_session.target_role or 'Not set'
        })
    
    except Exception as e:
        return jsonify({'error': f'Progress retrieval failed: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
