import re
import newOrganisation.sample.model.DisjunctiveNormalForm as dnf
import newOrganisation.sample.model.ReactionSystem as rs
import newOrganisation.sample.model.Reaction as r
import newOrganisation.sample.model.MoleculeType as mt
import copy
from newOrganisation.sample.algorithm.MaxRAFAlgorithm import MaxRAFAlgorithm as mraf


""" var = "d,e&(a,b)&c,f&(g),h,i"
tree_a = ["a", "b"]
tree_b = ["c", "d"]
res = [] """
""" while len(res) < len(var):
    res.append(dnf.next_or(var, len(res)))

print(len(var))
 """
""" test_rs = rs.ReactionSystem("newRS")
test_rs.foods = [mt("test_food")]
test_rs.reactions = [r("test_Reaction")]
test_other_rs = copy.copy(test_rs)
print(hash(test_rs) == hash(test_other_rs)) """
""" print(dnf.compute(var)) """
print(mraf())