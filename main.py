import pygame as pg
from pygame.locals import *
import sys, os, math, random as rd
from conf import *
from tilemap import * 
from sprites import *


def draw_player_health(surf,x,y,pct):
    if pct < 0 : pct = 0
    fill = PLAYER_H_BAR_W*pct
    outline_rect = pg.Rect(x,y,PLAYER_H_BAR_W,PLAYER_H_BAR_H)
    fill_rect = pg.Rect(x,y,fill,PLAYER_H_BAR_H)
    if 0.6 < pct <= 1:
        col = GREEN
    elif 0.3 < pct <= 0.6:
        col = YELLOW
    else: col = RED
    pg.draw.rect(surf,col,fill_rect)
    pg.draw.rect(surf,WHITE,outline_rect,2)


class Game:
    def __init__(self):
        pg.mixer.pre_init(44100,-16,1,2048) #los primerso 3 parámetros son default, el último es tamaño de 
        #buffer que ayuda a evitar lags en sound effects y debe ser en potencias de 2s
        pg.init()
        self.screen = pg.display.set_mode( (WIDTH,HEIGHT) )
        pg.display.set_caption(TITULO)
        self.font = pg.font.match_font(FONT_NAME)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500,100) #how long to wait to start repetitions, repeat every 100
        self.load_data()
        self.running = True
        self.paused = False
    def load_data(self):
        #self.map = Map(os.path.join(GAME_DIR,'map.txt'))
        self.surf_pause = pg.Surface(self.screen.get_size()).convert_alpha() #superficie gris para ponerla cuando esté en pausa
        self.surf_pause.fill((0,0,0,150)) #último parámetro es transparencia-->si es 0 es completamente transparente,255 es negro
        #IMÁGENES
        self.player_img = pg.image.load(os.path.join(IMG_DIR,PLAYER_IMG)).convert_alpha()
        self.wall_imgs = []
        for img in WALL_IMGS:
            self.wall_imgs.append(pg.image.load(os.path.join(IMG_DIR,img)).convert_alpha())
        self.wall_imgs = [pg.transform.scale(im,(TILESIZE,TILESIZE)) for im in self.wall_imgs]
        self.mob_imgs = [pg.image.load(os.path.join(IMG_DIR,im)).convert_alpha() for im in MOB_IMGS ]
        self.mob_imgs = dict( zip(['M','N'], self.mob_imgs) )
        self.bullet_imgs = {}
        self.bullet_imgs['lg'] = pg.image.load(os.path.join(IMG_DIR,BULLET_IMG)).convert_alpha()
        self.bullet_imgs['lg'] = pg.transform.scale(self.bullet_imgs['lg'],(6,12))
        self.bullet_imgs['lg'] = pg.transform.rotate(self.bullet_imgs['lg'],-90) #-90 grados (negativo para dir en manecillas de reloj)
        #se rota porque la img original está apuntando hacia arriba
        self.bullet_imgs['sm'] = pg.transform.scale(self.bullet_imgs['lg'],(4,8))
        self.gun_flash_imgs = []
        for im in FLASH_IMGS:
            self.gun_flash_imgs.append(pg.image.load(os.path.join(IMG_DIR,im)).convert_alpha())
        self.item_imgs = {}
        for item in ITEM_IMGS:
            self.item_imgs[item] = pg.image.load(os.path.join(IMG_DIR,ITEM_IMGS[item])).convert_alpha()
            self.item_imgs[item].set_colorkey(WHITE)
        self.splash_img = pg.image.load(os.path.join(IMG_DIR,'splash.png')).convert_alpha()
        self.splash_img.set_colorkey(WHITE)
        #SOUNDS
        pg.mixer.music.load(os.path.join(MUSIC_DIR,BG_MUSIC))
        self.effects_snds = {}
        for type in EFFECTS_SNDS:
            self.effects_snds[type] = pg.mixer.Sound(os.path.join(SND_DIR,EFFECTS_SNDS[type]))
        self.weapon_snds = {}
        for type in WEAPON_SND: #recorre tipos (llaves)
            self.weapon_snds[type] = []
            for snd in WEAPON_SND[type]: #recorre lista de sounds por cada tipo
                s = pg.mixer.Sound(os.path.join(SND_DIR,snd))
                s.set_volume(0.5)
                self.weapon_snds[type].append(s)
        self.mob_roar_snds = []
        for snd in MOB_ROAR_SNDS:
            s = pg.mixer.Sound(os.path.join(SND_DIR,snd))
            s.set_volume(0.15)
            self.mob_roar_snds.append(s) #set_volume entre 0 y 1 con 1 el máximo volumen actual
        self.mob_hit_snds = []
        for snd in MOB_HIT_SNDS:
            s = pg.mixer.Sound(os.path.join(SND_DIR,snd))
            s.set_volume(0.8)
            self.mob_hit_snds.append(s)
        self.player_hit_snds = []
        for snd in PLAYER_HIT_SNDS:
            s = pg.mixer.Sound(os.path.join(SND_DIR,snd))
            s.set_volume(1)
            self.player_hit_snds.append(s)

    def new(self):
        self.map = TiledMap(os.path.join(MAP_DIR,'tiledGameMap.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        #CREO GRUPOS
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        #self.player = Player(self,5,5) #COORDENADAS DE GRID, NO DE PIXELES
        """for row,lines in enumerate(self.map.data): #ESTE for ES PARA USAR MAPA HECHO A MANO EN ARCHIVO .txt
            for col,tile in enumerate(lines):
                if tile == '1':
                    Wall(self,col,row)
                if tile == 'P':
                    self.player = Player(self,col,row)
                if tile == 'M':
                    Mob(self,col,row,'M')
                if tile == 'N':
                    Mob(self,col,row,'N')"""
        for tile_obj in self.map.tmxdata.objects:
            obj_center = vec(tile_obj.x + tile_obj.width/2, tile_obj.y + tile_obj.height/2)
            if tile_obj.name == 'player':
                self.player = Player(self,obj_center.x,obj_center.y)
            if tile_obj.name == 'wall':
                Obstacle(self,tile_obj.x,tile_obj.y,tile_obj.width,tile_obj.height)
            if tile_obj.name == 'mob':
                Mob(self,obj_center.x,obj_center.y,rd.choice(['N','M']))
            if tile_obj.name in list(ITEM_IMGS.keys()):
                Item(self,obj_center,tile_obj.name)
        #self.player = Player(self,5,5)
        self.draw_debug = False
        self.camera = Camera(self.map.width,self.map.height)
        self.effects_snds['level_start'].play()
    def run(self):
        self.playing = True
        pg.mixer.music.play(loops=-1)
        while self.playing:
            self.dt = self.clock.tick(FPS)/1000
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug #muestra hit rects
                if event.key == pg.K_p:
                    self.paused = not self.paused
                """if event.key == pg.K_LEFT:
                    self.player.move(dx=-1)
                if event.key == pg.K_RIGHT:
                    self.player.move(dx=1)
                if event.key == pg.K_UP:
                    self.player.move(dy=-1)
                if event.key == pg.K_DOWN:
                    self.player.move(dy=1)"""
                    

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)
        #colisión de player y items
        hits = pg.sprite.spritecollide(self.player,self.items,False)
        if hits:
            for h in hits:
                if h.type == 'health' and self.player.health < PLAYER_HEALTH:
                    h.kill()
                    self.player.add_health()
                    self.effects_snds['health_up'].play()
                if h.type == 'shotgun':
                    h.kill()
                    self.player.weapon = 'shotgun'
                    self.effects_snds['shotgun_pickup'].play()
        #colisión de player y mobs
        hits = pg.sprite.spritecollide(self.player,self.mobs,False,collide_hit_rect)
        if hits: #debe cambiarse la pos de player para que no esté todo el tiempo colisionando con mob y pierda toda su health casi inmediatamente
            self.player.pos += vec(MOB_KNOCKBACK,0).rotate(-hits[0].rot) #rot del hit que sea, no importa
            self.player.got_hit()
            for h in hits:
                self.player.health -= MOB_DAMAGE
                h.vel = vec(0,0)
                if self.player.health <= 0:
                    self.playing = False
                if rd.random() < 0.7:
                    rd.choice(self.player_hit_snds).play()
        #colisión de mobs y bullets
        #hits da dict: por cada mob que colisionó con bullet, una lista de dichas bullets
        #cada key es un mob que fue golpeado
        hits = pg.sprite.groupcollide(self.mobs,self.bullets,False,True) #desaparecen?-->False para mobs, True para bullets
        for mob in hits:
            for bullet in hits[mob]:
                mob.health -= bullet.damage
            #h.health -= WEAPONS[self.player.weapon]['damage'] * len(hits[h]) # *cuántas bullets que colisionaron con mob 
            mob.vel = vec(0,0)
    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        #self.screen.fill(BROWN)
        #self.draw_grid()
        self.screen.blit(self.map_img,self.camera.apply_rect(self.map_rect))
        #self.all_sprites.draw(self.screen) #esto cambia al usar cámara
        for sprite in self.all_sprites:
            if isinstance(sprite,Mob):
                sprite.draw_health()
            self.screen.blit(sprite.image,self.camera.apply(sprite))
            if self.draw_debug:
                pg.draw.rect(self.screen,L_BLUE,self.camera.apply_rect(sprite.hit_rect),1)
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen,L_BLUE,self.camera.apply_rect(wall.rect),1)

        draw_player_health(self.screen,10,10,self.player.health/PLAYER_HEALTH)
        self.draw_text('Enemies: {}'.format(len(self.mobs)),self.font,35,YELLOW,WIDTH-100,20)
        #pg.draw.rect(self.screen,WHITE,self.camera.apply(self.player),2) #para ver cómo cambia el rect de la imagen cuando rota
        #pg.draw.rect(self.screen,RED,self.player.hit_rect,2) #para ver el hit_rect fijo
        if self.paused:
            self.screen.blit(self.surf_pause,(0,0))
            self.draw_text("PAUSED",self.font,100,RED,WIDTH/2,HEIGHT/2)
        pg.display.flip()
    """def draw_grid(self):
        for x in range(0,WIDTH,TILESIZE):
            pg.draw.line(self.screen,L_GRAY, (x,0), (x,HEIGHT) )
        for y in range(0,HEIGHT,TILESIZE):
            pg.draw.line(self.screen,L_GRAY, (0,y), (WIDTH,y) )"""
    def draw_text(self,text,font_name,size,color,x,y):
        font = pg.font.Font(font_name,size)
        txt_surf = font.render(text,True,color)
        txt_rect = txt_surf.get_rect()
        txt_rect.center = (x,y)
        self.screen.blit(txt_surf,txt_rect)
    def quit(self):
        pg.quit()
        sys.exit()
    def show_start_screen(self):
        pass
    def show_gameOver_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("GAME OVER",self.font,80,RED,WIDTH/2,HEIGHT/2)
        self.draw_text("Press any key to start again...",self.font,50,WHITE,WIDTH/2,HEIGHT/2+60)
        pg.display.flip()
        self.wait_key()
    def wait_key(self):
        pg.event.wait() #evita que KEYUP de teclas oprimidas antes de gameOver tengan efecto cuando estamos en gameOver
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False


g = Game()
g.show_start_screen()
while True: #while g.running?
    g.new()
    g.run() #se crea bandera self.playing
    g.show_gameOver_screen()


