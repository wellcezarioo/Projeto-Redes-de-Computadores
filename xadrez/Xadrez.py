import pygame
import sys

# Inicializando o pygame
pygame.init()

# Dimensões do tabuleiro e tela
LARGURA_JANELA = 937.5
ALTURA_JANELA = 750
TAMANHO_QUADRADO = 94

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (118, 150, 86)
BEGE = (238, 238, 210)
VERMELHO = (255, 0, 0)
AZUL = (125, 20, 125)

# Definindo a tela
tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
pygame.display.set_caption("Xadrez 2.0")

# Representação das peças
PECA_VAZIA = "."
PECA_BRANCA = 'B'
PECA_PRETA = 'P'

# sprites
pecas_ini = ["P", "T", "K", "B", "R", "Q"]
cores = ["B", "P"]

# Criar uma lista de todos os nomes de arquivos de sprites
nomes_arquivos = [f"{p}{cor}" for p in pecas_ini for cor in cores]

# Carregar os sprites
sprites = {nome: pygame.image.load(f"{nome}.png") for nome in nomes_arquivos}


class PecaVazia:
    def __init__(self):
        self.nome = "."
        self.cor = None  # Nenhuma cor, pois não é uma peça real
        self.atacada = False  # para evitar que o rei va para uma casa atacada

    def __repr__(self):
        return "PecaVazia"


class Piece:
    def __init__(self, nome, cor, sprite):
        self.nome = nome
        self.cor = cor
        self.sprite = sprite
        self.atacada = False  # para saber se o rei pode tomar

    # Método genérico que será sobrescrito por subclasses
    def movimento_valido(self, origem, destino, tabuleiro):
        raise NotImplementedError("Este método deve ser implementado pelas subclasses")


class Torre(Piece):
    def __init__(self, nome, cor, sprite):
        super().__init__(nome, cor, sprite)
        self.ja_moveu = False  # Para verificar se a Torre já se moveu

    def movimento_valido(self, origem, destino, tabuleiro):
        x_orig, y_orig = origem
        x_dest, y_dest = destino

        # Movimento em linha reta (mesma linha ou mesma coluna)
        if x_orig == x_dest:
            # Movimento na mesma coluna, verificar se há peças no caminho
            step = 1 if y_dest > y_orig else -1
            for y in range(y_orig + step, y_dest, step):
                if not isinstance(tabuleiro[x_orig][y], PecaVazia):
                    return False  # Há uma peça no caminho

        elif y_orig == y_dest:
            # Movimento na mesma linha, verificar se há peças no caminho
            step = 1 if x_dest > x_orig else -1
            for x in range(x_orig + step, x_dest, step):
                if not isinstance(tabuleiro[x][y_orig], PecaVazia):
                    return False  # Há uma peça no caminho

        return True


class Cavalo(Piece):
    def movimento_valido(self, origem, destino, tabuleiro):
        x_orig, y_orig = origem
        x_dest, y_dest = destino

        dx = abs(x_dest - x_orig)
        dy = abs(y_dest - y_orig)

        # Movimento em forma de "L"
        if (dx == 2 and dy == 1) or (dx == 1 and dy == 2):
            return True

        return False


class Bispo(Piece):
    def movimento_valido(self, origem, destino, tabuleiro):
        x_orig, y_orig = origem
        x_dest, y_dest = destino

        dx = abs(x_dest - x_orig)
        dy = abs(y_dest - y_orig)

        # Movimento diagonal
        if dx == dy:
            # Verificar se há peças no caminho na diagonal
            x_step = 1 if x_dest > x_orig else -1
            y_step = 1 if y_dest > y_orig else -1
            for i in range(1, dx):  # dx == dy, podemos usar qualquer um
                if not isinstance(tabuleiro[x_orig + i * x_step][y_orig + i * y_step], PecaVazia):
                    return False  # Há uma peça no caminho

            return True
        return False


