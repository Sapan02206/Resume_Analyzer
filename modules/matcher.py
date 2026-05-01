import json
from typing import Dict, List, Tuple

class SkillMatcher:
    """Match resume skills against job requirements and calculate scores"""
    
    def __init__(self, job_roles_data_path: str, required_weight: float = 1.0, optional_weight: float = 0.5):
        """
        Initialize skill matcher
        
        Args:
            job_roles_data_path: Path to job_roles.json file
            required_weight: Weight for required skills in scoring
            optional_weight: Weight for optional skills in scoring
        """
        with open(job_roles_data_path, 'r') as f:
            self.job_roles = json.load(f)
        
        self.required_weight = required_weight
        self.optional_weight = optional_weight
    
    def get_available_roles(self) -> List[str]:
        """Get list of available job roles"""
        return list(self.job_roles.keys())
    
    def get_role_details(self, role_name: str) -> Dict:
        """Get details for a specific job role"""
        return self.job_roles.get(role_name, {})
    
    def match_skills(self, resume_skills: List[str], role_name: str) -> Dict:
        """
        Match resume skills against job role requirements
        
        Args:
            resume_skills: List of skills extracted from resume
            role_name: Target job role name
            
        Returns:
            Dictionary containing match results
        """
        if role_name not in self.job_roles:
            raise ValueError(f"Job role '{role_name}' not found")
        
        role_data = self.job_roles[role_name]
        required_skills = set([s.lower() for s in role_data['required_skills']])
        optional_skills = set([s.lower() for s in role_data['optional_skills']])
        resume_skills_lower = set([s.lower() for s in resume_skills])
        
        # Find matched and missing skills
        matched_required = required_skills.intersection(resume_skills_lower)
        missing_required = required_skills - resume_skills_lower
        matched_optional = optional_skills.intersection(resume_skills_lower)
        missing_optional = optional_skills - resume_skills_lower
        
        # Calculate match score
        score = self._calculate_score(
            len(matched_required),
            len(required_skills),
            len(matched_optional),
            len(optional_skills)
        )
        
        # Prepare results
        results = {
            'role_name': role_name,
            'role_description': role_data['description'],
            'experience_level': role_data['experience_level'],
            'match_score': round(score, 2),
            'matched_required': sorted(list(matched_required)),
            'missing_required': sorted(list(missing_required)),
            'matched_optional': sorted(list(matched_optional)),
            'missing_optional': sorted(list(missing_optional)),
            'total_resume_skills': len(resume_skills),
            'total_required_skills': len(required_skills),
            'total_optional_skills': len(optional_skills)
        }
        
        return results
    
    def _calculate_score(self, matched_req: int, total_req: int, 
                        matched_opt: int, total_opt: int) -> float:
        """
        Calculate weighted match score
        
        Args:
            matched_req: Number of matched required skills
            total_req: Total required skills
            matched_opt: Number of matched optional skills
            total_opt: Total optional skills
            
        Returns:
            Match score as percentage (0-100)
        """
        if total_req == 0 and total_opt == 0:
            return 0.0
        
        # Calculate weighted scores
        required_score = (matched_req / total_req) * self.required_weight if total_req > 0 else 0
        optional_score = (matched_opt / total_opt) * self.optional_weight if total_opt > 0 else 0
        
        # Normalize to 0-100 scale
        total_weight = self.required_weight + self.optional_weight
        final_score = ((required_score + optional_score) / total_weight) * 100
        
        return final_score
    
    def compare_multiple_roles(self, resume_skills: List[str]) -> List[Dict]:
        """
        Compare resume against all available job roles
        
        Args:
            resume_skills: List of skills extracted from resume
            
        Returns:
            List of match results sorted by score (descending)
        """
        results = []
        
        for role_name in self.job_roles.keys():
            match_result = self.match_skills(resume_skills, role_name)
            results.append(match_result)
        
        # Sort by match score (descending)
        results.sort(key=lambda x: x['match_score'], reverse=True)
        
        return results
