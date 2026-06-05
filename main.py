import pygame
import math
import random
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
timer_fim = 0          
tempo_espera = 0     # Controle de tempo não-bloqueante para virar a carta
particulas = []      # Lista para guardar as estrelinhas da explosão

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

# ─── Funções de Efeitos Visuais ───────────────────────────────────────────────

def desenhar_fundo_cassino():
    cor_topo = (15, 60, 30)
    cor_base = (5, 20, 10)
    for y in range(ALTURA):
        r = cor_topo[0] + (cor_base[0] - cor_topo[0]) * y // ALTURA
        g = cor_topo[1] + (cor_base[1] - cor_topo[1]) * y // ALTURA
        b = cor_topo[2] + (cor_base[2] - cor_topo[2]) * y // ALTURA
        pygame.draw.line(tela, (r, g, b), (0, y), (LARGURA, y))

def desenhar_sombra(rect):
    sombra = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(sombra, (0, 0, 0, 130), sombra.get_rect(), border_radius=8)
    tela.blit(sombra, (rect.x + 6, rect.y + 6))

def gerar_explosao(i):
    """Gera partículas explodindo a partir do centro da carta 'i'."""
    rect = pos_carta(i)
    cx, cy = rect.center
    for _ in range(30): # 30 estrelinhas por carta
        dx = random.uniform(-8, 8)
        dy = random.uniform(-8, 8)
        vida_max = random.randint(30, 60)
        tamanho = random.randint(3, 8)
        cor = random.choice([AMARELO, BRANCO, (255, 215, 0), (255, 255, 150)])
        # [x, y, vel_x, vel_y, vida_atual, cor, tamanho, vida_maxima]
        particulas.append([cx, cy, dx, dy, vida_max, cor, tamanho, vida_max])

