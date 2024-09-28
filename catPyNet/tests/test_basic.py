# -*- coding: utf-8 -*-

import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


from hypothesis import assume, example, given, settings, strategies as st
import unittest
import copy

from catpynet.fileIO.ModelIO import ModelIO
from catpynet.settings.ReactionNotation import ReactionNotation
from catpynet.settings.ArrowNotation import ArrowNotation
from catpynet.model.MoleculeType import MoleculeType
from catpynet.model.ReactionSystem import ReactionSystem
from catpynet.model.Reaction import Reaction
from catpynet.model.DisjunctiveNormalForm import *


listsize = 3
base_alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

def standard_list(strat):
    return st.lists(strat, min_size=listsize, max_size=listsize)

def standard_text():
    return st.text(base_alphabet, min_size=1)

class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_absolute_truth_and_meaning(self):
        assert True
        
class MoleculeTypeTests(unittest.TestCase):
    """Tests for Moleculetype"""
    
    def test_basic_generation(self):
        
        result = MoleculeType()
        self.assertEqual(MoleculeType(), result)
        
    def test_value_generation(self):
        
        data = "A"
        result = MoleculeType(data)
        self.assertEqual(MoleculeType(data), result)
        
    def test_value_generation_without_constructor(self):
        
        data = MoleculeType()
        result_of_function = data.value_of("A")
        resulting_obj = data
        self.assertEqual(MoleculeType(name2type={"A":MoleculeType("A")}), resulting_obj)
        self.assertEqual(MoleculeType("A"), result_of_function)

    def test_values_generation_without_constructor(self):
        
        data_obj = MoleculeType("A", {"A":MoleculeType("A")})
        data_list = ["A", "B", "C", "A"]
        result_of_function = data_obj.values_of(data_list)
        self.assertEqual(set([MoleculeType("A"), MoleculeType("B"), MoleculeType("C"), MoleculeType("A")]), result_of_function)
        self.assertEqual(MoleculeType("A", {"A":MoleculeType("A"), "B":MoleculeType("B"), "C":MoleculeType("C")}), data_obj)
        
    def test_copy(self):
        
        data = MoleculeType("A", {"A":MoleculeType("A")})
        result = copy.deepcopy(data)
        self.assertEqual(data, result)

