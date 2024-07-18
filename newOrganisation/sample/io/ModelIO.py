from __future__ import annotations

from ..model.Reaction import MoleculeType

import re

class ModelIO:
    
    
    FORMAL_FOOD = MoleculeType().value_of(name="$")

    def parse_food(a_line:str) -> list[MoleculeType]:
        
        a_line = re.sub(" +", " ",a_line.replace(",", " "))
        if a_line.startswith("Food:"):
            if len(a_line) > len("Food:"):
                a_line = a_line.removeprefix("Food:").strip()
            else:
                a_line = ""
        elif a_line.startswith("Food"):
            if len(a_line) > len("Food"):
                a_line = a_line.removeprefix("Food").strip()
            else:
                a_line = ""
        elif a_line.startswith("F:"):
            if len(a_line) > len("F:"):
                a_line = a_line.removeprefix("F:").strip()
            else:
                a_line = ""
        
        result = []
        for name in a_line.split(" "):
            result.append(MoleculeType().value_of(name))
        return result