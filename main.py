import pygame
from jogo_memoria import JogoMemoria

pygame.init()

# Tela
LARGURA = 800
ALTURA = 600
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

# Jogo
estado = "menu"
nivel_escolhido = "facil"
jogo = None


# Grid
COLUNAS = 6
LINHAS = 6

TAM = 100
MARGEM = 10

clock = pygame.time.Clock()
rodando = True

def desenhar():
    tela.fill((30, 30, 30))

    for i in range(len(jogo.cartas)):
        linha = i // COLUNAS
        col = i % COLUNAS

        x = col * (TAM + MARGEM) + 100
        y = linha * (TAM + MARGEM) + 50

        rect = pygame.Rect(x, y, TAM, TAM)

        if jogo.reveladas[i]:
            pygame.draw.rect(tela, (0, 200, 0), rect)
            texto = fonte.render(str(jogo.cartas[i]), True, (0, 0, 0))
            tela.blit(texto, (x + 35, y + 30))
        else:
            pygame.draw.rect(tela, (200, 0, 0), rect)

    texto_pontos = fonte.render(f"Pontos: {jogo.pontuacao()}", True, (255, 255, 255))
    texto_vida = fonte.render(f"Vidas: {jogo.vida_total()}", True, (255, 255, 255))
    tela.blit(texto_pontos, (10, 10))
    tela.blit(texto_vida, (10, 50))
    
    pygame.display.flip()


def desenhar_tela_inicial():
    tela.fill((20, 20, 40))  # fundo azul escuro

    # --- Título ---
    titulo = fonte_titulo.render("Jogo da Memória", True, BRANCO)
    tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 80))

    # --- Informações ---
    infos = [
        "Encontre todos os pares de cartas!",
        "Você começa com 10 vidas.",
        "Cada erro remove 1 vida.",
        "Cada par encontrado vale 100 pontos.",
    ]
    for i, linha in enumerate(infos):
        texto = fonte_info.render(linha, True, BRANCO)
        tela.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 200 + i * 35))

    # --- Botões ---
    botoes = {
        "facil":   {"label": "Fácil",   "cor": VERDE,        "x": 100},
        "medio":   {"label": "Médio",   "cor": AMARELO,      "x": 300},
        "dificil": {"label": "Difícil", "cor": VERMELHO, "x": 500},
    }

    for nivel, dados in botoes.items():
        rect = pygame.Rect(dados["x"], 440, 180, 60)
        pygame.draw.rect(tela, dados["cor"], rect, border_radius=10)
        texto = fonte.render(dados["label"], True, BRANCO)
        tela.blit(texto, (rect.x + rect.width // 2 - texto.get_width() // 2,
                          rect.y + rect.height // 2 - texto.get_height() // 2))

    pygame.display.flip()

def verificar_clique_botao(pos):
    """Retorna o nível clicado ou None se não clicou em nenhum botão."""
    botoes_rect = {
        "facil":   pygame.Rect(100, 440, 180, 60),
        "medio":   pygame.Rect(300, 440, 180, 60),
        "dificil": pygame.Rect(500, 440, 180, 60),
    }
    for nivel, rect in botoes_rect.items():
        if rect.collidepoint(pos):
            return nivel
    return None

def clique(pos):
    for i in range(len(jogo.cartas)):
        linha = i // COLUNAS
        col = i % COLUNAS

        x = col * (TAM + MARGEM) + 100
        y = linha * (TAM + MARGEM) + 50

        rect = pygame.Rect(x, y, TAM, TAM)

        if rect.collidepoint(pos):
            jogo.selecionar(i)


while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False


        if evento.type == pygame.MOUSEBUTTONDOWN:
            if estado == "menu":
                nivel = verificar_clique_botao(pygame.mouse.get_pos())
                if nivel:
                    nivel_escolhido = nivel
                    jogo = JogoMemoria(nivel_escolhido)
                    LINHAS = len(jogo.cartas) // COLUNAS
                    estado = "jogando"

            elif estado == "jogando":          # ← ADICIONE ISSO AQUI
                clique(pygame.mouse.get_pos())

    # --- Desenho ---
    if estado == "menu":
        desenhar_tela_inicial()

    elif estado == "jogando":
        desenhar()
    

        if len(jogo.selecionadas) == 2:
            pygame.time.delay(500)
            jogo.verificar()

        if jogo.venceu():
            print("VOCÊ VENCEU!")
            pygame.time.delay(2000)
            rodando = False

        if jogo.perdeu():
            print("VOCÊ PERDEU!")
            pygame.time.delay(2000)
            rodando = False

    clock.tick(60)



pygame.quit()