"""
Main processor class for orchestrating rule matching and variable extraction.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from .rule import Rule
from .parser import RuleParser


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
            result = rule.apply(text)
            if result:
                return result
        
        return None

