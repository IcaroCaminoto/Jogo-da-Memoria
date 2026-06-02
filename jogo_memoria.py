import random

def verificar_par(c1, c2):
    return c1 == c2

def criar_cartas(nivel):
    config = {
        "facil": 8,
        "medio": 12,
        "dificil": 18
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

    def selecionar(self, index):
        if self.reveladas[index] or len(self.selecionadas) >= 2:
            return

        self.selecionadas.append(index)
        self.reveladas[index] = True

    def verificar(self):
        if len(self.selecionadas) == 2:
            i1, i2 = self.selecionadas

            if not verificar_par(self.cartas[i1], self.cartas[i2]):
                self.reveladas[i1] = False
                self.reveladas[i2] = False

            self.selecionadas = []

    def venceu(self):
        return all(self.reveladas)