class Rainha(Piece):
    def movimento_valido(self, origem, destino, tabuleiro):
        x_orig, y_orig = origem
        x_dest, y_dest = destino

        if x_orig == x_dest or y_orig == y_dest:
            # Movimento em linha reta (mesma linha ou mesma coluna)
            if x_orig == x_dest:
                # Movimento na mesma coluna, verificar se há peças no caminho
                step = 1 if y_dest > y_orig else -1
                for y in range(y_orig + step, y_dest, step):
                    if not isinstance(tabuleiro[x_orig][y], PecaVazia):
                        return False  # Há uma peça no caminho

            elif y_orig == y_dest:
                # Movimento na mesma linha, verificar se há peças no caminho
                step = 1 if x_dest > x_orig else -1
                for x in range(x_orig + step, x_dest, step):
                    if not isinstance(tabuleiro[x][y_orig], PecaVazia):
                        return False  # Há uma peça no caminho

            return True

        dx = abs(x_dest - x_orig)
        dy = abs(y_dest - y_orig)

        # Movimento diagonal
        if dx == dy:
            # Verificar se há peças no caminho na diagonal
            x_step = 1 if x_dest > x_orig else -1
            y_step = 1 if y_dest > y_orig else -1
            for i in range(1, dx):  # dx == dy, podemos usar qualquer um
                if not isinstance(tabuleiro[x_orig + i * x_step][y_orig + i * y_step], PecaVazia):
                    return False  # Há uma peça no caminho

            return True
        return False


class Rei(Piece):
    def __init__(self, nome, cor, sprite):
        super().__init__(nome, cor, sprite)
        self.ja_moveu = False  # Para verificar se o Rei já se moveu

    def movimento_valido(self, origem, destino, tabuleiro):
        x_orig, y_orig = origem
        x_dest, y_dest = destino

        dx = abs(x_dest - x_orig)
        dy = abs(y_dest - y_orig)

        # Verificar se é o roque
        if not self.ja_moveu and dy == 2 and dx == 0:
            # Roque pequeno (lado do rei)
            if y_dest < y_orig and isinstance(tabuleiro[x_orig][y_orig - 3], Torre):
                tower = tabuleiro[x_orig][y_orig - 3]
                if tower.movimento_valido((x_orig, y_orig - 3), (x_orig, y_orig - 1),
                                          tabuleiro) and not tower.ja_moveu:
                    return self.verificar_roque(origem, destino, tabuleiro, pequeno=True)

            # Roque grande (lado da rainha)
            elif y_dest > y_orig and isinstance(tabuleiro[x_orig][y_orig + 4], Torre):
                tower = tabuleiro[x_orig][y_orig + 4]
                if tower.movimento_valido((x_orig, y_orig + 4), (x_orig, y_orig + 1),
                                          tabuleiro) and not tower.ja_moveu:
                    return self.verificar_roque(origem, destino, tabuleiro, pequeno=False)

        # O rei pode se mover uma casa em qualquer direção
        if max(dx, dy) == 1:
            return True
        return False

    def verificar_roque(self, origem, destino, tabuleiro, pequeno):
        # Verifica se o caminho está livre e move a Torre
        x_orig, y_orig = origem
        if pequeno:
            if isinstance(tabuleiro[x_orig][y_orig - 3], Torre) and tabuleiro[x_orig][y_orig - 2].nome == ".":
                return True
        else:
            if isinstance(tabuleiro[x_orig][y_orig + 4], Torre) and tabuleiro[x_orig][y_orig + 2].nome == "." and \
                    tabuleiro[x_orig][y_orig + 3].nome == ".":
                return True
        return False


class Peao(Piece):
    def __init__(self, nome, cor, sprite):
        super().__init__(nome, cor, sprite)
        self.primeiro_movimento = True  # Para saber se é o primeiro movimento

    def movimento_valido(self, origem, destino, tabuleiro):
        x_orig, y_orig = origem
        x_dest, y_dest = destino

        direcao = 1 if self.cor == 'B' else -1  # Brancas avançam (+1), Pretas recuam (-1)
        destino_vazio = isinstance(tabuleiro[x_dest][y_dest], PecaVazia)

        # Movimento normal de uma casa para frente
        if x_dest == x_orig + direcao and y_dest == y_orig and destino_vazio:
            self.primeiro_movimento = False  # Primeiro movimento foi feito
            return True

        # Movimento de duas casas no primeiro turno
        if self.primeiro_movimento and x_dest == x_orig + (2 * direcao) and y_dest == y_orig:
            casa_entre = tabuleiro[x_orig + direcao][y_orig]
            if destino_vazio and isinstance(casa_entre,
                                            PecaVazia):  # Verificar se a casa intermediária também está vazia
                self.primeiro_movimento = False
                return True

        # Captura normal (diagonal)
        if x_dest == x_orig + direcao and abs(y_dest - y_orig) == 1:
            peca_destino = tabuleiro[x_dest][y_dest]
            if not destino_vazio and peca_destino.cor != self.cor:
                self.primeiro_movimento = False
                return True

        # Captura en passant
        if x_dest == x_orig + direcao and abs(y_dest - y_orig) == 1 and destino_vazio:
            peao_lateral = tabuleiro[x_orig][y_dest]
            if isinstance(peao_lateral, Peao) and peao_lateral.cor != self.cor and not peao_lateral.primeiro_movimento:
                # Captura o peão en passant
                tabuleiro[x_orig][y_dest] = PecaVazia()  # Remover o peão capturado
                return True

        return False


