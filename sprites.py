import pygame as pg
import random as rd, math
import itertools #.chain (devuelve iterador) para transparencia alpfa en efecto de damage de player
from conf import *
#from tilemap import collide_hit_rect
import pytweening as tween #se debe instalar

vec = pg.math.Vector2
"""Se usan dos rects, uno que varía cuando rotamos la imagen y otro fijo para las colisiones
Si no se diferencían uno del otro, pasan cosas extrañas
"""
def collide_with_wall(sprite,group,dir): #si choco con wall, sigo moviéndome sobre la wall (deslizándome)
    """sprite que colisiona con group"""
    #hits = pg.sprite.spritecollide(self,self.game.walls,False)
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite,group,False,collide_hit_rect) #último parámetro indica qué función de colisión usamos; en este caso una propia
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx: #moviéndose a la derecha-->chocó con lado izq de wall
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width/2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width/2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite,group,False,collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery: #moviéndose hacia abajo
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height/2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height/2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y
    #para que la velocidad cuando vaya en diagonal no sea mayor que la de ejes:
    #if self.vel.x != 0 and self.vel.y != 0: #si está moviendose en diagonal
    #    self.vel *= 0.7071 # 1 / sqrt(2) 

def collide_hit_rect(player,wall): #dos sprites; el one es el player
    return player.hit_rect.colliderect(wall.rect)
    #lo que hace spritecollide es lo mismo pero usando player.rect

class Player(pg.sprite.Sprite):
    def __init__(self,game,x,y): #coordenadas de grid
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game
        #self.image = pg.Surface( (TILESIZE,TILESIZE) )
        #self.image.fill(YELLOW)
        self.image = self.game.player_img
        #self.image = pg.transform.scale(self.image,(TILESIZE,TILESIZE))
        #self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0,0)
        self.pos = vec(x,y) #* TILESIZE #grid coordinates
        self.rot = 0 #rotación de 0 implica que img está viendo hacia la derecha (si uso imagen original)
        self.last_shot = 0
        self.health = PLAYER_HEALTH
        self.damaged = False #para dibujar efecto cuando player gets hit
        self.weapon = 'pistol'
    def get_keys(self):
        self.vel = vec(0,0)
        self.rot_speed = 0
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            #self.vel.x = -PLAYER_SPEED
            self.rot_speed = PLAYER_ROT_SPEED
        if keys[pg.K_RIGHT]: #si pongo elif en vez de if no se puede mover en diagonal!!
            #self.vel.x = PLAYER_SPEED
            self.rot_speed = -PLAYER_ROT_SPEED
        if keys[pg.K_UP]:
            #self.vel.y = -PLAYER_SPEED
            self.vel = vec(PLAYER_SPEED,0).rotate(-self.rot)
        if keys[pg.K_DOWN]:
            #self.vel.y = PLAYER_SPEED
            self.vel = vec(-PLAYER_SPEED,0).rotate(-self.rot)
        if keys[pg.K_SPACE]:
            self.shoot()
    def shoot(self):
        now = pg.time.get_ticks() 
        if now - self.last_shot > WEAPONS[self.weapon]['rate']: #controla qué tan seguido dispara si la tecla está oprimida todo el tiempo
            self.last_shot = now
            pos = self.pos + BULLET_OFFSET.rotate(-self.rot) #posición desde la cual se dibujará la bala; no desde el centro exactamente
            self.vel = vec(-WEAPONS[self.weapon]['kickback'],0).rotate(-self.rot) #patada de mula del disparo que empuja a player hacia atrás
            for i in range(WEAPONS[self.weapon]['bullet_count']):
                spread = rd.uniform(-WEAPONS[self.weapon]['spread'],WEAPONS[self.weapon]['spread'])
                dir = vec(1,0).rotate(-self.rot).rotate(spread)
                Bullet(self.game,pos,dir,spread,WEAPONS[self.weapon]['damage'])
                #rd.choice(list(self.game.shoot_snds.values())).play()    
            snd = rd.choice(self.game.weapon_snds[self.weapon])   
            if snd.get_num_channels() > 2: #en cuántos canales se está tocando ese sound
                snd.stop()
            snd.play()
    def got_hit(self):
        self.damaged = True
        self.alpha_damage = itertools.chain(ALPHA_DAMAGE * 2) #para parpadear dos veces
    def update(self):
        self.get_keys()
        self.pos += self.vel * self.game.dt
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.image = pg.transform.rotate(self.game.player_img,self.rot)
        if self.damaged:
            try:
                self.image.fill((255,0,0,next(self.alpha_damage)), special_flags=pg.BLEND_RGBA_MULT) #flag para determinar'the affected surface area'
            except StopIteration:
                self.damaged = False
        self.rect = self.image.get_rect() #para evitar que se vea el balanceo de la imagen al rotar
        self.rect.center = self.pos
        #self.x += self.vx * self.game.dt #multiplied times game.dt for frame independent movement!! 
        #self.y += self.vy * self.game.dt #to move at a consistent speed, not based on our frame rate
        #descompongo el movimiento en las dos direcciones, en orden, para saber en qué lado colisiono
        self.hit_rect.centerx = self.pos.x
        collide_with_wall(self,self.game.walls,'x')
        self.hit_rect.centery = self.pos.y
        collide_with_wall(self,self.game.walls,'y')
        self.rect.center = self.hit_rect.center
        #OJO! si pongo self.rect.x = ...\self.rect.y =...\self.collide..('x')\self.collide...('y') en ese orden:
        #se descompone el movimiento, hace cosas raras
        #if pg.sprite.collideany(self,self.game.walls): #regresa boolean si colisionó con alguno, no importa cuál
        #    pass
    def add_health(self):
        self.health += HEALTH_ITEM_AMOUNT
        if self.health > PLAYER_HEALTH:
            self.health = PLAYER_HEALTH


