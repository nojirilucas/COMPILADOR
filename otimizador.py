# otimizador.py
import nodes

class Optimizer:
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        # Para nós que não têm um método 'visit' específico,
        # simplesmente chamamos a visita em seus filhos.
        for attr, value in node.__dict__.items():
            if isinstance(value, list):
                new_list = []
                for item in value:
                    if isinstance(item, nodes.Node):
                        new_list.append(self.visit(item))
                    else:
                        new_list.append(item)
                setattr(node, attr, new_list)
            elif isinstance(value, nodes.Node):
                setattr(node, attr, self.visit(value))
        return node

    def visit_BinaryOpNode(self, node):
        # Visita os filhos primeiro, caso eles também possam ser otimizados
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)

        # A mágica do Constant Folding acontece aqui
        if isinstance(node.left, nodes.NumberNode) and isinstance(node.right, nodes.NumberNode):
            print(f"Otimização: Expressão '{node.left.value} {node.op_token.valor} {node.right.value}' será calculada agora.")
            left_val = float(node.left.value)
            right_val = float(node.right.value)
            
            result = 0
            if node.op_token.valor == '+': result = left_val + right_val
            elif node.op_token.valor == '-': result = left_val - right_val
            elif node.op_token.valor == '*': result = left_val * right_val
            elif node.op_token.valor == '/': result = left_val / right_val
            
            # Se o resultado for inteiro, mantenha como inteiro
            if result == int(result):
                result = int(result)

            print(f"Otimização: Resultado calculado como '{result}'.")
            # Substitui este nó de operação por um simples nó de número
            return nodes.NumberNode(token=None, value=str(result))
        
        # Se não puder otimizar, retorna o nó original
        return node