class ReactionTests(unittest.TestCase):
    """Tests for Reaction"""
    
    def __init__(self, methodName: str = "runTest") -> None:
        self.BASIC_REACTION = Reaction("Test_Reaction", warned_about_suppressing_coefficients = True,
                                reactants = MoleculeType().values_of(["A", "B"]), products = MoleculeType().values_of(["Z", "Y"]),
                                catalysts = "C,D", inhibitions =  MoleculeType().values_of(["E"]),
                                reactant_coefficients = {"A":1, "B":2},
                                product_coefficients = {"Z":1, "Y": 1},
                                direction = "forward")
        self.EMPTY_REACTION = Reaction()
    
        super().__init__(methodName)
    
    def basic_to_reaction(self,name:str, warned:bool, reactants:list[str], products:list[str], catalysts:list[str]
                              , inhibitors:list[str], reaction_coefficients:list[int], product_coefficients:list[int],
                              direction)->Reaction:
        reactants_m = MoleculeType().values_of(reactants)
        products_m = MoleculeType().values_of(products)
        inhibitors_m = MoleculeType().values_of(inhibitors)
        catalysts_str = catalysts[0]
        for i, c in enumerate(catalysts):
            if i == 0:
                continue
            catalysts_str += "," + c
        reaction_coefficients_dict = {mol:reaction_coefficients[i] for i, mol in enumerate(reactants_m)}
        product_coefficients_dict = {mol:product_coefficients[i] for i, mol in enumerate(products_m)}
        match str(direction):
            case "0":
                direction_key = "forward"
            case "1":
                direction_key = "reverse"
            case "2":
                direction_key = "both"
        test_reaction = Reaction(name, warned_about_suppressing_coefficients=warned, reactants = reactants_m,
                                       products=products_m, catalysts = catalysts_str, inhibitions=inhibitors_m,
                                       reactant_coefficients=reaction_coefficients_dict,
                                       product_coefficients=product_coefficients_dict, direction=direction_key)
        
        return test_reaction
    
    @given(name=st.text(base_alphabet, min_size=1), warned = st.booleans(), reactants = standard_list(standard_text()), 
           products = standard_list(standard_text()), catalysts = standard_list(standard_text()), inhibitors = standard_list(standard_text()),
           reactant_coefficients = st.lists(st.integers(min_value=1), min_size=listsize, max_size=listsize), product_coefficients = st.lists(st.integers(min_value=1), min_size=listsize, max_size=listsize),
           direction = st.integers(0, 2))
    def test_basic_generation(self, name:str, warned:bool, reactants:list[str], products:list[str], catalysts:list[str]
                              , inhibitors:list[str], reactant_coefficients:list[int], product_coefficients:list[int],
                              direction):
        
        result = self.basic_to_reaction(name, warned, reactants, products, catalysts, inhibitors, reactant_coefficients, product_coefficients, direction)
        same_result = self.basic_to_reaction(name, warned, reactants, products, catalysts, inhibitors, reactant_coefficients, product_coefficients, direction)
        self.assertEqual(same_result, result)
        
    def test_name_generation(self):
        
        result = Reaction("A")
        expected = Reaction("A", warned_about_suppressing_coefficients = False,
                                reactants = set(), products = set(),
                                catalysts = "", inhibitions = set(),
                                reactant_coefficients = {},
                                product_coefficients = {},
                                direction = "forward")
        self.assertEqual(result, expected)
        
    @given(name=st.text(base_alphabet, min_size=1), warned = st.booleans(), reactants = standard_list(standard_text()), 
           products = standard_list(standard_text()), catalysts = standard_list(standard_text()), inhibitors = standard_list(standard_text()),
           reactant_coefficients = st.lists(st.integers(min_value=1), min_size=listsize, max_size=listsize), product_coefficients = st.lists(st.integers(min_value=1), min_size=listsize, max_size=listsize),
           direction = st.integers(0, 2))
    def test_copy(self, name:str, warned:bool, reactants:list[str], products:list[str], catalysts:list[str]
                              , inhibitors:list[str], reactant_coefficients:list[int], product_coefficients:list[int],
                              direction):
        
        expected = self.basic_to_reaction(name, warned, reactants, products, catalysts, inhibitors, reactant_coefficients, product_coefficients, direction)
        result = copy.deepcopy(expected)
        self.assertEqual(expected, result)
    
    @given(name=st.text(base_alphabet, min_size=1), warned = st.booleans(), reactants = standard_list(standard_text()), 
           products = standard_list(standard_text()), catalysts = standard_list(standard_text()), inhibitors = standard_list(standard_text()),
           reactant_coefficients = st.lists(st.integers(min_value=1), min_size=listsize, max_size=listsize), product_coefficients = st.lists(st.integers(min_value=1), min_size=listsize, max_size=listsize),
           direction_reaction = st.integers(0, 2), direction_test = st.integers(0, 2), food = st.lists(st.text(base_alphabet, min_size=1)))
    def test_inhibitions_catalization_food_catalyzed(self, name:str, warned:bool, reactants:list[str], products:list[str], catalysts:list[str]
                              , inhibitors:list[str], reactant_coefficients:list[int], product_coefficients:list[int],
                              direction_reaction, direction_test, food:list[str]):
        
        data_obj:Reaction = self.basic_to_reaction(name, warned, reactants, products, catalysts, inhibitors, reactant_coefficients, product_coefficients, direction_reaction)
        data_food_catalyzed = MoleculeType().values_of(food)
        data_catalysts = MoleculeType().values_of(data_obj.catalysts.split(","))
        match str(direction_test):
            case "0":
                direction_key = "forward"
            case "1":
                direction_key = "reverse"
            case "2":
                direction_key = "both"
        result_catalyzed = data_obj.is_catalyzed_uninhibited_all_reactants(direction_key, food=data_food_catalyzed)
        
        if (direction_key in {"forward" or "both"}
            and data_food_catalyzed 
            and data_obj.reactants.issubset(data_food_catalyzed)
            and data_catalysts.issubset(data_food_catalyzed)
            and data_obj.inhibitions.isdisjoint(data_food_catalyzed)):
            self.assertTrue(result_catalyzed)
        elif (direction_key in {"forward" or "both"}
              and data_food_catalyzed 
            and data_obj.products.issubset(data_food_catalyzed)
            and data_catalysts.issubset(data_food_catalyzed)
            and data_obj.inhibitions.isdisjoint(data_food_catalyzed)):
            self.assertTrue(result_catalyzed)
        elif (direction_key in {"forward" or "both"}
              and data_food_catalyzed 
            and data_obj.reactants.issubset(data_food_catalyzed) 
            and data_catalysts.issubset(data_food_catalyzed)
            and data_obj.inhibitions.issubset(data_food_catalyzed)
            and data_obj.inhibitions):
            self.assertFalse(result_catalyzed)
        elif (direction_key in {"forward" or "both"}
              and data_food_catalyzed 
            and data_obj.products.issubset(data_food_catalyzed)
            and data_catalysts.issubset(data_food_catalyzed)
            and data_obj.inhibitions.issubset(data_food_catalyzed)
            and data_obj.inhibitions):
            self.assertFalse(result_catalyzed)
            
    @given(name=st.text(base_alphabet, min_size=1), warned = st.booleans(), reactants = standard_list(standard_text()), 
           products = standard_list(standard_text()), catalysts = standard_list(standard_text()), inhibitors = standard_list(standard_text()),
           reactant_coefficients = st.lists(st.integers(min_value=1), min_size=listsize, max_size=listsize), product_coefficients = st.lists(st.integers(min_value=1), min_size=listsize, max_size=listsize),
           direction_reaction = st.integers(0, 2), direction_test = st.integers(0, 2), food_reactants = st.lists(st.text(base_alphabet, min_size=1)),food_catalyst = st.lists(st.text(base_alphabet, min_size=1)), food_inhibition = st.lists(st.text(base_alphabet, min_size=1)))
    def test_inhibitions_catalization_food_specific(self, name:str, warned:bool, reactants:list[str], products:list[str], catalysts:list[str]
                              , inhibitors:list[str], reactant_coefficients:list[int], product_coefficients:list[int],
                              direction_reaction, direction_test, food_reactants:list[str], food_catalyst:list[str], food_inhibition:list[str]):
        
        data_obj:Reaction = self.basic_to_reaction(name, warned, reactants, products, catalysts, inhibitors, reactant_coefficients, product_coefficients, direction_reaction)
        data_food_catalyzed = MoleculeType().values_of(food_reactants)
        data_food_catalysts = MoleculeType().values_of(food_catalyst)
        data_food_inhibitors = MoleculeType().values_of(food_inhibition)
        
        data_obj_catalysts = MoleculeType().values_of(data_obj.catalysts.split(","))
        
        match str(direction_test):
            case "0":
                direction_key = "forward"
            case "1":
                direction_key = "reverse"
            case "2":
                direction_key = "both"
        result_catalyzed = data_obj.is_catalyzed_uninhibited_all_reactants(direction_key, food_for_reactants = data_food_catalyzed,
                                                                           food_for_catalysts = data_food_catalysts,
                                                                           food_for_inhibitions = data_food_inhibitors)
        
        if (direction_key in {"forward" or "both"}
            and data_obj.reactants.issubset(data_food_catalyzed) 
            and data_obj_catalysts.issubset(data_food_catalysts)
            and data_obj.inhibitions.isdisjoint(data_food_inhibitors)):
            self.assertTrue(result_catalyzed)
        elif (direction_key in {"forward" or "both"}
            and data_obj.reactants.issubset(data_food_catalyzed) 
            and data_obj_catalysts.issubset(data_food_catalysts)
            and data_obj.inhibitions.isdisjoint(data_food_inhibitors)):
            self.assertTrue(result_catalyzed)
        elif (direction_key in {"forward" or "both"}
            and data_obj.reactants.issubset(data_food_catalyzed) 
            and data_obj_catalysts.issubset(data_food_catalysts)
            and data_obj.inhibitions.issubset(data_food_inhibitors)
            and data_obj.inhibitions):
            self.assertFalse(result_catalyzed)
        elif (direction_key in {"forward" or "both"}
            and data_obj.reactants.issubset(data_food_catalyzed) 
            and data_obj_catalysts.issubset(data_food_catalysts)
            and data_obj.inhibitions.issubset(data_food_inhibitors)
            and data_obj.inhibitions):
            self.assertFalse(result_catalyzed)
     
    @given(name=st.text(base_alphabet, min_size=1), warned = st.booleans(), reactants = standard_list(standard_text()), 
           products = standard_list(standard_text()), catalysts = standard_list(standard_text()), inhibitors = standard_list(standard_text()),
           reactant_coefficients = st.lists(st.integers(min_value=1), min_size=listsize, max_size=listsize), product_coefficients = st.lists(st.integers(min_value=1), min_size=listsize, max_size=listsize),
           direction = st.integers(0, 2), tabbed = st.booleans())
    def parser(self, name:str, warned:bool, reactants:list[str], products:list[str], catalysts:list[str]
                              , inhibitors:list[str], reactant_coefficients:list[int], product_coefficients:list[int],
                              direction:int, tabbed:bool):
        """doesnt test for and in catalysts"""
        """ assume(all([react.isalpha() for react in reactants]))
        assume(all([product.isalpha() for product in products]))
        assume(all([catalyst.isalpha() for catalyst in catalysts]))
        assume(all([inhibitor.isalpha() for inhibitor in inhibitors])) """
        result = self.basic_to_reaction(name, warned, reactants, products, catalysts, inhibitors, reactant_coefficients, product_coefficients, direction)
        if not tabbed:
            test_text = name + "/t:"
            for react in reactants:
                test_text += " " + str(result.reactant_coefficients[MoleculeType().value_of(react)]) + " " + react
            test_text += " ["
            for i, c in enumerate(catalysts):
                if i == 0:
                    test_text += c
                else: test_text += "," + c
            test_text += "] {"
            for i, inh in enumerate(inhibitors):
                if i == 0:
                    test_text += inh
                else: test_text += "," + inh
            test_text += "}"
            match str(direction):
                case "0":
                    test_text += " -> "
                case "1":
                    test_text += " <- "
                case "2":
                    test_text += " <-> "
            for product in products:
                test_text += " " + str(result.product_coefficients[MoleculeType().value_of(product)]) + " " + product
        elif tabbed:
            test_text = name + " /t "
            for react in reactants:
                test_text += " " + str(result.reactant_coefficients[MoleculeType().value_of(react)]) + " " + react
            match str(direction):
                case "0":
                    test_text += " -> "
                case "1":
                    test_text += " <- "
                case "2":
                    test_text += " <-> "
            for product in products:
                test_text += " " + str(result.product_coefficients[MoleculeType().value_of(product)]) + " " + product
            test_text += " /t ["
            for i, c in enumerate(catalysts):
                if i == 0:
                    test_text += c
                else: test_text += "," + c
            test_text += "] /t {"
            for i, inh in enumerate(inhibitors):
                if i == 0:
                    test_text += inh
                else: test_text += "," + inh
            test_text += "}"
        
        test_obj = Reaction().parse_new(test_text, tabbed_format=tabbed)
        
        self.assertEqual(test_obj,result)
            
    def dnf(self):
        
        data_str = ["AB,CD&EF&GH,IJ", "AB,(CD&EF)&GH,IJ", "AB,(CD,EF)&GH,IJ", "(AB,CD)&(EF,GH),IJ"]
        dummy_res_str = [{"AB","CD&EF&GH","IJ"}, {"AB","CD&EF&GH","IJ"}, {"AB","CD&GH","EF&GH","IJ"}, {"AB&EF","AB&GH","CD&EF","CD&GH","IJ"}]
        res_str = [MoleculeType().values_of(list(dummy_res_str[i])) for i in range(0,len(dummy_res_str))]
        test_str = [Reaction("", catalysts=data).get_catalyst_conjunctions() for data in data_str]
        print([[mol.name for mol in s] for s in test_str])
        self.assertEqual(test_str, res_str)
        
    def dnf_elements(self):
        data_str = ["AB,CD&EF&GH,IJ", "AB,(CD&EF)&GH,IJ", "AB,(CD,EF)&GH,IJ", "(AB,CD)&(EF,GH),IJ"]
        dummy_res_str = [{"AB","CD","EF","GH","IJ"}, {"AB","CD","EF","GH","IJ"},{"AB","CD","EF","GH","IJ"},{"AB","CD","EF","GH","IJ"}]
        res_str = [MoleculeType().values_of(list(dummy_res_str[i])) for i in range(0,len(dummy_res_str))]
        test_str = [Reaction("", catalysts=data).get_catalyst_elements() for data in data_str]
        print([[mol.name for mol in s] for s in test_str])
        self.assertEqual(test_str, res_str)
                

