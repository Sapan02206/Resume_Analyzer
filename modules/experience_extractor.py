"""
Experience Extractor Module
Extracts years of experience for skills from resume text

VERSION: 1.1.0 (Hybrid - Narrative + Structured)
STATUS: Production-ready with known limitations

KNOWN LIMITATIONS (to be addressed in future versions):
1. First Match Wins: Does not prioritize based on context
2. Requirements vs Experience: Cannot distinguish job requirements from actual experience
3. Multiple Mentions: Picks first match rather than strongest/most recent
4. Structured Data: Does not parse experience from structured date fields
   (e.g., start_date/end_date columns). Only extracts from narrative text.

USAGE NOTE:
This extractor works with narrative resume text containing explicit
experience statements like:
- "5 years of Python experience"
- "React developer with 3 years"
- "JavaScript: 2019-2023"

For resumes with structured data (separate date fields), consider:
- Calculating job duration from start_date/end_date fields
- Mapping job duration to skills used in that job
- Using a hybrid approach (text + structured data) - Phase 2

FUTURE ENHANCEMENTS (Phase 2+):
- Context-aware prioritization (distinguish "Requirements:" from "I have")
- Semantic understanding ("started 10 years ago" vs "professional experience")
- Multiple mention ranking (prioritize strongest evidence)
- Confidence-based selection (pick highest confidence match)
- Structured data parsing (start_date/end_date fields)
- Job duration to skill experience mapping
- Hybrid text + structured data extraction

DESIGN NOTES:
- Modular pattern system allows easy addition of new patterns
- Extraction logic separated from pattern matching for future ML integration
- Returns structured data with confidence scores for downstream filtering
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class ExperienceExtractor:
    """Extract years of experience for skills from resume text"""
    
    def __init__(self):
        """Initialize experience extractor with patterns"""
        self.patterns = self._build_patterns()
    
    def _build_patterns(self) -> List[Dict]:
        """
        Build regex patterns for experience extraction
        
        Returns:
            List of pattern dictionaries with regex and extraction logic
        """
        return [
            # Pattern 1: "X-Y years [skill]" (range) - CHECK THIS FIRST
            {
                'pattern': r'(\d+)\s*-\s*(\d+)\s*years?\s+(?:of\s+)?(?:experience\s+)?(?:in\s+|with\s+)?{skill}',
                'type': 'year_range',
                'confidence': 0.9
            },
            # Pattern 2: "X years of [skill]" or "[skill] with X years"
            {
                'pattern': r'(\d+(?:\.\d+)?)\s*(?:\+)?\s*years?\s+(?:of\s+)?(?:experience\s+)?(?:in\s+|with\s+)?{skill}',
                'type': 'explicit_years',
                'confidence': 0.95
            },
            # Pattern 3: "[skill] (X years)" or "[skill] - X years"
            {
                'pattern': r'{skill}\s*[\(\-]\s*(\d+(?:\.\d+)?)\s*(?:\+)?\s*years?',
                'type': 'explicit_years',
                'confidence': 0.95
            },
            # Pattern 4: "[skill] developer/engineer with X+ years"
            {
                'pattern': r'{skill}\s+(?:developer|engineer|specialist)?\s*with\s+(\d+(?:\.\d+)?)\s*\+?\s*years?',
                'type': 'explicit_years',
                'confidence': 0.95
            },
            # Pattern 5: "X+ years [skill]" or "X+ years of [skill]"
            {
                'pattern': r'(\d+(?:\.\d+)?)\s*\+\s*years?\s+(?:of\s+)?{skill}',
                'type': 'explicit_years_plus',
                'confidence': 0.9
            },
            # Pattern 6: "[skill]: YYYY-YYYY" or "[skill] (YYYY-YYYY)" or "[skill] YYYY-YYYY"
            {
                'pattern': r'{skill}\s*[\:\(]?\s*(\d{4})\s*[\-–]\s*(\d{4}|present|current|now)',
                'type': 'date_range',
                'confidence': 0.85
            },
            # Pattern 6b: "[skill] Developer/Engineer: YYYY-YYYY"
            {
                'pattern': r'{skill}\s+(?:developer|engineer|specialist|analyst)?\s*[\:\(]\s*(\d{4})\s*[\-–]\s*(\d{4}|present|current|now)',
                'type': 'date_range',
                'confidence': 0.85
            },
            # Pattern 7: "X months of [skill]" or "worked with [skill] for X months"
            {
                'pattern': r'(?:worked\s+with\s+)?{skill}\s+for\s+(\d+)\s*months?',
                'type': 'months',
                'confidence': 0.9
            },
            # Pattern 8: "X months of [skill]"
            {
                'pattern': r'(\d+)\s*months?\s+(?:of\s+)?(?:experience\s+)?(?:in\s+|with\s+)?{skill}',
                'type': 'months',
                'confidence': 0.9
            },
            # Pattern 8b: "[skill] over X months" or "using [skill] over X months"
            {
                'pattern': r'(?:using\s+)?{skill}\s+over\s+(\d+)\s*months?',
                'type': 'months',
                'confidence': 0.85
            },
            # Pattern 8c: "X yrs" abbreviated format
            {
                'pattern': r'(\d+(?:\.\d+)?)\s*yrs?\s+(?:of\s+)?{skill}',
                'type': 'explicit_years',
                'confidence': 0.9
            },
            # Pattern 8d: "[skill]: X yrs" abbreviated with colon
            {
                'pattern': r'{skill}\s*[\:\-]\s*(\d+(?:\.\d+)?)\s*yrs?',
                'type': 'explicit_years',
                'confidence': 0.9
            },
            # Pattern 9: "[skill] for X years"
            {
                'pattern': r'{skill}\s+for\s+(\d+(?:\.\d+)?)\s*(?:\+)?\s*years?',
                'type': 'explicit_years',
                'confidence': 0.95
            },
            # Pattern 10: "Senior/Expert [skill]" (implies 5+ years)
            {
                'pattern': r'(?:senior|expert|lead)\s+{skill}',
                'type': 'seniority_implied',
                'confidence': 0.6
            },
        ]
    
    def extract_experience(self, text: str, skill: str) -> Optional[Dict]:
        """
        Extract years of experience for a specific skill
        
        Args:
            text: Resume text (cleaned)
            skill: Skill name to search for
            
        Returns:
            Dictionary with experience data or None if not found
            {
                'skill': str,
                'years': float,
                'confidence': float,
                'context': str,
                'source': str
            }
        """
        text_lower = text.lower()
        skill_lower = skill.lower()
        
        # Try each pattern
        for i, pattern_dict in enumerate(self.patterns):
            # Replace {skill} placeholder with actual skill
            pattern = pattern_dict['pattern'].replace('{skill}', re.escape(skill_lower))
            
            match = re.search(pattern, text_lower, re.IGNORECASE)
            
            if match:
                # Extract years based on pattern type
                years = self._extract_years_from_match(
                    match, 
                    pattern_dict['type']
                )
                
                if years is not None:
                    # Get context (surrounding text)
                    context = self._get_context(text, match.start(), match.end())
                    
                    return {
                        'skill': skill,
                        'years': years,
                        'confidence': pattern_dict['confidence'],
                        'context': context,
                        'source': pattern_dict['type']
                    }
        
        return None
    
    def _extract_years_from_match(self, match: re.Match, pattern_type: str) -> Optional[float]:
        """
        Extract years value from regex match based on pattern type
        
        Args:
            match: Regex match object
            pattern_type: Type of pattern matched
            
        Returns:
            Years as float or None
        """
        try:
            if pattern_type == 'explicit_years' or pattern_type == 'explicit_years_plus':
                # Single number: "3 years"
                return float(match.group(1))
            
            elif pattern_type == 'year_range':
                # Range: "2-3 years" → average
                start = float(match.group(1))
                end = float(match.group(2))
                return round((start + end) / 2, 1)
            
            elif pattern_type == 'date_range':
                # Date range: "2019-2023" → calculate difference
                start_year = int(match.group(1))
                end_str = match.group(2)
                
                # Handle "present", "current", etc.
                if end_str.lower() in ['present', 'current', 'now']:
                    end_year = datetime.now().year
                else:
                    end_year = int(end_str)
                
                years = end_year - start_year
                return float(years) if years > 0 else None
            
            elif pattern_type == 'months':
                # Months: "18 months" → 1.5 years
                months = float(match.group(1))
                return round(months / 12, 1)
            
            elif pattern_type == 'seniority_implied':
                # Senior/Expert implies 5+ years
                return 5.0
            
        except (ValueError, IndexError):
            return None
        
        return None
    
    def _get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """
        Get surrounding context for the match
        
        Args:
            text: Full text
            start: Match start position
            end: Match end position
            window: Characters to include before/after
            
        Returns:
            Context string
        """
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        context = text[context_start:context_end].strip()
        
        # Clean up context
        context = ' '.join(context.split())
        
        return context
    
    def extract_all_experiences(self, text: str, skills: List[str]) -> List[Dict]:
        """
        Extract experience for all skills in the list
        
        Args:
            text: Resume text
            skills: List of skill names
            
        Returns:
            List of experience dictionaries
        """
        experiences = []
        
        for skill in skills:
            exp = self.extract_experience(text, skill)
            if exp:
                experiences.append(exp)
        
        return experiences
    
    def get_total_experience(self, experiences: List[Dict]) -> float:
        """
        Calculate total years of experience (max of all skills)
        
        Args:
            experiences: List of experience dictionaries
            
        Returns:
            Maximum years of experience
        """
        if not experiences:
            return 0.0
        
        return max(exp['years'] for exp in experiences)
    
    def get_average_experience(self, experiences: List[Dict]) -> float:
        """
        Calculate average years of experience across all skills
        
        Args:
            experiences: List of experience dictionaries
            
        Returns:
            Average years of experience
        """
        if not experiences:
            return 0.0
        
        total = sum(exp['years'] for exp in experiences)
        return round(total / len(experiences), 1)
    
    # ========================================================================
    # STRUCTURED DATA SUPPORT (v1.1.0) - Hybrid Approach
    # ========================================================================
    
    def extract_experience_from_dates(self, start_date: str, end_date: str) -> Optional[float]:
        """
        Calculate years of experience from job start and end dates
        
        This method handles structured data formats where dates are in separate fields
        rather than in narrative text.
        
        VERSION: 1.1.0 (Structured Data Support)
        
        Args:
            start_date: Start date string (e.g., "Nov 2019", "2019-11", "11/2019")
            end_date: End date string (e.g., "Dec 2023", "Till Date", "Present", "2023-12")
            
        Returns:
            Years of experience as float, or None if parsing fails
            
        Examples:
            >>> extractor = ExperienceExtractor()
            >>> extractor.extract_experience_from_dates("Nov 2019", "Dec 2023")
            4.08  # 4 years, 1 month
            >>> extractor.extract_experience_from_dates("2020-01", "Present")
            5.0  # Current year - 2020
        """
        from dateutil import parser as date_parser
        from dateutil.relativedelta import relativedelta
        
        try:
            # Parse start date
            start = self._parse_date_flexible(start_date)
            if not start:
                return None
            
            # Parse end date (handle "Present", "Till Date", "Current", etc.)
            if end_date and end_date.lower() in ['present', 'till date', 'current', 'now', 'ongoing']:
                end = datetime.now()
            else:
                end = self._parse_date_flexible(end_date)
                if not end:
                    end = datetime.now()  # Default to present if can't parse
            
            # Calculate difference
            delta = relativedelta(end, start)
            years = delta.years + (delta.months / 12.0)
            
            # Round to 1 decimal place
            return round(years, 1) if years > 0 else None
            
        except Exception as e:
            # If parsing fails, return None
            return None
    
    def _parse_date_flexible(self, date_str: str) -> Optional[datetime]:
        """
        Flexibly parse various date formats
        
        Handles formats like:
        - "Nov 2019", "November 2019"
        - "2019-11", "2019/11"
        - "11/2019", "11-2019"
        - "2019"
        
        Args:
            date_str: Date string to parse
            
        Returns:
            datetime object or None if parsing fails
        """
        from dateutil import parser as date_parser
        
        if not date_str or not isinstance(date_str, str):
            return None
        
        date_str = date_str.strip()
        
        try:
            # Try dateutil parser (handles most formats)
            return date_parser.parse(date_str, fuzzy=True)
        except:
            pass
        
        # Try year-only format
        try:
            if date_str.isdigit() and len(date_str) == 4:
                return datetime(int(date_str), 1, 1)
        except:
            pass
        
        return None
    
    def extract_experience_from_job_history(self, jobs: List[Dict]) -> Dict[str, float]:
        """
        Extract experience from structured job history
        
        This method processes a list of jobs with start/end dates and calculates
        total experience. Useful for resumes with structured data.
        
        VERSION: 1.1.0 (Structured Data Support)
        
        Args:
            jobs: List of job dictionaries with 'start_date' and 'end_date' keys
                  Example: [
                      {'start_date': 'Nov 2019', 'end_date': 'Dec 2021', 'skills': ['Python', 'Django']},
                      {'start_date': 'Jan 2022', 'end_date': 'Present', 'skills': ['React', 'Node.js']}
                  ]
        
        Returns:
            Dictionary mapping skills to total years of experience
            Example: {'Python': 2.1, 'Django': 2.1, 'React': 3.0, 'Node.js': 3.0}
        """
        skill_experience = {}
        
        for job in jobs:
            # Calculate job duration
            start_date = job.get('start_date')
            end_date = job.get('end_date')
            
            if not start_date:
                continue
            
            years = self.extract_experience_from_dates(start_date, end_date)
            
            if years:
                # Add experience to all skills used in this job
                skills = job.get('skills', [])
                for skill in skills:
                    if skill in skill_experience:
                        skill_experience[skill] += years
                    else:
                        skill_experience[skill] = years
        
        # Round all values
        return {skill: round(years, 1) for skill, years in skill_experience.items()}
    
    def extract_experience_hybrid(self, text: str, skill: str, 
                                  start_date: Optional[str] = None, 
                                  end_date: Optional[str] = None) -> Optional[Dict]:
        """
        Hybrid extraction: Try narrative text first, fall back to structured dates
        
        This is the recommended method for maximum coverage of resume formats.
        
        VERSION: 1.1.0 (Hybrid Approach)
        
        Args:
            text: Resume narrative text
            skill: Skill name to search for
            start_date: Optional job start date (for structured data fallback)
            end_date: Optional job end date (for structured data fallback)
            
        Returns:
            Experience dictionary with years, confidence, context, source
            
        Example:
            >>> # Try narrative first
            >>> result = extractor.extract_experience_hybrid(
            ...     text="Python developer with 5 years experience",
            ...     skill="Python"
            ... )
            >>> # Falls back to dates if narrative fails
            >>> result = extractor.extract_experience_hybrid(
            ...     text="Developed applications using Python",
            ...     skill="Python",
            ...     start_date="Nov 2019",
            ...     end_date="Present"
            ... )
        """
        # Try narrative extraction first (higher confidence)
        narrative_result = self.extract_experience(text, skill)
        
        if narrative_result:
            return narrative_result
        
        # Fall back to structured dates if available
        if start_date:
            years = self.extract_experience_from_dates(start_date, end_date)
            
            if years:
                return {
                    'skill': skill,
                    'years': years,
                    'confidence': 0.75,  # Lower confidence for inferred experience
                    'context': f"Job duration: {start_date} to {end_date or 'Present'}",
                    'source': 'structured_dates'
                }
        
        return None


# Example usage and testing
if __name__ == '__main__':
    # Test the extractor
    extractor = ExperienceExtractor()
    
    test_cases = [
        ("I have 3 years of Python experience", "Python", 3.0),
        ("React developer with 5+ years", "React", 5.0),
        ("Django (2 years)", "Django", 2.0),
        ("Worked with Node.js for 18 months", "Node.js", 1.5),
        ("JavaScript: 2019-2023", "JavaScript", 4.0),
        ("Senior Python Developer", "Python", 5.0),
        ("2-3 years experience in AWS", "AWS", 2.5),
    ]
    
    print("=" * 60)
    print("EXPERIENCE EXTRACTOR - TEST CASES")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for text, skill, expected in test_cases:
        result = extractor.extract_experience(text, skill)
        
        if result and result['years'] == expected:
            print(f"✅ PASS: '{text}' → {result['years']} years")
            passed += 1
        else:
            actual = result['years'] if result else None
            print(f"❌ FAIL: '{text}' → Expected {expected}, Got {actual}")
            if result:
                print(f"   Source: {result['source']}, Confidence: {result['confidence']}")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)


    # ========================================================================
    # STRUCTURED DATA SUPPORT (v1.1.0) - Hybrid Approach
    # ========================================================================
    
    def extract_experience_from_dates(self, start_date: str, end_date: str) -> Optional[float]:
        """
        Calculate years of experience from job start and end dates
        
        This method handles structured data formats where dates are in separate fields
        rather than in narrative text.
        
        VERSION: 1.1.0 (Structured Data Support)
        
        Args:
            start_date: Start date string (e.g., "Nov 2019", "2019-11", "11/2019")
            end_date: End date string (e.g., "Dec 2023", "Till Date", "Present", "2023-12")
            
        Returns:
            Years of experience as float, or None if parsing fails
            
        Examples:
            >>> extractor = ExperienceExtractor()
            >>> extractor.extract_experience_from_dates("Nov 2019", "Dec 2023")
            4.08  # 4 years, 1 month
            >>> extractor.extract_experience_from_dates("2020-01", "Present")
            5.0  # Current year - 2020
        """
        from dateutil import parser as date_parser
        from dateutil.relativedelta import relativedelta
        
        try:
            # Parse start date
            start = self._parse_date_flexible(start_date)
            if not start:
                return None
            
            # Parse end date (handle "Present", "Till Date", "Current", etc.)
            if end_date and end_date.lower() in ['present', 'till date', 'current', 'now', 'ongoing']:
                end = datetime.now()
            else:
                end = self._parse_date_flexible(end_date)
                if not end:
                    end = datetime.now()  # Default to present if can't parse
            
            # Calculate difference
            delta = relativedelta(end, start)
            years = delta.years + (delta.months / 12.0)
            
            # Round to 1 decimal place
            return round(years, 1) if years > 0 else None
            
        except Exception as e:
            # If parsing fails, return None
            return None
    
    def _parse_date_flexible(self, date_str: str) -> Optional[datetime]:
        """
        Flexibly parse various date formats
        
        Handles formats like:
        - "Nov 2019", "November 2019"
        - "2019-11", "2019/11"
        - "11/2019", "11-2019"
        - "2019"
        
        Args:
            date_str: Date string to parse
            
        Returns:
            datetime object or None if parsing fails
        """
        from dateutil import parser as date_parser
        
        if not date_str or not isinstance(date_str, str):
            return None
        
        date_str = date_str.strip()
        
        try:
            # Try dateutil parser (handles most formats)
            return date_parser.parse(date_str, fuzzy=True)
        except:
            pass
        
        # Try year-only format
        try:
            if date_str.isdigit() and len(date_str) == 4:
                return datetime(int(date_str), 1, 1)
        except:
            pass
        
        return None
    
    def extract_experience_from_job_history(self, jobs: List[Dict]) -> Dict[str, float]:
        """
        Extract experience from structured job history
        
        This method processes a list of jobs with start/end dates and calculates
        total experience. Useful for resumes with structured data.
        
        VERSION: 1.1.0 (Structured Data Support)
        
        Args:
            jobs: List of job dictionaries with 'start_date' and 'end_date' keys
                  Example: [
                      {'start_date': 'Nov 2019', 'end_date': 'Dec 2021', 'skills': ['Python', 'Django']},
                      {'start_date': 'Jan 2022', 'end_date': 'Present', 'skills': ['React', 'Node.js']}
                  ]
        
        Returns:
            Dictionary mapping skills to total years of experience
            Example: {'Python': 2.1, 'Django': 2.1, 'React': 3.0, 'Node.js': 3.0}
        """
        skill_experience = {}
        
        for job in jobs:
            # Calculate job duration
            start_date = job.get('start_date')
            end_date = job.get('end_date')
            
            if not start_date:
                continue
            
            years = self.extract_experience_from_dates(start_date, end_date)
            
            if years:
                # Add experience to all skills used in this job
                skills = job.get('skills', [])
                for skill in skills:
                    if skill in skill_experience:
                        skill_experience[skill] += years
                    else:
                        skill_experience[skill] = years
        
        # Round all values
        return {skill: round(years, 1) for skill, years in skill_experience.items()}
    
    def extract_experience_hybrid(self, text: str, skill: str, 
                                  start_date: Optional[str] = None, 
                                  end_date: Optional[str] = None) -> Optional[Dict]:
        """
        Hybrid extraction: Try narrative text first, fall back to structured dates
        
        This is the recommended method for maximum coverage of resume formats.
        
        VERSION: 1.1.0 (Hybrid Approach)
        
        Args:
            text: Resume narrative text
            skill: Skill name to search for
            start_date: Optional job start date (for structured data fallback)
            end_date: Optional job end date (for structured data fallback)
            
        Returns:
            Experience dictionary with years, confidence, context, source
            
        Example:
            >>> # Try narrative first
            >>> result = extractor.extract_experience_hybrid(
            ...     text="Python developer with 5 years experience",
            ...     skill="Python"
            ... )
            >>> # Falls back to dates if narrative fails
            >>> result = extractor.extract_experience_hybrid(
            ...     text="Developed applications using Python",
            ...     skill="Python",
            ...     start_date="Nov 2019",
            ...     end_date="Present"
            ... )
        """
        # Try narrative extraction first (higher confidence)
        narrative_result = self.extract_experience(text, skill)
        
        if narrative_result:
            return narrative_result
        
        # Fall back to structured dates if available
        if start_date:
            years = self.extract_experience_from_dates(start_date, end_date)
            
            if years:
                return {
                    'skill': skill,
                    'years': years,
                    'confidence': 0.75,  # Lower confidence for inferred experience
                    'context': f"Job duration: {start_date} to {end_date or 'Present'}",
                    'source': 'structured_dates'
                }
        
        return None
