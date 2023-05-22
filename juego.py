from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys
import random

FIRST_PLAYER = 0
SECOND_PLAYER = 1
numberpSSTR = ["jugador1", "jugador2"]

TABLERO = (700, 467)
X=0
Y=1

DELTA = 15

estrellas = 4
aros = 8
nubes = 2

level = []
for i in range(aros):
    level.append([random.randint(0,600), random.randint(0,400)])
    
recarga_energia = [(100,50), (500, 50)]
         
#Se define la clse jugador         
class Player():
    
    def __init__(self, numberp):
        
        '''
        Cada jugador viene definido por su número, 0 o 1, e inicialmente 
        aparecerán cada uno en una de las esquinas inferiores del tablero
        de juego
        '''
        
        self.numberp = numberp
        if numberp == FIRST_PLAYER:
            self.pos = [5, TABLERO[Y]-5]
        else:
            self.pos = [TABLERO[X] - 30, TABLERO[Y]-5]

    def get_pos(self): #posición del jugador
        return self.pos

    def get_numberp(self): #número del jugador
        return self.numberp

    # SE DEFINEN LOS MOVIMIENTOS DEL JUGADOR   
    def moveDown(self):        
        self.pos[Y] += DELTA
        if self.pos[Y] > TABLERO[Y]:
            self.pos[Y] = TABLERO[Y]
    
    def moveRight(self):
        self.pos[X] += DELTA
        if self.pos[X] > TABLERO[X]-40:
            self.pos[X] = TABLERO[X]-40

    def moveLeft(self):
        self.pos[X] -= DELTA
        if self.pos[X] < 0:
            self.pos[X] = 0

    def moveUp(self):
        self.pos[Y] -= DELTA
        if self.pos[Y] < 0:
            self.pos[Y] = 0

    def __str__(self):
        return f"P<{numberpSSTR[self.numberp]}, {self.pos}>"

#Se define la clase aro, los jugadores tienen que atraparlos para ganar
class Aro():
    
    def __init__(self, numero):
        '''
        Cada aro se va a colocar en una posición aleatoria del tablero definida
        en la lista level que se crea al principio del códdigo 
        '''
        self.pos = [level[numero][0], level[numero][1]]

    def get_pos(self): #posición del aro
        return self.pos

    def update(self): #los aros están fijos en el tablero
        self.pos[X] = self.pos[X]
        self.pos[Y] = self.pos[Y]

    def collide_player(self, numberp):
        '''
        Si algún jugador coge el aro entonces este se colocará en la parte
        derecha de la pantalla que no forma parte del espacio del tablero 
        donde se pueden mover los jugadores
        '''        
        self.pos[X] = TABLERO[X]-10
        self.pos[Y] = random.randint(0, 467)


#Se define la clase estrellan que restan una vida al jugador con el que colisionen
class estrella():
    
    def __init__(self, number,velocity):
        self.pos=[ random.randint(0,700) , 0 ]
        self.velocity = velocity
        self.number = number

    def get_pos(self): #posición de la estrella
        return self.pos

    def get_number(self):
        return self.number
    
    #Las estrellas se moverán en el tablero
    def update(self):
        self.pos[X] += self.velocity[X]
        self.pos[Y] += self.velocity[Y]

    def edge(self, AXIS):
        self.velocity[AXIS] = -self.velocity[AXIS]
    
    #Cuando una estrella choca a un jugador vuelve a la parte superior del tablero
    def collide_player(self, numberp):        
        self.pos[X] = random.randint(0,700)
        self.pos[Y] = 0

    def __str__(self):
        return f"B<{self.pos, self.velocity}>"

#Se define la clase nube que otorga una vida al jugador que la alcance
        
class Nube():
    
    def __init__(self, numero):
        '''
        Inicialmente las nubes se colocan en la posiciones establecidad en una
        lista al inicio del código
        '''
        self.pos = [recarga_energia[numero][0], recarga_energia[numero][1]]

    def get_pos(self):
        return self.pos

    def update(self): #Las nubes están fijas en el tablero
        self.pos[X] = self.pos[X]
        self.pos[Y] = self.pos[Y]

    def collide_player(self, numberp):
        '''
        Si algún jugador atrapa una nube esta se desplaza a otra posición en la 
        misma vertical
        '''        
        self.pos[X] = self.pos[X]
        self.pos[Y] = random.randint(10,390)

    
