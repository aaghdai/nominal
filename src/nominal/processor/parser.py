"""
Parser for YAML rule files.
"""

import yaml
from typing import Dict, List, Any
from pathlib import Path
from .rule import Rule
from .criterion import Criterion, ContainsCriterion, RegexCriterion, AllCriterion, AnyCriterion
from .action import Action, SetAction, RegexExtractAction, DeriveAction, ExtractAction
from .enums import CriterionType, ActionType


class RuleParser:
    """Parses YAML rule files into Rule objects."""
    
    def parse_file(self, rule_path: str) -> Rule:
        """Parse a YAML rule file."""
        path = Path(rule_path)
        if not path.exists():
            raise FileNotFoundError(f"Rule file not found: {rule_path}")
        
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        
        return self.parse_dict(data)
    
    def parse_dict(self, data: Dict[str, Any]) -> Rule:
        """Parse a dictionary into a Rule object."""
        # Validate required fields
        required_fields = ['form_name', 'variables', 'criteria', 'actions']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Parse criteria
        criteria = [self._parse_criterion(c) for c in data['criteria']]
        
        # Parse actions
        actions = [self._parse_action(a) for a in data['actions']]
        
        return Rule(
            form_name=data['form_name'],
            description=data.get('description', ''),
            variables=data['variables'],
            criteria=criteria,
            actions=actions
        )
    
    def _parse_criterion(self, data: Dict[str, Any]) -> Criterion:
        """Parse a criterion dictionary."""
        criterion_type = data.get('type')
        if not criterion_type:
            raise ValueError("Criterion must have a 'type' field")
        
        description = data.get('description', '')
        
        if criterion_type == CriterionType.CONTAINS:
            return ContainsCriterion(
                value=data.get('value'),
                case_sensitive=data.get('case_sensitive', True),
                description=description
            )
        
        elif criterion_type == CriterionType.REGEX:
            return RegexCriterion(
                pattern=data.get('pattern'),
                capture=data.get('capture', False),
                variable=data.get('variable'),
                description=description
            )
        
        elif criterion_type == CriterionType.ALL:
            sub_criteria_data = data.get('criteria', [])
            sub_criteria = [self._parse_criterion(c) for c in sub_criteria_data]
            return AllCriterion(sub_criteria=sub_criteria, description=description)
        
        elif criterion_type == CriterionType.ANY:
            sub_criteria_data = data.get('criteria', [])
            sub_criteria = [self._parse_criterion(c) for c in sub_criteria_data]
            return AnyCriterion(sub_criteria=sub_criteria, description=description)
        
        else:
            raise ValueError(f"Unknown criterion type: {criterion_type}")
    
    def _parse_action(self, data: Dict[str, Any]) -> Action:
        """Parse an action dictionary."""
        action_type = data.get('type')
        if not action_type:
            raise ValueError("Action must have a 'type' field")
        
        variable = data.get('variable', '')
        
        if action_type == ActionType.SET:
            return SetAction(
                variable=variable,
                value=data.get('value')
            )
        
        elif action_type == ActionType.REGEX_EXTRACT:
            return RegexExtractAction(
                variable=variable,
                pattern=data.get('pattern'),
                group=data.get('group', 0),
                from_text=data.get('from_text', False)
            )
        
        elif action_type == ActionType.DERIVE:
            return DeriveAction(
                variable=variable,
                from_var=data.get('from'),
                method=data.get('method'),
                args=data.get('args', {})
            )
        
        elif action_type == ActionType.EXTRACT:
            return ExtractAction(
                variable=variable,
                from_var=data.get('from'),
                method=data.get('method'),
                args=data.get('args', {})
            )
        
        else:
            raise ValueError(f"Unknown action type: {action_type}")

