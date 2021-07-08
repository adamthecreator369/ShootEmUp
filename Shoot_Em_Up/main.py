# Created by Adam Jost Dec, 2020

import pygame
from pygame import mixer
import random

# init()
pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init() 

# Set clock
clock = pygame.time.Clock()
fps = 60

# Set values for height and width of play screen
screen_width = 626
screen_height = 936

# Define colors (health bars)
red = (255, 0, 0)
green = (0, 255, 0)

# Text and Font (scores)
font_style = pygame.font.SysFont("Arial", 30)
text_background = (61, 61, 61)

# Screen and Caption (play screen and title)
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Shoot Em Up')

# Define game variables (various)
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False 
health = 3
rows = 9
cols = 3
alien_cooldown = 1000 
spaceship_cooldown = 1000 
last_alien_shot = pygame.time.get_ticks()
last_spaceship_shot = pygame.time.get_ticks()
# define key for when a key is pressed 
key = pygame.key.get_pressed()
write_count = 0
paused = False
level_count = 1

# Load sounds and set volumes
player1_killed_explosion_fx = pygame.mixer.Sound('assets/player1_killed_explosion.wav')
player1_killed_explosion_fx.set_volume(0.50)  # decrease volume
explosion_fx = pygame.mixer.Sound('assets/bad_guy_killed_explosion.wav')
explosion_fx.set_volume(0.20)  # decrease volume
explosion_fx2 = pygame.mixer.Sound('assets/player1_got_hit_explosion.wav')
explosion_fx2.set_volume(0.75)  # decrease volume
laser_fx = pygame.mixer.Sound('assets/laser.wav')
laser_fx.set_volume(0.20)  # decrease volume
intro_music = pygame.mixer.Sound('assets/intro.mp3')
intro_music.set_volume(0.20)  # decrease volume
increase_health_fx = pygame.mixer.Sound('assets/increase_health.wav')
increase_health_fx.set_volume(.80)  # decrease volume by 50%

# Load images
bgbg = pygame.image.load('assets/star_bg.jpg')  # game background
ground_img = pygame.image.load('assets/ground_626_doubled.png')  # ground of game
button_img = pygame.image.load('assets/restart_button.png')  # reset game button


# Create Message Function used for displaying score and high score
def message(msg, color, w, h, text_background):
    mesg = font_style.render(msg, True, color, text_background)
    screen.blit(mesg, [w / 3, h / 3])


# Define function to write players score to a file (currently used for determining high score)
def write_score(score, write_count):
    # Define score records file
    scores = open('scores.txt', 'a')
    if write_count < 1:
        scores.write(str(score) + "\n")
        write_count += 1
    scores.close()
    return write_count


# Function to find highest score 
def highest_score():
    # Read in scores from file and store in a list
    score_list_file = open('scores.txt', 'r')
    score_list = score_list_file.read()
    score_list = score_list.split()
    high_score = 0 
    # Find the Highest Score in the list
    for score in score_list:
        if int(score) > int(high_score):
            high_score = score
    score_list_file.close()
    return high_score


# Function to Reset Game and Resume Play
def reset_game():
    player1.rect.x = 100
    player1.rect.y = int(screen_height / 2)
    alien_group.empty()
    alien_bullet_group.empty()
    bullet_group.empty()
    spaceship_bullet_group.empty()
    astronaut_group.draw(screen)
    astronaut_group.update()
    alien_group.draw(screen)
    alien_group.update()
    spaceship_group.draw(screen)
    spaceship_group.update()
    create_aliens()
    astronaut_group.add(player1)
    spaceship_group.add(spaceship)
    health = 3
    player1.health_remaining = health
    player1.health_start = health
    spaceship.health_remaining = health
    spaceship.health_start = health
    player1.score = 0
    return health

# Classes 


