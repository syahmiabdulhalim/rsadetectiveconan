import pygame
import sys
import random
import time
from sympy import isprime, mod_inverse

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()
pygame.display.set_caption("Detective Conan RSA Cipher Challenge")
font = pygame.font.Font("assets/fonts/anime_font.ttf", 28)

# Load animation cutscenes
cutscene_success = pygame.image.load("assets/images/cutscene_success.jpg")
cutscene_success = pygame.transform.scale(cutscene_success, (screen_width, screen_height))
cutscene_fail = pygame.image.load("assets/images/cutscene_fail.jpg")
cutscene_fail = pygame.transform.scale(cutscene_fail, (screen_width, screen_height))

# Helper to draw stage titles
stage_titles = {
    0: "Stage 1: Difficulty Selection",
    1: "Stage 2: Prime Number Selection",
    2: "Stage 3: Key Generation",
    3: "Stage 4: Decryption",
    4: "Conclusion"
}

def draw_stage_title(stage):
    title = stage_titles.get(stage, "")
    if title:
        label = font.render(title, True, (255, 255, 0))
        label_rect = label.get_rect(center=(screen_width // 2, 20))
        screen.blit(label, label_rect)

# Use small primes like 3, 5, 7, 11, 17 to make game easier

def generate_small_primes():
    return [p for p in [3, 5, 7, 11, 17] if isprime(p)]

def apply_shadow(image, offset=(5, 5)):
    shadow = pygame.Surface((image.get_width() + offset[0], image.get_height() + offset[1]), pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 100))
    shadow.blit(image, offset)
    shadow.blit(image, (0, 0))
    return shadow

def draw_button(rect, text, active):
    color = (0, 150, 150) if active else (0, 100, 100)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (255, 255, 255), rect, 2)
    label = font.render(text, True, (255, 255, 255))
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)

