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

# Jogo
jogo = JogoMemoria("facil")

# Grid
COLUNAS = 4
LINHAS = len(jogo.cartas) // COLUNAS

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

    pygame.display.flip()


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
            clique(pygame.mouse.get_pos())

    desenhar()

    if len(jogo.selecionadas) == 2:
        pygame.time.delay(500)
        jogo.verificar()

    if jogo.venceu():
        print("VOCÊ VENCEU!")
        pygame.time.delay(2000)
        rodando = False

    clock.tick(60)

pygame.quit()