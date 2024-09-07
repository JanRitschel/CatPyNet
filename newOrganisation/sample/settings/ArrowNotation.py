from __future__ import annotations
from enum import StrEnum


class ArrowNotation(StrEnum):

    USES_EQUALS = "USES_EQUALS"
    USES_MINUS = "USES_MINUS"

    def __init__(self, label: str = "=>") -> None:
        super().__init__()
        self.label: str = label

    def value_of_label(label: str) -> ArrowNotation | None:
        """returns appropriate enum-value given an arrow (label)

        Args:
            label (str): an arrow, i.e. '->' or '=>'

        Returns:
            ArrowNotation | None: USES_EQUALS or USES_MINUS
        """        
        if label in ["<=>", "<=", "=>"]:
            return ArrowNotation.USES_EQUALS
        elif label in ["<->", "<-", "->"]:
            return ArrowNotation.USES_MINUS
        else:
            return None
