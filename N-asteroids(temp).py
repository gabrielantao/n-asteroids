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
import os 
import sys
import random
import math
import csv
import datetime
import pygame
from pygame.locals import *
pygame.init()

WIDTH = 1200
HEIGHT = 850
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# cria o clock 
clock = pygame.time.Clock()

# inicializa screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("N-asteroids")

# carrega imagens
SPRITESHEET = {}
SPRITESHEET["normal"] = {"logo": pygame.image.load(os.path.join("image", "logo.png")),
                         "background": pygame.image.load(os.path.join("image", "background.png")),
                         "infobar": pygame.image.load(os.path.join("image", "infobar.png")),
                         "asteroid": pygame.image.load(os.path.join("image", "asteroid.png")),
                         "item": pygame.image.load(os.path.join("image", "item.png")),
                         "ship": pygame.image.load(os.path.join("image", "ship.png")),
                         "explosion": pygame.image.load(os.path.join("image", "explosion.png"))}

SPRITESHEET["vintage"] = {"logo": pygame.image.load(os.path.join("image", "logo_vin.png")),
                         "background": pygame.image.load(os.path.join("image", "background.png")),
                         "infobar": pygame.image.load(os.path.join("image", "infobar_vin.png")),
                         "asteroid": pygame.image.load(os.path.join("image", "asteroid_vin.png")),
                         "item": pygame.image.load(os.path.join("image", "item_vin.png")),
                         "ship": pygame.image.load(os.path.join("image", "ship_vin.png")),
                         "explosion": pygame.image.load(os.path.join("image", "explosion_vin.png"))}

# carrega fontes
small_font = pygame.font.Font("font/HANGAR_flat.ttf", 20)
large_font = pygame.font.Font("font/HANGAR_flat.ttf", 40)
super_large_font = pygame.font.Font("font/HANGAR_flat.ttf", 60)

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
    def __init__(self, style, row, dimension, level):
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
        self.fill(style)
        
    def fill(self, style):
        asteroid_num = int(self.asteroid_density * self.dimension[0] * self.dimension[1])
        item_num = int(self.item_density * self.dimension[0] * self.dimension[1])
        assert item_num > 0, "item_num == 0. Redefinir densidade de itens."
        pos_set = set()        
        while len(pos_set) < asteroid_num + item_num:
            pos_set.add((random.randrange(0, self.dimension[0]),
                         random.randrange(0, self.dimension[1])))
        for i in range(asteroid_num):
            tile_pos = pos_set.pop()
            pos = (self.rect.x + tile_pos[0] * self.sprite_size[0],
                   self.rect.y + tile_pos[1] * self.sprite_size[1])
            self.add(Object(style, "asteroid", pos))
        for i in range(item_num):
            tile_pos = pos_set.pop()
            pos = (self.rect.x + tile_pos[0] * self.sprite_size[0],
                   self.rect.y + tile_pos[1] * self.sprite_size[1])
            self.add(Object(style, "item", pos, self.level))  
    
    #TODO: remover esse metodo (SOMENTE PARA DEBUG)
    def draw(self, surface, debug=False):
       ## super(self.__class__, self).draw(surface)
        for sprite in self.sprites():
            sprite.draw(surface, debug)
        if debug:
            pygame.draw.rect(surface, (255,0,0), self.rect, 1)
            
    def update(self, speed, deltat):
        self.rect.move_ip(speed * deltat, 0)
        super(self.__class__, self).update(speed, deltat)
 
        
class Object(pygame.sprite.Sprite):
    size = (50, 50)
    def __init__(self, style, kind, pos, current_sprite=0):
        pygame.sprite.Sprite.__init__(self)
        self.kind = kind
        self.rect = Rect(pos, self.size)   
        self.sheet = SPRITESHEET[style][kind]
        self.image = pygame.Surface(self.size, pygame.SRCALPHA, 32).convert_alpha()
        self.sprites_num = self.sheet.get_width() // self.size[0]
        if kind == "asteroid":
            self.current_sprite = random.randrange(0, self.sprites_num)
        else:
            self.current_sprite = current_sprite
        self.image.blit(self.sheet, (0, 0), (self.size[0] * self.current_sprite,
                        0, self.size[0], self.size[1]))
        self.radius = 28
        
    def draw(self, surface, debug=False):
        surface.blit(self.image, self.rect.topleft)
        if debug:
            pygame.draw.circle(surface, (255,0,255), self.rect.center, self.radius, 1)
        
    def update(self, speed, deltat):
        self.rect.move_ip(speed * deltat, 0)
        
        
