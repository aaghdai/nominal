"""
Nominal Processor: Rule-based document processing engine.

This module implements a DSL-based processor for extracting information
from tax documents based on configurable rules.
"""

import re
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Variable:
    """Represents a variable that can be extracted from a document."""
    name: str
    scope: str  # 'global' or 'local'
    value: Optional[str] = None


@dataclass
class Criterion:
    """Represents a matching criterion for form identification."""
    type: str  # 'contains', 'regex', 'all', 'any'
    description: str = ""
    
    # For 'contains' type
    value: Optional[str] = None
    case_sensitive: bool = True
    
    # For 'regex' type
    pattern: Optional[str] = None
    capture: bool = False
    variable: Optional[str] = None
    
    # For composite types ('all', 'any')
    sub_criteria: List['Criterion'] = field(default_factory=list)


@dataclass
class Action:
    """Represents an action to execute when criteria match."""
    type: str  # 'set', 'extract', 'derive', 'transform', 'regex_extract'
    variable: str
    
    # For 'set' type
    value: Optional[str] = None
    
    # For 'extract', 'regex_extract' type
    from_text: bool = False
    pattern: Optional[str] = None
    group: int = 0
    
    # For 'derive' type
    from_var: Optional[str] = None  # Source variable name
    method: Optional[str] = None
    args: Dict[str, Any] = field(default_factory=dict)


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
        
        criterion = Criterion(
            type=criterion_type,
            description=data.get('description', '')
        )
        
        if criterion_type == 'contains':
            criterion.value = data.get('value')
            criterion.case_sensitive = data.get('case_sensitive', True)
        
        elif criterion_type == 'regex':
            criterion.pattern = data.get('pattern')
            criterion.capture = data.get('capture', False)
            criterion.variable = data.get('variable')
        
        elif criterion_type in ['all', 'any']:
            sub_criteria_data = data.get('criteria', [])
            criterion.sub_criteria = [self._parse_criterion(c) for c in sub_criteria_data]
        
        else:
            raise ValueError(f"Unknown criterion type: {criterion_type}")
        
        return criterion
    
    def _parse_action(self, data: Dict[str, Any]) -> Action:
        """Parse an action dictionary."""
        action_type = data.get('type')
        if not action_type:
            raise ValueError("Action must have a 'type' field")
        
        action = Action(
            type=action_type,
            variable=data.get('variable', '')
        )
        
        if action_type == 'set':
            action.value = data.get('value')
        
        elif action_type == 'regex_extract':
            action.from_text = data.get('from_text', False)
            action.pattern = data.get('pattern')
            action.group = data.get('group', 0)
        
        elif action_type == 'derive':
            action.from_var = data.get('from')
            action.method = data.get('method')
            action.args = data.get('args', {})
        
        elif action_type == 'extract':
            action.from_var = data.get('from')
            action.method = data.get('method')
            action.args = data.get('args', {})
        
        else:
            raise ValueError(f"Unknown action type: {action_type}")
        
        return action


class CriteriaEvaluator:
    """Evaluates criteria against document text."""
    
    def __init__(self):
        self.captured_values: Dict[str, str] = {}
    
    def evaluate(self, criterion: Criterion, text: str) -> bool:
        """Evaluate a criterion against text. Returns True if criterion matches."""
        if criterion.type == 'contains':
            return self._evaluate_contains(criterion, text)
        
        elif criterion.type == 'regex':
            return self._evaluate_regex(criterion, text)
        
        elif criterion.type == 'all':
            return all(self.evaluate(c, text) for c in criterion.sub_criteria)
        
        elif criterion.type == 'any':
            return any(self.evaluate(c, text) for c in criterion.sub_criteria)
        
        else:
            raise ValueError(f"Unknown criterion type: {criterion.type}")
    
    def _evaluate_contains(self, criterion: Criterion, text: str) -> bool:
        """Evaluate a 'contains' criterion."""
        search_text = text
        search_value = criterion.value
        
        if not criterion.case_sensitive:
            search_text = text.lower()
            search_value = criterion.value.lower()
        
        return search_value in search_text
    
    def _evaluate_regex(self, criterion: Criterion, text: str) -> bool:
        """Evaluate a 'regex' criterion."""
        match = re.search(criterion.pattern, text)
        
        if match and criterion.capture and criterion.variable:
            # Store captured value
            self.captured_values[criterion.variable] = match.group(0)
        
        return match is not None


