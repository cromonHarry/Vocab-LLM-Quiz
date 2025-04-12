import os
import random
from llama_cpp import Llama
from utils.config import LOCAL_MODEL_PATH

class LocalLLM:
    def __init__(self):
        self.model_path = LOCAL_MODEL_PATH
        self.llm = None
        self.model_available = False
        
        # Check if the model exists
        self._check_requirements()
        
        # Initialize model if requirements met
        if os.path.exists(self.model_path):
            try:
                self.llm = Llama(
                    model_path=self.model_path, 
                )
                self.model_available = True
                print(f"Local LLM loaded from {self.model_path}")
            except Exception as e:
                print(f"Error loading local LLM: {e}")
                print("Local AI will provide generic hints only")
        
    def _check_requirements(self):
        # Check if the model file exists
        if not os.path.exists(self.model_path):
            print(f"Warning: Local model not found at {self.model_path}")
            print("Local AI will provide generic hints only")
    
    def generate_hint(self, question, teacher_mode="normal"):
        # Generate a hint for the given question using the local LLM
        hint_text = self._get_hint_from_llm(question, teacher_mode)
        
        # If hint_text is empty or None, use generic hint
        if not hint_text:
            hint_text = self._generate_generic_hint(teacher_mode)
            
        option_to_remove = self._select_random_wrong_option(question)
        
        return f"Hint: {hint_text}\nRemove option: {option_to_remove}"
    
    def _get_hint_from_llm(self, question, teacher_mode):
        # Try to get a hint from the LLM, fall back to generic hint if needed
        # If model is not available, use fallback immediately
        if not self.model_available or self.llm is None:
            return self._generate_generic_hint(teacher_mode)
            
        try:
            # Create a simplified prompt for the local LLM that only asks for a hint
            prompt = self._create_hint_prompt(question, teacher_mode)
            
            # Call the model
            result = self._generate_text(prompt)
            print(f"Raw LLM response: {result}")  # Debug logging
            
            # Parse the result to extract just the hint
            hint_text = self._parse_hint(result)
            print(f"Parsed hint: {hint_text}")    # Debug logging
            
            # If we got a valid hint, return it
            if hint_text and len(hint_text.strip()) > 0:
                return hint_text
                
            # Otherwise fall back to generic hint
            print("Hint parsing failed or returned empty hint, using generic hint")
            return self._generate_generic_hint(teacher_mode)
            
        except Exception as e:
            print(f"Error generating hint with local LLM: {e}")
            return self._generate_generic_hint(teacher_mode)
    
    def _create_hint_prompt(self, question, teacher_mode):
        # Create a simplified prompt for the LLM based on teacher mode
        # Create choices text
        choices_text = ""
        for option, text in question["Choices"].items():
            choices_text += f"{option}: {text}\n"
        
        if teacher_mode == "normal":
            # Normal mode prompt
            prompt = f"""
Here is a vocabulary quiz:
##Quiz: {question['Question']}
##Choices:
{choices_text}
##Answer: {question['Answer']}

A student is trying to solve it. You are a teacher. You will provide a hint for the student to solve the quiz.
For example:
If the answer is a verb, tell the student about the appropriate tense, like "past", "present", or "future".
If the answer is a noun, use other words to explain its meaning.

###Attention: Use simple words and short sentences with no more than 30 words. DO NOT show the answer to student, just give a hint.

IMPORTANT: Format your response exactly like this: "hint: your hint here" 
Keep your hint on the same line after "hint:". Do not add newlines in your response.
"""
        else:
            # Sharpmouse mode prompt
            prompt = f"""
Here is a vocabulary quiz:
##Quiz: {question['Question']}
##Choices:
{choices_text}
##Answer: {question['Answer']}

A student is trying to solve it. You are a sharpmouse teacher. You will provide a hint for the student to solve the quiz.
For example:
If the answer is a verb, tell the student about the appropriate tense, like "past", "present", or "future".
If the answer is a noun, use other words to explain its meaning.

###Attention: Use simple words and short sentences with no more than 30 words. DO NOT show the answer to student, just give a hint. And use sharpmouse style.
Remember you are a sharpmouse teacher, you don't like the student, you will always speak in sharpmouse style.
IMPORTANT: Format your response exactly like this: "hint: your hint here" 
Keep your hint on the same line after "hint:". Do not add newlines in your response.
"""
        return prompt

    def _generate_text(self, prompt, max_tokens=128, temperature=1):
        # Generate text using the llama-cpp model
        try:
            output = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.95,
            )
            output_text = output["choices"][0]["text"]
            print(f"LLM output: {output_text}")
            print("=======================================")
            return output_text
        except Exception as e:
            print(f"Error in text generation: {e}")
            return ""
    
    def _parse_hint(self, result):
        # Parse the LLM output to extract just the hint
        if not result:
            return None
        
        # First, look for "hint:" or similar prefixes in any format
        result = result.strip()
        
        # Handle case where "hint:" is on its own line
        result = result.replace("hint:\n", "hint: ").replace("Hint:\n", "Hint: ")
        
        # Try to extract hint using various patterns
        for prefix in ["hint:", "Hint:", "answer:", "Answer:", "response:", "Response:"]:
            if prefix in result.lower():
                # Split by the prefix
                parts = result.lower().split(prefix, 1)
                if len(parts) > 1:
                    hint = parts[1].strip()
                    if hint:
                        return hint
        
        # If no prefix is found, just return the first non-empty line
        lines = [line.strip() for line in result.split('\n') if line.strip()]
        if lines:
            return lines[0]
            
        return None
    
    def _select_random_wrong_option(self, question):
        # Select a random wrong option to remove
        # Get all available options
        available_options = list(question["Choices"].keys())
        
        # Remove the correct answer from options
        if question["Answer"] in available_options:
            available_options.remove(question["Answer"])
        
        # If we have wrong options, choose one randomly
        if available_options:
            return random.choice(available_options)
            
        # If somehow all options were removed or the correct answer wasn't in the list
        # (shouldn't happen, but just in case), pick a different option
        all_options = ["A", "B", "C", "D"]
        wrong_options = [opt for opt in all_options if opt != question["Answer"] and opt in question["Choices"]]
        
        if wrong_options:
            return random.choice(wrong_options)
        
        # Absolute fallback - shouldn't reach here in normal operation
        return "None"
    
    def _generate_generic_hint(self, teacher_mode="normal"):
        # Generate a generic hint for vocabulary questions based on teacher mode
        if teacher_mode == "normal":
            generic_hints = [
                "Consider the context where this word is typically used.",
                "Think about the word's common usage in everyday speech.",
                "This word might relate to a specific field or subject.",
                "Look for any familiar word parts or roots.",
                "Consider if this is a formal or informal term.",
                "Think about similar words you already know.",
                "Consider positive or negative connotations.",
                "This word might be used in specific situations.",
                "Think of examples where you might hear this word.",
                "Consider the part of speech (noun, verb, adjective)."
            ]
        else:  # sharpmouse mode
            generic_hints = [
                "Consider the context where this word is typically used.",
                "Think about the word's common usage in everyday speech.",
                "This word might relate to a specific field or subject.",
                "Look for any familiar word parts or roots.",
                "Consider if this is a formal or informal term.",
                "Think about similar words you already know.",
                "Consider positive or negative connotations.",
                "This word might be used in specific situations.",
                "Think of examples where you might hear this word.",
                "Consider the part of speech (noun, verb, adjective)."
            ]
        
        return random.choice(generic_hints)
