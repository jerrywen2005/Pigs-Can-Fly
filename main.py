import pygame
from sys import exit
import random

pygame.init()
clock = pygame.time.Clock()

class Character (pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = character_images[0]

        # Mask for better accuracy collision tracking, only gets visible pixels
        self.mask = pygame.mask.from_surface(self.image)
        outline = self.mask.outline()
        if outline:
            min_x = min([point[0] for point in outline])
            max_x = max([point[0] for point in outline])
            min_y = min([point[1] for point in outline])
            max_y = max([point[1] for point in outline])
            self.mask_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)


        # Makes sure rect is only around the character itself and not invisible png pixels
        self.rect = self.mask_rect

        self.rect.center = character_start_position
        self.image_index = 0
        self.velocity = 0
        self.can_flap = True
        self.alive = True

    def update(self, user_flap_input):
        if self.alive:
            self.image_index += 1
        if self.image_index >= 30:
            self.image_index = 0
        self.image = character_images[self.image_index // 10] # Bird changes image every 10 units of time

        # Gravity and flap
        self.velocity += 0.5 # Gravity acceleration rate
        if self.velocity > 7:
            self.velocity = 7 # Max fall speed
        if self.rect.y < 500: # Make sure bird above ground
            self.rect.y += self.velocity
        if self.velocity == 0: # Can only flap after bird reaches highest point from previous flap
            self.can_flap = True


        # Rotate bird
        self.image = pygame.transform.rotate(self.image, self.velocity * -7)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

        # User flap
        if user_flap_input[pygame.K_SPACE] and self.can_flap and self.rect.y > 0 and self.alive:
            self.can_flap = False
            self.velocity = -7



class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, image, pipe_type):
        pygame.sprite.Sprite.__init__(self)
        self.image = image



        # Mask for better accuracy collision tracking
        self.mask = pygame.mask.from_surface(self.image)

        outline = self.mask.outline()
        if outline:
            min_x = min([point[0] for point in outline])
            max_x = max([point[0] for point in outline])
            min_y = min([point[1] for point in outline])
            max_y = max([point[1] for point in outline])
            self.mask_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)


        # Makes sure rect is only around the obstacle itself and not invisible png pixels
        self.rect = self.mask_rect.copy()

        self.rect.x = x
        self.rect.y = y


        self.passed_pipe = False
        self.pipe_type = pipe_type

    def update(self):
        # Move pipe
        self.rect.x -= game_speed
        if self.rect.x < - window_width:
            self.kill()
        # Score
        global score

        if self.pipe_type == 'bottom': # Updating score based on if bird has passed the bottom pipe
            if character_start_position[0] > self.rect.right and not self.passed_pipe:
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
        self.rect.x -= game_speed
        if self.rect.x <= -window_width:
            self.kill()

def add_wings(character_image, wing_image, position = (0,0)):
    combined_image = character_image.copy() # Blitting alters the original copy so a new copy is needed
    combined_image.blit(wing_image, position)
    return combined_image


def quit_game(events):
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

def check_mouse_click(events):
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Check for left click
            return True
        return False