class Spaceship(pygame.sprite.Sprite):
    size = (50, 30)
    def __init__(self, style, pos, current_sprite=0):
        pygame.sprite.Sprite.__init__(self)
        self.rect = Rect(pos, self.size)   
        self.current_sprite = current_sprite
        self.sheet = SPRITESHEET[style]["ship"]
        self.image = pygame.Surface(self.size, pygame.SRCALPHA, 32).convert_alpha()
        self.sprites_num = self.sheet.get_width() // self.size[0]
        self.image.blit(self.sheet, (0, 0), (self.size[0] * self.current_sprite,
                        0, self.size[0], self.size[1]))
        self.radius = 20 
        self.destiny = self.rect.centery
        self.set_move_func(0, 0)
        
    def set_move_func(self, t0, increment):
        self.destiny += increment * 50
        self.move = lambda t: self.rect.centery + \
                              int((self.destiny-self.rect.centery) * \
                                  (1.0-round(math.exp(-4*(t-t0)), 1)))   
        
    def draw(self, surface, debug=False):
        self.image = pygame.Surface(self.size, pygame.SRCALPHA, 32).convert_alpha()
        self.image.blit(self.sheet, (0, 0), (self.size[0] * self.current_sprite,
                        0, self.size[0], self.size[1]))
        surface.blit(self.image, self.rect.topleft)
        if debug:
            pygame.draw.circle(surface, (0,255,0), self.rect.center, self.radius, 1)
    
    def update(self, playtime):
        self.rect.centery = self.move(playtime)
        
   
class Explosion(pygame.sprite.Sprite):
    size = (50, 50)
    def __init__(self, style, pos, timeframe=0.1, current_sprite=0):
        pygame.sprite.Sprite.__init__(self)
        self.rect = Rect(pos, self.size)  
        self.timeframe = timeframe  #tempo por frame
        self.current_sprite = current_sprite
        self.time_counter = 0
        self.sheet = SPRITESHEET[style]["explosion"]
        self.image = pygame.Surface(self.size, pygame.SRCALPHA, 32).convert_alpha()
        self.sprites_num = self.sheet.get_width() // self.size[0]

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
        
    def update(self, speed, deltat):
        if self.time_counter > self.timeframe:
            self.current_sprite += 1
            self.time_counter = 0
            self.image = pygame.Surface(self.size, pygame.SRCALPHA, 32).convert_alpha()
            self.image.blit(self.sheet, (0, 0), (self.size[0] * self.current_sprite,
                        0, self.size[0], self.size[1]))
        if self.current_sprite >= self.sprites_num:
            self.kill()  #nesse caso mata o sprite, mas poderia ciclar a animacao
        self.time_counter += deltat
        self.rect.move_ip(speed * deltat, 0)
                
