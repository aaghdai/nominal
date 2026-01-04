"""
Action classes for extracting and transforming variables.
"""

import re
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from .enums import ActionType
from nominal.logging_config import setup_logger

logger = setup_logger('nominal.processor.action')


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
        logger.info(f"Setting variable: {self.variable}='{self.value}'")
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
            logger.debug(f"Attempting regex extraction for {self.variable}: pattern='{self.pattern}'")
            
            try:
                match = re.search(self.pattern, text)
            except re.error as e:
                logger.error(f"Invalid regex pattern '{self.pattern}' for {self.variable}: {e}")
                return None
            
            if match:
                # group(0) is the full match, group(1+) are capture groups
                if self.group < len(match.groups()) + 1:
                    value = match.group(self.group)
                    logger.info(f"✓ Extracted {self.variable}='{value}' using regex")
                    return value
                else:
                    logger.debug(f"✗ Group {self.group} not found in regex match for {self.variable}")
            else:
                logger.debug(f"✗ Regex pattern did not match for {self.variable}")
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
        # Skip derivation if the variable already exists (was extracted directly)
        if self.variable in variables:
            logger.debug(f"Skipping derivation for {self.variable}: already exists with value '{variables[self.variable]}'")
            return None
        
        # Skip if source variable doesn't exist
        if self.from_var not in variables:
            logger.debug(f"Cannot derive {self.variable}: source variable '{self.from_var}' not found")
            return None
        
        source_value = variables[self.from_var]
        logger.debug(f"Deriving {self.variable} from {self.from_var}='{source_value}' using method '{self.method}'")
        
        try:
            if self.method == 'slice':
                start = self.args.get('start')
                end = self.args.get('end')
                result = source_value[start:end]
                logger.info(f"✓ Derived {self.variable}='{result}' by slicing {self.from_var}")
                return result
            
            elif self.method == 'upper':
                result = source_value.upper()
                logger.info(f"✓ Derived {self.variable}='{result}' by uppercasing {self.from_var}")
                return result
            
            elif self.method == 'lower':
                result = source_value.lower()
                logger.info(f"✓ Derived {self.variable}='{result}' by lowercasing {self.from_var}")
                return result
            
            else:
                logger.error(f"Unknown derivation method '{self.method}' for {self.variable}")
                
        except Exception as e:
            logger.error(f"Error deriving {self.variable} from {self.from_var}: {e}")
        
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
            logger.debug(f"Cannot extract {self.variable}: source variable '{self.from_var}' not found")
            return None
        
        source_value = variables[self.from_var]
        logger.debug(f"Extracting {self.variable} from {self.from_var}='{source_value}' using method '{self.method}'")
        
        try:
            if self.method == 'split':
                pattern = self.args.get('pattern', r'\s+')
                index = self.args.get('index', 0)
                parts = re.split(pattern, source_value)
                if 0 <= index < len(parts):
                    result = parts[index]
                    logger.info(f"✓ Extracted {self.variable}='{result}' by splitting {self.from_var}")
                    return result
                else:
                    logger.debug(f"✗ Index {index} out of range when splitting {self.from_var} (got {len(parts)} parts)")
            else:
                logger.error(f"Unknown extraction method '{self.method}' for {self.variable}")
                
        except Exception as e:
            logger.error(f"Error extracting {self.variable} from {self.from_var}: {e}")
        
        return None
    
    def get_type(self) -> ActionType:
        return ActionType.EXTRACT

