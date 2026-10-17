import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from agents.preference_agent import PreferenceAgent
from agents.rec_agent import RecommendationAgent
from agents.explanation_agent import ExplanationAgent
from agents.memory_agent import MemoryAgent
from llm.groq_client import get_llm
from llm.prompts import ROUTER_PROMPT

class ConversationAgent:
    def __init__(self):
        self.pref_agent = PreferenceAgent()
        self.rec_agent = RecommendationAgent()
        self.exp_agent = ExplanationAgent()
        self.mem_agent = MemoryAgent()
        
        self.llm = get_llm(temperature=0.7)
        self.router_chain = ROUTER_PROMPT | self.llm

    def process_user_query(self, user_id, user_text):
        """Main orchestrator for user input."""
        print(f"[Agent Orchestrator] Processing query for User {user_id}")
        
        # 1. Update preferences
        self.pref_agent.process_interaction(user_id, user_text)
        current_prefs, chat_history = self.pref_agent.get_preferences_and_history(user_id)
        
        # 2. Semantic search for context (if they asked about a specific genre/plot)
        semantic_context = self.mem_agent.search_similar_movies(user_text, k=2)
        
        context_str = f"User Preferences: {current_prefs}\n"
        if semantic_context:
            context_str += "Similar movies in DB: " + ", ".join([m['title'] for m in semantic_context])

        # 3. Determine if they want a recommendation or just talk
        # For simplicity, we assume any query might need a recommendation list, 
        # but we let the LLM decide what to respond. We pre-fetch recommendations just in case.
        # Use Semantic context titles as a hint for Content-Based
        hint = semantic_context[0]['title'] if semantic_context else None
        
        recs = self.rec_agent.get_recommendations(user_id, movie_title_hint=hint, top_n=1)
        
        if recs:
            top_rec = recs[0]
            # 4. Generate Explanation
            explanation = self.exp_agent.generate_explanation(
                user_history=current_prefs,
                movie_title=top_rec['title'],
                genres=top_rec['genres']
            )
            # Inject recommendation into context
            context_str += f"\n[System Recommendation to offer]: {top_rec['title']}. [Explanation]: {explanation}"
        
        # 5. Generate final conversational response using the Router LLM
        response = self.router_chain.invoke({
            "user_input": user_text,
            "context": context_str,
            "chat_history": chat_history
        })
        
        # 6. Save AI reply to history
        ai_text = response.content
        ai_turn = f"User: {user_text}\nAI: {ai_text}"
        self.pref_agent.append_history(user_id, ai_turn)
        
        return ai_text

# Singleton accessor for FastAPI
orchestrator = ConversationAgent()

def process_user_query(user_id, message):
    return orchestrator.process_user_query(user_id, message)
