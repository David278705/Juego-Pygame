# main_menu.py

import pygame

def show_main_menu(screen, background_image, click_sound):
    # Fuente y tamaño para el título y los botones
    font_title = pygame.font.Font(None, 80)
    font_button = pygame.font.Font(None, 50)
    
    # Colores
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    # Cargar y reproducir la música del menú principal
    pygame.mixer.music.load('./main-menu.mp3')
    pygame.mixer.music.play(-1)  # Reproducir en bucle

    # Crear título y botones
    title_text = font_title.render("Jumping Gangster Levels", True, WHITE)
    button_text_play = font_button.render("Play", True, WHITE)
    button_text_help = font_button.render("Help", True, WHITE)
    button_text_exit = font_button.render("Salir", True, WHITE)
    
    # Obtener rectángulos para centrar el título y los botones
    title_rect = title_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 3))
    button_rect_play = button_text_play.get_rect(center=(screen.get_width() // 2, screen.get_height() // 1.5))
    button_rect_help = button_text_help.get_rect(center=(screen.get_width() // 2, screen.get_height() // 1.3))
    button_rect_exit = button_text_exit.get_rect(center=(screen.get_width() // 2, screen.get_height() // 1.1))
    
    # Bucle de la pantalla del menú principal
    running = True
    while running:
        # Dibujar el fondo
        screen.blit(background_image, (0, 0))
        
        # Dibujar el título y los botones
        screen.blit(title_text, title_rect)
        pygame.draw.rect(screen, BLACK, button_rect_play.inflate(20, 20), border_radius=10)  # Fondo del botón Play
        screen.blit(button_text_play, button_rect_play)
        pygame.draw.rect(screen, BLACK, button_rect_help.inflate(20, 20), border_radius=10)  # Fondo del botón Help
        screen.blit(button_text_help, button_rect_help)
        pygame.draw.rect(screen, BLACK, button_rect_exit.inflate(20, 20), border_radius=10)  # Fondo del botón Salir
        screen.blit(button_text_exit, button_rect_exit)

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect_play.collidepoint(event.pos):
                    click_sound.play()
                    return  # Salir del menú y continuar con el juego
                elif button_rect_help.collidepoint(event.pos):
                    click_sound.play()
                    show_help_menu(screen, background_image, click_sound)  # Pasar click_sound
                elif button_rect_exit.collidepoint(event.pos):
                    click_sound.play()
                    pygame.quit()
                    exit()

        # Actualizar pantalla
        pygame.display.flip()

def show_help_menu(screen, background_image, click_sound):
    # Fuente y tamaño para el texto de ayuda y el botón de volver
    font_help = pygame.font.Font(None, 40)
    font_button = pygame.font.Font(None, 50)
    
    # Colores
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    # Crear texto de ayuda y botón de volver
    help_text_lines = [
        "Instrucciones del juego:",
        "1. Usa las teclas A/D o Flechas Izquierda/Derecha para moverte.",
        "2. Presiona W o Flecha Arriba para saltar.",
        "3. Evita los obstáculos y enemigos.",
        "4. Dispara con la pistola para eliminar enemigos.",
        "5. Recoge objetos para ganar puntos."
    ]
    help_texts = [font_help.render(line, True, WHITE) for line in help_text_lines]
    button_text_back = font_button.render("Volver", True, WHITE)
    
    # Obtener rectángulos para centrar el texto de ayuda y el botón de volver
    help_text_rects = [text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 4 + i * 50)) for i, text in enumerate(help_texts)]
    button_rect_back = button_text_back.get_rect(center=(screen.get_width() // 2, screen.get_height() // 1.1))
    
    # Bucle de la pantalla del menú de ayuda
    running = True
    while running:
        # Dibujar el fondo
        screen.blit(background_image, (0, 0))
        
        # Dibujar el texto de ayuda y el botón de volver
        for text, rect in zip(help_texts, help_text_rects):
            screen.blit(text, rect)
        pygame.draw.rect(screen, BLACK, button_rect_back.inflate(20, 20), border_radius=10)  # Fondo del botón Volver
        screen.blit(button_text_back, button_rect_back)

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect_back.collidepoint(event.pos):
                    click_sound.play()
                    return  # Volver al menú principal

        # Actualizar pantalla
        pygame.display.flip()
