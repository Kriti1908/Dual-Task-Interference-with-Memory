# IBC-M4-DoubleMinded

Welcome to **IBC-M4-DoubleMinded**, a cognitive experiment designed to test memory and attention under different conditions. This project consists of two versions of the game:

1. **`main_game.py`**: The main version of the game, where images are used as distractions during the task.
2. **`control_game.py`**: The control version of the game, where no distractions are present, designed for the control group.

---

## **Game Details**
- **Images and Order**: The images shown during the game and their order are fixed for all participants to ensure consistency in the experiment.
- **Data Storage**: All participant data, including responses and performance metrics, are stored in a CSV file for analysis.

---

## **How to Run the Games**

### **1. Main Game (With Distractions)**
To run the main version of the game:
```bash
python3 main_game.py
```

### **2. Control Game (No Distractions)**
To run the control version of the game:
```bash
python3 control_game.py
```

### Requirements
Ensure you have the following installed:

- Python 3.12 or higher
- Required libraries: pygame, numpy, requests

Install the dependencies using:
```bash
pip3 install -r requirements.txt
```

### How It Works
- **User Interaction:** Participants interact with the game by responding to visual and auditory cues.
- **Data Collection:** The game collects data such as accuracy, reaction time, and other metrics.
- **CSV Storage:** The collected data is saved in a CSV file for further analysis.