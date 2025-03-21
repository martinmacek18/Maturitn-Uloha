import pygame
import random
import sqlite3

# Inicializace Pygame
pygame.init()

# Nastavení okna
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Game")

# Barvy
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0,255,0)
GOLD = (255,215,0)
MAGENT = (255,0,255)

# Nastavení hry
paddle_width, paddle_height = 20, 100
ball_size = 20

# Počáteční pozice
player1_y, player2_y = HEIGHT // 2 - paddle_height // 2, HEIGHT // 2 - paddle_height // 2
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_dx, ball_dy = random.choice([-5, 5]), random.choice([-5, 5])

# Skóre
score1, score2 = 0, 0

# Fonty
font_game = pygame.font.Font(None, 50)
font_menu = pygame.font.Font(None, 80)  # Větší font pro menu
font_input = pygame.font.Font(None, 40)

# Funkce pro vytvoření databáze a tabulky
def vytvorit_databazi():
    conn = sqlite3.connect('vysledky_zapasu.db')
    cursor = conn.cursor()

    # Vytvoření tabulky, pokud ještě neexistuje
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player1_name TEXT,
        player2_name TEXT,
        player1_score INTEGER,
        player2_score INTEGER,
        winner TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Funkce pro uložení výsledku zápasu do databáze
def ulozit_vysledek(player1_name, player2_name, score1, score2, winner):
    conn = sqlite3.connect('vysledky_zapasu.db')
    cursor = conn.cursor()
    
    # Vložení výsledku zápasu
    cursor.execute('''
    INSERT INTO results (player1_name, player2_name, player1_score, player2_score, winner)
    VALUES (?, ?, ?, ?, ?)
    ''', (player1_name, player2_name, score1, score2, winner))
    
    conn.commit()
    conn.close()

# Funkce pro zobrazení posledních 5 výsledků zápasů
def zobrazit_vysledky():
    conn = sqlite3.connect('vysledky_zapasu.db')
    cursor = conn.cursor()
    
    # Načtení posledních 5 zápasů
    cursor.execute('SELECT * FROM results ORDER BY id DESC LIMIT 5')
    results = cursor.fetchall()
    
    conn.close()
    return results

