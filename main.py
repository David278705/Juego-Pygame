import pygame
from gangster import Gangster, load_images_from_folder
from main_menu import show_main_menu

# Inicialización de Pygame
pygame.init()

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

# Definir el mapa del nivel
MAPA_NIVEL = [
    "                          ",
    "                          ",
    "             P            ",
    "    XXXXXXXXXXXXXXXXXXXXXX",
    "                          ",
    "                          ",
    "      P          P        ",
    "XXXXXXXXXXXXXXXXXXXXXX    ",
    "                          ",
    "                          ",
    "          P          P    ",
    "    XXXXXXXXXXXXXXXXXXXXXX",
    "                          ",
    "                          ",
    "   P                      ",
    "XXXXXXXXXXXXXPPXXXXXXX    ",
    "                          ",
    "                          ",
    "         P         P      ",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXX",
]

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
    gangster1 = Gangster(50, 690, *gangster1_images)
    gangster2 = Gangster(50, 690, *gangster2_images)
    return gangster1, gangster2

def crear_elementos_nivel(mapa_nivel):
    plataformas = []
    monedas = []
    spikes = []

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

    return plataformas, monedas, spikes

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

def detectar_colision_con_plataformas(gangster, plataformas):
    gangster.is_jumping = True

    if gangster.rect.left < 0:
        gangster.rect.left = 0
        gangster.vel_x = 0
    elif gangster.rect.right > WIDTH:
        gangster.rect.right = WIDTH
        gangster.vel_x = 0
    if gangster.rect.top < 0:
        gangster.rect.top = 0
        gangster.vel_y = 0
    elif gangster.rect.bottom > HEIGHT:
        gangster.rect.bottom = HEIGHT
        gangster.vel_y = 0
        gangster.is_jumping = False

    for plataforma in plataformas:
        plat_rect = plataforma['rect']
        if gangster.rect.colliderect(plat_rect):
            manejar_colision_plataforma(gangster, plat_rect)

def manejar_colision_plataforma(gangster, plat_rect):
    if gangster.vel_y > 0 and gangster.rect.bottom <= plat_rect.top + abs(gangster.vel_y):
        gangster.rect.bottom = plat_rect.top
        gangster.vel_y = 0
        gangster.is_jumping = False
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
            break

def detectar_colision_con_monedas(gangster, monedas):
    for moneda in monedas[:]:
        if gangster.rect.colliderect(moneda):
            monedas.remove(moneda)

def show_pause_menu(screen):
    font = pygame.font.Font(None, 74)
    resume_text = font.render('Resume', True, WHITE)
    main_menu_text = font.render('Main Menu', True, WHITE)
    resume_rect = resume_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    main_menu_rect = main_menu_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

    while True:
        screen.fill(BLACK)
        screen.blit(resume_text, resume_rect)
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
                    if resume_rect.collidepoint(pygame.mouse.get_pos()):
                        return 'resume'
                    elif main_menu_rect.collidepoint(pygame.mouse.get_pos()):
                        return 'main_menu'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if resume_rect.collidepoint(event.pos):
                    return 'resume'
                elif main_menu_rect.collidepoint(event.pos):
                    return 'main_menu'

def main():
    running = True
    while running:
        show_main_menu(screen, background_image)
        gangster1_images, gangster2_images = cargar_imagenes_personajes()
        gangster1, gangster2 = crear_instancias_personajes(gangster1_images, gangster2_images)
        plataformas, monedas, spikes = crear_elementos_nivel(MAPA_NIVEL)
        paused = False

        while not paused:
            clock.tick(60)
            screen.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    paused = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    paused = True

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

            dibujar_elementos(screen, plataformas, monedas, spikes, gangster1, gangster2)
            pygame.display.flip()

            if paused:
                action = show_pause_menu(screen)
                if action == 'resume':
                    paused = False
                elif action == 'main_menu':
                    break

    pygame.quit()

def dibujar_elementos(screen, plataformas, monedas, spikes, gangster1, gangster2):
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

    gangster1.draw(screen)
    gangster2.draw(screen)

if __name__ == "__main__":
    main()
