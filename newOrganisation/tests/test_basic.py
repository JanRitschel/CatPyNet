# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sample
import unittest
import copy

import sample.model as model


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_absolute_truth_and_meaning(self):
        assert True
        
class MoleculeTypeTests(unittest.TestCase):
    """Tests for Moleculetype"""
    
    def test_basic_generation(self):
        
        result = model.MoleculeType()
        self.assertEqual(model.MoleculeType(), result)
        
    def test_value_generation(self):
        
        data = "A"
        result = model.MoleculeType(data)
        self.assertEqual(model.MoleculeType(data), result)
        
    def test_value_generation_without_constructor(self):
        
        data = model.MoleculeType()
        result_of_function = data.value_of("A")
        resulting_obj = data
        self.assertEqual(model.MoleculeType(name2type={"A":model.MoleculeType("A")}), resulting_obj)
        self.assertEqual(model.MoleculeType("A"), result_of_function)

    def test_values_generation_without_constructor(self):
        
        data_obj = model.MoleculeType("A", {"A":model.MoleculeType("A")})
        data_list = ["A", "B", "C", "A"]
        result_of_function = data_obj.values_of(data_list)
        self.assertEqual([model.MoleculeType("A"), model.MoleculeType("B"), model.MoleculeType("C"), model.MoleculeType("A")], result_of_function)
        self.assertEqual(model.MoleculeType("A", {"A":model.MoleculeType("A"), "B":model.MoleculeType("B"), "C":model.MoleculeType("C")}), data_obj)
        
    def test_copy(self):
        
        data = model.MoleculeType("A", {"A":model.MoleculeType("A")})
        result = copy.deepcopy(data)
        self.assertEqual(data, result)

class ReactionTests(unittest.TestCase):
    """Tests for Reaction"""
    
    def __init__(self, methodName: str = "runTest") -> None:
        self.BASIC_REACTION = model.Reaction("Test_Reaction", warned_about_suppressing_coefficients = True,
                                reactants = model.MoleculeType().values_of(["A", "B"]), products = model.MoleculeType().values_of(["Z", "Y"]),
                                catalysts = "C,D", inhibitions =  model.MoleculeType().values_of(["E"]),
                                reactant_coefficients = {"A":1, "B":2},
                                product_coefficients = {"Z":1, "Y": 1},
                                direction = "forward")
        self.EMPTY_REACTION = model.Reaction()
    
        super().__init__(methodName)
    
    def test_basic_generation(self):
        
        result = model.Reaction()
        self.assertEqual(model.Reaction(), result)
        
    def test_full_generation(self):
        
        result = model.Reaction("Test_Reaction", warned_about_suppressing_coefficients = True,
                                reactants = model.MoleculeType().values_of(["A", "B"]), products = model.MoleculeType().values_of(["Z", "Y"]),
                                catalysts = "C,D", inhibitions =  model.MoleculeType().values_of(["E"]),
                                reactant_coefficients = {"A":1, "B":2},
                                product_coefficients = {"Z":1, "Y": 1},
                                direction = "forward")
        expected = self.BASIC_REACTION
        self.assertEqual(result, expected)
        
    def test_name_generation(self):
        
        result = model.Reaction("A")
        expected = model.Reaction("A", warned_about_suppressing_coefficients = False,
                                reactants = [], products = [],
                                catalysts = "", inhibitions = [],
                                reactant_coefficients = {},
                                product_coefficients = {},
                                direction = "forward")
        self.assertEqual(result, expected)
        
    def test_copy(self):
        expected = self.BASIC_REACTION
        result = copy.deepcopy(expected)
        self.assertEqual(expected, result)
        
    def test_inhibitions_catalization_food_catalyzed(self):
        data_direction = "forward"
        data_food_catalyzed = model.MoleculeType().values_of(["A", "B", "C", "D", "A"])
        data_obj = self.BASIC_REACTION
        result_catalyzed = data_obj.is_catalyzed_uninhibited_all_reactants(data_direction, food=data_food_catalyzed)
        self.assertTrue(result_catalyzed)
        
    def test_inhibitions_catalization_food_half_catalyzed(self):
        data_direction = "forward"
        data_food_half_catalyzed = model.MoleculeType().values_of(["A", "B", "C", "A"])
        data_obj = self.BASIC_REACTION
        result_half_catalyzed = data_obj.is_catalyzed_uninhibited_all_reactants(data_direction, food=data_food_half_catalyzed)
        self.assertTrue(result_half_catalyzed)
        
    def test_inhibitions_catalization_food_not_catalyzed(self):
        data_direction = "forward"
        data_food_not_catalyzed = model.MoleculeType().values_of(["A", "B", "A"])
        data_obj = self.BASIC_REACTION
        result_not_catalyzed = data_obj.is_catalyzed_uninhibited_all_reactants(data_direction, food=data_food_not_catalyzed)
        self.assertFalse(result_not_catalyzed)
    
    def test_inhibitions_catalization_food_inhibited(self):
        data_direction = "forward"
        data_food = model.MoleculeType().values_of(["A", "B", "C", "E", "A"])
        data_obj = self.BASIC_REACTION
        result_not_catalyzed = data_obj.is_catalyzed_uninhibited_all_reactants(data_direction, food=data_food)
        self.assertFalse(result_not_catalyzed)
     
    def test_inhibitions_catalization_food_specific_inhibited(self):
        data_direction = "forward"
        data_food_for_reactants = model.MoleculeType().values_of(["A", "B", "A"])
        data_food_for_catalysts = model.MoleculeType().values_of(["C", "D", "C"])
        data_food_for_inhibitions = model.MoleculeType().values_of(["E", "F", "E"])
        data_obj = self.BASIC_REACTION
        result = data_obj.is_catalyzed_uninhibited_all_reactants(data_direction, food_for_reactants = data_food_for_reactants,
                                                                 food_for_catalysts = data_food_for_catalysts,
                                                                 food_for_inhibitions = data_food_for_inhibitions)
        self.assertFalse(result)
        
    def test_inhibitions_catalization_food_specific_catalyzed(self):
        data_direction = "forward"
        data_food_for_reactants = model.MoleculeType().values_of(["A", "B", "A"])
        data_food_for_catalysts = model.MoleculeType().values_of(["C", "D", "C"])
        data_obj = self.BASIC_REACTION
        result = data_obj.is_catalyzed_uninhibited_all_reactants(data_direction, food_for_reactants = data_food_for_reactants,
                                                                 food_for_catalysts = data_food_for_catalysts)
        self.assertTrue(result)
        
        
if __name__ == '__main__':
    unittest.main()