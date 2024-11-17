import pygame
from gangster import Gangster, load_images_from_folder
from main_menu import show_main_menu

# Inicialización de Pygame
pygame.init()

# Configuración de pantalla
WIDTH, HEIGHT = 1000, 800
TAMANIO_CELDA = 40
PLATFORM_HEIGHT = 20  # Altura de las plataformas más angosta
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gangster Levels")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Configuración del reloj para controlar los FPS
clock = pygame.time.Clock()

# Cargar las imágenes de los personajes
gangster1_run_images = load_images_from_folder('./gangster_1/run')
gangster1_jump_images = load_images_from_folder('./gangster_1/jump')
gangster1_idle_images = load_images_from_folder('./gangster_1/idle')

gangster2_run_images = load_images_from_folder('./gangster_2/run')
gangster2_jump_images = load_images_from_folder('./gangster_2/jump')
gangster2_idle_images = load_images_from_folder('./gangster_2/idle')

# Crear instancias de los personajes
gangster1 = Gangster(50, 690, gangster1_run_images, gangster1_jump_images, gangster1_idle_images)
gangster2 = Gangster(50, 690, gangster2_run_images, gangster2_jump_images, gangster2_idle_images)

# Cargar y escalar la imagen de fondo para que cubra toda la pantalla
background_image = pygame.image.load("./bg.jpg")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Mostrar el menú principal
show_main_menu(screen, background_image)

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
spike_mask = pygame.mask.from_surface(spike_image)  # Crear máscara para los pinchos

# Definir el mapa del nivel
mapa_nivel = [
    "                          ",
    "                          ",
    "                          ",
    "       XXXXXXXXXXXXXXXXXXX",
    "                          ",
    "                          ",
    "    P                     ",
    "XXXXXXXXXXXXXXXXXXXX      ",
    "                          ",
    "                          ",
    "                  P       ",
    "      XXXXXXXXXXXXXXXXXXXX",
    "                          ",
    "                          ",
    "        P                 ",
    "XXXXXXXXXXXXXXXX      ",
    "                          ",
    "                          ",
    "                   P      ",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXX",
]

# Crear listas para plataformas, monedas y pinchos a partir del mapa del nivel
plataformas = []
monedas = []
spikes = []

for fila_indice, fila in enumerate(mapa_nivel):
    for col_indice, celda in enumerate(fila):
        x = col_indice * TAMANIO_CELDA
        y = fila_indice * TAMANIO_CELDA + (TAMANIO_CELDA - PLATFORM_HEIGHT)  # Ajustar para plataformas más angostas
        if celda == 'X':  # Crear una plataforma
            # Determinar el tipo de segmento de plataforma
            if col_indice == 0 or fila[col_indice - 1] != 'X':
                if col_indice + 1 < len(fila) and fila[col_indice + 1] == 'X':
                    tipo = 'left'
                else:
                    tipo = 'single'
            elif col_indice + 1 == len(fila) or fila[col_indice + 1] != 'X':
                tipo = 'right'
            else:
                tipo = 'center'
            plataforma = {'rect': pygame.Rect(x, y, TAMANIO_CELDA, PLATFORM_HEIGHT), 'type': tipo}
            plataformas.append(plataforma)
        elif celda == 'O':  # Crear una moneda
            moneda = pygame.Rect(x + 10, y + 10, 20, 20)
            monedas.append(moneda)
        elif celda == 'P':  # Crear un pincho
            spike_rect = pygame.Rect(x, y + PLATFORM_HEIGHT, TAMANIO_CELDA, TAMANIO_CELDA)
            spikes.append({'rect': spike_rect, 'mask': spike_mask})

# Función para manejar colisiones con plataformas
def detectar_colision_con_plataformas(gangster):

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

# Función para manejar colisiones con pinchos
def detectar_colision_con_pinchos(gangster):
    for spike in spikes:
        spike_rect = spike['rect']
        spike_mask = spike['mask']
        offset = (spike_rect.x - gangster.rect.x, spike_rect.y - gangster.rect.y)
        if gangster.mask.overlap(spike_mask, offset):
            # Reiniciar posición del personaje al inicio
            gangster.rect.x = gangster.start_x
            gangster.rect.y = gangster.start_y
            break

# Función para manejar colisiones con monedas
def detectar_colision_con_monedas(gangster):
    for moneda in monedas[:]:
        if gangster.rect.colliderect(moneda):
            monedas.remove(moneda)

# Loop principal del juego
running = True
while running:
    clock.tick(60)
    screen.fill(WHITE)

    # Capturamos los eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Dibujar el fondo que ahora cubre toda la pantalla
    screen.blit(background_image, (0, 0))

    # Obtener las teclas presionadas
    keys = pygame.key.get_pressed()

    # Movimiento de Gangster 1 (WASD)
    gangster1.move(keys, pygame.K_a, pygame.K_d, pygame.K_w)
    gangster1.apply_gravity()
    detectar_colision_con_plataformas(gangster1)
    detectar_colision_con_pinchos(gangster1)
    detectar_colision_con_monedas(gangster1)
    gangster1.update()

    # Movimiento de Gangster 2 (Flechas)
    gangster2.move(keys, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP)
    gangster2.apply_gravity()
    detectar_colision_con_plataformas(gangster2)
    detectar_colision_con_pinchos(gangster2)
    detectar_colision_con_monedas(gangster2)
    gangster2.update()

    # Dibujar plataformas, monedas y pinchos
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
            screen.blit(platform_center_image, plat_rect)  # Puedes cambiar esto si tienes una imagen específica

    for moneda in monedas:
        pygame.draw.ellipse(screen, (255, 215, 0), moneda)

    for spike_rect in spikes:
        screen.blit(spike_image, spike_rect['rect'])

    # Dibujar personajes
    gangster1.draw(screen)
    gangster2.draw(screen)

    # Actualizar la pantalla
    pygame.display.flip()

# Salir del juego
pygame.quit()
