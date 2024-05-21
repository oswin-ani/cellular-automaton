import pygame
import sys
import random
import time
from copy import deepcopy

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 624
BLOCK_SIZE = 16
NET_COLOR = (50,60,50)
SOIL = (160, 82, 45)
FAIR = (207, 0, 0)
TREE = (16, 82, 47)
AFTER_FAIR = (54, 34, 21)
RIVER = (66, 194, 229)

pygame.init()

frame = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("FireSimulation")

forest_fraction = 0.8
neighbourhood = ((-1,-1), (-1,0), (-1,1), (0,-1), (0, 1), (1,-1), (1,0), (1,1))
tree_sq = 1507

# помимо обычных массивов, добавляем еще с клетками, являющимися рекой
all_rects = []
fair_rects = []
river_rects = []
soil_rects = []
for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
    row = []
    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        rect = pygame.Rect(x, y, BLOCK_SIZE - 1, BLOCK_SIZE - 1)
        if random.random() >= forest_fraction:
            row.append([rect, SOIL]) 
            soil_rects.append((x // BLOCK_SIZE, y // BLOCK_SIZE))
        # создание реки
        elif 250 < x < 280 and 30 < y < 550:
            row.append([rect, RIVER]) 
            river_rects.append((x // BLOCK_SIZE, y // BLOCK_SIZE))
        else:
            row.append([rect, TREE])      
    all_rects.append(row)
    fair_rects.append([0] * (SCREEN_WIDTH // BLOCK_SIZE))

start = 0
generations = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            x //= BLOCK_SIZE
            y //= BLOCK_SIZE
            # клетка загорается при нажатии, только если не принадлежит массиву с клетками реки
            if (x,y) not in river_rects:
                fair_rects[y][x] = 1
        elif event.type == pygame.KEYDOWN:
            if start == float('inf'):
                start = time.time()
            else:
                start = float('inf')
                print('Кол-во поколений с начала пожара:', generations-1)
                print('Процент охваченной огнём площади:', int(fire_sq / (len(all_rects) * len(all_rects[0])) * 100))
                print('Отношение кол-ва "живых" деревьев ко всем в процентах:', int((tree_sq - fire_tree_sq - after_tree_sq) / tree_sq * 100))
                print('Отношение выжженой площади земли ко всей территории леса в процентах:', int(after_sq / (len(all_rects) * len(all_rects[0])) * 100))
                #Пусть каждая клетка = 4 м^2. Тогда вся площадь леса = 7800 м^2. Пусть одно поколение = 60 с. Тогда можно рассчитать скорость распространения пожара:
                print('Скорость распространения пожара:', round(fire_sq * 4 / (generations-1) / 60, 2), 'м^2/с')
    if time.time() - start > 1.5:
        generations += 1
        fair_rects0 = deepcopy(fair_rects)
        for y in range(SCREEN_HEIGHT // BLOCK_SIZE):
            for x in range(SCREEN_WIDTH // BLOCK_SIZE):
                if fair_rects[y][x] > 0:
                    fair_rects0[y][x] = fair_rects[y][x] + 1
                    for dx,dy in neighbourhood:
                        # Соседние по диагонали деревья находятся дальше, поэтому загораются с меньшей вероятностью:
                        if abs(dx) == abs(dy) and random.random() < 0.573:
                            continue
                        # добавилось условие, чтобы клетки реки не горели
                        if 0 <= (x + dx) * BLOCK_SIZE < SCREEN_WIDTH and 0 <= (y + dy) * BLOCK_SIZE < SCREEN_HEIGHT and fair_rects[y + dy][x + dx] == 0 and (x + dx,y + dy) not in river_rects:
                            fair_rects0[y + dy][x + dx] = 1
        start = time.time()
        fair_rects = fair_rects0             
    
    frame.fill(NET_COLOR)

    for row in all_rects:
        for item in row:
            rect, color = item
            pygame.draw.rect(frame, color, rect)
    
    fire_sq = 0
    after_sq = 0
    fire_tree_sq = 0
    after_tree_sq = 0
    for y in range(SCREEN_HEIGHT // BLOCK_SIZE):
        for x in range(SCREEN_WIDTH // BLOCK_SIZE):
            if (x,y) not in soil_rects:
                if 0 < fair_rects[y][x] <= 5:
                    pygame.draw.rect(frame, FAIR, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1))
                    fire_sq += 1
                    fire_tree_sq += 1
                if 5 < fair_rects[y][x] <= 50:
                    pygame.draw.rect(frame, AFTER_FAIR, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1))
                    after_sq += 1
                    after_tree_sq += 1
                if 50 < fair_rects[y][x] <= 80:
                    pygame.draw.rect(frame, SOIL, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1))
            else:
                if 0 < fair_rects[y][x] <= 1:
                    pygame.draw.rect(frame, FAIR, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1))
                    fire_sq += 1
                if 1 < fair_rects[y][x] <= 45:
                    pygame.draw.rect(frame, AFTER_FAIR, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1))
                    after_sq += 1
                if 45 < fair_rects[y][x] <= 80:
                    pygame.draw.rect(frame, SOIL, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1))

    pygame.display.flip()