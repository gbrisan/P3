from multiprocessing.connection import Client
import traceback
import pygame
import sys
pygame.font.init()


BLACK2 = (0, 0, 1)

X = 0
Y = 1
TABLERO = (700, 467)

FIRST_PLAYER = 0
SECOND_PLAYER = 1

FPS = 90

aros = 8
nubes = 2
estrellas = 4

numberpS = ["jugador1", "jugador2"]


#Se define la clase jugador
class Player():
    def __init__(self, numberp):
        self.numberp = numberp
        self.pos = [None, None]

    def get_pos(self):
        return self.pos

    def get_numberp(self):
        return self.numberp

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"P<{numberpS[self.numberp], self.pos}>"

#Se define la clase aro
class aro():
    def __init__(self, number):
        self.pos=[None, None]
        self.numer = number

    def get_pos(self):
        return self.pos

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"B<{self.pos}>"

#Se define la clase estrella
class estrella():
    def __init__(self,number):
        self.pos = [None,None]
        self.number = number
    
    def get_pos(self):
        return self.pos

    def set_pos(self,pos):
        self.pos = pos

    def __str__(self):
        return f"B<{self.pos}>"

#Se define la clase nube     
class nube():
    def __init__(self, number):
        self.pos=[None, None]
        self.numer = number

    def get_pos(self):
        return self.pos

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"B<{self.pos}>"

#Se define la clase juego
class Game():
    def __init__(self):
        self.players = [Player(i) for i in range(2)]
        self.aro = [aro(j) for j in range(aros)]  
        self.estrella = [estrella(i) for i in range(estrellas)] 
        self.nube = [nube(k) for k in range(nubes)]
        self.score = [0,0]
        self.life = [2,2]
        self.running = True

    def get_player(self, numberp):
        return self.players[numberp]

    def get_estrella(self,i):
        return self.estrella[i]

    def get_aro(self,j):
        return self.aro[j]
    
    def get_nube(self,k):
        return self.nube[k]

    def get_score(self):
        return self.score

    def get_life(self):
        return self.life

    def set_pos_player(self, numberp, pos):
        self.players[numberp].set_pos(pos)

    def set_aro_pos(self, j, pos):
        self.aro[j].pos = pos

    def set_estrella_pos(self, i, pos):
        self.estrella[i].pos = pos
    
    def set_nube_pos(self, k, pos):
        self.nube[k].pos = pos

    def set_score(self, score):
        self.score = score
  
    def set_life(self, life):
        self.life = life

    def update(self, gameinfo):
        self.set_pos_player(FIRST_PLAYER, gameinfo['pos_first_player'])
        self.set_pos_player(SECOND_PLAYER, gameinfo['pos_second_player'])
        for i in range(estrellas):
            self.set_estrella_pos(i, gameinfo['pos_estrella_list'][i])
        for i in range(aros):
            self.set_aro_pos(i, gameinfo['pos_aro_list'][i])
        for i in range(nubes):
            self.set_nube_pos(i, gameinfo['pos_nube_list'][i])
        self.set_score(gameinfo['score'])
        self.set_life(gameinfo['life'])
        self.running = gameinfo['is_running']

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False

    def __str__(self):
        return f"G<{self.players[SECOND_PLAYER]}:{self.players[FIRST_PLAYER]}:{self.aro}>"

#En las clases que se definen a continuación se le asigna la apariencia de cada
#uno de los elementos del juego
class Sonic(pygame.sprite.Sprite):
    
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.image = pygame.image.load('sonic1.png')

        self.rect = self.image.get_rect()
        self.update()

    def update(self):
        pos = self.player.get_pos()  
        self.rect.centerx, self.rect.centery = pos

    def __str__(self):
        return f"S<{self.player}>"


class AroSprite(pygame.sprite.Sprite):
    
    def __init__(self, aro):
        super().__init__()
        self.aro = aro
        self.image = pygame.image.load('moneda.png')
        self.rect = self.image.get_rect()
        self.update()
    
    def update(self):
        pos = self.aro.get_pos()
        self.rect.centerx, self.rect.centery = pos
    
    
class estrellaSprite(pygame.sprite.Sprite):
    
    def __init__(self, estrella):
        super().__init__()
        self.estrella = estrella
        self.image = pygame.image.load('estrella.png')
        self.rect = self.image.get_rect()
        self.update()

    def update(self):
        pos = self.estrella.get_pos()
        self.rect.centerx, self.rect.centery = pos

