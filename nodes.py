# nodes.py

class Node:
    """Nó base para todos os nós da AST."""
    def __repr__(self):
        return f"<{self.__class__.__name__}>"

class ProgramNode(Node):
    """Nó raiz da AST."""
    def __init__(self, declarations):
        self.declarations = declarations

class FuncDeclNode(Node):
    """Nó para declaração de função. Ex: int main() { ... }"""
    def __init__(self, type_node, name_token, body):
        self.type_node = type_node
        self.name = name_token.valor
        self.body = body

class VarDeclNode(Node):
    """Nó para declaração de variável. Ex: int x = 5;"""
    def __init__(self, type_node, var_token, expr_node=None):
        self.type_node = type_node
        self.var_name = var_token.valor
        self.expr_node = expr_node

class AssignNode(Node):
    """Nó para atribuição. Ex: x = 10;"""
    def __init__(self, var_token, expr_node):
        self.var_name = var_token.valor
        self.expr_node = expr_node
        
class ReturnNode(Node):
    """Nó para o comando return. Ex: return 0;"""
    def __init__(self, expr_node):
        self.expr_node = expr_node

class FuncCallStmtNode(Node):
    """Nó para uma chamada de função como um comando. Ex: printf("oi");"""
    def __init__(self, name_token, arg_list):
        self.name = name_token.valor
        self.arg_list = arg_list

class BinaryOpNode(Node):
    """Nó para uma operação binária. Ex: a + b"""
    def __init__(self, left, op_token, right):
        self.left = left
        self.op_token = op_token
        self.right = right

class TypeNode(Node):
    """Nó que representa um tipo. Ex: int"""
    def __init__(self, token):
        self.token = token
        self.value = token.valor

class IdentifierNode(Node):
    """Nó para um identificador. Ex: x"""
    def __init__(self, token):
        self.token = token
        self.value = token.valor

class NumberNode(Node):
    """Nó para um número (inteiro ou real)."""
    # ############################################################### #
    # A CORREÇÃO ESTÁ AQUI                                            #
    # Tornamos o construtor mais flexível.                            #
    # ############################################################### #
    def __init__(self, token=None, value=None):
        self.token = token
        # Usa o 'value' se for fornecido, senão extrai do 'token'
        self.value = value if value is not None else token.valor
        
class StringNode(Node):
    """Nó para uma string literal."""
    def __init__(self, token):
        self.token = token
        self.value = token.valor

class CharNode(Node):
    """Nó para um caractere literal."""
    def __init__(self, token):
        self.token = token
        self.value = token.valor