from __future__ import annotations
from enum import Enum



class ArrowNotation(Enum):
    

    USES_EQUALS = 1
    USES_MINUS = 2
    
    def __init__(self, label:str = "=>") -> None:
        super().__init__()
        self.label:str = label
    
    def value_of_label(label:str)->ArrowNotation|None:
        if label in ["<=>", "<=", "=>"]: return ArrowNotation.USES_EQUALS
        elif label in ["<->", "<-", "->"]: return ArrowNotation.USES_MINUS
        else: return None
    