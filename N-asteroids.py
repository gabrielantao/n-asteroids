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
import pygame
from pygame.locals import *
pygame.init()

WIDTH = 1200
HEIGHT = 850
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 30 # maximo frames por segundo
SPEED = -150
# cria o clock
clock = pygame.time.Clock()

# inicializa screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("N-asteroids")

# carrega imagens e large_font
background = pygame.image.load("image/background2.png")
info_bar = pygame.image.load("image/infobar.png")

small_font = pygame.font.Font("font/HANGAR_flat.ttf", 20)
large_font = pygame.font.Font("font/HANGAR_flat.ttf", 40)

def play_sound(sound, loops=-1):
    pygame.mixer.music.stop()
    pygame.mixer.music.load("sound/{}".format(sound))
    pygame.mixer.music.play(loops)

class Zone(pygame.sprite.Group):
    """
    row [int]: numero da linha onde esta a zona
    dimension [tuple]: dimensoes em tiles da zone
    level [int]: numero do nivel de risco 
    level_info: asteroid density, item density, score, level name
    finishing [bool]: indica se a zona pode ser deletada
    """
    sprite_size = (50, 50) # TODO: remover esse atributo e talvez colocar como global
    level_info = ((0.07, 0.05, 100, "very_low"),
                  (0.12, 0.05, 200, "low"),
                  (0.16, 0.05, 300, "moderate"),
                  (0.18, 0.05, 400, "high"),
                  (0.22, 0.05, 500, "very_high"))
    def __init__(self, row, dimension, level):
        super(self.__class__, self).__init__()
        self.dimension = dimension
        self.level = level
        self.asteroid_density = Zone.level_info[level][0]
        self.item_density = Zone.level_info[level][1]
        self.score = Zone.level_info[level][2]
        self.level_name = Zone.level_info[level][3]
        pos = (WIDTH, row * self.dimension[1] * self.sprite_size[1])        
        dim = (dimension[0] * self.sprite_size[0], dimension[1] * self.sprite_size[1])
        self.rect = Rect(pos, dim)
        self.fill()
        
    def fill(self):
        asteroid_num = int(self.asteroid_density * self.dimension[0] * self.dimension[1])
        item_num = int(self.item_density * self.dimension[0] * self.dimension[1])
        assert item_num > 0, "item_num == 0. Redefinir densidade de itens."
        pos_set = set()        
        while len(pos_set) < asteroid_num + item_num:
            pos_set.add((random.randint(0, self.dimension[0] - 1),
                         random.randint(0, self.dimension[1] - 1)))
        for i in range(asteroid_num):
            tile_pos = pos_set.pop()
            pos = (self.rect.x + tile_pos[0] * self.sprite_size[0],
                   self.rect.y + tile_pos[1] * self.sprite_size[1])
            self.add(Object("asteroid", pos))
        for i in range(item_num):
            tile_pos = pos_set.pop()
            pos = (self.rect.x + tile_pos[0] * self.sprite_size[0],
                   self.rect.y + tile_pos[1] * self.sprite_size[1])
            self.add(Object("item", pos, self.level))  
    
    #TODO: remover esse metodo (SOMENTE PARA DEBUG)
    def draw(self, surface):
        super(self.__class__, self).draw(surface)
      ##  pygame.draw.rect(surface, (255,0,0), self.rect,1)
        
    def update(self, deltat):
        self.rect.move_ip(SPEED * deltat, 0)
        super(self.__class__, self).update(deltat)
 
        
class Object(pygame.sprite.Sprite):
    size = (50, 50)
    spritesheet = {"asteroid": "image/asteroid_sheet.png", 
                   "item": "image/item_sheet.png"}
    def __init__(self, kind, pos, current_sprite=0):
        pygame.sprite.Sprite.__init__(self)
        self.kind = kind
        self.rect = Rect(pos, self.size)   
        self.sheet = pygame.image.load(self.spritesheet[kind])
        self.image = pygame.Surface(self.size, pygame.SRCALPHA, 32).convert_alpha()
        self.sprites_num = self.sheet.get_width() // self.size[0]
        if kind == "asteroid":
            self.current_sprite = random.randint(0, self.sprites_num)
        else:
            self.current_sprite = current_sprite
        self.image.blit(self.sheet, (0, 0), (self.size[0] * self.current_sprite,
                        0, self.size[0], self.size[1]))
    
    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
        
    def update(self, deltat):
        self.rect.move_ip(SPEED * deltat, 0)


class Spaceship(pygame.sprite.Sprite):
    size = (65, 40)
    def __init__(self, pos, current_sprite=0):
        pygame.sprite.Sprite.__init__(self)
        self.rect = Rect(pos, self.size)   
        self.current_sprite = current_sprite
        self.sheet = pygame.image.load("image/rocket_test4.png")
        self.image = pygame.Surface(self.size, pygame.SRCALPHA, 32).convert_alpha()
        self.sprites_num = self.sheet.get_width() // self.size[0]
        self.image.blit(self.sheet, (0, 0), (self.size[0] * self.current_sprite,
                        0, self.size[0], self.size[1]))
    
    def draw(self, surface):
        self.image = pygame.Surface(self.size, pygame.SRCALPHA, 32).convert_alpha()
        self.image.blit(self.sheet, (0, 0), (self.size[0] * self.current_sprite,
                        0, self.size[0], self.size[1]))
        surface.blit(self.image, self.rect.topleft)
        
    def update(self, event_key):
        # TODO: animar movimentacao (SUAVE!)
        if event_key == K_UP and self.rect.top > 0:
                self.rect.move_ip(0, -50)
        if event_key == K_DOWN and self.rect.bottom <= HEIGHT-50:
                self.rect.move_ip(0, 50)

   
