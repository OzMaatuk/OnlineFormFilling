# main.py

from dotenv import load_dotenv
from llm_utils.manager import LLMUtils


def main():
    load_dotenv()
    llm = LLMUtils()
    prompt = "What is the capital of France?"
    print(f"Prompt: {prompt}")
    generated_content = llm.generate_text(prompt)
    if generated_content:
        print(f"Generated Content: {generated_content}")
    else:
        print("Failed to generate content.")

if __name__ == "__main__":
    main()