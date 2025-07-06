# gerador_codigo.py
import nodes

class CodeGenerator:
    def __init__(self):
        self.indent_level = 0
        self.python_code = ""

    def _indent(self):
        return "    " * self.indent_level

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"Visita não implementada para o nó: {type(node).__name__}")

    def visit_list(self, nodes_list):
        for node in nodes_list:
            self.visit(node)
            
    def visit_ProgramNode(self, node):
        self.visit_list(node.declarations)
        return self.python_code

    def visit_FuncDeclNode(self, node):
        self.python_code += f"def {node.name}():\n"
        self.indent_level += 1
        self.visit_list(node.body)
        self.indent_level -= 1

    def visit_VarDeclNode(self, node):
        if node.expr_node:
            expr_code = self.visit(node.expr_node)
            self.python_code += f"{self._indent()}{node.var_name} = {expr_code}\n"
        else:
            self.python_code += f"{self._indent()}{node.var_name} = None\n"
            
    def visit_AssignNode(self, node):
        expr_code = self.visit(node.expr_node)
        self.python_code += f"{self._indent()}{node.var_name} = {expr_code}\n"
        
    def visit_FuncCallStmtNode(self, node):
        function_name_map = {
            'printf': 'print'
            # Se você adicionar outras funções (ex: 'scanf'), pode mapeá-las aqui
        }
        # Usa o nome mapeado se existir, senão, o nome original
        target_function_name = function_name_map.get(node.name, node.name)

        arg_code = ""
        if node.arg_list:
            arg_code = self.visit(node.arg_list[0])
        self.python_code += f"{self._indent()}{target_function_name}({arg_code})\n"

    def visit_ReturnNode(self, node):
        expr_code = self.visit(node.expr_node)
        self.python_code += f"{self._indent()}return {expr_code}\n"

    def visit_BinaryOpNode(self, node):
        left_code = self.visit(node.left)
        right_code = self.visit(node.right)
        return f"({left_code} {node.op_token.valor} {right_code})"

    def visit_IdentifierNode(self, node):
        return node.value

    def visit_NumberNode(self, node):
        return node.value

    def visit_StringNode(self, node):
        return f'"{node.value}"'

    def visit_CharNode(self, node):
        return f'"{node.value}"'