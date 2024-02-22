import os
import random
import pygame
import neat

# Inicialización de Pygame y configuración de la ventana
pygame.init()
WIN_WIDTH, WIN_HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Space War - Antonio Barrera Reyzabal")

# Definición de colores básicos
BLACK = (0, 0, 0)

# Parámetros generales del juego
FPS = 60
GAME_FONT = pygame.font.SysFont('Arial', 20)

# Parámetros de la nave
NAVE_WIDTH, NAVE_HEIGHT = 50, 50
NAVE_MAX_VEL = 5

# Parámetros de los obstáculos
OBSTACULO_MIN_VEL, OBSTACULO_MAX_VEL = 2, 6
OBSTACULO_MIN_SIZE, OBSTACULO_MAX_SIZE = 20, 60

# Carga y configuración de imágenes
BACKGROUND_IMG = pygame.transform.scale(pygame.image.load(os.path.join('imagenes', 'escenario_naves.jpg')), (WIN_WIDTH, WIN_HEIGHT))
NAVE_IMG = pygame.transform.scale(pygame.image.load(os.path.join('imagenes', 'nave.png')), (NAVE_WIDTH, NAVE_HEIGHT))
OBSTACULO_IMG = pygame.image.load(os.path.join('imagenes', 'bullet_.png'))

MARGEN = 40

# Clase Nave: Representa al jugador en el juego
class Nave:
    def __init__(self):
        self.x = WIN_WIDTH // 2
        self.y = WIN_HEIGHT - 100
        self.width = NAVE_WIDTH
        self.height = NAVE_HEIGHT
        self.vel = NAVE_MAX_VEL
        self.img = NAVE_IMG
    
    def draw(self, win):
        win.blit(self.img, (self.x, self.y))

    def collide(self, obstaculo):
        nave_mask = pygame.mask.from_surface(self.img)
        obstaculo_mask = pygame.mask.from_surface(obstaculo.img)

        offset = (obstaculo.x - self.x, obstaculo.y - self.y)
        punto_colision = nave_mask.overlap(obstaculo_mask, offset)

        return punto_colision is not None

# Clase Obstaculo: Representa los enemigos en el juego
class Obstaculo:
    def __init__(self):
        self.width = random.randint(OBSTACULO_MIN_SIZE, OBSTACULO_MAX_SIZE)
        self.height = self.width
        self.x = random.randint(0, WIN_WIDTH - self.width)
        self.y = -self.height
        self.vel = random.randint(OBSTACULO_MIN_VEL, OBSTACULO_MAX_VEL)
        self.img = pygame.transform.scale(OBSTACULO_IMG, (self.width, self.height))
        self.esquivado = False
    
    def draw(self, win):
        win.blit(self.img, (self.x, self.y))
    
    def update(self):
        self.y += self.vel

