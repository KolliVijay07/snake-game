"""
Snake Game in Python (Turtle Graphics)

A modular, event-driven implementation of the classic Snake Game.
Refactored from Jupyter Notebook to a standalone Python script with
improved game loop timing, non-blocking input handling, fixed rendering
issues, grid-aligned food spawning, and optimized high score persistence.
"""

import os
import random
import turtle

# ---------------------------------------------------------
# Configuration and File Paths
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HIGH_SCORE_FILE = os.path.join(BASE_DIR, "high_score.txt")
IMAGE_FILE = os.path.join(BASE_DIR, "snakeimg.gif")

# Grid and Screen Dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
GRID_STEP = 20
BOUNDARY_LIMIT = 290  # Wall collision threshold (-290 to 290)

# Speed Configuration (in milliseconds)
INITIAL_DELAY_MS = 100
MIN_DELAY_MS = 30
SPEED_DECREMENT_MS = 1

# Game States
STATE_WELCOME = "welcome"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"

# ---------------------------------------------------------
# Global State Variables
# ---------------------------------------------------------
score = 0
high_score = 0
current_delay_ms = INITIAL_DELAY_MS
game_state = STATE_WELCOME
current_direction = "Stop"
last_moved_direction = "Stop"

segments = []

# ---------------------------------------------------------
# High Score Persistence
# ---------------------------------------------------------
def load_high_score():
    """Load the high score from file safely."""
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, "r") as file:
                content = file.read().strip()
                if content.isdigit():
                    return int(content)
        except Exception as error:
            print(f"Warning: Could not read {HIGH_SCORE_FILE}: {error}")
    return 0


def save_high_score(new_high_score):
    """Save the updated high score to file only when changed."""
    try:
        with open(HIGH_SCORE_FILE, "w") as file:
            file.write(str(new_high_score))
    except Exception as error:
        print(f"Warning: Could not save high score to {HIGH_SCORE_FILE}: {error}")


# ---------------------------------------------------------
# Screen & Visual Component Setup
# ---------------------------------------------------------
screen = turtle.Screen()
screen.title("Snake Game")
screen.bgcolor("#E6E6FA")  # Lavender background
screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
screen.tracer(0)  # Manual screen rendering

# Welcome screen elements
welcome_image = turtle.Turtle()
welcome_image.penup()
welcome_image.hideturtle()

welcome_pen = turtle.Turtle()
welcome_pen.penup()
welcome_pen.hideturtle()

# Game Play Objects
head = turtle.Turtle()
head.shape("square")
head.color("brown")
head.penup()
head.hideturtle()
head.goto(0, 0)
head.direction = "Stop"

food = turtle.Turtle()
food.shape("circle")
food.color("green")
food.speed(0)
food.penup()
food.hideturtle()

# Heads-Up Display (Scoreboard)
score_pen = turtle.Turtle()
score_pen.speed(0)
score_pen.penup()
score_pen.hideturtle()
score_pen.goto(0, 260)

# Message Overlay (Game Over / Pause banner)
overlay_pen = turtle.Turtle()
overlay_pen.speed(0)
overlay_pen.penup()
overlay_pen.hideturtle()

# Buttons (Pause & Resume)
pause_button = turtle.Turtle()
pause_button.shape("circle")
pause_button.fillcolor("red")
pause_button.penup()
pause_button.hideturtle()

resume_button = turtle.Turtle()
resume_button.shape("circle")
resume_button.fillcolor("red")
resume_button.penup()
resume_button.hideturtle()

button_label_pen = turtle.Turtle()
button_label_pen.penup()
button_label_pen.hideturtle()


