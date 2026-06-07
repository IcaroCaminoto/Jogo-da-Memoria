import pygame
import json
from datetime import datetime
import os
import math
import sys


# ------------------------------------------------------------
# BACK - HALL DA FAMA | LÓGICA DE DADOS E FUNÇÕES AUXILIARES
# ------------------------------------------------------------

def salvar_dados_json(nome, nivel, pontuacao):
    """Salva os dados da partida em um arquivo JSON."""
    arquivo = 'pontuacoes.json'
    dados = []
    
    if os.path.exists(arquivo):
        with open(arquivo, 'r', encoding='utf-8') as f:
            try:
                dados = json.load(f)
            except json.JSONDecodeError:
                dados = []
                
    novo_registro = {
        "nome": nome,
        "horario": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "nivel": nivel,
        "pontuacao": pontuacao
    }
    
    dados.append(novo_registro)
    
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def carregar_ranking_melhores():
    """Lê o JSON, ordena pelas maiores pontuações e retorna os 3 melhores."""
    arquivo = 'pontuacoes.json'
    if not os.path.exists(arquivo):
        return []
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
    except Exception:
        return []

    # Ordena a lista de dicionários baseada na chave 'pontuacao' em ordem decrescente
    dados_ordenados = sorted(dados, key=lambda x: x.get('pontuacao', 0), reverse=True)
    return dados_ordenados[:3] # Pega apenas o Top 3

#--------------------------------------------------------
# BACK - PERSISTÊNCIA DE DADOS E RANKING COMPLETO
#--------------------------------------------------------

RANKING_ARQUIVO = "ranking.txt"

def salvar_resultado_txt(nome: str, data: str, hora: str, pontuacao: int, tempo: int, d_id: str, res: str):
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

def carregar_ranking_completo():
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

# ------------------------------------------------
# FRONTEND - TELA DE LOGIN COM RANKING
# ------------------------------------------------

def desenhar_fundo_cassino(tela, largura, altura):
    """Desenha um gradiente verde escuro lembrando uma mesa de feltro premium."""
    cor_topo = (15, 60, 30)
    cor_base = (5, 20, 10)
    for y in range(altura):
        r = cor_topo[0] + (cor_base[0] - cor_topo[0]) * y // altura
        g = cor_topo[1] + (cor_base[1] - cor_topo[1]) * y // altura
        b = cor_topo[2] + (cor_base[2] - cor_topo[2]) * y // altura
        pygame.draw.line(tela, (r, g, b), (0, y), (largura, y))

