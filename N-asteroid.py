#-------------------------------------------------------------------------------
# Name:        Flappy Mario v1.4
# Purpose:
#
# Author:      Gabriel
#
# Created:     12/07/2014
# Copyright:   (c) Gabriel 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys
import random
import csv
import datetime
from collections import deque
import pygame
from pygame.locals import *
pygame.init()

WIDTH = 1000
HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 30 # maximo frames por segundo

# cria o clock
clock = pygame.time.Clock()

# inicializa screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("N-asteroids")

# carrega imagens e large_font
##background = pygame.image.load("images/parallax.png")

##large_font = pygame.font.Font("fonts/Super_Mario_World.ttf", 32)
##small_font = pygame.font.Font("fonts/Super_Mario_World.ttf", 20)

def change_music(new_music, loops=-1):
    pygame.mixer.music.stop()
    pygame.mixer.music.load("sound/{}".format(new_music))
    pygame.mixer.music.play(loops)

class Zone(pygame.sprite.Group):
    """
    row [int]: numero da linha onde esta a zona
    dimension [tuple]: dimensoes em tiles da zone
    level [int]: numero do nivel de risco 
    level_info: asteroid density, item density, score, level name
    finishing [bool]: indica se a zona pode ser deletada
    """
    level_info = ((0.1, 0.05, 100, "very_low"),
                  (0.2, 0.05, 200, "low"),
                  (0.3, 0.05, 300, "moderate")
                  (0.4, 0.05, 400, "high")
                  (0.5, 0.05, 500, "very_high"))
    def __init__(self, row, dimension, level):
        self.level = level
        self.asteroid_density = Zone.level_info[level][0]
        self.item_density = Zone.level_info[level][1]
        self.score = Zone.level_info[level][2]
        self.level_name = Zone.level_info[level][3]
        self.fill()
        sprite_size = self.sprites()[0].size
        pos = (0, row * dimesion[1] * sprite_size[1])        
        dim = (dimension[0] * sprite_size[0], dimension[1] * sprite_size[1])
        self.rect = Rect(pos, dim)
        self.finishing = False
        
    def fill(self):
        asteroid_num = int(self.asteroid_density * self.dimension[0] * self.dimension[1])
        item_num = int(self.item_density * self.dimension[0] * self.dimension[1])
        assert intem_num > 0, "item_num == 0. Redefinir densidade de itens"
        pos_set = set()        
        while len(pos_set) < (asteroid_num + item_num):
            pos_set.add((random.randint(self.dimension[0]),
                         random.randint(self.dimension[1])))
        while len(pos_set):
            if len(pos_set) > item_num:
                self.add(Object("asteroid", pos_set.pop()))
            else:
                self.add(Object("item", pos_set.pop(), self.level))  
 
class BaseSprite(pygame.sprite.Sprite):
    size = ()
    spritesheet = {"speceship": "", 
                   "asteroid": "", 
                   "item": ""}
    def __init__(self, kind, pos, current_sprite):
        super(self.__class__, self).__init__()
        self.kind = kind
        self.rect = Rect(pos, self.size)   
        self.current_sprite = current_sprite
        self.sheet = pygame.image.load(spritesheet[kind])
        self.sprites_num = self.sheet.get_width() // self.size[0]
    
    def draw(self, surface):
        surface.blit(self.sheet, self.rec.topleft, 
                     (self.size[0] * self.current_sprite, 0, 
                      self.size[0], self.size[1]))
  
class Object(BaseSprite):
    vel = 4
    def __init__(self, kind, tile_pos, current_sprite=0):
        pos = (tile_pos[0] * size[0], tile_pos[1] * size[1])
        super(self.__class__, self).__init__(kind, pos, current_sprite)
        if kind == "asteroid":
            self.current_sprite = random.randint(self.sprites_num)
            
    def update(self, seconds):
        if self.rect.right > 0:
            self.rect.x += self.vel * seconds
        else:
            self.kill()

class Spaceship(BaseSprite):
    def __init__(self, pos, current_sprite=0):
        super(self.__class__, self).__init__("spaceship", pos, current_sprite)
    
    def update(self, event):
        if event.key == K_UP and self.rect.top > 0:
                self.rect.y  -= 5
        if event.key == K_DOWN and self.rect.bottom < HEIGHT:
                self.rect.y += 5
            