class Mob(pg.sprite.Sprite):
    def __init__(self,game,x,y,tipo): #coordenadas de grid
        self._layer = MOB_LAYER
        self.groups = game.mobs, game.all_sprites
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game
        self.tipo = tipo
        self.image = self.game.mob_imgs[tipo].copy() #copia para evitar problemas de que se sobredibuje health bar en todos los mobs cuando daño solo a uno de ellos
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.hit_rect = MOB_HIT_RECT.copy() #copia porque hay varios mobs
        self.hit_rect.center = self.rect.center
        self.health = MOB_HEALTH
        self.pos = vec(x, y)#*TILESIZE
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.rect.center = self.pos
        self.rot = 0
    def update(self):
        target_dist = self.game.player.pos -self.pos
        if target_dist.length_squared() < DETECT_RADIUS**2: #calcular sqrts (teorema Pitágoras) es lento, así que comparamos el cuadrado 
            if rd.random() < 0.008:
                rd.choice(self.game.mob_roar_snds).play()
            self.rot = (target_dist).angle_to(vec(1,0)) #el ángulo formado respecto al eje x entre la diferencia de vectores de posición
            self.image = pg.transform.rotate(self.game.mob_imgs[self.tipo],self.rot)
            self.rect = self.image.get_rect()
            self.rect.center = self.pos
            self.acc = vec(1,0).rotate(-self.rot) #vector unitario primero para poder escalarlo según cercanía o no de otros mobs
            self.avoid_mobs()
            self.acc.scale_to_length(rd.choice(MOB_SPEED))
            self.acc += self.vel*-1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5*self.acc*self.game.dt**2
            self.hit_rect.centerx = self.pos.x
            collide_with_wall(self,self.game.walls,'x')
            self.hit_rect.centery = self.pos.y
            collide_with_wall(self,self.game.walls,'y')
            self.rect.center = self.hit_rect.center
        if self.health <= 0:
            self.kill()
            self.game.map_img.blit(self.game.splash_img,self.pos - vec(32,32)) #para centrar img
            rd.choice(self.game.mob_hit_snds).play()
    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos #vector apuntando a self desde mob, pues en esa dirección nos alejaremos de dicho mob
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize() #cambia la aceleración para alejarlo de mob en esa dirección
                    #normalizado porque solo debe cambiar dirección


    def draw_health(self):
        if MOB_HEALTH*0.6 < self.health <= MOB_HEALTH:
            col = GREEN
        elif MOB_HEALTH*0.3 < self.health <= MOB_HEALTH*0.6:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health/MOB_HEALTH)
        self.health_bar = pg.Rect(0,0,width,8) #se dibujará sobre sprite, no sobre screen
        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image,col,self.health_bar)


