import pygame
import random
import math
import uuid  # added for unique player IDs
import time  # added for profile IDs generation
import secrets  # added for profile IDs generation

# Initialize Pygame
pygame.init()

# Create a Clock object
clock = pygame.time.Clock()

# Game Constants
WIDTH, HEIGHT = 1400, 800
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# Create Game Window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")


# Load Background Music
pygame.mixer.music.load("Graphics/Music/SoundM.mp3")  # Replace with the correct path to your music file
pygame.mixer.music.set_volume(0.5)  # Set the volume (optional)

# Load Images
player_img = pygame.image.load("Graphics/player1/set1.png")
enemy_img = pygame.image.load("Graphics/enemy.png")
bullet_img = pygame.image.load("Graphics/bullet.png")

# Resize Images
player_img = pygame.transform.scale(player_img, (120, 120))

# Load Player Animation Frames
player_frames = [
    pygame.image.load("Graphics/player1/set1.png"),
    pygame.image.load("Graphics/player1/set2.png"),
    pygame.image.load("Graphics/player1/set3.png"),
    pygame.image.load("Graphics/player1/set4.png"),
]

# Resize Player Animation Frames
player_frames = [pygame.transform.scale(frame, (80, 80)) for frame in player_frames]

# Animation Variables
player_frame_index = 0
animation_speed = 100  # Milliseconds per frame
last_animation_time = pygame.time.get_ticks()

# Load Bullet Animation Frames
bullet_frames = [
    pygame.image.load(f"Graphics/un/un{i}.png") for i in range(1, 4)
]

# Resize Bullet Animation Frames
bullet_frames = [pygame.transform.scale(frame, (20, 60)) for frame in bullet_frames]  # Increased size

# Bullet Animation Variables
bullet_frame_index = 0
bullet_animation_speed = 90  # Milliseconds per frame
last_bullet_animation_time = pygame.time.get_ticks()

# Replace the static enemy image with an animation
enemy_frames = [pygame.image.load(f"Graphics/alien2/m{i}.png") for i in range(1,7)]
enemy_frames = [pygame.transform.scale(frame, (50, 40)) for frame in enemy_frames]

# Enemy Animation Variables
enemy_frame_index = 0
enemy_animation_speed = 100  # Milliseconds per frame
last_enemy_animation_time = pygame.time.get_ticks()

# Load Top Shooter Enemy (Enemy2) Animation Frames
enemy2_frames = [pygame.image.load(f"Graphics/alien2/m{i}.png") for i in range(1, 7)]
enemy2_frames = [pygame.transform.scale(frame, (62, 50)) for frame in enemy2_frames]

# Top Shooter Enemy Animation Variables
enemy2_frame_index = 0
enemy2_animation_speed = 100  # Milliseconds per frame
last_enemy2_animation_time = pygame.time.get_ticks()

# Top Shooter Enemy Variables
enemy2_x = WIDTH // 2 - 35        # Centered at the top (adjust as needed)
enemy2_y = 10                    # Y position near the top
enemy2_bullets = []              # List to store enemy2 bullets
enemy2_shot_cooldown = 90      # Cooldown period in milliseconds between shots
last_enemy2_shot_time = pygame.time.get_ticks()
enemy2_bullet_speed = 25         # Speed of enemy2 bullets

# Load Button Sound
button_sound = pygame.mixer.Sound("Graphics/Music/buttons.mp3")  # Replace with the correct path to your sound file
button_sound.set_volume(0.5)  # Set the volume (optional)

# Load Laser Shot Sound
laser_shot = pygame.mixer.Sound("Graphics/Music/laser-shot.mp3")
laser_shot.set_volume(0.3)  # Adjust volume as needed

# Load Enemy Death Sound
enemyD = pygame.mixer.Sound("Graphics/Music/enemyD.mp3")
enemyD.set_volume(0.6)  # Adjust volume as needed

# Player Variables
player_x = WIDTH // 2 - 35
player_y = HEIGHT - 120
player_speed = 10
# Unique identifiers for players (UIDs)
player1_uid = str(uuid.uuid4())
player2_uid = str(uuid.uuid4())

# Bullet Variables
bullets = []
can_shoot = True           # Allow shooting by default
last_shot_time_p1 = 0         # For player 1 shooting
last_shot_time_p2 = 0         # For player 2 shooting
shoot_cooldown = 350       # Cooldown period in milliseconds (adjust as needed)
bullet_speed = 12          # Bullet movement speed (adjust as needed)

# Score and Level
score = 0
level = 1
highest_score = 0  # Global variable to track highest score

# Load Custom Font
font = pygame.font.Font("Graphics/Font/monogram.ttf", 36)  # Adjust the path and size as needed

# Enemy Spacing
def create_enemies(rows, cols, speed):
    enemies = []
    x_spacing = (WIDTH - 700) // cols  # Reduced horizontal spacing
    y_spacing = 65  # Reduced vertical spacing
    start_x = 100  # Starting x position (adjusted for centering)
    start_y = 80  # Starting y position

    for row in range(rows):
        for col in range(cols):
            enemy_x = start_x + col * x_spacing
            enemy_y = start_y + row * y_spacing
            enemies.append([enemy_x, enemy_y, speed])
    return enemies

def create_alien_formation(alien_speed):
    formation = []
    offset = 60  # <-- Change this value to lower (increase) or raise (decrease) the formation
    cols = 11  # Fixed number of columns
    x_spacing = (WIDTH - 700) // cols  # Horizontal spacing
    start_x = 100  # Starting x position
    y_spacing = 55  # Vertical spacing between rows
    gap_between_groups = 1  # Gap between different groups

    # Top group: Alien1 (1 row) with offset added
    alien1_start_y = 55 + offset
    for col in range(cols):
        x = start_x + col * x_spacing
        formation.append([x, alien1_start_y, alien_speed, 'alien1'])
    
    # Middle group: Alien3 (2 rows)
    alien3_start_y = alien1_start_y + y_spacing + gap_between_groups
    for row in range(2):
        for col in range(cols):
            x = start_x + col * x_spacing
            y = alien3_start_y + row * y_spacing
            formation.append([x, y, alien_speed, 'alien3'])
    
    # Bottom group: Enemy2 (2 rows)
    enemy2_start_y = alien3_start_y + 2 * y_spacing + gap_between_groups
    for row in range(2):
        for col in range(cols):
            x = start_x + col * x_spacing
            y = enemy2_start_y + row * y_spacing
            formation.append([x, y, alien_speed, 'enemy2'])
    return formation

def draw_button(text, x, y, text_color, is_hovered):
    # Render Shadow
    shadow_color = (50, 50, 50)  # Dark gray for shadow
    shadow_offset = 2  # Offset for the shadow
    shadow_label = font.render(text, True, shadow_color)
    shadow_rect = shadow_label.get_rect(center=(x, y + shadow_offset))
    screen.blit(shadow_label, shadow_rect)

    # Render Text
    label = font.render(text, True, WHITE if is_hovered else text_color)
    text_rect = label.get_rect(center=(x, y))
    screen.blit(label, text_rect)

    # Remove arrow drawing for hovered buttons
    # (Previously, an arrow was drawn here when `is_hovered` was True)

def draw_arrow(x, text_center_y):
    # Arrow dimensions for consistent design
    arrow_width = 10  # Width of the arrow
    arrow_height = 6  # Height of the arrow
    arrow_points = [
        (x, text_center_y),                      # Tip of the arrow
        (x - arrow_width, text_center_y - arrow_height),  # Top point
        (x - arrow_width, text_center_y + arrow_height)   # Bottom point
    ]
    pygame.draw.polygon(screen, WHITE, arrow_points)

def draw_back_arrow():
    # Draw a back arrow in the top-left corner
    arrow_points = [(20, 20), (40, 30), (20, 40)]  # Arrow shape
    pygame.draw.polygon(screen, WHITE, arrow_points)