# Construct and Astronaut Object
class Astronaut(pygame.sprite.Sprite):

    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img = pygame.image.load(f'assets/astronaut_flame{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.x = x
        self.y = y
        self.vel = 0 
        self.clicked = False
        self.last_shot = pygame.time.get_ticks()
        self.health_start = health
        self.health_remaining = health
        self.score = 0
   
    def update(self):
        # set cooldown variable for bullets
        cooldown = 425  # milliseconds 
        # define key for when a key is pressed 
        key = pygame.key.get_pressed()  # remember to clean this up!
        
        if flying == True:
            # gravity
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 824:
                self.rect.y += int(self.vel)
        
        if game_over == False: 
            # go up
            if self.rect.top > 10:
                if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                    self.vel = -10
                    self.clicked = True
                if pygame.mouse.get_pressed()[0] == 0:
                    self.clicked = False
        
            self.counter += 1
            astronaut_cooldown = 5
            # Sprite animation
            if self.counter > astronaut_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # rotate astronaut
            self.image = pygame.transform.rotate(self.images[self.index], self.vel / 3 * -1)
        else:
             # rotate astronaut
            self.image = pygame.transform.rotate(self.images[self.index], -260)
            self.kill()
            player1_killed_explosion_fx.play()
             # create explosion
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            player1_killed_explosion_fx.play()
            write_score(player1.score, write_count)

        # Slight rotation of Player at start before game play begins
        if flying == False and game_over == False: 
            self.image = pygame.transform.rotate(self.images[self.index], -3)
            
        # record current time
        time_now = pygame.time.get_ticks()
        # shoot
        if flying == True and game_over == False:
                if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
                    laser_fx.play()
                    bullet = Bullets(self.rect.right, self.rect.centery)
                    bullet_group.add(bullet)
                    self.last_shot = time_now
                if key[pygame.K_DOWN]:
                    self.image = pygame.transform.rotate(self.images[self.index], -35)
                if key[pygame.K_UP]:
                    self.image = pygame.transform.rotate(self.images[self.index], 25)
                    
        # update mask
        self.mask = pygame.mask.from_surface(self.image)
                    
        # draw health bar 
        pygame.draw.rect(screen, red, (self.rect.x - 12, self.rect.y + 30, 10, self.rect.height - 55))
        # draw green health bar on top of red health bar and decrease size as health goes down
        if self.health_remaining > 0:
                pygame.draw.rect(screen, green, (self.rect.x - 12, self.rect.y + 30, 10.25, int(self.rect.height - 55) * (self.health_remaining / self.health_start)))
        elif self.health_remaining <= 0:
            # create explosion
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
# End of Astronaut class


# Construct a Aliens object
class Aliens(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/bad_guy' + str(random.randint(1, 5)) + '.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1
    
    def update(self):
         # update mask
        self.mask = pygame.mask.from_surface(self.image)
        
        if flying == True and game_over == False:
            # add direction and back and forth movement
            self.rect.y += self.move_direction
            self.move_counter += 1
            if abs(self.move_counter) > 65:
                self.move_direction *= -1
                self.move_counter *= self.move_direction
                
# End of Aliens Class


# Level 2 Spaceship class
class Spaceship(pygame.sprite.Sprite):

    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/level2_spaceship_.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 2
        self.health_start = health
        self.health_remaining = health
        
    def update(self):
        # update mask
        self.mask = pygame.mask.from_surface(self.image)
        if flying == True and game_over == False:
            # add direction and back and forth movement
            self.rect.y += self.move_direction
            self.move_counter += 2
            if self.rect.top <= 10 or self.rect.bottom >= 824:
                self.move_direction *= -1
                self.move_counter *= self.move_direction
        # draw health bar 
        pygame.draw.rect(screen, red, (self.rect.x - 12, self.rect.y + 30, 10, self.rect.height - 55))
        # draw green health bar on top of red health bar and decrease size as health goes down
        if self.health_remaining > 0:
                pygame.draw.rect(screen, green, (self.rect.x - 12, self.rect.y + 30, 10.25, int(self.rect.height - 55) * (self.health_remaining / self.health_start)))
        elif self.health_remaining <= 0:
            self.kill()
            # create explosion
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)    
# End Spaceship Class


# Construct a Alien Bullet object
class Alien_Bullets(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/alien_bullet.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
    
    def update(self):
        # move bullets to the left
        self.rect.x -= 3 
        # delete of bullet from memory if it goes off the side of the screen
        if self.rect.left < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, astronaut_group, False, pygame.sprite.collide_mask):
            # reduce health
            player1.health_remaining -= 1
            # delete bullet
            self.kill()
            # play explosion sound
            explosion_fx2.play()
            # create explosion
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)
# End of  Alien Bullets Class 


