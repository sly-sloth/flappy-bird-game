import neat.nn.feed_forward
import pygame
import os
import random
import neat
import time
pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800
FPS = 120
IMM_GRAVITY = 0.26
GRAVITY = 0.21
JUMP_VEL = -1.8    
H_VEL = 4  


TEST_JUMP_VEL = -10.5
TEST_IMM_GRAVITY = 3.5
TEST_GRAVITY = 3.0
TEST_H_VEL = 5


BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

RED_BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "redbird-upflap.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "redbird-midflap.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "redbird-downflap.png")))]

BLUE_BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bluebird-upflap.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bluebird-midflap.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bluebird-downflap.png")))]

MAIN_IMGS = BIRD_IMGS

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
GAME_OVER_IMG = pygame.transform.scale_by(pygame.image.load(os.path.join("imgs", "gameover.png")), factor=1.5)

STAT_FONT = pygame.font.SysFont("showcardgothic", 30)

# region bird
class Bird:
    IMGS = MAIN_IMGS
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
def draw_window(win, birds, pipes, base, score, len_birds):
    win.blit(BG_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render(f"Score: {score}", 1, (255, 255, 255))
    text_birds = STAT_FONT.render(f"Birds: {len_birds}", 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    win.blit(text_birds, (10, 10))

    base.draw(win)

    for bird in birds:
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
def main(genomes, config):
    # pygame.init()
    # rerun = True
    # while rerun:

    with open("game/hs.txt", "r") as file:
        high_score = int(file.read())

    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)


    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    score = 0
    run = True
    begin_jumping = True  # later will change to False
    
    # runF = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                # rerun = False
                # runF = False
            # elif event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_SPACE:
            #         begin_jumping = True
            #         bird.jump()

        # if begin_jumping:   
        #     bird.move()

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break


        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.05

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()


        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                    
                    # print("collision detected")
                    # run = False
                    # break

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            if score == 10:
                for bird in birds:
                    bird.IMGS = BLUE_BIRD_IMGS

            if score > high_score:
                high_score = score
                with open("game/hs.txt", "w") as f:
                    f.write(f"{high_score}")

            for g in ge:
                g.fitness += 5 
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                # run = False
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        
        base.move()
        draw_window(win, birds, pipes, base, score, len(birds))

        # while runF:
        #     draw_window_static(win, bird, pipes, base, score)
        #     for event in pygame.event.get():
        #         if event.type == pygame.QUIT:
        #             runF = False
        #             rerun = False
        #         elif event.type == pygame.KEYDOWN:
        #             runF = False
        #             rerun = True
    
    # pygame.quit()
    # quit() 



def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
