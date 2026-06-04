import random
import time 



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
        
        self.tempo_inicial = time.time()
        self.tempo_final = None

        config_pontos = {
            "facil": 100,
            "medio": 150,
            "dificil": 200
        }
        self.pontos_por_acerto = config_pontos[nivel]

    def selecionar(self, index):
        if self.reveladas[index] or len(self.selecionadas) >= 2:
            return

        self.selecionadas.append(index)
        self.reveladas[index] = True

    def verificar(self):
        if len(self.selecionadas) == 2:
            i1, i2 = self.selecionadas

            carta_1 = self.cartas[i1]
            carta_2 = self.cartas[i2]

            if carta_1 == 6 and carta_2 == 7:
                print("ESTER-EGG ENCONTRADO!!!!")
                self.selecionadas = []
                self._pontos += 6700000000

            if verificar_par(self.cartas[i1], self.cartas[i2]):
                self._pontos += self.pontos_por_acerto
            else:
                self.reveladas[i1] = False
                self.reveladas[i2] = False
                self._vidas -= 1

            self.selecionadas = []

        if self.venceu() or self.perdeu():
                self._parar_cronometro()
                print(f"Tempo: {self.obter_tempo_formatado()} - Pontos: {self.pontos_por_acerto} - Vidas restantes: {self._vidas}")

    def pontuacao(self):
        return self._pontos

    def vida_total(self):
        return self._vidas

    def venceu(self):
        return all(self.reveladas)

    def perdeu(self):
        return self._vidas <= 0
    
    def _parar_cronometro(self):
        """Método interno para travar o tempo. (Uso do back-end)"""
        if self.tempo_final is None:
            self.tempo_final = time.time()

    def obter_tempo_segundos(self):
        """Retorna o tempo decorrido bruto em segundos (int). 
        Útil se o front quiser salvar em banco de dados ou arquivos."""
        if self.tempo_final is not None:
            duracao = self.tempo_final - self.tempo_inicial
        else:
            duracao = time.time() - self.tempo_inicial
        return int(duracao)

    def obter_tempo_formatado(self):
        """Retorna o tempo pronto para o Front-end exibir na tela.
        Exemplo de retorno: '00:45', '02:15'"""
        total_segundos = self.obter_tempo_segundos()
        minutos = total_segundos // 60
        segundos = total_segundos % 60
        
        # Retorna no formato MM:SS (ex: 05:08)
        return f"{minutos:02d}:{segundos:02d}"
    

    def reiniciar_para_menu(self):
        """
        Zera o estado do jogo apenas se a partida tiver terminado (Vitória ou Derrota).
        Retorna o próximo estado do jogo ("menu" ou "jogando").
        """
        # TRAVA DE SEGURANÇA: Só reseta se o jogo realmente acabou
        if self.venceu() or self.perdeu():
            self.reveladas = [False] * len(self.cartas)
            self.selecionadas = []
            self._pontos = 0
            self._vidas = 10
            
            # Zera o cronômetro para a próxima partida
            self.tempo_inicial = time.time()
            self.tempo_final = None
            
            print("Jogo resetado com sucesso! Voltando ao menu.")
            return "menu"
        
        # Se tentarem apertar R no meio da partida, o back-end ignora e mantém o jogo rodando
        return "jogando"


