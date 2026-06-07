import pygame
import math
import random
import sys
from datetime import datetime
from jogo_memoria import JogoMemoria
from loguin import tela_login, salvar_dados_json, salvar_resultado_txt

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

# Tela inicial
estado = "login" 
nome_jogador = "" # Começa vazio
nivel_escolhido = "facil"
jogo = None
timer_fim = 0          
tempo_espera = 0     
particulas = []      

# Variável de controle do novo modal de confirmação
mostrar_confirmacao = False

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
    rect = pos_carta(i)
    cx, cy = rect.center
    for _ in range(30): 
        dx = random.uniform(-8, 8)
        dy = random.uniform(-8, 8)
        vida_max = random.randint(30, 60)
        tamanho = random.randint(3, 8)
        cor = random.choice([AMARELO, BRANCO, (255, 215, 0), (255, 255, 150)])
        particulas.append([cx, cy, dx, dy, vida_max, cor, tamanho, vida_max])

def atualizar_e_desenhar_particulas():
    for p in particulas[:]:
        p[0] += p[2] 
        p[1] += p[3] 
        p[4] -= 1    
        p[3] += 0.3  
        if p[4] <= 0:
            particulas.remove(p)
        else:
            escala = p[4] / p[7]
            tam_atual = max(1, int(p[6] * escala)) 
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
            tela.blit(texto, (rect.x + rect.width  // 2 - texto.get_width()  // 2, rect.y + rect.height // 2 - texto.get_height() // 2))
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

    # Textos do HUD
    texto_nome   = fonte.render(f"Jogador: {nome_jogador}", True, BRANCO)
    texto_pontos = fonte.render(f"Pontos: {jogo.pontuacao()}", True, BRANCO)
    texto_vida   = fonte.render(f"Vidas: {jogo.vida_total()}", True, BRANCO)
    
    tela.blit(fonte.render(f"Jogador: {nome_jogador}", True, (0,0,0)), (12, 12))
    tela.blit(fonte.render(f"Pontos: {jogo.pontuacao()}", True, (0,0,0)), (12, 42))
    tela.blit(fonte.render(f"Vidas: {jogo.vida_total()}", True, (0,0,0)), (12, 72))
    
    tela.blit(texto_nome,   (10, 10))
    tela.blit(texto_pontos, (10, 40))
    tela.blit(texto_vida,   (10, 70))

    # Desenhar o Botão de Voltar no canto superior direito
    btn_voltar_rect = pygame.Rect(LARGURA - 180, 20, 160, 45)
    mouse_pos = pygame.mouse.get_pos()
    
    # Efeito hover (muda de cor se o mouse passar por cima)
    cor_btn_voltar = (200, 50, 50) if btn_voltar_rect.collidepoint(mouse_pos) else (150, 30, 30)
    
    pygame.draw.rect(tela, cor_btn_voltar, btn_voltar_rect, border_radius=8)
    pygame.draw.rect(tela, BRANCO, btn_voltar_rect, 2, border_radius=8) # Bordinha branca
    
    txt_btn = fonte_info.render("Sair do Jogo", True, BRANCO)
    tela.blit(txt_btn, (btn_voltar_rect.centerx - txt_btn.get_width() // 2, btn_voltar_rect.centery - txt_btn.get_height() // 2))

def desenhar_modal_confirmacao():
    """Desenha a tela flutuante perguntando se o jogador quer mesmo voltar."""
    # Fundo escurecido
    overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    tela.blit(overlay, (0, 0))

    # Caixinha central
    pw, ph = 500, 250
    px, py = (LARGURA - pw) // 2, (ALTURA - ph) // 2
    
    pygame.draw.rect(tela, (20, 30, 40), (px, py, pw, ph), border_radius=15)
    pygame.draw.rect(tela, (218, 165, 32), (px, py, pw, ph), 3, border_radius=15) # Borda dourada

    # Textos
    t1 = fonte.render("Deseja mesmo voltar?", True, BRANCO)
    t2 = fonte_info.render("Seu progresso atual será perdido!", True, (255, 100, 100))
    tela.blit(t1, (LARGURA // 2 - t1.get_width() // 2, py + 40))
    tela.blit(t2, (LARGURA // 2 - t2.get_width() // 2, py + 90))

    # Pegar posição do mouse para efeito Hover
    mouse_pos = pygame.mouse.get_pos()

    # Botões
    btn_voltar = pygame.Rect(px + 40, py + 150, 190, 55)
    btn_continuar = pygame.Rect(px + 270, py + 150, 190, 55)

    cor_voltar = (200, 50, 50) if btn_voltar.collidepoint(mouse_pos) else (150, 30, 30)
    cor_continuar = (50, 200, 50) if btn_continuar.collidepoint(mouse_pos) else (30, 150, 30)

    pygame.draw.rect(tela, cor_voltar, btn_voltar, border_radius=8)
    pygame.draw.rect(tela, cor_continuar, btn_continuar, border_radius=8)

    t_voltar = fonte_info.render("Voltar", True, BRANCO)
    t_continuar = fonte_info.render("Continuar", True, BRANCO)

    tela.blit(t_voltar, (btn_voltar.centerx - t_voltar.get_width() // 2, btn_voltar.centery - t_voltar.get_height() // 2))
    tela.blit(t_continuar, (btn_continuar.centerx - t_continuar.get_width() // 2, btn_continuar.centery - t_continuar.get_height() // 2))

    # Retorna as coordenadas dos botões para verificar o clique depois
    return btn_voltar, btn_continuar


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
    
    # Botão para trocar de usuário
    btn_trocar_usuario = pygame.Rect((LARGURA - 200) // 2, 600, 200, 50)
    mouse_pos = pygame.mouse.get_pos()
    
    # hover effect botão trocar usuário
    if btn_trocar_usuario.collidepoint(mouse_pos):
        cor_btn_trocar = (180, 50, 50)
    else:
        cor_btn_trocar = (120, 30, 30)

    pygame.draw.rect(tela, cor_btn_trocar, btn_trocar_usuario, border_radius=10)
    pygame.draw.rect(tela, (218, 165, 32), btn_trocar_usuario, 2, border_radius=10) # Borda dourada
    
    texto_trocar = fonte_info.render("Trocar Jogador", True, BRANCO)
    tela.blit(texto_trocar, (btn_trocar_usuario.centerx - texto_trocar.get_width() // 2, 
                             btn_trocar_usuario.centery - texto_trocar.get_height() // 2))

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
    tela.blit(t_btn, (btn_rect.centerx - t_btn.get_width() // 2, btn_rect.centery - t_btn.get_height() // 2))
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

    return _desenhar_painel_central((20, 60, 20), (0, 220, 80), "VITÓRIA!", (80, 255, 120),
                                    f"Parabéns, {nome_jogador}!", jogo.pontuacao(), tempo_ms)

def desenhar_tela_derrota(tempo_ms):
    desenhar()   
    if tempo_ms < 600:
        shake = int(6 * math.sin(tempo_ms / 40) * max(0, 1 - tempo_ms / 600))
        tela.scroll(shake, 0)
    return _desenhar_painel_central((60, 10, 10), (220, 40, 40), "FIM DE JOGO", (255, 80, 80),
                                    f"Tente de novo, {nome_jogador}!", jogo.pontuacao(), tempo_ms)

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
    global estado, jogo, timer_fim, COLUNAS, TAM, MARGEM, tempo_espera, particulas, mostrar_confirmacao
    estado = "menu"
    jogo   = None
    timer_fim = 0
    tempo_espera = 0
    mostrar_confirmacao = False # Zera a confirmação pra não abrir o menu bugado
    particulas.clear()
    COLUNAS, TAM, MARGEM = GRID_CONFIG["facil"]

# ─── Loop principal ───────────────────────────────────────────────────────────

while rodando:
    tempo_agora = pygame.time.get_ticks()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
            sys.exit()  # Encerra o programa completamente

        if evento.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            if estado == "menu":
                nivel = verificar_clique_botao(pos)
                if nivel:
                    nivel_escolhido = nivel
                    COLUNAS, TAM, MARGEM = GRID_CONFIG[nivel_escolhido]
                    jogo = JogoMemoria(nivel_escolhido)
                    estado = "jogando"
                
                botao_trocar_usuario = pygame.Rect((LARGURA - 200) // 2, 600, 200, 50)
                if botao_trocar_usuario.collidepoint(pos):
                    estado = "login" # manda de volta pra tela de login

            elif estado == "jogando":
                # Se a janela de confirmação estiver aberta, os botões que valem são os dela
                if mostrar_confirmacao:
                    pw, ph = 500, 250
                    px, py = (LARGURA - pw) // 2, (ALTURA - ph) // 2
                    
                    # Recria os retângulos virtuais para verificar o clique
                    btn_voltar = pygame.Rect(px + 40, py + 150, 190, 55)
                    btn_continuar = pygame.Rect(px + 270, py + 150, 190, 55)

                    if btn_voltar.collidepoint(pos):
                        reiniciar_jogo() # Volta para o menu zerando tudo
                    elif btn_continuar.collidepoint(pos):
                        mostrar_confirmacao = False # Fecha a janela e volta pro jogo
                
                # Se a janela não estiver aberta e as cartas não estiverem no delay
                elif tempo_espera == 0:
                    btn_sair = pygame.Rect(LARGURA - 180, 20, 160, 45)
                    
                    if btn_sair.collidepoint(pos):
                        mostrar_confirmacao = True # Abre o modal
                    else:
                        clique(pos) # Clica nas cartas normalmente

            elif estado in ("vitoria", "derrota"):
                py_painel = (ALTURA - 340) // 2
                btn_rect = pygame.Rect(LARGURA // 2 - 140, py_painel + 260, 280, 55)
                if btn_rect.collidepoint(pos):
                    reiniciar_jogo()

    # ── Renderização por estado ──

    if estado == "login":
        novo_nome = tela_login(tela) 
        
        if novo_nome: 
            nome_jogador = novo_nome
            estado = "menu"

    elif estado == "menu":
        desenhar_tela_inicial()

    elif estado == "jogando":
        desenhar()
        
        # Só atualiza partículas e regras do jogo se a tela de confirmação NÃO estiver aberta
        if not mostrar_confirmacao:
            atualizar_e_desenhar_particulas() 

            if len(jogo.selecionadas) == 2 and tempo_espera == 0:
                tempo_espera = tempo_agora
                c1, c2 = jogo.selecionadas
                if jogo.cartas[c1] == jogo.cartas[c2]: 
                    gerar_explosao(c1)
                    gerar_explosao(c2)

            if tempo_espera > 0 and tempo_agora - tempo_espera > 1200:
                jogo.verificar()
                tempo_espera = 0

            if jogo.venceu() and tempo_espera == 0:
                data_atual = datetime.now().strftime("%d/%m/%Y")
                hora_atual = datetime.now().strftime("%H:%M:%S")
                tempo_jogado = tempo_agora // 1000 # Tempo em segundos
                salvar_dados_json(nome_jogador, nivel_escolhido, jogo.pontuacao())
                salvar_resultado_txt(nome_jogador, data_atual, hora_atual, jogo.pontuacao(), tempo_jogado, nivel_escolhido, "Vitória")
                timer_fim = tempo_agora
                estado = "vitoria"

            elif jogo.perdeu() and tempo_espera == 0:
                data_atual = datetime.now().strftime("%d/%m/%Y")
                hora_atual = datetime.now().strftime("%H:%M:%S")
                tempo_jogado = tempo_agora // 1000 # Tempo em segundos
                salvar_dados_json(nome_jogador, nivel_escolhido, jogo.pontuacao())
                salvar_resultado_txt(nome_jogador, data_atual, hora_atual, jogo.pontuacao(), tempo_jogado, nivel_escolhido, "Derrota")
                timer_fim = tempo_agora
                estado = "derrota"
        
        # Se a tela de confirmação foi acionada, desenha ela por cima das cartas
        else:
            desenhar_modal_confirmacao()

    elif estado == "vitoria":
        tempo_decorrido = tempo_agora - timer_fim
        desenhar_tela_vitoria(tempo_decorrido)

    elif estado == "derrota":
        tempo_decorrido = tempo_agora - timer_fim
        desenhar_tela_derrota(tempo_decorrido)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()