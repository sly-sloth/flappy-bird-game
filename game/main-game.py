import pygame
import os
import random
pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800
FPS = 60
IMM_GRAVITY = 0.16
GRAVITY = 0.11
JUMP_VEL = -1.0     
H_VEL = 4  


BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

RED_BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "redbird-upflap.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "redbird-midflap.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "redbird-downflap.png")))]

BLUE_BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bluebird-upflap.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bluebird-midflap.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bluebird-downflap.png")))]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
GAME_OVER_IMG = pygame.transform.scale_by(pygame.image.load(os.path.join("imgs", "gameover.png")), factor=1.5)

STAT_FONT = pygame.font.SysFont("showcardgothic", 30)

# region bird
class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]


    def jump(self):
        self.vel = JUMP_VEL
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        if self.tick_count < 2:
            d = self.vel * self.tick_count + 0.5 * IMM_GRAVITY * self.tick_count**2
        else:
            d = self.vel * self.tick_count + 0.5 * GRAVITY * self.tick_count**2

            
        if d >= 16:
            d = 16

        if d < 0:
            d -= 2

        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw_static(self, win):
        self.img = RED_BIRD_IMGS[1]
        
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)   
        win.blit(rotated_image, new_rect.topleft)

    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0


        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)   
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    

# region pipe
class Pipe:
    GAP = 220
    VEL = H_VEL

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP
    
    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True

        return False


# region base
class Base:
    VEL = H_VEL
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):   
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))
        

# region window
def draw_window(win, bird, pipes, base, score):
    win.blit(BG_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render(f"Score: {score}", 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(win)

    bird.draw(win)
    pygame.display.update()

def draw_window_static(win, bird, pipes, base, score):
    win.blit(BG_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render(f"Score: {score}", 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(win)

    bird.draw_static(win)
    win.blit(GAME_OVER_IMG, (110, 369))
    # bird.draw(win)
    pygame.display.update()


# region main
def main():
    pygame.init()
    rerun = True
    while rerun:
        bird = Bird(230, 350)
        base = Base(730)
        pipes = [Pipe(600)]
        win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        clock = pygame.time.Clock()

        score = 0
        run = True
        begin_jumping = False
        
        runF = True
        while run:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    rerun = False
                    runF = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        begin_jumping = True
                        bird.jump()

            if begin_jumping:   
                bird.move()

            add_pipe = False
            rem = []
            for pipe in pipes:
                if pipe.collide(bird):
                    # pass 
                    print("collision detected")
                    run = False
                    break
                
                if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                    rem.append(pipe)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

                pipe.move()

            if add_pipe:
                score += 1
                if score == 20:
                    bird.IMGS = BLUE_BIRD_IMGS
                pipes.append(Pipe(600))

            for r in rem:
                pipes.remove(r)

            if bird.y + bird.img.get_height() >= 730:
                pass

            
            base.move()
            draw_window(win, bird, pipes, base, score)

        while runF:
            draw_window_static(win, bird, pipes, base, score)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    runF = False
                    rerun = False
                elif event.type == pygame.KEYDOWN:
                    runF = False
                    rerun = True
    
    pygame.quit()
    quit() 

main()
