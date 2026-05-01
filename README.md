# AI Resume Analyzer - Career Readiness Platform

**Version:** 2.0.0 (Phase 2 MVP)  
**Status:** ✅ Production Ready

A Flask-based career development platform that analyzes resumes, tracks progress, and provides evidence-based career readiness scoring with actionable guidance.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python create_database.py
python migrate_phase2_mvp.py
```

### 3. Run the Application
```bash
python app.py
```

### 4. Open Browser
```
http://localhost:5000
```

---

## ✨ Features

### **Phase 1 Features (Original)**
- 📄 **Resume Upload** - Support for PDF and DOCX files
- 🔍 **Skill Extraction** - Automatically detect 119+ skills from resumes
- 🎯 **Job Matching** - Compare resume skills against 7 job roles
- 📊 **Gap Analysis** - Identify missing required and optional skills
- 💡 **Recommendations** - Get personalized learning suggestions
- 🎮 **Demo Mode** - Test with Kaggle dataset (9,544 resumes)
- 🧠 **ML Models** - 3 trained models for classification and scoring

### **Phase 2 Features (NEW - MVP)**
- 🎯 **Career Readiness Dashboard** - Overall score (0-100) with 3-factor breakdown
- 📈 **Progress Tracking** - Historical snapshots showing improvement over time
- 🏆 **Evidence-Based Scoring** - Projects and URLs validate your skills
- 🔄 **Dynamic Updates** - Scores recalculate automatically when you add projects
- 💼 **Project Management** - Track your work with skills, dates, and URLs
- 🎨 **User-Friendly UI** - Clean, career-focused design with smooth interactions
- 🔐 **Session Management** - Persistent sessions with UUID-based tracking

---

## 📊 Scoring System

### **Readiness Formula**
```
Overall Score = (Skill Match × 50%) + (Experience × 30%) + (Evidence × 20%)
```

### **Status Levels**
| Score | Badge | Meaning |
|-------|-------|---------|
| 80-100 | 🎉 Ready to Apply! | Start applying with confidence |
| 60-79 | 👍 Almost There | Focus on recommendations |
| 40-59 | 📚 Keep Learning | Build more skills |
| 0-39 | 🚀 Getting Started | Follow the roadmap |

### **Evidence Scoring**
- **0 projects:** 0 points
- **1 project:** 25 points (+10 with URL)
- **2 projects:** 50 points (+20 with URLs)
- **3+ projects:** 75-100 points (+20 bonus cap)

---

## 🎯 Available Pages

### **Main Application**
- **Homepage**: `http://localhost:5000` - Upload and analyze resumes
- **Career Dashboard**: `http://localhost:5000/career-dashboard` - View readiness score and progress
- **Demo Mode**: `http://localhost:5000/demo` - Test with Kaggle dataset
- **History**: `http://localhost:5000/history` - View past analyses

### **API Endpoints**
- `POST /set-target-role` - Set your target job role
- `GET /dashboard` - Get readiness data
- `POST /api/projects` - Add a project
- `GET /api/projects` - List your projects
- `GET /api/progress` - Get progress timeline

📖 **Full API Documentation:** See `API_DOCUMENTATION_MVP.md`

---

## 📁 Project Structure

```
Resume_Analyzer/
├── app.py                          # Main Flask application
├── config.py                       # Configuration
├── models.py                       # Database models (7 tables)
├── requirements.txt                # Dependencies
├── requirements-dev.txt            # Dev dependencies
│
├── modules/
│   ├── parser.py                   # Resume parsing
│   ├── skill_extractor.py          # Skill extraction (v2.1.0)
│   ├── experience_extractor.py     # Experience detection (v1.1.0)
│   ├── matcher.py                  # Job matching
│   ├── recommender.py              # Recommendations
│   ├── readiness_calculator.py     # Readiness scoring (NEW)
│   └── dataset_processor.py        # Kaggle data
│
├── templates/
│   ├── index.html                  # Homepage
│   ├── career_dashboard.html       # Dashboard (NEW)
│   ├── demo.html                   # Demo mode
│   ├── results.html                # Results page
│   └── history.html                # History page
│
├── static/
│   ├── css/style.css               # Styles
│   └── js/
│       ├── main.js                 # Homepage JS
│       └── dashboard.js            # Dashboard JS (NEW)
│
├── ml_models/                      # Machine learning models
├── tests/                          # Test suite (65 tests)
├── data/                           # Skills and job roles data
└── uploads/                        # Temporary file storage
```

---

## 🎓 Usage

### **First-Time User Flow**
1. Visit homepage
2. Upload your resume (PDF or DOCX)
3. Select target job role
4. Click "Analyze Resume"
5. **Automatically redirected to dashboard**
6. View your readiness score and gaps
7. Add projects to boost your evidence score
8. Track your progress over time

### **Returning User Flow**
1. Visit `/career-dashboard`
2. Dashboard loads from cache
3. Add more projects
4. Watch your score improve

---

## 🛠️ Technologies

### **Backend**
- Flask 2.3+
- PostgreSQL 12+
- SQLAlchemy
- Python 3.8+

### **NLP & ML**
- spaCy (optional)
- NLTK
- scikit-learn
- 3 trained ML models

### **File Processing**
- PyPDF2 (PDF parsing)
- python-docx (DOCX parsing)

