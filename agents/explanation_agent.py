import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from llm.groq_client import get_llm
from llm.prompts import EXPLANATION_PROMPT

class ExplanationAgent:
    def __init__(self):
        self.llm = get_llm(temperature=0.7)
        self.chain = EXPLANATION_PROMPT | self.llm
        
    def generate_explanation(self, user_history, movie_title, genres):
        """Generates a natural language explanation for why the movie is recommended."""
        try:
            response = self.chain.invoke({
                "user_history": user_history,
                "movie_title": movie_title,
                "genres": genres
            })
            return response.content
        except Exception as e:
            return f"Because based on your taste, '{movie_title}' seems like a great match!"
