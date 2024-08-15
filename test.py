""" import re
import newOrganisation.sample.model.DisjunctiveNormalForm as dnf
import newOrganisation.sample.model.ReactionSystem as rs
import newOrganisation.sample.model.Reaction as r
import newOrganisation.sample.model.MoleculeType as mt
import copy
from newOrganisation.sample.algorithm.MaxRAFAlgorithm import MaxRAFAlgorithm as mraf """


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

from os import walk
from os.path import join


f = []
fs = []
for (dirpath, dirnames, filenames) in walk("G:/Github/BA-Jan/catlynet java/catlynet-master/examples"):
    for filename in filenames:
        f.append(join("G:/Github/BA-Jan/catlynet java/catlynet-master/examples", filename))
    fs.extend(filenames)
test_path = "G:/Github/BA-Jan/newOrganisation/test_files"
for i, file in enumerate(f):
    file_lines = []
    with open(file, "r") as one_file:
        lines = one_file.readlines()
        for line in lines:
            if not line.startswith("#"):
                file_lines.append(line)
        
    with open(join(test_path, fs[i]), "w") as new_file:
        new_file.writelines(file_lines)