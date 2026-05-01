import pandas as pd
import json
import ast
from typing import List, Dict, Tuple
import re

class DatasetProcessor:
    """Process Kaggle resume and job description datasets"""
    
    def __init__(self, resume_csv_path: str = 'data/archive/resume_data.csv'):
        """
        Initialize dataset processor
        
        Args:
            resume_csv_path: Path to resume dataset CSV
        """
        self.resume_csv_path = resume_csv_path
        self.resume_df = None
        self.job_df = None
        
    def load_datasets(self):
        """Load and prepare datasets"""
        print("Loading datasets...")
        self.resume_df = pd.read_csv(self.resume_csv_path)
        print(f"Loaded {len(self.resume_df)} resumes")
        
        # Clean column names (remove BOM character)
        self.resume_df.columns = [col.replace('\ufeff', '') for col in self.resume_df.columns]
        
        # Extract job-related columns for job dataset
        job_columns = ['job_position_name', 'educationaL_requirements', 
                      'experiencere_requirement', 'age_requirement', 
                      'responsibilities.1', 'skills_required']
        
        # Create job dataframe (drop duplicates)
        self.job_df = self.resume_df[job_columns].drop_duplicates().dropna(subset=['job_position_name'])
        print(f"Extracted {len(self.job_df)} unique job positions")
        
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        if pd.isna(text) or text is None:
            return ""
        
        text = str(text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep alphanumeric and common punctuation
        text = re.sub(r'[^\w\s\.\,\-\+\#\/\(\)\[\]]', '', text)
        return text.strip()
    
    def parse_skill_list(self, skill_string: str) -> List[str]:
        """
        Parse skill string (which might be a list representation)
        
        Args:
            skill_string: String representation of skills
            
        Returns:
            List of skills
        """
        if pd.isna(skill_string) or skill_string is None:
            return []
        
        try:
            # Try to parse as Python literal (list)
            skills = ast.literal_eval(skill_string)
            if isinstance(skills, list):
                return [str(s).strip() for s in skills if s]
        except:
            # If parsing fails, split by comma
            skills = str(skill_string).split(',')
            return [s.strip() for s in skills if s.strip()]
        
        return []
    
    def get_random_resume(self, n: int = 1) -> pd.DataFrame:
        """
        Get random resume(s) from dataset
        
        Args:
            n: Number of resumes to retrieve
            
        Returns:
            DataFrame with resume data
        """
        if self.resume_df is None:
            self.load_datasets()
        
        return self.resume_df.sample(n=n)
    
    def get_resume_by_position(self, position: str, n: int = 5) -> pd.DataFrame:
        """
        Get resumes for a specific position
        
        Args:
            position: Job position name
            n: Number of resumes to retrieve
            
        Returns:
            DataFrame with matching resumes
        """
        if self.resume_df is None:
            self.load_datasets()
        
        # Filter by position (case-insensitive)
        mask = self.resume_df['positions'].str.contains(position, case=False, na=False)
        matching = self.resume_df[mask]
        
        if len(matching) == 0:
            return pd.DataFrame()
        
        return matching.sample(n=min(n, len(matching)))
    
    def extract_resume_skills(self, resume_row: pd.Series) -> List[str]:
        """
        Extract skills from a resume row
        
        Args:
            resume_row: Single row from resume DataFrame
            
        Returns:
            List of skills
        """
        skills = []
        
        # Extract from 'skills' column
        if 'skills' in resume_row and not pd.isna(resume_row['skills']):
            skills.extend(self.parse_skill_list(resume_row['skills']))
        
        # Extract from 'related_skils_in_job' column
        if 'related_skils_in_job' in resume_row and not pd.isna(resume_row['related_skils_in_job']):
            job_skills = self.parse_skill_list(resume_row['related_skils_in_job'])
            # Handle nested lists
            for skill in job_skills:
                if isinstance(skill, list):
                    skills.extend(skill)
                else:
                    skills.append(skill)
        
        # Clean and deduplicate
        skills = [self.clean_text(s) for s in skills if s]
        skills = list(set([s for s in skills if len(s) > 1]))
        
        return skills
    
    def get_job_requirements(self, job_position: str) -> Dict:
        """
        Get job requirements for a specific position
        
        Args:
            job_position: Job position name
            
        Returns:
            Dictionary with job requirements
        """
        if self.job_df is None:
            self.load_datasets()
        
        # Find matching job (case-insensitive)
        mask = self.job_df['job_position_name'].str.contains(job_position, case=False, na=False)
        matching_jobs = self.job_df[mask]
        
        if len(matching_jobs) == 0:
            return {}
        
        # Get first match
        job = matching_jobs.iloc[0]
        
        # Extract skills required
        skills_required = self.parse_skill_list(job['skills_required'])
        
        return {
            'position': job['job_position_name'],
            'education': self.clean_text(job['educationaL_requirements']),
            'experience': self.clean_text(job['experiencere_requirement']),
            'age': self.clean_text(job['age_requirement']),
            'responsibilities': self.clean_text(job['responsibilities.1']),
            'skills_required': skills_required
        }
    
    def get_all_job_positions(self) -> List[str]:
        """
        Get list of all unique job positions in dataset
        
        Returns:
            List of job position names
        """
        if self.job_df is None:
            self.load_datasets()
        
        positions = self.job_df['job_position_name'].dropna().unique().tolist()
        return sorted([str(p) for p in positions if p])
    
    def create_resume_text(self, resume_row: pd.Series) -> str:
        """
        Create a text representation of resume (similar to uploaded resume)
        
        Args:
            resume_row: Single row from resume DataFrame
            
        Returns:
            Resume text
        """
        sections = []
        
        # Career Objective
        if 'career_objective' in resume_row and not pd.isna(resume_row['career_objective']):
            sections.append(f"CAREER OBJECTIVE\n{resume_row['career_objective']}")
        
        # Skills
        skills = self.extract_resume_skills(resume_row)
        if skills:
            sections.append(f"SKILLS\n{', '.join(skills)}")
        
        # Education
        if 'educational_institution_name' in resume_row and not pd.isna(resume_row['educational_institution_name']):
            edu_text = f"EDUCATION\n{resume_row['educational_institution_name']}"
            if 'degree_names' in resume_row and not pd.isna(resume_row['degree_names']):
                edu_text += f"\n{resume_row['degree_names']}"
            sections.append(edu_text)
        
        # Experience
        if 'positions' in resume_row and not pd.isna(resume_row['positions']):
            exp_text = f"EXPERIENCE\n{resume_row['positions']}"
            if 'professional_company_names' in resume_row and not pd.isna(resume_row['professional_company_names']):
                exp_text += f"\n{resume_row['professional_company_names']}"
            sections.append(exp_text)
        
        return "\n\n".join(sections)
    
    def export_job_roles_to_json(self, output_path: str = 'data/kaggle_job_roles.json', 
                                  top_n: int = 20):
        """
        Export job roles from dataset to JSON format compatible with the system
        
        Args:
            output_path: Path to save JSON file
            top_n: Number of top job positions to export
        """
        if self.job_df is None:
            self.load_datasets()
        
        # Get top N most common positions
        top_positions = self.job_df['job_position_name'].value_counts().head(top_n).index.tolist()
        
        job_roles = {}
        
        for position in top_positions:
            job_req = self.get_job_requirements(position)
            if job_req and job_req['skills_required']:
                # Split skills into required and optional (first 5 required, rest optional)
                all_skills = job_req['skills_required']
                required_skills = all_skills[:min(5, len(all_skills))]
                optional_skills = all_skills[5:] if len(all_skills) > 5 else []
                
                job_roles[position] = {
                    'description': job_req['responsibilities'][:200] if job_req['responsibilities'] else f"Professional {position}",
                    'required_skills': required_skills,
                    'optional_skills': optional_skills,
                    'experience_level': job_req['experience'] if job_req['experience'] else 'Entry to Mid-level',
                    'education': job_req['education']
                }
        
        # Save to JSON
        with open(output_path, 'w') as f:
            json.dump(job_roles, f, indent=2)
        
        print(f"Exported {len(job_roles)} job roles to {output_path}")
        return job_roles
    
    def get_dataset_statistics(self) -> Dict:
        """
        Get statistics about the datasets
        
        Returns:
            Dictionary with statistics
        """
        if self.resume_df is None:
            self.load_datasets()
        
        # Count unique skills
        all_skills = set()
        for idx, row in self.resume_df.iterrows():
            skills = self.extract_resume_skills(row)
            all_skills.update(skills)
        
        stats = {
            'total_resumes': len(self.resume_df),
            'total_unique_jobs': len(self.job_df),
            'total_unique_skills': len(all_skills),
            'top_10_positions': self.job_df['job_position_name'].value_counts().head(10).to_dict(),
            'columns': self.resume_df.columns.tolist()
        }
        
        return stats


# Utility function for testing
def test_dataset_processor():
    """Test the dataset processor"""
    processor = DatasetProcessor()
    processor.load_datasets()
    
    print("\n=== Dataset Statistics ===")
    stats = processor.get_dataset_statistics()
    print(f"Total Resumes: {stats['total_resumes']}")
    print(f"Unique Jobs: {stats['total_unique_jobs']}")
    print(f"Unique Skills: {stats['total_unique_skills']}")
    
    print("\n=== Top 10 Job Positions ===")
    for pos, count in list(stats['top_10_positions'].items())[:10]:
        print(f"{pos}: {count}")
    
    print("\n=== Sample Resume ===")
    sample = processor.get_random_resume(1).iloc[0]
    print(processor.create_resume_text(sample)[:500])
    
    print("\n=== Sample Job Requirements ===")
    job_req = processor.get_job_requirements("Data Analyst")
    print(json.dumps(job_req, indent=2))


if __name__ == "__main__":
    test_dataset_processor()
