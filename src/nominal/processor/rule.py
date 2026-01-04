"""
Rule class for representing form identification rules.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from .criterion import Criterion
from .action import Action


@dataclass
class Rule:
    """Represents a complete rule for a form type."""
    form_name: str
    description: str
    variables: Dict[str, List[str]]  # {'global': [...], 'local': [...]}
    criteria: List[Criterion]
    actions: List[Action]
    
    @property
    def all_variables(self) -> List[str]:
        """Returns all variable names defined in this rule."""
        result = []
        if 'global' in self.variables:
            result.extend(self.variables['global'])
        if 'local' in self.variables:
            result.extend(self.variables['local'])
        return result
    
    def apply(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Apply the rule to the given text.
        Returns extracted variables if all criteria match, None otherwise.
        """
        # Check if all criteria match
        all_captured_values = {}
        for criterion in self.criteria:
            if not criterion.match(text):
                return None
            # Collect captured values
            all_captured_values.update(criterion.captured_values)
        
        # Execute all actions
        variables = {}
        variables.update(all_captured_values)
        
        for action in self.actions:
            result = action.act(text, variables)
            if result is not None:
                variables[action.variable] = result
        
        return {
            'form_name': self.form_name,
            'variables': variables,
            'rule_description': self.description
        }

