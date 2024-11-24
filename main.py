import pygame
from gangster import Gangster, load_images_from_folder
from main_menu import show_main_menu
import random


# Inicialización de Pygame
pygame.init()

# Inicialización del mezclador de sonido
pygame.mixer.init()

# Cargar efectos de sonido
click_sound = pygame.mixer.Sound('./click.mp3')
death_sound = pygame.mixer.Sound('./death.mp3')
shot_sound = pygame.mixer.Sound('./shot.mp3')

# Configuración de pantalla
WIDTH, HEIGHT = 1000, 800
TAMANIO_CELDA = 40
PLATFORM_HEIGHT = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gangster Levels")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Configuración del reloj para controlar los FPS
clock = pygame.time.Clock()

# Cargar y escalar la imagen de fondo para que cubra toda la pantalla
background_image = pygame.image.load("./bg.jpg")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Cargar y escalar la imagen de la pistola
gun_image = pygame.image.load('./pistola.png')
gun_image = pygame.transform.scale(gun_image, (TAMANIO_CELDA, TAMANIO_CELDA))


# Cargar las imágenes de las plataformas y escalarlas
platform_left_image = pygame.image.load('platform/platform-left.png')
platform_left_image = pygame.transform.scale(platform_left_image, (TAMANIO_CELDA, PLATFORM_HEIGHT))

platform_center_image = pygame.image.load('platform/platform.png')
platform_center_image = pygame.transform.scale(platform_center_image, (TAMANIO_CELDA, PLATFORM_HEIGHT))

platform_right_image = pygame.image.load('platform/platform-right.png')
platform_right_image = pygame.transform.scale(platform_right_image, (TAMANIO_CELDA, PLATFORM_HEIGHT))

# Cargar y escalar la imagen de los pinchos
spike_image = pygame.image.load('pinchos.png')
spike_image = pygame.transform.scale(spike_image, (TAMANIO_CELDA, TAMANIO_CELDA))
spike_mask = pygame.mask.from_surface(spike_image)

# Cargar y escalar la imagen de la puerta
door_image = pygame.image.load('door.png')
door_image = pygame.transform.scale(door_image, (TAMANIO_CELDA * 2, TAMANIO_CELDA * 2.5))

# Definir el mapa del nivel
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
        "                      W   ",
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
    
    # Eliminar cualquier 'P' o 'G' existente
    mapa_sin_PG = [row.replace('P', ' ').replace('G', ' ') for row in base_mapa_padded]
    
    NUM_ROWS = len(mapa_sin_PG)
    NUM_COLS = len(mapa_sin_PG[0])
    
    # Posición de aparición de los jugadores en términos de índices de mapa
    # Jugador 1: col = 1, row = 16 (calculado a partir de x=50, y=670)
    spawn_positions = [(16, 1)]  # Lista de posiciones de spawn a evitar
    # Puedes agregar aquí las posiciones de spawn de otros jugadores si son diferentes
    
    # Obtener todas las posiciones donde hay 'X's
    posiciones_X = []
    for row_idx in range(1, NUM_ROWS):  # Empezar desde la segunda fila para evitar la primera
        row = mapa_sin_PG[row_idx]
        for col_idx, cell in enumerate(row):
            if cell == 'X':
                posiciones_X.append((row_idx, col_idx))
    
    # Obtener posiciones donde se pueden colocar 'P's y 'G's (encima de 'X's)
    posiciones_sobre_X = []
    for (row_idx, col_idx) in posiciones_X:
        if row_idx > 0:
            # Asegurar que col_idx esté dentro del rango de la fila anterior
            if col_idx < len(mapa_sin_PG[row_idx - 1]):
                cell_above = mapa_sin_PG[row_idx - 1][col_idx]
                if cell_above == ' ':
                    posiciones_sobre_X.append((row_idx - 1, col_idx))
    
    # Excluir posiciones cercanas al spawn de los jugadores
    posiciones_sobre_X = [pos for pos in posiciones_sobre_X if pos not in spawn_positions]
    
    # Excluir la primera fila
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
    
    # Crear el nuevo mapa con 'P's y 'G's
    mapa_con_PG = [list(row) for row in mapa_sin_PG]
    
    # Colocar los pinchos 'P'
    for (row_idx, col_idx) in posiciones_P:
        mapa_con_PG[row_idx][col_idx] = 'P'
        
    # Colocar las pistolas 'G'
    for (row_idx, col_idx) in posiciones_G:
        mapa_con_PG[row_idx][col_idx] = 'G'
        
    # Convertir las filas de nuevo a cadenas
    mapa_final = [''.join(row) for row in mapa_con_PG]
    
    return mapa_final



