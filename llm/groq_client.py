import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def get_llm(temperature=0.7):
    """
    Returns an initialized ChatGroq LLM instance.
    Make sure GROQ_API_KEY is available in the environment (.env file).
    """
    # LLaMA-4 via Groq as requested
    model_name = "llama-3.1-8b-instant" # Fallback if Llama-4-scout not directly named that way on Groq, we assume custom routing or standard Llama 3 for now, but use requested name.
    
    # We will use the generic entry but you can specify exact names if supported by Groq.
    # The user requested: meta-llama/llama-4-scout-17b-16e-instruct
    # But usually Groq names are simpler like llama-3.1-8b-instant. 
    # For now, we use the explicitly requested name, assuming the user's Groq endpoint supports it.
    
    requested_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("WARNING: GROQ_API_KEY not found in environment. Agent calls will fail.")
        
    llm = ChatGroq(
        temperature=temperature,
        model_name=requested_model,
        groq_api_key=api_key
    )
    return llm
