import random


def verificar_par(c1, c2):
    return c1 == c2

def criar_cartas(nivel):
    config = {
        "facil": 8,
        "medio": 16,
        "dificil": 24
    }

    quantidade_pares = config[nivel]
    cartas = []

    for i in range(1, quantidade_pares + 1):
        cartas.append(i)
        cartas.append(i)

    random.shuffle(cartas)
    return cartas

class JogoMemoria:
    def __init__(self, nivel="facil"):
        self.cartas = criar_cartas(nivel)
        self.reveladas = [False] * len(self.cartas)
        self.selecionadas = []
        self._pontos = 0
        self._vidas = 10
        
    def selecionar(self, index):
        if self.reveladas[index] or len(self.selecionadas) >= 2:
            return

        self.selecionadas.append(index)
        self.reveladas[index] = True

    def verificar(self):
        if len(self.selecionadas) == 2:
            i1, i2 = self.selecionadas

            if verificar_par(self.cartas[i1], self.cartas[i2]):
                self._pontos += 100
            else:
                self.reveladas[i1] = False
                self.reveladas[i2] = False
                self._vidas -= 1

            self.selecionadas = []

    def pontuacao(self):
        return self._pontos

    def vida_total(self):
        return self._vidas

    def venceu(self):
        return all(self.reveladas)

    def perdeu(self):
        return self._vidas <= 0