# Game method:
def run_game(character_type, difficulty):
    global game_state
    global game_character
    global game_difficulty
    global score
    global game_speed
    global character_images
    global ground_image
    global background_image
    while True:
        events = pygame.event.get()
        quit_game(events)  # Ends program when user closes out window, essential for processing user inputs.
        window.fill((0, 0, 0))
        if character_type == 'bird': # Determine game mechanics based on the two parameters
            ground_image =  ground_bird_image
            character_images = bird_images
            background_image = background_bird_image
        elif character_type == 'pig':
            if difficulty == 'easy':
                ground_image = ground_pig_easy_image
                background_image = background_pig_easy_image
            elif difficulty == 'medium':
                ground_image = ground_pig_medium_image
                background_image = background_pig_medium_image
            elif difficulty == 'hard':
                ground_image = ground_pig_hard_image
                background_image = background_pig_hard_image
            character_images = pig_images

        # Draw start screen
        window.blit(background_image, (0, 0))
        window.blit(ground_image, (0, 520))
        window.blit(character_images[0], (100, 250))
        window.blit(start_image, (
        window_width // 2 - start_image.get_width() // 2, window_height // 2 - start_image.get_height() // 2))
        pygame.display.update()

        user_input = pygame.key.get_pressed()

        if user_input[pygame.K_SPACE]:
            # Create bird
            character = pygame.sprite.GroupSingle()
            character.add(Character())

            # Create pipes
            pipe_timer = 0
            pipes = pygame.sprite.Group()

            # Create ground
            x_ground_position, y_ground_position = 0, 520
            ground = pygame.sprite.Group()
            ground.add(Ground(x_ground_position, y_ground_position))


            # Start game
            while True:
                events = pygame.event.get()
                quit_game(events)  # Ends program when user closes out window, essential for processing user inputs.

                # Reset frame to black
                window.fill((0, 0, 0))

                # User input
                user_input = pygame.key.get_pressed()  # Redefined inside loop to constantly recheck for user input

                # Spawn ground on right side
                if (len(ground)) < 2:
                    ground.add(Ground(window_width, y_ground_position))

                # Draw background
                window.blit(background_image, (0, 0))

                # Draw and update pipes, bird, ground
                pipes.draw(window)
                ground.draw(window)
                character.draw(window)

                if character.sprite.alive:
                    pipes.update()
                    ground.update()
                character.update(user_input)

                # Detect collision with pipes
                ground_collision = pygame.sprite.spritecollide(character.sprites()[0], ground, False, pygame.sprite.collide_mask)
                pipe_collision = pygame.sprite.spritecollide(character.sprites()[0], pipes, False, pygame.sprite.collide_mask)
                if ground_collision or pipe_collision:
                    character.sprite.alive = False
                    if ground_collision:
                        window.blit(gameover_image, (window_width // 2 - gameover_image.get_width() // 2,
                                                     window_height // 2 - gameover_image.get_height() // 2))
                        if user_input[pygame.K_m]:
                            score = 0
                            game_speed = 1
                            game_state = "menu"
                            return

                        elif user_input[pygame.K_r]:
                            score = 0
                            game_speed = 1
                            game_character = character_type
                            game_difficulty = difficulty
                            game_state = "run_game"
                            return

                # Display score
                score_text_font = pygame.font.SysFont("Segoe", 26)
                score_text = score_text_font.render("Score: " + str(score), True, (255, 255, 255))
                window.blit(score_text, (20, 20))

                # Determine Obstacle type
                top_obstacle_image = top_pipe_image
                bottom_obstacle_image = bottom_pipe_image

                # For starting position
                x_offset = 0
                y_offset = 0

                difficulty_offset = 0


                if character_type == 'pig':
                    y_offset = 450
                    x_offset = -60
                    if difficulty == 'easy':
                        top_obstacle_image = tree_down_images[random.randint(0, len(tree_down_images) - 1)]
                        bottom_obstacle_image = tree_up_images[random.randint(0, len(tree_up_images) - 1)]

                    if difficulty == 'medium':
                        top_obstacle_image = tower_down_images[random.randint(0, len(tower_down_images) - 1)]
                        bottom_obstacle_image = tower_up_images[random.randint(0, len(tower_up_images) - 1)]

                    if difficulty == 'hard':
                        top_obstacle_image = weapon_down_images[random.randint(0, len(weapon_down_images) - 1)]
                        bottom_obstacle_image = weapon_up_images[random.randint(0, len(weapon_up_images) - 1)]

                if character_type == 'custom':
                    top_obstacle_image = all_top_obstacles[random.randint(0, len(all_top_obstacles) - 1)]
                    bottom_obstacle_image = all_bottom_obstacles[random.randint(0, len(all_bottom_obstacles) - 1)]

                # Spawn obstacle
                if pipe_timer <= 0 and character.sprite.alive:
                    x_top, x_bottom = 550 + x_offset, 550 + x_offset
                    y_top = y_offset + random.randint(-600, -480)  # Negative because pipe is created above the screen. Y increases as you move down
                    y_bottom = y_top + random.randint(100, 150) + bottom_obstacle_image.get_height() - difficulty_offset
                    pipes.add(Pipe(x_top, y_top, top_obstacle_image, 'top'))
                    pipes.add(Pipe(x_bottom, y_bottom, bottom_obstacle_image, 'bottom'))
                    pipe_timer = random.randint(180, 250)
                pipe_timer -= 1

                clock.tick(60)
                pygame.display.update()


# Menu
def menu():

    global game_character
    global game_difficulty
    global game_state
    global character_images


    while True:
        # Get all events in this loop iteration
        events = pygame.event.get()

        quit_game(events)  # Ends program when user closes out window, essential for processing user inputs.

        mouse_position = pygame.mouse.get_pos()
        mouse_click = check_mouse_click(events)

        font_menu = pygame.font.SysFont("Segoe", 40)

        # Draw menu
        window.fill((0, 0, 0))
        window.blit(ground_image, (0, 520))
        window.blit(background_image, (0, 0))
        window.blit(character_images[1], character_start_position)

        # Create menu options
        bird_option = font_menu.render("1. Flappy Bird Mode", True, (255, 255, 255))
        pig_option = font_menu.render("2. Pigs Can Fly Mode", True, (255, 255, 255))
        custom_option = font_menu.render("3. Custom Character Mode", True, (255, 255, 255))

        window.blit(bird_option, (window_width // 2 - bird_option.get_width() // 2, 300))
        window.blit(pig_option, (window_width // 2 - pig_option.get_width() // 2, 350))
        window.blit(custom_option, (window_width // 2 - custom_option.get_width() // 2, 400))


        pygame.display.update()

        # Check for mouse clicks on menu options
        if bird_option.get_rect(topleft=(window_width // 2 - bird_option.get_width() // 2, 300)).collidepoint(mouse_position):
            if mouse_click:  # Left mouse button click
                game_character = 'bird'
                game_state = 'run_game'
                return

        elif pig_option.get_rect(topleft=(window_width // 2 - pig_option.get_width() // 2, 350)).collidepoint(mouse_position):
            if mouse_click:  # Left mouse button click
                game_character = 'pig'
                game_state = 'run_game'

                select_difficulty()
                return


        elif custom_option.get_rect(topleft=(window_width // 2 - custom_option.get_width() // 2, 400)).collidepoint(mouse_position):
            if mouse_click:  # Left mouse button click
                print("this mode has not been made yet")


# Difficulty selection screen
def select_difficulty():
    global game_difficulty
    global game_state
    while True:

        events = pygame.event.get()
        quit_game(events)

        mouse_pos = pygame.mouse.get_pos()
        mouse_click1 = check_mouse_click(events)

        font_menu = pygame.font.SysFont("Segoe", 40)

        # Reset frame to black
        window.fill((0, 0, 0))

        # Draw pig menu
        easy_option = font_menu.render("Easy", True, (255, 255, 255))
        normal_option = font_menu.render("Normal", True, (255, 255, 255))
        hard_option = font_menu.render("Hard", True, (255, 255, 255))

        # Blit difficulty options
        window.blit(easy_option, (window_width // 2 - easy_option.get_width() // 2, 300))
        window.blit(normal_option, (window_width // 2 - normal_option.get_width() // 2, 350))
        window.blit(hard_option, (window_width // 2 - hard_option.get_width() // 2, 400))

        pygame.display.update()

        # Check for mouse clicks on difficulty options
        if easy_option.get_rect(topleft=(window_width // 2 - easy_option.get_width() // 2, 300)).collidepoint(mouse_pos):
            if mouse_click1:  # Left mouse button click
                game_difficulty = 'easy'
                return

        if normal_option.get_rect(topleft=(window_width // 2 - normal_option.get_width() // 2, 350)).collidepoint(mouse_pos):
            if mouse_click1:  # Left mouse button click
                game_difficulty = 'medium'
                return

        if hard_option.get_rect(topleft=(window_width // 2 - hard_option.get_width() // 2, 400)).collidepoint(mouse_pos):
            if mouse_click1:  # Left mouse button click
                game_difficulty = 'hard'
                return

# Game-loop variable
game_state = "menu"
game_character = "pig"
game_difficulty = "easy"

# Pygame window
window_height = 720
window_width = 551
window = pygame.display.set_mode((window_width, window_height))

#load bird images
bird_images = [pygame.image.load("assets/bird_down.png"), pygame.image.load("assets/bird_mid.png"), pygame.image.load("assets/bird_up.png")]
background_bird_image = pygame.image.load("assets/background.png")
gameover_image = pygame.image.load("assets/game_over.png")
top_pipe_image = pygame.image.load("assets/pipe_top.png")
bottom_pipe_image = pygame.image.load("assets/pipe_bottom.png")
start_image = pygame.image.load("assets/start.png")
ground_bird_image = pygame.image.load("assets/ground.png")

#load pig images
pig_image = pygame.image.load("assets/pig.png")
background_pig_easy_image = pygame.image.load("assets/background_pig_easy.png")
background_pig_medium_image = pygame.image.load("assets/background_pig_medium.png")
background_pig_hard_image = pygame.image.load("assets/background_pig_hard.png")
branch_up_image = pygame.image.load("assets/branch_up.png")
branch_down_image = pygame.image.load("assets/branch_down.png")
ground_pig_easy_image = pygame.image.load("assets/ground_pig_easy.png")
ground_pig_medium_image = pygame.image.load("assets/ground_pig_medium.png")
ground_pig_hard_image = pygame.image.load("assets/ground_pig_hard.png")
pig_image = pygame.image.load("assets/pig.png")
tower1_down_image = pygame.image.load("assets/tower1_down.png")
tower1_up_image = pygame.image.load("assets/tower1_up.png")
tower2_down_image = pygame.image.load("assets/tower2_down.png")
tower2_up_image = pygame.image.load("assets/tower2_up.png")
tower3_down_image = pygame.image.load("assets/tower3_down.png")
tower3_up_image = pygame.image.load("assets/tower3_up.png")
tower4_down_image = pygame.image.load("assets/tower4_down.png")
tower4_up_image = pygame.image.load("assets/tower4_up.png")
tower5_down_image = pygame.image.load("assets/tower5_down.png")
tower5_up_image = pygame.image.load("assets/tower5_up.png")
tower6_down_image = pygame.image.load("assets/tower6_down.png")
tower6_up_image = pygame.image.load("assets/tower6_up.png")
tower7_down_image = pygame.image.load("assets/tower7_down.png")
tower7_up_image = pygame.image.load("assets/tower7_up.png")
tower8_down_image = pygame.image.load("assets/tower8_down.png")
tower8_up_image = pygame.image.load("assets/tower8_up.png")
tower9_down_image = pygame.image.load("assets/tower9_down.png")
tower9_up_image = pygame.image.load("assets/tower9_up.png")
tower10_down_image = pygame.image.load("assets/tower10_down.png")
tower10_up_image = pygame.image.load("assets/tower10_up.png")
tree_down_image = pygame.image.load("assets/tree_down.png")
tree_up_image = pygame.image.load("assets/tree_up.png")
weapon1_down_image = pygame.image.load("assets/weapon1_down.png")
weapon1_up_image = pygame.image.load("assets/weapon1_up.png")
weapon2_down_image = pygame.image.load("assets/weapon2_down.png")
weapon2_up_image = pygame.image.load("assets/weapon2_up.png")
weapon3_down_image = pygame.image.load("assets/weapon3_down.png")
weapon3_up_image = pygame.image.load("assets/weapon3_up.png")
weapon4_down_image = pygame.image.load("assets/weapon4_down.png")
weapon4_up_image = pygame.image.load("assets/weapon4_up.png")
weapon5_down_image = pygame.image.load("assets/weapon5_down.png")
weapon5_up_image = pygame.image.load("assets/weapon5_up.png")
weapon6_down_image = pygame.image.load("assets/weapon6_down.png")
weapon6_up_image = pygame.image.load("assets/weapon6_up.png")
weapon7_down_image = pygame.image.load("assets/weapon7_down.png")
weapon7_up_image = pygame.image.load("assets/weapon7_up.png")
weapon8_down_image = pygame.image.load("assets/weapon8_down.png")
weapon8_up_image = pygame.image.load("assets/weapon8_up.png")
weapon9_down_image = pygame.image.load("assets/weapon9_down.png")
weapon9_up_image = pygame.image.load("assets/weapon9_up.png")
weapon10_down_image = pygame.image.load("assets/weapon10_down.png")
weapon10_up_image = pygame.image.load("assets/weapon10_up.png")
wing_down_image = pygame.image.load("assets/wing_down.png")
wing_up_image = pygame.image.load("assets/wing_up.png")
wing_middle_image = pygame.image.load("assets/wing_medium.png")

# Group obstacles
tree_up_images = [tree_up_image, branch_up_image]
tree_down_images = [tree_down_image, branch_down_image]
tower_up_images = [tower1_up_image, tower2_up_image, tower3_up_image, tower4_up_image, tower5_up_image, tower6_up_image, tower7_up_image, tower8_up_image, tower9_up_image, tower10_up_image]
tower_down_images = [tower1_down_image, tower2_down_image, tower3_down_image, tower4_down_image, tower5_down_image, tower6_down_image, tower7_down_image, tower8_down_image, tower9_down_image, tower10_down_image]
weapon_up_images = [weapon1_up_image, weapon2_up_image, weapon3_up_image, weapon4_up_image, weapon5_up_image, weapon6_up_image, weapon7_up_image, weapon8_up_image, weapon9_up_image, weapon10_up_image]
weapon_down_images = [weapon1_down_image, weapon2_down_image, weapon3_down_image, weapon4_down_image, weapon5_down_image, weapon6_down_image, weapon7_down_image, weapon8_down_image, weapon9_down_image, weapon10_down_image]
all_bottom_obstacles = [top_pipe_image]+ tree_up_images+ tower_up_images + weapon_up_images
all_top_obstacles = [bottom_pipe_image] + tree_down_images + tower_down_images + weapon_down_images

# Scale variables
pig_image = pig_image.convert_alpha() # This preserves the transparency of the PNG and optimizes the image for fast rendering with transparency.
pig_image = pygame.transform.scale(pig_image, (pig_image.get_width() // 25, pig_image.get_height() // 25))
wing_down_image = wing_down_image.convert_alpha()
wing_down_image = pygame.transform.scale(wing_down_image, (wing_down_image.get_width() // 8, wing_down_image.get_height() // 8))
wing_middle_image = wing_middle_image.convert_alpha()
wing_middle_image = pygame.transform.scale(wing_middle_image, (wing_middle_image.get_width() // 8, wing_middle_image.get_height() // 8))
wing_up_image = wing_up_image.convert_alpha()
wing_up_image = pygame.transform.scale(wing_up_image, (wing_up_image.get_width() // 8, wing_up_image.get_height() // 8))
for i in range(0, len(tower_up_images)):
    tower_up_images[i] = tower_up_images[i].convert_alpha()
    tower_up_images[i] = pygame.transform.scale(tower_up_images[i], (tower_up_images[i].get_width() // 1.75, tower_up_images[i].get_height() //1.75 ))
for i in range(0, len(tower_down_images)):
    tower_down_images[i] = tower_down_images[i].convert_alpha()
    tower_down_images[i] = pygame.transform.scale(tower_down_images[i], (tower_down_images[i].get_width() // 1.75, tower_down_images[i].get_height()//1.75 ))
for i in range(0, len(weapon_up_images)):
        weapon_up_images[i] = weapon_up_images[i].convert_alpha()
        weapon_up_images[i] = pygame.transform.scale(weapon_up_images[i], (
        weapon_up_images[i].get_width() // 1.75, weapon_up_images[i].get_height() // 1.75))
for i in range(0, len(weapon_down_images)):
        weapon_down_images[i] = weapon_down_images[i].convert_alpha()
        weapon_down_images[i] = pygame.transform.scale(weapon_down_images[i], (
        weapon_down_images[i].get_width() // 1.75, weapon_down_images[i].get_height() // 1.75))
for i in range(0, len(tree_down_images)):
        tree_down_images[i] = tree_down_images[i].convert_alpha()
        tree_down_images[i] = pygame.transform.scale(tree_down_images[i], (
        tree_down_images[i].get_width() // 1.75, tree_down_images[i].get_height() // 1.75))
for i in range(0, len(tree_up_images)):
        tree_up_images[i] = tree_up_images[i].convert_alpha()
        tree_up_images[i] = pygame.transform.scale(tree_up_images[i], (
        tree_up_images[i].get_width() // 1.75, tree_up_images[i].get_height() // 1.75))



# Add wings to pig
pig_down_image = add_wings(pig_image, wing_down_image, position = (-18,-4))
pig_middle_image = add_wings(pig_image, wing_middle_image, position = (-14,8))
pig_up_image = add_wings(pig_image, wing_up_image, position = (-18,-6))

pig_images = [pig_down_image, pig_middle_image, pig_up_image]

# Game variables
game_speed = 1
character_start_position = (100, 250)
score = 0
character_images = pig_images
ground_image = ground_pig_easy_image
background_image = background_pig_easy_image

# Game loop to prevent stack overflow from nested functions
while True:
    events = pygame.event.get() # Collect all events once per frame
    quit_game(events)

    if game_state == 'menu':
        menu()
    elif game_state == 'run_game':
        run_game(game_character, game_difficulty)