def atualizar_e_desenhar_particulas():
    """Anima e desenha as partículas das explosões."""
    for p in particulas[:]:
        p[0] += p[2] # Atualiza posição X
        p[1] += p[3] # Atualiza posição Y
        p[4] -= 1    # Diminui a vida
        
        p[3] += 0.3  # Adiciona gravidade (as estrelas caem com o tempo)
        
        if p[4] <= 0:
            particulas.remove(p)
        else:
            escala = p[4] / p[7]
            tam_atual = max(1, int(p[6] * escala)) # Encolhe com o tempo
            pygame.draw.circle(tela, p[5], (int(p[0]), int(p[1])), tam_atual)

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
    desenhar_fundo_cassino()
    fonte_carta = pygame.font.SysFont("georgia", max(25, TAM // 2), bold=True)

    for i in range(len(jogo.cartas)):
        rect = pos_carta(i)
        desenhar_sombra(rect)

        if jogo.reveladas[i] or (i in jogo.selecionadas):
            pygame.draw.rect(tela, BRANCO, rect, border_radius=8)
            pygame.draw.rect(tela, (220, 220, 220), rect.inflate(-10, -10), width=1, border_radius=6) 
            
            texto = fonte_carta.render(str(jogo.cartas[i]), True, (30, 30, 30))
            tela.blit(texto, (rect.x + rect.width  // 2 - texto.get_width()  // 2,
                              rect.y + rect.height // 2 - texto.get_height() // 2))
            
            fonte_mini = pygame.font.SysFont("georgia", max(12, TAM // 5), bold=True)
            texto_mini = fonte_mini.render(str(jogo.cartas[i]), True, (50, 50, 50))
            tela.blit(texto_mini, (rect.x + 8, rect.y + 6))
            texto_mini_inv = pygame.transform.rotate(texto_mini, 180)
            tela.blit(texto_mini_inv, (rect.right - 8 - texto_mini_inv.get_width(), rect.bottom - 6 - texto_mini_inv.get_height()))
        else:
            pygame.draw.rect(tela, BRANCO, rect, border_radius=8)
            cor_verso = (170, 20, 35) 
            rect_interno = rect.inflate(-16, -16)
            pygame.draw.rect(tela, cor_verso, rect_interno, border_radius=4)
            pygame.draw.rect(tela, (218, 165, 32), rect_interno, width=2, border_radius=4)
            pygame.draw.circle(tela, (218, 165, 32), rect.center, rect.width // 4, 2)
            pygame.draw.circle(tela, (218, 165, 32), rect.center, rect.width // 6, 1)

    texto_nome   = fonte.render(f"Jogador: {nome_jogador}", True, BRANCO)
    texto_pontos = fonte.render(f"Pontos: {jogo.pontuacao()}", True, BRANCO)
    texto_vida   = fonte.render(f"Vidas: {jogo.vida_total()}", True, BRANCO)
    
    tela.blit(fonte.render(f"Jogador: {nome_jogador}", True, (0,0,0)), (12, 12))
    tela.blit(fonte.render(f"Pontos: {jogo.pontuacao()}", True, (0,0,0)), (12, 42))
    tela.blit(fonte.render(f"Vidas: {jogo.vida_total()}", True, (0,0,0)), (12, 72))
    
    tela.blit(texto_nome,   (10, 10))
    tela.blit(texto_pontos, (10, 40))
    tela.blit(texto_vida,   (10, 70))


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

def _desenhar_painel_central(cor_fundo, cor_borda, titulo_txt, cor_titulo,
                             subtitulo_txt, pontuacao, tempo_ms):
    prog = min(1.0, tempo_ms / 400)
    escala = 1 - (1 - prog) ** 3          
    pw, ph = 560, 340
    px = (LARGURA - pw) // 2
    py = (ALTURA  - ph) // 2

    overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    tela.blit(overlay, (0, 0))

    sw = int(pw * escala)
    sh = int(ph * escala)
    sx = (LARGURA - sw) // 2
    sy = (ALTURA  - sh) // 2

    painel = pygame.Surface((sw, sh), pygame.SRCALPHA)
    painel.fill((*cor_fundo, 230))
    tela.blit(painel, (sx, sy))
    pygame.draw.rect(tela, cor_borda, (sx, sy, sw, sh), 4, border_radius=16)

    if prog < 1.0:          
        return None

    t_titulo = fonte_grande.render(titulo_txt, True, cor_titulo)
    tela.blit(t_titulo, (LARGURA // 2 - t_titulo.get_width() // 2, py + 30))
    t_sub = fonte_titulo.render(subtitulo_txt, True, BRANCO)
    tela.blit(t_sub, (LARGURA // 2 - t_sub.get_width() // 2, py + 130))
    t_pont = fonte.render(f"Pontuação final: {pontuacao} pontos", True, CINZA)
    tela.blit(t_pont, (LARGURA // 2 - t_pont.get_width() // 2, py + 200))

    btn_rect = pygame.Rect(LARGURA // 2 - 140, py + 260, 280, 55)
    mouse_pos = pygame.mouse.get_pos()
    cor_btn = (50, 180, 50) if btn_rect.collidepoint(mouse_pos) else (30, 130, 30)
    pygame.draw.rect(tela, cor_btn, btn_rect, border_radius=10)
    t_btn = fonte.render("Jogar Novamente", True, BRANCO)
    tela.blit(t_btn, (btn_rect.centerx - t_btn.get_width() // 2,
                      btn_rect.centery - t_btn.get_height() // 2))
    return btn_rect

def desenhar_tela_vitoria(tempo_ms):
    desenhar()   
    for k in range(12):
        angulo = (tempo_ms / 800 + k * 30) * math.pi / 180
        r = 260 + 20 * math.sin(tempo_ms / 300 + k)
        sx = int(LARGURA // 2 + r * math.cos(angulo))
        sy = int(ALTURA  // 2 + r * math.sin(angulo))
        raio = 5 + int(3 * math.sin(tempo_ms / 200 + k))
        pygame.draw.circle(tela, AMARELO, (sx, sy), raio)

    return _desenhar_painel_central(
        cor_fundo   = (20, 60, 20), cor_borda = (0, 220, 80),
        titulo_txt  = "VITÓRIA!", cor_titulo = (80, 255, 120),
        subtitulo_txt = f"Parabéns, {nome_jogador}!", pontuacao = jogo.pontuacao(),
        tempo_ms    = tempo_ms,
    )

def desenhar_tela_derrota(tempo_ms):
    desenhar()   
    if tempo_ms < 600:
        shake = int(6 * math.sin(tempo_ms / 40) * max(0, 1 - tempo_ms / 600))
        tela.scroll(shake, 0)
    return _desenhar_painel_central(
        cor_fundo   = (60, 10, 10), cor_borda = (220, 40, 40),
        titulo_txt  = "FIM DE JOGO", cor_titulo = (255, 80, 80),
        subtitulo_txt = f"Tente de novo, {nome_jogador}!", pontuacao = jogo.pontuacao(),
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
        if rect.collidepoint(pos): return nivel
    return None

def clique(pos):
    for i in range(len(jogo.cartas)):
        if pos_carta(i).collidepoint(pos):
            jogo.selecionar(i)

def reiniciar_jogo():
    global estado, jogo, timer_fim, COLUNAS, TAM, MARGEM, tempo_espera, particulas
    estado = "menu"
    jogo   = None
    timer_fim = 0
    tempo_espera = 0
    particulas.clear()
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
                # Só permite o clique se o jogo não estiver pausado esperando você ver a carta
                if tempo_espera == 0:
                    clique(pos)

            elif estado in ("vitoria", "derrota"):
                py_painel = (ALTURA - 340) // 2
                btn_rect = pygame.Rect(LARGURA // 2 - 140, py_painel + 260, 280, 55)
                if btn_rect.collidepoint(pos):
                    reiniciar_jogo()

    # ── Renderização por estado ──

    if estado == "menu":
        desenhar_tela_inicial()

    elif estado == "jogando":
        desenhar()
        atualizar_e_desenhar_particulas() # Efeito de explosão fica por cima das cartas

        # Assim que clica na 2ª carta, salva o tempo e verifica se explodiu
        if len(jogo.selecionadas) == 2 and tempo_espera == 0:
            tempo_espera = tempo_agora
            c1, c2 = jogo.selecionadas
            if jogo.cartas[c1] == jogo.cartas[c2]: # Se acertou o par
                gerar_explosao(c1)
                gerar_explosao(c2)

        # Só esconde/verifica as cartas DEPOIS de 1.2 segundos (1200 ms)
        if tempo_espera > 0 and tempo_agora - tempo_espera > 1200:
            jogo.verificar()
            tempo_espera = 0

        # Verifica se o jogo acabou
        if jogo.venceu() and tempo_espera == 0:
            salvar_dados(nome_jogador, nivel_escolhido, jogo.pontuacao())
            timer_fim = tempo_agora
            estado = "vitoria"

        elif jogo.perdeu() and tempo_espera == 0:
            salvar_dados(nome_jogador, nivel_escolhido, jogo.pontuacao())
            timer_fim = tempo_agora
            estado = "derrota"

    elif estado == "vitoria":
        tempo_decorrido = tempo_agora - timer_fim
        desenhar_tela_vitoria(tempo_decorrido)

    elif estado == "derrota":
        tempo_decorrido = tempo_agora - timer_fim
        desenhar_tela_derrota(tempo_decorrido)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()