class nubeSprite(pygame.sprite.Sprite):
    
    def __init__(self, nube):
        super().__init__()
        self.nube = nube
        self.image = pygame.image.load('tormenta.png')
        self.rect = self.image.get_rect()
        self.update()

    def update(self):
        pos = self.nube.get_pos()
        self.rect.centerx, self.rect.centery = pos
    


class Display():
    def __init__(self, game):
        
        self.game = game
        self.sonics = [Sonic(self.game.get_player(i)) for i in range(2)]
        self.aro = [AroSprite(self.game.get_aro(i)) for i in range(aros)]
        self.estrella = [estrellaSprite(self.game.get_estrella(i)) for i in range(estrellas)]
        self.nube = [nubeSprite(self.game.get_nube(i)) for i in range(nubes)]
      
        self.all_sprites = pygame.sprite.Group()
        self.sonic_group = pygame.sprite.Group()
        for sonic in self.sonics:
            self.all_sprites.add(sonic)
            self.sonic_group.add(sonic)
        for b in self.aro:
            self.all_sprites.add(b)
        for c in self.estrella:
            self.all_sprites.add(c) 
        for d in self.nube:
            self.all_sprites.add(d)
        self.screen = pygame.display.set_mode(TABLERO) 
        self.clock =  pygame.time.Clock() 
        self.background = pygame.image.load('background.png')
        pygame.init()

    def analyze_events(self, numberp):
        events = []
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    events.append("quit")
            elif event.type == pygame.QUIT:
                events.append("quit")
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
           events.append("left")
        elif keys[pygame.K_RIGHT]:
           events.append("right")
        elif keys[pygame.K_UP]:
           events.append("up")
        elif keys[pygame.K_DOWN]:
            events.append("down")
        for i in range(aros):
            if pygame.sprite.collide_rect(self.aro[i], self.sonics[numberp]): 
                events.append(f"collidearo{i}")
        for i in range(estrellas):
            if pygame.sprite.collide_rect(self.estrella[i], self.sonics[numberp]):
                events.append("collideestrella"+f"{i}")
        for i in range(nubes):
            if pygame.sprite.collide_rect(self.nube[i], self.sonics[numberp]):
                events.append("collidenube"+f"{i}")
        if self.game.life[numberp] == 0:
            events.append("muerte"+f"{numberp}")
        if self.game.score[numberp] > aros//2:
            events.append("victoria"+f"{numberp}")    
        if self.game.score[0] == self.game.score[1] == aros//2 and aros%2 == 0:
            events.append("empate")   
        return events

    
    def refresh(self): #Aspecto del tablero
        
        self.all_sprites.update()
        self.screen.blit(self.background, (0, 0))
        score = self.game.get_score()
        life = self.game.get_life()
        main_font = pygame.font.SysFont("comicsans", 25)
        
        text1 = main_font.render(f"Puntuacion {score[FIRST_PLAYER]}", 1, BLACK2)
        self.screen.blit(text1, (10, 10))
        text = main_font.render(f"Puntuacion {score[SECOND_PLAYER]}", 1, BLACK2)
        self.screen.blit(text, (TABLERO[X]-text.get_width() -30, 10))
        self.all_sprites.draw(self.screen)
        pygame.display.flip() #Update the full display Surface to the screen
        
        text2 = main_font.render(f"Vidas {life[FIRST_PLAYER]}", 5, BLACK2)
        self.screen.blit(text2, (10, 50))
        text3 = main_font.render(f"Vidas {life[SECOND_PLAYER]}", 1, BLACK2)
        self.screen.blit(text3, (TABLERO[X]-text3.get_width() -30, 50))
        self.all_sprites.draw(self.screen)
        pygame.display.flip() #Update the full display Surface to the screen

    def tick(self):
        self.clock.tick(FPS)

    @staticmethod
    def quit():
        pygame.quit()


def main(ip_address):
    try:
        with Client((ip_address, 6000), authkey=b'secret password') as conn:
            game = Game()
            numberp,gameinfo = conn.recv()
            print(f"Empieza la partida {numberpS[numberp]}.")
            game.update(gameinfo)
            display = Display(game)
            while game.is_running():
                events = display.analyze_events(numberp)
                for ev in events:
                    conn.send(ev)
                    if ev == 'quit':
                        game.stop()
                conn.send("next")
                gameinfo = conn.recv()
                game.update(gameinfo)
                display.refresh()
                display.tick()
    except:
        traceback.print_exc()
    finally:
        pygame.quit()


if __name__=="__main__":
    ip_address = "147.96.133.4"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)
