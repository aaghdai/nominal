"""
Criterion classes for matching document content.
"""

import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from .enums import CriterionType
from nominal.logging_config import setup_logger

logger = setup_logger('nominal.processor.criterion')


class Criterion(ABC):
    """Abstract base class for matching criteria."""
    
    def __init__(self, description: str = ""):
        self.description = description
    
    @abstractmethod
    def match(self, text: str) -> Tuple[bool, Dict[str, str]]:
        """
        Check if the criterion matches the given text.
        
        Returns:
            Tuple of (match_result, captured_variables)
        """
        pass
    
    @abstractmethod
    def get_type(self) -> CriterionType:
        """Get the criterion type."""
        pass


class ContainsCriterion(Criterion):
    """Criterion that checks if text contains a specific value."""
    
    def __init__(self, value: str, case_sensitive: bool = True, description: str = ""):
        super().__init__(description)
        self.value = value
        self.case_sensitive = case_sensitive
    
    def match(self, text: str) -> Tuple[bool, Dict[str, str]]:
        logger.debug(f"Checking contains criterion: '{self.value}' (case_sensitive={self.case_sensitive})")
        
        search_text = text
        search_value = self.value
        
        if not self.case_sensitive:
            search_text = text.lower()
            search_value = self.value.lower()
        
        result = search_value in search_text
        
        if result:
            logger.debug(f"✓ Contains criterion matched: '{self.value}'")
        else:
            logger.debug(f"✗ Contains criterion failed: '{self.value}' not found")
        
        return (result, {})
    
    def get_type(self) -> CriterionType:
        return CriterionType.CONTAINS


class RegexCriterion(Criterion):
    """Criterion that matches text using a regular expression."""
    
    def __init__(self, pattern: str, capture: bool = False, variable: Optional[str] = None, description: str = ""):
        super().__init__(description)
        self.pattern = pattern
        self.capture = capture
        self.variable = variable
    
    def match(self, text: str) -> Tuple[bool, Dict[str, str]]:
        logger.debug(f"Checking regex criterion: pattern='{self.pattern}', capture={self.capture}")
        
        try:
            match = re.search(self.pattern, text)
        except re.error as e:
            logger.error(f"Invalid regex pattern '{self.pattern}': {e}")
            return (False, {})
        
        captured = {}
        if match:
            if self.capture and self.variable:
                captured[self.variable] = match.group(0)
                logger.info(f"✓ Regex matched and captured: {self.variable}='{match.group(0)}'")
            else:
                logger.debug(f"✓ Regex criterion matched: '{self.pattern}'")
        else:
            logger.debug(f"✗ Regex criterion failed: pattern '{self.pattern}' not found")
        
        return (match is not None, captured)
    
    def get_type(self) -> CriterionType:
        return CriterionType.REGEX


class AllCriterion(Criterion):
    """Composite criterion that requires all sub-criteria to match."""
    
    def __init__(self, sub_criteria: List[Criterion], description: str = ""):
        super().__init__(description)
        self.sub_criteria = sub_criteria
    
    def match(self, text: str) -> Tuple[bool, Dict[str, str]]:
        logger.debug(f"Evaluating ALL criterion with {len(self.sub_criteria)} sub-criteria")
        
        all_captured = {}
        
        for i, criterion in enumerate(self.sub_criteria, 1):
            matches, captured = criterion.match(text)
            if not matches:
                logger.debug(f"✗ ALL criterion failed: sub-criterion {i}/{len(self.sub_criteria)} did not match")
                return (False, {})
            all_captured.update(captured)
        
        logger.debug(f"✓ ALL criterion matched: all {len(self.sub_criteria)} sub-criteria passed")
        return (True, all_captured)
    
    def get_type(self) -> CriterionType:
        return CriterionType.ALL


class AnyCriterion(Criterion):
    """Composite criterion that requires at least one sub-criterion to match."""
    
    def __init__(self, sub_criteria: List[Criterion], description: str = ""):
        super().__init__(description)
        self.sub_criteria = sub_criteria
    
    def match(self, text: str) -> Tuple[bool, Dict[str, str]]:
        logger.debug(f"Evaluating ANY criterion with {len(self.sub_criteria)} sub-criteria")
        
        for i, criterion in enumerate(self.sub_criteria, 1):
            matches, captured = criterion.match(text)
            if matches:
                logger.debug(f"✓ ANY criterion matched: sub-criterion {i}/{len(self.sub_criteria)} passed")
                return (True, captured)
        
        logger.debug(f"✗ ANY criterion failed: none of {len(self.sub_criteria)} sub-criteria matched")
        return (False, {})
    
    def get_type(self) -> CriterionType:
        return CriterionType.ANY

