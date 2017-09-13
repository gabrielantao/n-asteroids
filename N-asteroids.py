#-------------------------------------------------------------------------------
# Name:        N-asteroids
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
SPEED = 50
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
    level_info = ((0.05, 0.05, 100, "very_low"),
                  (0.05, 0.05, 200, "low"),
                  (0.3, 0.05, 300, "moderate"),
                  (0.4, 0.05, 400, "high"),
                  (0.5, 0.05, 500, "very_high"))
    def __init__(self, row, dimension, level):
        super(self.__class__, self).__init__()
        self.dimension = dimension
        self.level = level
        self.asteroid_density = Zone.level_info[level][0]
        self.item_density = Zone.level_info[level][1]
        self.score = Zone.level_info[level][2]
        self.level_name = Zone.level_info[level][3]
        self.fill()
        sprite_size = self.sprites()[0].size
        pos = (0, row * self.dimension[1] * sprite_size[1])        
        dim = (dimension[0] * sprite_size[0], dimension[1] * sprite_size[1])
        self.rect = Rect(pos, dim)
        
    def fill(self):
        asteroid_num = int(self.asteroid_density * self.dimension[0] * self.dimension[1])
        item_num = int(self.item_density * self.dimension[0] * self.dimension[1])
        assert item_num > 0, "item_num == 0. Redefinir densidade de itens."
        pos_set = set()        
        while len(pos_set) < (asteroid_num + item_num):
            pos_set.add((random.randint(0, self.dimension[0]),
                         random.randint(0, self.dimension[1])))
        while len(pos_set):
            if len(pos_set) > item_num:
                self.add(Object("asteroid", pos_set.pop()))
            else:
                self.add(Object("item", pos_set.pop(), self.level))  
                
    def update(self, deltat):
        if self.rect.right > 0:
            self.rect.x -= SPEED * deltat
        super(self.__class__, self).update(deltat)
        
        
class BaseSprite(pygame.sprite.Sprite):
    size = (50, 50)
    spritesheet = {"spaceship": "image/rocket_test2.png", 
                   "asteroid": "image/asteroid_test2.png", 
                   "item": "image/item_test2.png"}
    def __init__(self, kind, tile_pos, current_sprite):
        pygame.sprite.Sprite.__init__(self)
        self.kind = kind
        pos_xy = (tile_pos[0] * BaseSprite.size[0], 
                  tile_pos[1] * BaseSprite.size[1])
        self.rect = Rect(pos_xy, self.size)   
        self.current_sprite = current_sprite
        self.image = pygame.image.load(BaseSprite.spritesheet[kind])
        self.sprites_num = self.image.get_width() // self.size[0]
    
    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft, 
                     (self.size[0] * self.current_sprite, 0, 
                      self.size[0], self.size[1]))
  
class Object(BaseSprite):
    def __init__(self, kind, tile_pos, current_sprite=0):
        super(self.__class__, self).__init__(kind, tile_pos, current_sprite)
        if kind == "asteroid":
            self.current_sprite = random.randint(0, self.sprites_num)
            
    def update(self, deltat):
        if self.rect.right > 0:
            self.rect.x -= SPEED * deltat
      #  else:
      #      self.kill()

class Spaceship(BaseSprite):
    def __init__(self, tile_pos, current_sprite=0):
        super(self.__class__, self).__init__("spaceship", tile_pos, current_sprite)
    
    def update(self, event_key):
        if event_key == K_UP and self.rect.top > 0:
                self.rect.y -= 20
        if event_key == K_DOWN and self.rect.bottom < HEIGHT:
                self.rect.y += 20
            
class Game():
    """
    0 modo contagem (5 segundos) 
    1 modo tutorial; 
    2 modo jogo; 
    
    """
    def __init__(self):
        self.game_mode = 0
        self.score = 0   
        self.zones = []
        self.spaceship = Spaceship((0, 0))
        # TODO: colocar as inicializacoes da tela e outras constantes
    
    # adiciona e remove zonas    
    def manage_zones(self, playtime, rows=2):
     #   if len(self.zones) == 0 or self.zones[-1][0].rect.right < WIDTH:
        if len(self.zones) == 0 or playtime % 5 == 0:
            self.zones.append([Zone(row, (5, 5), row) for row in range(rows)])
        if self.zones[0][0].rect.right < 0:
            self.zones.popleft()

    # verifica qual zona a nave esta
    def detect_zone(self):
        for zone in [row for column in self.zones[:2] for row in column]:
            if zone.rect.collidepoint(self.spaceship.rect.center):
                return zone
            
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
    # mostra o contador e bipes de tempo 5egundos (chamado na transicao e na e)
    def reset(self):
        pass
        
    def start(self):
        directory = "experiments/{:%Y-%b-%d %H:%M:%S}".format(datetime.datetime.now())
        os.mkdir(directory)
        log_tutorial = open("{}/tutorial.csv".format(directory), "w")
        tutorial_writer = csv.writer(log_tutorial)
        tutorial_writer.writerow(["time", "risklevel", "score"])
        log_game = open("{}/game.csv".format(directory), "w")
        game_writer = csv.writer(log_game)
        game_writer.writerow(["time", "risklevel", "score"])   
        playtime = 0 # tempo jogado por partida
        penalty = False # estado de penalidade 
        penaltytime = 0 #contador de tempo da penalidade (3 segundos)
        ##change_music("Title Theme.ogg")
        while True:
            milliseconds = clock.tick(FPS)  # milisegundos passados desde ultimo frame
            deltat = milliseconds/1000.0    # delta de tempo em segundos
            screen.fill(BLACK)
            for event in pygame.event.get():
                if event.type == QUIT:
                    log_tutorial.close()
                    log_game.close()
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:   
                    self.spaceship.update(event.key)                   
        #-----------------------------------------------------------------------
        # GERENCIA OS MODOS DE JOGO
        # 0 modo inicial; 1 preparacao para o jogo; 2 rodando jogo; 3 game over
        #-----------------------------------------------------------------------
            # MODO DE JOGO (NUM PAR): contador de preparacao para o jogo
          ##  if self.game_mode % 2:
          ##      if playtime < 1:
          ##          pass #animar texto contando 5 segndos
          ##      else:
          ##          self.game_mode += 1
                    
            # MODO DE JOGO 1: TUTORIAL
            #TODO: COLOCAR FUNcao para modular a velocidade ou densidade
            if self.game_mode == 0:
                if playtime >= 30:
                    self.game_mode += 1
                playtime += deltat
                self.manage_zones(playtime)
                current_zone = self.detect_zone()
                score = 0
                if penalty:
                    penaltytime += deltat
                    if penaltytime > 3:
                        penaltytime = 0
                        penalty = False
                else:
                    sprite = pygame.sprite.spritecollideany(self.spaceship, current_zone) 
                    if sprite:
                        if sprite.kind == "asteroid":
                            score = -current_zone.score 
                            penalty = True
                            # TODO: executar som de explosao
                        else: #if "item"
                            sprite.kill()
                            score = current_zone.score  
                tutorial_writer.writerow([playtime, current_zone.level, score])
                for column in self.zones:
                    for zone in column:
                        zone.update(deltat)
                        zone.draw(screen)
                self.spaceship.draw(screen)
                ##self.draw_parallax()
            pygame.display.update()

if __name__ == "__main__":
    game = Game()
    game.start()
