"""
UNKLAR: Warum ist das eine Klasse, welche Vorteile hat das? Es sollte auch als File funktionieren.
"""


def compute(expression:str) -> str:
    """
    Return a Disjunctive Normal Form of the expression as a String.

    The resulting String uses "," as "or"/Disjunction and "&" as 
    "and"/Conjunction and does not contain any brackets.
    The input-expression can contain the logical operators:
        "or" as ","
        "and" as "&"
        brackets as "(" and ")" 
    Everything else will be treated as elements.
    There cannot be any whitespaces in the input-expression.

    Parameters:
        expression  (str): A logical expression with brackets to be turned
        into a DNF without brackets

    Returns:

    """
    return ""

def recurse(inner_expression:str) -> list[str]:
    print(inner_expression)
    last_pos = len(inner_expression) #FEHLERANFÄLLIG, warum funktioniert das?
    print(last_pos)
    if inner_expression.startswith("("):
        associated_closed_bracket = find_associated_closed_bracket(inner_expression, 0)
        print(str(associated_closed_bracket+1),last_pos)
        if associated_closed_bracket == last_pos:
            return recurse(inner_expression[1:associated_closed_bracket])
        else:
            next_outside_operator = inner_expression[associated_closed_bracket + 1]
            if next_outside_operator == ",":
                print(str(associated_closed_bracket+1), next_outside_operator,last_pos)
                return union(recurse(inner_expression[1:associated_closed_bracket]), recurse(inner_expression[associated_closed_bracket + 2:last_pos]))
            if next_outside_operator == "&":
                return product(recurse(inner_expression[1:associated_closed_bracket]), recurse(inner_expression[associated_closed_bracket + 2:last_pos]))
    else:
        next_inside_operator = next_or(inner_expression, 0)
        print("or: ", next_inside_operator)
        if next_inside_operator > 0:
            return union(recurse(inner_expression[0:next_inside_operator]), recurse(inner_expression[next_inside_operator + 1:last_pos]))
        next_inside_operator = next_and(inner_expression, 0)
        print("and: ", next_inside_operator)
        if next_inside_operator > 0:
            second_expression = inner_expression[next_inside_operator + 1:last_pos]
            end_of_brackets = find_associated_closed_bracket(second_expression, 0)
            print(second_expression, end_of_brackets)
            if end_of_brackets > 0:
                print("reached endofBracketscheck")
                print("nextAnd: ", next_and(second_expression, end_of_brackets))
                print("nextOR: ", next_or(second_expression, end_of_brackets))
                print("test of last statement: ", next_and(inner_expression[end_of_brackets:last_pos], 0))
                position_after_brackets_and = next_and(second_expression, end_of_brackets)
                position_after_brackets_or = next_or(second_expression, end_of_brackets)
                if ((position_after_brackets_and >= 0 and position_after_brackets_or < 0) 
                      or (position_after_brackets_and < position_after_brackets_or 
                          and position_after_brackets_and >= 0 
                          and position_after_brackets_or >= 0)):
                    print("outer and")
                    return product(product(recurse(inner_expression[0:next_inside_operator]), 
                                        recurse(inner_expression[next_inside_operator + 1:end_of_brackets])),
                                        recurse(inner_expression[end_of_brackets + 1:last_pos]))
                elif ((position_after_brackets_or >= 0 and position_after_brackets_and < 0) 
                      or (position_after_brackets_or < position_after_brackets_and 
                          and position_after_brackets_or >= 0 
                          and position_after_brackets_and >= 0)):
                    print("outer or")
                    return union(product(recurse(inner_expression[0:next_inside_operator]), 
                                        recurse(inner_expression[next_inside_operator + 1:end_of_brackets])),
                                        recurse(inner_expression[end_of_brackets + 1:last_pos]))
            return product(recurse(inner_expression[0:next_inside_operator]), recurse(inner_expression[next_inside_operator + 1:last_pos]))

    return [inner_expression] #FEHLERANFÄLLIG

def union(tree_a:list, tree_b:list) -> list:
    print("union: ", tree_a, tree_b)
    tree_a.extend(tree_b)
    return tree_a

def product(tree_a:list, tree_b:list) -> list:
    print("product: ", tree_a, tree_b)
    res = []
    for content_a in tree_a:
        for content_b in tree_b:
            if content_a == content_b:
                res.append(content_a)
            else:
                res.append(content_a + "&" + content_b)
            print(res)
    return res

def next_or(expression:str, start_pos:int) -> int:
    """
    Return the postion of the next "," after "start_pos" in "expression".
    
    If no "," is found returns -1 instead.
    If no "," is found before the next open bracket "(" returns -1 as well.

    Parameters:
        expression  (str): The string to be searched
        start_pos   (int): The position at which searching starts.

    Returns:
        start_pos   (int): Position of the next ","
        -1          (int): Returned if no relevant "," is found
    """
    end_pos = len(expression) - 1
    while start_pos <= end_pos:
        if expression[start_pos] == ",": return start_pos
        elif expression[start_pos] == "(": return -1
        start_pos += 1
    
    return -1

def next_and(expression:str, start_pos:int) -> int:
    """
    Return the postion of the next "&" after "start_pos" in "expression".
    
    If no "&" is found returns -1 instead.
    If no "&" is found before the next open bracket "(" returns -1 as well.

    Parameters:
        expression  (str): The string to be searched
        start_pos   (int): The position at which searching starts.

    Returns:
        start_pos   (int): Position of the next "&"
        -1          (int): Returned if no relevant "&" is found
    """
    end_pos = len(expression) - 1
    while start_pos <= end_pos:
        if expression[start_pos] == "&": return start_pos
        elif expression[start_pos] == "(": return -1
        start_pos += 1
    
    return -1

def find_associated_closed_bracket(expression:str, start_pos:int) -> int:
    """
    Return position of associated bracket of the open bracket at "start_pos".

    If "start_pos" is not the position of an open bracket returns start_pos.
    If no closed bracket is found after an open bracket returns -1 instead.

    Parameters:
        expression  (str): The string to be analyzed
        start_pos   (int): The position at which analysis starts.

    Returns:
        start_pos   (int): Either the initial position or the position of
        the associated closed bracket.
        -1          (int): Returned if the expression doesn't contain an
        associated bracket
    """
    end_pos = len(expression) - 1
    depth = 0
    while start_pos <= end_pos:
        if expression[start_pos] == "(": depth += 1
        elif expression[start_pos] == ")": depth -= 1
        if depth == 0: return start_pos
        start_pos += 1
    return -1