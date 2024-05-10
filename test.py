import re
import newOrganisation.sample.model.DisjunctiveNormalForm as dnf

""" catalysts="[a, b, c * d,   (e f)]".strip()
catalysts = re.sub("\\|", ",", catalysts)
catalysts = re.sub("\\*", "&", catalysts)
catalysts = re.sub("\\s*\\(\\s*", "(", catalysts)
catalysts = re.sub("\\s*\\)\\s*", ")", catalysts)
catalysts = re.sub("\\s*&\\s*", "&", catalysts)
catalysts = re.sub("\\s*,\\s*", ",", catalysts)
catalysts = re.sub("\\s+", ",", catalysts) """

var = "d,e&(a,b),c"
tree_a = ["a", "b"]
tree_b = ["c", "d"]
res = []
""" while len(res) < len(var):
    res.append(dnf.next_or(var, len(res)))

print(len(var))
 """
print(dnf.recurse(var))
print(dnf.find_associated_closed_bracket(var, 4))
#print(dnf.recurse(var))
#print(res)