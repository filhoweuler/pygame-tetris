import pygame
import random
from pygame.locals import *

PIECES = [('1.png', (1, 4)), ('L.png', (2, 3)), ('R.png', (2, 2)), ('S.png', (3, 2)), ('T_2.png', (3, 2))]
SCREEN_WIDTH = 590
SCREEN_HEIGHT = 960
TILE_SIZE = 45

LEFT_LINE = 16
RIGHT_LINE = 420
BOTTOM_LINE = 940
TOP_LINE = 940 - (45 * 20)

NEXT_X = 440
NEXT_Y = 170

drop_speed = TILE_SIZE

def bottom_limit(sprite):
    return sprite.rect[1] + sprite.rect[3]

def on_ground(piece):
    return bottom_limit(piece) >= BOTTOM_LINE

def get_random_piece(rescale=2.51):
    piece_name, tiles = random.choice(PIECES)
    asset_path = f'assets/{piece_name}'
    print(f"Asset: {asset_path}")
    image = pygame.image.load(asset_path).convert_alpha()

    new_size = (tiles[0] * TILE_SIZE, tiles[1] * TILE_SIZE)
    scaled_image = pygame.transform.scale(image, new_size)

    return scaled_image

def fix_sprite_height(sprite):
    if on_ground(sprite):
        sprite.rect[1] = BOTTOM_LINE - sprite.rect[3]
        return sprite

    sprite.rect[1] = BOTTOM_LINE - (( BOTTOM_LINE - sprite.rect[1] ) // TILE_SIZE + 1) * TILE_SIZE
    return sprite


class Piece(pygame.sprite.Sprite):

    def __init__(self, next=False):
        pygame.sprite.Sprite.__init__(self)

        # Used for the next piece
        if next:
            self.image = get_random_piece()
            self.rect = self.image.get_rect()
            self.rect[0], self.rect[1] = (NEXT_X, NEXT_Y)            
        else:
            self.image = get_random_piece()
            self.rect = self.image.get_rect()
            self.rect[0] = LEFT_LINE
            self.rect[1] = TOP_LINE

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect[1] += drop_speed
    
    def undo_update(self):
        self.rect[1] -= drop_speed

    def move_left(self):
        if self.rect[0] > LEFT_LINE:
            self.rect[0] -= TILE_SIZE
    
    def move_right(self):
        # If width + block position are within the border
        if self.rect[0] + self.rect[2] < RIGHT_LINE:
            self.rect[0] += TILE_SIZE

    def move_down(self):
        if self.rect[1] + self.rect[3] < BOTTOM_LINE:
            self.rect[1] += TILE_SIZE

    def rotate(self):
        self.image = pygame.transform.rotate(self.image, -90)
        self.mask = pygame.mask.from_surface(self.image)

    def reset(self):
        self.rect[0] = LEFT_LINE
        self.rect[1] = TOP_LINE
        
pygame.init()
BACKGROUND = pygame.image.load('assets/background.jpg')

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

current_piece = Piece()
current_group = pygame.sprite.GroupSingle()
current_group.add(current_piece)

next_piece = Piece(next=True)
next_group = pygame.sprite.GroupSingle()
next_group.add(next_piece)

ground_pieces = pygame.sprite.Group()

clock = pygame.time.Clock()

while True:
    clock.tick(5)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()

        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                current_group.sprite.move_left()
            if event.key == K_RIGHT:
                current_group.sprite.move_right()
            # if event.key == K_DOWN:
            #     current_group.sprite.move_down()
            if event.key == K_UP:
                current_group.sprite.rotate()
    
    current_group.sprite.update()

    # Check if moving caused any collisions or complete rows and fix
    if (pygame.sprite.spritecollideany(current_group.sprite, ground_pieces, pygame.sprite.collide_mask) or 
        on_ground(current_group.sprite)):
        
        # The current sprite might have "entered" in other sprites
        # current_group.sprite = fix_sprite_height(current_group.sprite)
        if not on_ground(current_group.sprite):
            current_group.sprite.undo_update()
        
        ground_pieces.add(current_group.sprite)
        current_group.add(next_group.sprite)
        current_group.sprite.reset()
        
        next_group.add(Piece(next=True))

    # Clear the screen with background
    screen.blit(BACKGROUND, (0, 0))

    # Update the pieces sprite on screen
    current_group.draw(screen)
    next_group.draw(screen)

    ground_pieces.draw(screen)

    pygame.display.update()