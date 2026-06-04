import pygame
import math
from jogo_memoria import JogoMemoria
from loguin import tela_login, salvar_dados

pygame.init()

# Tela
LARGURA = 1000
ALTURA = 700
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo da Memória")

# Fontes
fonte       = pygame.font.SysFont(None, 40)
fonte_titulo = pygame.font.SysFont(None, 72)
fonte_info  = pygame.font.SysFont(None, 30)
fonte_grande = pygame.font.SysFont(None, 100)

# Cores
BRANCO  = (255, 255, 255)
CINZA   = (200, 200, 200)
VERDE   = (0, 200, 0)
AMARELO = (255, 255, 0)
VERMELHO = (200, 0, 0)

# Tela de login
nome_jogador = tela_login(tela)

# Estado do jogo
estado = "menu"
nivel_escolhido = "facil"
jogo = None
timer_fim = 0          # tick em que venceu/perdeu (para animação)

# Grid configurações por dificuldade
GRID_CONFIG = {
    "facil"  : (4,  100, 12),
    "medio"  : (6,  90,  10),
    "dificil": (8,  72,   8),
}

COLUNAS = 4
TAM     = 100
MARGEM  = 12
HUD_ALTURA = 60

clock = pygame.time.Clock()
rodando = True

# ─── Helpers de layout ────────────────────────────────────────────────────────

def calcular_offset(num_cartas):
    linhas = (num_cartas + COLUNAS - 1) // COLUNAS
    grid_largura = COLUNAS * (TAM + MARGEM) - MARGEM
    grid_altura  = linhas  * (TAM + MARGEM) - MARGEM
    offset_x = (LARGURA - grid_largura) // 2
    offset_y = HUD_ALTURA + (ALTURA - HUD_ALTURA - grid_altura) // 2
    return offset_x, offset_y

def pos_carta(i):
    col   = i % COLUNAS
    linha = i // COLUNAS
    ox, oy = calcular_offset(len(jogo.cartas))
    x = ox + col   * (TAM + MARGEM)
    y = oy + linha * (TAM + MARGEM)
    return pygame.Rect(x, y, TAM, TAM)

# ─── Desenhos ─────────────────────────────────────────────────────────────────

