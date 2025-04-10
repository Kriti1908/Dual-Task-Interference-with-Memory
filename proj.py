import pygame
import random
import time
import json
import os
import datetime
import numpy as np
from pygame import mixer
import csv

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
PATTERN_PRESENTATION_TIME = 4  # seconds
DELAY_TIME = 2  # seconds
ACTIVATION_DURATION = PATTERN_PRESENTATION_TIME / NUM_ACTIVATED_SQUARES  # seconds per square
NUM_TRIALS = 10  # Total number of trials
FEEDBACK_DURATION = 3  # seconds

# Audio settings for dual task
HIGH_TONE_FREQ = 1000  # Hz
LOW_TONE_FREQ = 500  # Hz
TONE_DURATION = 0.2  # seconds

# Create tones
def generate_tone(frequency, duration):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    tone = np.sin(2 * np.pi * frequency * t)
    tone = np.int16(tone * 32767)
    if mixer.get_init()[2] == 1:  # Check if mixer is set to mono
        return pygame.sndarray.make_sound(tone)
    else:  # Duplicate the tone for stereo
        stereo_tone = np.column_stack((tone, tone))
        return pygame.sndarray.make_sound(stereo_tone)

high_tone = generate_tone(HIGH_TONE_FREQ, TONE_DURATION)
low_tone = generate_tone(LOW_TONE_FREQ, TONE_DURATION)

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
                # Draw selection order number
                if (row, col) in selection_order:
                    font = pygame.font.SysFont(None, 36)
                    order_text = font.render(str(selection_order[(row, col)]), True, WHITE)
                    text_rect = order_text.get_rect(center=rect.center)
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

# Function to collect user information
def collect_user_info(screen):
    user_info = {}
    
    user_info['name'] = text_input_screen(screen, "Enter your name:")
    
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
# def save_results(user_info, trial_results):
#     data = {
#         "user_info": user_info,
#         "trial_results": trial_results
#     }
    
#     # Create results directory if it doesn't exist
#     if not os.path.exists("results"):
#         os.makedirs("results")
    
#     # Check if file exists and load existing data
#     filename = "results/memory_task_results.json"
#     if os.path.exists(filename):
#         with open(filename, 'r') as f:
#             try:
#                 existing_data = json.load(f)
#             except json.JSONDecodeError:
#                 existing_data = []
#     else:
#         existing_data = []
    
#     # Append new data
#     if isinstance(existing_data, list):
#         existing_data.append(data)
#     else:
#         existing_data = [existing_data, data]
    
