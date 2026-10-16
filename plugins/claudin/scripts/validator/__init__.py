"""Validador do claudin: regras opinativas sobre estruturas `.claude/` e plugins.

Complementa o `claude plugin validate`, que cobre o formato do plugin.
"""

from . import checks  # noqa: F401  registra as regras
from .core import RULES, Finding, Rule, Target, run

__all__ = ["RULES", "Finding", "Rule", "Target", "run"]