class ReactionSystemTests(unittest.TestCase):
    
    def basic_to_Reactionsystem(self,reaction_names:list[str], warned:list[bool], reactants:list[list[str]], products:list[list[str]], catalysts:list[list[str]]
                              , inhibitors:list[list[str]], reaction_coefficients:list[list[int]], product_coefficients:list[list[int]],
                              direction:list[int], foods:list[str], rs_name:str)->ReactionSystem:
        sys_reactions = []
        for i, name in enumerate(reaction_names):
            sys_reactions.append(ReactionTests().basic_to_reaction(reaction_names[i], warned[i], reactants[i], 
                                                             products[i], catalysts[i], inhibitors[i], 
                                                             reaction_coefficients[i], product_coefficients[i], direction[i]))
        sys_foods = MoleculeType().values_of(foods)
        return ReactionSystem(rs_name, reactions=sys_reactions, foods=sys_foods)
    
    @given(reaction_names=standard_list(standard_text()), 
           warned = st.lists(st.booleans(), min_size=listsize, max_size=listsize),
           reactants = standard_list(standard_list(standard_text())), 
           products = standard_list(standard_list(standard_text())), 
           catalysts = standard_list(standard_list(standard_text())), 
           inhibitors = standard_list(standard_list(standard_text())),
           reaction_coefficients = standard_list(standard_list(st.integers(min_value=1))), 
           product_coefficients = standard_list(standard_list(st.integers(min_value=1))),
           direction = standard_list(st.integers(0, 2)),
           foods = standard_list(standard_text()),
           rs_name=standard_text())  
    @settings(max_examples=20)
    def test_copy(self,reaction_names:list[str], warned:list[bool], reactants:list[list[str]], products:list[list[str]], catalysts:list[list[str]]
                              , inhibitors:list[list[str]], reaction_coefficients:list[list[int]], product_coefficients:list[list[int]],
                              direction:list[int], foods:list[str], rs_name:str):
        #st = time.time()
        test_obj = self.basic_to_Reactionsystem(reaction_names, warned, reactants, products, catalysts, inhibitors, reaction_coefficients, product_coefficients, direction, foods, rs_name)
        #et = time.time()
        #print(et-st)
        res_obj = copy.copy(test_obj)
        self.assertEqual(test_obj, res_obj)
    
    @given(reaction_names=standard_list(standard_text()), 
           warned = st.lists(st.booleans(), min_size=listsize, max_size=listsize),
           reactants = standard_list(standard_list(standard_text())), 
           products = standard_list(standard_list(standard_text())), 
           catalysts = standard_list(standard_list(standard_text())), 
           inhibitors = standard_list(standard_list(standard_text())),
           reaction_coefficients = standard_list(standard_list(st.integers(min_value=1))), 
           product_coefficients = standard_list(standard_list(st.integers(min_value=1))),
           direction = standard_list(st.integers(0, 2)),
           foods = standard_list(standard_text()),
           rs_name=standard_text(),
           outside_foods = standard_list(standard_text()))  
    @settings(max_examples=20)
    def test_mentioned_foods(self,reaction_names:list[str], warned:list[bool], reactants:list[list[str]], products:list[list[str]], catalysts:list[list[str]]
                              , inhibitors:list[list[str]], reaction_coefficients:list[list[int]], product_coefficients:list[list[int]],
                              direction:list[int], foods:list[str], rs_name:str, outside_foods:list[str]):
        test_obj = self.basic_to_Reactionsystem(reaction_names, warned, reactants, products, catalysts, inhibitors, reaction_coefficients, product_coefficients, direction, foods, rs_name)
        molecules = []
        for one_type in [reactants, products, inhibitors, catalysts]:
            for reactions in one_type:
                for reaction in reactions:
                    molecules.append(reaction)
        molecules = list(set(molecules).intersection(outside_foods))
        result = MoleculeType().values_of(molecules)
        test_res = test_obj.compute_mentioned_foods(MoleculeType().values_of(molecules))
        """ print("function: ")
        print([mol.name for mol in test_res])
        print("constructed: ")
        print([mol.name for mol in result]) """
        self.assertEqual(result, test_res)
        
class ModelIOTests(unittest.TestCase):
    
    def test_in_is_out(self):
        global application_path
        file_path = "G:/Github/BA-Jan/test_files/inhibitions-1.crs"
        test_path = "G:/Github/BA-Jan/test_results/result.crs"
        res_lines = []
        notation = (ReactionNotation.FULL, ArrowNotation.USES_EQUALS)
        with open(file_path, "r") as f:
            res_lines = f.readlines()
            notation = ReactionNotation.detect_notation(res_lines)
        test_obj = ReactionSystem()
        ModelIO.read(test_obj, file_path, notation[0])
        with open(test_path, "w") as f:
            f.write(ModelIO().write(test_obj, True, notation[0], notation[1]))
            
        #print(ModelIO().write(test_obj, True, ReactionNotation.FULL, ArrowNotation.USES_MINUS),test_path)
        with open(test_path) as file:
            test_lines = file.readlines()
            
        self.assertEqual(res_lines, test_lines)
    
            
        
if __name__ == '__main__':
    unittest.main()
    print(sys.path)