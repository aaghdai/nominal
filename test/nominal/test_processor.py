"""
Unit tests for the Nominal Processor.
"""

import pytest
from nominal.processor import (
    RuleParser, Rule, Criterion, Action,
    CriteriaEvaluator, ActionExecutor, NominalProcessor
)
import tempfile
import os
from pathlib import Path


class TestRuleParser:
    """Tests for RuleParser."""
    
    def test_parse_simple_rule(self):
        """Test parsing a simple rule."""
        rule_data = {
            'form_name': 'W2',
            'description': 'Test form',
            'variables': {
                'global': ['FIRST_NAME', 'LAST_NAME'],
                'local': ['FORM_NAME']
            },
            'criteria': [
                {
                    'type': 'contains',
                    'value': 'form w-2',
                    'case_sensitive': False
                }
            ],
            'actions': [
                {
                    'type': 'set',
                    'variable': 'FORM_NAME',
                    'value': 'W2'
                }
            ]
        }
        
        parser = RuleParser()
        rule = parser.parse_dict(rule_data)
        
        assert rule.form_name == 'W2'
        assert rule.description == 'Test form'
        assert 'FIRST_NAME' in rule.variables['global']
        assert 'FORM_NAME' in rule.variables['local']
        assert len(rule.criteria) == 1
        assert len(rule.actions) == 1
    
    def test_parse_regex_criterion(self):
        """Test parsing a regex criterion."""
        criterion_data = {
            'type': 'regex',
            'pattern': r'\d{3}-\d{2}-\d{4}',
            'capture': True,
            'variable': 'SSN'
        }
        
        parser = RuleParser()
        criterion = parser._parse_criterion(criterion_data)
        
        assert criterion.type == 'regex'
        assert criterion.pattern == r'\d{3}-\d{2}-\d{4}'
        assert criterion.capture is True
        assert criterion.variable == 'SSN'
    
    def test_parse_composite_criterion(self):
        """Test parsing composite (all/any) criteria."""
        criterion_data = {
            'type': 'all',
            'criteria': [
                {'type': 'contains', 'value': 'test1'},
                {'type': 'contains', 'value': 'test2'}
            ]
        }
        
        parser = RuleParser()
        criterion = parser._parse_criterion(criterion_data)
        
        assert criterion.type == 'all'
        assert len(criterion.sub_criteria) == 2
    
    def test_parse_derive_action(self):
        """Test parsing a derive action."""
        action_data = {
            'type': 'derive',
            'variable': 'SSN_LAST_FOUR',
            'from': 'SSN',
            'method': 'slice',
            'args': {'start': -4}
        }
        
        parser = RuleParser()
        action = parser._parse_action(action_data)
        
        assert action.type == 'derive'
        assert action.variable == 'SSN_LAST_FOUR'
        assert action.from_var == 'SSN'
        assert action.method == 'slice'
        assert action.args['start'] == -4
    
    def test_missing_required_field_raises_error(self):
        """Test that missing required fields raise ValueError."""
        parser = RuleParser()
        
        with pytest.raises(ValueError, match="Missing required field"):
            parser.parse_dict({'form_name': 'W2'})


class TestCriteriaEvaluator:
    """Tests for CriteriaEvaluator."""
    
    def test_evaluate_contains_case_sensitive(self):
        """Test case-sensitive contains evaluation."""
        criterion = Criterion(
            type='contains',
            value='Form W-2',
            case_sensitive=True
        )
        
        evaluator = CriteriaEvaluator()
        
        assert evaluator.evaluate(criterion, 'This is Form W-2') is True
        assert evaluator.evaluate(criterion, 'This is form w-2') is False
    
    def test_evaluate_contains_case_insensitive(self):
        """Test case-insensitive contains evaluation."""
        criterion = Criterion(
            type='contains',
            value='Form W-2',
            case_sensitive=False
        )
        
        evaluator = CriteriaEvaluator()
        
        assert evaluator.evaluate(criterion, 'This is Form W-2') is True
        assert evaluator.evaluate(criterion, 'This is form w-2') is True
        assert evaluator.evaluate(criterion, 'This is FORM W-2') is True
    
    def test_evaluate_regex(self):
        """Test regex evaluation."""
        criterion = Criterion(
            type='regex',
            pattern=r'\d{3}-\d{2}-\d{4}'
        )
        
        evaluator = CriteriaEvaluator()
        
        assert evaluator.evaluate(criterion, 'SSN: 123-45-6789') is True
        assert evaluator.evaluate(criterion, 'SSN: 12-345-6789') is False
    
    def test_evaluate_regex_with_capture(self):
        """Test regex evaluation with capture."""
        criterion = Criterion(
            type='regex',
            pattern=r'\d{3}-\d{2}-\d{4}',
            capture=True,
            variable='SSN'
        )
        
        evaluator = CriteriaEvaluator()
        result = evaluator.evaluate(criterion, 'SSN: 123-45-6789')
        
        assert result is True
        assert evaluator.captured_values['SSN'] == '123-45-6789'
    
    def test_evaluate_all_criterion(self):
        """Test 'all' composite criterion."""
        sub_criteria = [
            Criterion(type='contains', value='test1', case_sensitive=False),
            Criterion(type='contains', value='test2', case_sensitive=False)
        ]
        
        criterion = Criterion(
            type='all',
            sub_criteria=sub_criteria
        )
        
        evaluator = CriteriaEvaluator()
        
        assert evaluator.evaluate(criterion, 'test1 and test2') is True
        assert evaluator.evaluate(criterion, 'test1 only') is False
    
    def test_evaluate_any_criterion(self):
        """Test 'any' composite criterion."""
        sub_criteria = [
            Criterion(type='contains', value='test1', case_sensitive=False),
            Criterion(type='contains', value='test2', case_sensitive=False)
        ]
        
        criterion = Criterion(
            type='any',
            sub_criteria=sub_criteria
        )
        
        evaluator = CriteriaEvaluator()
        
        assert evaluator.evaluate(criterion, 'test1 only') is True
        assert evaluator.evaluate(criterion, 'test2 only') is True
        assert evaluator.evaluate(criterion, 'neither') is False


