# semantico.py
import nodes

class Symbol:
    """Representa um símbolo (variável ou função) na tabela."""
    def __init__(self, name, symbol_type):
        self.name = name
        self.type = symbol_type

class SymbolTable:
    """
    Gerencia uma pilha de escopos. Cada escopo é um dicionário de símbolos.
    """
    def __init__(self):
        self.scoped_tables = [{}]  # Começa com o escopo global (nível 0)

    @property
    def current_scope_level(self):
        return len(self.scoped_tables) - 1

    def enter_scope(self):
        """Entra em um novo escopo empilhando uma nova tabela."""
        self.scoped_tables.append({})
        print(f"INFO (Tabela de Símbolos): Entrando no escopo, nível {self.current_scope_level}")

    def leave_scope(self):
        """Sai do escopo atual desempilhando a tabela e seus símbolos."""
        print(f"INFO (Tabela de Símbolos): Saindo do escopo, voltando para o nível {self.current_scope_level - 1}")
        for name in self.scoped_tables[-1]:
            print(f"INFO (Tabela de Símbolos): Removendo símbolo '{name}' do escopo {self.current_scope_level}")
        self.scoped_tables.pop()

    def define(self, symbol):
        """Define um símbolo no escopo atual."""
        print(f"INFO (Tabela de Símbolos): Adicionando símbolo '{symbol.name}' (tipo: {symbol.type}) ao escopo {self.current_scope_level}")
        table = self.scoped_tables[-1]
        if symbol.name in table:
            raise NameError(f"Erro: Símbolo '{symbol.name}' já definido neste escopo.")
        table[symbol.name] = symbol

    def lookup(self, name):
        """Busca por um símbolo do escopo mais interno para o mais externo."""
        print(f"INFO (Tabela de Símbolos): Buscando por '{name}'...")
        for i in range(len(self.scoped_tables) - 1, -1, -1):
            table = self.scoped_tables[i]
            if name in table:
                return table[name]
        return None

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.symbol_table.define(Symbol('print', 'function'))

    def visit(self, node):
        # ############################################################### #
        # A CORREÇÃO ESTÁ AQUI                                            #
        # Verificamos se o nó é uma lista e a percorremos.                #
        # ############################################################### #
        if isinstance(node, list):
            for item in node:
                self.visit(item)
            return

        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for child in node.__dict__.values():
            if isinstance(child, list):
                for item in child:
                    if isinstance(item, nodes.Node):
                        self.visit(item)
            elif isinstance(child, nodes.Node):
                self.visit(child)
    
    def visit_FuncDeclNode(self, node):
        self.symbol_table.define(Symbol(node.name, 'function'))
        self.symbol_table.enter_scope()
        self.visit(node.body)  # Agora esta chamada funcionará corretamente
        self.symbol_table.leave_scope()

    def visit_VarDeclNode(self, node):
        if node.expr_node:
            self.visit(node.expr_node)
        var_symbol = Symbol(node.var_name, node.type_node.value)
        self.symbol_table.define(var_symbol)

    def visit_IdentifierNode(self, node):
        symbol = self.symbol_table.lookup(node.value)
        if not symbol:
            raise NameError(f"Erro: Variável '{node.value}' não foi declarada.")