class Game():
    """
    0 modo contagem (5 segundos) 
    1 modo tutorial; 
    2 modo jogo;    
    """
    FPS = 50 # maximo frames por segundo
    INITIAL_SPEED = -200 #velocidade inicial
    WAIT_TIME = 300  #tempo de repouso)
    TUTORIAL_TIME = 60 #tempo de jogo para tutorial
    GAME_TIME = 60 # tempo de jogo (duas densidades)
    SPEED_INTERVAL = 15 # intervalo para nova velocidade 
    def __init__(self):
        self.style = "vintage"
        self.set_images()
        self.game_mode = 0
        self.zones = []
        self.spaceship = Spaceship(self.style, (150, 10+300))
        self.explosions = pygame.sprite.Group()
        ##self.stars = pygame.sprite.Group()  #background
        self.background_pos = 0
        self.zone_dim = (16, 16)
        self.rows = 1
        try:
            os.mkdir("experiments")
        except:
            pass
    
    # modifica as imagens base do jogo
    def set_images(self):
        self.logo = SPRITESHEET[self.style]["logo"]
        self.background = SPRITESHEET[self.style]["background"]
        self.infobar = SPRITESHEET[self.style]["infobar"]
   
    # adiciona e remove zonas    
    def manage_zones(self):
        rows = self.rows
        if len(self.zones) == 0 or self.zones[-1][0].rect.right <= WIDTH:
            self.zones.append([Zone(self.style, row, self.zone_dim, row) for row in range(rows)])
        if self.zones[0][0].rect.right < 0:
            self.zones.pop(0)

    # verifica qual zona a nave esta
    def detect_zone(self):
        for zone in [row for column in self.zones[:2] for row in column]:
            if zone.rect.collidepoint(self.spaceship.rect.center):
                return zone
      
    # desenha o fundo
    def manage_background(self, surface, deltat):
        self.background_pos += (self.INITIAL_SPEED/2) * deltat
        if self.background_pos < - WIDTH:
            self.background_pos = 0
        surface.blit(background, (self.background_pos, 0))
        surface.blit(background, (WIDTH + self.background_pos, 0))
    
    # detecta colisao por regioes circulares
    def spaceship_collision(self, current_zone):
        for sprite in current_zone:
            if pygame.sprite.collide_circle(self.spaceship, sprite):
                return sprite
                
    # reseta parametros
    def reset(self):
        self.playtime = 0 # tempo jogado por partida
        self.second = 1   # contador de segundos (regressivo) 
        self.penalty = False # estado de penalidade 
        self.penaltytime = 0 # contador de tempo da penalidade (3 segundos)
        self.total_score = 0 # pontuacao total
        
    def start(self, DEBUG=False):
        directory = os.path.join("experiments",
                            "{:%Y-%b-%d %H-%M-%S}".format(datetime.datetime.now()))
        os.mkdir(directory)
        log_tutorial = open("{}/tutorial.csv".format(directory), "w")
        tutorial_writer = csv.writer(log_tutorial)
        tutorial_writer.writerow(["time", "risklevel", "score", "speed"])
        log_game = open("{}/game.csv".format(directory), "w")
        game_writer = csv.writer(log_game)
        game_writer.writerow(["time", "risklevel", "score", "speed"])   
        self.playtime = 0 # tempo jogado por partida
        self.second = 1   # contador de segundos (regressivo) 
        self.penalty = False # estado de penalidade 
        self.penaltytime = 0 # contador de tempo da penalidade (3 segundos)
        self.total_score = 0 # pontuacao total
        cursor = 0 # cursor de selecao 
        while True:
            milliseconds = clock.tick(self.FPS)  # milisegundos passados desde ultimo frame
            deltat = milliseconds/1000.0    # delta de tempo em segundos
            screen.fill(BLACK)
            for event in pygame.event.get():
                if event.type == QUIT:
                    log_tutorial.close()
                    log_game.close()
                    pygame.quit()
                if event.type == KEYDOWN:
                    ship_tile = int(self.spaceship.rect.centery/50) 
                    #self.rows*self.zone_dim[1]-1:
                    if event.key == K_UP:
                        if self.game_mode == 0 and cursor > 0:
                            cursor -= 1
                            self.style = "vintage"
                            self.set_images()
                        if (self.game_mode == 3 or self.game_mode == 5) and \
                        ship_tile > 0:
                            self.spaceship.set_move_func(self.playtime, -1)
                    if event.key == K_DOWN:
                        if self.game_mode == 0 and cursor < 1:
                            cursor += 1
                            self.style = "normal"
                            self.set_images()
                        if (self.game_mode == 3 or self.game_mode == 5) and \
                        ship_tile < self.rows*self.zone_dim[1]-1:
                            self.spaceship.set_move_func(self.playtime, 1)
                    if  event.key == K_RETURN or event.key == K_KP_ENTER:
                        if self.game_mode == 0:
                            self.game_mode += 1    
                            self.playtime = 0
                            self.set_images()
                            self.spaceship = Spaceship(self.style, (150, 10+300))
                           

        #-----------------------------------------------------------------------
        # GERENCIA OS MODOS DE JOGO
        #-----------------------------------------------------------------------
            # MODO 0: tela inicial (selecao do estilo)
            if self.game_mode == 0:
                ##self.manage_background(screen, deltat)
                screen.blit(self.logo, (WIDTH/2 - self.logo.get_width()/2 + 30 , 300))
                text = small_font.render("vintage", True, WHITE)
                screen.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 + 100))
                text = small_font.render("normal", True, WHITE)
                screen.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 + 150))
                text = large_font.render("Pressione [ENTER]", True, WHITE)
                screen.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 + 300))
                pygame.draw.circle(screen, (255,0,0), (WIDTH/2 - 40, HEIGHT/2 + 110 + cursor*50), 5)
                self.playtime += deltat
                # TODO: colocar a selecao em si na secao de eventos (usar exemplo do flapy mario)
                #        usar set_images para setar as novas imagens !!!
                
            # MODO 1: repouso inicial
            if self.game_mode == 1:
                pygame.draw.line(screen, WHITE, (WIDTH/2, HEIGHT/2 - 50), 
                                 (WIDTH/2, HEIGHT/2 + 50), 4)
                pygame.draw.line(screen, WHITE, (WIDTH/2 - 50, HEIGHT/2), 
                                 (WIDTH/2 + 50, HEIGHT/2), 4)                 
                if self.playtime >= 1: # TODO: alterar para self.WAIT_TIME:
                    self.playtime = 0 
                    self.game_mode += 1
                self.playtime += deltat
        
            # MODO 2: contagem regressiva
            if self.game_mode == 2:
                ##self.manage_background(screen, 0)
                self.spaceship.draw(screen, DEBUG)
                pygame.draw.circle(screen, WHITE,(WIDTH/2, HEIGHT/2-35), 40, 2)
                if  self.second >= 1:
                    play_sound("beep-pre.ogg", 0)
                    self.second = 0
                if self.playtime <= 5:
                    text = super_large_font.render(str(5 - int(self.playtime)), True, WHITE)
                    screen.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - 60))
                else:
                    self.playtime = 0 
                    self.second = 1   
                    self.game_mode += 1
                self.playtime += deltat
                self.second += deltat
                
            # TODO: ajsutar entrada no arquivo de log da velocidade atual        
            # MODO 3: calibracao
            if self.game_mode == 3:
                ##self.manage_background(screen, deltat)
                speed = self.INITIAL_SPEED - 100 * (self.playtime//self.SPEED_INTERVAL)
                screen.blit(self.infobar, (0, HEIGHT - 50))
                self.spaceship.draw(screen, DEBUG)
                self.spaceship.update(self.playtime)
                for column in self.zones:
                    for zone in column:
                        zone.update(speed, deltat)
                        zone.draw(screen, DEBUG)
                self.explosions.draw(screen)
                self.explosions.update(speed, deltat)
                text = small_font.render("score: "+ str(self.total_score), True, WHITE)
                screen.blit(text, (WIDTH/2 + text.get_width(), HEIGHT - 30))
                text = small_font.render("time: {}".format(self.TUTORIAL_TIME - int(self.playtime)), 
                                         True, WHITE)
                screen.blit(text, (WIDTH/2 - text.get_width(), HEIGHT - 30))
                text = small_font.render("FPS: "+ str(int(clock.get_fps())), True, WHITE)
                screen.blit(text, (WIDTH - text.get_width() - 15, HEIGHT - 30))
                self.manage_zones()
                current_zone = self.detect_zone()
                score = 0
                if current_zone:
                    if self.penalty:
                        self.penaltytime += deltat
                        log_row = [round(self.playtime, 4), current_zone.level, score, abs(speed)]
                        if self.penaltytime > 4:
                            self.penaltytime = 0
                            self.penalty = False
                            self.spaceship.current_sprite = 0
                    else:
                        sprite = self.spaceship_collision(current_zone) 
                        if sprite:
                            sprite.kill()  #apaga o sprite dos grupos
                            if sprite.kind == "asteroid":
                                score = -current_zone.score 
                                self.penalty = True
                                self.explosions.add(Explosion(self.style, sprite.rect.topleft))
                                play_sound("DeathFlash.ogg", 0)
                                self.spaceship.current_sprite = 1
                            else: #if "item"
                                score = current_zone.score
                                play_sound("pickup_item.ogg", 0)
                        log_row = [round(self.playtime, 4), current_zone.level, score, abs(speed)]
                else:
                    log_row = [round(self.playtime, 4), -1, score, abs(speed)]
                self.total_score += score
                tutorial_writer.writerow(log_row)
                if self.playtime >= 60:##self.TUTORIAL_TIME:
                    self.playtime = 0 
                    self.second = 1   
                    self.penalty = False 
                    self.penaltytime = 0 
                    self.total_score = 0 
                    self.game_mode += 1
                    self.zones = []
                    self.spaceship = Spaceship(self.style, (150, 10+300))
                    self.zone_dim = (8, 8)
                    self.rows = 2
                self.playtime += deltat
          
            # MODO 4: contagem regressiva
            if self.game_mode == 4:
                ##self.manage_background(screen, 0)
                self.spaceship.draw(screen, DEBUG)
                pygame.draw.circle(screen, WHITE,(WIDTH/2, HEIGHT/2-35), 40, 2)
                if  self.second >= 1:
                    play_sound("beep-pre.ogg", 0)
                    self.second = 0
                if self.playtime <= 5:
                    text = super_large_font.render(str(5 - int(self.playtime)), True, WHITE)
                    screen.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - 60))
                else:
                    self.playtime = 0 
                    self.second = 1   
                    self.game_mode += 1
                self.playtime += deltat
                self.second += deltat
                
            # MODO 5: jogo com duas densidades
            if self.game_mode == 5:
                ##self.manage_background(screen, deltat)
                speed = self.INITIAL_SPEED - 100 * (self.playtime//self.SPEED_INTERVAL)
                screen.blit(self.infobar, (0, HEIGHT - 50))
                self.spaceship.draw(screen, DEBUG)
                self.spaceship.update(self.playtime)
                for column in self.zones:
                    for zone in column:
                        zone.update(speed, deltat)
                        zone.draw(screen, DEBUG)
                self.explosions.draw(screen)
                self.explosions.update(speed, deltat)
                text = small_font.render("score: "+ str(self.total_score), True, WHITE)
                screen.blit(text, (WIDTH/2 + text.get_width(), HEIGHT - 30))
                text = small_font.render("time: {}".format(self.GAME_TIME - int(self.playtime)), 
                                         True, WHITE)
                screen.blit(text, (WIDTH/2 - text.get_width(), HEIGHT - 30))
                text = small_font.render("FPS: "+ str(int(clock.get_fps())), True, WHITE)
                screen.blit(text, (WIDTH - text.get_width() - 15, HEIGHT - 30))
                self.manage_zones()
                current_zone = self.detect_zone()
                score = 0
                if current_zone:
                    if self.penalty:
                        self.penaltytime += deltat
                        log_row = [round(self.playtime, 4), current_zone.level, score, abs(speed)]
                        if self.penaltytime > 4:
                            self.penaltytime = 0
                            self.penalty = False
                            self.spaceship.current_sprite = 0
                    else:
                        sprite = self.spaceship_collision(current_zone) 
                        if sprite:
                            sprite.kill()  #apaga o sprite dos grupos
                            if sprite.kind == "asteroid":
                                score = -current_zone.score 
                                self.penalty = True
                                self.explosions.add(Explosion(self.style, sprite.rect.topleft))
                                play_sound("DeathFlash.ogg", 0)
                                self.spaceship.current_sprite = 1
                            else: #if "item"
                                score = current_zone.score
                                play_sound("pickup_item.ogg", 0)
                        log_row = [round(self.playtime, 4), current_zone.level, score, abs(speed)]
                else:
                    log_row = [round(self.playtime, 4), -1, score, abs(speed)]
                self.total_score += score
                game_writer.writerow(log_row)
                if self.playtime >= 60:#self.GAME_TIME:
                    self.playtime = 0 
                    self.game_mode += 1
                    play_sound("Well Done.ogg", 0)
                self.playtime += deltat
                
            #MODO 6: mostra pontuacao total e agradecimento
            if self.game_mode == 6:
                if self.playtime < 5:
                    text = large_font.render("Pontuacao", True, WHITE)
                    screen.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - 60))
                    text = large_font.render(str(self.total_score), True, WHITE)
                    screen.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - 20)) 
                if 5 < self.playtime < 10:
                    text = large_font.render("OBRIGADO!", True, WHITE)
                    screen.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - 60))
                if  self.playtime > 10:
                    pygame.event.post(pygame.event.Event(QUIT))
                self.playtime += deltat 
            pygame.display.update()
            

if __name__ == "__main__":
    game = Game()
    game.start(True)