"""class Wall(pg.sprite.Sprite):
    def __init__(self,game,x,y): #coordenadas de grid
        #self._layer = WALL_LAYER 
        self.groups = game.walls, game.all_sprites
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game
        self.image = rd.choice(self.game.wall_imgs)
        #self.image = pg.Surface( (TILESIZE,TILESIZE) )
        #self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.x, self.y = x, y
    def update(self):
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE"""


class Obstacle(pg.sprite.Sprite):
    def __init__(self,game,x,y,w,h): #coordenadas de grid
        self.groups = game.walls 
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game
        self.rect = pg.Rect(x,y,w,h)
        self.x, self.y = x, y
        self.rect.x = self.x 
        self.rect.y = self.y 

class Bullet(pg.sprite.Sprite):
    def __init__(self,game,pos,dir,spread,damage): #pos y dir son vectores
        #damage: si disparo pistol y tomo shotgun_item antes de q bala colisione con mob; damage de bala cuando colisione
        #será el correspondiente a pistol, aunque al momento de colisión ya haya cambiado a shotgun
        self._layer = BULLET_LAYER
        self.groups = game.bullets, game.all_sprites
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game
        #self.image = pg.transform.rotate(self.game.bullet_img,self.game.player.rot+spread)
        self.image = pg.transform.rotate(self.game.bullet_imgs[WEAPONS[self.game.player.weapon]['bullet_size']],self.game.player.rot+spread)
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect #se usa en game.draw cuando se hace for para dibujar hit rects de todos los sprites
        self.pos = vec(pos) #OJO!! SE DEBE HACER COPIA O CAMBIA LA POS DEL PLAYER TAMBIÉN
        self.rect.center = self.pos
        Flash(self.game,pos) #creo efecto de flash
        self.vel = dir * WEAPONS[self.game.player.weapon]['bullet_speed'] #multiplicación de un vector unitario en la dirección adecuada con BULLET_SPEED
        self.spawn_time = pg.time.get_ticks() #para lifetime de bullet
        self.damage = damage
    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self,self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > WEAPONS[self.game.player.weapon]['bullet_lifetime']: 
            self.kill()

class Flash(pg.sprite.Sprite):
    def __init__(self,game,pos):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self,self.groups)
        size = rd.randint(20,40)
        self.image = pg.transform.scale(rd.choice(game.gun_flash_imgs),(size,size))
        self.image.set_colorkey(WHITE) #lo puse aquí porque poniendolo en load_data de main no funcionó 
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect #porque en main se usa for sobre todos los hits_rects
        self.rect.center = pos 
        self.spawn_time = pg.time.get_ticks()
    def update(self):
        if pg.time.get_ticks() - self.spawn_time > FLASH_DURATION:
            self.kill()

class Item(pg.sprite.Sprite):
    def __init__(self,game,pos,type):
        self._layer = ITEM_LAYER
        self.groups = game.items, game.all_sprites
        pg.sprite.Sprite.__init__(self,self.groups)
        self.type = type
        self.image = game.item_imgs[self.type]
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = pos
        self.rect.center = self.pos
        self.tween = tween.easeInOutSine #funciones tweening devuelven valor entre 0 y 1 y reciben valores entre 0 y 1
        self.step = 0 #rastrea en dónde estamo entre 0 y 1 según la función tween
        self.dir = 1 #dirección de bobbing de item (arriba/abajo)
    def update(self):
        #bobbing motion
        offset = BOBBING_RANGE * (self.tween(self.step/BOBBING_RANGE) - 0.5) 
        #se resta 0.5 para que el motion empiece desde el centro, no desde un extremo
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOBBING_SPEED
        if self.step > BOBBING_RANGE:
            self.step = 0
            self.dir *= -1 #revierte dirección



        