# ---------------------------------------------------------
# Welcome Screen
# ---------------------------------------------------------
def display_welcome_screen():
    """Renders the initial welcome screen with image and instructions."""
    global game_state
    game_state = STATE_WELCOME

    # Register and show image if it exists
    if os.path.exists(IMAGE_FILE):
        try:
            turtle.register_shape(IMAGE_FILE)
            welcome_image.shape(IMAGE_FILE)
            welcome_image.goto(0, 0)
            welcome_image.showturtle()
        except Exception as error:
            print(f"Notice: Could not load image shape: {error}")

    welcome_pen.clear()
    welcome_pen.color("black")
    welcome_pen.goto(0, 150)
    welcome_pen.write(
        "Snake Game",
        align="center",
        font=("Copperplate Gothic Bold", 30, "bold")
    )

    instructions = (
        "Instructions :\n"
        "1. Press Up Arrow ( ↑ ) to move up\n"
        "2. Press Down Arrow ( ↓ ) to move down\n"
        "3. Press Left Arrow ( ← ) to move left\n"
        "4. Press Right Arrow ( → ) to move right\n"
        "5. Click Pause button (or press P / Space) to pause\n"
        "6. Click Resume button (or press P / Space) to resume"
    )
    welcome_pen.goto(0, -160)
    welcome_pen.write(
        instructions,
        align="center",
        font=("Lucida Calligraphy", 12, "bold")
    )

    welcome_pen.goto(0, -190)
    welcome_pen.write(
        "Press Enter to start",
        align="center",
        font=("Lucida Calligraphy", 12, "bold")
    )

    screen.update()


def clear_welcome_screen():
    """Hides and clears the welcome screen components."""
    welcome_pen.clear()
    welcome_image.hideturtle()


# ---------------------------------------------------------
# Direction Controls & Input Debouncing
# ---------------------------------------------------------
def go_up():
    """Change direction to up if not currently moving down."""
    if last_moved_direction != "down" and game_state == STATE_PLAYING:
        head.direction = "up"


def go_down():
    """Change direction to down if not currently moving up."""
    if last_moved_direction != "up" and game_state == STATE_PLAYING:
        head.direction = "down"


def go_left():
    """Change direction to left if not currently moving right."""
    if last_moved_direction != "right" and game_state == STATE_PLAYING:
        head.direction = "left"


def go_right():
    """Change direction to right if not currently moving left."""
    if last_moved_direction != "left" and game_state == STATE_PLAYING:
        head.direction = "right"


def move():
    """Advance the snake head by one grid step in the current direction."""
    global last_moved_direction
    last_moved_direction = head.direction

    if head.direction == "up":
        head.sety(head.ycor() + GRID_STEP)
    elif head.direction == "down":
        head.sety(head.ycor() - GRID_STEP)
    elif head.direction == "left":
        head.setx(head.xcor() - GRID_STEP)
    elif head.direction == "right":
        head.setx(head.xcor() + GRID_STEP)


# ---------------------------------------------------------
# Pause and Resume Handling
# ---------------------------------------------------------
def pause_game(x=0, y=0):
    """Pauses the game loop and shows the pause overlay."""
    global game_state
    if game_state == STATE_PLAYING:
        game_state = STATE_PAUSED
        overlay_pen.clear()
        overlay_pen.color("#4B0082")  # Indigo
        overlay_pen.goto(0, 50)
        overlay_pen.write("PAUSED", align="center", font=("Georgia", 36, "bold"))
        overlay_pen.goto(0, 10)
        overlay_pen.write("Click Resume or Press P / Space", align="center", font=("Georgia", 14, "italic"))
        screen.update()


def resume_game(x=0, y=0):
    """Resumes the game loop and clears the pause overlay."""
    global game_state
    if game_state == STATE_PAUSED:
        game_state = STATE_PLAYING
        overlay_pen.clear()
        screen.update()


def toggle_pause():
    """Toggle between paused and playing states with keyboard."""
    if game_state == STATE_PLAYING:
        pause_game()
    elif game_state == STATE_PAUSED:
        resume_game()


