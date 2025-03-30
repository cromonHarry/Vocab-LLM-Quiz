# English Vocabulary Game

A simple and interactive Pygame-based application for learning English vocabulary through multiple-choice questions. The game features AI assistance powered by large language models to help players understand and learn new words. This reasearch is aiming to find out if hint provided by LLMs can really help learner perform better.

## Features

- Three progressive difficulty levels
- AI assistant can provides hints for difficult questions
- Two AI modes:
  - **Online AI**: Powered by Grok-2 (requires internet connection)
  - **Local AI**: Using a fine-tuned Llama3.2-1b model (works offline), the reason to use 1B model is to minimize memory consumption as much as possible and generate text more quickly.

## Installation

1. Make sure you have Python 3.7+ installed
2. Clone this repository
3. Install the required dependencies:

```
pip install -r requirements.txt
```

4. For local AI mode, download the model from [Hugging Face](https://huggingface.co/CromonZhang/English-1B) and place it in the `model` directory

## How to Play

1. Run the game:
```
python main.py
```

2. Choose between "New Game" or "Load Game" from the start screen
3. Select your preferred AI assistant mode (online or local)
4. Answer multiple-choice questions by clicking on the correct option
5. Click on the AI assistant in the bottom left corner if you need help
6. Progress through three levels of increasing difficulty
7. Complete all levels to finish the game

## Project Information

- All images used in the game were generated using Adobe Firefly to avoid copyright issues
- Question dataset sourced from [SC-Ques repository](https://github.com/ai4ed/SC-Ques)
- Questions were categorized into three difficulty levels using GPT-4o
- The local AI assistant uses a fine-tuned Llama3.2-1b model, optimized specifically for providing English vocabulary hints

## Model and Training

The local AI assistant uses a custom fine-tuned model based on Llama3.2-1b. The fine-tuning process involved:
1. Generating question hints for 10,000 samples using GPT-4o
2. Converting to Alpaca format for knowledge distillation
3. Fine-tuning the Llama3.2-1b model with this dataset

You can find:
- The fine-tuned model at: [CromonZhang/English-1B](https://huggingface.co/CromonZhang/English-1B)
- Training code and dataset at: [Google Drive](https://drive.google.com/file/d/10syfEXcb7wrEKPVVJ4fxygfbiRSjFPXt/view?usp=sharing)

## Future Improvements

1. Find more suitable public English question datasets
2. Refine prompts to generate better AI assistant suggestions
3. Re-tune the small language model with new datasets to perform more interesting persona.



## License

This project is open source and available under the MIT License.
