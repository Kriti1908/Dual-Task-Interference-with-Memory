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
    {
        "file": "image2.jpeg",
        "question": "Who is in the image?",
        "options": ["Jethalal", "Bhide"],
        "correct_option": 0
    },
    # Add entries for all 12 images here
    {
        "file": "image3.jpg",
        "question": "Movie?",
        "options": ["Kahani", "3 Idiots"],
        "correct_option": 0
    },
    {
        "file": "image4.jpeg",
        "question": "Us?",
        "options": ["US!!", "You need therapy"],
        "correct_option": 1
    },
    {
        "file": "image5.jpeg",
        "question": "...",
        "options": ["HAHAHA", "haha"],
        "correct_option": 0
    },
    {
        "file": "image6.jpeg",
        "question": "What are you?",
        "options": ["Idiot Sandwich", "Bored"],
        "correct_option": 1
    },
    {
        "file": "image7.jpg",
        "question": "Red or blue pill?",
        "options": ["Red", "Blue"],
        "correct_option": 0
    },
    {
        "file": "image8.jpeg",
        "question": "What is this?",
        "options": ["Dog", "Frog"],
        "correct_option": 1
    },
    {
        "file": "image9.jpeg",
        "question": "Pineapple on pizza?",
        "options": ["Yayyy", "Nayyy"],
        "correct_option": 0
    },
    {
        "file": "image10.png",
        "question": "Android or Iphone?",
        "options": ["Iphone", "Android"],
        "correct_option": 1
    },
    {
        "file": "image11.jpeg",
        "question": "?",
        "options": ["yuh-uh", "nuh-uh"],
        "correct_option": 0
    },
    {
        "file": "image12.jpeg",
        "question": "Did I make you smile?",
        "options": ["Yes", "No"],
        "correct_option": 1
    }
]

# Initialize pygame
pygame.init()
mixer.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Grid settings
GRID_SIZE = 3
CELL_SIZE = 80
GRID_MARGIN = 2
GRID_OFFSET_X = (WINDOW_WIDTH - (CELL_SIZE + GRID_MARGIN) * GRID_SIZE) // 2
GRID_OFFSET_Y = (WINDOW_HEIGHT - (CELL_SIZE + GRID_MARGIN) * GRID_SIZE) // 2 - 50

# Game parameters
NUM_ACTIVATED_SQUARES = 6
PATTERN_PRESENTATION_TIME = 6  # seconds (changed from 4 to 6)
DELAY_TIME = 2  # seconds
ACTIVATION_DURATION = PATTERN_PRESENTATION_TIME / NUM_ACTIVATED_SQUARES  # seconds per square
NUM_TRIALS = 10  # Total number of actual trials (excluding practice)
NUM_PRACTICE_TRIALS = 2  # Number of practice trials
FEEDBACK_DURATION = 3  # seconds

# Function to create a random pattern
def create_random_pattern():
    all_positions = [(row, col) for row in range(GRID_SIZE) for col in range(GRID_SIZE)]
    return random.sample(all_positions, NUM_ACTIVATED_SQUARES)

# Function to draw grid
def draw_grid(screen, activated=None, user_selection=None, selection_order=None):
    if activated is None:
        activated = []
    if user_selection is None:
        user_selection = []
    if selection_order is None:
        selection_order = {}
    
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = pygame.Rect(
                GRID_OFFSET_X + (CELL_SIZE + GRID_MARGIN) * col,
                GRID_OFFSET_Y + (CELL_SIZE + GRID_MARGIN) * row,
                CELL_SIZE,
                CELL_SIZE
            )
            
            # Determine cell color
            if (row, col) in activated:
                color = RED
            elif (row, col) in user_selection:
                color = BLUE
            else:
                color = GRAY
                
            pygame.draw.rect(screen, color, rect)
            
            # Draw selection order number if applicable
            if (row, col) in selection_order:
                font = pygame.font.SysFont(None, 36)
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

