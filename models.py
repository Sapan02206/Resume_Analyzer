"""
Database models for Resume Analyzer
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Resume(db.Model):
    """Resume analysis records"""
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    job_role = db.Column(db.String(100), nullable=False)
    match_score = db.Column(db.Float)
    extracted_skills = db.Column(db.JSON)
    matched_skills = db.Column(db.JSON)
    missing_skills = db.Column(db.JSON)
    recommendations = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Resume {self.filename} - {self.job_role}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'job_role': self.job_role,
            'match_score': self.match_score,
            'extracted_skills': self.extracted_skills,
            'matched_skills': self.matched_skills,
            'missing_skills': self.missing_skills,
            'recommendations': self.recommendations,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class User(db.Model):
    """User accounts (optional for future use)"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.email}>'


class JobRole(db.Model):
    """Job roles stored in database"""
    __tablename__ = 'job_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    required_skills = db.Column(db.JSON)
    optional_skills = db.Column(db.JSON)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<JobRole {self.name}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'required_skills': self.required_skills,
            'optional_skills': self.optional_skills,
            'description': self.description
        }


class Skill(db.Model):
    """Skills database"""
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50))
    synonyms = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Skill {self.name}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'synonyms': self.synonyms
        }


# ============================================================================
# PHASE 2 MVP MODELS - Career Readiness Platform
# ============================================================================

class UserSession(db.Model):
    """User sessions for tracking without full authentication"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255))  # Optional for tracking
    target_role = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    snapshots = db.relationship('ReadinessSnapshot', backref='session', lazy=True, cascade='all, delete-orphan')
    projects = db.relationship('UserProject', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<UserSession {self.session_id}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'email': self.email,
            'target_role': self.target_role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }


class ReadinessSnapshot(db.Model):
    """Readiness score snapshots for progress tracking"""
    __tablename__ = 'readiness_snapshots'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), db.ForeignKey('user_sessions.session_id'), nullable=False, index=True)
    target_role = db.Column(db.String(100), nullable=False)
    overall_score = db.Column(db.Float, nullable=False)
    skill_match_score = db.Column(db.Float, nullable=False)
    experience_score = db.Column(db.Float, nullable=False)
    evidence_score = db.Column(db.Float, nullable=False)
    snapshot_data = db.Column(db.JSON)  # Full breakdown for transparency
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<ReadinessSnapshot {self.session_id} - {self.overall_score}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'target_role': self.target_role,
            'overall_score': round(self.overall_score, 2),
            'skill_match_score': round(self.skill_match_score, 2),
            'experience_score': round(self.experience_score, 2),
            'evidence_score': round(self.evidence_score, 2),
            'snapshot_data': self.snapshot_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserProject(db.Model):
    """User projects for evidence-based scoring"""
    __tablename__ = 'user_projects'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), db.ForeignKey('user_sessions.session_id'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    skills_used = db.Column(db.JSON)  # Array of skill names
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    project_url = db.Column(db.Text)  # Optional GitHub/demo link
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserProject {self.title}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'title': self.title,
            'description': self.description,
            'skills_used': self.skills_used,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'project_url': self.project_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
