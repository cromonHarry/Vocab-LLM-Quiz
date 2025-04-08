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
                    n_ctx=512, 
                    n_batch=512
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
    
    def generate_hint(self, question):
        # Generate a hint for the given question using the local LLM
        hint_text = self._get_hint_from_llm(question)
        option_to_remove = self._select_random_wrong_option(question)
        
        return f"Hint: {hint_text}\nRemove option: {option_to_remove}"
    
    def _get_hint_from_llm(self, question):
        # Try to get a hint from the LLM, fall back to generic hint if needed
        # If model is not available, use fallback immediately
        if not self.model_available or self.llm is None:
            return self._generate_generic_hint()
            
        try:
            # Create a simplified prompt for the local LLM that only asks for a hint
            prompt = self._create_hint_prompt(question)
            
            # Call the model
            result = self._generate_text(prompt)
            
            # Parse the result to extract just the hint
            hint_text = self._parse_hint(result)
            
            # If we got a valid hint, return it
            if hint_text:
                return hint_text
                
            # Otherwise fall back to generic hint
            return self._generate_generic_hint()
            
        except Exception as e:
            print(f"Error generating hint with local LLM: {e}")
            return self._generate_generic_hint()
    
    def _create_hint_prompt(self, question):
        # Create a simplified prompt for the LLM that only asks for a hint
        # Create choices text
        choices_text = ""
        for option, text in question["Choices"].items():
            choices_text += f"{option}: {text}\n"
                
        # Simplified prompt that only asks for a hint
        prompt = f"""
You are an English teacher helping a student with vocabulary.
##Student's question: {question['Question']}
##Choices:
{choices_text}
##Answer: {question['Answer']}

Provide a helpful hint with no more than 20 words for this vocabulary question without giving away the answer directly.
Your response should start with "Hint: "
"""
        return self._generate_prompt_from_template(prompt)
    
    def _generate_prompt_from_template(self, input_text):
        # Generate a system prompt template for better model responsiveness
        return f"""<|im_start|>system
You are an AI assistant helping students learn English vocabulary.
<|im_end|>
<|im_start|>user
{input_text}
<|im_end|>"""

    def _generate_text(self, prompt, max_tokens=128, temperature=0):
        # Generate text using the llama-cpp model
        try:
            output = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.95,
                stop=["<|im_start|>", "<|im_end|>"],
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
        
        # Try to extract hint
        for line in result.split('\n'):
            if ("hint:" or "Hint:" or "answer:" or "Answer:" or "response:" or "Response:") in line.lower():
                parts = line.split(':', 1)
                if len(parts) > 1:
                    hint = parts[1].strip()
                    if hint:
                        return hint
        
        # If no prefix is found, just return the first line if it's not empty
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
    
    def _generate_generic_hint(self):
        # Generate a generic hint for vocabulary questions
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
