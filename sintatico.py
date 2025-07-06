# sintatico.py
from tokens import Token, TokenType
from nodes import (ProgramNode, FuncDeclNode, VarDeclNode, AssignNode, ReturnNode, 
                   FuncCallStmtNode, BinaryOpNode, TypeNode, IdentifierNode, 
                   NumberNode, StringNode, CharNode)

# ... (todo o código das classes SyntaxError e Parser permanece o mesmo) ...
class SyntaxError(Exception):
    def __init__(self, message, linha=None):
        super().__init__(message)
        self.linha = linha
    def __str__(self):
        return f"Syntax Error at line {self.linha}: {super().__str__()}" if self.linha else f"Syntax Error: {super().__str__()}"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else Token(TokenType.EOF, "EOF", -1)

    def _advance(self):
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else Token(TokenType.EOF, "EOF", -1)

    def _consume(self, expected_type, expected_value=None):
        token = self.current_token
        if token.tipo == TokenType.EOF:
            expected_descr = f"'{expected_value}' ({expected_type.value})" if expected_value else expected_type.value
            raise SyntaxError(f"Unexpected end of input. Expected {expected_descr}.")
        linha = token.linha
        if token.tipo != expected_type or (expected_value and token.valor != expected_value):
            raise SyntaxError(f"Expected '{expected_value or expected_type.value}', got '{token.valor}'", linha)
        self._advance()
        return token

    def parse_programa(self):
        func_declaration = self.parse_declaracao_funcao()
        if self.current_token.tipo != TokenType.EOF:
             raise SyntaxError(f"Unexpected token '{self.current_token.valor}' after program completion.", self.current_token.linha)
        return ProgramNode([func_declaration])

    def parse_declaracao_funcao(self):
        type_node = self.parse_tipo()
        name_token = self._consume(TokenType.IDENTIFICADOR)
        self._consume(TokenType.SIMBOLO, '(')
        self._consume(TokenType.SIMBOLO, ')')
        self._consume(TokenType.SIMBOLO, '{')
        body = self.parse_lista_comandos()
        self._consume(TokenType.SIMBOLO, '}')
        return FuncDeclNode(type_node, name_token, body)

    def parse_tipo(self):
        token = self.current_token
        if token.tipo == TokenType.PALAVRA_RESERVADA and token.valor in {"int", "real", "char"}:
            self._consume(TokenType.PALAVRA_RESERVADA, token.valor)
            return TypeNode(token)
        raise SyntaxError(f"Expected type (int, real, char), got '{token.valor}'", token.linha)

    def parse_lista_comandos(self):
        comandos = []
        while self.current_token.valor != '}':
            comandos.append(self.parse_comando())
        return comandos

    def parse_comando(self):
        token = self.current_token
        if token.valor == "return":
            return self.parse_comando_retorno()
        if token.valor in {"int", "real", "char"}:
            return self.parse_declaracao_variavel()
        
        if token.tipo == TokenType.IDENTIFICADOR:
            if self.pos + 1 < len(self.tokens):
                next_token = self.tokens[self.pos+1]
                if next_token.valor == '=':
                    return self.parse_atribuicao()
                if next_token.valor == '(':
                    return self.parse_chamada_funcao_stmt()
        
        raise SyntaxError(f"Unexpected token '{token.valor}' to start a command.", token.linha)

    def parse_declaracao_variavel(self):
        type_node = self.parse_tipo()
        var_token = self._consume(TokenType.IDENTIFICADOR)
        expr_node = None
        if self.current_token.valor == '=':
            self._consume(TokenType.SIMBOLO, '=')
            expr_node = self.parse_expressao()
        self._consume(TokenType.SIMBOLO, ';')
        return VarDeclNode(type_node, var_token, expr_node)

    def parse_atribuicao(self):
        var_token = self._consume(TokenType.IDENTIFICADOR)
        self._consume(TokenType.SIMBOLO, '=')
        expr_node = self.parse_expressao()
        self._consume(TokenType.SIMBOLO, ';')
        return AssignNode(var_token, expr_node)

    def parse_comando_retorno(self):
        self._consume(TokenType.PALAVRA_RESERVADA, "return")
        expr_node = self.parse_expressao()
        self._consume(TokenType.SIMBOLO, ';')
        return ReturnNode(expr_node)
        
    def parse_chamada_funcao_stmt(self):
        name_token = self._consume(TokenType.IDENTIFICADOR)
        self._consume(TokenType.SIMBOLO, '(')
        arg_list = []
        if self.current_token.valor != ')':
            arg_list = self.parse_lista_argumentos()
        self._consume(TokenType.SIMBOLO, ')')
        self._consume(TokenType.SIMBOLO, ';')
        return FuncCallStmtNode(name_token, arg_list)

    def parse_lista_argumentos(self):
        return [self.parse_expressao()]

    def parse_expressao(self):
        node = self.parse_termo()
        while self.current_token.valor == '+':
            op_token = self._consume(TokenType.SIMBOLO, '+')
            right = self.parse_termo()
            node = BinaryOpNode(left=node, op_token=op_token, right=right)
        return node

    def parse_termo(self):
        token = self.current_token
        if token.tipo == TokenType.IDENTIFICADOR:
            self._advance()
            return IdentifierNode(token)
        if token.tipo == TokenType.NUMERO or token.tipo == TokenType.REAL:
            self._advance()
            return NumberNode(token)
        if token.tipo == TokenType.STRING:
            self._advance()
            return StringNode(token)
        if token.tipo == TokenType.CARACTERE:
            self._advance()
            return CharNode(token)
        raise SyntaxError(f"Expected identifier or literal, got '{token.valor}'", token.linha)