#     # Save updated data
#     with open(filename, 'w') as f:
#         json.dump(existing_data, f, indent=4)
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
            "name", "age", "gender", "start_time", "trial_index", "is_dual_task",
            "accuracy", "reaction_time", "high_tones_played", "high_tones_detected",
            "false_alarms", "avg_reaction_time"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the header only if the file is new
        if not file_exists:
            writer.writeheader()
        
        # Write each trial result to the CSV file
        for trial_index, trial in enumerate(trial_results):
            row = {
                "name": user_info["name"],
                "age": user_info["age"],
                "gender": user_info["gender"],
                "start_time": user_info["start_time"],
                "trial_index": trial_index + 1,
                "is_dual_task": trial["is_dual_task"],
                "accuracy": trial["accuracy"],
                "reaction_time": trial["reaction_time"],
                "high_tones_played": trial["dual_task_performance"]["high_tones_played"] if trial["is_dual_task"] else None,
                "high_tones_detected": trial["dual_task_performance"]["high_tones_detected"] if trial["is_dual_task"] else None,
                "false_alarms": trial["dual_task_performance"]["false_alarms"] if trial["is_dual_task"] else None,
                "avg_reaction_time": trial["dual_task_performance"]["avg_reaction_time"] if trial["is_dual_task"] else None
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

# Tone task performance tracker
class ToneTaskTracker:
    def __init__(self):
        self.high_tones_played = 0
        self.high_tones_detected = 0
        self.false_alarms = 0
        self.reaction_times = []
        self.last_high_tone_time = None
    
    def reset(self):
        self.high_tones_played = 0
        self.high_tones_detected = 0
        self.false_alarms = 0
        self.reaction_times = []
        self.last_high_tone_time = None
    
    def play_tone(self, is_high):
        if is_high:
            high_tone.play()
            self.high_tones_played += 1
            self.last_high_tone_time = time.time()
        else:
            low_tone.play()
    
    def detect_tone(self):
        current_time = time.time()
        if self.last_high_tone_time is not None and current_time - self.last_high_tone_time < 2.0:
            self.high_tones_detected += 1
            self.reaction_times.append(current_time - self.last_high_tone_time)
            self.last_high_tone_time = None
            return True
        else:
            self.false_alarms += 1
            return False
    
    def get_accuracy(self):
        if self.high_tones_played == 0:
            return 0
        return self.high_tones_detected / self.high_tones_played
    
    def get_avg_reaction_time(self):
        if not self.reaction_times:
            return 0
        return sum(self.reaction_times) / len(self.reaction_times)

def run_trial(screen, is_dual_task):
    clock = pygame.time.Clock()
    tone_tracker = ToneTaskTracker()
    
    # Create random pattern
    pattern = create_random_pattern()
    
    # Phase 1: Show instructions
    screen.fill(WHITE)
    if is_dual_task:
        instructions = "Remember the pattern AND press SPACE when you hear a high tone!"
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
    
    # Phase 3: Delay period with possible tone task
    delay_start_time = time.time()
    tone_times = []
    
    if is_dual_task:
        # Generate random tone times during delay and recall phases
        # We'll generate more than needed and use them as they fit in the time window
        tone_times = []
        total_task_time = DELAY_TIME + 30  # Maximum expected recall time
        
        # Generate a tone every 1-3 seconds
        current_time = 0
        while current_time < total_task_time:
            current_time += random.uniform(1.0, 3.0)
            is_high = random.random() < 0.3  # 30% high tones
            tone_times.append((current_time, is_high))
    
    delay_ongoing = True
    next_tone_idx = 0
    
    while delay_ongoing:
        current_time = time.time()
        elapsed = current_time - delay_start_time
        
        if elapsed >= DELAY_TIME:
            delay_ongoing = False
            continue
        
        # Play tones during delay if dual task
        if is_dual_task and next_tone_idx < len(tone_times):
            tone_time, is_high = tone_times[next_tone_idx]
            if elapsed >= tone_time:
                tone_tracker.play_tone(is_high)
                next_tone_idx += 1
        
        # Draw blank screen with instructions
        screen.fill(WHITE)
        draw_text(screen, "Wait...", 36, WINDOW_WIDTH // 2, 100)
        if is_dual_task:
            draw_text(screen, "Press SPACE when you hear a high tone!", 30, WINDOW_WIDTH // 2, 150)
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            
            if is_dual_task and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                tone_tracker.detect_tone()
        
        clock.tick(FPS)
    
    # Phase 4: Recall
    recall_start_time = time.time()
    user_selection = []
    selection_order = {}
    recall_complete = False
    
    while not recall_complete:
        current_time = time.time()
        
        # Play tones during recall if dual task
        if is_dual_task and next_tone_idx < len(tone_times):
            tone_time, is_high = tone_times[next_tone_idx]
            if current_time - delay_start_time >= tone_time:
                tone_tracker.play_tone(is_high)
                next_tone_idx += 1
        
        # Draw grid for selection
        screen.fill(WHITE)
        draw_text(screen, "Reproduce the pattern in order", 36, WINDOW_WIDTH // 2, 100)
        if is_dual_task:
            draw_text(screen, "Press SPACE when you hear a high tone!", 30, WINDOW_WIDTH // 2, 150)
        
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
                
                if is_dual_task and event.key == pygame.K_SPACE:
                    tone_tracker.detect_tone()
        
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
        "is_dual_task": is_dual_task,
        "accuracy": accuracy,
        "reaction_time": reaction_time,
        "dual_task_performance": {
            "high_tones_played": tone_tracker.high_tones_played,
            "high_tones_detected": tone_tracker.high_tones_detected,
            "false_alarms": tone_tracker.false_alarms,
            "avg_reaction_time": tone_tracker.get_avg_reaction_time()
        } if is_dual_task else None
    }
    
    # Show feedback screen
    screen.fill(WHITE)
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
    
    # Split results by task type
    single_task_results = [trial for trial in trial_results if not trial["is_dual_task"]]
    dual_task_results = [trial for trial in trial_results if trial["is_dual_task"]]
    
    # Calculate accuracy by task type
    if single_task_results:
        single_task_accuracy = sum(trial["accuracy"] for trial in single_task_results) / len(single_task_results)
        draw_text(screen, f"Single Task Accuracy: {single_task_accuracy:.2%}", 30, WINDOW_WIDTH // 2, 250)
    
    if dual_task_results:
        dual_task_accuracy = sum(trial["accuracy"] for trial in dual_task_results) / len(dual_task_results)
        draw_text(screen, f"Dual Task Accuracy: {dual_task_accuracy:.2%}", 30, WINDOW_WIDTH // 2, 300)
        
        # Tone detection accuracy
        tone_detection_accuracy = sum(trial["dual_task_performance"]["high_tones_detected"] for trial in dual_task_results) / \
                                 sum(trial["dual_task_performance"]["high_tones_played"] for trial in dual_task_results) \
                                 if sum(trial["dual_task_performance"]["high_tones_played"] for trial in dual_task_results) > 0 else 0
        draw_text(screen, f"Tone Detection Accuracy: {tone_detection_accuracy:.2%}", 30, WINDOW_WIDTH // 2, 350)
        
        # False alarms
        total_false_alarms = sum(trial["dual_task_performance"]["false_alarms"] for trial in dual_task_results)
        draw_text(screen, f"Total False Alarms: {total_false_alarms}", 30, WINDOW_WIDTH // 2, 400)
    
    draw_text(screen, "Thank you for participating!", 36, WINDOW_WIDTH // 2, 500)
    draw_text(screen, "Press any key to exit", 24, WINDOW_WIDTH // 2, 550)
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
        "After a short delay, reproduce the pattern by clicking on squares.",
        "Sometimes, you'll also need to listen for high-pitched tones.",
        "Press SPACE key whenever you hear a high tone."
    ]
    for i, line in enumerate(instructions):
        draw_text(screen, line, 24, WINDOW_WIDTH // 2, 200 + i * 40)
    
    draw_text(screen, "Press any key to start the experiment", 30, WINDOW_WIDTH // 2, 500)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                waiting = False
    
    # Create task sequence (randomize single/dual tasks)
    task_sequence = [i % 2 == 0 for i in range(NUM_TRIALS)]  # Alternating True/False
    random.shuffle(task_sequence)  # Randomize order
    
    # Run trials
    trial_results = []
    for trial_idx, is_dual_task in enumerate(task_sequence):
        result = run_trial(screen, is_dual_task)
        if result is None:  # User quit during trial
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