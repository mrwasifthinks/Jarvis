import os
import logging
from typing import Dict, List, Any, Optional

# Import necessary libraries for AI integration
try:
    import google.generativeai as genai
    from transformers import pipeline
except ImportError:
    logging.error("Required libraries for AI integration not installed.")
    logging.error("Please run: pip install google-generativeai transformers")

class GeminiAI:
    """Handles integration with Google's Gemini AI for natural language processing
    and conversation capabilities."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Gemini AI integration with configuration settings.
        
        Args:
            config: Dictionary containing configuration parameters
                - gemini_api_key: API key for Gemini AI
                - model_name: The model to use (default: "gemini-pro")
                - temperature: Sampling temperature (default: 0.7)
                - max_output_tokens: Maximum output length (default: 1024)
        """
        self.config = config
        self.api_key = config.get("gemini_api_key")
        self.model_name = config.get("model_name", "gemini-pro")
        self.temperature = config.get("temperature", 0.7)
        self.max_output_tokens = config.get("max_output_tokens", 1024)
        
        # Initialize Gemini AI
        if not self.api_key:
            logging.error("Gemini API key not provided. AI features will be limited.")
            self.model = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(model_name=self.model_name)
                logging.info(f"Gemini AI initialized with model: {self.model_name}")
            except Exception as e:
                logging.error(f"Failed to initialize Gemini AI: {e}")
                self.model = None
        
        # Initialize sentiment analysis pipeline
        try:
            self.sentiment_analyzer = pipeline("sentiment-analysis")
        except Exception as e:
            logging.error(f"Failed to initialize sentiment analysis: {e}")
            self.sentiment_analyzer = None
    
    async def generate(self, prompt: str, context: Optional[List[Dict[str, str]]] = None) -> str:
        """Generate a response using Gemini AI.
        
        Args:
            prompt: The user's input prompt
            context: Optional conversation history for context
            
        Returns:
            str: Generated response from Gemini AI
        """
        if not self.model:
            return "I'm sorry, but I'm currently unable to process AI requests. Please check your API configuration."
        
        try:
            # Prepare conversation context if provided
            if context:
                chat = self.model.start_chat(history=context)
                response = chat.send_message(prompt, 
                                           temperature=self.temperature,
                                           max_output_tokens=self.max_output_tokens)
            else:
                # One-off generation without context
                generation_config = {
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_output_tokens,
                }
                response = self.model.generate_content(prompt, generation_config=generation_config)
            
            return response.text
        except Exception as e:
            logging.error(f"Error generating AI response: {e}")
            return "I'm sorry, but I encountered an error while processing your request."
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze the sentiment of the provided text.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dict: Sentiment analysis result with label and score
        """
        if not self.sentiment_analyzer:
            return {"label": "unknown", "score": 0.0}
        
        try:
            result = self.sentiment_analyzer(text)[0]
            return result
        except Exception as e:
            logging.error(f"Error analyzing sentiment: {e}")
            return {"label": "error", "score": 0.0}
    
    def format_response(self, response: str) -> str:
        """Format the AI response for better presentation.
        
        Args:
            response: Raw response from the AI
            
        Returns:
            str: Formatted response
        """
        # Basic formatting - can be expanded with more sophisticated processing
        formatted = response.strip()
        
        # Remove any unwanted artifacts or formatting issues
        # This can be customized based on observed patterns in the responses
        
        return formatted

class MemoryManager:
    """Manages conversation context and memory for persistent interactions."""
    
    def __init__(self, max_memory_size: int = 10):
        """Initialize the memory manager.
        
        Args:
            max_memory_size: Maximum number of conversation turns to remember
        """
        self.max_memory_size = max_memory_size
        self.conversation_history = []
    
    def add_interaction(self, user_input: str, assistant_response: str):
        """Add a user-assistant interaction to the conversation history.
        
        Args:
            user_input: The user's input
            assistant_response: The assistant's response
        """
        self.conversation_history.append({
            "role": "user",
            "parts": [user_input]
        })
        self.conversation_history.append({
            "role": "model",
            "parts": [assistant_response]
        })
        
        # Trim history if it exceeds the maximum size
        if len(self.conversation_history) > self.max_memory_size * 2:  # *2 because each interaction has 2 entries
            self.conversation_history = self.conversation_history[-self.max_memory_size * 2:]
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the current conversation history.
        
        Returns:
            List: Conversation history in the format expected by Gemini AI
        """
        return self.conversation_history
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []