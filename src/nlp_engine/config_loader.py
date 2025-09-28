# config_loader.py
# Configuration loader for skills and action verbs from YAML files

import yaml
from pathlib import Path
from typing import Dict, List, Set, Optional
import logging

# Set up logging
logger = logging.getLogger(__name__)


class ConfigLoader:
    """Loads and manages skills and action verb configurations from YAML files."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the ConfigLoader.
        
        Args:
            config_path: Path to the config directory. If None, uses default path.
        """
        if config_path is None:
            # Default path: go up from src/nlp_engine to project root, then to config
            self.config_path = Path(__file__).parent.parent.parent / 'config'
        else:
            self.config_path = config_path
            
        self._skills_mapping = None
        self._verbs_data = None
        self._skills_list = None
    
    def load_skills(self) -> Dict[str, str]:
        """Load skills and create a canonical mapping including synonyms.
        
        Returns:
            Dict mapping lowercase skill names/synonyms to canonical skill names.
        """
        if self._skills_mapping is None:
            skills_file = self.config_path / 'skills.yaml'
            
            if not skills_file.exists():
                raise FileNotFoundError(f"Skills configuration file not found: {skills_file}")
            
            try:
                with open(skills_file, 'r', encoding='utf-8') as f:
                    raw_data = yaml.safe_load(f)
                
                canonical_skills = {}
                
                # Process each category
                for category, skills in raw_data.items():
                    if not isinstance(skills, list):
                        logger.warning(f"Skipping invalid category '{category}': expected list, got {type(skills)}")
                        continue
                        
                    for skill_entry in skills:
                        if isinstance(skill_entry, dict) and 'name' in skill_entry:
                            skill_name = skill_entry['name']
                            
                            # Add the main skill name (normalize to lowercase for lookup)
                            canonical_skills[skill_name.lower()] = skill_name
                            
                            # Add all synonyms
                            synonyms = skill_entry.get('synonyms', [])
                            if isinstance(synonyms, list):
                                for synonym in synonyms:
                                    if isinstance(synonym, str):
                                        canonical_skills[synonym.lower()] = skill_name
                                    else:
                                        logger.warning(f"Skipping invalid synonym for '{skill_name}': {synonym}")
                        else:
                            logger.warning(f"Skipping invalid skill entry in category '{category}': {skill_entry}")
                
                self._skills_mapping = canonical_skills
                logger.info(f"Loaded {len(canonical_skills)} skill mappings from {len(raw_data)} categories")
                
            except yaml.YAMLError as e:
                raise ValueError(f"Error parsing skills YAML file: {e}")
            except Exception as e:
                raise RuntimeError(f"Error loading skills configuration: {e}")
        
        return self._skills_mapping
    
    def load_action_verbs(self) -> Dict[str, List[str]]:
        """Load action verbs categorized by impact level.
        
        Returns:
            Dict with keys 'impact_verbs', 'build_verbs', 'support_verbs' and lists of verbs.
        """
        if self._verbs_data is None:
            verbs_file = self.config_path / 'action_verbs.yaml'
            
            if not verbs_file.exists():
                raise FileNotFoundError(f"Action verbs configuration file not found: {verbs_file}")
            
            try:
                with open(verbs_file, 'r', encoding='utf-8') as f:
                    self._verbs_data = yaml.safe_load(f)
                
                # Validate structure
                expected_keys = {'impact_verbs', 'build_verbs', 'support_verbs'}
                if not all(key in self._verbs_data for key in expected_keys):
                    missing_keys = expected_keys - set(self._verbs_data.keys())
                    raise ValueError(f"Missing required verb categories: {missing_keys}")
                
                # Ensure all values are lists
                for category, verbs in self._verbs_data.items():
                    if not isinstance(verbs, list):
                        raise ValueError(f"Category '{category}' must be a list, got {type(verbs)}")
                
                total_verbs = sum(len(verbs) for verbs in self._verbs_data.values())
                logger.info(f"Loaded {total_verbs} action verbs across {len(self._verbs_data)} categories")
                
            except yaml.YAMLError as e:
                raise ValueError(f"Error parsing action verbs YAML file: {e}")
            except Exception as e:
                raise RuntimeError(f"Error loading action verbs configuration: {e}")
        
        return self._verbs_data
    
    def get_skills_list(self) -> List[str]:
        """Get a flat list of all canonical skill names.
        
        Returns:
            List of canonical skill names.
        """
        if self._skills_list is None:
            skills_mapping = self.load_skills()
            # Get unique canonical names
            self._skills_list = list(set(skills_mapping.values()))
            self._skills_list.sort()  # Sort for consistency
        
        return self._skills_list
    
    def find_skill_canonical(self, skill_text: str) -> Optional[str]:
        """Find the canonical form of a skill from input text.
        
        Args:
            skill_text: The skill text to look up (case-insensitive).
            
        Returns:
            Canonical skill name if found, None otherwise.
        """
        skills_mapping = self.load_skills()
        return skills_mapping.get(skill_text.lower())
    
    def reload_config(self):
        """Force reload of all configuration data."""
        self._skills_mapping = None
        self._verbs_data = None
        self._skills_list = None
        logger.info("Configuration cache cleared, will reload on next access")


# Global instance for easy access
_config_loader_instance = None

def get_config_loader() -> ConfigLoader:
    """Get a singleton instance of ConfigLoader."""
    global _config_loader_instance
    if _config_loader_instance is None:
        _config_loader_instance = ConfigLoader()
    return _config_loader_instance