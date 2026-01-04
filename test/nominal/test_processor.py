"""
Unit tests for the Nominal Processor.
"""

import os
import tempfile

import pytest
from nominal.processor import (
    ActionType,
    AllCriterion,
    AnyCriterion,
    ContainsCriterion,
    CriterionType,
    DeriveAction,
    ExtractAction,
    NominalProcessor,
    RegexCriterion,
    RegexExtractAction,
    RuleParser,
    SetAction,
)


class TestRuleParser:
    """Tests for RuleParser."""

    def test_parse_simple_rule(self):
        """Test parsing a simple rule."""
        rule_data = {
            "form_name": "W2",
            "description": "Test form",
            "variables": {
                "global": ["FIRST_NAME", "LAST_NAME"],
                "local": ["FORM_NAME"],
                "derived": [],
            },
            "criteria": [{"type": "contains", "value": "form w-2", "case_sensitive": False}],
            "actions": [{"type": "set", "variable": "FORM_NAME", "value": "W2"}],
        }

        parser = RuleParser()
        rule = parser.parse_dict(rule_data)

        assert rule.rule_id == "W2"
        assert rule.description == "Test form"
        assert "FIRST_NAME" in rule.global_variables
        assert "FORM_NAME" in rule.local_variables
        assert len(rule.derived_variables) == 0
        assert len(rule.criteria) == 1
        assert len(rule.actions) == 1

    def test_parse_regex_criterion(self):
        """Test parsing a regex criterion."""
        criterion_data = {
            "type": "regex",
            "pattern": r"\d{3}-\d{2}-\d{4}",
            "capture": True,
            "variable": "SSN",
        }

        parser = RuleParser()
        criterion = parser._parse_criterion(criterion_data)

        assert criterion.get_type() == CriterionType.REGEX
        assert isinstance(criterion, RegexCriterion)
        assert criterion.pattern == r"\d{3}-\d{2}-\d{4}"
        assert criterion.capture is True
        assert criterion.variable == "SSN"

    def test_parse_composite_criterion(self):
        """Test parsing composite (all/any) criteria."""
        criterion_data = {
            "type": "all",
            "criteria": [
                {"type": "contains", "value": "test1"},
                {"type": "contains", "value": "test2"},
            ],
        }

        parser = RuleParser()
        criterion = parser._parse_criterion(criterion_data)

        assert criterion.get_type() == CriterionType.ALL
        assert isinstance(criterion, AllCriterion)
        assert len(criterion.sub_criteria) == 2

    def test_parse_derive_action(self):
        """Test parsing a derive action."""
        action_data = {
            "type": "derive",
            "variable": "SSN_LAST_FOUR",
            "from": "SSN",
            "method": "slice",
            "args": {"start": -4},
        }

        parser = RuleParser()
        action = parser._parse_action(action_data)

        assert action.get_type() == ActionType.DERIVE
        assert isinstance(action, DeriveAction)
        assert action.variable == "SSN_LAST_FOUR"
        assert action.from_var == "SSN"
        assert action.method == "slice"
        assert action.args["start"] == -4

    def test_missing_required_field_raises_error(self):
        """Test that missing required fields raise ValueError."""
        parser = RuleParser()

        with pytest.raises(ValueError, match="Missing required field"):
            parser.parse_dict({"form_name": "W2"})


class TestCriterion:
    """Tests for Criterion subclasses."""

    def test_contains_case_sensitive(self):
        """Test case-sensitive contains evaluation."""
        criterion = ContainsCriterion(value="Form W-2", case_sensitive=True)

        matches, captured = criterion.match("This is Form W-2")
        assert matches is True
        assert captured == {}

        matches, captured = criterion.match("This is form w-2")
        assert matches is False

    def test_contains_case_insensitive(self):
        """Test case-insensitive contains evaluation."""
        criterion = ContainsCriterion(value="Form W-2", case_sensitive=False)

        matches, _ = criterion.match("This is Form W-2")
        assert matches is True

        matches, _ = criterion.match("This is form w-2")
        assert matches is True

        matches, _ = criterion.match("This is FORM W-2")
        assert matches is True

    def test_regex_criterion(self):
        """Test regex evaluation."""
        criterion = RegexCriterion(pattern=r"\d{3}-\d{2}-\d{4}")

        matches, captured = criterion.match("SSN: 123-45-6789")
        assert matches is True
        assert captured == {}

        matches, _ = criterion.match("SSN: 12-345-6789")
        assert matches is False

    def test_regex_with_capture(self):
        """Test regex evaluation with capture."""
        criterion = RegexCriterion(pattern=r"\d{3}-\d{2}-\d{4}", capture=True, variable="SSN")

        matches, captured = criterion.match("SSN: 123-45-6789")

        assert matches is True
        assert captured["SSN"] == "123-45-6789"

    def test_all_criterion(self):
        """Test 'all' composite criterion."""
        sub_criteria = [
            ContainsCriterion(value="test1", case_sensitive=False),
            ContainsCriterion(value="test2", case_sensitive=False),
        ]

        criterion = AllCriterion(sub_criteria=sub_criteria)

        matches, _ = criterion.match("test1 and test2")
        assert matches is True

        matches, _ = criterion.match("test1 only")
        assert matches is False

    def test_any_criterion(self):
        """Test 'any' composite criterion."""
        sub_criteria = [
            ContainsCriterion(value="test1", case_sensitive=False),
            ContainsCriterion(value="test2", case_sensitive=False),
        ]

        criterion = AnyCriterion(sub_criteria=sub_criteria)

        matches, _ = criterion.match("test1 only")
        assert matches is True

        matches, _ = criterion.match("test2 only")
        assert matches is True

        matches, _ = criterion.match("neither")
        assert matches is False