def create_button(center_x, y, width, height):
    return pygame.Rect(center_x - width // 2, y, width, height)

bg = pygame.image.load("assets/images/bg_city_vibrant(1).jpg")
bg = pygame.transform.scale(bg, (screen_width, screen_height))

conan_img = apply_shadow(pygame.image.load("assets/images/conan.png"))
conan_thinking = apply_shadow(pygame.image.load("assets/images/conan_thinking.png"))
kid_img = apply_shadow(pygame.image.load("assets/images/kid.png"))
kid_worried = apply_shadow(pygame.image.load("assets/images/kid_worried.png"))

pygame.mixer.music.load("assets/sounds/game_theme.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)
start_sfx = pygame.mixer.Sound("assets/sounds/start.mp3")
success_sfx = pygame.mixer.Sound("assets/sounds/success.mp3")
fail_sfx = pygame.mixer.Sound("assets/sounds/failed.mp3")

stage = -2
message = ""
cipher = []
result = ""
p = q = n = phi = e = d = 0
difficulty = 8
prime_inputs = []
user_decrypted = ""
speaker = ""
dialog = ""
ending = ""

typing_effect = ""
typing_index = 0
typing_time = time.time()

splash_shown = True
splash_start_time = time.time()
intro_lines = [
    "Conan: Another case? ",
    "* Conan opens the card *",
    "Kaito Kid: Yes, a challenge for you, Detective.",
    "Conan: What is it this time?",
    "Kaito Kid: A treasure hidden behind a cipher. Crack it, and you win.",
    "Conan: A cipher? I love a good challenge.",
    "Kaito Kid: It's an RSA cipher. Can you handle it?",
    "Conan: RSA? That's child's play for me.",
    "Kaito Kid: We'll see about that. Here's the card with the cipher.",
    "Kaito Kid: *hands over a card with RSA parameters*",
    "Conan: *examines the card*",
    "Conan: Two primes, a public key, and a message. Let's get started.",
    "Kaito Kid: Good luck, Detective. I'll be watching."
    "Conan: You won't get away that easily, Kid. I'll crack this code.",
    "Kaito Kid: We'll see, Detective. The treasure is at stake."
]
intro_index = 0
intro_time = time.time()

clock = pygame.time.Clock()
running = True

conan_x = -300
kid_x = screen_width + 300
anim_speed = 12

def draw_text_centered(text, y, color=(255, 255, 255)):
    rendered = font.render(text, True, color)
    text_rect = rendered.get_rect(center=(screen_width // 2, y))
    screen.blit(rendered, text_rect)

def draw_typing_text(text, y, color=(255, 255, 255)):
    global typing_index, typing_time, typing_effect
    if typing_effect != text:
        typing_effect = text
        typing_index = 0
        typing_time = time.time()
    if typing_index < len(typing_effect):
        if time.time() - typing_time > 0.03:
            typing_index += 1
            typing_time = time.time()
    draw_text_centered(typing_effect[:typing_index], y, color)

# Button declarations
buttons = {
    "easy": create_button(screen_width // 2 - 160, 300, 120, 50),
    "medium": create_button(screen_width // 2, 300, 140, 50),
    "hard": create_button(screen_width // 2 + 180, 300, 120, 50),
    "restart": create_button(screen_width // 2, 360, 240, 50),
    "exit": create_button(screen_width // 2, 430, 200, 50)
}

prime_buttons = []
e_buttons = []
d_buttons = []

user_message_input = ""
input_active = False
input_box = pygame.Rect(screen_width // 2 - 200, 320, 400, 50)
input_color = pygame.Color('dodgerblue2')


while running:
    screen.blit(bg, (0, 0))

    if conan_x < screen_width // 4:
        conan_x += anim_speed
    if kid_x > 3 * screen_width // 4:
        kid_x -= anim_speed

    conan_rect = conan_img.get_rect(midbottom=(conan_x, screen_height - 20))
    kid_rect = kid_img.get_rect(midbottom=(kid_x, screen_height - 20))

    screen.blit(conan_img if stage <= 3 else conan_thinking, conan_rect)
    screen.blit(kid_img if stage < 4 else kid_worried, kid_rect)

    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_clicked = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    if stage == -2:
        draw_text_centered("Detective Conan RSA Challenge", 80, (255, 255, 0))
        draw_text_centered("Click to start...", 130, (255, 255, 255))
        if mouse_clicked:
            stage = -1
            intro_time = time.time()
    elif stage == -1:
        draw_typing_text(intro_lines[intro_index], 80, (173, 216, 230))
        if mouse_clicked:
            intro_index += 1
            if intro_index >= len(intro_lines):
                stage = 0
                dialog = "Welcome to the RSA Game! Choose difficulty: Easy / Medium / Hard"
                speaker = "Conan"
    else:
        pygame.draw.rect(screen, (0, 0, 0, 180), (screen_width // 2 - 400, 30, 800, 120))
        pygame.draw.rect(screen, (0, 255, 255), (screen_width // 2 - 400, 30, 800, 120), 2)
        draw_typing_text(f"{speaker}: {dialog}", 80, (255, 255, 255))

        if stage == 0:
            for key in ["easy", "medium", "hard"]:
                draw_button(buttons[key], key.capitalize(), buttons[key].collidepoint(mouse_pos))
            if mouse_clicked:
                if buttons["easy"].collidepoint(mouse_pos):
                    difficulty = 1
                elif buttons["medium"].collidepoint(mouse_pos):
                    difficulty = 3
                elif buttons["hard"].collidepoint(mouse_pos):
                    difficulty = 5
                stage = 1
                dialog = "Select the first prime number (p):"
                speaker = "Conan"
                prime_buttons = []
                prime_choices = []
                choices = []
                while len(prime_choices) < 2:
                    candidate = random.randint(10**(difficulty-1), 10**difficulty - 1)
                    if isprime(candidate) and candidate not in prime_choices:
                        prime_choices.append(candidate)
                while len(choices) < 4:
                    candidate = random.randint(10**(difficulty-1), 10**difficulty - 1)
                    if candidate not in choices and candidate not in prime_choices:
                        choices.append(candidate)
                choices.extend(prime_choices)
                random.shuffle(choices)
                for i, val in enumerate(choices):
                    rect = create_button(screen_width // 2 - 300 + (i % 3) * 200, 200 + (i // 3) * 80, 160, 60)
                    prime_buttons.append((rect, val))

        elif stage == 1:
            for rect, val in prime_buttons:
                draw_button(rect, str(val), rect.collidepoint(mouse_pos))
            if mouse_clicked:
                for rect, val in prime_buttons:
                    if rect.collidepoint(mouse_pos):
                        prime_inputs.append(val)
                        if len(prime_inputs) == 2:
                            p, q = prime_inputs
                            n = p * q
                            phi = (p - 1) * (q - 1)
                            stage = 2
                            dialog = "Choose a public key (e):"
                            valid_es = [e for e in [3, 17, 65537] if phi % e != 0]
                            if not valid_es:
                                dialog = "No valid public key (e) found. Restarting..."
                                stage = 0
                                prime_inputs = []
                                continue
                            e_buttons = []
                            for i, val in enumerate(valid_es):
                                rect = create_button(screen_width // 2 - 200 + i * 200, 200, 120, 60)
                                e_buttons.append((rect, val))
                        else:
                            dialog = "Select the second prime number (q):"

        elif stage == 2:
            for rect, val in e_buttons:
                draw_button(rect, str(val), rect.collidepoint(mouse_pos))
            if mouse_clicked:
                for rect, val in e_buttons:
                    if rect.collidepoint(mouse_pos):
                        e = val
                        d = mod_inverse(e, phi)
                        stage = 3
                        dialog = "Message encrypted! Select the correct private key (d):"
                        speaker = "Conan"
                        message = "SecretTreasure"
                        cipher = [pow(ord(char), e, n) for char in message]
                        d_buttons = []
                        distractors = [d + random.randint(1, 1000) for _ in range(3)]
                        candidates = distractors + [d]
                        random.shuffle(candidates)
                        for i, val in enumerate(candidates):
                            rect = create_button(screen_width // 2 - 300 + (i % 2) * 300, 250 + (i // 2) * 100, 200, 60)
                            d_buttons.append((rect, val))

        elif stage == 3:
            draw_text_centered("Encrypted Cipher:", 180)
            draw_text_centered(' '.join(map(str, cipher[:4])) + " ...", 220)
            for rect, val in d_buttons:
                draw_button(rect, str(val), rect.collidepoint(mouse_pos))
            if mouse_clicked:
                for rect, val in d_buttons:
                    if rect.collidepoint(mouse_pos):
                        user_d = val
                        user_decrypted = ''
                        for c in cipher:
                            decrypted_val = pow(c, user_d, n)
                            if 0 <= decrypted_val <= 1114111:
                                user_decrypted += chr(decrypted_val)
                            else:
                                user_decrypted = "[Invalid Decryption]"
                                break
                        if user_d == d and user_decrypted == message:
                            ending = "✅ You cracked the code! The treasure is safe!"
                            success_sfx.play()
                        else:
                            ending = "❌ Too late… The Kid escapes with the treasure."
                            fail_sfx.play()
                        stage = 4
                        dialog = "Case closed. Try again or exit?"

        elif stage == 4:
                if "Success" in ending or "✅" in ending:
                    screen.blit(cutscene_success, (0, 0))
                else:
                    screen.blit(cutscene_fail, (0, 0))
                draw_text_centered(ending, 280, (255, 215, 0))
                draw_button(buttons["restart"], "Restart Game", buttons["restart"].collidepoint(mouse_pos))
                draw_button(buttons["exit"], "Exit Game", buttons["exit"].collidepoint(mouse_pos))
                if mouse_clicked:
                    if buttons["restart"].collidepoint(mouse_pos):
                        stage = 0
                        dialog = "Welcome to the RSA Game! Choose difficulty: Easy / Medium / Hard"
                        speaker = "Conan"
                        prime_inputs = []
                        ending = ""
                    elif buttons["exit"].collidepoint(mouse_pos):
                        running = False

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