### **Frontend**
- Bootstrap 5
- JavaScript (ES6+)
- Bootstrap Icons

### **Data**
- Kaggle Resume Dataset (9,544 resumes)
- 119+ skills database
- 7 job role definitions

---

## 💼 Job Roles Available

1. Frontend Developer
2. Backend Developer
3. Full Stack Developer
4. Data Scientist
5. DevOps Engineer
6. Mobile Developer
7. UI/UX Designer

---

## 🧪 Testing

### **Automated Tests**
```bash
# Run complete integration test
python test_complete_flow.py

# Run unit tests
pytest tests/
```

### **Manual Testing**
See `MANUAL_TESTING_GUIDE.md` for detailed testing scenarios

### **Test Coverage**
- 65 unit tests (100% passing)
- 13 integration test scenarios
- End-to-end flow testing

---

## 📚 Documentation

### **Quick References**
- `PHASE2_QUICK_START.md` - Quick reference guide
- `MANUAL_TESTING_GUIDE.md` - Manual testing scenarios
- `API_DOCUMENTATION_MVP.md` - API reference with examples

### **Detailed Documentation**
- `PHASE2_MVP_COMPLETE.md` - Complete project summary
- `PHASE2_CAREER_PLATFORM_DESIGN.md` - Full design (7 modules)
- `INTEGRATION_TEST_GUIDE.md` - Testing procedures
- `TESTING_POLISH_CHECKLIST.md` - QA checklist

### **Progress Tracking**
- `PHASE1_VS_PHASE2_COMPARISON.md` - Transformation overview
- `PHASE2_MVP_PROGRESS.md` - Development progress

---

## 🔧 Configuration

### **Environment Variables**
Create a `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost/resume_analyzer
SECRET_KEY=your-secret-key-here
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
```

### **Database Setup**
```bash
# Create database
createdb resume_analyzer

# Initialize tables
python create_database.py

# Run Phase 2 migrations
python migrate_phase2_mvp.py
```

---

## 🚀 Deployment

### **Requirements**
- Python 3.8+
- PostgreSQL 12+
- 512MB RAM minimum
- 1GB disk space

### **Production Setup**
1. Set environment variables
2. Initialize database
3. Run migrations
4. Configure reverse proxy (nginx/Apache)
5. Use production WSGI server (gunicorn/uWSGI)

---

## 📈 Metrics & Performance

- **API Response Time:** < 200ms
- **Page Load Time:** < 1 second
- **Database Queries:** Optimized with indexes
- **Test Pass Rate:** 100%
- **Code Quality:** Clean, documented, tested

---

## 🎉 What's New in Phase 2

### **Transformation**
From **one-time analysis tool** → **continuous career development platform**

### **Key Improvements**
1. ✅ Career readiness scoring (0-100)
2. ✅ Evidence-based validation (projects)
3. ✅ Progress tracking over time
4. ✅ Dynamic score updates
5. ✅ Session management
6. ✅ User-friendly dashboard
7. ✅ Actionable recommendations

### **Technical Improvements**
- 3 new database tables
- 5 new API endpoints
- Smart caching with invalidation
- Real-time recalculation
- Toast notifications
- Loading overlays
- Smooth animations

---

## 🔮 Future Enhancements (Phase 2.1+)

Potential features for future releases:
- User authentication
- GitHub API integration
- Skill validation tests
- Certification verification
- AI-powered roadmap generation
- Job board integration
- Resume builder
- Interview preparation

---

## 🐛 Troubleshooting

### **Common Issues**

**Issue:** Dashboard shows "No resume data found"  
**Solution:** Upload a resume first from homepage

**Issue:** Score doesn't update after adding project  
**Solution:** Check browser console for errors. Refresh page.

**Issue:** Demo mode shows "Kaggle datasets not loaded"  
**Solution:** Ensure `data/archive/resume_data.csv` exists

**Issue:** Database connection error  
**Solution:** Check PostgreSQL is running and DATABASE_URL is correct

---

## 📞 Support

- **Documentation:** See `/docs` folder
- **Issues:** Check `TESTING_POLISH_CHECKLIST.md`
- **API Reference:** See `API_DOCUMENTATION_MVP.md`
- **Testing Guide:** See `MANUAL_TESTING_GUIDE.md`

---

## 📄 License

MIT License

---

## 🏆 Achievements

### **Phase 1 (Original)**
- ✅ Resume parsing (PDF/DOCX)
- ✅ Skill extraction (119 skills)
- ✅ Job matching (7 roles)
- ✅ Experience detection (14+ patterns)
- ✅ ML models (3 trained models)
- ✅ Kaggle integration (9,544 resumes)

### **Phase 2 (NEW)**
- ✅ Career readiness scoring
- ✅ Evidence-based validation
- ✅ Progress tracking
- ✅ Dynamic updates
- ✅ Session management
- ✅ User-friendly dashboard
- ✅ Actionable recommendations

---

**Built with:** Flask, PostgreSQL, Bootstrap, JavaScript  
**Powered by:** AI, NLP, Machine Learning  
**Designed for:** Career Development & Job Readiness

**Version:** 2.0.0 (MVP)  
**Status:** ✅ PRODUCTION READY  
**Last Updated:** May 1, 2026