# Construct a Spaceship Bullet object
class Spaceship_Bullets(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/spaceship_bullet.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
    
    def update(self):
        # move bullets to the left
        self.rect.x -= 3 
        # delete of bullet from memory if it goes off the side of the screen
        if self.rect.left < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, astronaut_group, False, pygame.sprite.collide_mask):
            # reduce health
            player1.health_remaining -= 1
            # delete bullet
            self.kill()
            # play explosion sound
            explosion_fx2.play()
            # create explosion
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)
# End of  Alien Bullets Class 


# Construct a Bullet object
class Bullets(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/bullet.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
    
    def update(self):
        # move bullets to the right
        self.rect.x += 5
        # delete of bullet from memory if it goes off the side of the screen
        if self.rect.left > 626:
            self.kill()
            
        # if bullet hits alien
        if pygame.sprite.spritecollide(self, alien_group, True, pygame.sprite.collide_mask):
            # delete bullet
            self.kill()
            explosion_fx.play()
            # create explosion
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
            player1.score += 10
        
        # if bullet hits spaceship
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            # delete bullet
            self.kill()
            explosion_fx.play()
            spaceship.health_remaining -= 1
            """
            # create explosion
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
            """
            player1.score += 20
# End of Bullets Class 

        
# Create Explosion Class
class Explosion(pygame.sprite.Sprite):

    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 7):
            explosion_img = pygame.image.load(f'assets/explosion{num}.png')
            if size == 1:
                explosion_img = pygame.transform.scale(explosion_img, (20, 20))
            if size == 2:
                explosion_img = pygame.transform.scale(explosion_img, (40, 40))
            if size == 3:
                explosion_img = pygame.transform.scale(explosion_img, (160, 160))
            # add img to list
            self.images.append(explosion_img)
        self.index = 0 
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0
        
    def update(self):
        explosion_speed = 3
        self.counter += 1
        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self_counter = 0
            self.index += 1
            self.image = self.images[self.index]
            
        # delete explosion
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()
# End Explosion Class


# Construct a Health Pack object
class Health_Pack(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/health_pack.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
    
    def update(self):
        # move health pack to the left
        self.rect.x -= 3 
        # delete health pack from memory if it goes off the side of the screen
        if self.rect.left < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, astronaut_group, False, pygame.sprite.collide_mask):
            # delete health pack
            self.kill()
            # play health increase sound
            increase_health_fx.play()
            if player1.health_remaining < 3:
                # increase health
                player1.health_remaining += 1
            
# End of Health_Pack Class 


# Start Button Class
class Button():

    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
    def draw(self):
        action = False
        # get mouse position
        pos = pygame.mouse.get_pos()
        # check if mouse is over but ton
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
                
        screen.blit(self.image, (self.rect.x, self.rect.y))
    
        return action
# End Button Class


# Sprite Groups
astronaut_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group() 
bullet_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
spaceship_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
spaceship_group = pygame.sprite.Group()
health_pack_group = pygame.sprite.Group()

