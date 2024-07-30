from graphviz import Digraph

# Definición de la clase Nodo para construir el árbol sintáctico
class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

# Función para obtener la precedencia de los operadores de expresiones regulares
def get_precedence(c):
    precedences = {'(': 1, '|': 2, '.': 3, '?': 4, '*': 4, '+': 4, '^': 5}
    return precedences.get(c, 6)

# Función para formatear la expresión regular añadiendo operadores de concatenación explícitos
def format_regex(regex):
    all_operators = ['|', '?', '+', '*', '^']
    binary_operators = ['^', '|']
    res = ""

    i = 0
    while i < len(regex):
        c1 = regex[i]

        if i + 1 < len(regex):
            c2 = regex[i + 1]

            res += c1

            if (
                c1 != '(' and
                c2 != ')' and
                c2 not in all_operators and
                c1 not in binary_operators
            ):
                res += '.'

        i += 1

    res += regex[-1]
    return res

# Función para convertir la expresión regular de notación infija a notación postfija
def infix_to_postfix(regex):
    postfix = ""
    stack = []
    formatted_regex = format_regex(regex)
    steps = []

    i = 0
    while i < len(formatted_regex):
        c = formatted_regex[i]

        if c == '\\':
            # Manejo de caracteres escapados
            if i + 1 < len(formatted_regex):
                postfix += formatted_regex[i:i+2]
                i += 2
                continue
        elif c.isalnum() or c in '[]{}\\':
            postfix += c
        elif c == '(':
            stack.append(c)
        elif c == ')':
            while stack and stack[-1] != '(':
                postfix += stack.pop()
            if stack:
                stack.pop()
        else:
            while stack and get_precedence(stack[-1]) >= get_precedence(c):
                postfix += stack.pop()
            stack.append(c)

        steps.append((c, ''.join(stack), postfix))
        i += 1

    while stack:
        postfix += stack.pop()

    return postfix, steps

# Función para construir el árbol sintáctico a partir de la notación postfija
def construct_ast(postfix):
    stack = []
    for char in postfix:
        if char.isalnum() or char in '[]{}\\':
            stack.append(Node(char))
        elif char in '*+?':
            node = Node(char)
            if stack:
                node.right = stack.pop()
            stack.append(node)
        else:
            node = Node(char)
            if stack:
                node.right = stack.pop()
            if stack:
                node.left = stack.pop()
            stack.append(node)
    return stack[0] if stack else None

# Función para visualizar el árbol sintáctico usando graphviz
def visualize_ast(root, graph, count=[0]):
    if root is not None:
        node_id = str(count[0])
        graph.node(node_id, label=root.value.replace('\\', '\\\\').replace('|', '\\|'))
        count[0] += 1

        if root.left:
            left_id = visualize_ast(root.left, graph, count)
            graph.edge(node_id, left_id)

        if root.right:
            right_id = visualize_ast(root.right, graph, count)
            graph.edge(node_id, right_id)

        return node_id

# Función para procesar el archivo de entrada y generar los árboles sintácticos
def process_file(input_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        expression_count = 1
        for line in file:
            regex = line.strip()
            if regex:
                postfix, steps = infix_to_postfix(regex)
                print(f"Regex: {regex} -> Postfix: {postfix}")
                print("Steps:")
                for step in steps:
                    print(f"Token: {step[0]}, Stack: {step[1]}, Postfix: {step[2]}")
                print()

                ast_root = construct_ast(postfix)
                graph = Digraph()
                visualize_ast(ast_root, graph)
                graph.render(filename=f'ast_{expression_count}', format='png', cleanup=True)
                expression_count += 1

# Archivo de entrada
input_file = 'expresiones.txt'
process_file(input_file)
