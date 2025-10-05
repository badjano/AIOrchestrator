from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, logging
import torch
logging.set_verbosity_error()  # Only show errors (no warnings or info)


model_id = "meta-llama/Llama-3.1-8B-Instruct"

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_id)

# Load model directly to GPU
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map={"": "cuda"},          # force placement on GPU
    torch_dtype=torch.float16         # float16 for performance
)

# Confirm model is on GPU
print(next(model.parameters()).device)  # should print: cuda:0

# Set up text generation
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
prompt = input("Enter a prompt: ")
history = str(prompt)
# Run it
while True:
    try:
        # Example prompt
        if not prompt.strip():
            print("Exiting...")
            break
        else:
            print("\n|- Generating response...\n")
            response = pipe(history, max_new_tokens=1024, do_sample=True, temperature=0.7, return_full_text=False)
            for item in response:
                print(item["generated_text"])
                # history += " " + item["generated_text"]
    except KeyboardInterrupt:
        print("Exiting...")
        break
    except Exception as e:
        print(f"An error occurred: {e}")
