#https://www.youtube.com/watch?v=3zV2ewk-IGU -> tutorial de scrolling camera
import pygame as pg
import pytmx #debe instalarse
from conf import *


class TiledMap:
    def __init__(self,filename):
        tm = pytmx.load_pygame(filename,pixelalpha=True) #pixelalpha para adquirir la transparencia del mapa
        self.width = tm.width * tm.tilewidth #cuántos tiles a lo ancho * tile pixel width
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm #para tener referencia a toda la info de tm
    def render(self,surf): 
        """takes pygame surface and draw tiles from map onto it"""
        ti = self.tmxdata.get_tile_image_by_gid #gid=global identifier-->permite mapear número en archivo tmx a imagen correspondiente
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer,pytmx.TiledTileLayer):
                for x,y,gid in layer: #x,y son coordenadas en pixeles
                    tile = ti(gid)
                    if tile:
                        surf.blit(tile,(x*self.tmxdata.tilewidth,y*self.tmxdata.tileheight)) #coordenadas de mosaicos, NO pixeles
    def make_map(self):
        temp_surface = pg.Surface((self.width,self.height))
        self.render(temp_surface)
        return temp_surface


"""class Map: #mapa en txt
    def __init__(self,filename):
        #self.data = []
        #for line in fmap: #24 renglones-->24 elementos de la lista (los lee como string)
        #    self.data.append(line)
        with open(filename,'rt') as fmap:
            self.data = fmap.readlines() #readlines extrae renglones como elementos de lista; read extrae todo en una sola string
        self.data = [x[:-1] for x in self.data] #quito los '\n' de cada elemento de la lista obtenida
        self.tilewidth = len(self.data[0]) #tiles a lo ancho
        self.tileheight = len(self.data) #tiles a lo alto
        self.width = self.tilewidth * TILESIZE #en pixeles
        self.height = self.tileheight * TILESIZE #en pixeles"""

class Camera:
    def __init__(self,w,h):
        self.camera = pg.Rect(0,0,w,h)
        self.width = w
        self.height = h
    def apply(self,entity): #entity is sprite
        return entity.rect.move(self.camera.topleft)
        #move devuelve nuevo rect que estará recorrido 'tanto', siendo 'tanto'=self.camera.toplet
    def apply_rect(self,rect): #en vez de tomar un sprite, toma un rect--> se usa para aplicar la cam al mapa
        return rect.move(self.camera.topleft)
    def update(self, target): #target será player
        x = -target.rect.centerx + int(WIDTH/2) #para mantener al jug en centro
        y = -target.rect.centery + int(HEIGHT/2)
        #limitar scrolling al tamaño del mapa
        x = min(0,x) #cuando x positiva (offset), la cámara muestra los límites izquierdos del mapa
        y = min(0,y) #top
        x = max(-(self.width-WIDTH),x) #derecha
        y = max(-(self.height-HEIGHT),y) #bottom
        self.camera = pg.Rect(x,y,self.width,self.height)
