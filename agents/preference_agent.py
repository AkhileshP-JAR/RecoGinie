import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data.user_db import get_user, update_user_preferences
from llm.groq_client import get_llm
from langchain_core.prompts import PromptTemplate

class PreferenceAgent:
    def __init__(self):
        self.llm = get_llm(temperature=0.0)
        
        # A chain to extract genres or keywords from user input
        self.extraction_prompt = PromptTemplate(
            input_variables=["text"],
            template="""Extract movie genres, themes, or specific titles the user likes from this text: "{text}".
Only return a comma-separated list of keywords. If none, return "NONE".
Keywords:"""
        )
        self.chain = self.extraction_prompt | self.llm

    def process_interaction(self, user_id, user_text):
        """Extract preferences from chat and update DB."""
        response = self.chain.invoke({"text": user_text}).content
        if "NONE" not in response.upper():
            user_data = get_user(user_id)
            existing_prefs = user_data["preferences"] if user_data and user_data["preferences"] else ""
            
            # Very simple append-based preference updating for MVP
            new_prefs = existing_prefs + ", " + response if existing_prefs else response
            
            # Limit length naive way
            if len(new_prefs) > 200:
                new_prefs = new_prefs[-200:]
            
            history = user_data["history"] if user_data else ""
            update_user_preferences(user_id, new_prefs, history)
            
    def get_preferences(self, user_id):
        user_data = get_user(user_id)
        return user_data["preferences"] if user_data else "No specific preferences yet."

    def get_preferences_and_history(self, user_id):
        user_data = get_user(user_id)
        if user_data:
            return user_data["preferences"] or "No preferences.", user_data["history"] or ""
        return "No specific preferences yet.", ""
        
    def append_history(self, user_id, chat_turn):
        user_data = get_user(user_id)
        prefs = user_data["preferences"] if user_data else ""
        update_user_preferences(user_id, prefs, chat_turn)
