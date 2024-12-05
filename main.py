from flask import Flask, request, jsonify, render_template
import ply.lex as lex
import ply.yacc as yacc
from lark import Lark, Tree

grammar = """
    ?start: sum
          | NAME -> memory
    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub
    ?product: atom
            | product "*" atom  -> mul
            | product "/" atom  -> div
    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | "(" sum ")"
    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS
    %ignore WS
"""

parser_lark = Lark(grammar)

def lark_tree_to_d3(tree):
    """
    Convierte un árbol de Lark a un formato compatible con D3.js.
    """
    if isinstance(tree, Tree):
        return {
            "name": tree.data,
            "children": [lark_tree_to_d3(child) for child in tree.children]
        }
    else:
        # Nodo hoja (un token)
        return {"name": str(tree)}


app = Flask(__name__)

# Lexer y parser
tokens = ('NUMBER', 'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'LPAREN', 'RPAREN')

t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_ignore = ' \t'


def t_NUMBER(t):
    r'\d+\.\d*|\d+'
    t.value = float(t.value) if '.' in t.value else int(t.value)  
    return t




def t_error(t):
    t.lexer.skip(1)


lexer = lex.lex()

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('nonassoc', 'UMINUS'),
)


class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression MULTIPLY expression
                  | expression DIVIDE expression'''
    p[0] = Node(p[2], p[1], p[3])


def p_expression_number(p):
    'expression : NUMBER'
    p[0] = Node(p[1])


def p_expression_parens(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]


def p_expression_uminus(p):
    'expression : MINUS expression %prec UMINUS'
    p[0] = Node('-', None, p[2])


def p_error(p):
    pass

def categorize_token(token):
    if token.isdigit() or ('.' in token and token.replace('.', '', 1).isdigit()):
        return "Número Decimal" if '.' in token else "Número Entero"
    elif token in {'+', '-', '*', '/'}:
        return "Operador"
    elif token in {'(', ')'}:
        return "Paréntesis"
    return "Desconocido"

def classify_expression(expression):
    classifications = []
    for char in expression:
        if char.isdigit():
            classifications.append(f"'{char}': Entero")
        elif char == '.':
            classifications.append(f"'{char}': Decimal")
        elif char in '+-*/()':
            classifications.append(f"'{char}': Operador")
        elif char == 'M':
            classifications.append(f"'{char}': MS")
        else:
            classifications.append(f"'{char}': Desconocido")
    return classifications



parser = yacc.yacc()

 
memory_store = None
input_buffer = ""

def evaluate(node):
    if isinstance(node.value, (int, float)):  
        return node.value
    elif node.value == '+':
        return evaluate(node.left) + evaluate(node.right)
    elif node.value == '-':
        return evaluate(node.left) - evaluate(node.right)
    elif node.value == '*':
        return evaluate(node.left) * evaluate(node.right)
    elif node.value == '/':
        return evaluate(node.left) / evaluate(node.right)



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    global input_buffer, memory_store
    data = request.json
    action = data.get("action", "")
    expression = data.get("expression", "")

    try:
        if action == "=" and expression:
            tree = parser_lark.parse(expression)
            result = evaluate(parser.parse(expression))
            memory_store = result

            response = {
                "expression": expression,
                "result": result,
                "classifications": classify_expression(expression),
                "tree": lark_tree_to_d3(tree), 
            }
        else:
            response = {
                "expression": "",
                "result": None,
                "classifications": [],
                "tree": None,
            }
    except Exception as e:
        response = {
            "expression": expression if expression else input_buffer,
            "result": "Error",
            "error": str(e),
            "classifications": [],
            "tree": None,
        }

    return jsonify(response)





if __name__ == '__main__':
    app.run(debug=True)
