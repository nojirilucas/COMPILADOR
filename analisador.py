# analisador.py
from tokens import Token, TokenType

palavras_reservadas = {"int", "real", "char", "return"}

def analisar_linha(linha, num_linha):
    tokens = []
    i = 0
    while i < len(linha):
        c = linha[i]

        if c.isspace():
            i += 1
            continue

        # Comentários de linha (padrão //)
        if c == '/' and i + 1 < len(linha) and linha[i+1] == '/':
            # Comentário vai até o fim da linha, podemos parar de analisar
            break

        # Identificadores e palavras reservadas
        if c.isalpha() or c == '_':
            lexema = ""
            while i < len(linha) and (linha[i].isalnum() or linha[i] == '_'):
                lexema += linha[i]
                i += 1
            tipo = TokenType.PALAVRA_RESERVADA if lexema in palavras_reservadas else TokenType.IDENTIFICADOR
            tokens.append(Token(tipo, lexema, num_linha))
            continue

        # Números inteiros ou reais
        elif c.isdigit():
            num = ""
            ponto = False
            while i < len(linha) and (linha[i].isdigit() or (linha[i] == '.' and not ponto)):
                if linha[i] == '.':
                    ponto = True
                num += linha[i]
                i += 1
            tipo = TokenType.REAL if ponto else TokenType.NUMERO
            tokens.append(Token(tipo, num, num_linha))
            continue

        # Strings
        elif c == '"':
            i += 1
            str_val = ""
            while i < len(linha) and linha[i] != '"':
                str_val += linha[i]
                i += 1
            if i < len(linha) and linha[i] == '"':
                i += 1
                tokens.append(Token(TokenType.STRING, str_val, num_linha))
            else:
                tokens.append(Token(TokenType.ERRO, f"String não terminada: {str_val}", num_linha))
            continue

        # Caracteres
        elif c == "'":
            if i + 2 < len(linha) and linha[i+2] == "'":
                tokens.append(Token(TokenType.CARACTERE, linha[i+1], num_linha))
                i += 3
            else:
                tokens.append(Token(TokenType.ERRO, linha[i:], num_linha))
                break
            continue

        # Símbolos
        elif c in "();{}=+":
            tokens.append(Token(TokenType.SIMBOLO, c, num_linha))
            i += 1
            continue

        else:
            tokens.append(Token(TokenType.ERRO, c, num_linha))
            i += 1

    return tokens

def analisar_arquivo(nome_arquivo):
    try:
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            linhas = f.readlines()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{nome_arquivo}' não encontrado.")
        return None

    todos_tokens = []
    for num, linha in enumerate(linhas, start=1):
        tokens = analisar_linha(linha.strip(), num)
        todos_tokens.extend(tokens)

    return todos_tokens