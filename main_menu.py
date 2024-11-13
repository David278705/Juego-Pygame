import pygame

def show_main_menu(screen, background_image):
    # Fuente y tamaño para el título y el botón
    font_title = pygame.font.Font(None, 80)
    font_button = pygame.font.Font(None, 50)
    
    # Colores
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    # Crear título y botón
    title_text = font_title.render("Gangster Levels", True, WHITE)
    button_text = font_button.render("Play (Nanainas kukas)", True, WHITE)
    
    # Obtener rectángulos para centrar el título y el botón
    title_rect = title_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 3))
    button_rect = button_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 1.5))
    
    # Bucle de la pantalla del menú principal
    running = True
    while running:
        # Dibujar el fondo
        screen.blit(background_image, (0, 0))
        
        # Dibujar el título y el botón
        screen.blit(title_text, title_rect)
        pygame.draw.rect(screen, BLACK, button_rect.inflate(20, 20), border_radius=10)  # Fondo del botón
        screen.blit(button_text, button_rect)

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return  # Salir del menú y continuar con el juego

        # Actualizar pantalla
        pygame.display.flip()
