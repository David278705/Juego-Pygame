# gangster.py
import pygame
import os
from PIL import Image

# Función para cargar y recortar imágenes desde una carpeta
def load_images_from_folder(folder):
    images = []
    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".png"):
            # Abrir imagen con PIL
            with Image.open(os.path.join(folder, filename)) as img:
                # Convertir a RGBA (asegura transparencia)
                img = img.convert("RGBA")
                # Obtener el cuadro de recorte del área no transparente
                bbox = img.getbbox()
                # Recortar y guardar
                cropped_img = img.crop(bbox)

                # Convertir la imagen recortada a un objeto de pygame
                mode = cropped_img.mode
                size = cropped_img.size
                data = cropped_img.tobytes()

                # Crear imagen pygame desde el recorte
                pygame_image = pygame.image.fromstring(data, size, mode)
                images.append(pygame_image)
    return images

class Gangster:
    def __init__(self, x, y, run_images, jump_images, idle_images):
        # Cargar imágenes normales y volteadas
        self.run_images_right = run_images
        self.run_images_left = [pygame.transform.flip(img, True, False) for img in run_images]
        self.jump_images_right = jump_images
        self.jump_images_left = [pygame.transform.flip(img, True, False) for img in jump_images]
        self.idle_images_right = idle_images
        self.idle_images_left = [pygame.transform.flip(img, True, False) for img in idle_images]

        self.image_index = 0
        self.current_images = self.idle_images_right  # Iniciar con imágenes en reposo mirando a la derecha
        self.prev_images = self.current_images  # Para rastrear cambios en el conjunto de imágenes
        self.rect = self.run_images_right[0].get_rect()
        self.rect.x = x
        self.rect.y = y
        self.start_x = x
        self.start_y = y
        self.vel_x = 0
        self.vel_y = 0
        self.gravity = 0.4
        self.current_gravity = self.gravity
        self.jump_strength = -20
        self.is_jumping = False
        self.is_jumping_animation = False
        self.facing_left = False  # Para saber si está mirando a la izquierda

    def move(self, keys, left, right, jump):
        if keys[left]:
            self.vel_x = -5
            self.facing_left = True
        elif keys[right]:
            self.vel_x = 5
            self.facing_left = False
        else:
            self.vel_x = 0

        # Saltar solo si no está ya en el aire
        if keys[jump] and not self.is_jumping:
            self.is_jumping = True
            self.is_jumping_animation = True
            self.vel_y = self.jump_strength
            self.current_gravity = self.gravity  # Gravedad estándar al saltar

    def apply_gravity(self):
        # Seleccionar el conjunto de imágenes correcto según el estado y la dirección
        if self.is_jumping_animation:
            new_images = self.jump_images_left if self.facing_left else self.jump_images_right
        else:
            if self.vel_x == 0:
                new_images = self.idle_images_left if self.facing_left else self.idle_images_right
            else:
                new_images = self.run_images_left if self.facing_left else self.run_images_right

        # Si el conjunto de imágenes ha cambiado, reiniciar el índice de imagen
        if new_images != self.current_images:
            self.current_images = new_images
            self.image_index = 0  # Reiniciar el índice para comenzar la nueva animación desde el inicio

        if self.is_jumping:
            self.vel_y += self.current_gravity
        else:
            self.vel_y = 0

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Animar iterando a través de las imágenes
        self.image_index += 0.2  # Controla la velocidad de la animación
        if self.image_index >= len(self.current_images):
            self.image_index = 0

    def draw(self, screen):
        current_image = self.current_images[int(self.image_index)]
        screen.blit(current_image, (self.rect.x, self.rect.y))
