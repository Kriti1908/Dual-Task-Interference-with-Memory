import pygame
import random
import time
import json
import os
import datetime
import numpy as np
from pygame import mixer
import csv
import os.path

# Define image data (questions and options)
IMAGE_DATA = [
    {
        "file": "image1.jpeg",
        "question": "What is shown in the image?",
        "options": ["Overwhelm", "Party"],
        "correct_option": 0  # 0-based index of the correct option
    },
    # Add entries for all 12 images here
    {
        "file": "image2.jpeg",
        "question": "Who is in the image?",
        "options": ["Jethalal", "Bhide"],
        "correct_option": 0
    },
    {
        "file": "image3.jpeg",
        "question": "What is shown in image?",
        "options": ["Batch hoodie UG2k23", "Scam 2024"],
        "correct_option": 0
    },
    {
        "file": "image4.jpeg",
        "question": "Who is this character?",
        "options": ["Pikachu", "Doraemon"],
        "correct_option": 1
    },
    {
        "file": "image5.jpeg",
        "question": "Name of trend?",
        "options": ["Rick roll", "Ice Bucket challenge"],
        "correct_option": 0
    },
    {
        "file": "image6.jpeg",
        "question": "What are you?",
        "options": ["Idiot Burger", "Idiot Sandwich"],
        "correct_option": 1
    }
]

# Initialize pygame
pygame.init()
mixer.init()

# Constants
WINDOW_WIDTH = 1000  # Increased width for better layout
WINDOW_HEIGHT = 700  # Increased height for better spacing
FPS = 60

# Modern color palette
DARK_BLUE = (13, 27, 42)
NAVY_BLUE = (27, 38, 59)
LIGHT_BLUE = (65, 90, 119)
CREAM = (224, 225, 221)
LIGHT_GRAY = (200, 200, 200)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (212, 175, 55)
GREEN = (46, 204, 113)
RED = (231, 76, 60)
BLUE = (52, 152, 219)

# Grid settings
GRID_SIZE = 3
CELL_SIZE = 100  # Larger cells for better visibility
GRID_MARGIN = 10  # Increased margin for cleaner look
GRID_OFFSET_X = (WINDOW_WIDTH - (CELL_SIZE + GRID_MARGIN) * GRID_SIZE) // 2
GRID_OFFSET_Y = (WINDOW_HEIGHT - (CELL_SIZE + GRID_MARGIN) * GRID_SIZE) // 2 

# Game parameters
NUM_ACTIVATED_SQUARES = 6
PATTERN_PRESENTATION_TIME = 6  # seconds (changed from 4 to 6)
DELAY_TIME = 2  # seconds
ACTIVATION_DURATION = PATTERN_PRESENTATION_TIME / NUM_ACTIVATED_SQUARES  # seconds per square
NUM_TRIALS = 5  # Total number of actual trials (excluding practice)
NUM_PRACTICE_TRIALS = 1  # Number of practice trials
FEEDBACK_DURATION = 3  # seconds

# Font setup
def get_font(size):
    try:
        # Try to load a modern, clean font (Arial if available)
        return pygame.font.SysFont("Arial", size)
    except:
        return pygame.font.SysFont(None, size)

# Function to create a random pattern
def create_random_pattern():
    all_positions = [(row, col) for row in range(GRID_SIZE) for col in range(GRID_SIZE)]
    return random.sample(all_positions, NUM_ACTIVATED_SQUARES)

# Function to draw grid with modern styling
def draw_grid(screen, activated=None, user_selection=None, selection_order=None):
    if activated is None:
        activated = []
    if user_selection is None:
        user_selection = []
    if selection_order is None:
        selection_order = {}
    
    # Draw grid background
    grid_background = pygame.Rect(
        GRID_OFFSET_X - GRID_MARGIN,
        GRID_OFFSET_Y - GRID_MARGIN,
        (CELL_SIZE + GRID_MARGIN) * GRID_SIZE + GRID_MARGIN,
        (CELL_SIZE + GRID_MARGIN) * GRID_SIZE + GRID_MARGIN
    )
    pygame.draw.rect(screen, NAVY_BLUE, grid_background, border_radius=10)
    
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = pygame.Rect(
                GRID_OFFSET_X + (CELL_SIZE + GRID_MARGIN) * col,
                GRID_OFFSET_Y + (CELL_SIZE + GRID_MARGIN) * row,
                CELL_SIZE,
                CELL_SIZE
            )
            
            # Determine cell color with modern styling
            if (row, col) in activated:
                color = GOLD
                border_color = (GOLD[0]-20, GOLD[1]-20, GOLD[2]-20)  # Slightly darker for border
            elif (row, col) in user_selection:
                color = BLUE
                border_color = (BLUE[0]-20, BLUE[1]-20, BLUE[2]-20)
            else:
                color = LIGHT_BLUE
                border_color = (LIGHT_BLUE[0]-20, LIGHT_BLUE[1]-20, LIGHT_BLUE[2]-20)
            
            # Draw cell with rounded corners and border
            pygame.draw.rect(screen, color, rect, border_radius=8)
            pygame.draw.rect(screen, border_color, rect, width=3, border_radius=8)
            
            # Draw selection order number if applicable
            if (row, col) in selection_order:
                font = get_font(36)
                order_text = font.render(str(selection_order[(row, col)]), True, WHITE)
                text_rect = order_text.get_rect(center=rect.center)
                screen.blit(order_text, text_rect)

