import pathlib
maindir = pathlib.Path(__file__).parent.resolve()
imgdir = maindir.joinpath('gfx')

import pygame as pg
from pygame.locals import *
from pygame.math import Vector2 as vec2


class SpriteSheet(pg.sprite.Sprite):
    def __init__(self, img, pos, size, col, row):
        super().__init__()
        self.sheet = img
        self.w, self.h = size
        self.all_image = self.iterate(row, col)
        
        self.down_anims = self.all_image[:3]
        self.left_anims = self.all_image[3:6]
        self.right_anims = self.all_image[6:9]
        self.up_anims = self.all_image[9:]

        self.index = 1  # the middle frame
        self.current_animations = self.down_anims

        #the two required attr!
        self.image = self.sheet.subsurface(self.current_animations[self.index])
        self.rect = self.image.get_rect(topleft=pos)

        #for movement
        self.direction = vec2()
        self.speed = 250.
    def iterate(self, row, col) -> list[pg.Rect]:
        all_img = []
        for i in range(row):
            for j in range(col):
                all_img.append(pg.Rect(
                    j*self.w,i*self.h,self.w,self.h
                ))
        return all_img
    def update(self, dt):
        #move the player
        self.rect.center += self.direction*self.speed*dt
        #produce animation
        self.animate()
        #update corresponding image due to the animation
        self.image = self.sheet.subsurface(self.current_animations[self.index])
        self.rect = self.image.get_rect(topleft=(self.rect.left,self.rect.top))
    def animate(self):
        if self.direction.x != 0 or self.direction.y != 0:
            if self.direction.x > 0:
                self.current_animations = self.right_anims
            elif self.direction.x < 0:
                self.current_animations = self.left_anims
            elif self.direction.y > 0:
                self.current_animations = self.down_anims
            elif self.direction.y < 0:
                self.current_animations = self.up_anims
            self.index += 1
            if self.index > len(self.current_animations)-1:  ##last-frame reached!
                self.index = 0
        else:  ##standing still!
            self.index = 1

pg.init()

dims = vec2(480,320)
flags = SRCALPHA|DOUBLEBUF
bpp = 8  ##bit-depth per pixel
win = pg.display.set_mode(dims,flags,bpp)
clk = pg.time.Clock()

##load image files
test_img = pg.image.load(imgdir.joinpath('vx_chara01_b.png')).convert_alpha(win)

##each sub-sheet width and height (in this case 4 columns and 2 rows)
sub_w = test_img.get_width()//4
sub_h = test_img.get_height()//2

stripped_rects = []  ##sub-sheet rects
for i in range(2):
    for j in range(4):
        stripped_rects.append(pg.Rect(j*sub_w,i*sub_h,sub_w,sub_h))
stripped_images = []  ##sub-sheet actual images
for rect in stripped_rects:
    stripped_image = test_img.subsurface(rect)
    stripped_images.append(stripped_image)

##get each sprite(single character) width and height
spr_w = test_img.get_width()//12
spr_h = test_img.get_height()//8
##instantiate our objects
ss = SpriteSheet(stripped_images[2], (0,0), (spr_w,spr_h), 3, 4)
sprite_manager = pg.sprite.GroupSingle(ss)

PLAYER_TIMER = pg.event.custom_type()
pg.time.set_timer(PLAYER_TIMER,120)

##main game loop
done = 0.
while not done:
    dt = clk.tick(24)/1000
    pg.display.set_caption(f'fps: {clk.get_fps()}')
    ##main event loop
    for e in pg.event.get():
        if e.type in (QUIT,WINDOWCLOSE):
            done = 1.
        elif e.type == PLAYER_TIMER:
            sprite_manager.update(dt)
        elif e.type == KEYDOWN:
            if e.key == K_DOWN:
                sprite_manager.sprite.direction.y = 1
            elif e.key == K_UP:
                sprite_manager.sprite.direction.y =-1
            elif e.key == K_RIGHT:
                sprite_manager.sprite.direction.x = 1
            elif e.key == K_LEFT:
                sprite_manager.sprite.direction.x =-1
        elif e.type == KEYUP:
            if e.key == K_DOWN:
                sprite_manager.sprite.direction.y = 0
            elif e.key == K_UP:
                sprite_manager.sprite.direction.y = 0
            elif e.key == K_RIGHT:
                sprite_manager.sprite.direction.x = 0
            elif e.key == K_LEFT:
                sprite_manager.sprite.direction.x = 0
    ##paint the screen with plain color
    win.fill('white')
    #win.blit(stripped_images[0],(0,0))
    sprite_manager.draw(win)
    ##update the entire display(what we've drawn onto)
    pg.display.flip()
pg.quit()
