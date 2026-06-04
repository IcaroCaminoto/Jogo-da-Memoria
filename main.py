import pygame
from jogo_memoria import JogoMemoria
# 1. IMPORTAR AS FUNÇÕES DO SEU FICHEIRO loguin.py
from loguin import tela_login, salvar_dados

pygame.init()

# Tela
LARGURA = 1000
ALTURA = 700
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo da Memória")

# Fonte
fonte = pygame.font.SysFont(None, 40)
fonte_titulo = pygame.font.SysFont(None, 72)
fonte_info = pygame.font.SysFont(None, 30)

BRANCO = (255, 255, 255)
CINZA = (200, 200, 200)
VERDE = (0, 200, 0)
AMARELO = (255, 255, 0)
VERMELHO = (200, 0, 0)

# 2. CHAMAR A TELA DE LOGIN ANTES DO MENU E GUARDAR O NOME
nome_jogador = tela_login(tela)

# Jogo
estado = "menu"
nivel_escolhido = "facil"
jogo = None

# Grid configurações por dificuldade
GRID_CONFIG = {
    #  nivel    : (colunas, tam_carta, margem)
    "facil"  : (4,  100, 12),   # 16 cartas  → 4×4
    "medio"  : (6,  90,  10),   # 36 cartas  → 6×6
    "dificil": (8,  72,   8),   # 48 cartas  → 8×6
}

COLUNAS = 4
TAM     = 100
MARGEM  = 12

# Área útil reservada para o HUD (pontos / vidas) no topo
HUD_ALTURA = 60

clock = pygame.time.Clock()
rodando = True

# Helpers de layout
def calcular_offset(num_cartas):
    """Retorna (offset_x, offset_y) para centralizar o grid na tela."""
    linhas = (num_cartas + COLUNAS - 1) // COLUNAS
    grid_largura = COLUNAS * (TAM + MARGEM) - MARGEM
    grid_altura  = linhas  * (TAM + MARGEM) - MARGEM
    offset_x = (LARGURA - grid_largura) // 2
    offset_y = HUD_ALTURA + (ALTURA - HUD_ALTURA - grid_altura) // 2
    return offset_x, offset_y

def pos_carta(i):
    """Retorna o pygame.Rect da carta de índice i."""
    col   = i % COLUNAS
    linha = i // COLUNAS
    ox, oy = calcular_offset(len(jogo.cartas))
    x = ox + col   * (TAM + MARGEM)
    y = oy + linha * (TAM + MARGEM)
    return pygame.Rect(x, y, TAM, TAM)

# Desenho do jogo
def desenhar():
    tela.fill((30, 30, 30))

    # Fonte proporcional ao tamanho da carta
    fonte_carta = pygame.font.SysFont(None, max(20, TAM // 3))

    for i in range(len(jogo.cartas)):
        rect = pos_carta(i)

        if jogo.reveladas[i]:
            pygame.draw.rect(tela, (0, 200, 0), rect, border_radius=6)
            texto = fonte_carta.render(str(jogo.cartas[i]), True, (0, 0, 0))
            tela.blit(texto, (rect.x + rect.width  // 2 - texto.get_width()  // 2,
                              rect.y + rect.height // 2 - texto.get_height() // 2))
        else:
            pygame.draw.rect(tela, (200, 0, 0), rect, border_radius=6)

    # HUD (Mostra agora também o nome do jogador)
    texto_nome   = fonte.render(f"Jogador: {nome_jogador}", True, BRANCO)
    texto_pontos = fonte.render(f"Pontos: {jogo.pontuacao()}", True, BRANCO)
    texto_vida   = fonte.render(f"Vidas: {jogo.vida_total()}",  True, BRANCO)
    
    tela.blit(texto_nome,   (10, 10))
    tela.blit(texto_pontos, (10, 40))
    tela.blit(texto_vida,   (10, 70))

    pygame.display.flip()

# Tela inicial
def desenhar_tela_inicial():
    tela.fill((20, 20, 40))

    titulo = fonte_titulo.render("Jogo da Memória", True, BRANCO)
    tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 80))

    infos = [
        "Encontre todos os pares de cartas!",
        "Você começa com 10 vidas.",
        "Cada erro remove 1 vida.",
        "Cada par encontrado vale 100 pontos.",
    ]
    for i, linha in enumerate(infos):
        texto = fonte_info.render(linha, True, BRANCO)
        tela.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 200 + i * 35))

    botoes = {
        "facil"  : {"label": "Fácil",   "cor": VERDE,   "x": 160},
        "medio"  : {"label": "Médio",   "cor": AMARELO, "x": 410},
        "dificil": {"label": "Difícil", "cor": VERMELHO,"x": 660},
    }
    for nivel, dados in botoes.items():
        rect = pygame.Rect(dados["x"], 440, 180, 60)
        pygame.draw.rect(tela, dados["cor"], rect, border_radius=10)
        texto = fonte.render(dados["label"], True, BRANCO)
        tela.blit(texto, (rect.x + rect.width  // 2 - texto.get_width()  // 2,
                          rect.y + rect.height // 2 - texto.get_height() // 2))

    pygame.display.flip()

def verificar_clique_botao(pos):
    botoes_rect = {
        "facil"  : pygame.Rect(160, 440, 180, 60),
        "medio"  : pygame.Rect(410, 440, 180, 60),
        "dificil": pygame.Rect(660, 440, 180, 60),
    }
    for nivel, rect in botoes_rect.items():
        if rect.collidepoint(pos):
            return nivel
    return None

# Clique nas cartas
def clique(pos):
    for i in range(len(jogo.cartas)):
        if pos_carta(i).collidepoint(pos):
            jogo.selecionar(i)

# Loop principal
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if estado == "menu":
                nivel = verificar_clique_botao(pygame.mouse.get_pos())
                if nivel:
                    nivel_escolhido = nivel

                    # ── Aplica configuração de grid para o nível escolhido ──
                    COLUNAS, TAM, MARGEM = GRID_CONFIG[nivel_escolhido]

                    jogo = JogoMemoria(nivel_escolhido)
                    estado = "jogando"

            elif estado == "jogando":
                clique(pygame.mouse.get_pos())

    if estado == "menu":
        desenhar_tela_inicial()

    elif estado == "jogando":
        desenhar()

        if len(jogo.selecionadas) == 2:
            pygame.time.delay(500)
            jogo.verificar()

        # 3. GRAVAR OS DADOS AO VENCER OU PERDER
        if jogo.venceu():
            print("VOCÊ VENCEU!")
            salvar_dados(nome_jogador, nivel_escolhido, jogo.pontuacao())
            pygame.time.delay(2000)
            rodando = False

        if jogo.perdeu():
            print("VOCÊ PERDEU!")
            salvar_dados(nome_jogador, nivel_escolhido, jogo.pontuacao())
            pygame.time.delay(2000)
            rodando = False

    clock.tick(60)

pygame.quit()