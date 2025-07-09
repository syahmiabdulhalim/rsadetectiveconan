# Detective Conan RSA Cipher Mystery – Visual Novel with Game Modes and Prime Selection Redesign

import pygame
import sys
import sympy
import random
import time

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Detective Conan: RSA Cipher Mystery")
font = pygame.font.SysFont("arial", 28)
large_font = pygame.font.SysFont("arial", 48)
clock = pygame.time.Clock()
screen_width, screen_height = screen.get_size()

# Load visual assets
bg_start = pygame.image.load("assets/images/bg_start.jpg")
bg_start = pygame.transform.scale(bg_start, (screen_width, screen_height))
bg_vibrant = pygame.image.load("assets/images/bg_city_vibrant(1).jpg")
bg_vibrant = pygame.transform.scale(bg_vibrant, (screen_width, screen_height))
bg_failed = pygame.image.load("assets/images/explosion.jpeg")
bg_failed = pygame.transform.scale(bg_failed, (screen_width, screen_height))
cutscene_success_img = pygame.transform.scale(
    pygame.image.load("assets/images/cutscene_success.jpg"),
    (800, 450)  # You can tweak this size as needed
)
bg = bg_start

conan_img = pygame.transform.scale(pygame.image.load("assets/images/conan(2).png"), (250, 370))
kid_img = pygame.transform.scale(pygame.image.load("assets/images/kaito_kid.png"), (250, 370))
kid_center_img = pygame.transform.scale(pygame.image.load("assets/images/kid.png"), (300, 450))

# Load music and sound
pygame.mixer.music.load("assets/sounds/bgm_mystery.mp3")
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1)
select_sound = pygame.mixer.Sound("assets/sounds/select.mp3")
select_sound.set_volume(0.3)
success_sound = pygame.mixer.Sound("assets/sounds/success.mp3")
success_sound.set_volume(0.3)
# RSA logic
def is_valid_prime(n):
    return sympy.isprime(n)

def choose_public_exponent(phi):
    return [e for e in range(3, phi, 2) if sympy.gcd(e, phi) == 1 and sympy.isprime(e)][:5]

def encrypt_message(msg, e, n):
    return [pow(ord(c), e, n) for c in msg]

def decrypt_message(cipher, d, n):
    return ''.join(chr(pow(c, d, n)) for c in cipher)

# Dialog
def draw_dialog(speaker, text):
    dialog_box = pygame.Rect(50, 540, 1180, 150)
    pygame.draw.rect(screen, (30, 30, 30), dialog_box, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), dialog_box, 2, border_radius=10)
    name_surface = font.render(speaker, True, (255, 255, 0))
    screen.blit(name_surface, (70, 510))
    render_text(text, (70, 570))

def render_text(text, pos, color=(255,255,255), max_width=1100):
    words = text.split(" ")
    line = ""
    y = pos[1]
    for word in words:
        test_line = f"{line} {word}".strip()
        if font.size(test_line)[0] <= max_width:
            line = test_line
        else:
            screen.blit(font.render(line, True, color), (pos[0], y))
            y += font.get_linesize()
            line = word
    if line:
        screen.blit(font.render(line, True, color), (pos[0], y))

# Game state
stage = "menu"
difficulty = ""
p = q = n = phi = e = d = 0
primes = []
e_choices = []
message = ""
cipher = []
decrypted = ""
input_mode = False
user_input = ""
prime_options = []
prime_index = 0
selecting = "p"
selected_e_index = 0
timer_start = None
timer_limit = None
input_box = pygame.Rect(200, 300, 880, 40)
start_text_y = 500
start_text_direction = 1
decryption_index = 0
decryption_input = ""
decryption_result = ""
decryption_feedback = ""
decryption_timer_start = None
decryption_time_limit = 60  # seconds
show_hint = False
hint_button_rect = pygame.Rect(1120, 600, 100, 40)
wrong_attempts = 0