# Inicializando o tabuleiro (10x8)
def inicializar_tabuleiro():
    tabuleiro = [
        # Linha 1 (torres, cavalos, bispos, guerreiro, rei, rainha)
        [Torre("Torre", "B", sprites["TB"]), Cavalo("Cavalo", "B", sprites["KB"]),
         Bispo("Bispo", "B", sprites["BB"]),
         Rei("Rei", "B", sprites["RB"]), Rainha("Rainha", "B", sprites["QB"]),
         Bispo("Bispo", "B", sprites["BB"]),
         Cavalo("Cavalo", "B", sprites["KB"]), Torre("Torre", "B", sprites["TB"])],

        # Linha 2 (peões brancos)
        [Peao("Peao", "B", sprites["PB"]) for _ in range(10)],

        # Linhas intermediárias vazias
        [PecaVazia() for _ in range(10)],
        [PecaVazia() for _ in range(10)],
        [PecaVazia() for _ in range(10)],
        [PecaVazia() for _ in range(10)],

        # Linha 7 (peões pretos)
        [Peao("Peao", "P", sprites["PP"]) for _ in range(10)],

        # Linha 8 (torres, cavalos, bispos, guerreiro, rei, rainha)
        [Torre("Torre", "P", sprites["TP"]), Cavalo("Cavalo", "P", sprites["KP"]),
         Bispo("Bispo", "P", sprites["BP"]),
         Rei("Rei", "P", sprites["RP"]), Rainha("Rainha", "P", sprites["QP"]),
         Bispo("Bispo", "P", sprites["BP"]),
         Cavalo("Cavalo", "P", sprites["KP"]), Torre("Torre", "P", sprites["TP"])]
    ]

    return tabuleiro


# Função para desenhar o tabuleiro
def desenhar_tabuleiro():
    for linha in range(8):
        for coluna in range(8):
            cor = BEGE if (linha + coluna) % 2 == 0 else VERDE
            pygame.draw.rect(tela, cor,
                             (coluna * TAMANHO_QUADRADO, linha * TAMANHO_QUADRADO, TAMANHO_QUADRADO, TAMANHO_QUADRADO))


# Função para desenhar as peças no tabuleiro
def desenhar_pecas(tabuleiro):
    for linha in range(8):
        for coluna in range(8):
            peca = tabuleiro[linha][coluna]
            if not isinstance(peca, PecaVazia):
                sprite = peca.sprite
                tela.blit(sprite, (coluna * TAMANHO_QUADRADO, linha * TAMANHO_QUADRADO))


# Função para verificar se o movimento é válido
def movimento_valido(origem, destino, tabuleiro):
    peca = tabuleiro[origem[0]][origem[1]]

    # Verificar se a peça é vazia
    if isinstance(peca, PecaVazia):
        return False

    # Verificar se o destino é uma posição vazia ou uma peça de cor diferente
    peca_destino = tabuleiro[destino[0]][destino[1]]
    if isinstance(peca_destino, PecaVazia) or peca.cor != peca_destino.cor:
        # Chama o método movimento_valido da peça específica
        return peca.movimento_valido(origem, destino, tabuleiro)

    return False


