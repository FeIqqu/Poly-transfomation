import pygame
import pygame_gui
import numpy as np
from tkinter import filedialog, Tk
import os

class Poly:
    def __init__(self, vertices, faces):
        self.vertices = np.array(vertices, dtype=float)
        self.faces = faces
        self.center = np.mean(self.vertices, axis=0)

    def translate(self, dx, dy, dz):
        translation_matrix = np.array([dx, dy, dz])
        self.vertices += translation_matrix
        self.center += translation_matrix

    def scale(self, factor):
        self.vertices = self.center + (self.vertices - self.center) * factor

    def rotate(self, axis, angle):
        angle = np.radians(angle)
        if axis == 'x':
            rotation_matrix = np.array([
                [1, 0, 0],
                [0, np.cos(angle), -np.sin(angle)],
                [0, np.sin(angle), np.cos(angle)],
            ])
        elif axis == 'y':
            rotation_matrix = np.array([
                [np.cos(angle), 0, np.sin(angle)],
                [0, 1, 0],
                [-np.sin(angle), 0, np.cos(angle)],
            ])
        elif axis == 'z':
            rotation_matrix = np.array([
                [np.cos(angle), -np.sin(angle), 0],
                [np.sin(angle), np.cos(angle), 0],
                [0, 0, 1],
            ])
        else:
            raise ValueError("Ось может быть только 'x', 'y' или 'z'")
        
        self.vertices = self.center + np.dot(self.vertices - self.center, rotation_matrix.T)

    def save_to_file(self, filename):
        try:
            with open(filename, 'w') as file:
                file.write(f"{len(self.vertices)}\n")
                for vertex in self.vertices:
                    file.write(" ".join(map(str, vertex)) + "\n")
                file.write(f"{len(self.faces)}\n")
                for face in self.faces:
                    file.write(" ".join(map(str, face)) + "\n")
        except Exception as e:
            print(f"Ошибка при сохранении многогранника: {e}")

    @staticmethod
    def load_from_file(filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
        vertex_count = int(lines[0])
        vertices = [list(map(float, lines[i + 1].split())) for i in range(vertex_count)]
        face_count = int(lines[vertex_count + 1])
        faces = [list(map(int, lines[vertex_count + 2 + i].split())) for i in range(face_count)]
        return Poly(vertices, faces)


def draw_poly(screen, poly):
    width, height = screen.get_size()
    projected_vertices = []
    for vertex in poly.vertices:
        x, y, z = vertex
        f = 500 / (z + 5)
        x_proj = int(width // 2 + f * x)
        y_proj = int(height // 2 - f * y)
        projected_vertices.append((x_proj, y_proj))

    for face in poly.faces:
        points = [projected_vertices[i] for i in face]
        pygame.draw.polygon(screen, (0, 0, 0), points, 1)


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    theme_path = os.path.join(os.path.dirname(__file__), "theme.json")
    manager = pygame_gui.UIManager((800, 800), theme_path)
    
    # Кнопки GUI
    translate_up_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((20, 430), (100, 50)),
                                                       text='Вверх', manager=manager)
    translate_down_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((20, 490), (100, 50)),
                                                         text='Вниз', manager=manager)
    translate_left_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((20, 550), (100, 50)),
                                                         text='Влево', manager=manager)
    translate_right_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((20, 610), (100, 50)),
                                                         text='Вправо', manager=manager)
    translate_forward_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((20, 670), (100, 50)),
                                                         text='Вперёд', manager=manager)
    translate_backward_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((20, 730), (100, 50)),
                                                         text='Назад', manager=manager)
    scale_up_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((140, 670), (100, 50)),
                                                   text='Растяжение', manager=manager)
    scale_down_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((140, 730), (100, 50)),
                                                     text='Сжатие', manager=manager)
    rotate_x_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((260, 610), (100, 50)),
                                                   text='Поворот X', manager=manager)
    rotate_y_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((260, 670), (100, 50)),
                                                   text='Поворот Y', manager=manager)
    rotate_z_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((260, 730), (100, 50)),
                                                   text='Поворот Z', manager=manager)

    clock = pygame.time.Clock()

    Tk().withdraw()
    filename = filedialog.askopenfilename(title="Выберите файл многогранника", filetypes=[("Text Files", "*.txt")])
    if not filename:
        return

    poly = Poly.load_from_file(filename)

    running = True
    while running:
        time_delta = clock.tick(30) / 1000.0
        screen.fill((255, 255, 255))

        draw_poly(screen, poly)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Обработка кнопок GUI
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == translate_up_button:
                    poly.translate(0, 0.1, 0)
                elif event.ui_element == translate_down_button:
                    poly.translate(0, -0.1, 0)
                elif event.ui_element == translate_left_button:
                    poly.translate(-0.1, 0, 0)
                elif event.ui_element == translate_right_button:
                    poly.translate(0.1, 0, 0)
                elif event.ui_element == translate_forward_button:
                    poly.translate(0, 0, 0.1)
                elif event.ui_element == translate_backward_button:
                    poly.translate(0, 0, -0.1)    
                elif event.ui_element == scale_up_button:
                    poly.scale(1.1)
                elif event.ui_element == scale_down_button:
                    poly.scale(0.9)
                elif event.ui_element == rotate_x_button:
                    poly.rotate('x', 10)
                elif event.ui_element == rotate_y_button:
                    poly.rotate('y', 10)
                elif event.ui_element == rotate_z_button:
                    poly.rotate('z', 10)

            manager.process_events(event)
            
        # Обработка клавиш
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            poly.translate(0, 0.1, 0)
        if keys[pygame.K_DOWN]:
            poly.translate(0, -0.1, 0)
        if keys[pygame.K_LEFT]:
            poly.translate(-0.1, 0, 0)
        if keys[pygame.K_RIGHT]:
            poly.translate(0.1, 0, 0)
        if keys[pygame.K_w]:
            poly.scale(1.1)
        if keys[pygame.K_s]:
            poly.scale(0.9)
        if keys[pygame.K_x]:
            poly.rotate('x', 2)
        if keys[pygame.K_y]:
            poly.rotate('y', 2)
        if keys[pygame.K_z]:
            poly.rotate('z', 2)
    
        manager.update(time_delta)
        manager.draw_ui(screen)

        pygame.display.flip()

    save_filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if save_filename:
        poly.save_to_file(save_filename)
    
    pygame.quit()


if __name__ == "__main__":
    main()