import pygame
import json


# Player: 2 blocks high
# cannot jump 1 block higher


pygame.init()
width = 800
height = 800
game_over = 0
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('New Project 1')
clock = pygame.time.Clock()
fps = 60


bg = pygame.image.load('images/bg.png')
level = 1
max_level = 4
def reset_level():
    player.rect.x = 40
    player.rect.y = height - 60 - 40
    door_group.empty()
    lava_group.empty()
    key_group.empty()
    with open(f'levels/level{level}.json', 'r') as file:
        world_data = json.load(file)
    world = World(world_data)
    return world
tile_size = 40


class Player:
    def __init__(self):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        self.direction = 0
        self.key = False
        for num in range(1,4):
            img_right = pygame.image.load(f'images/player/player{num}.png')
            img_right = pygame.transform.scale(img_right, (35, 60))
            img_left = pygame.transform.flip(img_right, True, False)
            # Adding to list
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.image  = self.images_right[self.index]
        self.rect = self.image.get_rect(x=40, y=height - 60 - 40)
        self.gravity = 0
        self.inair = False
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.dead_image = pygame.image.load('images/ghost.png')
        self.dead_image = pygame.transform.scale(self.dead_image, (50,60))

    def update(self):
        global game_over
        screen.blit(self.image, self.rect)
        x = 0
        y = 0
        walk_speed = 10

        if game_over == 0:
            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT]:
                x -= 5
                self.counter += 1
                if self.rect.left > 0:
                    self.direction = -1
                else:
                    self.direction = 1
            if key[pygame.K_RIGHT]:
                x += 5
                self.counter += 1
                if self.rect.right < width:
                    self.direction = 1
                else:
                    self.direction = -1

            # Up and down
            if key[pygame.K_SPACE] and self.inair == False:
                self.gravity = -15
                self.inair = True

            if self.counter > walk_speed:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                else:
                    self.image = self.images_left[self.index]
            self.gravity += 1
            if self.gravity > 10:
                self.gravity = 10
            y += self.gravity

            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + x, self.rect.y, self.width, self.height):
                    x = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + y, self.width, self.height):
                    if self.gravity < 0:
                        y = tile[1].bottom - self.rect.top
                        self.gravity = 0
                    elif self.gravity >= 0:
                        y = tile[1].top - self.rect.bottom
                        self.gravity = 0
                        self.inair = False
                if pygame.sprite.spritecollide(self, lava_group, False):
                    game_over = -1
                if pygame.sprite.spritecollide(self, key_group, True):
                    self.key = True
                if pygame.sprite.spritecollide(self, door_group, False) and self.key:
                    game_over = 1
                    self.key = False

        elif game_over == -1:
            self.image = self.dead_image
            if self.rect.y > 0:
                self.rect.y -= 3

        self.rect.x += x
        self.rect.y += y

        if self.rect.bottom > height:
            self.rect.bottom = height
            self.inair = False
        if self.rect.right > width:
            self.rect.right = width
        if self.rect.left < 0:
            self.rect.left = 0

class World:
    def __init__(self, data):
        dirt_img = pygame.image.load('images/map/tile10.png')
        grass_img = pygame.image.load('images/map/tile7.png')
        self.tile_list = []
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1 or tile == 2:
                    images = {1 : dirt_img, 2 : grass_img}
                    img = pygame.transform.scale(images[tile], (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                elif tile == 3:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                elif tile == 5:
                    door = Door(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    door_group.add(door)
                elif tile == 4:
                    key = Key(col_count * tile_size + (tile_size//2), row_count * tile_size + (tile_size // 2))
                    key_group.add(key)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load('images/map/tile6.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

lava_group = pygame.sprite.Group()

class Door(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load('images/map/exit.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

door_group = pygame.sprite.Group()

class Key(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load('images/map/key3.png')
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

key_group = pygame.sprite.Group()

class Button:
    def __init__(self,x,y,image):
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect(center=(x,y))

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        screen.blit(self.image, self.rect)
        return action

player = Player()
world = reset_level()
restart_button = Button(width//2, height//2, 'images/buttons/restart.png')
start_button = Button(width//2-150, height//2, 'images/buttons/start.png')
exit_button = Button(width//2+150, height//2, 'images/buttons/exit.png')
run = True
main_menu = True

while run:
    clock.tick(fps)
    screen.blit(bg, (0,0))
    if main_menu:
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else:
        player.update()
        world.draw()
        lava_group.draw(screen)
        lava_group.update()
        door_group.draw(screen)
        door_group.update()
        key_group.draw(screen)
        key_group.update()
        if game_over == -1:
            if restart_button.draw():
                player = Player()
                level = 1
                world = reset_level()
                game_over = 0
        if game_over == 1:
            game_over = 0
            if level < max_level:
                level += 1
                world = reset_level()
            else:
                print("Win")
                main_menu = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()
pygame.quit()