class TestAction:
    """Tests for Action subclasses."""

    def test_set_action(self):
        """Test set action execution."""
        action = SetAction(variable="FORM_NAME", value="W2")

        result = action.act("", {})

        assert result == "W2"

    def test_regex_extract_action(self):
        """Test regex_extract action execution."""
        text = "Employee Name: John Doe"

        action = RegexExtractAction(
            variable="FIRST_NAME", pattern=r"Name:\s+(\w+)\s+(\w+)", group=1, from_text=True
        )

        result = action.act(text, {})

        assert result == "John"

    def test_derive_slice_action(self):
        """Test derive action with slice method."""
        variables = {"SSN": "123-45-6789"}

        action = DeriveAction(
            variable="SSN_LAST_FOUR", from_var="SSN", method="slice", args={"start": -4}
        )

        result = action.act("", variables)

        assert result == "6789"

    def test_derive_upper_action(self):
        """Test derive action with upper method."""
        variables = {"NAME": "john doe"}

        action = DeriveAction(variable="NAME_UPPER", from_var="NAME", method="upper", args={})

        result = action.act("", variables)

        assert result == "JOHN DOE"

    def test_extract_split_action(self):
        """Test extract action with split method."""
        variables = {"FULL_NAME": "John Doe"}

        action = ExtractAction(
            variable="FIRST_NAME",
            from_var="FULL_NAME",
            method="split",
            args={"pattern": r"\s+", "index": 0},
        )

        result = action.act("", variables)

        assert result == "John"


class TestNominalProcessor:
    """Tests for NominalProcessor."""

    def test_process_document_with_matching_rule(self):
        """Test processing a document that matches a rule."""
        processor = NominalProcessor()

        # Create a simple rule
        rule_data = {
            "form_name": "W2",
            "description": "Test W2",
            "variables": {
                "global": ["SSN"],
                "local": ["FORM_NAME"],
                "derived": ["SSN_LAST_FOUR"],  # SSN_LAST_FOUR is derived
            },
            "criteria": [
                {"type": "contains", "value": "form w-2", "case_sensitive": False},
                {
                    "type": "regex",
                    "pattern": r"\d{3}-\d{2}-\d{4}",
                    "capture": True,
                    "variable": "SSN",
                },
            ],
            "actions": [
                {"type": "set", "variable": "FORM_NAME", "value": "W2"},
                {
                    "type": "derive",
                    "variable": "SSN_LAST_FOUR",
                    "from": "SSN",
                    "method": "slice",
                    "args": {"start": -4},
                },
            ],
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
        assert result["rule_id"] == "W2"
        assert result["local_variables"]["FORM_NAME"] == "W2"
        assert result["global_variables"]["SSN"] == "123-45-6789"
        assert result["derived_variables"]["SSN_LAST_FOUR"] == "6789"

    def test_process_document_no_match(self):
        """Test processing a document that doesn't match any rule."""
        processor = NominalProcessor()

        # Create a rule
        rule_data = {
            "form_name": "W2",
            "description": "Test W2",
            "variables": {"global": [], "local": [], "derived": []},
            "criteria": [{"type": "contains", "value": "form w-2", "case_sensitive": False}],
            "actions": [],
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
  derived: []
criteria:
  - type: contains
    value: test
actions:
  - type: set
    variable: TEST_VAR
    value: test_value
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(rule_content)
            temp_path = f.name

        try:
            processor = NominalProcessor()
            processor.load_rule(temp_path)

            assert len(processor.rules) == 1
            assert processor.rules[0].rule_id == "TEST"
        finally:
            os.unlink(temp_path)
