import random
import time
import os
import sys
import datetime
import json

PRETO        = (0,   0,   0)
BRANCO       = (255, 255, 255)
CINZA        = (128, 128, 128)
CINZA_CLARO  = (200, 200, 200)
AZUL         = (30,  100, 200)
AZUL_CLARO   = (70,  140, 240)
VERDE        = (50,  180,  80)
VERMELHO     = (200,  50,  50)
AMARELO      = (255, 200,   0)
LARANJA      = (230, 120,  30)
ROXO         = (130,  50, 200)
ROSA         = (220,  80, 150)
DOURADO      = (212, 175,  55)
FUNDO        = (15,   25,  50)
FUNDO_CARD   = (40,   60, 110)
FUNDO_CARD_H = (60,   90, 160)

SIMBOLOS_NUMERICOS = [1, 2, 3, 4, 5, 6, 7, 8,
                      9, 10, 11, 12, 13, 14, 15, 16,
                      17, 18, 19, 20, 21, 22, 23, 24]

SIMBOLOS_UNICOS_NUMERICOS = [1, 2, 3, 4, 5, 6, 7, 8,
                             9, 10, 11, 12, 13, 14, 15, 16,
                             17, 18, 19, 20, 21, 22, 23, 24]

CORES_SIMB = [AMARELO, VERMELHO, AZUL_CLARO, VERDE, ROSA, DOURADO, CINZA_CLARO, LARANJA,
            ROXO, VERDE, ROSA, VERMELHO, AMARELO, BRANCO, AZUL_CLARO, CINZA,
            VERMELHO, VERDE, LARANJA, AZUL_CLARO, ROXO, AMARELO, ROSA, DOURADO]

NIVEL_CONFIG = {
    "facil": 8,
    "medio": 12,
    "dificil": 18
}

#________________________BLOCO 1________________________

def verificar_par(c1, c2):
    return c1 == c2


def calcular_pontuacao(pares, nivel, tempo_s, vidas_restantes):
    pontos_pares = pares * 100

    bonus_tempo = max(0, 300 - tempo_s)

    bonus_vidas = vidas_restantes * 50

    return pontos_pares + bonus_tempo + bonus_vidas

def formatar_tempo(segundos):
    minutos = segundos // 60
    segundos_restantes = segundos % 60

    return f"{minutos:02}:{segundos_restantes:02}"



#________________________BLOCO 2________________________

def criar_cartas(nivel):
    quantidade_pares = NIVEL_CONFIG[nivel]

    cartas = []

    for i in range(1, quantidade_pares + 1):
        cartas.append(i)
        cartas.append(i)

    return cartas

def embaralhar_cartas(cartas):
    random.shuffle(cartas)
    return cartas

#________________________BLOCO 3________________________

def salvar_resultado():
    return

def carregar_ranking(caminho_json):
    return

def salvar_ranking(caminho_json, ranking):
    return

cartas = criar_cartas("facil")
embaralhar_cartas(cartas)

print(cartas)

primeira = int(input("Primeira posição: "))
segunda = int(input("Segunda posição: "))

if verificar_par(cartas[primeira], cartas[segunda]):
    print("Acertou!")
else:
    print("Errou!")