def print_ast(node, indent=""):
    node_repr = indent + node.__class__.__name__
    if hasattr(node, 'name'): node_repr += f" (Name: {node.name})"
    if hasattr(node, 'var_name'): node_repr += f" (VarName: {node.var_name})"
    if hasattr(node, 'value'): node_repr += f" (Value: {node.value})"
    if hasattr(node, 'op_token') and node.op_token: node_repr += f" (Op: {node.op_token.valor})"
    print(node_repr)
    new_indent = indent + "  "
    child_attrs = ['type_node', 'declarations', 'body', 'expr_node', 'arg_list', 'left', 'right']
    for attr_name in child_attrs:
        if hasattr(node, attr_name):
            child_or_children = getattr(node, attr_name)
            if child_or_children is None: continue
            print(new_indent + f"({attr_name}) ->")
            if isinstance(child_or_children, list):
                for child in child_or_children:
                    print_ast(child, new_indent + "  ")
            else:
                print_ast(child_or_children, new_indent + "  ")

# --- Bloco Principal de Execução ---
if __name__ == "__main__":
    import subprocess
    from analisador import analisar_arquivo
    from semantico import SemanticAnalyzer
    from otimizador import Optimizer
    from gerador_codigo import CodeGenerator
    
    nome_arquivo = "teste.txt"
    print(f"--- Iniciando Compilação do Arquivo: {nome_arquivo} ---\n")

    try:
        # FASE 1: ANÁLISE LÉXICA
        print("--- Fase 1: Análise Léxica ---")
        tokens = analisar_arquivo(nome_arquivo)
        if not tokens: exit(1)
        print("Análise léxica concluída.\n")

        # FASE 2: ANÁLISE SINTÁTICA E CONSTRUÇÃO DA AST
        print("--- Fase 2: Análise Sintática e Construção da AST ---")
        parser = Parser(tokens)
        ast_root = parser.parse_programa()
        print("Análise sintática e construção da AST concluídas.\n")
        
        # FASE 3: ANÁLISE SEMÂNTICA
        print("--- Fase 3: Análise Semântica ---")
        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.visit(ast_root)
        print("Análise semântica concluída com sucesso!\n")

        # FASE 4: OTIMIZAÇÃO
        print("--- Fase 4: Otimização (Constant Folding) ---")
        optimizer = Optimizer()
        optimized_ast = optimizer.visit(ast_root)
        print("Otimização concluída.\n")
        print("--- AST Otimizada ---")
        print_ast(optimized_ast)
        print("---------------------\n")

        # FASE 5: GERAÇÃO DE CÓDIGO
        print("--- Fase 5: Geração de Código (Transpilando para Python) ---")
        code_gen = CodeGenerator()
        python_code = code_gen.visit(optimized_ast)
        
        output_filename = "output.py"
        with open(output_filename, "w") as f:
            f.write(python_code)
            # Adiciona a chamada à função principal se ela existir
            f.write("\nif __name__ == '__main__':\n    main()\n")
        print(f"Código Python gerado com sucesso no arquivo: {output_filename}\n")

        # FASE 6: EXECUÇÃO DO CÓDIGO GERADO
        print(f"--- Executando o script Python gerado ({output_filename})... ---")
        subprocess.run(["python3", output_filename])
        print("------------------------------------------------------")

    except (SyntaxError, NameError) as e:
        print(f"\nERRO DE COMPILAÇÃO: {e}")
    except Exception as e:
        import traceback
        print(f"\n--- ERRO INESPERADO (RELATÓRIO DE DEPURAÇÃO) ---")
        print(f"Tipo do Erro: {type(e)}")
        print(f"Mensagem do Erro: '{e}'")
        print("\n--- Rastreamento de Pilha (Traceback) ---")
        traceback.print_exc()
        print("--------------------------------------------")