# Restart button Instance
button = Button(screen_width // 2 - 75, screen_height // 2 - 100, button_img)

# Create instance of Astronaut
player1 = Astronaut(100, int(screen_height / 2), health)  # place him about the middle of the screen

astronaut_group.add(player1)


# Instantiate and Create Aliens
def create_aliens():
    for row in range(rows):
        for item in range(cols):
            alien = Aliens(340 + item * 100, 100 + row * 70)
            alien_group.add(alien)


create_aliens()

# Create spaceship instance
spaceship = Spaceship(screen_height // 2, screen_width // 2, health)
spaceship_group.add(spaceship)

# is the program running
run = True
while run:
    # Event Loop and Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True
            if flying == True:
                pygame.mixer.music.load('assets/game_play.mp3')
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.63)
            if flying == False: 
                pygame.mixer.music.pause()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
    if paused == True:
        continue
    
    # Check if all bad guys have been killed / regenerate bad guy and restore their health
    if len(alien_group) < 1 and len(spaceship_group) < 1:
        # Regenerate Bad Aliens
        create_aliens()
        # Restore Health of Spaceship
        spaceship.health_remaining = health
        spaceship.health_start = health
        # Add spaceship
        spaceship_group.add(spaceship)
        # Increase Level Number on Score Message
        level_count += 1
        if player1.y > screen_height // 2:
            health_pack = Health_Pack(screen_height // 2 + 10, screen_width)
        elif player1.y > screen_height // 2 - 60:
            health_pack = Health_Pack(screen_height // 2 - 60, screen_width)
        else:
            health_pack = Health_Pack(screen_height // 2 - 100, screen_width)
        health_pack_group.add(health_pack)
        
    # check if astronaut has hit the ground or ran out of health
    if player1.rect.bottom > 824:
        game_over = True
        flying = False
        
    # health check: if player1 is dead: Game over
    if player1.health_remaining <= 0:
        game_over = True
 
    if game_over == False and flying == True:
        # scroll the ground
        ground_scroll -= scroll_speed  # make ground scroll to the left
        # redraw at original place once it reaches the correct point
        if abs(ground_scroll) > 626:
            ground_scroll = 0
    
        # alien bullets randomization
        time_now2 = pygame.time.get_ticks()
        if time_now2 - last_alien_shot > alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0:
            attacking_alien = random.choice(alien_group.sprites())
            alien_bullet = Alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.centery)
            alien_bullet_group.add(alien_bullet)
            last_alien_shot = time_now2
            
        # spaceship bullets shooting
        if time_now2 - last_spaceship_shot > spaceship_cooldown and len(spaceship_bullet_group) < 5 and len(spaceship_group) > 0:
            attacking_spaceship = random.choice(spaceship_group.sprites())
            spaceship_bullet = Spaceship_Bullets(attacking_spaceship.rect.centerx, attacking_spaceship.rect.centery)
            spaceship_bullet_group.add(spaceship_bullet)
            last_spaceship_shot = time_now2
    
    # clock running at 60 fps
    clock.tick(fps)
    
    # Display the background image 
    screen.blit(bgbg, (-130, 0))
    
    # draw the astronaut 
    astronaut_group.draw(screen)
    astronaut_group.update()
    
    # draw aliens
    alien_group.draw(screen)
    alien_group.update()
    
    # draw spaceship
    spaceship_group.draw(screen)
    spaceship_group.update()
    
    # draw the bullets
    bullet_group.draw(screen)
    bullet_group.update()
    
    # draw alien bullets
    alien_bullet_group.draw(screen)
    alien_bullet_group.update()
    
    # draw spaceship bullets
    spaceship_bullet_group.draw(screen)
    spaceship_bullet_group.update()
    
    # draw explosions
    explosion_group.draw(screen)
    explosion_group.update()
    
    # health pack
    health_pack_group.draw(screen)
    health_pack_group.update()
    
    # draw the ground
    screen.blit(ground_img, (ground_scroll, 800))  # draw / show
    
    # Display Score using message()
    message("Lv" + str(level_count) + " Score: " + str(player1.score), (255, 255, 255), 60, 2600, text_background)
    
    # Display High Score using message() and and high_score()
    message("High Score: " + highest_score(), (255, 255, 255), 1150, 2600, text_background)
    # check for game over and reset
    if game_over == True:
        if button.draw() == True:
            game_over = False
            level_count = 1  # reset level
            health = reset_game()
            
    pygame.display.update()  # update everything that has happened above
pygame.quit()