# Función auxiliar para calcular distancia
def distance(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

# Variables globales para rastrear el estado del juego
GEN = 0
MAX_SCORE = 0
GEN_AT_MAX_SCORE = 0

# Función principal de evaluación para NEAT
def eval_genomes(genomes, config):
    # Inicialización de listas para redes neuronales, genomas y naves.
    nets = []
    ge = []
    naves = []

    # Reinicio de la ventana de visualización y del reloj de Pygame.
    global WIN, GEN, MAX_SCORE, GEN_AT_MAX_SCORE
    WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    # Creación inicial de obstáculos en el juego.
    obstaculos = [Obstaculo() for _ in range(5)]
    GEN += 1  # Incremento del contador de generaciones.
    score = 0  # Puntuación inicial para esta generación.

    # Inicialización de cada genoma y su red neuronal correspondiente.
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)  # Creación de la red neuronal.
        nets.append(net)  # Añadir la red a la lista de redes.
        naves.append(Nave())  # Crear una nueva nave y añadirla a la lista.
        genome.fitness = 0  # Inicializar la fitness del genoma a 0.
        ge.append(genome)  # Añadir el genoma a la lista de genomas.

    # Bucle principal de la simulación.
    run = True
    while run and len(naves) > 0:
        clock.tick(FPS)  # Control de la velocidad del juego.
        WIN.blit(BACKGROUND_IMG, (0, 0))  # Dibujo del fondo de pantalla.

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # Añadir nuevos obstáculos si es necesario para mantener el desafío.
        if len(obstaculos) < 5:
            obstaculos.append(Obstaculo())

        # Actualizar y dibujar obstáculos.
        for obstaculo in obstaculos:
            obstaculo.update()
            obstaculo.draw(WIN)

        # Lista para mantener índices de naves a remover debido a colisiones.
        remove_indices = set()

        # Evaluación de cada nave en el juego.
        for x, nave in enumerate(naves):
            # Identificar los 10 obstáculos más cercanos para la red neuronal.
            obstaculos_cercanos = sorted(obstaculos, key=lambda o: distance(nave.x, nave.y, o.x + o.width / 2, o.y + o.height / 2))[:10]

            # Preparación de las entradas para la red neuronal.
            inputs = [nave.x, nave.y] + [val for obstaculo in obstaculos_cercanos for val in (obstaculo.x + obstaculo.width / 2, obstaculo.y + obstaculo.height / 2)]
            inputs += [0, WIN_HEIGHT] * (10 - len(obstaculos_cercanos))  # Rellenar si hay menos de 10 obstáculos.

            # Activación de la red neuronal con las entradas actuales.
            output = nets[x].activate(inputs)

            # Lógica de movimiento basada en la salida de la red neuronal.
            nave.x += output[0] * 10 - 5
            nave.y += output[1] * 10 - 5

            # Restricciones para mantener la nave dentro de la ventana.
            nave.x = min(max(MARGEN, nave.x), WIN_WIDTH - nave.width - MARGEN)
            nave.y = min(max(MARGEN, nave.y), WIN_HEIGHT - nave.height - MARGEN)

            nave.draw(WIN)  # Dibujar la nave en su nueva posición.

            # Comprobar colisiones y ajustar fitness.
            for obstaculo in obstaculos:
                if nave.collide(obstaculo):
                    ge[x].fitness -= 200  # Penalizar la fitness por colisionar.
                    remove_indices.add(x)  # Marcar la nave para ser eliminada.

            # Recompensar la esquiva de obstáculos.
            for obstaculo in obstaculos:
                if not obstaculo.esquivado and obstaculo.y > nave.y + nave.height:
                    obstaculo.esquivado = True
                    ge[x].fitness += 10  # Recompensa por esquivar obstáculos.

        # Eliminar naves que colisionaron.
        for index in sorted(remove_indices, reverse=True):
            nets.pop(index)
            ge.pop(index)
            naves.pop(index)

        score += 0  # Incrementar puntuación por frame sobrevivido.

        # Dibujar información de la generación, naves activas y puntuación en pantalla.
        gen_text = GAME_FONT.render(f"Gen: {GEN}", True, (255, 255, 255))
        players_text = GAME_FONT.render(f"Players: {len(naves)}", True, (255, 255, 255))
        score_text = GAME_FONT.render(f"Score: {score}", True, (255, 255, 255))
        highest_score_text = GAME_FONT.render(f"Highest Score: {MAX_SCORE} (Gen: {GEN_AT_MAX_SCORE})", True, (255, 255, 255))

        WIN.blit(gen_text, (10, 10))
        WIN.blit(players_text, (10, 30))
        WIN.blit(score_text, (10, 50))
        WIN.blit(highest_score_text, (10, 70))

        pygame.display.update()  # Actualizar la ventana de visualización.

        # Eliminar obstáculos que ya no están en pantalla.
        obstaculos = [o for o in obstaculos if o.y < WIN_HEIGHT]

    # Actualizar el score máximo si es necesario.
    if score > MAX_SCORE:
        MAX_SCORE = score
        GEN_AT_MAX_SCORE = GEN


# Configuración y ejecución de NEAT
def run_neat(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes, 50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run_neat(config_path)