def desenhar():
    tela.fill((30, 30, 30))
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

    texto_nome   = fonte.render(f"Jogador: {nome_jogador}", True, BRANCO)
    texto_pontos = fonte.render(f"Pontos: {jogo.pontuacao()}", True, BRANCO)
    texto_vida   = fonte.render(f"Vidas: {jogo.vida_total()}", True, BRANCO)
    tela.blit(texto_nome,   (10, 10))
    tela.blit(texto_pontos, (10, 40))
    tela.blit(texto_vida,   (10, 70))

    pygame.display.flip()


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
        "facil"  : {"label": "Fácil",   "cor": VERDE,    "x": 160},
        "medio"  : {"label": "Médio",   "cor": AMARELO,  "x": 410},
        "dificil": {"label": "Difícil", "cor": VERMELHO, "x": 660},
    }
    for nivel, dados in botoes.items():
        rect = pygame.Rect(dados["x"], 440, 180, 60)
        pygame.draw.rect(tela, dados["cor"], rect, border_radius=10)
        texto = fonte.render(dados["label"], True, BRANCO)
        tela.blit(texto, (rect.x + rect.width  // 2 - texto.get_width()  // 2,
                          rect.y + rect.height // 2 - texto.get_height() // 2))

    pygame.display.flip()


def _desenhar_painel_central(cor_fundo, cor_borda, titulo_txt, cor_titulo,
                              subtitulo_txt, pontuacao, tempo_ms):
    """
    Renderiza o painel semi-transparente de resultado no centro da tela.
    Usa uma animação de escala baseada no tempo decorrido desde o fim.
    Retorna o pygame.Rect do botão 'Jogar Novamente'.
    """
    # Animação de entrada (escala de 0 → 1 em 400 ms)
    prog = min(1.0, tempo_ms / 400)
    escala = 1 - (1 - prog) ** 3          # ease-out cúbico

    # Painel base
    pw, ph = 560, 340
    px = (LARGURA - pw) // 2
    py = (ALTURA  - ph) // 2

    # Superfície com alpha para overlay escuro
    overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    tela.blit(overlay, (0, 0))

    # Painel animado
    sw = int(pw * escala)
    sh = int(ph * escala)
    sx = (LARGURA - sw) // 2
    sy = (ALTURA  - sh) // 2

    painel = pygame.Surface((sw, sh), pygame.SRCALPHA)
    painel.fill((*cor_fundo, 230))
    tela.blit(painel, (sx, sy))
    pygame.draw.rect(tela, cor_borda, (sx, sy, sw, sh), 4, border_radius=16)

    if prog < 1.0:          # ainda animando — não desenha texto ainda
        pygame.display.flip()
        return None

    # ── Conteúdo do painel (só após animação completa) ──

    # Título grande
    t_titulo = fonte_grande.render(titulo_txt, True, cor_titulo)
    tela.blit(t_titulo, (LARGURA // 2 - t_titulo.get_width() // 2, py + 30))

    # Subtítulo
    t_sub = fonte_titulo.render(subtitulo_txt, True, BRANCO)
    tela.blit(t_sub, (LARGURA // 2 - t_sub.get_width() // 2, py + 130))

    # Pontuação
    t_pont = fonte.render(f"Pontuação final: {pontuacao} pontos", True, CINZA)
    tela.blit(t_pont, (LARGURA // 2 - t_pont.get_width() // 2, py + 200))

    # Botão "Jogar Novamente"
    btn_rect = pygame.Rect(LARGURA // 2 - 140, py + 260, 280, 55)
    mouse_pos = pygame.mouse.get_pos()
    cor_btn = (50, 180, 50) if btn_rect.collidepoint(mouse_pos) else (30, 130, 30)
    pygame.draw.rect(tela, cor_btn, btn_rect, border_radius=10)
    t_btn = fonte.render("Jogar Novamente", True, BRANCO)
    tela.blit(t_btn, (btn_rect.centerx - t_btn.get_width() // 2,
                      btn_rect.centery - t_btn.get_height() // 2))

    pygame.display.flip()
    return btn_rect


def desenhar_tela_vitoria(tempo_ms):
    """Tela de vitória — painel dourado/verde com estrelas."""
    desenhar()   # mantém o tabuleiro visível ao fundo

    # Partículas de estrela (simples, baseadas no tempo)
    for k in range(12):
        angulo = (tempo_ms / 800 + k * 30) * math.pi / 180
        r = 260 + 20 * math.sin(tempo_ms / 300 + k)
        sx = int(LARGURA // 2 + r * math.cos(angulo))
        sy = int(ALTURA  // 2 + r * math.sin(angulo))
        raio = 5 + int(3 * math.sin(tempo_ms / 200 + k))
        pygame.draw.circle(tela, AMARELO, (sx, sy), raio)

    return _desenhar_painel_central(
        cor_fundo   = (20, 60, 20),
        cor_borda   = (0, 220, 80),
        titulo_txt  = "VITÓRIA!",
        cor_titulo  = (80, 255, 120),
        subtitulo_txt = f"Parabéns, {nome_jogador}!",
        pontuacao   = jogo.pontuacao(),
        tempo_ms    = tempo_ms,
    )


def desenhar_tela_derrota(tempo_ms):
    """Tela de derrota — painel vermelho escuro."""
    desenhar()   # mantém o tabuleiro visível ao fundo

    # Efeito de tremor leve no início
    if tempo_ms < 600:
        shake = int(6 * math.sin(tempo_ms / 40) * max(0, 1 - tempo_ms / 600))
        tela.scroll(shake, 0)

    return _desenhar_painel_central(
        cor_fundo   = (60, 10, 10),
        cor_borda   = (220, 40, 40),
        titulo_txt  = "FIM DE JOGO",
        cor_titulo  = (255, 80, 80),
        subtitulo_txt = f"Tente de novo, {nome_jogador}!",
        pontuacao   = jogo.pontuacao(),
        tempo_ms    = tempo_ms,
    )


# ─── Helpers de interação ─────────────────────────────────────────────────────

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

def clique(pos):
    for i in range(len(jogo.cartas)):
        if pos_carta(i).collidepoint(pos):
            jogo.selecionar(i)

def reiniciar_jogo():
    """Volta ao menu principal e reseta o estado."""
    global estado, jogo, timer_fim, COLUNAS, TAM, MARGEM
    estado = "menu"
    jogo   = None
    timer_fim = 0
    COLUNAS, TAM, MARGEM = GRID_CONFIG["facil"]

# ─── Loop principal ───────────────────────────────────────────────────────────

while rodando:
    tempo_agora = pygame.time.get_ticks()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            if estado == "menu":
                nivel = verificar_clique_botao(pos)
                if nivel:
                    nivel_escolhido = nivel
                    COLUNAS, TAM, MARGEM = GRID_CONFIG[nivel_escolhido]
                    jogo = JogoMemoria(nivel_escolhido)
                    estado = "jogando"

            elif estado == "jogando":
                clique(pos)

            elif estado in ("vitoria", "derrota"):
                # Verifica clique no botão "Jogar Novamente" (rect calculado no desenho)
                # Como o botão está no painel, calculamos o rect manualmente
                py_painel = (ALTURA - 340) // 2
                btn_rect = pygame.Rect(LARGURA // 2 - 140, py_painel + 260, 280, 55)
                if btn_rect.collidepoint(pos):
                    reiniciar_jogo()

    # ── Renderização por estado ──

    if estado == "menu":
        desenhar_tela_inicial()

    elif estado == "jogando":
        desenhar()

        if len(jogo.selecionadas) == 2:
            pygame.time.delay(500)
            jogo.verificar()

        if jogo.venceu():
            salvar_dados(nome_jogador, nivel_escolhido, jogo.pontuacao())
            timer_fim = tempo_agora
            estado = "vitoria"

        elif jogo.perdeu():
            salvar_dados(nome_jogador, nivel_escolhido, jogo.pontuacao())
            timer_fim = tempo_agora
            estado = "derrota"

    elif estado == "vitoria":
        tempo_decorrido = tempo_agora - timer_fim
        desenhar_tela_vitoria(tempo_decorrido)

    elif estado == "derrota":
        tempo_decorrido = tempo_agora - timer_fim
        desenhar_tela_derrota(tempo_decorrido)

    clock.tick(60)

pygame.quit()