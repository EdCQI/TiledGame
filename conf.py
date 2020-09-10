import pygame as pg
import os

vec = pg.math.Vector2

#tamaño y título de pantalla
TILESIZE = 64 #tamaño de squares en grid

WIDTH = 1024 #16*64 o 32*32  o 64*12 múltiplos para que haya tiles enteros en pantalla
HEIGHT =  768 #16*48 o 32*24 o 64*12
#como nuestro TILESIZE es 32, WIDTH tiene 32 tiles (1024=32*32) y HEIGHT tiene 24 (768=32*24)
TITULO = "TILEMAP GAME"
FPS = 60
FONT_NAME = "Arial"

GAME_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(GAME_DIR,'img')
MAP_DIR = os.path.join(IMG_DIR,'Maps')
SND_DIR = os.path.join(GAME_DIR,'snd')
MUSIC_DIR = os.path.join(SND_DIR,'music')

GRID_WIDTH = WIDTH / TILESIZE
GRID_HEIGHT = HEIGHT / TILESIZE

#colores
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
L_BLUE = (0,255,255)
PURPLE = (255,0,255)
L_GRAY = (100,100,100)
BROWN = (100,55,55)

#player settings
PLAYER_IMG = 'hitman1_silencer.png'
PLAYER_SPEED = 300 #pixels per second! --> normalizado al delta t del juego (game.dt = game.clock.tick(FPS)/1000)
PLAYER_ROT_SPEED = 250 #por segundo debido al dt del game
PLAYER_HIT_RECT = pg.Rect(0,0,32,32) 
PLAYER_HEALTH = 500
PLAYER_H_BAR_W = 100 #health bar width
PLAYER_H_BAR_H = 15

#mobs
MOB_IMGS = ['soldier1_reload.png','zombie1_hold.png']
MOB_SPEED = [PLAYER_SPEED*0.3, PLAYER_SPEED*0.4, PLAYER_SPEED*0.5, PLAYER_SPEED*0.6, PLAYER_SPEED*0.7,PLAYER_SPEED*0.9,PLAYER_SPEED]
MOB_HIT_RECT = pg.Rect(0,0,32,32)
MOB_HEALTH = 100
MOB_DAMAGE = 10 #vida que le quita a player cuando chocan
MOB_KNOCKBACK = 20 #incremento en posición de player cuando colisionan para que no estén todo el tiempo 
#colisionando y player.health no se acabe casi inmediatamente
AVOID_RADIUS = 50 #radio en pixeles de círculo que demarca vecindad de mob para verse afectado cuando está cerca de otros mobs
DETECT_RADIUS = 500 #pixeles a la redonda que pueden ver los mobs para perseguir al player

#walls
WALL_IMGS = []
for i1 in [1,2]:
    for i2 in ['V','H']:
        for i3 in [1,2]:
            WALL_IMGS.append('ladrillo{color}_{orientacion}{tipo}.png'.format(color=i1,orientacion=i2,tipo=i3))

#bullet
BULLET_IMG = 'laser.png'
BULLET_OFFSET = vec(25,10) #(adelante,derecha) pequeño offset para que bala salga de la pistola en la imagen de player
#valores de offset se probaron heurísticamente
"""BULLET_SPEED = PLAYER_SPEED*2
BULLET_LIFETIME = 1000 #milisec
BULLET_RATE = 250 #milisec
KICKBACK = 100 #velocidad que empuja a player atrás cuando dispara
BULLET_SPREAD = 5 #grados que indican cuánto se puede desviar la bala al dispararla para hacerlo un poco aleatorio
BULLET_DAMAGE = 10 #puntos que le quita a mob al colisionar"""

#WEAPONS
WEAPONS = {}
WEAPONS['pistol'] = {'bullet_speed':PLAYER_SPEED*2,
                    'bullet_lifetime':600,
                    'rate': 250,
                    'kickback': 100,
                    'spread': 10,
                    'damage': 4,
                    'bullet_size': 'sm',
                    'bullet_count':3}
WEAPONS['shotgun'] = {'bullet_speed':PLAYER_SPEED*3,
                    'bullet_lifetime':1000,
                    'rate': 400,
                    'kickback': 400,
                    'spread': 5,
                    'damage': 15,
                    'bullet_size': 'lg',
                    'bullet_count':1}

#flashes and effects
FLASH_IMGS = ['explosion1.png','explosion2.png']
FLASH_DURATION = 40 #milisec
ALPHA_DAMAGE = [i for i in range(0,255,15)]

#items
ITEM_IMGS = {'health':'health_item.png',
            'shotgun':'shotgun_item.png'}
HEALTH_ITEM_AMOUNT = PLAYER_HEALTH/4
BOBBING_RANGE = 25 #cuántos pixeles se va a mover arriba y abajo el item en su animación
BOBBING_SPEED = 0.5

#Layers
WALL_LAYER = 1
PLAYER_LAYER = 2 
MOB_LAYER = 2
BULLET_LAYER = 3
ITEM_LAYER = 2
EFFECTS_LAYER = 4

#Sounds
BG_MUSIC = 'espionage.ogg'
PLAYER_HIT_SNDS = ['pain1.wav','pain2.wav','pain3.wav']
MOB_ROAR_SNDS = ['zombie-roar-1.wav','zombie-roar-2.wav','zombie-roar-3.wav','zombie-roar-4.wav','zombie-roar-5.wav']
MOB_HIT_SNDS = ['splat-15.wav']
EFFECTS_SNDS = {'level_start':'level_start.wav',
                'health_up':'health_pack.wav',
                'shotgun_pickup':'health_pack.wav'}
WEAPON_SND = {'pistol':['pistol.wav'],
              'shotgun': ['shotgun.wav']}



