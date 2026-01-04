"""
Criterion classes for matching document content.
"""

import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from .enums import CriterionType


class Criterion(ABC):
    """Abstract base class for matching criteria."""
    
    def __init__(self, description: str = ""):
        self.description = description
        self.captured_values: Dict[str, str] = {}
    
    @abstractmethod
    def match(self, text: str) -> bool:
        """Check if the criterion matches the given text."""
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
    
    def match(self, text: str) -> bool:
        search_text = text
        search_value = self.value
        
        if not self.case_sensitive:
            search_text = text.lower()
            search_value = self.value.lower()
        
        return search_value in search_text
    
    def get_type(self) -> CriterionType:
        return CriterionType.CONTAINS


class RegexCriterion(Criterion):
    """Criterion that matches text using a regular expression."""
    
    def __init__(self, pattern: str, capture: bool = False, variable: Optional[str] = None, description: str = ""):
        super().__init__(description)
        self.pattern = pattern
        self.capture = capture
        self.variable = variable
    
    def match(self, text: str) -> bool:
        match = re.search(self.pattern, text)
        
        if match and self.capture and self.variable:
            self.captured_values[self.variable] = match.group(0)
        
        return match is not None
    
    def get_type(self) -> CriterionType:
        return CriterionType.REGEX


class AllCriterion(Criterion):
    """Composite criterion that requires all sub-criteria to match."""
    
    def __init__(self, sub_criteria: List[Criterion], description: str = ""):
        super().__init__(description)
        self.sub_criteria = sub_criteria
    
    def match(self, text: str) -> bool:
        result = all(criterion.match(text) for criterion in self.sub_criteria)
        
        # Collect captured values from all sub-criteria
        for criterion in self.sub_criteria:
            self.captured_values.update(criterion.captured_values)
        
        return result
    
    def get_type(self) -> CriterionType:
        return CriterionType.ALL


class AnyCriterion(Criterion):
    """Composite criterion that requires at least one sub-criterion to match."""
    
    def __init__(self, sub_criteria: List[Criterion], description: str = ""):
        super().__init__(description)
        self.sub_criteria = sub_criteria
    
    def match(self, text: str) -> bool:
        for criterion in self.sub_criteria:
            if criterion.match(text):
                # Collect captured values from matching criteria
                self.captured_values.update(criterion.captured_values)
                return True
        return False
    
    def get_type(self) -> CriterionType:
        return CriterionType.ANY

