'''
UNKLAR: Warum ein Treeset? Was für einen Vorteil hat das, wenn man dabei kein set behält?
Es wird auch keine DMF...
UNKLAR: Warum ist das eine Klasse, welche Vorteile hat das? Es sollte auch als File funktionieren.
'''


def compute(expression:str) -> str:
    '''
    returns a Disjunctive Normal Form of the expression as a String.

    The resulting String uses "," as "or"/Disjunction and "&" as "and"/Conjunction and does not contain any brackets.
    The input-expression can contain the logical operators:
        "or" as ","
        "and" as "&"
        brackets as "(" and ")" 
    Everything else will be treated as elements.
    There cannot be any whitespaces in the input-expression.
    '''
    return ""

def recurse(expression:str) -> list[str]:
    last_pos = len(expression) - 1
    if expression.startswith("("):
        associated_closed_bracket = find_balance(expression, 0)
        if associated_closed_bracket == last_pos:
            return recurse(expression[1, associated_closed_bracket])
        else:
            next_outside_operator = expression[associated_closed_bracket + 1]
            if next_outside_operator == ",":
                return union(recurse(expression[1, associated_closed_bracket]), recurse(expression[associated_closed_bracket + 2, last_pos]))
            if next_outside_operator == "&":
                return product(recurse(expression[1, associated_closed_bracket]), recurse(expression[associated_closed_bracket + 2, last_pos]))
    else:
        next_inside_operator = next_or(expression, 0)
        if next_inside_operator > 0:
            return union(recurse(expression[0, next_inside_operator]), recurse(expression[next_inside_operator + 1, last_pos]))
        next_inside_operator = next_and(expression, 0)
        if next_inside_operator > 0:
            return product(recurse(expression[0, next_inside_operator]), recurse(expression[next_inside_operator + 1, last_pos]))

    return [expression] #FEHLERANFÄLLIG

def union(tree_a:list, tree_b:list) -> list:
    return []

def product(tree_a:list, tree_b:list) -> list:
    return []

def find_balance(expression:str, start_pos:int) -> int:
    return -1