import pygame
import sys

# Инициализация Pygame
pygame.init()

# Создание окна
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Тестовое окно")

# Основной цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Заливка экрана белым цветом
    screen.fill((255, 255, 255))
    
    # Обновление экрана
    pygame.display.flip()

pygame.quit()
sys.exit() 