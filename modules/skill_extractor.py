"""
Skill Extractor Module - Enhanced with Experience Extraction
VERSION: 2.1.0 (Hybrid - Narrative + Structured)

VERSION HISTORY:
- v2.1.0: Added hybrid extraction (narrative + structured dates)
- v2.0.0: Initial experience integration

INTEGRATION NOTES:
- Maintains backward compatibility with extract_skills()
- New method extract_skills_with_experience() returns enriched data
- Supports both narrative text and structured date extraction
- Modular design allows future enhancements without breaking changes
"""

import json
import re
from typing import List, Set, Dict, Optional

# Import experience extractor for integration
from modules.experience_extractor import ExperienceExtractor

# Try to import spacy (optional)
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None


class SkillExtractor:
    """Extract and normalize skills from resume text"""
    
    def __init__(self, skills_data_path: str):
        """
        Initialize skill extractor with predefined skills
        
        Args:
            skills_data_path: Path to skills.json file
        """
        with open(skills_data_path, 'r') as f:
            self.skills_data = json.load(f)
        
        # Build comprehensive skill list
        self.all_skills = self._build_skill_list()
        
        # Build reverse mapping for normalization
        self.skill_variations = self._build_variation_map()
        
        # Initialize experience extractor (NEW - v2.0.0)
        self.experience_extractor = ExperienceExtractor()
        
        # Load spaCy model for NLP (optional)
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load('en_core_web_sm')
            except Exception as e:
                print(f"Warning: spaCy model not loaded ({e}). Using pattern matching only.")
                self.nlp = None
        else:
            print("Info: spaCy not installed. Using pattern matching only.")
    
    def _build_skill_list(self) -> Set[str]:
        """Build a comprehensive set of all skills"""
        skills = set()
        
        # Add technical skills
        for category, skill_list in self.skills_data['technical_skills'].items():
            skills.update([s.lower() for s in skill_list])
        
        # Add soft skills
        skills.update([s.lower() for s in self.skills_data['soft_skills']])
        
        # Add variations
        for canonical, variations in self.skills_data['skill_variations'].items():
            skills.add(canonical.lower())
            skills.update([v.lower() for v in variations])
        
        return skills
    
    def _build_variation_map(self) -> Dict[str, str]:
        """Build mapping from variations to canonical skill names"""
        variation_map = {}
        
        for canonical, variations in self.skills_data['skill_variations'].items():
            # Map canonical to itself
            variation_map[canonical.lower()] = canonical
            
            # Map each variation to canonical
            for variation in variations:
                variation_map[variation.lower()] = canonical
        
        return variation_map
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from resume text
        
        Args:
            text: Cleaned resume text
            
        Returns:
            List of normalized skill names
        """
        found_skills = set()
        text_lower = text.lower()
        
        # Method 1: Direct pattern matching
        for skill in self.all_skills:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower, re.IGNORECASE):
                found_skills.add(skill)
        
        # Method 2: NLP-based extraction (if spaCy is available)
        if self.nlp:
            doc = self.nlp(text)
            
            # Extract noun chunks that might be skills
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.lower()
                if chunk_text in self.all_skills:
                    found_skills.add(chunk_text)
        
        # Normalize skills to canonical names
        normalized_skills = self._normalize_skills(list(found_skills))
        
        return sorted(list(set(normalized_skills)))
    
    def _normalize_skills(self, skills: List[str]) -> List[str]:
        """
        Normalize skill variations to canonical names
        
        Args:
            skills: List of extracted skills
            
        Returns:
            List of normalized skill names
        """
        normalized = []
        
        for skill in skills:
            skill_lower = skill.lower()
            
            # Check if it's a known variation
            if skill_lower in self.skill_variations:
                normalized.append(self.skill_variations[skill_lower])
            else:
                # Keep original if not in variation map
                # Try to find canonical form in technical skills
                found = False
                for category, skill_list in self.skills_data['technical_skills'].items():
                    for canonical_skill in skill_list:
                        if canonical_skill.lower() == skill_lower:
                            normalized.append(canonical_skill)
                            found = True
                            break
                    if found:
                        break
                
                if not found:
                    # Check soft skills
                    for soft_skill in self.skills_data['soft_skills']:
                        if soft_skill.lower() == skill_lower:
                            normalized.append(soft_skill)
                            found = True
                            break
                
                if not found:
                    # Capitalize first letter of each word
                    normalized.append(skill.title())
        
        return normalized
    
    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """
        Categorize skills into technical and soft skills
        
        Args:
            skills: List of normalized skills
            
        Returns:
            Dictionary with 'technical' and 'soft' categories
        """
        categorized = {
            'technical': [],
            'soft': []
        }
        
        for skill in skills:
            # Check if it's a soft skill
            if skill in self.skills_data['soft_skills']:
                categorized['soft'].append(skill)
            else:
                categorized['technical'].append(skill)
        
        return categorized

    
    # ========================================================================
    # NEW METHOD (v2.0.0): Enhanced Skill Extraction with Experience
    # ========================================================================
    
    def extract_skills_with_experience(self, text: str, start_date: Optional[str] = None, 
                                      end_date: Optional[str] = None) -> List[Dict]:
        """
        Extract skills with experience data from resume text
        
        This is the enhanced version that includes years of experience,
        confidence scores, and context for each skill.
        
        VERSION: 2.1.0 (Hybrid - Narrative + Structured)
        ENHANCEMENTS:
        - v2.1.0: Added hybrid extraction (narrative + structured dates)
        - v2.0.0: Initial experience integration
        
        FUTURE ENHANCEMENTS:
        - Context-aware prioritization (Phase 2)
        - Multiple mention ranking (Phase 2)
        - Semantic understanding (Phase 3)
        
        Args:
            text: Cleaned resume text
            start_date: Optional start date for structured extraction (e.g., "2020-01-01")
            end_date: Optional end date for structured extraction (e.g., "2024-01-01")
            
        Returns:
            List of dictionaries with enriched skill data:
            [
                {
                    'skill': str,                    # Original skill name
                    'normalized_name': str,          # Canonical skill name
                    'category': str,                 # 'technical' or 'soft'
                    'experience_years': float|None,  # Years of experience
                    'experience_confidence': float|None,  # Confidence (0-1)
                    'experience_context': str|None,  # Context where found
                    'experience_source': str|None    # Pattern type matched
                },
                ...
            ]
        
        Example:
            >>> extractor = SkillExtractor('data/skills.json')
            >>> text = "Senior Python Developer with 5 years of experience"
            >>> results = extractor.extract_skills_with_experience(text)
            >>> print(results[0])
            {
                'skill': 'Python',
                'normalized_name': 'Python',
                'category': 'technical',
                'experience_years': 5.0,
                'experience_confidence': 0.95,
                'experience_context': 'Senior Python Developer with 5 years...',
                'experience_source': 'explicit_years'
            }
        """
        # Step 1: Extract basic skills (backward compatible)
        basic_skills = self.extract_skills(text)
        
        # Step 2: Categorize skills
        categorized = self.categorize_skills(basic_skills)
        
        # Step 3: Extract experience for each skill using hybrid approach
        enriched_skills = []
        
        for skill in basic_skills:
            # Determine category
            if skill in categorized['soft']:
                category = 'soft'
            else:
                category = 'technical'
            
            # Extract experience data using hybrid method (v2.1.0)
            # Tries narrative first, falls back to structured dates if provided
            experience_data = self.experience_extractor.extract_experience_hybrid(
                text, skill, start_date, end_date
            )
            
            # Build enriched skill object
            skill_obj = {
                'skill': skill,
                'normalized_name': skill,  # Already normalized by extract_skills()
                'category': category,
                'experience_years': experience_data['years'] if experience_data else None,
                'experience_confidence': experience_data['confidence'] if experience_data else None,
                'experience_context': experience_data['context'] if experience_data else None,
                'experience_source': experience_data['source'] if experience_data else None
            }
            
            enriched_skills.append(skill_obj)
        
        return enriched_skills
    
    def get_experience_summary(self, enriched_skills: List[Dict]) -> Dict:
        """
        Generate summary statistics from enriched skills
        
        Args:
            enriched_skills: Output from extract_skills_with_experience()
            
        Returns:
            Dictionary with summary statistics:
            {
                'total_skills': int,
                'skills_with_experience': int,
                'total_experience_years': float,  # Maximum years
                'average_experience_years': float,
                'average_confidence': float,
                'skills_by_category': {
                    'technical': int,
                    'soft': int
                }
            }
        """
        skills_with_exp = [s for s in enriched_skills if s['experience_years'] is not None]
        
        summary = {
            'total_skills': len(enriched_skills),
            'skills_with_experience': len(skills_with_exp),
            'total_experience_years': 0.0,
            'average_experience_years': 0.0,
            'average_confidence': 0.0,
            'skills_by_category': {
                'technical': len([s for s in enriched_skills if s['category'] == 'technical']),
                'soft': len([s for s in enriched_skills if s['category'] == 'soft'])
            }
        }
        
        if skills_with_exp:
            # Calculate total (max) experience
            summary['total_experience_years'] = max(s['experience_years'] for s in skills_with_exp)
            
            # Calculate average experience
            summary['average_experience_years'] = round(
                sum(s['experience_years'] for s in skills_with_exp) / len(skills_with_exp),
                1
            )
            
            # Calculate average confidence
            summary['average_confidence'] = round(
                sum(s['experience_confidence'] for s in skills_with_exp) / len(skills_with_exp),
                2
            )
        
        return summary