class TestActionExecutor:
    """Tests for ActionExecutor."""
    
    def test_execute_set_action(self):
        """Test set action execution."""
        action = Action(
            type='set',
            variable='FORM_NAME',
            value='W2'
        )
        
        executor = ActionExecutor('')
        executor.execute(action)
        
        assert executor.variables['FORM_NAME'] == 'W2'
    
    def test_execute_regex_extract_action(self):
        """Test regex_extract action execution."""
        text = 'Employee Name: John Doe'
        
        action = Action(
            type='regex_extract',
            variable='FIRST_NAME',
            from_text=True,
            pattern=r'Name:\s+(\w+)\s+(\w+)',
            group=1
        )
        
        executor = ActionExecutor(text)
        executor.execute(action)
        
        assert executor.variables['FIRST_NAME'] == 'John'
    
    def test_execute_derive_slice_action(self):
        """Test derive action with slice method."""
        executor = ActionExecutor('')
        executor.variables['SSN'] = '123-45-6789'
        
        action = Action(
            type='derive',
            variable='SSN_LAST_FOUR',
            from_var='SSN',
            method='slice',
            args={'start': -4}
        )
        
        executor.execute(action)
        
        assert executor.variables['SSN_LAST_FOUR'] == '6789'
    
    def test_execute_derive_upper_action(self):
        """Test derive action with upper method."""
        executor = ActionExecutor('')
        executor.variables['NAME'] = 'john doe'
        
        action = Action(
            type='derive',
            variable='NAME_UPPER',
            from_var='NAME',
            method='upper',
            args={}
        )
        
        executor.execute(action)
        
        assert executor.variables['NAME_UPPER'] == 'JOHN DOE'
    
    def test_execute_extract_split_action(self):
        """Test extract action with split method."""
        executor = ActionExecutor('')
        executor.variables['FULL_NAME'] = 'John Doe'
        
        action = Action(
            type='extract',
            variable='FIRST_NAME',
            from_var='FULL_NAME',
            method='split',
            args={'pattern': r'\s+', 'index': 0}
        )
        
        executor.execute(action)
        
        assert executor.variables['FIRST_NAME'] == 'John'


class TestNominalProcessor:
    """Tests for NominalProcessor."""
    
    def test_process_document_with_matching_rule(self):
        """Test processing a document that matches a rule."""
        processor = NominalProcessor()
        
        # Create a simple rule
        rule_data = {
            'form_name': 'W2',
            'description': 'Test W2',
            'variables': {
                'global': ['SSN'],
                'local': ['FORM_NAME']
            },
            'criteria': [
                {
                    'type': 'contains',
                    'value': 'form w-2',
                    'case_sensitive': False
                },
                {
                    'type': 'regex',
                    'pattern': r'\d{3}-\d{2}-\d{4}',
                    'capture': True,
                    'variable': 'SSN'
                }
            ],
            'actions': [
                {
                    'type': 'set',
                    'variable': 'FORM_NAME',
                    'value': 'W2'
                },
                {
                    'type': 'derive',
                    'variable': 'SSN_LAST_FOUR',
                    'from': 'SSN',
                    'method': 'slice',
                    'args': {'start': -4}
                }
            ]
        }
        
        parser = RuleParser()
        rule = parser.parse_dict(rule_data)
        processor.rules.append(rule)
        
        # Test document
        document = """
        Form W-2 Wage and Tax Statement
        Employee SSN: 123-45-6789
        """
        
        result = processor.process_document(document)
        
        assert result is not None
        assert result['form_name'] == 'W2'
        assert result['variables']['FORM_NAME'] == 'W2'
        assert result['variables']['SSN'] == '123-45-6789'
        assert result['variables']['SSN_LAST_FOUR'] == '6789'
    
    def test_process_document_no_match(self):
        """Test processing a document that doesn't match any rule."""
        processor = NominalProcessor()
        
        # Create a rule
        rule_data = {
            'form_name': 'W2',
            'description': 'Test W2',
            'variables': {'global': [], 'local': []},
            'criteria': [
                {
                    'type': 'contains',
                    'value': 'form w-2',
                    'case_sensitive': False
                }
            ],
            'actions': []
        }
        
        parser = RuleParser()
        rule = parser.parse_dict(rule_data)
        processor.rules.append(rule)
        
        # Test document that doesn't match
        document = "This is not a W2 form"
        
        result = processor.process_document(document)
        
        assert result is None
    
    def test_load_rule_file(self):
        """Test loading a rule from a YAML file."""
        # Create a temporary rule file
        rule_content = """
form_name: TEST
description: Test form
variables:
  global: []
  local: []
criteria:
  - type: contains
    value: test
actions:
  - type: set
    variable: TEST_VAR
    value: test_value
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(rule_content)
            temp_path = f.name
        
        try:
            processor = NominalProcessor()
            processor.load_rule(temp_path)
            
            assert len(processor.rules) == 1
            assert processor.rules[0].form_name == 'TEST'
        finally:
            os.unlink(temp_path)

