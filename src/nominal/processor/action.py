"""
Action classes for extracting and transforming variables.
"""

import re
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from .enums import ActionType


class Action(ABC):
    """Abstract base class for actions."""
    
    def __init__(self, variable: str):
        self.variable = variable
    
    @abstractmethod
    def act(self, text: str, variables: Dict[str, str]) -> Optional[str]:
        """
        Execute the action and return the extracted/derived value.
        
        Args:
            text: The document text
            variables: Current variable context
            
        Returns:
            The extracted/derived value, or None if extraction failed
        """
        pass
    
    @abstractmethod
    def get_type(self) -> ActionType:
        """Get the action type."""
        pass


class SetAction(Action):
    """Action that sets a variable to a literal value."""
    
    def __init__(self, variable: str, value: str):
        super().__init__(variable)
        self.value = value
    
    def act(self, text: str, variables: Dict[str, str]) -> Optional[str]:
        return self.value
    
    def get_type(self) -> ActionType:
        return ActionType.SET


class RegexExtractAction(Action):
    """Action that extracts a value from text using a regex pattern."""
    
    def __init__(self, variable: str, pattern: str, group: int = 0, from_text: bool = True):
        super().__init__(variable)
        self.pattern = pattern
        self.group = group
        self.from_text = from_text
    
    def act(self, text: str, variables: Dict[str, str]) -> Optional[str]:
        if self.from_text:
            match = re.search(self.pattern, text)
            if match:
                # group(0) is the full match, group(1+) are capture groups
                if self.group < len(match.groups()) + 1:
                    return match.group(self.group)
        return None
    
    def get_type(self) -> ActionType:
        return ActionType.REGEX_EXTRACT


class DeriveAction(Action):
    """Action that derives a value from another variable."""
    
    def __init__(self, variable: str, from_var: str, method: str, args: Dict[str, Any]):
        super().__init__(variable)
        self.from_var = from_var
        self.method = method
        self.args = args
    
    def act(self, text: str, variables: Dict[str, str]) -> Optional[str]:
        if self.from_var not in variables:
            return None
        
        source_value = variables[self.from_var]
        
        if self.method == 'slice':
            start = self.args.get('start')
            end = self.args.get('end')
            return source_value[start:end]
        
        elif self.method == 'upper':
            return source_value.upper()
        
        elif self.method == 'lower':
            return source_value.lower()
        
        return None
    
    def get_type(self) -> ActionType:
        return ActionType.DERIVE


class ExtractAction(Action):
    """Action that extracts a value from another variable using various methods."""
    
    def __init__(self, variable: str, from_var: str, method: str, args: Dict[str, Any]):
        super().__init__(variable)
        self.from_var = from_var
        self.method = method
        self.args = args
    
    def act(self, text: str, variables: Dict[str, str]) -> Optional[str]:
        if self.from_var not in variables:
            return None
        
        source_value = variables[self.from_var]
        
        if self.method == 'split':
            pattern = self.args.get('pattern', r'\s+')
            index = self.args.get('index', 0)
            parts = re.split(pattern, source_value)
            if 0 <= index < len(parts):
                return parts[index]
        
        return None
    
    def get_type(self) -> ActionType:
        return ActionType.EXTRACT