# Function to get grid cell from mouse position
def get_cell_from_pos(pos):
    x, y = pos
    if (x < GRID_OFFSET_X or x >= GRID_OFFSET_X + (CELL_SIZE + GRID_MARGIN) * GRID_SIZE or
        y < GRID_OFFSET_Y or y >= GRID_OFFSET_Y + (CELL_SIZE + GRID_MARGIN) * GRID_SIZE):
        return None
    
    col = (x - GRID_OFFSET_X) // (CELL_SIZE + GRID_MARGIN)
    row = (y - GRID_OFFSET_Y) // (CELL_SIZE + GRID_MARGIN)
    
    return (row, col)

# Modern text drawing function with better typography
def draw_text(screen, text, font_size, x, y, color=WHITE, align="center", max_width=None):
    font = get_font(font_size)
    
    if max_width is not None:
        # Handle text wrapping
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width < max_width or not current_line:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, color)
            if align == "center":
                text_rect = text_surface.get_rect(center=(x, y + i * (font_size + 5)))
            elif align == "left":
                text_rect = text_surface.get_rect(midleft=(x, y + i * (font_size + 5)))
            screen.blit(text_surface, text_rect)
    else:
        text_surface = font.render(text, True, color)
        if align == "center":
            text_rect = text_surface.get_rect(center=(x, y))
        elif align == "left":
            text_rect = text_surface.get_rect(midleft=(x, y))
        screen.blit(text_surface, text_rect)

# Modern button class
class Button:
    def __init__(self, x, y, width, height, text, color=LIGHT_BLUE, hover_color=BLUE, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (color[0]-20, color[1]-20, color[2]-20), self.rect, width=3, border_radius=8)
        draw_text(screen, self.text, 24, self.rect.centerx, self.rect.centery, self.text_color)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def handle_event(self, event, callback=None):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if callback:
                callback()
            return True
        return False

# Modern input box
def text_input_screen(screen, prompt, max_chars=20):
    clock = pygame.time.Clock()
    input_box = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2, 300, 50)
    color_inactive = LIGHT_BLUE
    color_active = BLUE
    color = color_inactive
    active = True
    text = ''
    done = False
    
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                active = input_box.collidepoint(event.pos)
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        if len(text) < max_chars and event.unicode.isprintable():
                            text += event.unicode
        
        # Modern background
        screen.fill(DARK_BLUE)
        
        # Draw decorative elements
        pygame.draw.rect(screen, NAVY_BLUE, (0, 0, WINDOW_WIDTH, 100))
        draw_text(screen, "Memory Task Experiment", 36, WINDOW_WIDTH // 2, 50, GOLD)
        
        draw_text(screen, prompt, 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100, WHITE)
        
        # Render the input box with modern styling
        pygame.draw.rect(screen, color, input_box, border_radius=8)
        pygame.draw.rect(screen, (color[0]-20, color[1]-20, color[2]-20), input_box, width=3, border_radius=8)
        
        # Render the current text
        font = get_font(36)
        txt_surface = font.render(text, True, WHITE)
        width = max(300, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 10, input_box.y + 10))
        
        # Draw hint text if empty
        if not text and not active:
            hint_font = get_font(24)
            hint_surface = hint_font.render("Type here...", True, (200, 200, 200))
            screen.blit(hint_surface, (input_box.x + 10, input_box.y + 10))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return text