# Function to draw text
def draw_text(screen, text, font_size, x, y, color=BLACK):
    font = pygame.font.SysFont(None, font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

# Function to create input text box
def text_input_screen(screen, prompt, max_chars=20):
    clock = pygame.time.Clock()
    input_box = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2, 300, 50)
    color_inactive = GRAY
    color_active = BLACK
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
        
        screen.fill(WHITE)
        draw_text(screen, prompt, 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100)
        
        # Render the input box
        pygame.draw.rect(screen, color, input_box, 2)
        
        # Render the current text
        font = pygame.font.SysFont(None, 36)
        txt_surface = font.render(text, True, BLACK)
        width = max(300, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return text

# Function to collect user information (removed name collection)
def collect_user_info(screen):
    user_info = {}
    
    # Age input (numeric only)
    age_text = ""
    while not age_text.isdigit() or age_text == "":
        age_text = text_input_screen(screen, "Enter your age (numbers only):")
        if age_text and not age_text.isdigit():
            # Show error message
            screen.fill(WHITE)
            draw_text(screen, "Please enter numbers only for age", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            pygame.display.flip()
            pygame.time.delay(1500)
    
    user_info['age'] = int(age_text)
    
    # Gender selection
    gender_options = ["Male", "Female", "Other", "Prefer not to say"]
    selected = False
    selection = 0
    
    while not selected:
        screen.fill(WHITE)
        draw_text(screen, "Select your gender:", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3)
        
        for i, option in enumerate(gender_options):
            color = BLUE if i == selection else BLACK
            draw_text(screen, option, 32, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + i * 60, color)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selection = (selection - 1) % len(gender_options)
                elif event.key == pygame.K_DOWN:
                    selection = (selection + 1) % len(gender_options)
                elif event.key == pygame.K_RETURN:
                    user_info['gender'] = gender_options[selection]
                    selected = True
    
    user_info['start_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return user_info

# Function to save results
def save_results(user_info, trial_results):
    # Create results directory if it doesn't exist
    if not os.path.exists("results"):
        os.makedirs("results")
    
    # Define the CSV file path
    filename = "results/memory_task_results.csv"
    
    # Check if the file exists
    file_exists = os.path.isfile(filename)
    
    # Open the file in append mode
    with open(filename, mode='a', newline='') as csvfile:
        fieldnames = [
            "age", "gender", "start_time", "trial_index", 
            "accuracy", "reaction_time", "image_shown", "response_correct"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the header only if the file is new
        if not file_exists:
            writer.writeheader()
        
        # Write each trial result to the CSV file
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

# Function to calculate accuracy between pattern and user selection
def calculate_accuracy(pattern, user_selection, user_order):
    # Location accuracy
    if not user_selection:  # If user didn't select anything
        location_accuracy = 0
    else:
        correct_locations = set(pattern).intersection(set(user_selection))
        location_accuracy = len(correct_locations) / NUM_ACTIVATED_SQUARES
    
    # Order accuracy
    order_accuracy = 0
    if user_order and len(user_order) > 0:
        correct_order = 0
        for i, pos in enumerate(pattern):
            if pos in user_order and user_order[pos] == i + 1:
                correct_order += 1
        order_accuracy = correct_order / NUM_ACTIVATED_SQUARES
    
    return (location_accuracy + order_accuracy) / 2  # Average of both accuracies

# Function to display image and question
def display_image_question(screen, image_index):
    # Get image data
    image_data = IMAGE_DATA[image_index % len(IMAGE_DATA)]
    
    # Define image display parameters
    image_width = 400
    image_height = 300
    image_rect = pygame.Rect(
        (WINDOW_WIDTH - image_width) // 2,
        150,
        image_width,
        image_height
    )
    
    # Load the image
    try:
        image_path = os.path.join("images", image_data["file"])
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, (image_width, image_height))
    except pygame.error:
        # Create placeholder if image can't be loaded
        image = pygame.Surface((image_width, image_height))
        image.fill(GRAY)
        draw_text(image, f"Image #{image_index}", 36, image_width // 2, image_height // 2)
    
    # Get question and options
    question = image_data["question"]
    options = image_data["options"]
    correct_option = image_data["correct_option"]
    
    # Button parameters
    button_width = 300
    button_height = 50
    button_margin = 20
    button_rects = [
        pygame.Rect((WINDOW_WIDTH - button_width) // 2, 480, button_width, button_height),
        pygame.Rect((WINDOW_WIDTH - button_width) // 2, 480 + button_height + button_margin, button_width, button_height)
    ]
    
    selected = None
    while selected is None:
        # Draw background
        screen.fill(WHITE)
        
        # Draw question
        draw_text(screen, question, 36, WINDOW_WIDTH // 2, 100)
        
        # Draw image
        screen.blit(image, image_rect)
        
        # Draw options
        for i, (rect, option) in enumerate(zip(button_rects, options)):
            # Check if mouse is over the button
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = rect.collidepoint(mouse_pos)
            
            pygame.draw.rect(screen, BLUE if is_hovered else GRAY, rect)
            draw_text(screen, option, 24, rect.centerx, rect.centery, WHITE)
        
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        selected = i
                        break
    
    # Check if selected option is correct
    response_correct = selected == correct_option
    
    return {
        "image_shown": image_index,
        "response_correct": response_correct
    }

def run_trial(screen, image_index, is_practice=False):
    clock = pygame.time.Clock()
    
    # Create random pattern
    pattern = create_random_pattern()
    
    # Phase 1: Show instructions
    screen.fill(WHITE)
    if is_practice:
        instructions = "PRACTICE ROUND: Remember the pattern!"
    else:
        instructions = "Remember the pattern!"
    draw_text(screen, instructions, 36, WINDOW_WIDTH // 2, 100)
    draw_text(screen, "Starting in 3 seconds...", 30, WINDOW_WIDTH // 2, 150)
    pygame.display.flip()
    pygame.time.delay(3000)
    
    # Phase 2: Present pattern one square at a time
    activation_start_time = time.time()
    current_square_index = 0
    pattern_complete = False
    
    while not pattern_complete:
        current_time = time.time()
        elapsed = current_time - activation_start_time
        
        # Determine which square should be active now
        square_index = int(elapsed / ACTIVATION_DURATION)
        if square_index >= NUM_ACTIVATED_SQUARES:
            pattern_complete = True
            continue
        
        if square_index != current_square_index:
            current_square_index = square_index
        
        # Draw grid with only the current square activated
        screen.fill(WHITE)
        draw_text(screen, "Remember this pattern", 36, WINDOW_WIDTH // 2, 100)
        current_active = [pattern[current_square_index]] if current_square_index < len(pattern) else []
        draw_grid(screen, activated=current_active)
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
        
        clock.tick(FPS)
    
    # Phase 3: Delay period
    delay_start_time = time.time()
    delay_ongoing = True
    
    while delay_ongoing:
        current_time = time.time()
        elapsed = current_time - delay_start_time
        
        if elapsed >= DELAY_TIME:
            delay_ongoing = False
            continue
        
        # Draw blank screen with instructions
        screen.fill(WHITE)
        draw_text(screen, "Wait...", 36, WINDOW_WIDTH // 2, 100)
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
        
        clock.tick(FPS)
    
    # Phase 4: Display image and question
    image_response = display_image_question(screen, image_index)
    if image_response is None:  # User quit during image question
        pygame.quit()
        return None
    
    # Phase 5: Recall
    recall_start_time = time.time()
    user_selection = []
    selection_order = {}
    recall_complete = False
    
    while not recall_complete:
        # Draw grid for selection
        screen.fill(WHITE)
        draw_text(screen, "Reproduce the pattern in order", 36, WINDOW_WIDTH // 2, 100)
        
        draw_grid(screen, user_selection=user_selection, selection_order=selection_order)
        
        if len(user_selection) == NUM_ACTIVATED_SQUARES:
            draw_text(screen, "Press ENTER to continue", 30, WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100)
        
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                cell = get_cell_from_pos(event.pos)
                if cell:
                    if cell in user_selection:
                        # Remove cell if already selected
                        user_selection.remove(cell)
                        # Update order for remaining cells
                        removed_order = selection_order[cell]
                        del selection_order[cell]
                        for pos, order in list(selection_order.items()):
                            if order > removed_order:
                                selection_order[pos] = order - 1
                    elif len(user_selection) < NUM_ACTIVATED_SQUARES:
                        # Add cell to selection
                        user_selection.append(cell)
                        selection_order[cell] = len(user_selection)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(user_selection) == NUM_ACTIVATED_SQUARES:
                    recall_complete = True
        
        clock.tick(FPS)
    
    # Calculate reaction time
    reaction_time = time.time() - recall_start_time
    
    # Calculate accuracy
    accuracy = calculate_accuracy(pattern, user_selection, selection_order)
    
    # Return trial results
    trial_result = {
        "pattern": pattern,
        "user_selection": user_selection,
        "user_order": {str(k): v for k, v in selection_order.items()},  # Convert tuple keys to strings for JSON
        "accuracy": accuracy,
        "reaction_time": reaction_time,
        "image_shown": image_response["image_shown"],
        "response_correct": image_response["response_correct"]
    }
    
    # Show feedback screen
    screen.fill(WHITE)
    if is_practice:
        draw_text(screen, f"Practice round complete! Accuracy: {accuracy:.2%}", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)
        draw_text(screen, "Next round starts in 3 seconds", 30, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)
    else:
        draw_text(screen, "Well done! Next starts in 3 secs", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    pygame.display.flip()
    pygame.time.delay(FEEDBACK_DURATION * 1000)
    
    return trial_result

def show_results_screen(screen, trial_results):
    screen.fill(WHITE)
    draw_text(screen, "Experiment Complete!", 48, WINDOW_WIDTH // 2, 100)
    
    # Calculate overall accuracy
    total_accuracy = sum(trial["accuracy"] for trial in trial_results) / len(trial_results)
    draw_text(screen, f"Overall Accuracy: {total_accuracy:.2%}", 36, WINDOW_WIDTH // 2, 200)
    
    # Calculate image question performance
    correct_responses = sum(1 for trial in trial_results if trial["response_correct"])
    draw_text(screen, f"Image Questions Correct: {correct_responses}/{len(trial_results)}", 30, WINDOW_WIDTH // 2, 250)
    
    draw_text(screen, "Thank you for participating!", 36, WINDOW_WIDTH // 2, 400)
    draw_text(screen, "Press any key to exit", 24, WINDOW_WIDTH // 2, 500)
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
    
    # Welcome screen
    screen.fill(WHITE)
    draw_text(screen, "Memory Task Experiment", 48, WINDOW_WIDTH // 2, 200)
    draw_text(screen, "Press any key to begin", 36, WINDOW_WIDTH // 2, 300)
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
    if user_info is None:  # User quit during info collection
        pygame.quit()
        return
    
    # Instructions screen
    screen.fill(WHITE)
    draw_text(screen, "Instructions", 48, WINDOW_WIDTH // 2, 100)
    instructions = [
        "You will see a pattern of 6 squares lighting up one by one.",
        "Try to remember both the positions AND the order they appear.",
        "After a short delay, you'll see an image with a question.",
        "After answering the question, you'll need to reproduce the pattern.",
        "We'll start with 2 practice rounds to help you get familiar."
    ]
    for i, line in enumerate(instructions):
        draw_text(screen, line, 24, WINDOW_WIDTH // 2, 200 + i * 40)
    
    draw_text(screen, "Press any key to start the practice rounds", 30, WINDOW_WIDTH // 2, 500)
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
        screen.fill(WHITE)
        draw_text(screen, f"Practice Round {i+1}/{NUM_PRACTICE_TRIALS}", 48, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        pygame.display.flip()
        pygame.time.delay(1500)
        
        result = run_trial(screen, i, is_practice=True)
        if result is None:  # User quit during trial
            pygame.quit()
            return
    
    # Show message before actual trials
    screen.fill(WHITE)
    draw_text(screen, "Practice complete", 48, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)
    draw_text(screen, "Now starting the actual experiment", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)
    pygame.display.flip()
    pygame.time.delay(2000)
    
    # Run actual trials
    trial_results = []
    for trial_idx in range(NUM_TRIALS):
        screen.fill(WHITE)
        draw_text(screen, f"Trial {trial_idx+1}/{NUM_TRIALS}", 48, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        pygame.display.flip()
        pygame.time.delay(1500)
        
        # Use NUM_PRACTICE_TRIALS + trial_idx for image index to avoid using the same images as practice
        result = run_trial(screen, NUM_PRACTICE_TRIALS + trial_idx, is_practice=False)
        if result is None:  # User quit during trial
            pygame.quit()
            return
        trial_results.append(result)
    
    # Show results
    show_results_screen(screen, trial_results)
    
    # Save results (only for actual trials, not practice)
    save_results(user_info, trial_results)
    
    pygame.quit()

if __name__ == "__main__":
    main()