# ---------------------------------------------------------
# Food Placement (Grid-Aligned)
# ---------------------------------------------------------
def generate_food_position():
    """
    Generate a new random position for food snapped to the 20px grid
    that does not collide with the snake's head or existing body segments.
    """
    # Grid coordinates range from -260 to +260 with 20px step
    grid_coords = list(range(-260, 280, GRID_STEP))
    occupied = {(int(head.xcor()), int(head.ycor()))}
    for seg in segments:
        occupied.add((int(seg.xcor()), int(seg.ycor())))

    # Attempt random selections first
    for _ in range(100):
        new_x = random.choice(grid_coords)
        new_y = random.choice(grid_coords)
        if (new_x, new_y) not in occupied:
            return new_x, new_y

    # Fallback default
    return 0, 100


# ---------------------------------------------------------
# UI & Scoreboard Updates
# ---------------------------------------------------------
def update_score_display():
    """Render the current score and high score."""
    score_pen.clear()
    score_pen.color("black")
    score_pen.write(
        f"Score : {score}   High Score : {high_score}",
        align="center",
        font=("Georgia", 20, "bold")
    )


def draw_buttons():
    """Draw and setup interactive Pause and Resume buttons."""
    # Pause button
    pause_button.goto(260, 275)
    pause_button.showturtle()
    pause_button.onclick(pause_game)

    # Resume button
    resume_button.goto(260, 235)
    resume_button.showturtle()
    resume_button.onclick(resume_game)

    # Labels
    button_label_pen.clear()
    button_label_pen.color("black")
    button_label_pen.goto(260, 258)
    button_label_pen.write("Pause", align="center", font=("Georgia", 10, "bold"))
    button_label_pen.goto(260, 218)
    button_label_pen.write("Resume", align="center", font=("Georgia", 10, "bold"))


# ---------------------------------------------------------
# Game Over and Reset
# ---------------------------------------------------------
def trigger_game_over():
    """
    Displays the 'Game Over !' notification prominently, prevents
    immediate erasing, and schedules a clean reset.
    """
    global game_state
    if game_state == STATE_GAME_OVER:
        return
    game_state = STATE_GAME_OVER

    # Render Game Over text with screen update so it is clearly visible
    overlay_pen.clear()
    overlay_pen.color("red")
    overlay_pen.goto(0, 50)
    overlay_pen.write("Game Over !", align="center", font=("Arial", 46, "bold"))
    overlay_pen.goto(0, 10)
    overlay_pen.color("#333333")
    overlay_pen.write("Restarting in a moment (or Press Enter)...", align="center", font=("Georgia", 13, "bold"))
    screen.update()

    # Schedule clean reset after 1500ms without blocking GUI thread
    screen.ontimer(reset_game, 1500)


def reset_game():
    """Cleans up snake segments, resets score and speed, and starts fresh."""
    global score, current_delay_ms, game_state, last_moved_direction

    if game_state != STATE_GAME_OVER:
        return

    overlay_pen.clear()

    # Proper memory cleanup for turtle segments
    for seg in segments:
        seg.hideturtle()
        seg.clear()
    segments.clear()

    # Reset snake state
    head.goto(0, 0)
    head.direction = "Stop"
    last_moved_direction = "Stop"

    # Reset score and speed
    score = 0
    current_delay_ms = INITIAL_DELAY_MS
    update_score_display()

    # Reposition food
    food.goto(0, 100)

    # Resume gameplay loop
    game_state = STATE_PLAYING
    screen.update()
    screen.ontimer(game_tick, current_delay_ms)


