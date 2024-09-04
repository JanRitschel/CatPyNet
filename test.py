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
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sample.model.Reaction import Reaction
import math
import itertools

def main():
    names = ["r"+str(i) for i in range(3)]
    molecules_1 = ["02"]
    molecules_2 = ["01"]
    coefficients = ["0", "1.1", ""]
    arrows = ["<->", "<-", "->"]
    tests = itertools.product(names, [":"], coefficients, [" "], molecules_1, ["+"], coefficients,[" "], molecules_2
                              , ["["], molecules_1, ["]"], ["{"], molecules_2, ["}"], arrows, coefficients,[" "], molecules_1)
    result = {"<->":[], "<-":[], "->":[]}
    all_molec = molecules_1
    all_molec.extend(molecules_2)
    for test in tests:
        cache = "".join(test)
        res_dict = Reaction().parse_new(cache, False)
        res_bool = True
        fail_list = []
        if res_dict["r_name"] != test[0]:res_bool = False; fail_list.append("r_name")
        if set(res_dict["reactants"]) != {test[4], test[8]}:res_bool = False; fail_list.extend(["reactants", test[4], test[8]])
        if set(res_dict["reactant_coefficients"]) !={test[2], test[6]}:res_bool = False; fail_list.extend(["reactant_coefficients", test[2], test[6]])
        if set(res_dict["products"]) !=set([test[18]]):res_bool = False; fail_list.extend(["products", test[18]])
        if set(res_dict["product_coefficients"]) !=set([test[16]]):res_bool = False; fail_list.extend(["product_coefficients", test[16]])
        if set([res_dict["catalysts"]]) !=set([test[10]]):res_bool = False; fail_list.append("catalysts")
        if set([res_dict["inhibitors"]]) !=set([test[13]]):res_bool = False; fail_list.append("inhibitors")
        result[test[15]].append(tuple([res_bool, fail_list]))
    for k in result.keys():
        bool_list = [p[0] for p in result[k]]
        print(k + ": " + str(sum(bool_list)) + " of " + str(len(bool_list)) + "\nmean: " + str(sum(bool_list)/len(bool_list)))
        print("this was due to: ")  
        full_fall_list = [ps for p in result[k] for ps in p[1]]
        for key in Reaction().parse_new("", False).keys():
            print(key + ": " + str(full_fall_list.count(key)))
        for molecule in all_molec:
            print(molecule + ": " + str(full_fall_list.count(molecule)))
        for coef in coefficients:
            print(coef + ": " + str(full_fall_list.count(coef)))
    

if __name__ == "__main__":
    main()