# Funkce pro zadání jména hráče
def zadat_jmeno(player_num):
    global player1_name, player2_name
    input_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 40)
    clock = pygame.time.Clock()
    text = ''
    font = pygame.font.Font(None, 40)

    while True:
        screen.fill(BLACK)

        # Barvy pro hráče 1 a 2 přímo v renderovacích příkazech
        if player_num == 1:
            prompt_text = font.render("Zadej jméno hráče 1(ENTER):", True, RED)
            pygame.draw.rect(screen, RED, input_box, 2)
            back_text = font.render("Zpět", True, RED)
        else:
            prompt_text = font.render("Zadej jméno hráče 2(ENTER):", True, BLUE)
            pygame.draw.rect(screen, BLUE, input_box, 2)
            back_text = font.render("Zpět", True, BLUE)

        screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 - 50))

        # Pozice tlačítka "Zpět"
        back_x = WIDTH // 2 - back_text.get_width() // 2
        back_y = HEIGHT // 2 + 70  
        screen.blit(back_text, (back_x, back_y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif event.key == pygame.K_RETURN:
                    text = text.strip()
                    if text:
                        if player_num == 1:
                            player1_name = text
                            zadat_jmeno(2)  # Pokračuje na hráče 2
                        else:
                            player2_name = text
                            hra()  # Spustí hru
                        return
                else:
                    text += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_x <= event.pos[0] <= back_x + back_text.get_width() and \
                   back_y <= event.pos[1] <= back_y + back_text.get_height():
                    if player_num == 1:
                        menu()
                    else:
                        zadat_jmeno(1)
                    return

        # Vykreslení textu v poli v odpovídající barvě
        if player_num == 1:
            text_surface = font.render(text, True, RED)
        else:
            text_surface = font.render(text, True, BLUE)

        screen.blit(text_surface, (input_box.x + 10, input_box.y + 5))

        pygame.display.flip()
        clock.tick(30)

def odpocet():
    global ball_dx, ball_dy

    # Během odpočtu se míček nepohybuje
    for i in range(3, 0, -1):
        screen.fill(BLACK)

        # Kreslení pálky a míčku během odpočtu
        pygame.draw.rect(screen, RED, (0, player1_y, paddle_width, paddle_height))
        pygame.draw.rect(screen, BLUE, (WIDTH - paddle_width, player2_y, paddle_width, paddle_height))
        pygame.draw.ellipse(screen, WHITE, (ball_x, ball_y, ball_size, ball_size))

        # Zobrazení odpočtu
        countdown_text = font_game.render(str(i), True, WHITE)
        screen.blit(countdown_text, (WIDTH // 2 - countdown_text.get_width() // 2, HEIGHT // 2 - 50))
        
        # Zobrazení skóre a jmen hráčů během odpočtu
        score_text = font_game.render(f"{score1} : {score2}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))
        
        player1_text = font_game.render(player1_name, True, RED)
        player2_text = font_game.render(player2_name, True, BLUE)
        screen.blit(player1_text, (20, 10))  # Hráč 1 vlevo nahoře
        screen.blit(player2_text, (WIDTH - player2_text.get_width() - 20, 10))  # Hráč 2 vpravo nahoře

        pygame.display.flip()
        pygame.time.delay(1000)  # Počkej 1 sekundu

# Herní smyčka
def hra():
    global player1_y, player2_y, ball_x, ball_y, ball_dx, ball_dy, score1, score2
    reset_pozice()
    clock = pygame.time.Clock()
    # Zobraz odpočet před startem
    odpocet()
    running = True
    
    while running:
        screen.fill(BLACK)
        
        # Udalosti
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        # Ovládání
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and player1_y > 0:
            player1_y -= 5
        if keys[pygame.K_s] and player1_y < HEIGHT - paddle_height:
            player1_y += 5
        if keys[pygame.K_UP] and player2_y > 0:
            player2_y -= 5
        if keys[pygame.K_DOWN] and player2_y < HEIGHT - paddle_height:
            player2_y += 5
        
        # Pohyb míčku
        ball_x += ball_dx
        ball_y += ball_dy
        
        # Kolize s horními a dolními okraji
        if ball_y <= 0 or ball_y >= HEIGHT - ball_size:
            ball_dy *= -1
        
         # Kolize s pálkami - dynamická změna úhlu odrazu
        if ball_x <= paddle_width and player1_y <= ball_y <= player1_y + paddle_height:
            relative_intersect_y = (ball_y - player1_y) / paddle_height - 0.5
            ball_dx = abs(ball_dx)  # Míček letí doprava
            ball_dy += relative_intersect_y * 5  # Úprava vertikálního směru
        
        if ball_x >= WIDTH - paddle_width - ball_size and player2_y <= ball_y <= player2_y + paddle_height:
            relative_intersect_y = (ball_y - player2_y) / paddle_height - 0.5
            ball_dx = -abs(ball_dx)  # Míček letí doleva
            ball_dy += relative_intersect_y * 5  # Úprava vertikálního směru
        
        # Bodování
        if ball_x < 0:
            score2 += 1
            ball_x, ball_y = WIDTH // 2, HEIGHT // 2
            ball_dx *= -1
        elif ball_x > WIDTH:
            score1 += 1
            ball_x, ball_y = WIDTH // 2, HEIGHT // 2
            ball_dx *= -1
        
        # Konec hry
        if score1 == 5:
            vyherce(player1_name)  # Posíláme jméno vítěze
            return
        elif score2 == 5:
            vyherce(player2_name)  # Posíláme jméno vítěze
            return
        
        # Kreslení
        pygame.draw.rect(screen, RED, (0, player1_y, paddle_width, paddle_height))
        pygame.draw.rect(screen, BLUE, (WIDTH - paddle_width, player2_y, paddle_width, paddle_height))
        pygame.draw.ellipse(screen, WHITE, (ball_x, ball_y, ball_size, ball_size))
        
        # Skóre
        score_text = font_game.render(f"{score1} : {score2}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - 30, 10))
        
        
        # Text pro hráče 1 a 2
        player1_text = font_game.render(player1_name, True, RED)
        player2_text = font_game.render(player2_name, True, BLUE)
        screen.blit(player1_text, (20, 10))  # Hráč 1 vlevo nahoře
        screen.blit(player2_text, (WIDTH - player2_text.get_width() - 20, 10))  # Hráč 2 vpravo nahoře
        
        pygame.display.flip()
        clock.tick(60)

# Funkce pro resetování pozice pálek
def reset_pozice():
    global player1_y, player2_y
    player1_y = HEIGHT // 2 - paddle_height // 2
    player2_y = HEIGHT // 2 - paddle_height // 2

# Výherní obrazovka
def vyherce(vyherce_jmeno):
    global score1, score2
    
    # Uložení výsledku do databáze
    if vyherce_jmeno == player1_name:
        winner = player1_name
    else:
        winner = player2_name

    ulozit_vysledek(player1_name, player2_name, score1, score2, winner)

    screen.fill(BLACK)
    win_text = font_game.render(f"{vyherce_jmeno} vyhrál!", True, GOLD)
    screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 50))

    pygame.display.flip()
    pygame.time.delay(2000)
    
    score1, score2 = 0, 0  # Reset skóre
    menu()

# Menu
def menu():
    while True:
        screen.fill(BLACK)
        title = font_menu.render("Pong Game", True, MAGENT)
        play_button = font_menu.render("Hrát", True, GREEN)
        quit_button = font_menu.render("Ukončit", True, RED)
        results_button = font_menu.render("Výsledky", True, GOLD)
        
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        screen.blit(play_button, (WIDTH // 2 - play_button.get_width() // 2, 300))
        screen.blit(quit_button, (WIDTH // 2 - quit_button.get_width() // 2, 500))
        screen.blit(results_button, (WIDTH // 2 - results_button.get_width() // 2, 400))
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if WIDTH // 2 - play_button.get_width() // 2 <= x <= WIDTH // 2 + play_button.get_width() // 2 and \
                   300 <= y <= 300 + play_button.get_height():
                    zadat_jmeno(1)  # Zadej jméno hráče 1
                    zadat_jmeno(2)  # Zadej jméno hráče 2
                    hra()
                if WIDTH // 2 - quit_button.get_width() // 2 <= x <= WIDTH // 2 + quit_button.get_width() // 2 and \
                   500 <= y <= 500 + quit_button.get_height():
                    pygame.quit()
                    return
                if WIDTH // 2 - results_button.get_width() // 2 <= x <= WIDTH // 2 + results_button.get_width() // 2 and \
                   400 <= y <= 400 + results_button.get_height():
                    zobrazit_historii_vysledku()

# Funkce pro zobrazení historie výsledků
def zobrazit_historii_vysledku():
    while True:
        screen.fill(BLACK)
        results = zobrazit_vysledky()
        result_text = font_game.render("Poslední výsledky:", True, GOLD)
        screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, 50))
        
        y_offset = 100
        for result in results:
            result_line = font_game.render(f"{result[1]} vs {result[2]} | {result[3]} : {result[4]} | Vítěz: {result[5]}", True, GOLD)
            screen.blit(result_line, (WIDTH // 2 - result_line.get_width() // 2, y_offset))
            y_offset += 40
        
        # Přidání tlačítka "Zpět"
        back_button = font_game.render("Zpět", True, GOLD)
        screen.blit(back_button, (WIDTH // 2 - back_button.get_width() // 2, HEIGHT - 100))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if WIDTH // 2 - back_button.get_width() // 2 <= x <= WIDTH // 2 + back_button.get_width() // 2 and \
                   HEIGHT - 100 <= y <= HEIGHT - 100 + back_button.get_height():
                    return  # Vrátí se zpět do menu

# Hlavní smyčka
vytvorit_databazi()
menu()