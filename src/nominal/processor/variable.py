"""
Variable classes for the processor package.
"""

from abc import ABC, abstractmethod

from .enums import VariableScope


class Variable(ABC):
    """Abstract base class for variables."""

    def __init__(self, name: str, scope: VariableScope):
        self.name = name
        self.scope = scope
        self.value: str | None = None

    @abstractmethod
    def get_scope(self) -> VariableScope:
        """Get the variable scope."""
        pass


class GlobalVariable(Variable):
    """Global variable available across batches."""

    def __init__(self, name: str):
        super().__init__(name, VariableScope.GLOBAL)

    def get_scope(self) -> VariableScope:
        return VariableScope.GLOBAL


class LocalVariable(Variable):
    """Local variable specific to a single document."""

    def __init__(self, name: str):
        super().__init__(name, VariableScope.LOCAL)

    def get_scope(self) -> VariableScope:
        return VariableScope.LOCAL


class DerivedVariable(Variable):
    """Derived variable that can be computed from other variables."""

    def __init__(self, name: str):
        super().__init__(name, VariableScope.DERIVED)

    def get_scope(self) -> VariableScope:
        return VariableScope.DERIVED
