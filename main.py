import pygame
from sys import exit
import random

pygame.init()
clock = pygame.time.Clock()

#Pygame window
window_height = 720
window_width = 551
window = pygame.display.set_mode((window_width, window_height))

#load images
bird_images = [pygame.image.load("assets/bird_down.png"), pygame.image.load("assets/bird_mid.png"), pygame.image.load("assets/bird_up.png")]
skyline_image = pygame.image.load("assets/background.png")
gameover_image = pygame.image.load("assets/game_over.png")
top_pipe_image = pygame.image.load("assets/pipe_top.png")
bottom_pipe_image = pygame.image.load("assets/pipe_bottom.png")
start_image = pygame.image.load("assets/start.png")
ground_image = pygame.image.load("assets/ground.png")

# Game variables
gameSpeed = 1
bird_start_position = (100, 250)
score = 0


class Bird (pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = bird_images[0]
        self.rect = self.image.get_rect()
        self.rect.center = bird_start_position
        self.image_index = 0
        self.velocity = 0
        self.can_flap = True
        self.alive = True

    def update(self, user_flap_input):
        if self.alive:
            self.image_index += 1
        if self.image_index >= 30:
            self.image_index = 0
        self.image = bird_images[self.image_index // 10] # Bird changes image every 10 units of time

        # Gravity and flap
        self.velocity += 0.5
        if self.velocity > 7:
            self.velocity = 7
        if self.rect.y < 500:
            self.rect.y += self.velocity


        if self.velocity == 0:
            self.can_flap = True


        # Rotate bird
        self.image = pygame.transform.rotate(self.image, self.velocity * -7)

        # User flap
        if user_flap_input[pygame.K_SPACE] and self.can_flap and self.rect.y > 0 and self.alive:
            self.can_flap = False
            self.velocity = -7

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, image, pipe_type):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.passed_pipe = False
        self.pipe_type = pipe_type

    def update(self):
        # Move pipe
        self.rect.x -= gameSpeed
        if self.rect.x < - window_width:
            self.kill()
        # Score
        global score
        if self.pipe_type == 'bottom':
            if bird_start_position[0] > self.rect.topright[0] and not self.passed_pipe:
                self.passed_pipe = True
                score += 1



class Ground(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = ground_image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def update(self):
        # Move ground
        self.rect.x -= gameSpeed
        if self.rect.x <= -window_width:
            self.kill()




def quit_game():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

# Game method:
def flappy_bird():
    global score
    global gameSpeed

    # Create bird
    bird = pygame.sprite.GroupSingle()
    bird.add(Bird())

    # Create pipes
    pipe_timer = 0
    pipes = pygame.sprite.Group()

    # Create ground
    x_ground_postion, y_ground_postion = 0, 520
    ground = pygame.sprite.Group()
    ground.add(Ground(x_ground_postion, y_ground_postion))

    run = True
    while run:
        quit_game()  # Ends program when user closes out window

        # Reset frame to black
        window.fill((0, 0, 0))

        # User input
        user_input = pygame.key.get_pressed()

        # Spawn ground on right side
        if(len(ground)) < 2:
            ground.add(Ground(window_width, y_ground_postion))

        # Draw background
        window.blit(skyline_image, (0, 0))

        # Draw and update pipes, bird, ground
        pipes.draw(window)
        ground.draw(window)
        bird.draw(window)

        if bird.sprite.alive:
            pipes.update()
            ground.update()
        bird.update(user_input)

        # Detect collision with pipes
        ground_collision = pygame.sprite.spritecollide(bird.sprites()[0], ground, False)
        pipe_collision = pygame.sprite.spritecollide(bird.sprites()[0], pipes, False)
        if ground_collision or pipe_collision:
            bird.sprite.alive = False
            if ground_collision:
                window.blit(gameover_image, (window_width//2 - gameover_image.get_width()//2, window_height//2 - gameover_image.get_height()//2))
                if user_input[pygame.K_r]:
                    score = 0
                    gameSpeed = 1
                    break
        # Display score
        score_text_font = pygame.font.SysFont("Segoe", 26)
        score_text = score_text_font.render("Score: " + str(score), True, (255, 255, 255))
        window.blit(score_text, (20, 20))

        # Spawn pipes
        if pipe_timer <= 0 and bird.sprite.alive:
            x_top, x_bottom = 550, 550
            y_top = random.randint (-600, -480) # Negative because pipe is created above the screen. Y increases as you move down
            y_bottom = y_top + random.randint (90, 130) + bottom_pipe_image.get_height()
            pipes.add(Pipe(x_top, y_top, top_pipe_image, 'top'))
            pipes.add(Pipe(x_bottom, y_bottom, bottom_pipe_image, 'bottom'))
            pipe_timer = random.randint (180, 250)
        pipe_timer -= 1

        clock.tick(60)
        pygame.display.update()




# Menu
def menu():

    while True:
        quit_game()  # Ends program when user closes out window

        # Draw menu
        window.fill((0, 0, 0))
        window.blit(ground_image, (0, 520))
        window.blit(skyline_image, (0, 0))
        window.blit(bird_images[0], (100, 250))
        window.blit(start_image, (window_width//2 - start_image.get_width()//2, window_height//2 - start_image.get_height()//2))

        # Start game
        user_input = pygame.key.get_pressed()
        if user_input[pygame.K_SPACE]:
            flappy_bird()
        pygame.display.update()

menu()