MAPA_NIVEL = generar_mapa_random()


def cargar_imagenes_personajes():
    gangster1_run_images = load_images_from_folder('./gangster_1/run')
    gangster1_jump_images = load_images_from_folder('./gangster_1/jump')
    gangster1_idle_images = load_images_from_folder('./gangster_1/idle')

    gangster2_run_images = load_images_from_folder('./gangster_2/run')
    gangster2_jump_images = load_images_from_folder('./gangster_2/jump')
    gangster2_idle_images = load_images_from_folder('./gangster_2/idle')

    return ((gangster1_run_images, gangster1_jump_images, gangster1_idle_images),
            (gangster2_run_images, gangster2_jump_images, gangster2_idle_images))

def crear_instancias_personajes(gangster1_images, gangster2_images):
    gangster1 = Gangster(50, 670, *gangster1_images)
    gangster1.idle_images = gangster1_images[2]  # Ensure idle_images attribute is set
    gangster2 = Gangster(50, 670, *gangster2_images)
    gangster2.idle_images = gangster2_images[2]  # Ensure idle_images attribute is set
    return gangster1, gangster2

def crear_elementos_nivel(mapa_nivel):
    plataformas = []
    monedas = []
    spikes = []
    guns = []
    door = None

    NUM_COLS = len(mapa_nivel[0])

    for fila_indice, fila in enumerate(mapa_nivel):
        for col_indice, celda in enumerate(fila):
            x = col_indice * TAMANIO_CELDA
            y = fila_indice * TAMANIO_CELDA + (TAMANIO_CELDA - PLATFORM_HEIGHT)
            if celda == 'X':
                tipo = determinar_tipo_plataforma(fila, col_indice)
                plataforma = {'rect': pygame.Rect(x, y, TAMANIO_CELDA, PLATFORM_HEIGHT), 'type': tipo}
                plataformas.append(plataforma)
            elif celda == 'O':
                moneda = pygame.Rect(x + 10, y + 10, 20, 20)
                monedas.append(moneda)
            elif celda == 'P':
                spike_rect = pygame.Rect(x, y + PLATFORM_HEIGHT, TAMANIO_CELDA, TAMANIO_CELDA)
                spikes.append({'rect': spike_rect, 'mask': spike_mask})
            elif celda == 'W':
                door = pygame.Rect(x, y+20, TAMANIO_CELDA * 3, TAMANIO_CELDA * 2)
            elif celda == 'G':
                gun_rect = pygame.Rect(x, y, TAMANIO_CELDA, TAMANIO_CELDA)
                # Determinar la dirección según la posición
                if col_indice < NUM_COLS // 2:
                    direction = 1  # Apunta a la derecha
                else:
                    direction = -1  # Apunta a la izquierda
                gun = {'rect': gun_rect, 'cooldown': 0, 'direction': direction}
                guns.append(gun)

    return plataformas, monedas, spikes, guns, door



def determinar_tipo_plataforma(fila, col_indice):
    if col_indice == 0 or fila[col_indice - 1] != 'X':
        if col_indice + 1 < len(fila) and fila[col_indice + 1] == 'X':
            return 'left'
        else:
            return 'single'
    elif col_indice + 1 == len(fila) or fila[col_indice + 1] != 'X':
        return 'right'
    else:
        return 'center'

# Función para manejar colisiones con plataformas
def detectar_colision_con_plataformas(gangster, plataformas):

    gangster.is_jumping = True

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
                gangster.vel_x = 0  # Detiene el movimiento horizontal hacia la derecha
            # Colisión por el lado derecho
            elif gangster.vel_x < 0 and gangster.rect.left <= plat_rect.right and gangster.rect.right > plat_rect.right:
                gangster.rect.left = plat_rect.right
                gangster.vel_x = 0  # Detiene el movimiento horizontal hacia la izquierda


