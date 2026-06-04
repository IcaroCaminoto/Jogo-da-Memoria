# --------------------------------------------------------
# ranking.py - Módulo de Persistência de Dados
# --------------------------------------------------------
import os

RANKING_ARQUIVO = "ranking.txt"

def salvar_resultado(nome: str, data: str, hora: str, pontuacao: int, tempo: int, d_id: str, res: str):
    """Salva o resultado do jogador de forma permanente em um arquivo de texto"""
    info_jogador = {
        "nome": nome,
        "data": data,
        "hora": hora,
        "pontuacao": pontuacao,
        "tempo": tempo,
        "dificuldade": d_id,
        "resultado": res
    }

    with open(RANKING_ARQUIVO, "a", encoding="utf-8") as arquivo:
        # BUG FIX: Gravando com ponto e vírgula para bater com o split da leitura
        linha = f"{info_jogador['nome']};{info_jogador['data']};{info_jogador['hora']};{info_jogador['pontuacao']};{info_jogador['tempo']};{info_jogador['dificuldade']};{info_jogador['resultado']}\n"
        arquivo.write(linha)
    print("Resultado salvo com sucesso!")

def carregar_ranking():
    """Lê o arquivo .txt, converte cada linha para Dicionário e retorna o top 5"""
    l_ranking = []

    if not os.path.exists(RANKING_ARQUIVO):
        return l_ranking
    
    with open(RANKING_ARQUIVO, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if not linha:
                continue
            nome, data, hora, pontuacao, tempo, dificuldade, resultado = linha.split(";")

            jogador = {
                "nome": nome,
                "data": data,
                "hora": hora,
                "pontuacao": int(pontuacao),
                "tempo": int(tempo),
                "dificuldade": dificuldade,
                "resultado": resultado
            }
            l_ranking.append(jogador)

    #BUG FIX: .sort() ordena a lista de forma embutida. Estava atribuindo a uma variável, o que resultava em None.
    l_ranking.sort(key=lambda x: x["pontuacao"], reverse=True)
    return l_ranking[:5]  # Retorna com segurança o top 5