# Função para mover uma peça no tabuleiro
def mover_peca(origem, destino, tabuleiro, turno):
    peca_origem = tabuleiro[origem[0]][origem[1]]

    if isinstance(peca_origem, PecaVazia):  # Se não há peça na origem
        return False

    if movimento_valido(origem, destino, tabuleiro):
        if isinstance(peca_origem, Rei):
            # Verifica se é roque
            if abs(destino[1] - origem[1]) == 2 or abs(destino[0] - origem[0]) == 3:
                # Roque curto
                if destino[1] < origem[1]:
                    # Move a Torre no roque curto
                    tabuleiro[origem[0]][origem[1] - 1] = tabuleiro[origem[0]][origem[1] - 3]
                    tabuleiro[origem[0]][origem[1] - 3] = PecaVazia()
                # Roque grande
                else:
                    tabuleiro[origem[0]][origem[1] + 1] = tabuleiro[origem[0]][origem[1] + 4]
                    tabuleiro[origem[0]][origem[1] + 4] = PecaVazia()

        # Mover a peça
        tabuleiro[destino[0]][destino[1]] = peca_origem
        tabuleiro[origem[0]][origem[1]] = PecaVazia()

        # verificando se o peao foi promovido
        if isinstance(peca_origem, Peao) and destino[0] == 7 or destino[0] == 0:
            tabuleiro[destino[0]][destino[1]] = Rainha("Rainha", peca_origem.cor, sprites[f'Q{peca_origem.cor}'])

        # Marcar que o rei ou a torre já se moveram
        if isinstance(peca_origem, Rei) or isinstance(peca_origem, Torre):
            peca_origem.ja_moveu = True

        return True
    return False


def iniciar_novo_jogo():
    tabuleiro = inicializar_tabuleiro()

    selecionada = None
    turno_brancas = True  # True para brancas, False para pretas
    rodando = True
    clock = pygame.time.Clock()

    # Desenhar o tabuleiro completo e as peças na primeira vez que o jogo abre
    desenhar_tabuleiro()
    desenhar_pecas(tabuleiro)
    pygame.display.update()  # Atualiza a tela completa inicialmente

    while rodando:
        # Limitar a taxa de quadros para melhorar a performance
        clock.tick(30)  # Define o máximo de 30 FPS

        # Verificação dos eventos do Pygame
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN:
                pos_x, pos_y = pygame.mouse.get_pos()
                coluna = pos_x // TAMANHO_QUADRADO
                linha = pos_y // TAMANHO_QUADRADO

                if selecionada:
                    # Tentativa de mover a peça
                    destino = (linha, coluna)

                    # Verificar se o movimento é válido e realiza a movimentação
                    if mover_peca(selecionada, destino, tabuleiro, turno_brancas):
                        # Atualizar o quadrado de origem (desenhar o fundo do quadrado)
                        origem_rect = pygame.Rect(
                            selecionada[1] * TAMANHO_QUADRADO,
                            selecionada[0] * TAMANHO_QUADRADO,
                            TAMANHO_QUADRADO,
                            TAMANHO_QUADRADO
                        )
                        cor_origem = BEGE if (selecionada[0] + selecionada[1]) % 2 == 0 else VERDE
                        pygame.draw.rect(tela, cor_origem, origem_rect)

                        # Atualizar o quadrado de destino
                        destino_rect = pygame.Rect(
                            coluna * TAMANHO_QUADRADO,
                            linha * TAMANHO_QUADRADO,
                            TAMANHO_QUADRADO,
                            TAMANHO_QUADRADO
                        )
                        cor_destino = BEGE if (linha + coluna) % 2 == 0 else VERDE
                        pygame.draw.rect(tela, cor_destino, destino_rect)

                        # Redesenhar as peças no tabuleiro
                        desenhar_pecas(tabuleiro)

                        # Atualizar apenas as áreas que foram afetadas (origem e destino)
                        pygame.display.update([origem_rect, destino_rect])

                        # Alternar o turno após o movimento
                        turno_brancas = not turno_brancas

                    selecionada = None  # Desmarcar a peça selecionada
                    desenhar_tabuleiro()
                    desenhar_pecas(tabuleiro)
                    pygame.display.update()

                else:
                    # Selecionar a peça se for do turno correto
                    peca_selecionada = tabuleiro[linha][coluna]
                    if not isinstance(peca_selecionada, PecaVazia) and \
                            ((peca_selecionada.cor == "B" and turno_brancas) or
                             (peca_selecionada.cor == "P" and not turno_brancas)):
                        selecionada = (linha, coluna)
                        desenhar_tabuleiro()
                        desenhar_pecas(tabuleiro)
                        pygame.draw.rect(tela, AZUL,
                                         pygame.Rect(coluna * TAMANHO_QUADRADO, linha * TAMANHO_QUADRADO,
                                                     TAMANHO_QUADRADO, TAMANHO_QUADRADO), 3)
                        pygame.display.update()

# Função principal do jogo
def main():
    iniciar_novo_jogo()


if __name__ == "__main__":
    main()