class Game():
    """
    0 modo tutorial; 
    1 modo jogo; 
    
    """
    def __init__(self):
        self.game_mode = 0
        self.score = 0   
        self.zones = deque()
        # TODO: colocar as inicializacoes da tela e outras constantes
        
    def manage_zones(self):
        if len(self.zones) == 0 or self.zones[-1][0].right < WIDTH:
            self.zones.append([Zone(row, (10, 10), row) for row in range(rows)])
        if self.zones[0][0].right < 0:
            self.zones.popleft()

    # detectar colisao com o primeiro da lista
    def collision_detect(self):
        pass
         
    # atualiza a pontos e desenha o score
    def update_score(self, last_state):
        if self.mario_rect.colliderect(self.pipe_list[0][2]): #conseguiu passar pelo tubo
            passing_gap = True
        else: 
            if passing_gap:
                passing_gap = True
                self.score += 1
       
    # desenha pontos
    def draw_score(self):
        screen.blit(score_img, (WIDTH/2  - 50, 10))
        texto = large_font.render(str(self.score), True, WHITE)
        screen.blit(texto, (WIDTH/2 - 20, 28))
           
    # desenha o parallax 
    def draw_parallax(self):
        screen.blit(background, (0, 0))
        
    # reseta parametros
    def reset(self):
        pass
        
    def start(self):
        directory = "experiments/{:%Y-%b-%d %H:%M}".format(datetime.datetime.now())
        log_tutorial = open("{}/tutorial.csv".format(directory), "w")
        tutorial_writer = csv.writer(log_tutorial)
        tutorial_writer.writerow(["time", "risklevel", "score"])
        log_game = open("{}/game.csv".format(directory), "w")
        game_writer = csv.writer(log_game)
        game_writer.writerow(["time", "risklevel", "score"])   
        spaceship = SpaceShip((20, HEIGHT/2))
        self.create_zone()
        playtime = 0 # tempo jogado por partida
        change_music("Title Theme.ogg")
        while True:
            milliseconds = clock.tick(FPS)  # milisegundos passados desde ultimo frame
            seconds = milliseconds/1000.0 # tempo em segundos
            screen.fill(BLACK)
            for event in pygame.event.get():
                if event.type == QUIT:
                    log_tutorial.close()
                    log_game.close()
                    pygame.quit()
                    sys.exit()
                spaceship.update(event)
                
        #-----------------------------------------------------------------------
        # GERENCIA OS MODOS DE JOGO
        # 0 modo inicial; 1 preparacao para o jogo; 2 rodando jogo; 3 game over
        #-----------------------------------------------------------------------
            # MODO DE JOGO 0: TUTORIAL
            if self.game_mode == 0: 
                ##self.draw_parallax()
                # TODO: mudar a forma de criaçao de zonas 
                if len(self.zones) == 0 or self.zones[-1][0].right < WIDTH:
                    self.zones.append([Zone(row, (10, 10), row) for row in range(rows)])
                if self.zones[0][0].right < 0:
                    self.zones.popleft()
                if spaceship.rect.center
                playtime += seconds
               
           
            # MODO DE JOGO 1: JOGO
            elif self.game_mode == 1:
                if len(self.zones) == 0 or self.zones[-1][0].right < WIDTH:
                    self.zones.append([Zone(row, (10, 10), row) for row in range(rows)])
                if self.zones[0][0].right < 0:
                    self.zones.popleft()
                playtime += seconds
                
            # MODO DE JOGO 2: RODANDO O JOGO EM SI
            elif self.game_mode == 2:
                # gera obstaculos 
                if len(self.pipe_list) == 0 or self.pipe_list[-1][0].x < (WIDTH - self.gap_width):
                    self.create_pipe()
                # remove obstaculos que sairem da tela
                if self.pipe_list[0][0].x < -pipe_img.get_width():
                    self.pipe_list.remove(self.pipe_list[0])
                self.draw_parallax()
                self.draw_pipe()
                self.draw_ground()
                self.draw_mario() 
                # desenha placar
                screen.blit(score_img, (WIDTH/2 - 50, 10))
                text = large_font.render(str(self.score), True, WHITE)
                screen.blit(text, (WIDTH/2 - 20, 28))
                self.scroll_ground(seconds)
                self.scroll_pipe(seconds)
                # atualiza o placar
                if self.pipe_list[0][2].contains(self.mario_rect): 
                    passing_gap = True
                else: 
                    if passing_gap:
                        passing_gap = False
                        self.score += 1
                # restricao do limite superior
                if self.mario_rect.top <= 0 and self.mario_speed < 0: 
                    self.mario_speed = 0
                # atualiza posicao do mario e do rect 
                self.mario_speed += GRAVITY * seconds 
                self.mario_rect.top += self.mario_speed * seconds 
                if self.collision_detect():
                    # registra linha com dados da jogada
                    end_datetime = "{:%Y-%b-%d %H:%M:%S}".format(datetime.datetime.now())
                    logwriter.writerow([start_datetime, end_datetime, game_mode_list[self.level], self.score, round(playtime, 3)])
                    change_music("Life Lost.ogg", 0)
                    self.game_mode = 3
                playtime += seconds
        
            # MODO DE JOGO 3: TELA DE PONTUACAO E GAME OVER
            elif self.game_mode == 3:
                self.draw_parallax()
                self.draw_pipe()
                self.draw_ground()
                self.draw_mario(False)
                # quando a animacao acaba desenha game over e o score
                if self.mario_rect.bottom >= HEIGHT - GND_HEIGHT:
                    # para o personagem no chao
                    self.mario_speed = 0
                    self.mario_rect.bottom = HEIGHT - GND_HEIGHT
                    # desenha o placar
                    screen.blit(score_gameover,  (WIDTH/2 - 200, 100))
                    # mostra o score e o best score
                    text = large_font.render(str(self.score), True, BLACK)
                    screen.blit(text, (600, 210))
                    if self.score > self.best_score:
                        self.best_score = self.score
                    text = large_font.render(str(self.best_score), True, BLACK)
                    screen.blit(text, (600, 290))
                    # mostra medalha correspondente 20, 40, 60, 80
                    if self.score > 20 : #bronze
                        screen.blit(medals, (340, 225), (0,0,80,100))
                    if self.score > 40: #prata
                        screen.blit(medals, (340, 225), (80,0,80,100))
                    if self.score > 60: #ouro
                        screen.blit(medals, (340, 225), (160,0,80,100))
                    if self.score > 80: #diamante
                        screen.blit(medals, (340, 225), (240,0,80,100))
                    # desenha o play again
                    screen.blit(play_again, (300, 400))
                    screen.blit(cursor_img, (580, 405 + 30*cursor2_pos))
                else:
                    self.mario_speed += GRAVITY * seconds
                    self.mario_rect.top += self.mario_speed * seconds
            pygame.display.update()

if __name__ == "__main__":
    game = Game()
    game.start()
