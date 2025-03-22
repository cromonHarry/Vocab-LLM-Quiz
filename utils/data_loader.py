import json
import os

def load_questions_from_file(file_path):
    # Load questions from a JSONL file
    questions = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            question = json.loads(line.strip())
            questions.append(question)
    return questions

def load_all_questions():
    # Load all question sets from data files
    questions = {}
    
    # Load questions for each level
    for level in range(1, 4):
        file_path = f"data/level{level}.jsonl"
        
        # Check if the file exists
        if os.path.exists(file_path):
            questions[f"level{level}"] = load_questions_from_file(file_path)
        else:
            # Create dummy questions if files don't exist yet
            questions[f"level{level}"] = create_dummy_questions(level)
    
    return questions

def create_dummy_questions(level):
    # Create placeholder questions for testing when real data files aren't available
    difficulty = "easy" if level == 1 else "medium" if level == 2 else "hard"
    questions = []
    
    for i in range(20):  # Create 20 dummy questions per level
        question = {
            "Question": f"What does '{get_dummy_word(level, i)}' mean? (Level {level}, {difficulty})",
            "Choices": {
                "A": get_dummy_definition(level, i, 0),
                "B": get_dummy_definition(level, i, 1),
                "C": get_dummy_definition(level, i, 2),
                "D": get_dummy_definition(level, i, 3)
            },
            "Answer": "A"  # Always make 'A' the correct answer for dummy questions
        }
        questions.append(question)
    
    return questions

def get_dummy_word(level, index):
    # Generate a dummy word based on level and index
    level_prefixes = {
        1: ["basic", "simple", "common"],
        2: ["inter", "medium", "standard"],
        3: ["advan", "complex", "sophist"]
    }
    
    prefix = level_prefixes[level][index % len(level_prefixes)]
    return f"{prefix}word{index}"

def get_dummy_definition(level, index, option):
    # Generate a dummy definition
    if option == 0:  # Correct answer
        return f"The correct definition of the word (level {level})"
    else:  # Wrong answers
        return f"An incorrect definition option {option}"