def difficulty_selection():
    # Load the background animation frames for the difficulty selection screen
    background_frames = [
        pygame.image.load(f"Graphics/BackG3/h{i}.png") for i in range(1, 13)  # Adjusted range to 1-12
    ]
    background_frames = [pygame.transform.scale(frame, (WIDTH, HEIGHT)) for frame in background_frames]

    # Animation variables
    bg_frame_index = 0
    bg_animation_speed = 100  # Milliseconds per frame
    last_bg_animation_time = pygame.time.get_ticks()

    button_spacing = 50  # Spacing between buttons
    start_y = 330

    # Arrow blinking animation variables
    arrow_visible = True
    arrow_blink_speed = 500  # Milliseconds
    last_arrow_blink_time = pygame.time.get_ticks()

    # Load a larger and bold font for the title
    title_font = pygame.font.Font("Graphics/Font/monogram.ttf", 88)

    # Define "Settings" Button in the Top-Right Corner
    settings_text = font.render("SETTINGS", True, WHITE)
    settings_rect = settings_text.get_rect(topright=(WIDTH - 20, 20))

    while True:
        # Handle background animation timing
        current_time = pygame.time.get_ticks()
        if current_time - last_bg_animation_time > bg_animation_speed:
            bg_frame_index = (bg_frame_index + 1) % len(background_frames)
            last_bg_animation_time = current_time

        # Handle arrow blinking animation timing
        if current_time - last_arrow_blink_time > arrow_blink_speed:
            arrow_visible = not arrow_visible
            last_arrow_blink_time = current_time

        # Draw the current background frame
        screen.blit(background_frames[bg_frame_index], (0, 0))

        mouse_pos = pygame.mouse.get_pos()

        # Render "Choose Your Game Mode" Text
        title_text = title_font.render("Choose Your Game Mode", True, WHITE)
        title_shadow = title_font.render("Choose Your Game Mode", True, (50, 50, 50))
        title_rect = title_text.get_rect(center=(WIDTH // 2, 250))
        title_shadow_rect = title_shadow.get_rect(center=(WIDTH // 2 + 2, 252))

# Simulate bold by blitting shadow and text multiple times with slight offsets
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
           screen.blit(title_shadow, title_shadow_rect.move(dx, dy))
        screen.blit(title_shadow, title_shadow_rect)
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
           screen.blit(title_text, title_rect.move(dx, dy))
        screen.blit(title_text, title_rect)

        # Draw Buttons for EASY, MEDIUM, and HARD modes only
        easy_text = "EASY"
        medium_text = "MEDIUM"
        hard_text = "HARD"

        easy_rect = font.render(easy_text, True, WHITE).get_rect(center=(WIDTH // 2, start_y + button_spacing * 0.1))
        medium_rect = font.render(medium_text, True, WHITE).get_rect(center=(WIDTH // 2, start_y + button_spacing * 1.0))
        hard_rect = font.render(hard_text, True, WHITE).get_rect(center=(WIDTH // 2, start_y + button_spacing * 1.9))

        easy_btn_hover = easy_rect.collidepoint(mouse_pos)
        medium_btn_hover = medium_rect.collidepoint(mouse_pos)
        hard_btn_hover = hard_rect.collidepoint(mouse_pos)

        draw_button(easy_text, easy_rect.centerx, easy_rect.centery, WHITE, easy_btn_hover)
        draw_button(medium_text, medium_rect.centerx, medium_rect.centery, WHITE, medium_btn_hover)
        draw_button(hard_text, hard_rect.centerx, hard_rect.centery, WHITE, hard_btn_hover)

        # Draw blinking arrow for hovered buttons
        if arrow_visible:
            if easy_btn_hover:
                draw_arrow(easy_rect.left - 15, easy_rect.centery)
            if medium_btn_hover:
                draw_arrow(medium_rect.left - 15, medium_rect.centery)
            if hard_btn_hover:
                draw_arrow(hard_rect.left - 15, hard_rect.centery)
        
        # Draw "Settings" Button
        screen.blit(settings_text, settings_rect)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                # Change ESC behavior: now go to player selection instead of space invaders start screen
                if event.key == pygame.K_ESCAPE:
                    button_sound.play()  # Play button sound when ESC is pressed
                    start_mode_screen()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy_btn_hover:
                    button_sound.play()  # Play button sound when EASY is clicked
                    pygame.mixer.music.stop()
                    # Return to main loop to start the game
                    return 3, 5
                if medium_btn_hover:
                    button_sound.play()  # Play button sound when MEDIUM is clicked
                    pygame.mixer.music.stop()
                    return 5, 7
                if hard_btn_hover:
                    button_sound.play()  # Play button sound when HARD is clicked
                    pygame.mixer.music.stop()
                    return 7, 10
                if settings_rect.collidepoint(event.pos):
                    button_sound.play()  # Play button sound when SETTINGS is clicked
                    settings_screen()
        # ...existing code...
# ...existing code...

# Music Volume Variable
music_volume = 0.5  # Default volume (50%)

# Profile data generated only once per session
profile_uuid = uuid.uuid4()
profile_custom = f"{int(time.time() * 1000)}-{random.randint(1000,9999)}"
profile_secure = secrets.token_hex(8)

# Add new welcome banner function
def welcome_screen():
    # Load welcome background music
    welcome_bg_music = pygame.mixer.Sound("Graphics/Music/welcome.mp3")
    welcome_bg_music.set_volume(0.5)  # adjust volume as needed
    welcome_bg_music.play(-1)  # Loop while on welcome screen

    # Load background frames from BackG13 folder (we1.png to we48.png)
    bg_frames = [pygame.transform.scale(pygame.image.load(f"Graphics/BackG13/we{i}.png"), (WIDTH, HEIGHT)) for i in range(1,49)]
    bg_frame_index = 0
    bg_animation_speed = 10  # milliseconds per frame
    last_bg_animation_time = pygame.time.get_ticks()
    
    welcome_font = pygame.font.Font("Graphics/Font/monogram.ttf", 120)  # increased size
    shadow_offset = 2
    waiting = True
    while waiting:
        current_time = pygame.time.get_ticks()
        if current_time - last_bg_animation_time > bg_animation_speed:
            bg_frame_index = (bg_frame_index + 1) % len(bg_frames)
            last_bg_animation_time = current_time
        
        # Draw animated background frame
        screen.blit(bg_frames[bg_frame_index], (0, 0))
        # Darken the background with an overlay
        dark_overlay = pygame.Surface((WIDTH, HEIGHT))
        dark_overlay.fill((0, 0, 0))
        dark_overlay.set_alpha(80)  # Adjust alpha for desired darkness
        screen.blit(dark_overlay, (0, 0))
        
        # Render welcome text with shadow (will now be displayed in a larger font)
        welcome_text = welcome_font.render("Welcome, Players", True, WHITE)
        welcome_shadow = welcome_font.render("Welcome, Players", True, (50, 50, 50))
        welcome_rect = welcome_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        shadow_rect = welcome_shadow.get_rect(center=(WIDTH // 2 + shadow_offset, HEIGHT // 2 - 50 + shadow_offset))

        # Simulate bold by blitting shadow and text multiple times with slight offsets
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            screen.blit(welcome_shadow, shadow_rect.move(dx, dy))
        screen.blit(welcome_shadow, shadow_rect)
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            screen.blit(welcome_text, welcome_rect.move(dx, dy))
        screen.blit(welcome_text, welcome_rect)
        
        # Render prompt text with shadow
        prompt_text = font.render("Press any key to continue", True, WHITE)
        prompt_shadow = font.render("Press any key to continue", True, (50, 50, 50))
        prompt_rect = prompt_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        prompt_shadow_rect = prompt_shadow.get_rect(center=(WIDTH // 2 + shadow_offset, HEIGHT // 2 + 50 + shadow_offset))
        screen.blit(prompt_shadow, prompt_shadow_rect)
        screen.blit(prompt_text, prompt_rect)
        
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                button_sound.play()  # Play button sound when any button is clicked
                welcome_bg_music.stop()  # Stop welcome music on any input
                waiting = False
        clock.tick(30)

# Prepared by: Mary-Ann E. Lopez-Mzana, MTS 3
def settings_screen():
    global music_volume

    # Load the background animation frames for the settings screen
    background_frames = [
        pygame.image.load(f"Graphics/BACKG2/a{i}.png") for i in range(1, 35)
    ]
    background_frames = [pygame.transform.scale(frame, (WIDTH, HEIGHT)) for frame in background_frames]

    # Animation variables
    bg_frame_index = 0
    bg_animation_speed = 100  # Milliseconds per frame
    last_bg_animation_time = pygame.time.get_ticks()

    # Slider variables
    slider_x = WIDTH // 2 - 100
    slider_y = HEIGHT // 2
    slider_width = 200
    slider_height = 10
    slider_handle_radius = 10
    slider_handle_x = slider_x + int(music_volume * slider_width)
    is_dragging = False  # Flag to track if the slider handle is being dragged

    # Arrow blinking animation variables
    arrow_blink_speed = 500  # milliseconds
    last_arrow_blink_time = pygame.time.get_ticks()
    arrow_visible = True

    while True:
        # Handle background animation timing
        current_time = pygame.time.get_ticks()
        if current_time - last_bg_animation_time > bg_animation_speed:
            bg_frame_index = (bg_frame_index + 1) % len(background_frames)
            last_bg_animation_time = current_time

        # Handle arrow blinking animation timing
        if current_time - last_arrow_blink_time > arrow_blink_speed:
            arrow_visible = not arrow_visible
            last_arrow_blink_time = current_time

        # Draw the current background frame
        screen.blit(background_frames[bg_frame_index], (0, 0))

        # Render "Settings" Title with shadow
        shadow_offset = 2
        settings_big_font = pygame.font.Font("Graphics/Font/monogram.ttf", 110)  # new larger font for SETTINGS
        settings_shadow = settings_big_font.render("SETTINGS", True, (50,50,50))
        settings_shadow_rect = settings_shadow.get_rect(center=(WIDTH // 2 + shadow_offset, HEIGHT // 2 - 100 + shadow_offset))
        settings_text = settings_big_font.render("SETTINGS", True, WHITE)
        settings_title_rect = settings_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        screen.blit(settings_shadow, settings_shadow_rect)
        screen.blit(settings_text, settings_title_rect)

        # Draw the slider bar with a border and rounded corners
        pygame.draw.rect(screen, WHITE, (slider_x - 2, slider_y - 2, slider_width + 4, slider_height + 4), border_radius=slider_height // 2)
        pygame.draw.rect(screen, GRAY, (slider_x, slider_y, slider_width, slider_height), border_radius=slider_height // 2)
        pygame.draw.circle(screen, WHITE, (slider_handle_x, slider_y + slider_height // 2), slider_handle_radius)  # Handle

        # Render "Music Volume" Text
        volume_text = font.render(f"Music Volume: {int(music_volume * 100)}%", True, WHITE)
        volume_text_rect = volume_text.get_rect(center=(WIDTH // 2, slider_y - 30))
        screen.blit(volume_text, volume_text_rect)

        # Modified: Draw the PROFILE button using draw_button
        mouse_pos = pygame.mouse.get_pos()
        profile_label = "PROFILE"
        profile_rect = font.render(profile_label, True, WHITE).get_rect(center=(WIDTH // 2, slider_y + 100))
        profile_hover = profile_rect.collidepoint(mouse_pos)
        draw_button(profile_label, profile_rect.centerx, profile_rect.centery, WHITE, profile_hover)
        if arrow_visible and profile_hover:
            draw_arrow(profile_rect.left - 15, profile_rect.centery)

        pygame.display.update()

        # Handle Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the mouse is on the slider handle
                if (slider_handle_x - slider_handle_radius <= event.pos[0] <= slider_handle_x + slider_handle_radius and
                        slider_y - slider_handle_radius <= event.pos[1] <= slider_y + slider_height + slider_handle_radius):
                    is_dragging = True  # Start dragging
                if profile_rect.collidepoint(event.pos):
                    profile_screen()
            if event.type == pygame.MOUSEBUTTONUP:
                is_dragging = False  # Stop dragging
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Press ESC to go back to the start screen
                    return

        # Adjust the slider handle position while dragging
        if is_dragging:
            mouse_x = pygame.mouse.get_pos()[0]
            slider_handle_x = max(slider_x, min(mouse_x, slider_x + slider_width))  # Clamp the handle within the slider bar
            music_volume = (slider_handle_x - slider_x) / slider_width  # Calculate volume (0.0 to 1.0)
            pygame.mixer.music.set_volume(music_volume)  # Adjust music volume

def profile_screen():
    # Load background frames from "Graphics/BackG12/pf1.png" to "pf28.png"
    frames = [pygame.transform.scale(pygame.image.load(f"Graphics/BackG12/pf{i}.png"), (WIDTH, HEIGHT)) for i in range(1, 29)]
    bg_frame_index = 0
    bg_animation_speed = 100  # Milliseconds per frame
    last_bg_animation_time = pygame.time.get_ticks()
    
    # Use pre-generated profile IDs (do not regenerate)
    global profile_uuid, profile_custom, profile_secure
    unique_id_uuid = profile_uuid
    custom_id = profile_custom
    secure_id = profile_secure

    # --- Facebook-style profile layout with animated avatar ---
    # Load all profile images PF1 to PF27 for animation
    profile_imgs = [
        pygame.transform.scale(
            pygame.image.load(f"Graphics/profile/PF{i}.png"), (180, 180)
        ) for i in range(1, 28)
    ]
    profile_frame_index = 0
    profile_anim_speed = 120  # ms per frame
    last_profile_anim_time = pygame.time.get_ticks()
    avatar_size = 180
    avatar_y = HEIGHT // 2 - 180

    # Name and info font
    name_font = pygame.font.Font("Graphics/Font/monogram.ttf", 56)
    info_font = font  # already loaded at 36

    # Name (simulate account name, e.g., "My Profile")
    account_name = "Profile Info"

    # Shadow settings
    shadow_offset = 2
    shadow_color = (50, 50, 50)

    # Pre-render name with shadow
    name_shadow = name_font.render(account_name, True, shadow_color)
    name_text = name_font.render(account_name, True, WHITE)

    # Info lines (UUID, Time+Random, Secure) with shadow
    uuid_text = info_font.render("UUID: " + str(unique_id_uuid), True, WHITE)
    uuid_shadow = info_font.render("UUID: " + str(unique_id_uuid), True, shadow_color)
    custom_text = info_font.render("Time+Random: " + custom_id, True, WHITE)
    custom_shadow = info_font.render("Time+Random: " + custom_id, True, shadow_color)
    secure_text = info_font.render("Secure: " + secure_id, True, WHITE)
    secure_shadow = info_font.render("Secure: " + secure_id, True, shadow_color)

    info_lines = 3
    line_height = uuid_text.get_height() + 10

    running_profile = True
    while running_profile:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running_profile = False

        current_time = pygame.time.get_ticks()
        if current_time - last_bg_animation_time > bg_animation_speed:
            bg_frame_index = (bg_frame_index + 1) % len(frames)
            last_bg_animation_time = current_time

        # Animate profile avatar
        if current_time - last_profile_anim_time > profile_anim_speed:
            profile_frame_index = (profile_frame_index + 1) % len(profile_imgs)
            last_profile_anim_time = current_time

        screen.blit(frames[bg_frame_index], (0, 0))
        # Dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(100)
        screen.blit(overlay, (0, 0))

        # --- Draw account name with shadow (centered below avatar) ---
        name_y = avatar_y + avatar_size + 30
        name_shadow_rect = name_shadow.get_rect(center=(WIDTH//2 + shadow_offset, name_y + shadow_offset))
        name_text_rect = name_text.get_rect(center=(WIDTH//2, name_y))
        screen.blit(name_shadow, name_shadow_rect)
        screen.blit(name_text, name_text_rect)

        # --- Draw info lines with shadow, centered below name ---
        info_start_y = name_text_rect.bottom + 30
        y1 = info_start_y
        y2 = info_start_y + line_height
        y3 = info_start_y + 2 * line_height
        # UUID
        screen.blit(uuid_shadow, uuid_text.get_rect(center=(WIDTH//2 + shadow_offset, y1 + shadow_offset)))
        screen.blit(uuid_text, uuid_text.get_rect(center=(WIDTH//2, y1)))
        # Time+Random
        screen.blit(custom_shadow, custom_text.get_rect(center=(WIDTH//2 + shadow_offset, y2 + shadow_offset)))
        screen.blit(custom_text, custom_text.get_rect(center=(WIDTH//2, y2)))
        # Secure
        screen.blit(secure_shadow, secure_text.get_rect(center=(WIDTH//2 + shadow_offset, y3 + shadow_offset)))
        screen.blit(secure_text, secure_text.get_rect(center=(WIDTH//2, y3)))

        pygame.display.update()
        clock.tick(30)

def new_settings_screen():
    # Load background animation frames from BACKG4 (o1.png to o24.png)
    background_frames = [pygame.image.load(f"Graphics/BACKG4/o{i}.png") for i in range(1, 25)]
    background_frames = [pygame.transform.scale(frame, (WIDTH, HEIGHT)) for frame in background_frames]
    
    bg_frame_index = 0
    bg_animation_speed = 100  # milliseconds per frame
    last_bg_animation_time = pygame.time.get_ticks()
    
    # Slider (Music Volume) variables
    slider_x = WIDTH // 2 - 100
    slider_y = HEIGHT // 2 - 50
    slider_width = 200
    slider_height = 10
    slider_handle_radius = 10
    slider_handle_x = slider_x + int(pygame.mixer.music.get_volume() * slider_width)
    is_dragging = False
    
    # Create RESUME button
    resume_text = font.render("RESUME", True, WHITE)
    resume_rect = resume_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
    
    while True:
        current_time = pygame.time.get_ticks()
        if current_time - last_bg_animation_time > bg_animation_speed:
            bg_frame_index = (bg_frame_index + 1) % len(background_frames)
            last_bg_animation_time = current_time
        
        # Draw animated background
        screen.blit(background_frames[bg_frame_index], (0, 0))
        
        # Draw Music Volume Slider
        pygame.draw.rect(screen, WHITE, (slider_x - 2, slider_y - 2, slider_width + 4, slider_height + 4), border_radius=slider_height//2)
        pygame.draw.rect(screen, GRAY, (slider_x, slider_y, slider_width, slider_height), border_radius=slider_height//2)
        pygame.draw.circle(screen, WHITE, (slider_handle_x, slider_y + slider_height//2), slider_handle_radius)
        
        # Render Music Volume label
        volume_label = font.render("MUSIC VOLUME", True, WHITE)
        volume_label_rect = volume_label.get_rect(center=(WIDTH // 2, slider_y - 30))
        screen.blit(volume_label, volume_label_rect)
        
        # Draw RESUME button
        pygame.draw.rect(screen, GRAY, resume_rect.inflate(20, 10))
        screen.blit(resume_text, resume_rect)
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # If slider handle is clicked, start dragging
                    if (slider_handle_x - slider_handle_radius <= event.pos[0] <= slider_handle_x + slider_handle_radius and
                        slider_y - slider_handle_radius <= event.pos[1] <= slider_y + slider_height + slider_handle_radius):
                        is_dragging = True
                    # Check if RESUME is clicked: exit settings to return to gameplay
                    if resume_rect.collidepoint(event.pos):
                        button_sound.play()
                        return
            if event.type == pygame.MOUSEBUTTONUP:
                is_dragging = False
            if event.type == pygame.MOUSEMOTION and is_dragging:
                mouse_x = event.pos[0]
                slider_handle_x = max(slider_x, min(mouse_x, slider_x + slider_width))
                volume = (slider_handle_x - slider_x) / slider_width
                pygame.mixer.music.set_volume(volume)
                    
        clock.tick(30)

def start_game_screen():
    # Load the background animation frames
    background_frames = [pygame.transform.scale(pygame.image.load(f"Graphics/BackG10/Q{i}.png"), (WIDTH, HEIGHT)) for i in range(1, 145)]
    # Darken each frame by blitting a semi-transparent black overlay
    for i in range(len(background_frames)):
        dark_overlay = pygame.Surface(background_frames[i].get_size(), flags=pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 100))  # Adjust alpha (0-255) for desired darkness
        background_frames[i].blit(dark_overlay, (0, 0))

    title_font = pygame.font.Font("Graphics/Font/monogram.ttf", 96)  # Increase font size for bold effect

    # Animation variables
    bg_frame_index = 0
    bg_animation_speed = 20     # Milliseconds per frame
    last_bg_animation_time = pygame.time.get_ticks()

    # Arrow blinking animation variables
    arrow_visible = True
    arrow_blink_speed = 500  # Milliseconds
    last_arrow_blink_time = pygame.time.get_ticks()

    # Play background music only if it's not already playing
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load("Graphics/Music/SoundM.mp3")  # Load the background music
        pygame.mixer.music.play(-1)  # Play the music in a loop

    while True:
        # Handle background and arrow animations
        current_time = pygame.time.get_ticks()
        if current_time - last_bg_animation_time > bg_animation_speed:
            bg_frame_index = (bg_frame_index + 1) % len(background_frames)
            last_bg_animation_time = current_time
        if current_time - last_arrow_blink_time > arrow_blink_speed:
            arrow_visible = not arrow_visible
            last_arrow_blink_time = current_time

        # Draw the current background frame
        screen.blit(background_frames[bg_frame_index], (0, 0))
        
        # --- SHADOW: "SPACE INVADERS" TITLE ---
        shadow_color = (50, 50, 50)  # Dark gray for shadow
        shadow_offset = 2  # Offset for the shadow

        # Render "SPACE INVADERS" Title with shadow, moved higher
        title_text = title_font.render("SPACE INVADERS", True, WHITE)
        title_shadow = title_font.render("SPACE INVADERS", True, shadow_color)
        # Moved from HEIGHT // 2.5 to HEIGHT // 3
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        title_shadow_rect = title_shadow.get_rect(center=(WIDTH // 2 + shadow_offset, (HEIGHT // 3) + shadow_offset))
        screen.blit(title_shadow, title_shadow_rect)
        screen.blit(title_text, title_rect)
        
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            screen.blit(title_shadow, title_shadow_rect.move(dx, dy))
        screen.blit(title_shadow, title_shadow_rect)
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            screen.blit(title_text, title_rect.move(dx, dy))
        screen.blit(title_text, title_rect)

        # Render "PLAY" Text with shadow
        play_text = font.render("PLAY", True, WHITE)
        play_shadow = font.render("PLAY", True, shadow_color)
        play_text_rect = play_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        play_shadow_rect = play_shadow.get_rect(center=(WIDTH // 2 + shadow_offset, (HEIGHT // 2) + shadow_offset))
        screen.blit(play_shadow, play_shadow_rect)
        screen.blit(play_text, play_text_rect)

        # Render "SETTINGS" Text with shadow
        settings_text = font.render("SETTINGS", True, WHITE)
        settings_shadow = font.render("SETTINGS", True, shadow_color)
        settings_text_rect = settings_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        settings_shadow_rect = settings_shadow.get_rect(center=(WIDTH // 2 + shadow_offset, (HEIGHT // 2 + 40) + shadow_offset))
        screen.blit(settings_shadow, settings_shadow_rect)
        screen.blit(settings_text, settings_text_rect)

        # Render "EXIT" Text with shadow
        exit_text = font.render("EXIT", True, WHITE)
        exit_shadow = font.render("EXIT", True, shadow_color)
        exit_text_rect = exit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
        exit_shadow_rect = exit_shadow.get_rect(center=(WIDTH // 2 + shadow_offset, (HEIGHT // 2 + 80) + shadow_offset))
        screen.blit(exit_shadow, exit_shadow_rect)
        screen.blit(exit_text, exit_text_rect)
        
        # Draw a small arrow on the left side pointing to the right for "Play"
        mouse_pos = pygame.mouse.get_pos()
        if play_text_rect.collidepoint(mouse_pos) and arrow_visible:
            arrow_points = [
                (play_text_rect.left - 20, play_text_rect.centery),      # Tip
                (play_text_rect.left - 30, play_text_rect.centery - 5),  # Top point
                (play_text_rect.left - 30, play_text_rect.centery + 5)   # Bottom point
            ]
            pygame.draw.polygon(screen, WHITE, arrow_points)  # Draw the arrow

        # Draw a small arrow on the left side pointing to the right for "Settings"
        if settings_text_rect.collidepoint(mouse_pos) and arrow_visible:
            arrow_points = [
                (settings_text_rect.left - 20, settings_text_rect.centery),      # Tip
                (settings_text_rect.left - 30, settings_text_rect.centery - 5),  # Top point
                (settings_text_rect.left - 30, settings_text_rect.centery + 5)   # Bottom point
            ]
            pygame.draw.polygon(screen, WHITE, arrow_points)  # Draw the arrow

        # Draw a small arrow on the left side pointing to the right for "Exit"
        if exit_text_rect.collidepoint(mouse_pos) and arrow_visible:
            arrow_points = [
                (exit_text_rect.left - 20, exit_text_rect.centery),      # Tip
                (exit_text_rect.left - 30, exit_text_rect.centery - 5),  # Top point
                (exit_text_rect.left - 30, exit_text_rect.centery + 5)   # Bottom point
            ]
            pygame.draw.polygon(screen, WHITE, arrow_points)  # Draw the arrow

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_text_rect.collidepoint(event.pos):
                    button_sound.play()  # Play button sound
                    return  # Exit the start screen and proceed to difficulty selection
                if settings_text_rect.collidepoint(event.pos):
                    button_sound.play()  # Play button sound
                    settings_screen()  # Open the settings screen
                if exit_text_rect.collidepoint(event.pos):
                    button_sound.play()  # Play button sound
                    pygame.quit()  # Exit the game
                    exit()

def in_game_settings_screen():
    import sys, os
    # Load background animation frames (reuse BACKG4 frames)
    background_frames = [pygame.image.load(f"Graphics/BACKG4/o{i}.png") for i in range(1, 25)]
    background_frames = [pygame.transform.scale(frame, (WIDTH, HEIGHT)) for frame in background_frames]
    
    bg_frame_index = 0
    bg_animation_speed = 100  # milliseconds per frame
    last_bg_animation_time = pygame.time.get_ticks()
    
    # Slider (Music Volume) variables
    slider_x = WIDTH // 2 - 100
    slider_y = HEIGHT // 2 - 30
    slider_width = 200
    slider_height = 10
    slider_handle_radius = 10
    slider_handle_x = slider_x + int(pygame.mixer.music.get_volume() * slider_width)
    is_dragging = False
    
    # Create RESUME, PLAY AGAIN, and HOME buttons (rendered without a solid background)
    resume_text = font.render("RESUME", True, WHITE)
    resume_rect = resume_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
    play_again_text = font.render("PLAY AGAIN", True, WHITE)
    play_again_rect = play_again_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
    home_text = font.render("EXIT", True, WHITE)
    home_rect = home_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    
    arrow_blink_speed = 500  # milliseconds
    last_arrow_blink_time = pygame.time.get_ticks()
    arrow_visible = True

    while True:
        current_time = pygame.time.get_ticks()
        if current_time - last_bg_animation_time > bg_animation_speed:
            bg_frame_index = (bg_frame_index + 1) % len(background_frames)
            last_bg_animation_time = current_time

        if current_time - last_arrow_blink_time > arrow_blink_speed:
            arrow_visible = not arrow_visible
            last_arrow_blink_time = current_time
        
        # Draw animated background
        screen.blit(background_frames[bg_frame_index], (0, 0))
        
        # Draw slider outline and handle
        pygame.draw.rect(screen, WHITE, (slider_x - 2, slider_y - 2, slider_width + 4, slider_height + 4), border_radius=slider_height//2)
        pygame.draw.circle(screen, WHITE, (slider_handle_x, slider_y + slider_height//2), slider_handle_radius)
        
        # Set up shadow parameters
        shadow_color = (50, 50, 50)
        shadow_offset = 2
        
        # Render "GAME PAUSE" with shadow using a large font
        big_font = pygame.font.Font("Graphics/Font/monogram.ttf", 95)  # Increased font size
        pause_text = big_font.render("GAME PAUSE", True, WHITE)
        pause_shadow = big_font.render("GAME PAUSE", True, shadow_color)
        pause_rect = pause_text.get_rect(center=(WIDTH // 2, slider_y - 100))
        pause_shadow_rect = pause_shadow.get_rect(center=(WIDTH // 2 + shadow_offset, slider_y - 100 + shadow_offset))
        screen.blit(pause_shadow, pause_shadow_rect)
        screen.blit(pause_text, pause_rect)
        
        # Render Music Volume label with shadow
        volume_text = font.render(f"MUSIC VOLUME: {int(pygame.mixer.music.get_volume()*100)}%", True, WHITE)
        volume_shadow = font.render(f"MUSIC VOLUME: {int(pygame.mixer.music.get_volume()*100)}%", True, shadow_color)
        volume_text_rect = volume_text.get_rect(center=(WIDTH // 2, slider_y - 30))
        volume_shadow_rect = volume_shadow.get_rect(center=(WIDTH // 2 + shadow_offset, slider_y - 30 + shadow_offset))
        screen.blit(volume_shadow, volume_shadow_rect)
        screen.blit(volume_text, volume_text_rect)
        
        # Render button texts with shadows
        resume_shadow = font.render("RESUME", True, shadow_color)
        resume_shadow_rect = resume_shadow.get_rect(center=(WIDTH // 2 + shadow_offset, HEIGHT // 2 + 20 + shadow_offset))
        play_again_shadow = font.render("PLAY AGAIN", True, shadow_color)
        play_again_shadow_rect = play_again_shadow.get_rect(center=(WIDTH // 2 + shadow_offset, HEIGHT // 2 + 60 + shadow_offset))
        home_shadow = font.render("EXIT", True, shadow_color)
        home_shadow_rect = home_shadow.get_rect(center=(WIDTH // 2 + shadow_offset, HEIGHT // 2 + 100 + shadow_offset))
        screen.blit(resume_shadow, resume_shadow_rect)
        screen.blit(resume_text, resume_rect)
        screen.blit(play_again_shadow, play_again_shadow_rect)
        screen.blit(play_again_text, play_again_rect)
        screen.blit(home_shadow, home_shadow_rect)
        screen.blit(home_text, home_rect)

        # Blinking arrow and remaining code
        mouse_pos = pygame.mouse.get_pos()
        if arrow_visible:
            if resume_rect.collidepoint(mouse_pos):
                draw_arrow(resume_rect.left - 15, resume_rect.centery)
            if play_again_rect.collidepoint(mouse_pos):
                draw_arrow(play_again_rect.left - 15, play_again_rect.centery)
            if home_rect.collidepoint(mouse_pos):
                draw_arrow(home_rect.left - 15, home_rect.centery)

        pygame.display.update()
        
        # Handle events for in-game settings
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Start dragging slider if clicked on slider handle
                    if (slider_handle_x - slider_handle_radius <= event.pos[0] <= slider_handle_x + slider_handle_radius and
                        slider_y - slider_handle_radius <= event.pos[1] <= slider_y + slider_height + slider_handle_radius):
                        is_dragging = True
                    # Click on RESUME: exit settings overlay
                    if resume_rect.collidepoint(event.pos):
                        button_sound.play()
                        return
                    # Click on PLAY AGAIN: reset the game state
                    if play_again_rect.collidepoint(event.pos):
                        button_sound.play()
                        # Reset game state for PLAY AGAIN:
                        global score, level, player_health, player2_health, player_x, player_y, player2_x, player2_y, player_frame_index, player2_frame_index, last_animation_time, last_player2_animation_time, bullets, alien1_bullets, enemy_direction, enemy_speed, alien_formation, player1_alive, player2_alive, alien4_x, alien4_y
                        score = 0
                        level = 1
                        player_health = 3
                        player2_health = 3
                        player_x = WIDTH // 2 - 35
                        player_y = HEIGHT - 120
                        player2_x = WIDTH // 2 + 100
                        player2_y = HEIGHT - 120
                        player_frame_index = 0
                        player2_frame_index = 0
                        last_animation_time = pygame.time.get_ticks()
                        last_player2_animation_time = pygame.time.get_ticks()
                        bullets.clear()
                        alien1_bullets.clear()
                        enemy_direction = 1
                        # Stop pixel music and switch to SoundM for player selection
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load("Graphics/Music/SoundM.mp3")
                        pygame.mixer.music.play(-1)
                        # Go to player selection
                        start_mode_screen()
                        # Only ask for difficulty ONCE, then continue to gameplay
                        enemy_speed, _ = difficulty_selection()
                        # Switch to gameplay music and start game loop directly
                        pygame.mixer.music.load("Graphics/Music/pixel.mp3")
                        pygame.mixer.music.set_volume(0.5)
                        pygame.mixer.music.play(-1)
                        alien_formation = create_alien_formation(enemy_speed)
                        player1_alive = True
                        player2_alive = True
                        alien4_x = 0
                        # --- Reset gameplay background to level 1 ---
                        bg_frames = [pygame.image.load(f"Graphics/GAMEBACK/q{i}.png") for i in range(1, 33)]
                        bg_frames = [pygame.transform.scale(frame, (WIDTH, HEIGHT)) for frame in bg_frames]
                        bg_frame_index = 0
                        bg_animation_speed = 100
                        last_bg_animation_time = pygame.time.get_ticks()
                        # Main game loop resumes automatically after this function returns
                        return
                    # Change HOME button to EXIT:
                    if home_rect.collidepoint(event.pos):
                        button_sound.play()
                        pygame.quit()
                        exit()
            if event.type == pygame.MOUSEBUTTONUP:
                is_dragging = False
            if event.type == pygame.MOUSEMOTION and is_dragging:
                mouse_x = event.pos[0]
                slider_handle_x = max(slider_x, min(mouse_x, slider_x + slider_width))
                volume = (slider_handle_x - slider_x) / slider_width
                pygame.mixer.music.set_volume(volume)
        
        clock.tick(30)

# Load Alien3 Animation Frames for the top group (2 rows)
alien3_frames = [pygame.image.load(f"Graphics/alien3/b{i}.png") for i in range(1,7)]
alien3_frames = [pygame.transform.scale(frame, (50, 45)) for frame in alien3_frames]

# Alien3 Animation Variables
alien3_frame_index = 0
alien3_animation_speed = 100  # Milliseconds per frame
last_alien3_animation_time = pygame.time.get_ticks()

def draw_alien3(x, y):
    global alien3_frame_index, last_alien3_animation_time
    current_time = pygame.time.get_ticks()
    if current_time - last_alien3_animation_time > alien3_animation_speed:
        alien3_frame_index = (alien3_frame_index + 1) % len(alien3_frames)
        last_alien3_animation_time = current_time
    screen.blit(alien3_frames[alien3_frame_index], (x, y))

# Load Alien1 Animation Frames (from folder "alien1", images x1 to x12)
alien1_frames = [pygame.image.load(f"Graphics/alien1/x{i}.png") for i in range(1, 13)]
alien1_frames = [pygame.transform.scale(frame, (50, 40)) for frame in alien1_frames]

# Alien1 Animation Variables
alien1_frame_index = 0
alien1_animation_speed = 100  # Milliseconds per frame
last_alien1_animation_time = pygame.time.get_ticks()

def draw_alien1(x, y):
    global alien1_frame_index, last_alien1_animation_time
    current_time = pygame.time.get_ticks()
    if current_time - last_alien1_animation_time > alien1_animation_speed:
        alien1_frame_index = (alien1_frame_index + 1) % len(alien1_frames)
        last_alien1_animation_time = current_time
    screen.blit(alien1_frames[alien1_frame_index], (x, y))

# Load Alien1 Laser (bullet) Animation Frames from folder "laser" (images l1 to l5)
alien1_laser_frames = [pygame.image.load(f"Graphics/laser/l{i}.png") for i in range(1, 6)]
alien1_laser_frames = [pygame.transform.scale(frame, (40, 40)) for frame in alien1_laser_frames]

# Alien1 Laser Animation Variables
alien1_laser_frame_index = 0
alien1_laser_animation_speed = 100  # Milliseconds per frame
last_alien1_laser_animation_time = pygame.time.get_ticks()

# Alien1 Laser Bullet Variables
alien1_bullets = []           # List to store alien1 laser bullets
alien1_shot_cooldown = 3000   # Cooldown period in milliseconds between shots by an alien1
last_alien1_shot_time = pygame.time.get_ticks()
alien1_bullet_speed = 5       # Speed of alien1 laser bullets

enemy_direction = 1  # 1 for right, -1 for left

# Load Player 2 Animation Frames
player2_frames = [
    pygame.image.load("Graphics/player2/st1.png"),
    pygame.image.load("Graphics/player2/st2.png"),
    pygame.image.load("Graphics/player2/st3.png"),
    pygame.image.load("Graphics/player2/st4.png"),
]
player2_frames = [pygame.transform.scale(frame, (80, 80)) for frame in player2_frames]

# Player 2 Variables
player2_frame_index = 0
player2_animation_speed = 100  # Milliseconds per frame
last_player2_animation_time = pygame.time.get_ticks()
player2_x = WIDTH // 2 + 100  # Starting position for Player 2
player2_y = HEIGHT - 120
player2_speed = 10
bullets2 = []  # Separate bullet list for Player 2

# Load Heart Animation Frames for Player Health
heart_frames = [pygame.image.load(f"Graphics/player1/set{i}.png") for i in range(1, 5)]
heart_frames = [pygame.transform.scale(frame, (50, 50)) for frame in heart_frames]  # Adjust size as needed

heart_frame_index = 0
heart_animation_speed = 150  # Milliseconds per frame change for hearts
last_heart_animation_time = pygame.time.get_ticks()

player_health = 3  # Starting health (3 hearts)
# New global variables to track alive status
player1_alive = True
player2_alive = True  # Only used in two-player mode

# Load Heart Animation Frames for Player 2 Health
player2_heart_frames = [pygame.image.load(f"Graphics/player2/st{i}.png") for i in range(1, 5)]
player2_heart_frames = [pygame.transform.scale(frame, (50, 50)) for frame in player2_heart_frames]  # Adjust size as needed

player2_heart_frame_index = 0
player2_heart_animation_speed = 150  # Milliseconds per frame change for hearts
last_player2_heart_animation_time = pygame.time.get_ticks()

player2_health = 3  # Starting health for Player 2 (3 hearts)

# ----- New: Add Alien4 global variables -----
alien4_frames = [pygame.image.load(f"Graphics/alien4/br{i}.png") for i in range(1,7)]
alien4_frames = [pygame.transform.scale(frame, (50, 40)) for frame in alien4_frames]
alien4_frame_index = 0
alien4_animation_speed = 100  # milliseconds per frame
last_alien4_animation_time = pygame.time.get_ticks()
alien4_speed = 4  # constant speed (do not change)
alien4_x = 0
alien4_y = 65  # changed: fixed y to position alien4 on top of alien1
# -------------------------------------------

def display_health():
    global heart_frame_index, last_heart_animation_time, player2_heart_frame_index, last_player2_heart_animation_time
    current_time = pygame.time.get_ticks()

    # Animate Player 1 hearts
    if current_time - last_heart_animation_time > heart_animation_speed:
        heart_frame_index = (heart_frame_index + 1) % len(heart_frames)
        last_heart_animation_time = current_time

    # Animate Player 2 hearts only if two_player mode is active
    if two_player:
        if current_time - last_player2_heart_animation_time > player2_heart_animation_speed:
            player2_heart_frame_index = (player2_heart_frame_index + 1) % len(player2_heart_frames)
            last_player2_heart_animation_time = current_time

    # Draw Player 1 hearts in the top-right corner
    heart_width = 40  # Should match the heart image width
    for i in range(player_health):
        x = WIDTH - (heart_width + 10) * (i + 1)
        y = 10
        screen.blit(heart_frames[heart_frame_index], (x, y))

    # Draw Player 2 hearts on the right side only in two_player mode
    if two_player:
        for i in range(player2_health):
            x = WIDTH - (heart_width + 10) * (i + 1)
            y = 60  # Adjusted vertical position
            screen.blit(player2_heart_frames[player2_heart_frame_index], (x, y))

# ----- New: Function to draw alien4 -----
def draw_alien4(x, y):
    global alien4_frame_index, last_alien4_animation_time
    current_time = pygame.time.get_ticks()
    if current_time - last_alien4_animation_time > alien4_animation_speed:
        alien4_frame_index = (alien4_frame_index + 1) % len(alien4_frames)
        last_alien4_animation_time = current_time
    screen.blit(alien4_frames[alien4_frame_index], (x, y))
# -----------------------------------------

# Update the draw_player2 function
def draw_player2(x, y):
    global player2_frame_index, last_player2_animation_time
    current_time = pygame.time.get_ticks()
    if current_time - last_player2_animation_time > player2_animation_speed:
        player2_frame_index = (player2_frame_index + 1) % len(player2_frames)
        last_player2_animation_time = current_time
    screen.blit(player2_frames[player2_frame_index], (x, y))

def start_mode_screen():
    global two_player
    mode_frames = [pygame.image.load(f"Graphics/BackG/b{i}.png") for i in range(1,47)]
    mode_frames = [pygame.transform.scale(frame, (WIDTH, HEIGHT)) for frame in mode_frames]
    mode_bg_index = 0
    mode_anim_speed = 100
    last_mode_time = pygame.time.get_ticks()
    arrow_visible = True
    arrow_blink_speed = 500
    last_arrow_blink_time = pygame.time.get_ticks()
    shadow_color = (50, 50, 50)
    shadow_offset = 2
    
    while True:
        current_time = pygame.time.get_ticks()
        if current_time - last_mode_time > mode_anim_speed:
            mode_bg_index = (mode_bg_index + 1) % len(mode_frames)
            last_mode_time = current_time
        if current_time - last_arrow_blink_time > arrow_blink_speed:
            arrow_visible = not arrow_visible
            last_arrow_blink_time = current_time
        
        screen.blit(mode_frames[mode_bg_index], (0,0))
        
        # --- SHADOW: "Player selections" title ---
        selection_font = pygame.font.Font("Graphics/Font/monogram.ttf", 72)
        selection_title = selection_font.render("Player selections", True, WHITE)
        selection_shadow = selection_font.render("Player selections", True, shadow_color)
        selection_title_rect = selection_title.get_rect(center=(WIDTH//2, 290))
        selection_shadow_rect = selection_shadow.get_rect(center=(WIDTH//2 + shadow_offset, 290 + shadow_offset))

        # Simulate bold by blitting the shadow and title multiple times with slight offsets
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            screen.blit(selection_shadow, selection_shadow_rect.move(dx, dy))
        screen.blit(selection_shadow, selection_shadow_rect)  # Center shadow
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            screen.blit(selection_title, selection_title_rect.move(dx, dy))
        screen.blit(selection_title, selection_title_rect)    # Center text

        mouse_pos = pygame.mouse.get_pos()
        p1_text = "PLAYER 1"
        p2_text = "PLAYER 2"
        # Use a slightly smaller font for PLAYER 1 and PLAYER 2 (size 32)
        player_label_font = pygame.font.Font("Graphics/Font/monogram.ttf", 32)
        # --- SHADOW: PLAYER 1 ---
        p1_render = player_label_font.render(p1_text, True, WHITE)
        p1_shadow = player_label_font.render(p1_text, True, shadow_color)
        p1_rect = p1_render.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
        p1_shadow_rect = p1_shadow.get_rect(center=(WIDTH//2 + shadow_offset, HEIGHT//2 - 20 + shadow_offset))
        screen.blit(p1_shadow, p1_shadow_rect)
        screen.blit(p1_render, p1_rect)
        # --- SHADOW: PLAYER 2 ---
        p2_render = player_label_font.render(p2_text, True, WHITE)
        p2_shadow = player_label_font.render(p2_text, True, shadow_color)
        p2_rect = p2_render.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
        p2_shadow_rect = p2_shadow.get_rect(center=(WIDTH//2 + shadow_offset, HEIGHT//2 + 20 + shadow_offset))
        screen.blit(p2_shadow, p2_shadow_rect)
        screen.blit(p2_render, p2_rect)

        p1_hover = p1_rect.collidepoint(mouse_pos)
        p2_hover = p2_rect.collidepoint(mouse_pos)
        if arrow_visible:
            if p1_hover:
                draw_arrow(p1_rect.left - 15, p1_rect.centery)
            if p2_hover:
                draw_arrow(p2_rect.left - 15, p2_rect.centery)

        # --- SHADOW: Instructions Section ---
        manual_font = pygame.font.Font("Graphics/Font/monogram.ttf", 28)
        bullet_y = HEIGHT - 220
        # Label "BUTTONS:"
        p1_label_shadow = manual_font.render("BUTTONS:", True, shadow_color)
        p1_label = manual_font.render("BUTTONS:", True, WHITE)
        screen.blit(p1_label_shadow, (50 + shadow_offset, bullet_y - 40 + shadow_offset))
        screen.blit(p1_label, (50, bullet_y - 40))
        # PLAYER 1 label
        p1_shoot_shadow = manual_font.render("PLAYER 1", True, shadow_color)
        p1_shoot = manual_font.render("PLAYER 1", True, WHITE)
        screen.blit(p1_shoot_shadow, (90 + shadow_offset, bullet_y + shadow_offset))
        screen.blit(p1_shoot, (90, bullet_y))
        # Move Left
        move_left_img = pygame.image.load("Graphics/arrow/pf.png")
        move_left_img = pygame.transform.scale(move_left_img, (30, 30))
        screen.blit(move_left_img, (80, bullet_y + 36))
        p1_left_shadow = manual_font.render("Move Left", True, shadow_color)
        p1_left = manual_font.render("Move Left", True, WHITE)
        screen.blit(p1_left_shadow, (120 + shadow_offset, bullet_y + 38 + shadow_offset))
        screen.blit(p1_left, (120, bullet_y + 38))
        bullet_y += 40
        # Move Right
        move_right_img = pygame.image.load("Graphics/arrow/pr.png")
        move_right_img = pygame.transform.scale(move_right_img, (30, 30))
        screen.blit(move_right_img, (80, bullet_y+ 36))
        p1_right_shadow = manual_font.render("Move Right", True, shadow_color)
        p1_right = manual_font.render("Move Right", True, WHITE)
        screen.blit(p1_right_shadow, (120 + shadow_offset, bullet_y + 40 + shadow_offset))
        screen.blit(p1_right, (120, bullet_y + 40))
        bullet_y += 40
        # Spacebar: Shoot
        p1_shoot_shadow2 = manual_font.render("Spacebar: Shoot", True, shadow_color)
        p1_shoot2 = manual_font.render("Spacebar: Shoot", True, WHITE)
        screen.blit(p1_shoot_shadow2, (90 + shadow_offset, bullet_y + 40 + shadow_offset))
        screen.blit(p1_shoot2, (90, bullet_y + 40))

        # PLAYER 2 instructions (right side)
        p2_offset = 600
        bullet_y = HEIGHT - 220
        p2_title_shadow = manual_font.render("PLAYER 2", True, shadow_color)
        p2_title = manual_font.render("PLAYER 2", True, WHITE)
        screen.blit(p2_title_shadow, (p2_offset + shadow_offset, bullet_y + shadow_offset))
        screen.blit(p2_title, (p2_offset, bullet_y))
        bullet_y += 40
        p2_left_shadow = manual_font.render("A: Move Left", True, shadow_color)
        p2_left = manual_font.render("A: Move Left", True, WHITE)
        screen.blit(p2_left_shadow, (p2_offset + shadow_offset, bullet_y + shadow_offset))
        screen.blit(p2_left, (p2_offset, bullet_y))
        bullet_y += 40
        p2_right_shadow = manual_font.render("D: Move Right", True, shadow_color)
        p2_right = manual_font.render("D: Move Right", True, WHITE)
        screen.blit(p2_right_shadow, (p2_offset + shadow_offset, bullet_y + shadow_offset))
        screen.blit(p2_right, (p2_offset, bullet_y))
        bullet_y += 40
        p2_shoot_shadow = manual_font.render("I: Shoot", True, shadow_color)
        p2_shoot = manual_font.render("I: Shoot", True, WHITE)
        screen.blit(p2_shoot_shadow, (p2_offset + shadow_offset, bullet_y + shadow_offset))
        screen.blit(p2_shoot, (p2_offset, bullet_y))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    button_sound.play()
                    start_game_screen()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if p1_hover:
                    button_sound.play()
                    two_player = False
                    return
                if p2_hover:
                    button_sound.play()
                    two_player = True
                    return

# Insert welcome screen call before starting the game
welcome_screen()
# Call the start game screen before difficulty selection
start_game_screen()
start_mode_screen()  # now defined above and callable

# --- Only ask for difficulty ONCE and then enter the main game loop ---
enemy_speed, _ = difficulty_selection()  # then choose difficulty

# Now load gameplay background music with a fixed volume
pygame.mixer.music.load("Graphics/Music/pixel.mp3")
pygame.mixer.music.set_volume(0.5)  # Fixed gameplay music volume
pygame.mixer.music.play(-1)

alien_formation = create_alien_formation(enemy_speed)

# Load Background Animation Frames for gameplay from GAMEBACK folder (q1.png to q32.png)
bg_frames = [pygame.image.load(f"Graphics/GAMEBACK/q{i}.png") for i in range(1, 33)]
bg_frames = [pygame.transform.scale(frame, (WIDTH, HEIGHT)) for frame in bg_frames]
bg_animation_speed = 100  # Milliseconds per frame
last_bg_animation_time = pygame.time.get_ticks()
bg_frame_index = 0

# Game Loop
running = True

def draw_player(x, y):
    global player_frame_index, last_animation_time

    # Handle Animation Timing
    current_time = pygame.time.get_ticks()
    if current_time - last_animation_time > animation_speed:
        player_frame_index = (player_frame_index + 1) % len(player_frames)
        last_animation_time = current_time

    # Draw Current Frame
    screen.blit(player_frames[player_frame_index], (x, y))

def draw_enemy(x, y):
    global enemy_frame_index, last_enemy_animation_time
    current_time = pygame.time.get_ticks()
    if current_time - last_enemy_animation_time > enemy_animation_speed:
        enemy_frame_index = (enemy_frame_index + 1) % len(enemy_frames)
        last_enemy_animation_time = current_time
    screen.blit(enemy_frames[enemy_frame_index], (x, y))

def draw_enemy2(x, y):
    global enemy2_frame_index, last_enemy2_animation_time
    current_time = pygame.time.get_ticks()
    if current_time - last_enemy2_animation_time > enemy2_animation_speed:
        enemy2_frame_index = (enemy2_frame_index + 1) % len(enemy2_frames)
        last_enemy2_animation_time = current_time
    screen.blit(enemy2_frames[enemy2_frame_index], (x, y))

def fire_bullet(x, y):
    global can_shoot, last_shot_time_p1
    if player1_alive:  # Ensure player 1 can only shoot if alive
        current_time = pygame.time.get_ticks()
        if can_shoot and current_time - last_shot_time_p1 > shoot_cooldown:
            bullet_x = x + (79 // 2) - (20 // 2)
            bullet_y = y - 40  # moved a little on the top
            bullets.append([bullet_x, bullet_y])
            last_shot_time_p1 = current_time
            laser_shot.play()  # Play the laser shot sound

def fire_bullet2(x, y):
    global bullets2, last_shot_time_p2
    if player2_alive:  # Ensure player 2 can only shoot if alive
        current_time = pygame.time.get_ticks()
        if current_time - last_shot_time_p2 > shoot_cooldown:
            bullet_x = x + (79 // 2) - (20 // 2)
            bullet_y = y - 40  # moved a little on the top
            bullets2.append([bullet_x, bullet_y])
            last_shot_time_p2 = current_time
            laser_shot.play()

def is_collision(enemy_x, enemy_y, bullet_x, bullet_y):
    distance = math.sqrt((enemy_x - bullet_x) ** 2 + (enemy_y - bullet_y) ** 2)
    return distance < 27

def is_player_collision(player_x, player_y, enemy_x, enemy_y):
    # Check if the distance between the player and the enemy is less than a threshold
    distance = math.sqrt((player_x - enemy_x) ** 2 + (player_y - enemy_y) ** 2)
    return distance < 50  # Adjust the threshold based on the size of the player and enemy

def game_over():
    global highest_score, score, player_health, player2_health, player_x, player_y, player2_x, player2_y, bullets, alien1_bullets, alien_formation, enemy_speed, level, player1_alive, player2_alive, alien4_x
    # Update the highest score if needed
    if score > highest_score:
        highest_score = score

    # Load Game Over Background Frames from folder "BackG5" (images gg1.png to gg12.png)
    game_over_bg_frames = [pygame.image.load(f"Graphics/GameOver/sa{i}.png") for i in range(1, 113)]
    game_over_bg_frames = [pygame.transform.scale(frame, (WIDTH, HEIGHT)) for frame in game_over_bg_frames]
    bg_frame_index = 0
    bg_animation_speed = 100  # Milliseconds per frame
    last_bg_animation_time = pygame.time.get_ticks()

    # Create a large, bold font for the "GAME OVER" text
    game_over_font = pygame.font.Font("Graphics/Font/monogram.ttf", 120)


    # Set up arrow blinking for button animation
    arrow_blink_speed = 500  # milliseconds
    last_arrow_blink_time = pygame.time.get_ticks()
    arrow_visible = True

    while True:
        current_time = pygame.time.get_ticks()
        # Animate the background frames
        if current_time - last_bg_animation_time > bg_animation_speed:
            bg_frame_index = (bg_frame_index + 1) % len(game_over_bg_frames)
            last_bg_animation_time = current_time

        # Update arrow blinking
        if current_time - last_arrow_blink_time > arrow_blink_speed:
            arrow_visible = not arrow_visible
            last_arrow_blink_time = current_time

        # Draw the animated background
        screen.blit(game_over_bg_frames[bg_frame_index], (0, 0))
        # --- Darken the game over screen ---
        dark_overlay = pygame.Surface((WIDTH, HEIGHT))
        dark_overlay.fill((0, 0, 0))
        dark_overlay.set_alpha(180)
        screen.blit(dark_overlay, (0, 0))

        # --- Render Game Over Text (centered) with shadow ---
        shadow_offset = 2
        shadow_color = (50, 50, 50)
        game_over_shadow = game_over_font.render("GAME OVER", True, shadow_color)
        game_over_shadow_rect = game_over_shadow.get_rect(center=(WIDTH // 2 + shadow_offset, HEIGHT // 2 - 150 + shadow_offset))
        game_over_text = game_over_font.render("GAME OVER", True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
        screen.blit(game_over_shadow, game_over_shadow_rect)
        screen.blit(game_over_text, game_over_rect)

        # --- Render Score Information with shadow ---
        score_shadow = font.render(f"Your Score: {score}", True, shadow_color)
        score_shadow_rect = score_shadow.get_rect(center=(WIDTH // 2 + shadow_offset, HEIGHT // 2 - 50 + shadow_offset))
        score_text = font.render(f"Your Score: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(score_shadow, score_shadow_rect)
        screen.blit(score_text, score_rect)

        high_score_shadow = font.render(f"Highest Score: {highest_score}", True, shadow_color)
        high_score_shadow_rect = high_score_shadow.get_rect(center=(WIDTH // 2 + shadow_offset, HEIGHT // 2 + shadow_offset))
        high_score_text = font.render(f"Highest Score: {highest_score}", True, WHITE)
        high_score_rect = high_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(high_score_shadow, high_score_shadow_rect)
        screen.blit(high_score_text, high_score_rect)

        # Define button centers with PLAY AGAIN, HOME, and EXIT
        play_again_center = (WIDTH // 2, HEIGHT // 2 + 60)
        home_center = (WIDTH // 2, HEIGHT // 2 + 100)  # new HOME button center
        exit_center = (WIDTH // 2, HEIGHT // 2 + 140)

        # Get current mouse position and determine hover state
        mouse_pos = pygame.mouse.get_pos()
        play_again_rect = font.render("PLAY AGAIN", True, WHITE).get_rect(center=play_again_center)
        home_rect = font.render("HOME", True, WHITE).get_rect(center=home_center)
        exit_rect = font.render("EXIT", True, WHITE).get_rect(center=exit_center)
        play_again_hover = play_again_rect.collidepoint(mouse_pos)
        home_hover = home_rect.collidepoint(mouse_pos)
        exit_hover = exit_rect.collidepoint(mouse_pos)

        # Draw the buttons with animation using draw_button (which renders a shadow and changes color when hovered)
        draw_button("PLAY AGAIN", play_again_center[0], play_again_center[1], WHITE, play_again_hover)
        draw_button("HOME", home_center[0], home_center[1], WHITE, home_hover)
        draw_button("EXIT", exit_center[0], exit_center[1], WHITE, exit_hover)
        if arrow_visible:
            if play_again_hover:
                draw_arrow(play_again_rect.left - 15, play_again_rect.centery)
            if home_hover:
                draw_arrow(home_rect.left - 15, home_rect.centery)
            if exit_hover:
                draw_arrow(exit_rect.left - 15, exit_rect.centery)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_hover:
                    # Reset game state for PLAY AGAIN
                    score = 0
                    level = 1
                    player_health = 3
                    player2_health = 3
                    player_x = WIDTH // 2 - 35
                    player_y = HEIGHT - 120
                    player2_x = WIDTH // 2 + 100
                    player2_y = HEIGHT - 120
                    player_frame_index = 0
                   
                    player2_frame_index =  0
                    last_animation_time = pygame.time.get_ticks()
                    last_player2_animation_time = pygame.time.get_ticks()
                    bullets.clear()
                    alien1_bullets.clear()
                    enemy_direction = 1
                    # Stop pixel music and switch to SoundM for player selection
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load("Graphics/Music/SoundM.mp3")
                    pygame.mixer.music.play(-1)
                    # Go to player selection
                    start_mode_screen()
                    # Only ask for difficulty ONCE, then continue to gameplay
                    global enemy_speed
                    enemy_speed, _ = difficulty_selection()
                    # Switch to gameplay music and start game loop directly
                    pygame.mixer.music.load("Graphics/Music/pixel.mp3")
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.play(-1)
                    alien_formation = create_alien_formation(enemy_speed)
                    player1_alive = True
                    player2_alive = True
                    alien4_x = 0
                    # --- Reset gameplay background to level 1 ---
                    bg_frames = [pygame.image.load(f"Graphics/GAMEBACK/q{i}.png") for i in range(1, 33)]
                    bg_frames = [pygame.transform.scale(frame, (WIDTH, HEIGHT)) for frame in bg_frames]
                    bg_frame_index = 0
                    bg_animation_speed = 100
                    last_bg_animation_time = pygame.time.get_ticks()
                    # Main game loop resumes automatically after this function returns
                    return
                if home_hover:
                    # Reset game to home
                    start_game_screen()
                    score = 0
                    level = 1
                    player_health = 3
                    player_x = WIDTH // 2 - 35
                    player_y = HEIGHT - 120
                    bullets.clear()
                    alien1_bullets.clear()
                    enemy_direction = 1  # Reset enemy movement direction
                    # Prompt player selection so the player(s) can choose single or two-player mode
                    start_mode_screen()
                    enemy_speed, _ = difficulty_selection()
                    alien_formation = create_alien_formation(enemy_speed)
                    player1_alive = True
                    player2_alive = True
                    alien4_x = 0
                    return  # Exit game_win() and resume main game loop
                if exit_hover:
                    pygame.quit()
                    exit()

def game_win():
    global highest_score, score, player_health, player2_health, player_x, player_y, player2_x, player2_y, alien_formation, enemy_speed, level, bullets, alien1_bullets, alien4_x, bg_frames, bg_frame_index, last_bg_animation_time, bg_animation_speed
    if score > highest_score:
        highest_score = score
    win_bg_frames = [pygame.image.load(f"Graphics/BackW/w{i}.png") for i in range(1,46)]
    win_bg_frames = [pygame.transform.scale(frame, (WIDTH, HEIGHT)) for frame in win_bg_frames]
    bg_frame_index = 0
    bg_animation_speed = 100  # Milliseconds per frame
    last_bg_animation_time = pygame.time.get_ticks()

    win_font = pygame.font.Font("Graphics/Font/monogram.ttf", 120)
    arrow_blink_speed = 500  # milliseconds
    last_arrow_blink_time = pygame.time.get_ticks()
    arrow_visible = True

    while True:
        current_time = pygame.time.get_ticks()
        if current_time - last_bg_animation_time > bg_animation_speed:
            bg_frame_index = (bg_frame_index + 1) % len(win_bg_frames)
            last_bg_animation_time = current_time
        if current_time - last_arrow_blink_time > arrow_blink_speed:
            arrow_visible = not arrow_visible
            last_arrow_blink_time = current_time

        screen.blit(win_bg_frames[bg_frame_index], (0, 0))

        win_text = win_font.render("YOU WIN!", True, WHITE)
        win_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
        screen.blit(win_text, win_rect)

        score_text = font.render(f"Your Score: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(score_text, score_rect)
        high_score_text = font.render(f"Highest Score: {highest_score}", True, WHITE)
        high_score_rect = high_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(high_score_text, high_score_rect)

        # Updated buttons: add HOME button between PLAY AGAIN and EXIT
        play_again_center = (WIDTH // 2, HEIGHT // 2 + 60)
        home_center = (WIDTH // 2, HEIGHT // 2 + 100)
        exit_center = (WIDTH // 2, HEIGHT // 2 + 140)
        mouse_pos = pygame.mouse.get_pos()
        play_again_rect = font.render("PLAY AGAIN", True, WHITE).get_rect(center=play_again_center)
        home_rect = font.render("HOME", True, WHITE).get_rect(center=home_center)
        exit_rect = font.render("EXIT", True, WHITE).get_rect(center=exit_center)
        play_again_hover = play_again_rect.collidepoint(mouse_pos)
        home_hover = home_rect.collidepoint(mouse_pos)
        exit_hover = exit_rect.collidepoint(mouse_pos)
        draw_button("PLAY AGAIN", play_again_center[0], play_again_center[1], WHITE, play_again_hover)
        draw_button("HOME", home_center[0], home_center[1], WHITE, home_hover)
        draw_button("EXIT", exit_center[0], exit_center[1], WHITE, exit_hover)
        if arrow_visible:
            if play_again_hover:
                draw_arrow(play_again_rect.left - 15, play_again_rect.centery)
            if home_hover:
                draw_arrow(home_rect.left - 15, home_rect.centery)
            if exit_hover:
                draw_arrow(exit_rect.left - 15, exit_rect.centery)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_hover:
                    # Reset game state for PLAY AGAIN
                    score = 0
                    level = 1
                    player_health = 3
                    player2_health = 3
                    player_x = WIDTH // 2 - 35
                    player_y = HEIGHT - 120
                    player2_x = WIDTH // 2 + 100
                    player2_y = HEIGHT - 120
                    player_frame_index = 0
                    player2_frame_index = 0
                    last_animation_time = pygame.time.get_ticks()
                    last_player2_animation_time = pygame.time.get_ticks()
                    bullets.clear()
                    alien1_bullets.clear()
                    enemy_direction = 1
                    # Stop pixel music and switch to SoundM for player selection
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load("Graphics/Music/SoundM.mp3")
                    pygame.mixer.music.play(-1)
                    # Go to player selection
                    start_mode_screen()
                    # Only ask for difficulty ONCE, then continue to gameplay
                    global enemy_speed
                    enemy_speed, _ = difficulty_selection()
                    # Switch to gameplay music and start game loop directly
                    pygame.mixer.music.load("Graphics/Music/pixel.mp3")
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.play(-1)
                    alien_formation = create_alien_formation(enemy_speed)
                    player1_alive = True
                    player2_alive = True
                    alien4_x = 0
                    # --- Reset gameplay background to level 1 ---
                    bg_frames = [pygame.image.load(f"Graphics/GAMEBACK/q{i}.png") for i in range(1, 33)]
                    bg_frames = [pygame.transform.scale(frame, (WIDTH, HEIGHT)) for frame in bg_frames]
                    bg_frame_index = 0
                    bg_animation_speed = 100
                    last_bg_animation_time = pygame.time.get_ticks()
                    # Main game loop resumes automatically after this function returns
                    return
                if home_hover:
                    # Reset game to home
                    start_game_screen()
                    score = 0
                    level = 1
                    player_health = 3
                    player_x = WIDTH // 2 - 35
                    player_y = HEIGHT - 120
                    bullets.clear()
                    alien1_bullets.clear()
                    enemy_direction = 1  # Reset enemy movement direction
                    # Prompt player selection so the player(s) can choose single or two-player mode
                    start_mode_screen()
                    enemy_speed, _ = difficulty_selection()
                    alien_formation = create_alien_formation(enemy_speed)
                    player1_alive = True
                    player2_alive = True
                    alien4_x = 0
                    return  # Exit game_win() and resume main game loop
                if exit_hover:
                    pygame.quit()
                    exit()

def increase_difficulty():
    global enemy_speed, enemies, level, alien1_shot_cooldown
    if level >= 5:
        return
    enemy_speed += 1
    level += 1
    # For level 1 and 2 use 4 rows; for level 3, 4 and 5 use 5 rows.
    rows = 4 if level < 3 else 5
    cols = 11
    enemies = create_enemies(rows, cols, enemy_speed)
    update_background_for_level(level)
    # Make alien1 shoot faster as level increases (minimum 600ms)
    alien1_shot_cooldown = max(600, 3000 - (level - 1) * 600)

def display_score_and_level():
    # Use a moderately small font for level and score (size 28)
    small_font = pygame.font.Font("Graphics/Font/monogram.ttf", 28)
    shadow_color = (50, 50, 50)  # Dark gray for shadow
    shadow_offset = 2  # Offset for the shadow

    # Render Score Text with shadow
    score_shadow_text = small_font.render(f"Score: {score}", True, shadow_color)
    score_shadow_rect = score_shadow_text.get_rect(center=(WIDTH // 2 + shadow_offset, 20 + shadow_offset))
    screen.blit(score_shadow_text, score_shadow_rect)
    score_text = small_font.render(f"Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(WIDTH // 2, 20))
    screen.blit(score_text, score_rect)

    # Render Level Text with shadow
    level_shadow_text = small_font.render(f"Level: {level}", True, shadow_color)
    screen.blit(level_shadow_text, (10 + shadow_offset, 10 + shadow_offset))
    level_text = small_font.render(f"Level: {level}", True, WHITE)
    screen.blit(level_text, (10, 10))

def update_background_for_level(new_level):
    global bg_frames, bg_frame_index, last_bg_animation_time, bg_animation_speed
    # Choose the correct background set based on the level.
    if new_level == 1:
        frames = [pygame.image.load(f"Graphics/GAMEBACK/q{i}.png") for i in range(1, 33)]
    elif new_level == 2:
        frames = [pygame.image.load(f"Graphics/BackG9/sw{i}.png") for i in range(1, 53)]
    elif new_level == 3:
        frames = [pygame.image.load(f"Graphics/BackG6/aw{i}.png") for i in range(1, 25)]
    elif new_level == 4:
        frames = [pygame.image.load(f"Graphics/BackG11/sa{i}.png") for i in range(1, 43)]
    elif new_level == 5:
        frames = [pygame.image.load(f"Graphics/BackG9/xq{i}.png") for i in range(1, 41)]
    
    # Scale frames to fit the screen.
    new_frames = [pygame.transform.scale(frame, (WIDTH, HEIGHT)) for frame in frames]
    
    # Fade transition: gradually overlay the new background
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill(BLACK)
    for alpha in range(0, 156, 5):  # Smaller step for smoother fade
        fade_surface.set_alpha(alpha)
        screen.blit(new_frames[0], (0, 0))
        screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(20)  # Adjust delay as needed for smoother animation
    
    # Update the global background variables.
    bg_frames = new_frames
    bg_frame_index = 0
    last_bg_animation_time = pygame.time.get_ticks()

# Main game loop modifications for two–player mode
while running:
    current_time = pygame.time.get_ticks()
    if current_time - last_bg_animation_time > bg_animation_speed:
        bg_frame_index = (bg_frame_index + 1) % len(bg_frames)
        last_bg_animation_time = current_time

    screen.blit(bg_frames[bg_frame_index], (0,0))
    dark_overlay = pygame.Surface((WIDTH, HEIGHT))
    dark_overlay.fill((0,0,0))
    dark_overlay.set_alpha(150)
    screen.blit(dark_overlay, (0,0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                button_sound.play()
                in_game_settings_screen()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                button_sound.play()
                in_game_settings_screen()
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 70:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH - 190:
        player_x += player_speed
    if player1_alive and keys[pygame.K_RETURN]:
        fire_bullet(player_x, player_y)
    
    # New: Player 2 controls if two_player is True:
    if two_player:
        if keys[pygame.K_a] and player2_x > 70:
            player2_x -= player2_speed
        if keys[pygame.K_d] and player2_x < WIDTH - 190:
            player2_x += player2_speed
        if player2_alive and keys[pygame.K_SPACE]:
            fire_bullet2(player2_x, player2_y)
    
    # Instead of always drawing players, draw only if alive
    if player1_alive:
        draw_player(player_x, player_y)
        # Draw "player1" label below Player 1
        label_font = pygame.font.Font("Graphics/Font/monogram.ttf", 17)
        label_text = label_font.render("player1", True, WHITE)
        label_shadow = label_font.render("player1", True, (50, 50, 50))
        label_rect = label_text.get_rect(center=(player_x + 40, player_y + 90))
        label_shadow_rect = label_shadow.get_rect(center=(player_x + 40 + 2, player_y + 90 + 2))
        screen.blit(label_shadow, label_shadow_rect)
        screen.blit(label_text, label_rect)
    if two_player and player2_alive:
        draw_player2(player2_x, player2_y)
        # Draw "player2" label below Player 2
        label_font = pygame.font.Font("Graphics/Font/monogram.ttf", 17)
        label_text = label_font.render("player2", True, WHITE)
        label_shadow = label_font.render("player2", True, (50, 50, 50))
        label_rect = label_text.get_rect(center=(player2_x + 40, player2_y + 90))
        label_shadow_rect = label_shadow.get_rect(center=(player2_x + 40 + 2, player2_y + 90 + 2))
        screen.blit(label_shadow, label_shadow_rect)
        screen.blit(label_text, label_rect)
    
    # Move Enemies and process game logic
    enemy_move_down = False
    for enemy in alien_formation:
        enemy[0] += enemy_direction * enemy_speed
        # Check if any enemy hits the screen edges
        if enemy[0] <= 80 or enemy[0] >= WIDTH - 140:
            enemy_direction *= -1  # Reverse direction
            enemy_move_down = True  # Move enemies down
            break

    # Move enemies down if needed
    if enemy_move_down:
        for enemy in alien_formation:
            enemy[1] += 30  # Adjusted to move enemies down by 50 pixels

    # Check for collision between player and enemies
    for enemy in alien_formation:
        if is_player_collision(player_x, player_y, enemy[0], enemy[1]):
            game_over()  # End the game if a collision is detected

    # Drawing the combined formation
    for enemy in alien_formation:
        x, y, _, group_type = enemy
        if group_type == 'alien1':
            draw_alien1(x, y)
        elif group_type == 'alien3':
            draw_alien3(x, y)
        elif group_type == 'enemy2':
            draw_enemy2(x, y)

    # ----- New: Update alien4 movement and collision checks -----
    alien4_x += alien4_speed
    if alien4_x > WIDTH:
        alien4_x = -50  # reset x only, do not change y
        
    # Check collision for player1 bullets with alien4
    for bullet in bullets[:]:
        if is_collision(alien4_x, alien4_y, bullet[0], bullet[1]):
            score += 200  # Award 200 points
            bullets.remove(bullet)
            alien4_x = -50  # reset x only (do not change y)
            
    # Check collision for player2 bullets with alien4
    if two_player:
        for bullet in bullets2[:]:
            if is_collision(alien4_x, alien4_y, bullet[0], bullet[1]):
                score += 200
                bullets2.remove(bullet)
                alien4_x = -50  # reset x only, maintain y
                
    # Draw alien4 on screen
    draw_alien4(alien4_x, alien4_y)
    # --------------------------------------------------------------

    # Move Bullets
    current_time = pygame.time.get_ticks()

    # Handle bullet animation timing
    if current_time - last_bullet_animation_time > bullet_animation_speed:
        bullet_frame_index = (bullet_frame_index + 1) % len(bullet_frames)
        last_bullet_animation_time = current_time

    # Move Bullets
    for bullet in bullets[:]:
        bullet[1] -= bullet_speed
        screen.blit(bullet_frames[bullet_frame_index], (bullet[0], bullet[1]))
        if bullet[1] < 0:
            bullets.remove(bullet)
            continue
        for alien in alien_formation[:]:
            if is_collision(alien[0], alien[1], bullet[0], bullet[1]):
                if bullet in bullets:
                    bullets.remove(bullet)
                enemyD.play()
                alien_formation.remove(alien)
                score += 50
                break

    # New: Process bullets for player2 if two_player mode is True:
    if two_player:
        for bullet in bullets2[:]:
            bullet[1] -= bullet_speed
            screen.blit(bullet_frames[bullet_frame_index], (bullet[0], bullet[1]))
            if bullet[1] < 0:
                bullets2.remove(bullet)
                continue
            for alien in alien_formation[:]:
                if is_collision(alien[0], alien[1], bullet[0], bullet[1]):
                    if bullet in bullets2:
                        bullets2.remove(bullet)
                    enemyD.play()
                    alien_formation.remove(alien)
                    score += 50
                    break

    display_score_and_level()
    display_health()
    
    # Check if all enemies are defeated and process level up or win condition
    if not alien_formation:
        if level == 5:
            game_win()
            # Reset game state after win
            score = 0
            level = 1
            player_health = 3
            player2_health = 3
            player_x = WIDTH // 2 - 35
            player_y = HEIGHT - 120
            player2_x = WIDTH // 2 + 100
            player2_y = HEIGHT - 120
            bullets.clear()
            alien1_bullets.clear()
            # --- DO NOT call difficulty_selection() again here ---
            alien_formation = create_alien_formation(enemy_speed)
        else:
            increase_difficulty()
            alien_formation = create_alien_formation(enemy_speed)  # Reset alien formation with increased difficulty

    # Alien1 Shooting Logic
    current_time = pygame.time.get_ticks()
    if current_time - last_alien1_shot_time > alien1_shot_cooldown:
        # Get all aliens of group 'alien1'
        alien1_group = [alien for alien in alien_formation if alien[3] == 'alien1']
        if alien1_group:
            shooter = random.choice(alien1_group)
            # Adjust bullet position relative to shooter sprite size (assumed width=50, height=40)
            bullet_x = shooter[0] + (50 // 2) - (40 // 2)
            bullet_y = shooter[1] + 40  # Start from lower part of the alien1 sprite
            alien1_bullets.append([bullet_x, bullet_y])
            last_alien1_shot_time = current_time

    # Handle Alien1 Laser Bullet Animation Timing
    if current_time - last_alien1_laser_animation_time > alien1_laser_animation_speed:
        alien1_laser_frame_index = (alien1_laser_frame_index + 1) % len(alien1_laser_frames)
        last_alien1_laser_animation_time = current_time

    # Move and Draw Alien1 Bullets
    for bullet in alien1_bullets[:]:
        bullet[1] += alien1_bullet_speed  # Move bullet downward toward player
        screen.blit(alien1_laser_frames[alien1_laser_frame_index], (bullet[0], bullet[1]))
        if bullet[1] > HEIGHT:
            alien1_bullets.remove(bullet)
            continue
        collided = False
        if player1_alive and is_collision(player_x, player_y, bullet[0], bullet[1]):
            player_health -= 1  # Decrease player1's health
            collided = True
            if player_health <= 0:
                player1_alive = False
        elif two_player and player2_alive and is_collision(player2_x, player2_y, bullet[0], bullet[1]):
            player2_health -= 1  # Decrease player2's health
            collided = True
            if player2_health <= 0:
                player2_alive = False
        if collided:
            alien1_bullets.remove(bullet)
            continue

    # After processing collisions and game logic, check if both players are dead:
    if not player1_alive and (not two_player or not player2_alive):
        game_over()

    pygame.display.update()
    clock.tick(30)

pygame.quit()
