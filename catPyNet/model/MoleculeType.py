from __future__ import annotations

from copy import deepcopy


class MoleculeType:
    '''
    a molecule type
    '''

    def __deepcopy__(self, memo) -> MoleculeType:
        id_self = id(self)
        _copy = memo.get(id_self)
        if _copy == None:
            _copy = MoleculeType(deepcopy(self.name, memo),
                                 deepcopy(self.name2type, memo))
            memo[id_self] = _copy
        return _copy

    def __init__(self, name: str = None, name2type: dict = {}) -> None:
        self.name = name
        self.name2type = name2type

    def value_of(self, name: str) -> MoleculeType:
        if not (name in self.name2type):
            self.name2type[name] = MoleculeType(name)
        return self.name2type[name]

    def values_of(self, names: list[str]) -> set[MoleculeType]:
        return set([self.value_of(name) for name in names])

    def __eq__(self, other: MoleculeType) -> bool:
        if isinstance(other, MoleculeType):
            return (self.name == other.name)

    def __lt__(self, other: MoleculeType) -> bool:
        return hash(self) < hash(other)

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return self.name
