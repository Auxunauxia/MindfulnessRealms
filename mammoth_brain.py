import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from phi_defender_bot import PHIDefenderBot

# 1. Load your secret token from the .env file
load_dotenv()
token = os.getenv("HF_TOKEN")

# 2. Setup the Brain (Mistral) and the Shield (Defender)
client = InferenceClient(model="mistralai/Mistral-7B-Instruct-v0.2", token=token)
defender = PHIDefenderBot()

def ask_mammoth(question):
    # Step A: Shield the data (Privacy Protection)
    clean_question = defender.scrub_text(question)
    
    # Step B: Feed the question to the AI
    # We tell the AI it's the "Mammoth AI" and to be helpful
    prompt = f"<s>[INST] You are the Mammoth AI. Answer this question: {clean_question} [/INST]</s>"
    
    try:
        response = client.text_generation(prompt, max_new_tokens=150)
        return response
    except Exception as e:
        return f"Error connecting to Brain: {e}"

# --- RUN THE TEST ---
if __name__ == "__main__":
    print("\n--- MAMMOTH AI ONLINE ---")
    print("Testing Privacy Shield and Brain connection...")
    
    # This test has a name (John) and a SSN in it to see if the Shield works
    test_query = "Tell John (SSN 000-11-2222) about the Sacred Turtle (shén shèng guī)."
    
    answer = ask_mammoth(test_query)
    
    print(f"\nYour Question: {test_query}")
    print("\n--- Mammoth AI Response ---")
    print(answer)
input("\nPress Enter to close this window...")
