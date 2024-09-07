from __future__ import annotations
from enum import StrEnum

from .ArrowNotation import ArrowNotation


class ReactionNotation(StrEnum):

    FULL = "FULL"
    SPARSE = "SPARSE"
    TABBED = "TABBED"

    def detect_notation(lines: list[str]) -> tuple[ReactionNotation, ArrowNotation] | None:
        """detects the minimum line format given a list of lines.

        Args:
            lines (list[str]): lines decribing food and reactions

        Returns:
            tuple[ReactionNotation, ArrowNotation] | None: the minimum reaction notation and arrow notation
            
        Prefers FULL and SPARSE to TABBED
        """
        arrows_use_equals = False
        arrows_use_minus = False
        contains_tabs = False
        contains_square_brackets = False
        contains_commas = False

        for line in lines:
            if not line.startswith(("#", "Food:", "F:")):
                if "\t" in line:
                    contains_tabs = True
                if "[" in line or "]" in line:
                    contains_square_brackets = True
                if "=>" in line or "<=" in line:
                    arrows_use_equals = True
                if "->" in line or "<-" in line:
                    arrows_use_minus = True
            elif not line.startswith("#"):
                if "," in line:
                    contains_commas = True
        if arrows_use_minus or arrows_use_equals:
            if contains_square_brackets:
                if contains_commas:
                    return (ReactionNotation.FULL, ArrowNotation.USES_EQUALS if arrows_use_equals else ArrowNotation.USES_MINUS)
                else:
                    return (ReactionNotation.SPARSE, ArrowNotation.USES_EQUALS if arrows_use_equals else ArrowNotation.USES_MINUS)
            elif contains_tabs:
                return (ReactionNotation.TABBED, ArrowNotation.USES_EQUALS if arrows_use_equals else ArrowNotation.USES_MINUS)
        return None
