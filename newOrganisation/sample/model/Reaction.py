from __future__ import annotations
'''
 * Reaction.java Copyright (C) 2022 Daniel H. Huson
 *
 * (Some files contain contributions from other authors, who are then mentioned separately.)
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY  without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 '''

import re
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from tqdm import tqdm

from sample.model.DisjunctiveNormalForm import compute
from sample.model.MoleculeType import MoleculeType #UNSCHÖN, potentiell überflüssig
from copy import copy, deepcopy


FORMAL_FOOD = MoleculeType().value_of(name="$")

class Reaction:
    '''*
    * a reaction
    * Daniel Huson, 6.2019
    '''

    def __deepcopy__(self, memo) -> Reaction:
        id_self = id(self)
        _copy = memo.get(id_self)
        if _copy == None:
            _copy = Reaction(deepcopy(self.name, memo), warned_about_suppressing_coefficients = deepcopy(self.warned_about_suppressing_coefficients, memo),
                             reactants = deepcopy(self.reactants, memo), products = deepcopy(
                                 self.products, memo), catalysts = deepcopy(self.catalysts, memo),
                             inhibitions = deepcopy(self.inhibitions, memo), reactant_coefficients = deepcopy(
                                 self.reactant_coefficients, memo),
                             product_coefficients = deepcopy(self.product_coefficients, memo), direction = deepcopy(self.direction, memo))
            memo[id_self] = _copy
        return _copy

    def __init__(self, name: str = None, **kwargs) -> Reaction:        
        
        self.DIRECTION = {"forward": 'forward',
                          "reverse": 'reverse', "both": 'both'}

        self.warned_about_suppressing_coefficients = False if "warned_about_suppressing_coefficients" not in kwargs else kwargs["warned_about_suppressing_coefficients"]
        self.name = name
        self.reactants:list[MoleculeType] = [] if "reactants" not in kwargs else kwargs["reactants"]
        self.products:list[MoleculeType] = [] if "products" not in kwargs else kwargs["products"]
        self.catalysts:str = "" if "catalysts" not in kwargs else kwargs["catalysts"]
        self.inhibitions:list[MoleculeType] = [] if "inhibitions" not in kwargs else kwargs["inhibitions"]
        self.reactant_coefficients = {} if "reactant_coefficients" not in kwargs else kwargs["reactant_coefficients"]
        self.product_coefficients = {} if "product_coefficients" not in kwargs else kwargs["product_coefficients"]
        self.direction:str = self.DIRECTION["forward"] if "direction" not in kwargs else kwargs["direction"]

    def is_catalyzed_uninhibited_all_reactants(self, direction: str, **kwargs) -> bool:
        """Checks is reaction is uninhibited, catalyzed and has all reactants.

        Args:
            direction (str): direction of the reaction
            food (list[MoleculeType]): Molecules in food
            
            food_for_reactants(list[MoleculeType]): Molecules available as reactants
            food_for_catalysts(list[MoleculeType]): Molecules available as catalysts
            food_for_inhibitions(list[MoleculeType]): Molecules available as inhibitions
            
        Returns:
            bool: True if uninhibited, catalyzed and all reactants present.
                  If any of these are false returns false. 
        """        
        if "food" in kwargs:
            food_set = set(kwargs["food"])
            return ((direction in {"forward", "both"} and set(self.reactants).issubset(food_set)
                        or direction in {"reverse", "both"} and set(self.products).issubset(food_set))
                    and (len(self.catalysts) == 0 
                        or any(set(MoleculeType().values_of(conjunction.name.split("&"))).issubset(food_set) for conjunction in self.get_catalyst_conjunctions()))
                    and (len(self.inhibitions) == 0
                        or food_set.isdisjoint(self.inhibitions)))
        else:
            reactant_set = set() if not "food_for_reactants" in kwargs else set(kwargs["food_for_reactants"])
            catalyst_set = set() if not "food_for_catalysts" in kwargs else set(kwargs["food_for_catalysts"])
            inhibition_set = set() if not "food_for_inhibitions" in kwargs else set(kwargs["food_for_inhibitions"])
            return ((direction in {"forward", "both"} and set(self.reactants).issubset(reactant_set)
                        or direction in {"reverse", "both"} and set(self.products).issubset(reactant_set))
                    and (len(self.catalysts) == 0 
                        or any(set(MoleculeType().values_of(conjunction.name.split("&"))).issubset(catalyst_set) for conjunction in self.get_catalyst_conjunctions()))
                    and (len(self.inhibitions) == 0
                        or not bool(inhibition_set & set(self.inhibitions))))

    def is_all_reactants(self, food: set[MoleculeType], direction: str) -> bool:
        return (direction in {"forward", "both"} 
                and (set(self.reactants).issubset(food) 
                     or direction in {"reverse", "both"}) 
                and set(self.products).issubset(food))

    def __eq__(self, other: Reaction|None) -> bool:
        if not (isinstance(other, Reaction)):
            return False
        if self.name != other.name: return False; #print("failed at name")
        if self.reactants != other.reactants: return False; #print("failed at reactants")
        if self.products != other.products: return False; #print("failed at products")
        if self.catalysts != other.catalysts: return False; #print("failed at catalysts")
        if self.inhibitions != other.inhibitions: return False; #print("failed at inhibitions")
        if self.reactant_coefficients != other.reactant_coefficients: return False; #print("failed at reactant_coefficients")
        if self.product_coefficients != other.product_coefficients: return False; #print("failed at product_coefficients")
        if self.direction != other.direction: return False; #print("failed at product_coefficients")

        return True

    def __lt__(self, other: Reaction) -> bool:
        return hash(self) < hash(other)

    def __hash__(self) -> int:
        return hash(self.name)

    def parse_new(self, line: str, tabbed_format: bool) -> Reaction:
        
        if line.strip() == "":
            return None
        
        coefficient_bool = False
        line = line.replace("->", "=>")
        line = line.replace("<-", "<=")
        arrow = "=>"
        direction = self.DIRECTION["forward"]
        if "=>" in line: direction = self.DIRECTION["forward"]; arrow="=>"
        elif "<=" in line: direction = self.DIRECTION["reverse"]; arrow="<="
        if "<=>" in line: direction = self.DIRECTION["both"]; arrow="<=>"
        
        tabs = line.count("\t")
        tabbed_format = tabs > 1
        if tabbed_format:
            tokens:list[str] = line.split("\t")
            if len(tokens) == 2: tokens.append("")
            if len(tokens) == 3: tokens.append("")
            re_pro = tokens[1].split(arrow)
            tokens[1] = re_pro[0]
            tokens.append(re_pro[1])
        elif len(line.split("\t")) < 2:
            skipped:list[bool] = []
            for sep in [":", "[", "{", arrow]:
                if sep not in line: skipped.append(True)
                else:               skipped.append(False)
                line = line.replace(sep, "\t")
            tokens:list[str] = line.split("\t")
            for i, sep in enumerate(skipped):
                if sep: tokens.insert(i+1,"")
        else:
            tqdm.write("Line " + line + " could not be parsed as the " + 
                           "parser was unable to recognize the used format.")
            return Reaction()
        for i, token in enumerate(tokens):
            if tabbed_format:
                token = token.replace("[", "")
                token = token.replace("{", "")
            token = token.replace("]", "")
            token = token.replace("}", "")
            tokens[i] = token.strip()
            
        token_dict:dict[list|str] = {"r_name":tokens[0],
                                     "reactants":tokens[1],
                                     "reactant_coefficients":[],
                                     "catalysts":tokens[2],
                                     "inhibitions":tokens[3],
                                     "products":tokens[4],
                                     "product_coefficients":[]}
        is_all_numeric = True
        for side in ["reactants", "products"]:
            if "+" in token_dict[side]:
                token_dict[side] = token_dict[side].split("+")
            else:
                token_dict[side] = [token_dict[side]]
            if is_all_numeric:
                is_all_numeric = all([r.replace(".", "").replace(",","")
                                    .replace(" ", "").isdigit()
                                    for r in token_dict[side]])
        for side in ["reactants", "products"]:
            for i, r in enumerate(token_dict[side]):
                r = r.strip()
                if not is_all_numeric:
                    if " " in r:
                        cache = r.split()
                        if (cache[0].isnumeric() or 
                            cache[0].replace(".", "", 1)
                            .replace(",", "", 1).isdigit()):
                            token_dict[side[:-1] + "_coefficients"].append(cache[0])
                            r = cache[1]
                        elif(cache[1].isnumeric() or 
                            cache[1].replace(".", "", 1)
                            .replace(",", "", 1).isdigit()):
                            token_dict[side[:-1] + "_coefficients"].append(cache[1])
                            r = cache[0]
                        else:
                            tqdm.write("There was an unexpected whitespace in reaction: " +
                                    token_dict["r_name"] + " in reactant " +
                                    r)
                    else:
                        token_dict[side[:-1] + "_coefficients"].append("")
                else:
                    if " " in r:
                        if not coefficient_bool:
                            tqdm.write("Coefficients are illegal if all"
                                       + " molecules are numeric. Coeff is "
                                       + "assumed to be first number."
                                        +"\nThe first issue occured at reaction: \n"
                                        + token_dict["r_name"] + " in molecule " + r)
                        r = r.split()[1]
                token_dict[side][i] = r
        
        token_dict["inhibitions"] = (token_dict["inhibitions"]
                                     .replace(",", " ").split(" ") 
                                     if token_dict["inhibitions"]!="" else [])
        
        catalysts = token_dict["catalysts"]
        if catalysts == "": #FEHLERANFÄLLIG, y tho?
            global FORMAL_FOOD
            catalysts = FORMAL_FOOD.name
        else:
            catalysts = self.uniform_logic_notation(catalysts)
        token_dict["catalysts"] = catalysts
        
        res_reaction = Reaction(token_dict["r_name"], 
                                inhibitions=MoleculeType().values_of(token_dict["inhibitions"]),
                                reactants=MoleculeType().values_of(token_dict["reactants"]), 
                                products=MoleculeType().values_of(token_dict["products"]), 
                                catalysts=token_dict["catalysts"], 
                                reactant_coefficients=token_dict["reactant_coefficients"], 
                                product_coefficients=token_dict["product_coefficients"], 
                                direction=direction)
        return res_reaction
            
    def parse(self, line: str, tabbed_format: bool) -> Reaction: #aux_reations: list[Reaction],
        '''
        DEPRECATED, DOESN'T WORK PROPERLY
        parses a reaction
        ReactionNotation:\n
            name <tab>: [coefficient] reactant ... '[' catalyst ...']'  ['{' inhibitor ... '}'] -> [coefficient] product ...\n
            or
            name <tab>: [coefficient] reactant ... '[' catalyst ... ']'  ['{' inhibitor ... '}'] <- [coefficient] product ...\n
            or
            name <tab>: [coefficient] reactant ... '[' catalyst ... ']' ['{' inhibitor ... '}'] <-> [coefficient] product ...\n
            <p>
        Reactants can be separated by white space or +\n
        Products can be separated by white space or +\n
        Catalysts can be separated by white space or , (for or), or all can be separated by & (for 'and')

        The tabbed format is:\n
        name <tab> [coefficient] reactant ... -> [coefficient] product ... <tab> '[' catalyst ...']'  <tab> ['{' inhibitor ... '}']\n
        '''
        line = line.replace("->", "=>")
        line = line.replace("<-", "<=")
        
        if tabbed_format:
            tokens = line.split('\t')
            for t in tokens:
                t = t.strip()
            if len(tokens) == 3 or len(tokens) == 4:
                if tokens[1].find("<=") == -1:
                    arrow_start = tokens[1].find("=>")
                else:
                    arrow_start = tokens[1].index("<=")

                if arrow_start != -1:
                    if len(tokens) == 3:
                        line = (tokens[0] + ": " + tokens[1][0:arrow_start]
                                + " [" + tokens[2] + "] "
                                + tokens[1][arrow_start:len(tokens[1])-1])
                    else:
                        line = (tokens[0] + ": " + tokens[1][0:arrow_start] + " [" + tokens[2] +
                                "] " + " {" + tokens[3] + "} " +
                                tokens[1][arrow_start:len(tokens[1])-1])

        colon_pos = line.find(':')
        open_squarebracket = line.find('[')
        close_squarebracket = line.find(']')
        open_curlybracket = line.find('{')
        close_curlybracket = line.find('}')

        if ((colon_pos == -1 and not tabbed_format)
            or (open_squarebracket != -1
                and (open_squarebracket < colon_pos
                     or close_squarebracket < open_squarebracket))
            or (open_squarebracket == -1
                and close_squarebracket != -1)
            or (open_curlybracket != -1
                and (open_curlybracket < colon_pos
                     or close_curlybracket < open_curlybracket))
            or (open_curlybracket == -1
                and close_curlybracket != -1)):

            print("colon deosn't exist" + str(colon_pos == -1 and not tabbed_format))
            print("opensquare exist" + str((open_squarebracket != -1
                and (open_squarebracket < colon_pos
                     or close_squarebracket < open_squarebracket))))
            print("opensquare deosn't exist" + str((open_squarebracket == -1
                and close_squarebracket != -1)))
            print("opencurly exist" + str((open_curlybracket != -1
                and (open_curlybracket < colon_pos
                     or close_curlybracket < open_curlybracket))))
            print("opencurly doesn't exist" + str(open_curlybracket == -1
                and close_curlybracket != -1))
            print("Can't parse reaction due to missing/misplaced bracket/colon: " + line)
            raise ValueError

        start_arrow: int
        end_arrow: int
        direction: int

        if "<=>" in line:
            direction = self.DIRECTION["both"]
            start_arrow = line.find("<=>")
            end_arrow = start_arrow + 2
        elif "=>" in line:
            direction = self.DIRECTION["forward"]
            start_arrow = line.find("=>")
            end_arrow = start_arrow + 1
        elif "<=" in line:
            direction = self.DIRECTION["reverse"]
            start_arrow = line.find("<=")
            end_arrow = start_arrow + 1
        else:
            print("Can't parse reaction due to missing arrow: " + line)
            raise ValueError

        reaction_name = line[0:colon_pos].strip()
        end_of_reactants: int

        if open_squarebracket != -1:
            end_of_reactants = open_squarebracket
        elif open_squarebracket == -1:
            if open_curlybracket != -1:
                end_of_reactants = open_curlybracket
            elif open_curlybracket == -1:
                end_of_reactants = start_arrow
            else:
                print('''open_curlybracket has no int value.
                      Can't parse reaction: ''' + line)
                raise ValueError
        else:
            print('''open_squarebracket has no int value.
                      Can't parse reaction: ''' + line)
            raise ValueError
        if "+" in line[colon_pos+1:end_of_reactants]:
            reactants = line[colon_pos+1:end_of_reactants].strip().split("+")
        else: reactants = line[colon_pos+1:end_of_reactants].strip().split()
        """ for r in reactants:
            r = r.strip() """

        catalysts: str
        if open_squarebracket == -1:
            global FORMAL_FOOD
            catalysts = FORMAL_FOOD.name
        else:
            catalysts = line[open_squarebracket+1:close_squarebracket].strip().strip("[").strip("]")
            catalysts = re.sub("\\|", ",", catalysts)
            catalysts = re.sub("\\*", "&", catalysts)
            catalysts = re.sub("\\s*\\(\\s*", "(", catalysts)
            catalysts = re.sub("\\s*\\)\\s*", ")", catalysts)
            catalysts = re.sub("\\s*&\\s*", "&", catalysts)
            catalysts = re.sub("\\s*,\\s*", ",", catalysts)
            catalysts = re.sub("\\s+", ",", catalysts)

        inhibitions: list
        # UNSCHÖN
        if open_curlybracket != -1 and close_curlybracket != -1:
            inhibitor_string = (line[open_curlybracket+1:close_curlybracket]
                                .strip().strip("{").strip("}"))
            inhibitor_string = re.sub("\\|", ",", inhibitor_string)
            inhibitor_string = re.sub("\\*", "&", inhibitor_string)
            inhibitor_string = re.sub("\\s*\\(\\s*", "(", inhibitor_string)
            inhibitor_string = re.sub("\\s*\\)\\s*", ")", inhibitor_string)
            inhibitor_string = re.sub("\\s*&\\s*", "&", inhibitor_string)
            inhibitor_string = re.sub("\\s*,\\s*", ",", inhibitor_string)
            inhibitor_string = re.sub("\\s+", ",", inhibitor_string)
            inhibitions = inhibitor_string.split(",")
        else:
            inhibitions = []

        if "+" in line[end_arrow+1:]:
            products = line[end_arrow+1:].strip().split("+")  # FEHLERANFÄLLIG/NEU
        else: products = line[end_arrow+1:].strip().split()
        """ cache = []
        for p in products:
            cache.extend(p.split(" "))
        products = cache """
        reaction = Reaction(reaction_name)
        if all(r.isnumeric() for r in reactants):
            reactant_list = MoleculeType().values_of(names=reactants)
            for r in reactant_list:
                reaction.reactants.append(r)
        else:
            coefficient = -1
            for token in reactants:
                if token.isnumeric():  # might be problematic, UNSCHÖN
                    if coefficient == -1:
                        coefficient = int(token)
                    else:
                        print(
                            "Can't distinguish between coefficients and reactant names : ")
                        print(reactants)
                        raise ValueError
                else:
                    if coefficient == -1 or coefficient > 0:
                        reaction.reactants.append(MoleculeType().value_of(token))
                    if coefficient > 0:
                        reaction.set_reactant_coefficient(
                            MoleculeType().value_of(token), coefficient)
                        if (not (self.warned_about_suppressing_coefficients)):
                            print("Coefficients found in reactions, ignored")
                            self.warned_about_suppressing_coefficients = True
                    coefficient = -1
                if coefficient == -1 and token.isnumeric():  # might be problematic, UNSCHÖN
                    coefficient = int(token)
            if coefficient != -1:
                msg = "Can't distinguish between coefficients and reactant names : "
                for r in reactants:
                    msg = msg + str(r)
                raise ValueError(msg)

        if all(p.isnumeric() for p in products):
            product_list = MoleculeType().values_of(names=products)
            for p in product_list:
                reaction.products.append(p)
        else:
            coefficient = -1
            for token in products:
                if token.isnumeric():  # might be problematic, UNSCHÖN
                    if coefficient == -1:
                        coefficient = int(token)
                    else:
                        msg = "Can't distinguish between coefficients and product names : "
                        for r in products:
                            msg = msg + str(r)
                        raise ValueError(msg)
                else:
                    if coefficient == -1 or coefficient > 0:
                        reaction.products.append(MoleculeType().value_of(token))
                    if coefficient > 0:
                        reaction.set_product_coefficient(
                            MoleculeType().value_of(token), coefficient)
                        if (not (self.warned_about_suppressing_coefficients)):
                            # UNSCHÖN
                            print("Coefficients found in reactions, ignored")
                            self.warned_about_suppressing_coefficients = True
                    coefficient = -1
                """ if coefficient == -1 and token.isdigit():  # might be problematic, UNSCHÖN
                    coefficient = int(token) """
            if coefficient != -1:
                msg = "Can't distinguish between coefficients and product names : "
                for r in products:
                    msg = msg + str(r)
                raise ValueError(msg)

        reaction.catalysts = catalysts
        for inhibitor in inhibitions:  # UNSCHÖN
            reaction.inhibitions.append(MoleculeType().value_of(inhibitor))
        reaction.direction = direction

        return reaction

    def get_catalyst_conjunctions(self) -> set[MoleculeType]:
        '''
        returns conjunctions of catalysts as a set.
        One element of this set is one permutation of elements that can catalyze the reaction.
        The elements within one element of the set are divided by an "&".
        '''
        conjunctions = []
        dnf = compute(self.catalysts)
        parts = dnf.split(",")
        return set(MoleculeType().values_of(parts))

    def get_catalyst_elements(self) -> set[MoleculeType]:
        '''
        returns all catalyst elements for this reaction as a set, not considering associations between catalysts.
        '''
        toplevel_conjuncitons = self.get_catalyst_conjunctions()
        all_elements = set()
        for conjunction in toplevel_conjuncitons:
            con_elements = conjunction.name.split("&")
            all_elements.update(MoleculeType().values_of(con_elements))
        return all_elements

    def get_reactant_coefficient(self, reactant: MoleculeType) -> int:
        '''
        Returns coefficient mapped to reactant in reactand_coefficients.
        If no coefficient is assigned returns 1.
        '''
        return self.reactant_coefficients[reactant] if self.reactant_coefficients[reactant] else 1

    def set_reactant_coefficient(self, reactant: MoleculeType, coefficient: int) -> None:
        if not (reactant in self.reactant_coefficients):
            self.reactant_coefficients[reactant] = coefficient
        else:
            print('reactant already in coefficients')

    def get_product_coefficient(self, product: MoleculeType):
        '''
        Returns coefficient mapped to reactant in reactand_coefficients.
        If no coefficient is assigned returns 1.
        '''
        return self.product_coefficients[product] if self.product_coefficients[product] else 1

    def set_product_coefficient(self, product: MoleculeType, coefficient: int) -> None:
        if not (product in self.product_coefficients):
            self.product_coefficients[product] = coefficient
        else:
            print('product already in coefficients')

    def any_as_forward(self) -> list[Reaction]:
        '''
        turns this reaction into a list of reactions with the direction forward
        '''
        match self.direction:
            case "forward":
                return [deepcopy(self)]
            case "reverse":
                reverse = deepcopy(self)
                reverse.swap_reactants_and_products()
                return [reverse]
            case "both":
                forward, reverse = deepcopy(self), deepcopy(self)  # UNSCHÖN
                forward.name = forward.name + "[+]"
                reverse.name = reverse.name + "[-]"
                reverse.swap_reactants_and_products()
                return [forward, reverse]

    def swap_reactants_and_products(self):
        self.products, self.reactants = self.reactants, self.products

    def uniform_logic_notation(self, input:str)->str:
        input = re.sub("\\|", ",", input)
        input = re.sub("\\*", "&", input)
        input = re.sub("\\s*\\(\\s*", "(", input)
        input = re.sub("\\s*\\)\\s*", ")", input)
        input = re.sub("\\s*&\\s*", "&", input)
        input = re.sub("\\s*,\\s*", ",", input)
        input = re.sub("\\s+", ",", input)
        return input