# ---------------------------------------------------------
# Main Game Loop (Event-Driven using ontimer)
# ---------------------------------------------------------
def game_tick():
    """Single tick of the gameplay loop driven by screen.ontimer."""
    global score, high_score, current_delay_ms

    if game_state == STATE_PLAYING:
        # 1. Check Wall Collision
        if (
            head.xcor() > BOUNDARY_LIMIT
            or head.xcor() < -BOUNDARY_LIMIT
            or head.ycor() > BOUNDARY_LIMIT
            or head.ycor() < -BOUNDARY_LIMIT
        ):
            trigger_game_over()
            return  # Stop tick; reset_game will resume ontimer

        # 2. Check Food Collision
        if head.distance(food) < 20:
            new_x, new_y = generate_food_position()
            food.goto(new_x, new_y)

            # Add new segment to snake body
            new_segment = turtle.Turtle()
            new_segment.speed(0)
            new_segment.shape("square")
            new_segment.color("orange")
            new_segment.penup()
            segments.append(new_segment)

            # Increase score and adjust speed
            score += 10
            if score > high_score:
                high_score = score
                save_high_score(high_score)

            if current_delay_ms > MIN_DELAY_MS:
                current_delay_ms -= SPEED_DECREMENT_MS

            update_score_display()

        # 3. Move Segments (from tail to neck) only when actively moving
        if head.direction != "Stop":
            for i in range(len(segments) - 1, 0, -1):
                segments[i].goto(segments[i - 1].xcor(), segments[i - 1].ycor())

            if len(segments) > 0:
                segments[0].goto(head.xcor(), head.ycor())

            # 4. Advance Snake Head
            move()

            # 5. Check Self-Collision
            collision_detected = False
            for segment in segments:
                if segment.distance(head) < 15:
                    collision_detected = True
                    break

            if collision_detected:
                trigger_game_over()
                return

        screen.update()

    # Re-schedule the next tick if not in Game Over state
    if game_state != STATE_GAME_OVER:
        screen.ontimer(game_tick, current_delay_ms)


# ---------------------------------------------------------
# Game Start Controller
# ---------------------------------------------------------
def start_game():
    """Initializes the gameplay view and starts the game loop."""
    global game_state, high_score

    # Prevent starting multiple times on repeat Enter presses
    if game_state != STATE_WELCOME:
        return

    clear_welcome_screen()

    # Load high score
    high_score = load_high_score()
    update_score_display()

    # Show buttons and game elements
    draw_buttons()
    head.goto(0, 0)
    head.showturtle()
    food.goto(0, 100)
    food.showturtle()

    game_state = STATE_PLAYING
    screen.update()

    # Kick off the event loop
    screen.ontimer(game_tick, current_delay_ms)


# ---------------------------------------------------------
# Key Bindings and Entry Point
def handle_enter():
    """Handle Enter key depending on current game state."""
    if game_state == STATE_WELCOME:
        start_game()
    elif game_state == STATE_GAME_OVER:
        reset_game()


def quit_game():
    """Cleanly closes the game window."""
    try:
        screen.bye()
    except Exception:
        pass


def setup_controls():
    """Configure keyboard listeners for controls and navigation."""
    screen.listen()

    # Movement controls (Arrow keys)
    screen.onkeypress(go_up, "Up")
    screen.onkeypress(go_down, "Down")
    screen.onkeypress(go_left, "Left")
    screen.onkeypress(go_right, "Right")

    # Alternative WASD controls
    screen.onkeypress(go_up, "w")
    screen.onkeypress(go_up, "W")
    screen.onkeypress(go_down, "s")
    screen.onkeypress(go_down, "S")
    screen.onkeypress(go_left, "a")
    screen.onkeypress(go_left, "A")
    screen.onkeypress(go_right, "d")
    screen.onkeypress(go_right, "D")

    # Start or Restart game on Enter / Return
    screen.onkey(handle_enter, "Return")

    # Pause / Resume toggles via keyboard
    screen.onkey(toggle_pause, "p")
    screen.onkey(toggle_pause, "P")
    screen.onkey(toggle_pause, "space")

    # Clean exit
    screen.onkey(quit_game, "Escape")
    screen.onkey(quit_game, "q")
    screen.onkey(quit_game, "Q")


def main():
    """Main application entry point."""
    setup_controls()
    display_welcome_screen()
    turtle.mainloop()


if __name__ == "__main__":
    main()
