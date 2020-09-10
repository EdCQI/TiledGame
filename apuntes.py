######################################
#----------------TILED---------------
######################################
import pytmx #se debe instalar
tmx = pytmx.pygame_load(file,pixelalpha=True)

tmx.width / .height #tiles a lo ancho/alto
tmx.tilewidth / .tileheight #pixeles a lo ancho/alto de cada tile
tmx.visible_layers
tmx.objects ... .name .x .y .width .height #nombre de objetos asignados en Tiled, etc

#pone los tiles editados en Tiled:
ti = tmx.get_tile_image_by_gid #global identifier (gid) mapea número en tmx a imagen correspondiente
for layer in self.tmxdata.visible_layers:
    if isinstance(layer,pytmx.TiledTileLayer):
        for x,y,gid in layer: #x,y son coordenadas en pixeles
            tile = ti(gid)
            if tile:
                surf.blit(tile,(x*self.tmxdata.tilewidth,y*self.tmxdata.tileheight)) 

#pone los objetos creados con class cuya imagen se carga aparte (en decir,estas ims no se editan en Tiled)
for obj in tmx.objects:
    if obj.name == 'player':
        self.player = Player(self,obj_center.x,obj_center.y)
    if obj.name == 'wall':
        Obstacle(self,tile_obj.x,tile_obj.y,tile_obj.width,tile_obj.height)
    if obj.name == 'mob':
        Mob(self,obj_center.x,obj_center.y,rd.choice(['N','M']))
    if obj.name in list(ITEM_IMGS.keys()):
        Item(self,obj_center,tile_obj.name)

######################################
#--------
######################################