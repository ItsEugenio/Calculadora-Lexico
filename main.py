from flask import Flask, request, jsonify, render_template
import ply.lex as lex
import ply.yacc as yacc

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
    r'\d+'
    t.value = int(t.value)
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


parser = yacc.yacc()

 
memory_store = None
input_buffer = ""

def evaluate(node):
    if isinstance(node.value, int):
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
    try:
        if action == "borrar":
            if input_buffer:
                input_buffer = input_buffer[:-1]
        elif action == "limpiar":
            input_buffer = ""
            memory_store = None
        elif action == "MS":
            if memory_store is not None:
                input_buffer += str(memory_store)
            else:
                return jsonify({
                    "expression": input_buffer,
                    "result": "No hay valor en memoria"
                })
        else:
            input_buffer += action

        if input_buffer:
            result = parser.parse(input_buffer)
            if result:
                memory_store = evaluate(result)
                response = {
                    "expression": input_buffer,
                    "result": memory_store,
                }
            else:
                response = {
                    "expression": input_buffer,
                    "result": None,
                }
        else:
            response = {
                "expression": "",
                "result": None,
            }
    except Exception as e:
        response = {
            "expression": input_buffer,
            "result": "Error",
            "error": str(e),
        }

    return jsonify(response)





if __name__ == '__main__':
    app.run(debug=True)