# Modern gender selection screen
def collect_user_info(screen):
    user_info = {}
    
    # Age input (numeric only)
    age_text = ""
    while not age_text.isdigit() or age_text == "":
        age_text = text_input_screen(screen, "Enter your age (numbers only):")
        if age_text and not age_text.isdigit():
            # Show error message with modern styling
            screen.fill(DARK_BLUE)
            pygame.draw.rect(screen, NAVY_BLUE, (0, 0, WINDOW_WIDTH, 100))
            draw_text(screen, "Memory Task Experiment", 36, WINDOW_WIDTH // 2, 50, GOLD)
            draw_text(screen, "Please enter numbers only for age", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, RED)
            pygame.display.flip()
            pygame.time.delay(1500)
    
    user_info['age'] = int(age_text)
    
    # Gender selection with modern buttons
    gender_options = ["Male", "Female", "Other", "Prefer not to say"]
    selected = False
    selection = None
    
    # Create buttons
    buttons = []
    button_width = 300
    button_height = 60
    button_margin = 20
    start_y = WINDOW_HEIGHT // 2 - (len(gender_options) * (button_height + button_margin)) // 2
    
    for i, option in enumerate(gender_options):
        buttons.append(Button(
            WINDOW_WIDTH // 2 - button_width // 2,
            start_y + i * (button_height + button_margin),
            button_width,
            button_height,
            option
        ))
    
    while not selected:
        screen.fill(DARK_BLUE)
        
        # Draw header
        pygame.draw.rect(screen, NAVY_BLUE, (0, 0, WINDOW_WIDTH, 100))
        draw_text(screen, "Memory Task Experiment", 36, WINDOW_WIDTH // 2, 50, GOLD)
        draw_text(screen, "Select your gender:", 36, WINDOW_WIDTH // 2, 150, WHITE)
        
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw buttons
        for i, button in enumerate(buttons):
            button.check_hover(mouse_pos)
            button.draw(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, button in enumerate(buttons):
                    if button.is_hovered:
                        selection = gender_options[i]
                        selected = True
    
    user_info['gender'] = selection
    user_info['start_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return user_info

# Function to save results (unchanged)
def save_results(user_info, trial_results):
    if not os.path.exists("results"):
        os.makedirs("results")
    
    filename = "results/dual_task_data.csv"
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode='a', newline='') as csvfile:
        fieldnames = [
            "age", "gender", "start_time", "trial_index", 
            "accuracy", "reaction_time", "image_shown", "response_correct"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        for trial_index, trial in enumerate(trial_results):
            row = {
                "age": user_info["age"],
                "gender": user_info["gender"],
                "start_time": user_info["start_time"],
                "trial_index": trial_index + 1,
                "accuracy": trial["accuracy"],
                "reaction_time": trial["reaction_time"],
                "image_shown": trial["image_shown"],
                "response_correct": trial["response_correct"]
            }
            writer.writerow(row)

# Function to calculate accuracy (unchanged)
def calculate_accuracy(pattern, user_selection, user_order):
    if not user_selection:
        location_accuracy = 0
    else:
        correct_locations = set(pattern).intersection(set(user_selection))
        location_accuracy = len(correct_locations) / NUM_ACTIVATED_SQUARES
    
    order_accuracy = 0
    if user_order and len(user_order) > 0:
        correct_order = 0
        for i, pos in enumerate(pattern):
            if pos in user_order and user_order[pos] == i + 1:
                correct_order += 1
        order_accuracy = correct_order / NUM_ACTIVATED_SQUARES
    
    return (location_accuracy + order_accuracy) / 2

# Modern image and question display
def display_image_question(screen, image_index):
    image_data = IMAGE_DATA[image_index % len(IMAGE_DATA)]
    
    # Image display parameters
    image_width = 500
    image_height = 350
    image_rect = pygame.Rect(
        (WINDOW_WIDTH - image_width) // 2,
        180,
        image_width,
        image_height
    )
    
    # Load the image
    try:
        image_path = os.path.join("images", image_data["file"])
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, (image_width, image_height))
    except pygame.error:
        image = pygame.Surface((image_width, image_height))
        image.fill(LIGHT_BLUE)
        draw_text(image, f"Image #{image_index}", 36, image_width // 2, image_height // 2)
    
    # Create buttons for options
    button_width = 400
    button_height = 60
    button_margin = 20
    button_rects = [
        Button((WINDOW_WIDTH - button_width) // 2, 550, button_width, button_height, image_data["options"][0]),
        Button((WINDOW_WIDTH - button_width) // 2, 550 + button_height + button_margin, button_width, button_height, image_data["options"][1])
    ]
    
    correct_option = image_data["correct_option"]
    selected = None
    
    while selected is None:
        screen.fill(DARK_BLUE)
        
        # Draw header
        pygame.draw.rect(screen, NAVY_BLUE, (0, 0, WINDOW_WIDTH, 100))
        draw_text(screen, "Memory Task Experiment", 36, WINDOW_WIDTH // 2, 50, GOLD)
        
        # Draw question
        draw_text(screen, image_data["question"], 36, WINDOW_WIDTH // 2, 140, WHITE)
        
        # Draw image with border
        pygame.draw.rect(screen, WHITE, image_rect.inflate(10, 10), border_radius=8)
        pygame.draw.rect(screen, GOLD, image_rect.inflate(10, 10), width=3, border_radius=8)
        screen.blit(image, image_rect)
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for i, button in enumerate(button_rects):
            button.check_hover(mouse_pos)
            button.draw(screen)
        
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            
            for i, button in enumerate(button_rects):
                if button.handle_event(event):
                    selected = i
    
    response_correct = selected == correct_option
    
    return {
        "image_shown": image_index,
        "response_correct": response_correct
    }

# Modern trial function with improved visual feedback
def run_trial(screen, image_index, is_practice=False):
    clock = pygame.time.Clock()
    pattern = create_random_pattern()
    
    # Phase 1: Show instructions with modern styling
    screen.fill(DARK_BLUE)
    pygame.draw.rect(screen, NAVY_BLUE, (0, 0, WINDOW_WIDTH, 100))
    draw_text(screen, "Memory Task Experiment", 36, WINDOW_WIDTH // 2, 50, GOLD)
    
    if is_practice:
        draw_text(screen, "PRACTICE ROUND", 36, WINDOW_WIDTH // 2, 180, GOLD)
        draw_text(screen, "Remember the pattern!", 30, WINDOW_WIDTH // 2, 230, WHITE)
    else:
        draw_text(screen, "Remember the pattern!", 36, WINDOW_WIDTH // 2, 200, WHITE)
    
    # Countdown with modern styling
    for i in range(3, 0, -1):
        screen.fill(DARK_BLUE, (0, 300, WINDOW_WIDTH, 100))
        draw_text(screen, f"Starting in {i}...", 48, WINDOW_WIDTH // 2, 350, GOLD)
        pygame.display.flip()
        pygame.time.delay(1000)
    
    # Phase 2: Present pattern with smooth transitions
    activation_start_time = time.time()
    current_square_index = 0
    pattern_complete = False
    
    while not pattern_complete:
        current_time = time.time()
        elapsed = current_time - activation_start_time
        
        square_index = int(elapsed / ACTIVATION_DURATION)
        if square_index >= NUM_ACTIVATED_SQUARES:
            pattern_complete = True
            continue
        
        if square_index != current_square_index:
            current_square_index = square_index
        
        # Draw with modern styling
        screen.fill(DARK_BLUE)
        pygame.draw.rect(screen, NAVY_BLUE, (0, 0, WINDOW_WIDTH, 100))
        draw_text(screen, "Memory Task Experiment", 36, WINDOW_WIDTH // 2, 50, GOLD)
        draw_text(screen, "Remember this pattern", 36, WINDOW_WIDTH // 2, 150, WHITE)
        
        current_active = [pattern[current_square_index]] if current_square_index < len(pattern) else []
        draw_grid(screen, activated=current_active)
        
        # Progress indicator
        progress_width = 300
        progress_height = 20
        progress_rect = pygame.Rect(
            (WINDOW_WIDTH - progress_width) // 2,
            WINDOW_HEIGHT - 100,
            progress_width * (elapsed / PATTERN_PRESENTATION_TIME),
            progress_height
        )
        pygame.draw.rect(screen, NAVY_BLUE, ((WINDOW_WIDTH - progress_width) // 2, WINDOW_HEIGHT - 100, progress_width, progress_height), border_radius=10)
        pygame.draw.rect(screen, GOLD, progress_rect, border_radius=10)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
        
        clock.tick(FPS)
    
    # Phase 3: Modern delay screen
    delay_start_time = time.time()
    delay_ongoing = True
    
    while delay_ongoing:
        current_time = time.time()
        elapsed = current_time - delay_start_time
        
        if elapsed >= DELAY_TIME:
            delay_ongoing = False
            continue
        
        screen.fill(DARK_BLUE)
        pygame.draw.rect(screen, NAVY_BLUE, (0, 0, WINDOW_WIDTH, 100))
        draw_text(screen, "Memory Task Experiment", 36, WINDOW_WIDTH // 2, 50, GOLD)
        draw_text(screen, "Wait...", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, WHITE)
        
        # Animated ellipsis
        dot_count = int(elapsed * 2) % 4
        draw_text(screen, "." * dot_count, 48, WINDOW_WIDTH // 2 + 50, WINDOW_HEIGHT // 2, WHITE)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
        
        clock.tick(FPS)
    
    # Phase 4: Display image and question
    image_response = display_image_question(screen, image_index)
    if image_response is None:
        pygame.quit()
        return None
    
    # Phase 5: Modern recall screen
    recall_start_time = time.time()
    user_selection = []
    selection_order = {}
    recall_complete = False
    
    while not recall_complete:
        screen.fill(DARK_BLUE)
        pygame.draw.rect(screen, NAVY_BLUE, (0, 0, WINDOW_WIDTH, 100))
        draw_text(screen, "Memory Task Experiment", 36, WINDOW_WIDTH // 2, 50, GOLD)
        draw_text(screen, "Reproduce the pattern in order", 36, WINDOW_WIDTH // 2, 150, WHITE)
        
        draw_grid(screen, user_selection=user_selection, selection_order=selection_order)
        
        if len(user_selection) == NUM_ACTIVATED_SQUARES:
            draw_text(screen, "Press ENTER to continue", 30, WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100, GOLD)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                cell = get_cell_from_pos(event.pos)
                if cell:
                    if cell in user_selection:
                        user_selection.remove(cell)
                        removed_order = selection_order[cell]
                        del selection_order[cell]
                        for pos, order in list(selection_order.items()):
                            if order > removed_order:
                                selection_order[pos] = order - 1
                    elif len(user_selection) < NUM_ACTIVATED_SQUARES:
                        user_selection.append(cell)
                        selection_order[cell] = len(user_selection)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(user_selection) == NUM_ACTIVATED_SQUARES:
                    recall_complete = True
        
        clock.tick(FPS)
    
    reaction_time = time.time() - recall_start_time
    accuracy = calculate_accuracy(pattern, user_selection, selection_order)
    
    trial_result = {
        "pattern": pattern,
        "user_selection": user_selection,
        "user_order": {str(k): v for k, v in selection_order.items()},
        "accuracy": accuracy,
        "reaction_time": reaction_time,
        "image_shown": image_response["image_shown"],
        "response_correct": image_response["response_correct"]
    }
    
    # Modern feedback screen
    screen.fill(DARK_BLUE)
    pygame.draw.rect(screen, NAVY_BLUE, (0, 0, WINDOW_WIDTH, 100))
    draw_text(screen, "Memory Task Experiment", 36, WINDOW_WIDTH // 2, 50, GOLD)
    
    if is_practice:
        draw_text(screen, "Practice round complete!", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80, WHITE)
        draw_text(screen, f"Accuracy: {accuracy:.2%}", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30, GREEN if accuracy > 0.7 else RED)
        draw_text(screen, "Next round starts in 3 seconds", 30, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50, LIGHT_BLUE)
    else:
        draw_text(screen, "Well done!", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30, WHITE)
        draw_text(screen, "Next starts in 3 secs", 30, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20, LIGHT_BLUE)
    
    pygame.display.flip()
    pygame.time.delay(FEEDBACK_DURATION * 1000)
    
    return trial_result

# Modern results screen
def show_results_screen(screen, trial_results):
    screen.fill(DARK_BLUE)
    pygame.draw.rect(screen, NAVY_BLUE, (0, 0, WINDOW_WIDTH, 100))
    draw_text(screen, "Memory Task Experiment", 36, WINDOW_WIDTH // 2, 50, GOLD)
    draw_text(screen, "Experiment Complete!", 48, WINDOW_WIDTH // 2, 180, WHITE)
    
    # Calculate overall accuracy
    total_accuracy = sum(trial["accuracy"] for trial in trial_results) / len(trial_results)
    draw_text(screen, f"Overall Accuracy: {total_accuracy:.2%}", 36, WINDOW_WIDTH // 2, 280, 
             GREEN if total_accuracy > 0.7 else RED)
    
    # Calculate image question performance
    correct_responses = sum(1 for trial in trial_results if trial["response_correct"])
    draw_text(screen, f"Image Questions Correct: {correct_responses}/{len(trial_results)}", 30, WINDOW_WIDTH // 2, 330, 
             GREEN if correct_responses/len(trial_results) > 0.7 else RED)
    
    draw_text(screen, "Thank you for participating!", 36, WINDOW_WIDTH // 2, 450, WHITE)
    draw_text(screen, "Press any key to exit", 24, WINDOW_WIDTH // 2, 550, LIGHT_BLUE)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                waiting = False

def main():
    # Set up the display
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Memory Task Experiment")
    clock = pygame.time.Clock()
    
    # Modern welcome screen
    screen.fill(DARK_BLUE)
    pygame.draw.rect(screen, NAVY_BLUE, (0, 0, WINDOW_WIDTH, 100))
    draw_text(screen, "Memory Task Experiment", 48, WINDOW_WIDTH // 2, 50, GOLD)
    draw_text(screen, "Welcome!", 48, WINDOW_WIDTH // 2, 250, WHITE)
    draw_text(screen, "Press any key to begin", 36, WINDOW_WIDTH // 2, 350, LIGHT_BLUE)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                waiting = False
    
    # Collect user information
    user_info = collect_user_info(screen)
    if user_info is None:
        pygame.quit()
        return
    
    # Modern instructions screen
    screen.fill(DARK_BLUE)
    pygame.draw.rect(screen, NAVY_BLUE, (0, 0, WINDOW_WIDTH, 100))
    draw_text(screen, "Memory Task Experiment", 36, WINDOW_WIDTH // 2, 50, GOLD)
    draw_text(screen, "Instructions", 48, WINDOW_WIDTH // 2, 180, WHITE)
    
    instructions = [
        "You will see a pattern of 6 squares lighting up one by one.",
        "Try to remember both the positions AND the order they appear.",
        "After a short delay, you'll see an image with a question.",
        "After answering the question, you'll need to reproduce the pattern.",
        "We'll start with 1 practice round to help you get familiar."
    ]
    
    for i, line in enumerate(instructions):
        draw_text(screen, line, 24, WINDOW_WIDTH // 2, 280 + i * 40, WHITE)
    
    draw_text(screen, "Press any key to start the practice round", 30, WINDOW_WIDTH // 2, 550, LIGHT_BLUE)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                waiting = False
    
    # Run practice trials
    for i in range(NUM_PRACTICE_TRIALS):
        screen.fill(DARK_BLUE)
        pygame.draw.rect(screen, NAVY_BLUE, (0, 0, WINDOW_WIDTH, 100))
        draw_text(screen, "Memory Task Experiment", 36, WINDOW_WIDTH // 2, 50, GOLD)
        draw_text(screen, f"Practice Round {i+1}/{NUM_PRACTICE_TRIALS}", 48, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, WHITE)
        pygame.display.flip()
        pygame.time.delay(1500)
        
        result = run_trial(screen, i, is_practice=True)
        if result is None:
            pygame.quit()
            return
    
    # Show message before actual trials
    screen.fill(DARK_BLUE)
    pygame.draw.rect(screen, NAVY_BLUE, (0, 0, WINDOW_WIDTH, 100))
    draw_text(screen, "Memory Task Experiment", 36, WINDOW_WIDTH // 2, 50, GOLD)
    draw_text(screen, "Practice complete", 48, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50, WHITE)
    draw_text(screen, "Now starting the actual experiment (5 trials)", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50, LIGHT_BLUE)
    pygame.display.flip()
    pygame.time.delay(2000)
    
    # Run actual trials
    trial_results = []
    for trial_idx in range(NUM_TRIALS):
        screen.fill(DARK_BLUE)
        pygame.draw.rect(screen, NAVY_BLUE, (0, 0, WINDOW_WIDTH, 100))
        draw_text(screen, "Memory Task Experiment", 36, WINDOW_WIDTH // 2, 50, GOLD)
        draw_text(screen, f"Trial {trial_idx+1}/{NUM_TRIALS}", 48, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, WHITE)
        pygame.display.flip()
        pygame.time.delay(1500)
        
        result = run_trial(screen, NUM_PRACTICE_TRIALS + trial_idx, is_practice=False)
        if result is None:
            pygame.quit()
            return
        trial_results.append(result)
    
    # Show results
    show_results_screen(screen, trial_results)
    
    # Save results
    save_results(user_info, trial_results)
    
    pygame.quit()

if __name__ == "__main__":
    main()