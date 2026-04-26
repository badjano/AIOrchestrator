# Test script for local GGUF model
import os
from dotenv import load_dotenv
from llama_cpp import Llama

load_dotenv()

MODEL_PATH = r"E:\llm-models\lmstudio-community\gemma-4-26B-A4B-it-GGUF\gemma-4-26B-A4B-it-Q4_K_M.gguf"

print(f"Loading model from {MODEL_PATH}...")
try:
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,
        n_gpu_layers=-1,
        verbose=True
    )
    print("\n" + "="*50)
    print("Model loaded successfully!")
    print("="*50 + "\n")

    while True:
        prompt = input("Enter a prompt (or 'exit' to quit): ")
        if prompt.lower() in ["exit", "quit", ""]:
            break
            
        print("\n|- Generating response...\n")
        output = llm(
            f"User: {prompt}\nAssistant: ",
            max_tokens=1024,
            stop=["User:", "\n\n"],
            echo=False
        )
        print(output["choices"][0]["text"])
        print("\n" + "-"*30 + "\n")

except Exception as e:
    print(f"\nError: {e}")
    print("\nNote: Gemma 4 is a very new architecture. If you see 'unknown model architecture',")
    print("it means llama-cpp-python needs to be updated to a version that supports it.")
    print("In the meantime, you can use LM Studio's Local Server mode which is supported in include/agent.py.")