# Rects for difficulty buttons
difficulty_buttons = [
    ("easy", pygame.Rect(screen_width // 2 - 150, 280, 300, 60)),
    ("medium", pygame.Rect(screen_width // 2 - 150, 370, 300, 60)),
    ("hard", pygame.Rect(screen_width // 2 - 150, 460, 300, 60)),
]
# Dialog Scripts
intro_script = [
    ("Kaito", "Heheh... Time to give them a riddle they can't crack."),
    ("Kaito", "I'll plant the bomb and leave behind an encrypted clue."),
    ("Kaito", "Only the sharpest mind will defuse it. Let's begin.")
]
intro_index = 0

scenario_script = [
    ("Conan", "Kaito Kid! What are you up to this time?"),
    ("Kaito", "Ah, Detective Conan... You're just in time to see my next masterpiece unfold."),
    ("Conan", "You're planning something, aren't you?"),
    ("Kaito", "Indeed. I've left a puzzle – let's see if you can solve it before... boom."),
    ("Kaito", "Farewell, detective! Time is ticking.")
]
scenario_index = 0

def reset():
    global stage, p, q, n, phi, e, d, primes, e_choices, message, cipher, decrypted
    global user_input, input_mode, difficulty, prime_options, prime_index, selecting, selected_e_index
    global timer_start, timer_limit, bg, intro_index, scenario_index
    stage = "menu"
    p = q = n = phi = e = d = 0
    primes = []
    e_choices = []
    message = ""
    cipher = []
    decrypted = ""
    user_input = ""
    input_mode = False
    difficulty = ""
    prime_options = []
    prime_index = 0
    selecting = "p"
    selected_e_index = 0
    timer_start = None
    timer_limit = None
    bg = bg_start
    intro_index = 0
    scenario_index = 0
    decryption_index = 0
    decryption_input = ""
    decryption_result = ""
    decryption_feedback = ""
    show_hint = False
    decryption_timer_start = None
    timer_limit = 30
    hint_button_rect = pygame.Rect(1080, 600, 100, 40)
    LEADERBOARD_FILE = "leaderboard.txt"
    player_name = ""

def generate_primes(difficulty):
    if difficulty == "easy":
        r = (10, 100)
    elif difficulty == "medium":
        r = (100, 500)
    else:
        r = (500, 2000)
    return random.sample([x for x in range(r[0], r[1]) if is_valid_prime(x)], 6)

reset()
def load_leaderboard():
    leaderboard = []
    try:
        with open(LEADERBOARD_FILE, "r") as file:
            for line in file:
                name, time_str = line.strip().split(",")
                leaderboard.append((name, float(time_str)))
    except FileNotFoundError:
        pass
    return leaderboard

def save_leaderboard(name, time_taken):
    leaderboard = load_leaderboard()
    leaderboard.append((name, time_taken))
    leaderboard.sort(key=lambda x: x[1])  # Sort by fastest time
    leaderboard = leaderboard[:10]  # Keep top 10
    with open(LEADERBOARD_FILE, "w") as file:
        for entry in leaderboard:
            file.write(f"{entry[0]},{entry[1]:.2f}\n")

running = True
while running:
    screen.blit(bg, (0, 0))

    if stage == "intro":
        screen.blit(kid_img, (screen_width//2 - 125, 150))
    elif stage == "scenario":
        screen.blit(kid_img, (100, 150))
        screen.blit(conan_img, (900, 150))
    elif stage in ["decrypt", "done"]:
        screen.blit(conan_img, (50, 150))
    elif stage in ["get_message", "prime_selection", "select_e", "show_keys", "show_encrypted"]:
        screen.blit(kid_img, (100, 150))

    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if stage == "menu":
                stage = "difficulty_select"
                bg = bg_vibrant
                select_sound.play()

            elif stage == "intro" and event.key == pygame.K_RETURN:
                intro_index += 1
                if intro_index >= len(intro_script):
                    stage = "prime_selection"
                    prime_options = generate_primes(difficulty)

            elif stage == "scenario" and event.key == pygame.K_RETURN:
                scenario_index += 1
                if scenario_index >= len(scenario_script):
                    stage = "decrypt_manual"
                    decryption_timer_start = time.time()
                    decryption_index = 0
                    decryption_input = ""
                    decryption_result = ""
                    decryption_feedback = ""
                    show_hint = False

            elif stage == "show_encrypted" and event.key == pygame.K_RETURN:
                stage = "scenario"
                scenario_index = 0
                select_sound.play()

            elif input_mode:
                if event.key == pygame.K_RETURN:
                    input_mode = False
                    if stage == "get_message":
                        message = user_input
                        cipher = encrypt_message(message, e, n)
                        stage = "show_encrypted"
                        select_sound.play()
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                else:
                    user_input += event.unicode
            elif stage == "decrypt_manual":
                if event.key == pygame.K_RETURN:
                    if decryption_input and decryption_index < len(cipher):
                        expected_char = chr(pow(cipher[decryption_index], d, n))
                        if decryption_input == expected_char:
                            decryption_result += decryption_input
                            decryption_feedback = "Correct!"
                        else:
                            decryption_feedback = f"Wrong! Expected: {expected_char}"
                            wrong_attempts += 1  # ✅ Count wrong answers
                            if wrong_attempts >= 5:
                                stage = "failed"  # ✅ Go to failed screen
                                decryption_timer_start = None  # ❗ Stop timer when failed
                        decryption_index += 1
                        decryption_input = ""
                        if decryption_index >= len(cipher) and stage != "failed":
                            expected_result = decrypt_message(cipher, d, n)
                            if decryption_result == expected_result:
                                stage = "done"
                                success_sound.play()
                                decryption_timer_start = None
                                
                            else:
                                stage = "failed"
                                decryption_timer_start = None
                elif event.key == pygame.K_BACKSPACE:
                    decryption_input = decryption_input[:-1]
                else:
                    decryption_input += event.unicode
            elif stage == "success":
                    if event.key == pygame.K_RETURN:
                        reset()
        
            else:
                if event.key == pygame.K_RETURN:
                    if stage == "show_keys":
                        stage = "get_message"
                        input_mode = True
                    elif stage == "done":
                        reset()
                    elif stage == "failed":
                        reset()

                if stage == "prime_selection" and event.unicode in "123":
                    prime_index = int(event.unicode) - 1
                    if selecting == "p":
                        p = prime_options[prime_index]
                        prime_options = generate_primes(difficulty)
                        selecting = "q"
                    else:
                        q = prime_options[prime_index]
                        n = p * q
                        phi = (p - 1) * (q - 1)
                        stage = "select_e"
                    select_sound.play()

                elif stage == "select_e" and event.unicode in "123":
                    selected_e_index = int(event.unicode) - 1
                    e = e_choices[selected_e_index]
                    d = sympy.mod_inverse(e, phi)
                    stage = "show_keys"
                    select_sound.play()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_clicked = True
            if stage == "decrypt_manual" and hint_button_rect.collidepoint(mouse_pos):
                show_hint = True

    if stage == "menu":
        start_text_y += start_text_direction
        if start_text_y > 510 or start_text_y < 490:
            start_text_direction *= -1
        text_surface = large_font.render("Press [Enter] to Begin", True, (255, 255, 0))
        text_rect = text_surface.get_rect(center=(screen_width // 2, start_text_y))
        screen.blit(text_surface, text_rect)

    elif stage == "difficulty_select":
        title = large_font.render("Select your Difficulty", True, (255, 255, 255))
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, 200))
        for label, rect in difficulty_buttons:
            color = (0, 255, 0) if label == "easy" else (255, 215, 0) if label == "medium" else (255, 0, 0)
            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (255, 255, 255), rect.inflate(10, 10), border_radius=12)
                if mouse_clicked:
                    difficulty = label
                    stage = "intro"
                    intro_index = 0
                    select_sound.play()
            pygame.draw.rect(screen, color, rect, border_radius=12)
            pygame.draw.rect(screen, (255, 255, 255), rect, 3, border_radius=12)
            txt = large_font.render(label.upper(), True, (0, 0, 0))
            screen.blit(txt, txt.get_rect(center=rect.center))

    elif stage == "intro" and intro_index < len(intro_script):
        speaker, line = intro_script[intro_index]
        draw_dialog(speaker, line)

    elif stage == "scenario" and scenario_index < len(scenario_script):
        speaker, line = scenario_script[scenario_index]
        draw_dialog(speaker, line)

    elif stage == "prime_selection":
        text = "   ".join([f"({i+1}) {prime_options[i]}" for i in range(3)])
        label = "First" if selecting == "p" else "Second"
        draw_dialog("Kaito", f"Choose the {label} prime number:\n {text}")

    elif stage == "select_e":
        e_choices = choose_public_exponent(phi)
        options = "   ".join([f"({i+1}) e = {val}" for i, val in enumerate(e_choices[:3])])
        draw_dialog("Kaito", f"Choose a public exponent:\n {options}")

    elif stage == "show_keys":
        draw_dialog("Kaito", f"Public key exponent {e} selected.\n Private key d calculated: {d}.\n Press [Enter] to input message.")

    elif stage == "get_message":
        draw_dialog("Kaito", "Type the message and press [Enter] to encrypt it:")
    
        # Draw black input box with white border
        pygame.draw.rect(screen, (0, 0, 0), input_box)  # Fill black
        pygame.draw.rect(screen, (255, 255, 255), input_box, 2)  # White border
        
        # Draw white text inside the input box
        text = font.render(user_input, True, (255, 255, 255))
        text_rect = text.get_rect(center=(input_box.centerx, input_box.centery))
        screen.blit(text, text_rect)

    elif stage == "show_encrypted":
        draw_dialog("Kaito", f"Here's the encrypted code: {cipher}.\n Let's see if Conan can crack it!")
        
    elif stage == "decrypt_manual":
        encrypted_value = cipher[decryption_index] if decryption_index < len(cipher) else "Done"
        draw_dialog("Conan", 
            f"Encrypted character {decryption_index + 1}/{len(cipher)}: {encrypted_value}\n"
            f"Enter decrypted character: {decryption_input}\n{decryption_feedback}\n"
            f"Decrypted so far: {decryption_result}"
        )

        # Draw Hint Button
        pygame.draw.rect(screen, (70, 130, 180), hint_button_rect, border_radius=8)
        hint_text = font.render("Hint", True, (255, 255, 255))
        screen.blit(hint_text, hint_text.get_rect(center=hint_button_rect.center))

    # Draw timer
    if decryption_timer_start and timer_limit:
        time_left = int(timer_limit - (time.time() - decryption_timer_start))
        if time_left < 0:
            time_left = 0
            stage = "failed"
        timer_surface = font.render(f"Time left: {time_left}s", True, (255, 100, 100))
        screen.blit(timer_surface, (1000, 40))

    # Show hint if requested
    if show_hint:
        if show_hint:
            hint_lines = [
                "Hint: Each encrypted number represents one character.",
                "To decrypt: c^d mod n = original ASCII code.",
                "Enter the character you think was encrypted!"
            ]
            hint_box = pygame.Rect(80, 80, 1000, 100)
            pygame.draw.rect(screen, (0, 0, 0), hint_box, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), hint_box, 2, border_radius=10)

            for i, line in enumerate(hint_lines):
                hint_surface = font.render(line, True, (255, 255, 255))  # White text
                screen.blit(hint_surface, (100, 90 + i * 28))  # Slightly padded

        
    elif stage == "decrypt_manual":
        encrypted_char = cipher[decryption_index] if decryption_index < len(cipher) else ''
        dialog_text = (
            f"Encrypted character {decryption_index+1}/{len(cipher)}: {encrypted_char}\n"
            f"Enter decrypted character: {decryption_input}\n"
            f"{decryption_feedback}\n Decrypted so far: {decryption_result}"
    )
        draw_dialog("Conan", dialog_text)
    elif stage == "decrypt_manual" and event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN:
            expected_result = decrypted[decryption_index]  # Ensure this line is present and 'decrypted' is precomputed

            if decryption_input == expected_result:
                decrypted_text += decryption_input
                decryption_feedback = "Correct!"
                decryption_input = ""
                decryption_index += 1

                if decryption_index >= len(cipher):
                    stage = "success"
                    success_time = time.time()  # optional: track time
            else:
                decryption_feedback = "Incorrect! Try again."
                decryption_input = ""

        elif event.key == pygame.K_BACKSPACE:
            decryption_input = decryption_input[:-1]
        else:
            decryption_input += event.unicode
        

    elif stage == "done":
        screen.blit(bg_vibrant, (0, 0))  # Background

        # Show cutscene success image in the center
        success_rect = cutscene_success_img.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(cutscene_success_img, success_rect)

        # Show congratulatory text
        success_text = large_font.render("Success! You stopped the bomb in time!", True, (255, 255, 0))
        text_rect = success_text.get_rect(center=(screen_width // 2, 100))
        screen.blit(success_text, text_rect)

        sub_text = font.render("Press [Enter] to restart the mission.", True, (255, 255, 255))
        sub_rect = sub_text.get_rect(center=(screen_width // 2, 160))
        screen.blit(sub_text, sub_rect)
        
    elif stage == "failed":
        # Draw the explosion background
        explosion_img = pygame.image.load("assets/images/explosion.jpeg")
        explosion_img = pygame.transform.scale(explosion_img, (screen_width, screen_height))
        screen.blit(explosion_img, (0, 0))

        # Draw Kaito Kid in the center
        failed_kid = pygame.image.load("assets/images/kid.png")
        failed_kid = pygame.transform.scale(failed_kid, (300, 450))
        screen.blit(failed_kid, (screen_width // 2 - 150, screen_height // 2 - 225 + 50))  # moves it 50px lower


        # Show failure message
        failed_text = large_font.render("You failed to defuse the cipher in time!", True, (255, 255, 255))
        text_rect = failed_text.get_rect(center=(screen_width // 2, 100))
        screen.blit(failed_text, text_rect)
        
        restart_text = font.render("Press [Enter] to try again.", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(screen_width // 2, 160))
        screen.blit(restart_text, restart_rect)
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