class Explosion(pygame.sprite.Sprite):
    size = (50, 50)
    def __init__(self, pos, timeframe=0.1, current_sprite=0):
        pygame.sprite.Sprite.__init__(self)
        self.rect = Rect(pos, self.size)  
        self.timeframe = timeframe  #tempo por frame
        self.current_sprite = current_sprite
        self.time_counter = 0
        self.sheet = pygame.image.load("image/explosion.png")
        self.image = pygame.Surface(self.size, pygame.SRCALPHA, 32).convert_alpha()
        self.sprites_num = self.sheet.get_width() // self.size[0]

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
        
    def update(self, deltat):
        if self.time_counter > self.timeframe:
            self.current_sprite += 1
            self.time_counter = 0
            self.image = pygame.Surface(self.size, pygame.SRCALPHA, 32).convert_alpha()
            self.image.blit(self.sheet, (0, 0), (self.size[0] * self.current_sprite,
                        0, self.size[0], self.size[1]))
        if self.current_sprite >= self.sprites_num:
            self.kill()  #nesse caso mata o sprite, mas poderia ciclar
        self.time_counter += deltat
        self.rect.move_ip(SPEED * deltat, 0)
                
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
        self.spaceship = Spaceship((150, 0))
        self.explosions = pygame.sprite.Group()
        self.background_pos = 0
        # TODO: colocar as inicializacoes da tela e outras constantes
    
    # adiciona e remove zonas    
    def manage_zones(self, playtime, rows=2):
        if len(self.zones) == 0 or self.zones[-1][0].rect.right <= WIDTH:
            self.zones.append([Zone(row, (8, 8), row) for row in range(rows)])
        if self.zones[0][0].rect.right < 0:
            self.zones.pop(0)

    # verifica qual zona a nave esta
    def detect_zone(self):
        for zone in [row for column in self.zones[:2] for row in column]:
            if zone.rect.collidepoint(self.spaceship.rect.center):
                return zone
      
    # desenha o fundo
    def manage_background(self, surface, deltat):
        self.background_pos += (SPEED/2) * deltat
        if self.background_pos < - WIDTH:
            self.background_pos = 0
        surface.blit(background, (self.background_pos, 0))
        surface.blit(background, (WIDTH + self.background_pos, 0))
        
    # reseta parametros
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
        penaltytime = 0 # contador de tempo da penalidade (3 segundos)
        total_score = 0
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
            # MODO DE JOGO (NUM PAR): contador de preparacao entre os modos jogo
          ##  if self.game_mode % 2:
          ##      if playtime < 1:
          ##          pass #animar texto contando 5 segndos
          ##      else:
          ##          self.game_mode += 1
                    
            # MODO DE JOGO 1: TUTORIAL
            #TODO: COLOCAR FUNcao para modular a velocidade ou densidade
            if self.game_mode == 0:
                self.manage_background(screen, deltat)
                screen.blit(info_bar, (0, HEIGHT - 50))
                self.spaceship.draw(screen)
                for column in self.zones:
                    for zone in column:
                        zone.update(deltat)
                        zone.draw(screen)
                self.explosions.draw(screen)
                self.explosions.update(deltat)
                text = small_font.render("score: "+ str(total_score), True, WHITE)
                screen.blit(text, (WIDTH/2 + text.get_width(), HEIGHT - 30))
                text = small_font.render("time: {}".format(160 - int(playtime)), 
                                         True, WHITE)
                screen.blit(text, (WIDTH/2 - text.get_width(), HEIGHT - 30))
                self.manage_zones(playtime)
                current_zone = self.detect_zone()
                score = 0
                if current_zone:
                    if penalty:
                        penaltytime += deltat
                        log_row = [round(playtime, 4), current_zone.level, score]
                        if penaltytime > 4:
                            penaltytime = 0
                            penalty = False
                            self.spaceship.current_sprite = 0
                    else:
                        sprite = pygame.sprite.spritecollideany(self.spaceship, 
                                                                current_zone) 
                        if sprite:
                            sprite.kill()  #apaga o sprite dos grupos
                            if sprite.kind == "asteroid":
                                score = -current_zone.score 
                                penalty = True
                                self.explosions.add(Explosion(sprite.rect.topleft))
                                play_sound("DeathFlash.ogg", 0)
                                self.spaceship.current_sprite = 1
                            else: #if "item"
                                score = current_zone.score
                        log_row = [round(playtime, 4), current_zone.level, score]
                else:
                    log_row = [round(playtime, 4), -1, score]
                total_score += score
                tutorial_writer.writerow(log_row)
                if playtime >= 160:
                    playtime = 0
                    self.game_mode += 1
                playtime += deltat
                
                
            #MODO : mostra pontuacao total e agradecimento
            if self.game_mode == 1:
                if playtime < 5:
                    text = large_font.render("Pontuacao", True, WHITE)
                    screen.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - 60))
                    text = large_font.render(str(total_score), True, WHITE)
                    screen.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - 20)) 
                if 5 < playtime < 10:
                    text = large_font.render("OBRIGADO!", True, WHITE)
                    screen.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - 60))
                if  playtime > 10:
                    pygame.event.post(pygame.event.Event(QUIT))
                playtime += deltat 
            pygame.display.update()
            

if __name__ == "__main__":
    game = Game()
    game.start()