class ActionExecutor:
    """Executes actions to extract and transform variables."""
    
    def __init__(self, text: str):
        self.text = text
        self.variables: Dict[str, str] = {}
    
    def execute(self, action: Action, captured_values: Dict[str, str] = None):
        """Execute an action and update variables."""
        if captured_values is None:
            captured_values = {}
        
        if action.type == 'set':
            self._execute_set(action)
        
        elif action.type == 'regex_extract':
            self._execute_regex_extract(action)
        
        elif action.type == 'derive':
            self._execute_derive(action)
        
        elif action.type == 'extract':
            self._execute_extract(action)
        
        else:
            raise ValueError(f"Unknown action type: {action.type}")
    
    def _execute_set(self, action: Action):
        """Execute a 'set' action."""
        self.variables[action.variable] = action.value
    
    def _execute_regex_extract(self, action: Action):
        """Execute a 'regex_extract' action."""
        if action.from_text:
            match = re.search(action.pattern, self.text)
            if match:
                # group(0) is the full match, group(1+) are capture groups
                if action.group < len(match.groups()) + 1:
                    self.variables[action.variable] = match.group(action.group)
    
    def _execute_derive(self, action: Action):
        """Execute a 'derive' action."""
        if action.from_var not in self.variables:
            return
        
        source_value = self.variables[action.from_var]
        
        if action.method == 'slice':
            start = action.args.get('start')
            end = action.args.get('end')
            self.variables[action.variable] = source_value[start:end]
        
        elif action.method == 'upper':
            self.variables[action.variable] = source_value.upper()
        
        elif action.method == 'lower':
            self.variables[action.variable] = source_value.lower()
    
    def _execute_extract(self, action: Action):
        """Execute an 'extract' action."""
        if action.from_var not in self.variables:
            return
        
        source_value = self.variables[action.from_var]
        
        if action.method == 'split':
            pattern = action.args.get('pattern', r'\s+')
            index = action.args.get('index', 0)
            parts = re.split(pattern, source_value)
            if 0 <= index < len(parts):
                self.variables[action.variable] = parts[index]


class NominalProcessor:
    """Main processor class that orchestrates rule matching and variable extraction."""
    
    def __init__(self, rules_dir: Optional[str] = None):
        self.rules: List[Rule] = []
        self.parser = RuleParser()
        
        if rules_dir:
            self.load_rules(rules_dir)
    
    def load_rules(self, rules_dir: str):
        """Load all rule files from a directory."""
        rules_path = Path(rules_dir)
        if not rules_path.exists():
            raise FileNotFoundError(f"Rules directory not found: {rules_dir}")
        
        # Load all YAML files
        for rule_file in rules_path.glob('*.yaml'):
            rule = self.parser.parse_file(str(rule_file))
            self.rules.append(rule)
        
        for rule_file in rules_path.glob('*.yml'):
            rule = self.parser.parse_file(str(rule_file))
            self.rules.append(rule)
    
    def load_rule(self, rule_path: str):
        """Load a single rule file."""
        rule = self.parser.parse_file(rule_path)
        self.rules.append(rule)
    
    def process_document(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Process a document and extract variables.
        Returns a dict with 'form_name' and 'variables' if a match is found.
        """
        for rule in self.rules:
            result = self._try_match_rule(rule, text)
            if result:
                return result
        
        return None
    
    def _try_match_rule(self, rule: Rule, text: str) -> Optional[Dict[str, Any]]:
        """Try to match a rule against text."""
        evaluator = CriteriaEvaluator()
        
        # Check if all criteria match
        all_match = all(evaluator.evaluate(criterion, text) for criterion in rule.criteria)
        
        if not all_match:
            return None
        
        # Execute actions to extract variables
        executor = ActionExecutor(text)
        
        # First, populate with captured values from criteria
        executor.variables.update(evaluator.captured_values)
        
        # Then execute all actions
        for action in rule.actions:
            executor.execute(action, evaluator.captured_values)
        
        return {
            'form_name': rule.form_name,
            'variables': executor.variables,
            'rule_description': rule.description
        }

