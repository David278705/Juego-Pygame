import pygame  # Importa el módulo pygame para desarrollo de juegos
from gangster import Gangster, load_images_from_folder  # Importa la clase Gangster y función para cargar imágenes
from main_menu import show_main_menu  # Importa la función para mostrar el menú principal
import random  # Importa el módulo random para generar valores aleatorios

# Inicialización de Pygame
pygame.init()

# Inicialización del mezclador de sonido
pygame.mixer.init()

# Cargar efectos de sonido
click_sound = pygame.mixer.Sound('./click.mp3')  # Sonido al hacer clic
death_sound = pygame.mixer.Sound('./death.mp3')  # Sonido al morir
shot_sound = pygame.mixer.Sound('./shot.mp3')    # Sonido de disparo

# Configuración de pantalla
WIDTH, HEIGHT = 1000, 800  # Dimensiones de la ventana del juego
TAMANIO_CELDA = 40         # Tamaño de cada celda en el mapa
PLATFORM_HEIGHT = 20       # Altura de las plataformas
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Crea la ventana del juego
pygame.display.set_caption("Gangster Levels")       # Establece el título de la ventana

# Colores
WHITE = (255, 255, 255)  # Color blanco en RGB
BLACK = (0, 0, 0)        # Color negro en RGB

# Configuración del reloj para controlar los FPS
clock = pygame.time.Clock()

# Cargar y escalar la imagen de fondo para que cubra toda la pantalla
background_image = pygame.image.load("./bg.jpg")  # Carga la imagen de fondo
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))  # Escala la imagen al tamaño de la ventana

# Cargar y escalar la imagen de la pistola
gun_image = pygame.image.load('./pistola.png')  # Carga la imagen de la pistola
gun_image = pygame.transform.scale(gun_image, (TAMANIO_CELDA, TAMANIO_CELDA))  # Escala la imagen al tamaño de una celda

# Cargar las imágenes de las plataformas y escalarlas
platform_left_image = pygame.image.load('platform/platform-left.png')  # Imagen de la plataforma izquierda
platform_left_image = pygame.transform.scale(platform_left_image, (TAMANIO_CELDA, PLATFORM_HEIGHT))  # Escala la imagen

platform_center_image = pygame.image.load('platform/platform.png')  # Imagen de la plataforma central
platform_center_image = pygame.transform.scale(platform_center_image, (TAMANIO_CELDA, PLATFORM_HEIGHT))  # Escala la imagen

platform_right_image = pygame.image.load('platform/platform-right.png')  # Imagen de la plataforma derecha
platform_right_image = pygame.transform.scale(platform_right_image, (TAMANIO_CELDA, PLATFORM_HEIGHT))  # Escala la imagen

# Cargar y escalar la imagen de los pinchos
spike_image = pygame.image.load('pinchos.png')  # Carga la imagen de los pinchos
spike_image = pygame.transform.scale(spike_image, (TAMANIO_CELDA, TAMANIO_CELDA))  # Escala la imagen
spike_mask = pygame.mask.from_surface(spike_image)  # Crea una máscara para detección precisa de colisiones

# Cargar y escalar la imagen de la puerta
door_image = pygame.image.load('door.png')  # Carga la imagen de la puerta
door_image = pygame.transform.scale(door_image, (TAMANIO_CELDA * 2, TAMANIO_CELDA * 2.5))  # Escala la imagen

# Definir el mapa del nivel (comentado porque se genera aleatoriamente más adelante)
# MAPA_NIVEL = [
#     "                      W   ",
#     "                          ",
#     "          P               ",
#     "    XXXXXXXXXXXXXXXXXXXXXX",
#     "                          ",
#     "                          ",
#     "G      P       P          ",  # Añadimos la pistola aquí
#     "XXXXXXXXXXXXXXXXXXXXXX    ",
#     "                          ",
#     "                          ",
#     "           P          P   ",
#     "    XXXXXXXXXXXXXXXXXXXXXX",
#     "                          ",
#     "                          ",
#     "    P        PP           ",
#     "XXXXXXXXXXXXX  XXXXXXX    ",
#     "                          ",
#     "                          ",
#     "         P         P      ",
#     "XXXXXXXXXXXXXXXXXXXXXXXXXXX",
# ]

