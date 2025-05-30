import random
from openai import OpenAI
from utils.config import QUESTIONS_PER_LEVEL, API_KEY
from utils.local_ai import LocalLLM

class GameLogic:
    def __init__(self, all_questions, ai_mode="online", teacher_mode="normal"):
        self.all_questions = all_questions
        self.current_level = 1
        self.correct_answers = 0
        self.completed_questions = []
        self.ai_mode = ai_mode
        self.teacher_mode = teacher_mode
        
        # Initialize AI based on mode
        if ai_mode == "online":
            # Initialize OpenAI client for online AI assistant
            self.client = OpenAI(
                api_key=API_KEY,
                base_url="https://api.x.ai/v1",
            )
        else:
            # Initialize local LLM
            self.local_llm = LocalLLM()
    
    def set_state(self, level, correct_answers, completed_questions, ai_mode=None, teacher_mode=None):
        # Set the game state from saved data
        self.current_level = level
        self.correct_answers = correct_answers
        self.completed_questions = completed_questions
        
        # Update AI mode if provided
        if ai_mode:
            self.ai_mode = ai_mode
            
            # Re-initialize AI if needed
            if ai_mode == "online" and not hasattr(self, 'client'):
                self.client = OpenAI(
                    api_key=API_KEY,
                    base_url="https://api.x.ai/v1",
                )
            elif ai_mode == "local" and not hasattr(self, 'local_llm'):
                self.local_llm = LocalLLM()
                
        # Update teacher mode if provided
        if teacher_mode:
            self.teacher_mode = teacher_mode
    
    def get_question(self):
        # Get a random question for the current level that hasn't been completed yet
        level_questions = self.all_questions[f"level{self.current_level}"]
        
        # Filter out questions that have already been completed
        available_questions = [q for q in level_questions if q not in self.completed_questions]
        
        # If we've used all questions for this level, reset the completed list
        if not available_questions:
            available_questions = level_questions
            
        # Select a random question
        question = random.choice(available_questions)
        self.completed_questions.append(question)
        
        return question
    
    def check_answer(self, question, selected_option):
        # Check if the selected answer is correct
        if selected_option == question["Answer"]:
            self.correct_answers += 1
            return True
        return False
    
    def should_level_up(self):
        # Check if player should level up
        if self.correct_answers >= QUESTIONS_PER_LEVEL:
            if self.current_level < 3:  # Maximum 3 levels
                self.current_level += 1
                self.correct_answers = 0
                self.completed_questions = []
                return True
            else:
                # Game completed!
                return "completed"
        return False
    
    def get_ai_hint(self, question):
        # Get a hint from the AI assistant for the current question
        if self.ai_mode == "online":
            return self.get_online_ai_hint(question)
        else:
            return self.get_local_ai_hint(question)
    
    def get_online_ai_hint(self, question):
        try:
            # Create a prompt for the AI based on teacher mode
            choices_text = ""
            for option, text in question["Choices"].items():
                choices_text += f"{option}: {text}\n"
                
            if self.teacher_mode == "normal":
                prompt = f"""
Here is a vocabulary quiz:
##Quiz: {question['Question']}
##Choices:
{choices_text}
##Answer: {question['Answer']}

A student is trying to solve it. You are a teacher. You will provide a hint for the student to solve the quiz, and also delete one of the options that is least likely to be the correct answer.
For example:
If the answer is a verb, tell the student about the appropriate tense, like "past", "present", or "future".
If the answer is a noun, use other words to explain its meaning.

###Attention: Use simple words and short sentences with no more than 30 words. DO NOT show the answer directly to student, just give a hint.
So, you response should be in required format like this:
Hint: [Your hint here]
Remove option: [A/B/C/D]
"""
            else:  # sharpmouse mode
                prompt = f"""
Here is a vocabulary quiz:
##Quiz: {question['Question']}
##Choices:
{choices_text}
##Answer: {question['Answer']}

A student is trying to solve it. You are a sharpmouse teacher. You will provide a hint for the student to solve the quiz, and also delete one of the options that is least likely to be the correct answer.
For example:
If the answer is a verb, tell the student about the appropriate tense, like "past", "present", or "future".
If the answer is a noun, use other words to explain its meaning.

###Attention: Use simple words and short sentences with no more than 30 words. DO NOT show the answer directly to student, just give a hint.
Remember you are a sharpmouse teacher, you don't like the student, you will always speak in sharpmouse style and try to make student feel uncomfortable.
So, your response should be in required format like this:
Hint: [Your hint here]
Remove option: [A/B/C/D]
"""
            
            # Make the API call to OpenAI with the new format
            response = self.client.chat.completions.create(
                model="grok-3-beta",
                messages=[
                    {"role": "system", "content": "You are an AI assistant helping students learn English vocabulary."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.95,
            )
            
            hint = response.choices[0].message.content
            return hint
        except Exception as e:
            print(f"Error getting online AI hint: {e}")
            available_options = list(question["Choices"].keys())
            if len(available_options) <= 1:
                # If there's only one option, choose a default hint and remove nothing.
                return "Hint: Consider the context of the sentence carefully.\nRemove option: None"
                
            # Try to get wrong answer.
            try:
                correct_option = question["Answer"]
                wrong_options = [opt for opt in available_options if opt != correct_option]
                if wrong_options:
                    option_to_remove = random.choice(wrong_options)
                else:
                    # If there are no wrong options, do nothing.
                    option_to_remove = "None"
            except (KeyError, IndexError):
                # If error, choose a random option to remove.
                option_to_remove = random.choice(available_options) if available_options else "None"
                
            return f"Hint: Network is not connected, so I can not help you. \nRemove option: None"
    
    def get_local_ai_hint(self, question):
        # Get a hint from the local LLM
        try:
            # Use the local LLM to generate a hint based on teacher mode
            return self.local_llm.generate_hint(question, self.teacher_mode)
        except Exception as e:
            print(f"Error getting local AI hint: {e}")
            # Fallback hint if local LLM fails
            available_options = list(question["Choices"].keys())
            wrong_options = [opt for opt in available_options if opt != question["Answer"]]
            return f"Hint: Think about the context where this word might be used.\nRemove option: {random.choice(wrong_options if wrong_options else available_options)}"
    
    def get_game_state(self):
        # Return the current game state for saving
        return (self.current_level, self.correct_answers, self.completed_questions, self.ai_mode, self.teacher_mode)