def tela_login(tela):
    """Exibe a tela com Ranking e input para o jogador digitar seu nome."""
    pygame.font.init()
    
    largura = 1000
    altura = 700
    
    # Fontes premium
    fonte_nome = pygame.font.SysFont("georgia", 40)
    fonte_titulo = pygame.font.SysFont("georgia", 70, bold=True)
    fonte_sub = pygame.font.SysFont("georgia", 50, italic=True)
    fonte_instrucao = pygame.font.SysFont("georgia", 28)
    fonte_ranking = pygame.font.SysFont("georgia", 32, bold=True)
    fonte_ranking_tit = pygame.font.SysFont("georgia", 36, bold=True)
    
    nome = ""
    ativo = True
    
    # Configurações da caixa de texto (movida mais para baixo)
    caixa_largura = 400
    caixa_altura = 60
    caixa_texto = pygame.Rect((largura - caixa_largura) // 2, 500, caixa_largura, caixa_altura)
    
    # Paleta de Cores
    COR_DOURADA = (218, 165, 32)
    COR_CAIXA_FUNDO = (10, 30, 15)
    BRANCO = (255, 255, 255)
    
    # Cores do Pódio
    CORES_PODIO = [
        (255, 215, 0),   # 1º Ouro
        (192, 192, 192), # 2º Prata
        (205, 127, 50)   # 3º Bronze
    ]
    
    clock = pygame.time.Clock()
    
    # Carrega o ranking uma vez ao abrir a tela
    top3 = carregar_ranking_melhores()
    
    # PAINEL DE RANKING (Hall da Fama)
    painel_rank_w, painel_rank_h = 500, 220
    painel_rank_x = (largura - painel_rank_w) // 2
    painel_rank_y = 180

    # Botão para ver o histórico do rankking
    largura_botao_hist = 280
    altura_botao_hist = 45
    rect_botao_hist = pygame.Rect(
        (largura - largura_botao_hist) // 2,
        painel_rank_y + painel_rank_h + 10,
        largura_botao_hist,
        altura_botao_hist
    )

    while ativo:
        tempo = pygame.time.get_ticks()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()  # Encerra o programa completamente
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    if nome.strip() != "":
                        return nome.strip()
                elif evento.key == pygame.K_BACKSPACE:
                    nome = nome[:-1]
                else:
                    if len(nome) < 14:
                        nome += evento.unicode
                
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if rect_botao_hist.collidepoint(evento.pos):
                    desenhar_historico_completo(tela)

        # 1. Fundo luxuoso
        desenhar_fundo_cassino(tela, largura, altura)
        
        # 2. Textos do Título (Movidos mais para cima)
        titulo = fonte_titulo.render("Jogo da Memória", True, BRANCO)
        # Sombra no título
        tela.blit(fonte_titulo.render("Jogo da Memória", True, (0,0,0)), (largura // 2 - titulo.get_width() // 2 + 3, 43))
        tela.blit(titulo, (largura // 2 - titulo.get_width() // 2, 40))
        
        subtitulo = fonte_sub.render("Cards", True, COR_DOURADA)
        tela.blit(subtitulo, (largura // 2 - subtitulo.get_width() // 2, 100))
        
        # 3. PAINEL DE RANKING (Hall da Fama)
        # Trecho movido para antes do looping While
        
        # Fundo semi-transparente para o ranking
        sombra_rank = pygame.Surface((painel_rank_w, painel_rank_h), pygame.SRCALPHA)
        sombra_rank.fill((0, 0, 0, 100))
        tela.blit(sombra_rank, (painel_rank_x, painel_rank_y))
        pygame.draw.rect(tela, COR_DOURADA, (painel_rank_x, painel_rank_y, painel_rank_w, painel_rank_h), 2, border_radius=10)
        
        tit_rank = fonte_ranking_tit.render(" Hall da Fama ", True, COR_DOURADA)
        tela.blit(tit_rank, (largura // 2 - tit_rank.get_width() // 2, painel_rank_y + 15))
        
        # Desenhando os jogadores do Top 3
        if not top3:
            txt_vazio = fonte_instrucao.render("Nenhuma pontuação registrada ainda.", True, (150, 150, 150))
            tela.blit(txt_vazio, (largura // 2 - txt_vazio.get_width() // 2, painel_rank_y + 100))
        else:
            for i, jogador in enumerate(top3):
                cor_posicao = CORES_PODIO[i] if i < 3 else BRANCO
                y_pos = painel_rank_y + 70 + (i * 45)
                
                # Exemplo: "1º  Souza  ........................  600 pts"
                txt_pos = fonte_ranking.render(f"{i+1}º", True, cor_posicao)
                txt_nome = fonte_ranking.render(f"{jogador['nome'].upper()}", True, BRANCO)
                txt_pts = fonte_ranking.render(f"{jogador['pontuacao']} pts", True, cor_posicao)
                
                # Nível em tamanho menor
                txt_nivel = fonte_instrucao.render(f"({jogador['nivel']})", True, (180, 180, 180))
                
                tela.blit(txt_pos, (painel_rank_x + 30, y_pos))
                tela.blit(txt_nome, (painel_rank_x + 90, y_pos))
                tela.blit(txt_nivel, (painel_rank_x + 90 + txt_nome.get_width() + 10, y_pos + 4))
                tela.blit(txt_pts, (painel_rank_x + painel_rank_w - 30 - txt_pts.get_width(), y_pos))

        # 4. Label da caixa de texto
        txt_jogador = fonte_instrucao.render("Qual é o seu nome, jogador?", True, (200, 220, 200))
        tela.blit(txt_jogador, (largura // 2 - txt_jogador.get_width() // 2, 460))
        
        # 5. Caixa de texto
        pygame.draw.rect(tela, COR_CAIXA_FUNDO, caixa_texto, border_radius=8)
        pygame.draw.rect(tela, COR_DOURADA, caixa_texto, 2, border_radius=8)
        
        texto_surface = fonte_nome.render(nome, True, BRANCO)
        
        txt_x = caixa_texto.x + (caixa_texto.width - texto_surface.get_width()) // 2
        txt_y = caixa_texto.y + (caixa_texto.height - texto_surface.get_height()) // 2
        tela.blit(texto_surface, (txt_x, txt_y))
        
        # 6. Cursor Dourado Piscando
        if (tempo // 500) % 2 == 0:
            cursor_x = txt_x + texto_surface.get_width() + 4
            if nome == "":
                cursor_x = caixa_texto.centerx
            pygame.draw.line(tela, COR_DOURADA, (cursor_x, txt_y + 5), (cursor_x, txt_y + texto_surface.get_height() - 5), 3)
        
        # 7. Instrução para continuar (Efeito Pulsante)
        instrucao = fonte_instrucao.render("Pressione ENTER para jogar", True, BRANCO)
        alpha = int(150 + 105 * math.sin(tempo / 300))
        instrucao.set_alpha(alpha)
        tela.blit(instrucao, (largura // 2 - instrucao.get_width() // 2, 600))
        
        #Desenhando botão para ver o histórico completo
        mouse_pos = pygame.mouse.get_pos()
        if rect_botao_hist.collidepoint(mouse_pos):
            cor_fundo_botao = (40, 40, 40)
        else:
            cor_fundo_botao = (20, 20, 20)
        
        pygame.draw.rect(tela, cor_fundo_botao, rect_botao_hist, border_radius=8)
        pygame.draw.rect(tela, COR_DOURADA, rect_botao_hist, 2, border_radius=8)

        txt_botao = fonte_instrucao.render("Ranking Completo", True, BRANCO)
        txt_btn_x = rect_botao_hist.x + (rect_botao_hist.width - txt_botao.get_width()) // 2
        txt_btn_y = rect_botao_hist.y + (rect_botao_hist.height - txt_botao.get_height()) // 2
        tela.blit(txt_botao, (txt_btn_x, txt_btn_y))

        pygame.display.flip()
        clock.tick(60)

# ------------------------------------------------
# FRONTEND - TELA DE HISTÓRICO E RANKING
# ------------------------------------------------

def desenhar_historico_completo(tela):
    """Exibe a tela secundária com o histórico completo em TXT"""
    largura = 1000
    altura = 700
    ativo = True
    clock = pygame.time.Clock()

    fonte_titulo = pygame.font.SysFont("georgia", 50, bold=True)
    fonte_texto = pygame.font.SysFont("georgia", 24)
    fonte_botao = pygame.font.SysFont("georgia", 28, bold=True)

    BRANCO = (255, 255, 255)
    COR_DOURADA = (218, 165, 32)
    COR_BOTAO = (150, 40, 40) # Vermelho escuro para o botão de voltar

    # Botão voltar
    rect_voltar = pygame.Rect(largura // 2 - 100, altura - 80, 200, 50)

    historico = carregar_ranking_completo()

    while ativo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            # Volta a tela de login (captura de clique no botão)
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if rect_voltar.collidepoint(evento.pos):
                    return
                
        desenhar_fundo_cassino(tela, largura, altura)

        tit = fonte_titulo.render("Histórico Completo de Partidas", True, COR_DOURADA)
        tela.blit(tit, (largura // 2 - tit.get_width() // 2, 30))

        cabecalho = fonte_texto.render(f"{'NOME':<15} | {'PONTOS':<8} | {'NÍVEL':<10} | {'DATA/HORA':<15}", True, BRANCO)
        tela.blit(cabecalho, (150, 120))
        pygame.draw.line(tela, COR_DOURADA, (150, 150), (850, 150), 2)

        # Listando os jogadores: limitado a 12 para nao ter que colocar barra de rolagem 
        y_pos = 170
        for i, jog in enumerate(historico[:12]):
            linha_texto = f"{jog['nome'][:12]:<15} | {jog['pontuacao']:<8} | {jog['dificuldade']:<10} | {jog['data']} {jog['hora']}"
            txt_surface = fonte_texto.render(linha_texto, True, (200, 220, 200))
            tela.blit(txt_surface, (150, y_pos))
            y_pos += 35

        # Desenha botão de "voltar"
        pygame.draw.rect(tela, COR_BOTAO, rect_voltar, border_radius=10)
        pygame.draw.rect(tela, COR_DOURADA, rect_voltar, 2, border_radius=10)
        txt_voltar = fonte_botao.render("VOLTAR", True, BRANCO)
        tela.blit(txt_voltar, (rect_voltar.centerx - txt_voltar.get_width() // 2, rect_voltar.centery - txt_voltar.get_height() // 2))
        
        pygame.display.flip()
        clock.tick(60)