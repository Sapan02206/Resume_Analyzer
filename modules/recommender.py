from typing import Dict, List

class SkillRecommender:
    """Generate recommendations based on skill gap analysis"""
    
    # Learning resource suggestions
    LEARNING_RESOURCES = {
        'programming_languages': {
            'platforms': ['Codecademy', 'freeCodeCamp', 'LeetCode', 'HackerRank'],
            'action': 'Practice coding challenges and build projects'
        },
        'web_technologies': {
            'platforms': ['MDN Web Docs', 'Frontend Mentor', 'Scrimba', 'The Odin Project'],
            'action': 'Build responsive websites and web applications'
        },
        'databases': {
            'platforms': ['SQLZoo', 'MongoDB University', 'PostgreSQL Tutorial'],
            'action': 'Practice database design and query optimization'
        },
        'cloud_devops': {
            'platforms': ['AWS Training', 'Azure Learn', 'Docker Documentation', 'Kubernetes.io'],
            'action': 'Get cloud certifications and practice with free tiers'
        },
        'data_science': {
            'platforms': ['Kaggle', 'Coursera', 'DataCamp', 'Fast.ai'],
            'action': 'Work on real datasets and participate in competitions'
        },
        'mobile_development': {
            'platforms': ['React Native Docs', 'Flutter.dev', 'iOS Developer', 'Android Developer'],
            'action': 'Build and publish mobile apps to app stores'
        }
    }
    
    # Skill to category mapping
    SKILL_CATEGORIES = {
        'Python': 'programming_languages',
        'JavaScript': 'programming_languages',
        'Java': 'programming_languages',
        'React': 'web_technologies',
        'Node.js': 'web_technologies',
        'HTML': 'web_technologies',
        'CSS': 'web_technologies',
        'MongoDB': 'databases',
        'PostgreSQL': 'databases',
        'MySQL': 'databases',
        'AWS': 'cloud_devops',
        'Docker': 'cloud_devops',
        'Kubernetes': 'cloud_devops',
        'Machine Learning': 'data_science',
        'TensorFlow': 'data_science',
        'React Native': 'mobile_development',
        'Flutter': 'mobile_development'
    }
    
    def generate_recommendations(self, match_results: Dict) -> Dict:
        """
        Generate actionable recommendations based on skill gaps
        
        Args:
            match_results: Results from skill matching
            
        Returns:
            Dictionary containing recommendations
        """
        missing_required = match_results['missing_required']
        missing_optional = match_results['missing_optional']
        match_score = match_results['match_score']
        
        recommendations = {
            'priority': self._prioritize_skills(missing_required, missing_optional),
            'learning_paths': self._suggest_learning_paths(missing_required),
            'project_ideas': self._suggest_projects(match_results['role_name'], missing_required),
            'quick_wins': self._identify_quick_wins(missing_optional),
            'overall_advice': self._generate_overall_advice(match_score, missing_required),
            'estimated_timeline': self._estimate_timeline(missing_required, missing_optional)
        }
        
        return recommendations
    
    def _prioritize_skills(self, missing_required: List[str], missing_optional: List[str]) -> Dict:
        """Prioritize which skills to learn first"""
        return {
            'critical': missing_required[:3] if len(missing_required) > 0 else [],
            'important': missing_required[3:] if len(missing_required) > 3 else [],
            'nice_to_have': missing_optional[:5] if len(missing_optional) > 0 else []
        }
    
    def _suggest_learning_paths(self, missing_skills: List[str]) -> List[Dict]:
        """Suggest learning resources for missing skills"""
        learning_paths = []
        
        for skill in missing_skills[:5]:  # Focus on top 5 missing skills
            skill_title = skill.title()
            category = self.SKILL_CATEGORIES.get(skill_title, 'programming_languages')
            resources = self.LEARNING_RESOURCES.get(category, {})
            
            learning_paths.append({
                'skill': skill_title,
                'platforms': resources.get('platforms', ['Online tutorials', 'Official documentation']),
                'action': resources.get('action', 'Practice and build projects'),
                'estimated_time': self._estimate_learning_time(skill_title)
            })
        
        return learning_paths
    
    def _suggest_projects(self, role_name: str, missing_skills: List[str]) -> List[str]:
        """Suggest project ideas based on role and missing skills"""
        project_templates = {
            'Frontend Developer': [
                'Build a responsive portfolio website',
                'Create a weather app using a public API',
                'Develop a task management application',
                'Build an e-commerce product page'
            ],
            'Backend Developer': [
                'Create a RESTful API for a blog platform',
                'Build a user authentication system',
                'Develop a file upload service',
                'Create a real-time chat application'
            ],
            'Full Stack Developer': [
                'Build a full-stack social media clone',
                'Create an online marketplace',
                'Develop a project management tool',
                'Build a real-time collaboration platform'
            ],
            'Data Scientist': [
                'Analyze a public dataset and create visualizations',
                'Build a predictive model for house prices',
                'Create a sentiment analysis tool',
                'Develop a recommendation system'
            ],
            'DevOps Engineer': [
                'Set up a CI/CD pipeline for a sample project',
                'Containerize an application with Docker',
                'Deploy a multi-tier application on cloud',
                'Create infrastructure as code with Terraform'
            ],
            'Mobile Developer': [
                'Build a cross-platform mobile app',
                'Create a fitness tracking application',
                'Develop a recipe finder app',
                'Build a social networking mobile app'
            ]
        }
        
        return project_templates.get(role_name, [
            'Build a project showcasing your skills',
            'Contribute to open-source projects',
            'Create a portfolio of diverse applications'
        ])
    
    def _identify_quick_wins(self, missing_optional: List[str]) -> List[Dict]:
        """Identify skills that can be learned quickly"""
        quick_skills = ['Git', 'HTML', 'CSS', 'Bootstrap', 'jQuery', 'Postman']
        
        quick_wins = []
        for skill in missing_optional:
            if any(quick in skill.lower() for quick in [s.lower() for s in quick_skills]):
                quick_wins.append({
                    'skill': skill.title(),
                    'reason': 'Can be learned in 1-2 weeks',
                    'impact': 'Immediate resume boost'
                })
        
        return quick_wins[:3]
    
    def _generate_overall_advice(self, match_score: float, missing_required: List[str]) -> str:
        """Generate overall career advice"""
        if match_score >= 80:
            return "Excellent match! You're well-qualified for this role. Focus on the few missing skills and start applying."
        elif match_score >= 60:
            return "Good foundation! You have most required skills. Dedicate 2-3 months to learning the missing critical skills."
        elif match_score >= 40:
            return "Moderate match. You'll need to invest significant time (3-6 months) building the required skills before applying."
        else:
            return "Consider starting with entry-level positions or internships while building the required skills. Estimated timeline: 6-12 months."
    
    def _estimate_timeline(self, missing_required: List[str], missing_optional: List[str]) -> str:
        """Estimate time needed to fill skill gaps"""
        total_skills = len(missing_required) + len(missing_optional)
        
        if total_skills == 0:
            return "You're ready to apply now!"
        elif total_skills <= 3:
            return "1-2 months of focused learning"
        elif total_skills <= 6:
            return "3-4 months of consistent practice"
        elif total_skills <= 10:
            return "5-6 months of dedicated study"
        else:
            return "6-12 months of comprehensive learning"
    
    def _estimate_learning_time(self, skill: str) -> str:
        """Estimate time to learn a specific skill"""
        quick_skills = ['Git', 'HTML', 'CSS', 'Bootstrap']
        medium_skills = ['JavaScript', 'Python', 'SQL', 'React']
        
        if any(quick in skill for quick in quick_skills):
            return "1-2 weeks"
        elif any(medium in skill for medium in medium_skills):
            return "1-2 months"
        else:
            return "2-3 months"