def generar_mapa_random():
    base_mapa = [
        "                      W   ",  # 'W' representa la puerta de salida
        "                          ",
        "                          ",
        "    XXXXXXXXXXXXXXXXXXXXXX",  # 'X' representa una plataforma
        "                          ",
        "                          ",
        "                          ",
        "XXXXXXXXXXXXXXXXXXXXXX    ",
        "                          ",
        "                          ",
        "                          ",
        "    XXXXXXXXXXXXXXXXXXXXXX",
        "                          ",
        "                          ",
        "                          ",
        "XXXXXXXXXXXXXXXXXXXXXX    ",
        "                          ",
        "                          ",
        "                          ",
        "XXXXXXXXXXXXXXXXXXXXXXXXXXX",
    ]
    
    # Encontrar la longitud máxima de las filas
    max_length = max(len(row) for row in base_mapa)
    
    # Rellenar las filas más cortas con espacios para que todas tengan la misma longitud
    base_mapa_padded = [row.ljust(max_length) for row in base_mapa]
    
    # Eliminar cualquier 'P' (pinchos) o 'G' (pistolas) existente
    mapa_sin_PG = [row.replace('P', ' ').replace('G', ' ') for row in base_mapa_padded]
    
    NUM_ROWS = len(mapa_sin_PG)      # Número de filas en el mapa
    NUM_COLS = len(mapa_sin_PG[0])   # Número de columnas en el mapa
    
    # Posición de aparición de los jugadores en términos de índices de mapa
    spawn_positions = [(16, 1)]  # Lista de posiciones de spawn a evitar (fila 16, columna 1)
    
    # Obtener todas las posiciones donde hay plataformas 'X'
    posiciones_X = []
    for row_idx in range(1, NUM_ROWS):  # Empezar desde la segunda fila para evitar la primera
        row = mapa_sin_PG[row_idx]
        for col_idx, cell in enumerate(row):
            if cell == 'X':
                posiciones_X.append((row_idx, col_idx))
    
    # Obtener posiciones donde se pueden colocar pinchos 'P' y pistolas 'G' (encima de plataformas)
    posiciones_sobre_X = []
    for (row_idx, col_idx) in posiciones_X:
        if row_idx > 0:
            # Asegurar que col_idx esté dentro del rango de la fila anterior
            if col_idx < len(mapa_sin_PG[row_idx - 1]):
                cell_above = mapa_sin_PG[row_idx - 1][col_idx]
                if cell_above == ' ':
                    posiciones_sobre_X.append((row_idx - 1, col_idx))
    
    # Definir una función para verificar si una posición está cerca del spawn
    def esta_cerca_de_spawn(pos, spawn_positions, rango_x=3, rango_y=3):
        for spawn in spawn_positions:
            if abs(pos[0] - spawn[0]) <= rango_y and abs(pos[1] - spawn[1]) <= rango_x:
                return True
        return False

    # Excluir posiciones cercanas al spawn de los jugadores
    posiciones_sobre_X = [
        pos for pos in posiciones_sobre_X 
        if not esta_cerca_de_spawn(pos, spawn_positions)
    ]
    
    # Excluir la primera fila para evitar colocar elementos en ella
    posiciones_sobre_X = [pos for pos in posiciones_sobre_X if pos[0] > 0]
    
    # Mezclar posiciones aleatoriamente
    random.shuffle(posiciones_sobre_X)
    
    # Seleccionar 13 posiciones para los pinchos 'P'
    posiciones_P = posiciones_sobre_X[:13]
    posiciones_restantes = posiciones_sobre_X[13:]
    
    # Seleccionar posiciones para las pistolas 'G' en los costados y en diferentes niveles
    posiciones_sobre_X_left = [pos for pos in posiciones_restantes if pos[1] <= NUM_COLS // 3]
    posiciones_sobre_X_right = [pos for pos in posiciones_restantes if pos[1] >= 2 * NUM_COLS // 3]
    
    posiciones_G = []
    niveles_ocupados_por_G = set()
    
    # Función auxiliar para seleccionar una posición de pistola en un lado
    def seleccionar_pistola_en_lado(posiciones_lado):
        for pos in posiciones_lado:
            nivel = pos[0]
            if nivel not in niveles_ocupados_por_G:
                niveles_ocupados_por_G.add(nivel)
                return pos
        return None  # Si no se encuentra una posición en un nivel diferente
    
    # Seleccionar pistola en el lado izquierdo
    posicion_G_left = seleccionar_pistola_en_lado(posiciones_sobre_X_left)
    if posicion_G_left:
        posiciones_G.append(posicion_G_left)
        posiciones_restantes.remove(posicion_G_left)
    
    # Seleccionar pistola en el lado derecho
    posicion_G_right = seleccionar_pistola_en_lado(posiciones_sobre_X_right)
    if posicion_G_right:
        posiciones_G.append(posicion_G_right)
        posiciones_restantes.remove(posicion_G_right)
    
    # Si aún no hay 2 pistolas, seleccionar de las posiciones restantes en niveles diferentes
    while len(posiciones_G) < 2 and posiciones_restantes:
        pos = posiciones_restantes.pop()
        nivel = pos[0]
        if nivel not in niveles_ocupados_por_G:
            niveles_ocupados_por_G.add(nivel)
            posiciones_G.append(pos)
    
    # Crear el nuevo mapa con pinchos 'P' y pistolas 'G'
    mapa_con_PG = [list(row) for row in mapa_sin_PG]
    
    # Colocar los pinchos 'P' en el mapa
    for (row_idx, col_idx) in posiciones_P:
        mapa_con_PG[row_idx][col_idx] = 'P'
        
    # Colocar las pistolas 'G' en el mapa
    for (row_idx, col_idx) in posiciones_G:
        mapa_con_PG[row_idx][col_idx] = 'G'
        
    # Convertir las filas de nuevo a cadenas
    mapa_final = [''.join(row) for row in mapa_con_PG]
    
    return mapa_final

# Generar el mapa del nivel de forma aleatoria
MAPA_NIVEL = generar_mapa_random()

def cargar_imagenes_personajes():
    # Cargar imágenes de animación para el personaje 1
    gangster1_run_images = load_images_from_folder('./gangster_1/run')   # Imágenes de correr
    gangster1_jump_images = load_images_from_folder('./gangster_1/jump') # Imágenes de salto
    gangster1_idle_images = load_images_from_folder('./gangster_1/idle') # Imágenes en reposo

    # Cargar imágenes de animación para el personaje 2
    gangster2_run_images = load_images_from_folder('./gangster_2/run')   # Imágenes de correr
    gangster2_jump_images = load_images_from_folder('./gangster_2/jump') # Imágenes de salto
    gangster2_idle_images = load_images_from_folder('./gangster_2/idle') # Imágenes en reposo

    # Retornar las imágenes cargadas como una tupla de tuplas
    return ((gangster1_run_images, gangster1_jump_images, gangster1_idle_images),
            (gangster2_run_images, gangster2_jump_images, gangster2_idle_images))

def crear_instancias_personajes(gangster1_images, gangster2_images):
    # Crear instancia del personaje 1 en la posición inicial (50, 670)
    gangster1 = Gangster(50, 670, *gangster1_images)
    gangster1.idle_images = gangster1_images[2]  # Asegurar que las imágenes en reposo estén definidas

    # Crear instancia del personaje 2 en la misma posición inicial
    gangster2 = Gangster(50, 670, *gangster2_images)
    gangster2.idle_images = gangster2_images[2]  # Asegurar que las imágenes en reposo estén definidas

    return gangster1, gangster2  # Retornar las instancias creadas

def crear_elementos_nivel(mapa_nivel):
    plataformas = []  # Lista para almacenar las plataformas
    monedas = []      # Lista para almacenar las monedas
    spikes = []       # Lista para almacenar los pinchos
    guns = []         # Lista para almacenar las pistolas
    door = None       # Variable para la puerta de salida

    NUM_COLS = len(mapa_nivel[0])  # Número de columnas en el mapa

    # Recorrer cada celda del mapa para identificar y crear elementos
    for fila_indice, fila in enumerate(mapa_nivel):
        for col_indice, celda in enumerate(fila):
            x = col_indice * TAMANIO_CELDA  # Coordenada x de la celda
            y = fila_indice * TAMANIO_CELDA + (TAMANIO_CELDA - PLATFORM_HEIGHT)  # Coordenada y de la celda
            if celda == 'X':
                # Determinar el tipo de plataforma (izquierda, centro, derecha)
                tipo = determinar_tipo_plataforma(fila, col_indice)
                plataforma = {'rect': pygame.Rect(x, y, TAMANIO_CELDA, PLATFORM_HEIGHT), 'type': tipo}
                plataformas.append(plataforma)  # Agregar la plataforma a la lista
            elif celda == 'O':
                # Crear una moneda y agregarla a la lista
                moneda = pygame.Rect(x + 10, y + 10, 20, 20)
                monedas.append(moneda)
            elif celda == 'P':
                # Crear un pincho y agregarlo a la lista
                spike_rect = pygame.Rect(x, y + PLATFORM_HEIGHT, TAMANIO_CELDA, TAMANIO_CELDA)
                spikes.append({'rect': spike_rect, 'mask': spike_mask})
            elif celda == 'W':
                # Crear la puerta de salida
                door = pygame.Rect(x, y+20, TAMANIO_CELDA * 3, TAMANIO_CELDA * 2)
            elif celda == 'G':
                # Crear una pistola y determinar su dirección
                gun_rect = pygame.Rect(x, y, TAMANIO_CELDA, TAMANIO_CELDA)
                if col_indice < NUM_COLS // 2:
                    direction = 1  # Apunta a la derecha
                else:
                    direction = -1  # Apunta a la izquierda
                gun = {'rect': gun_rect, 'cooldown': 0, 'direction': direction}
                guns.append(gun)  # Agregar la pistola a la lista

    return plataformas, monedas, spikes, guns, door  # Retornar los elementos del nivel

def determinar_tipo_plataforma(fila, col_indice):
    # Determina si la plataforma es izquierda, central, derecha o individual
    if col_indice == 0 or fila[col_indice - 1] != 'X':
        if col_indice + 1 < len(fila) and fila[col_indice + 1] == 'X':
            return 'left'   # Inicio de una plataforma
        else:
            return 'single' # Plataforma individual
    elif col_indice + 1 == len(fila) or fila[col_indice + 1] != 'X':
        return 'right'  # Final de una plataforma
    else:
        return 'center' # Parte central de una plataforma

# Función para manejar colisiones con plataformas
def detectar_colision_con_plataformas(gangster, plataformas):
    gangster.is_jumping = True  # Asume que el personaje está en el aire

    # Colisiones con los bordes de la ventana
    if gangster.rect.left < 0:  # Límite izquierdo
        gangster.rect.left = 0
        gangster.vel_x = 0
    elif gangster.rect.right > WIDTH:  # Límite derecho
        gangster.rect.right = WIDTH
        gangster.vel_x = 0
    if gangster.rect.top < 0:  # Límite superior
        gangster.rect.top = 0
        gangster.vel_y = 0
    elif gangster.rect.bottom > HEIGHT:  # Límite inferior
        gangster.rect.bottom = HEIGHT
        gangster.vel_y = 0
        gangster.is_jumping = False  # Aterriza si toca el suelo

    # Colisiones con plataformas
    for plataforma in plataformas:
        plat_rect = plataforma['rect']
        if gangster.rect.colliderect(plat_rect):
            # Colisión desde arriba
            if gangster.vel_y > 0 and gangster.rect.bottom <= plat_rect.top + abs(gangster.vel_y):
                gangster.rect.bottom = plat_rect.top
                gangster.vel_y = 0
                gangster.is_jumping = False
                gangster.is_jumping_animation = False
            # Colisión desde abajo
            elif gangster.vel_y < 0 and gangster.rect.top >= plat_rect.bottom - abs(gangster.vel_y):
                gangster.rect.top = plat_rect.bottom
                gangster.vel_y = 2  # Hace que el personaje caiga nuevamente
            # Colisión por el lado izquierdo
            elif gangster.vel_x > 0 and gangster.rect.right >= plat_rect.left and gangster.rect.left < plat_rect.left:
                gangster.rect.right = plat_rect.left
                gangster.vel_x = 0  # Detiene el movimiento hacia la derecha
            # Colisión por el lado derecho
            elif gangster.vel_x < 0 and gangster.rect.left <= plat_rect.right and gangster.rect.right > plat_rect.right:
                gangster.rect.left = plat_rect.right
                gangster.vel_x = 0  # Detiene el movimiento hacia la izquierda

def manejar_colision_plataforma(gangster, plat_rect):
    # Maneja colisiones específicas con una plataforma
    if gangster.vel_y > 0 and gangster.rect.bottom <= plat_rect.top + abs(gangster.vel_y):
        gangster.rect.bottom = plat_rect.top
        gangster.vel_y = 0
        gangster.is_jumping = False
        gangster.time_jump = 0
        gangster.is_jumping_animation = False
    elif gangster.vel_y < 0 and gangster.rect.top >= plat_rect.bottom - abs(gangster.vel_y):
        gangster.rect.top = plat_rect.bottom
        gangster.vel_y = 2
    elif gangster.vel_x > 0 and gangster.rect.right >= plat_rect.left and gangster.rect.left < plat_rect.left:
        gangster.rect.right = plat_rect.left
        gangster.vel_x = 0
    elif gangster.vel_x < 0 and gangster.rect.left <= plat_rect.right and gangster.rect.right > plat_rect.right:
        gangster.rect.left = plat_rect.right
        gangster.vel_x = 0

def detectar_colision_con_pinchos(gangster, spikes):
    # Función para detectar colisiones entre el personaje y los pinchos
    for spike in spikes:
        spike_rect = spike['rect']
        spike_mask = spike['mask']
        # Calcular el desplazamiento entre el pincho y el personaje
        offset = (spike_rect.x - gangster.rect.x, spike_rect.y - gangster.rect.y)
        # Comprobar si las máscaras de colisión se solapan
        if gangster.mask.overlap(spike_mask, offset):
            # Reiniciar la posición del personaje al punto de inicio
            gangster.rect.x = gangster.start_x
            gangster.rect.y = gangster.start_y
            gangster.is_jumping = True  # El personaje está en el aire después de reiniciar
            break  # Salir del bucle después de detectar una colisión

def detectar_colision_con_monedas(gangster, monedas):
    # Función para detectar colisiones entre el personaje y las monedas
    for moneda in monedas[:]:  # Iterar sobre una copia de la lista
        if gangster.rect.colliderect(moneda):
            monedas.remove(moneda)  # Eliminar la moneda si se recoge

def detectar_colision_con_puerta(gangster, door):
    # Función para detectar si el personaje ha llegado a la puerta
    if door and gangster.rect.colliderect(door):
        return True  # El personaje ha llegado a la puerta
    return False  # El personaje no ha llegado a la puerta

def show_winner(screen, gangster, idle_image, click_sound):
    # Función para mostrar la pantalla de ganador
    font = pygame.font.Font(None, 74)
    winner_text = font.render(f'{gangster} Wins!', True, WHITE)
    winner_rect = winner_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))

    font_small = pygame.font.Font(None, 50)
    replay_text = font_small.render('Replay', True, WHITE)
    main_menu_text = font_small.render('Main Menu', True, WHITE)
    replay_rect = replay_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    main_menu_rect = main_menu_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))

    # Dibujar elementos en la pantalla
    screen.fill(BLACK)
    screen.blit(winner_text, winner_rect)
    screen.blit(idle_image, (WIDTH // 2 - idle_image.get_width() // 2, HEIGHT // 2 - idle_image.get_height() // 2 - 50))
    pygame.draw.rect(screen, BLACK, replay_rect.inflate(20, 20), border_radius=10)  # Fondo del botón 'Replay'
    screen.blit(replay_text, replay_rect)
    pygame.draw.rect(screen, BLACK, main_menu_rect.inflate(20, 20), border_radius=10)  # Fondo del botón 'Main Menu'
    screen.blit(main_menu_text, main_menu_rect)
    pygame.display.flip()

    # Bucle para manejar eventos en la pantalla de ganador
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if replay_rect.collidepoint(event.pos):
                    click_sound.play()
                    return 'replay'  # El usuario quiere volver a jugar
                elif main_menu_rect.collidepoint(event.pos):
                    click_sound.play()
                    return 'main_menu'  # El usuario quiere ir al menú principal

        pygame.time.Clock().tick(60)  # Control de FPS

def show_pause_menu(screen, click_sound):
    # Función para mostrar el menú de pausa
    font = pygame.font.Font(None, 74)
    resume_text = font.render('Resume', True, WHITE)
    main_menu_text = font.render('Main Menu', True, WHITE)
    resume_rect = resume_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    main_menu_rect = main_menu_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

    while True:
        # Dibujar elementos en la pantalla de pausa
        screen.fill(BLACK)
        pygame.draw.rect(screen, BLACK, resume_rect.inflate(20, 20), border_radius=10)  # Fondo del botón 'Resume'
        screen.blit(resume_text, resume_rect)
        pygame.draw.rect(screen, BLACK, main_menu_rect.inflate(20, 20), border_radius=10)  # Fondo del botón 'Main Menu'
        screen.blit(main_menu_text, main_menu_rect)
        pygame.display.flip()

        # Manejar eventos en el menú de pausa
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'resume'  # Continuar el juego
                elif event.key == pygame.K_RETURN:
                    # Obtener la posición del ratón para detectar en qué botón se hizo clic
                    mouse_pos = pygame.mouse.get_pos()
                    if resume_rect.collidepoint(mouse_pos):
                        click_sound.play()
                        return 'resume'  # Continuar el juego
                    elif main_menu_rect.collidepoint(mouse_pos):
                        click_sound.play()
                        return 'main_menu'  # Ir al menú principal
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if resume_rect.collidepoint(event.pos):
                    click_sound.play()
                    return 'resume'  # Continuar el juego
                elif main_menu_rect.collidepoint(event.pos):
                    click_sound.play()
                    return 'main_menu'  # Ir al menú principal

        pygame.time.Clock().tick(60)  # Control de FPS

class Bullet:
    # Clase para representar una bala disparada por una pistola
    def __init__(self, x, y, direction):
        self.image = pygame.Surface((10, 10))  # Crear una superficie para la bala
        self.image.fill((255, 255, 0))  # Color amarillo para la bala
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vel_x = direction * 3  # Velocidad de la bala en el eje X

    def update(self):
        # Actualizar la posición de la bala
        self.rect.x += self.vel_x

    def draw(self, screen):
        # Dibujar la bala en la pantalla
        screen.blit(self.image, self.rect)

def main():
    # Función principal del juego
    while True:
        show_main_menu(screen, background_image, click_sound)  # Mostrar el menú principal
        # Detener la música del menú principal al iniciar el juego
        pygame.mixer.music.stop()
        gangster1_images, gangster2_images = cargar_imagenes_personajes()  # Cargar imágenes de los personajes
        gangster1, gangster2 = crear_instancias_personajes(gangster1_images, gangster2_images)  # Crear instancias de los personajes
        
        MAPA_NIVEL = generar_mapa_random()  # Generar un mapa aleatorio
        plataformas, monedas, spikes, guns, door = crear_elementos_nivel(MAPA_NIVEL)  # Crear elementos del nivel
        bullets = []  # Lista para almacenar las balas
        paused = False  # Bandera para el estado de pausa
        running = True  # Bandera para el estado del juego

        def replay_game():
            # Función para reiniciar el juego
            nonlocal MAPA_NIVEL, plataformas, monedas, spikes, guns, door
            MAPA_NIVEL = generar_mapa_random()
            plataformas, monedas, spikes, guns, door = crear_elementos_nivel(MAPA_NIVEL)
            bullets.clear()
            # Reiniciar posiciones y estados de los personajes
            gangster1.rect.x = gangster1.start_x
            gangster1.rect.y = gangster1.start_y
            gangster2.rect.x = gangster2.start_x
            gangster2.rect.y = gangster2.start_y
            gangster1.is_jumping = True
            gangster1.time_jump = 0
            gangster2.is_jumping = True
            gangster2.time_jump = 0

        while running:
            clock.tick(60)  # Control de FPS
            screen.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:  # Manejar eventos de teclado
                    if event.key == pygame.K_ESCAPE:
                        paused = True  # Pausar el juego
                    elif event.key == pygame.K_0:
                        replay_game()  # Reiniciar el juego

            screen.blit(background_image, (0, 0))  # Dibujar el fondo
            keys = pygame.key.get_pressed()  # Obtener las teclas presionadas

            # Mover y actualizar el personaje 1
            gangster1.move(keys, pygame.K_a, pygame.K_d, pygame.K_w)
            gangster1.apply_gravity()
            detectar_colision_con_plataformas(gangster1, plataformas)
            detectar_colision_con_pinchos(gangster1, spikes)
            detectar_colision_con_monedas(gangster1, monedas)
            gangster1.update()

            # Mover y actualizar el personaje 2
            gangster2.move(keys, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP)
            gangster2.apply_gravity()
            detectar_colision_con_plataformas(gangster2, plataformas)
            detectar_colision_con_pinchos(gangster2, spikes)
            detectar_colision_con_monedas(gangster2, monedas)
            gangster2.update()

            # Manejo de las pistolas y las balas
            for gun in guns:
                if gun['cooldown'] > 0:
                    gun['cooldown'] -= 1  # Reducir el tiempo de enfriamiento
                else:
                    # Crear una nueva bala
                    bullet_x = gun['rect'].centerx
                    bullet_y = gun['rect'].centery
                    bullet = Bullet(bullet_x, bullet_y, direction=gun['direction'])
                    bullets.append(bullet)
                    gun['cooldown'] = 120  # Restablecer el enfriamiento
                    shot_sound.play()  # Reproducir sonido de disparo

            # Actualizar y dibujar las balas
            for bullet in bullets[:]:
                bullet.update()
                if bullet.rect.x > WIDTH or bullet.rect.x < 0:
                    bullets.remove(bullet)  # Eliminar la bala si sale de la pantalla
                else:
                    # Comprobar colisión con el personaje 1
                    if bullet.rect.colliderect(gangster1.rect):
                        death_sound.play()  # Reproducir sonido de muerte
                        gangster1.rect.x = gangster1.start_x  # Reiniciar posición
                        gangster1.rect.y = gangster1.start_y
                        gangster1.is_jumping = True
                        bullets.remove(bullet)
                    # Comprobar colisión con el personaje 2
                    elif bullet.rect.colliderect(gangster2.rect):
                        death_sound.play()  # Reproducir sonido de muerte
                        gangster2.rect.x = gangster2.start_x  # Reiniciar posición
                        gangster2.rect.y = gangster2.start_y
                        gangster2.is_jumping = True
                        bullets.remove(bullet)

            # Comprobar si el personaje 1 ha llegado a la puerta
            if detectar_colision_con_puerta(gangster1, door):
                action = show_winner(screen, "Gangster 1", gangster1.idle_images[0], click_sound)
                if action == 'replay':
                    MAPA_NIVEL = generar_mapa_random()
                    plataformas, monedas, spikes, guns, door = crear_elementos_nivel(MAPA_NIVEL)
                    bullets.clear()  # Limpiar las balas existentes
                    # Reiniciar posiciones y estados de los personajes
                    gangster1.rect.x = gangster1.start_x
                    gangster1.rect.y = gangster1.start_y
                    gangster2.rect.x = gangster2.start_x
                    gangster2.rect.y = gangster2.start_y
                    gangster1.is_jumping = True
                    gangster1.time_jump = 0
                    gangster2.is_jumping = True
                    gangster2.time_jump = 0
                elif action == 'main_menu':
                    running = False  # Salir al menú principal
            # Comprobar si el personaje 2 ha llegado a la puerta
            elif detectar_colision_con_puerta(gangster2, door):
                action = show_winner(screen, "Gangster 2", gangster2.idle_images[0], click_sound)
                if action == 'replay':
                    MAPA_NIVEL = generar_mapa_random()
                    plataformas, monedas, spikes, guns, door = crear_elementos_nivel(MAPA_NIVEL)
                    bullets.clear()  # Limpiar las balas existentes
                    # Reiniciar posiciones y estados de los personajes
                    gangster1.rect.x = gangster1.start_x
                    gangster1.rect.y = gangster1.start_y
                    gangster2.rect.x = gangster2.start_x
                    gangster2.rect.y = gangster2.start_y
                    gangster1.is_jumping = True
                    gangster1.time_jump = 0
                    gangster2.is_jumping = True
                    gangster2.time_jump = 0
                elif action == 'main_menu':
                    running = False  # Salir al menú principal

            # Dibujar todos los elementos en la pantalla
            dibujar_elementos(screen, plataformas, monedas, spikes, guns, bullets, door, gangster1, gangster2)

            pygame.display.flip()  # Actualizar la pantalla

            if paused:
                # Mostrar el menú de pausa
                action = show_pause_menu(screen, click_sound)  # Pasar click_sound
                if action == 'resume':
                    paused = False  # Continuar el juego
                elif action == 'main_menu':
                    running = False  # Salir al menú principal
                    break

    pygame.quit()  # Salir del juego

def dibujar_elementos(screen, plataformas, monedas, spikes, guns, bullets, door, gangster1, gangster2):
    # Función para dibujar todos los elementos en la pantalla
    for plataforma in plataformas:
        plat_rect = plataforma['rect']
        tipo = plataforma['type']
        if tipo == 'left':
            screen.blit(platform_left_image, plat_rect)  # Dibujar plataforma izquierda
        elif tipo == 'center':
            screen.blit(platform_center_image, plat_rect)  # Dibujar plataforma central
        elif tipo == 'right':
            screen.blit(platform_right_image, plat_rect)  # Dibujar plataforma derecha
        elif tipo == 'single':
            screen.blit(platform_center_image, plat_rect)  # Dibujar plataforma individual

    for moneda in monedas:
        pygame.draw.ellipse(screen, (255, 215, 0), moneda)  # Dibujar las monedas

    for spike_rect in spikes:
        screen.blit(spike_image, spike_rect['rect'])  # Dibujar los pinchos

    for gun in guns:
        if gun['direction'] == 1:
            # Voltear la imagen para que mire a la derecha
            image = pygame.transform.flip(gun_image, True, False)
        else:
            image = gun_image  # La imagen mira a la izquierda por defecto
        screen.blit(image, gun['rect'].topleft)  # Dibujar las pistolas

    for bullet in bullets:
        bullet.draw(screen)  # Dibujar las balas

    if door:
        screen.blit(door_image, door.topleft)  # Dibujar la puerta

    gangster1.draw(screen)  # Dibujar el personaje 1
    gangster2.draw(screen)  # Dibujar el personaje 2

if __name__ == "__main__":
    main()  # Ejecutar el juego
