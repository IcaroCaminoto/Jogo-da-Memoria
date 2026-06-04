import pygame
import json
from datetime import datetime
import os

def salvar_dados(nome, nivel, pontuacao):
    """Salva os dados da partida em um arquivo JSON."""
    arquivo = 'pontuacoes.json'
    dados = []
    
    # Verifica se o arquivo já existe e carrega os dados anteriores
    if os.path.exists(arquivo):
        with open(arquivo, 'r', encoding='utf-8') as f:
            try:
                dados = json.load(f)
            except json.JSONDecodeError:
                dados = []
                
    # Cria o novo registro com as informações solicitadas
    novo_registro = {
        "nome": nome,
        "horario": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "nivel": nivel,
        "pontuacao": pontuacao
    }
    
    # Adiciona o novo registro à lista e salva no arquivo
    dados.append(novo_registro)
    
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def tela_login(tela):
    """Exibe uma tela para o jogador digitar seu nome e retorna a string digitada."""
    pygame.font.init()
    fonte = pygame.font.SysFont(None, 40)
    fonte_titulo = pygame.font.SysFont(None, 72)
    
    nome = ""
    ativo = True
    
    # Posição e tamanho da caixa de texto (baseado na largura 1000 e altura 700)
    caixa_texto = pygame.Rect(300, 300, 400, 50)
    cor_ativa = pygame.Color('dodgerblue2')
    
    while ativo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    # Só avança se o usuário tiver digitado algo
                    if nome.strip() != "":
                        return nome.strip()
                elif evento.key == pygame.K_BACKSPACE:
                    # Apaga o último caractere
                    nome = nome[:-1]
                else:
                    # Adiciona a letra digitada
                    nome += evento.unicode
                    
        tela.fill((20, 20, 40))  # Fundo azul escuro igual ao do menu
        
        # Textos da tela
        titulo = fonte_titulo.render("Digite seu Nome", True, (255, 255, 255))
        tela.blit(titulo, (1000 // 2 - titulo.get_width() // 2, 150))
        
        instrucao = fonte.render("Pressione ENTER para jogar", True, (200, 200, 200))
        tela.blit(instrucao, (1000 // 2 - instrucao.get_width() // 2, 400))
        
        # Desenha a caixa de texto e o nome
        pygame.draw.rect(tela, cor_ativa, caixa_texto, 2, border_radius=5)
        texto_surface = fonte.render(nome, True, (255, 255, 255))
        tela.blit(texto_surface, (caixa_texto.x + 10, caixa_texto.y + 10))
        
        # Aumenta a caixa se o nome ficar muito grande
        caixa_texto.w = max(400, texto_surface.get_width() + 20)
        
        pygame.display.flip()