class Game():
    
    def __init__(self, manager):
        '''
        El juego se inicializa con los jugadores, los aros y sus posiciones, las
        nubes y sus posiciones, las estrellas y sus posiciones, las vidas iniciales,
        los marcadores inicializados en 0. Un lock que sincronizará todos los
        movimientos y colisiones en el juego
        '''
        self.players = manager.list( [Player(FIRST_PLAYER), Player(SECOND_PLAYER)] )
        
        self.aro = manager.list( ([Aro(j) for j in range(aros)]) )
        self.aro_pos = manager.list([self.aro[j].get_pos() for j in range(aros)])
        
        self.nube = manager.list(([Nube(j) for j in range(nubes)]) )
        self.nube_pos = manager.list([self.nube[j].get_pos() for j in range(nubes)])
        
        self.score = manager.list( [0,0] )
        self.life = manager.list( [3,3] )
        
        self.estrella = manager.list([estrella(i,[random.randint(-3,3),random.randint(5,7)]) for i in range(estrellas)])
        self.estrella_pos = manager.list([self.estrella[i].get_pos() for i in range(estrellas)])
        
        self.running = Value('i', 1)
        self.lock = Lock()

    def get_player(self, numberp):
        return self.players[numberp]

    def get_aro(self, j):
        return self.aro[j]

    def get_estrella(self,i):
        return self.estrella[i]
    
    def get_nube(self, k):
        return self.nube[k]

    def get_score(self):
        return list(self.score)
    
    def get_life(self):
        return list(self.life)

    def is_running(self):
        return self.running.value == 1

    def stop(self):
        self.running.value = 0
    
    #Movimientos sincronizados de los jugadores 
    def moveUp(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveUp()
        self.players[player] = p
        self.lock.release()
    
    def moveLeft(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveLeft()
        self.players[player] = p
        self.lock.release()
    
    def moveRight(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveRight()
        self.players[player] = p
        self.lock.release()

    def moveDown(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveDown()
        self.players[player] = p
        self.lock.release()
    
    #Colisiones sincronizadas
    def aro_collide(self, playernumberp, aronumberp):
        self.lock.acquire()
        aro = self.aro[aronumberp]
        aro.collide_player(playernumberp)    
        self.aro[aronumberp] = aro
        self.lock.release()

    def estrella_collide(self,i, playernumberp):
        self.lock.acquire()
        estrella = self.estrella[i]
        estrella.collide_player(playernumberp)    
        self.estrella[i] = estrella
        self.lock.release()
        
    def nube_collide(self,playernumberp, nubenumberp):
        self.lock.acquire()
        nube = self.nube[nubenumberp]
        nube.collide_player(playernumberp)    
        self.nube[nubenumberp] = nube
        self.lock.release()
    
      

    def get_info(self):
        info = {
            'pos_first_player': self.players[FIRST_PLAYER].get_pos(),
            'pos_second_player': self.players[SECOND_PLAYER].get_pos(),
            'score': list(self.score),
            'life' : list(self.life),
            'is_running': self.running.value == 1,
            'pos_estrella_list': list(self.estrella_pos),
            'pos_aro_list': list(self.aro_pos),
            'pos_nube_list':list(self.nube_pos)
         
        }
        return info
    
    #Movimientos sincronizados de los aros, las estrellas y las nubes
    def move_aro(self,j):
        self.lock.acquire()
        aro = self.aro[j]
        aro.update()
        pos = aro.get_pos()

        self.aro[j] = aro
        self.aro_pos[j] = [pos[X],pos[Y]]
        self.lock.release()
    
    def move_estrella(self,i):
        self.lock.acquire()
        estrella = self.estrella[i]
        estrella.update()
        pos = estrella.get_pos()
        if pos[Y]<0 or pos[Y]>TABLERO[Y]:
            pos[Y] = 0        
            pos[X] = random.randint(10,700)
        self.estrella[i]=estrella
        self.estrella_pos[i] = [pos[X],pos[Y]]
        self.lock.release()
        
    def move_nube(self,k):
        self.lock.acquire()
        nube = self.nube[k]
        nube.update()
        pos = nube.get_pos()
        
        self.nube[k] = nube
        self.nube_pos[k] = [pos[X],pos[Y]]
        self.lock.release()

    def __str__(self):
        return f"G<{self.players[SECOND_PLAYER]}:{self.players[FIRST_PLAYER]}:{self.aro[0]}:{self.running.value}>"

def player(numberp, conn, game):
    
    try:
        print(f"starting player {numberpSSTR[numberp]}:{game.get_info()}")
        conn.send( (numberp, game.get_info()) )
        while game.is_running():
            command = ""
            while command != "next":
                command = conn.recv()
                if command == "up":
                    game.moveUp(numberp)
                elif command == "down":
                    game.moveDown(numberp)
                elif command == "right":
                    game.moveRight(numberp)
                elif command == "left":
                    game.moveLeft(numberp)
                elif "collidearo" in command:
                    j = int(command[10])
                    game.aro_collide(numberp,j)
                    game.score[numberp] +=1
                elif "collideestrella" in command:
                    i = int(command[15]) 
                    game.estrella_collide(i,numberp)
                    game.life[numberp] -=1  
                elif "collidenube" in command:
                    k = int(command[11]) 
                    game.nube_collide(numberp,k)
                    game.life[numberp] +=1                                   
                elif command == "quit":
                    game.stop()
                elif "muerte" in command:
                    game.stop()
                    print('El jugador ' + f'{numberp + 1}' + ' murió')
                    if numberp == 0 :
                        print('El jugador ' + f'{2}' + ' ha ganado')
                    else: 
                        print('El jugador ' + f'{1}' + ' ha ganado')
                elif "victoria" in command:
                    game.stop()
                    print('El jugador ' + f'{numberp + 1}' + ' ha ganado')
                elif "empate" in command:
                    game.stop()
                    print('EMPATE')
            if numberp == 1:
                for i in range(aros):
                    game.move_aro(i)
                for i in range(estrellas):
                    game.move_estrella(i)
                for i in range(nubes):
                    game.move_nube(i)

            conn.send(game.get_info())
    except:
        traceback.print_exc()
        conn.close()
    finally:
        print(f"Game ended {game}")


def main(ip_address):
    manager = Manager()
    try:
        with Listener((ip_address, 6000),
                      authkey=b'secret password') as listener:
            n_player = 0
            players = [None, None]
            game = Game(manager)
            while True:
                print(f"accepting connection {n_player}")
                conn = listener.accept()
                players[n_player] = Process(target=player,
                                            args=(n_player, conn, game))
                n_player += 1
                if n_player == 2:
                    players[0].start()
                    players[1].start()
                    n_player = 0
                    players = [None, None]
                    game = Game(manager)

    except Exception as e:
        traceback.print_exc()

if __name__=='__main__':
    ip_address = "147.96.133.4"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]

    main(ip_address)