def manejar_colision_plataforma(gangster, plat_rect):
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
    for spike in spikes:
        spike_rect = spike['rect']
        spike_mask = spike['mask']
        offset = (spike_rect.x - gangster.rect.x, spike_rect.y - gangster.rect.y)
        if gangster.mask.overlap(spike_mask, offset):
            gangster.rect.x = gangster.start_x
            gangster.rect.y = gangster.start_y
            gangster.is_jumping = True
            break

def detectar_colision_con_monedas(gangster, monedas):
    for moneda in monedas[:]:
        if gangster.rect.colliderect(moneda):
            monedas.remove(moneda)

def detectar_colision_con_puerta(gangster, door):
    if door and gangster.rect.colliderect(door):
        return True
    return False


def show_winner(screen, gangster, idle_image, click_sound):
    font = pygame.font.Font(None, 74)
    winner_text = font.render(f'{gangster} Wins!', True, WHITE)
    winner_rect = winner_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))

    font_small = pygame.font.Font(None, 50)
    replay_text = font_small.render('Replay', True, WHITE)
    main_menu_text = font_small.render('Main Menu', True, WHITE)
    replay_rect = replay_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    main_menu_rect = main_menu_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))

    screen.fill(BLACK)
    screen.blit(winner_text, winner_rect)
    screen.blit(idle_image, (WIDTH // 2 - idle_image.get_width() // 2, HEIGHT // 2 - idle_image.get_height() // 2 - 50))
    pygame.draw.rect(screen, BLACK, replay_rect.inflate(20, 20), border_radius=10)  # Fondo del botón Replay
    screen.blit(replay_text, replay_rect)
    pygame.draw.rect(screen, BLACK, main_menu_rect.inflate(20, 20), border_radius=10)  # Fondo del botón Main Menu
    screen.blit(main_menu_text, main_menu_rect)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if replay_rect.collidepoint(event.pos):
                    click_sound.play()
                    return 'replay'
                elif main_menu_rect.collidepoint(event.pos):
                    click_sound.play()
                    return 'main_menu'

        pygame.time.Clock().tick(60)  # Evitar uso excesivo de CPU



def show_pause_menu(screen, click_sound):
    font = pygame.font.Font(None, 74)
    resume_text = font.render('Resume', True, WHITE)
    main_menu_text = font.render('Main Menu', True, WHITE)
    resume_rect = resume_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    main_menu_rect = main_menu_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

    while True:
        screen.fill(BLACK)
        pygame.draw.rect(screen, BLACK, resume_rect.inflate(20, 20), border_radius=10)  # Fondo del botón Resume
        screen.blit(resume_text, resume_rect)
        pygame.draw.rect(screen, BLACK, main_menu_rect.inflate(20, 20), border_radius=10)  # Fondo del botón Main Menu
        screen.blit(main_menu_text, main_menu_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'resume'
                elif event.key == pygame.K_RETURN:
                    # Obtener la posición del ratón para detectar en qué botón se hizo clic
                    mouse_pos = pygame.mouse.get_pos()
                    if resume_rect.collidepoint(mouse_pos):
                        click_sound.play()
                        return 'resume'
                    elif main_menu_rect.collidepoint(mouse_pos):
                        click_sound.play()
                        return 'main_menu'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if resume_rect.collidepoint(event.pos):
                    click_sound.play()
                    return 'resume'
                elif main_menu_rect.collidepoint(event.pos):
                    click_sound.play()
                    return 'main_menu'

        pygame.time.Clock().tick(60)  # Evitar uso excesivo de CPU

class Bullet:
    def __init__(self, x, y, direction):
        self.image = pygame.Surface((10, 10))  # Pequeña bola amarilla
        self.image.fill((255, 255, 0))  # Color amarillo
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vel_x = direction * 3  # Velocidad lenta

    def update(self):
        self.rect.x += self.vel_x

    def draw(self, screen):
        screen.blit(self.image, self.rect)


def main():
    while True:
        show_main_menu(screen, background_image, click_sound)  # Pasar click_sound
        # Detener la música del menú principal al iniciar el juego
        pygame.mixer.music.stop()
        gangster1_images, gangster2_images = cargar_imagenes_personajes()
        gangster1, gangster2 = crear_instancias_personajes(gangster1_images, gangster2_images)
        
        MAPA_NIVEL = generar_mapa_random()  # Asignar antes de definir replay_game()
        plataformas, monedas, spikes, guns, door = crear_elementos_nivel(MAPA_NIVEL)
        bullets = []
        paused = False
        running = True

        def replay_game():
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
            clock.tick(60)
            screen.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:  # Asegúrate de que este es el tipo de evento
                    if event.key == pygame.K_ESCAPE:
                        paused = True
                    elif event.key == pygame.K_0:
                        replay_game()


            screen.blit(background_image, (0, 0))
            keys = pygame.key.get_pressed()

            gangster1.move(keys, pygame.K_a, pygame.K_d, pygame.K_w)
            gangster1.apply_gravity()
            detectar_colision_con_plataformas(gangster1, plataformas)
            detectar_colision_con_pinchos(gangster1, spikes)
            detectar_colision_con_monedas(gangster1, monedas)
            gangster1.update()

            gangster2.move(keys, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP)
            gangster2.apply_gravity()
            detectar_colision_con_plataformas(gangster2, plataformas)
            detectar_colision_con_pinchos(gangster2, spikes)
            detectar_colision_con_monedas(gangster2, monedas)
            gangster2.update()


            # Manejo de las pistolas y las balas
            for gun in guns:
                if gun['cooldown'] > 0:
                    gun['cooldown'] -= 1
                else:
                    bullet_x = gun['rect'].centerx
                    bullet_y = gun['rect'].centery
                    bullet = Bullet(bullet_x, bullet_y, direction=gun['direction'])
                    bullets.append(bullet)
                    gun['cooldown'] = 120  # Dispara cada 2 segundos
                    shot_sound.play()  # Reproducir sonido de disparo




            # Actualizar y dibujar las balas
            for bullet in bullets[:]:
                bullet.update()
                if bullet.rect.x > WIDTH or bullet.rect.x < 0:
                    bullets.remove(bullet)
                else:
                    # Colisión con los jugadores
                    if bullet.rect.colliderect(gangster1.rect):
                        death_sound.play()  # Reproducir sonido de muerte
                        gangster1.rect.x = gangster1.start_x
                        gangster1.rect.y = gangster1.start_y
                        gangster1.is_jumping = True
                        bullets.remove(bullet)
                    elif bullet.rect.colliderect(gangster2.rect):
                        death_sound.play()  # Reproducir sonido de muerte
                        gangster2.rect.x = gangster2.start_x
                        gangster2.rect.y = gangster2.start_y
                        gangster2.is_jumping = True
                        bullets.remove(bullet)


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
                    running = False
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
                    running = False

            dibujar_elementos(screen, plataformas, monedas, spikes, guns, bullets, door, gangster1, gangster2)

            pygame.display.flip()

            if paused:
                action = show_pause_menu(screen, click_sound)  # Pasar click_sound
                if action == 'resume':
                    paused = False
                elif action == 'main_menu':
                    running = False
                    break

    pygame.quit()

def dibujar_elementos(screen, plataformas, monedas, spikes, guns, bullets, door, gangster1, gangster2):
    for plataforma in plataformas:
        plat_rect = plataforma['rect']
        tipo = plataforma['type']
        if tipo == 'left':
            screen.blit(platform_left_image, plat_rect)
        elif tipo == 'center':
            screen.blit(platform_center_image, plat_rect)
        elif tipo == 'right':
            screen.blit(platform_right_image, plat_rect)
        elif tipo == 'single':
            screen.blit(platform_center_image, plat_rect)

    for moneda in monedas:
        pygame.draw.ellipse(screen, (255, 215, 0), moneda)

    for spike_rect in spikes:
        screen.blit(spike_image, spike_rect['rect'])

    for gun in guns:
        if gun['direction'] == 1:
            # Voltear la imagen para que mire a la derecha
            image = pygame.transform.flip(gun_image, True, False)
        else:
            image = gun_image  # La imagen mira a la izquierda por defecto
        screen.blit(image, gun['rect'].topleft)

    for bullet in bullets:
        bullet.draw(screen)

    if door:
        screen.blit(door_image, door.topleft)

    gangster1.draw(screen)
    gangster2.draw(screen)



if __name__ == "__main__":
    main()
