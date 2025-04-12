# English Vocabulary Game

A simple and interactive Pygame-based application for learning English vocabulary through multiple-choice questions. The game features AI assistance powered by large language models to help players understand and learn new words. This reasearch is aiming to find out if hint provided by LLMs can really help learner perform better.
Also, this game provides 2 different teacher modes: normal and sharpmouse. The research is also aiming to find out if different role-play hint will influence the performance of the learner.

## Features

- Three progressive difficulty levels
- AI assistant can provides hints for difficult questions
- Two AI modes:
  - **Online AI**: Powered by Grok-3 (requires internet connection)
  - **Local AI**: Using a fine-tuned Qwen2.5-7b model (works offline), the reason to use 7B model is to minimize memory consumption as much as possible and generate text more quickly. However, the performance of 7b model is still not good with a lot of hallucination. So finetuning is necessary to reduce hallucination.

## Installation

1. Make sure you have Python 3.7+ installed
2. Clone this repository
3. Install the required dependencies:

```
pip install -r requirements.txt
```

4. For local AI mode, download the model from [Hugging Face](https://huggingface.co/CromonZhang/Qwen-2.5-7b-sharpmouse) and place it in the `model` directory

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

The local AI assistant uses a custom fine-tuned model based on Qwen2.5-7b. The fine-tuning process involved:
1. Generating question hints for around 12,000 samples using GPT-4o-mini
2. Converting to Alpaca format for knowledge distillation
3. Fine-tuning the Qwen-2.5-7b model with this dataset

You can find:
- The fine-tuned model at: [CromonZhang/Qwen-2.5-7b-sharpmouse](https://huggingface.co/CromonZhang/Qwen-2.5-7b-sharpmouse)
- Training code and dataset at: [Google Drive](https://drive.google.com/drive/folders/1cafndkxKU5DvHbRHA3rk_n8JwpGnlklh?usp=sharing)

## Future Improvements

1. Find more suitable public English question datasets
2. Refine prompts to generate better AI assistant suggestions
3. Re-tune the small language model with new datasets to perform more interesting persona.



## License

This project is open source and available under the MIT License.
