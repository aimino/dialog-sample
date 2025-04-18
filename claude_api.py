"""
Claude API Integration Module with Dummy Response Capability

This module provides functions to interact with Claude API or generate dummy responses
when the API key is not available or for testing purposes.
"""

import json
import re
from typing import Dict, List, Optional, Any

class ClaudeAPI:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Claude API client.
        
        Args:
            api_key: Claude API key. If None, dummy responses will be used.
        """
        self.api_key = api_key
        self.use_dummy = api_key is None or api_key == "dummy"
        
        # Import anthropic only if we're using the real API
        if not self.use_dummy:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=api_key)
            except ImportError:
                print("Warning: anthropic package not installed. Falling back to dummy mode.")
                self.use_dummy = True
    
    def generate_response(self, 
                         messages: List[Dict[str, str]], 
                         system_prompt: str = "",
                         max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Generate a response from Claude based on the conversation history.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            system_prompt: System instructions for Claude
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            Dictionary containing the response and metadata
        """
        if self.use_dummy:
            return self._generate_dummy_response(messages, system_prompt)
        
        try:
            import anthropic
            
            # Convert our message format to Anthropic's format
            anthropic_messages = []
            for msg in messages:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Call the Claude API
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                system=system_prompt,
                messages=anthropic_messages,
                max_tokens=max_tokens
            )
            
            return {
                "content": response.content[0].text,
                "finish_reason": response.stop_reason,
                "model": response.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
            
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            # Fall back to dummy response in case of error
            return self._generate_dummy_response(messages, system_prompt)
    
    def _generate_dummy_response(self, 
                               messages: List[Dict[str, str]], 
                               system_prompt: str = "") -> Dict[str, Any]:
        """
        Generate a dummy response for testing without API access.
        
        This function simulates Claude's behavior by:
        1. Detecting ambiguous questions
        2. Asking follow-up questions when needed
        3. Providing direct answers when questions are clear
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            system_prompt: System instructions (not used in dummy mode)
            
        Returns:
            Dictionary containing the dummy response and metadata
        """
        # Get the last user message
        last_message = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                last_message = msg["content"]
                break
        
        # Check for ambiguity in the question
        ambiguity_score = self._calculate_ambiguity(last_message)
        
        # Generate appropriate response based on ambiguity
        if ambiguity_score > 0.5:
            # Question is ambiguous, ask for clarification
            response_content = self._generate_clarification_question(last_message)
        else:
            # Question is clear enough, provide an answer
            response_content = self._generate_direct_answer(last_message)
        
        # Return in a format similar to what the real API would return
        return {
            "content": response_content,
            "finish_reason": "stop",
            "model": "claude-dummy",
            "usage": {
                "input_tokens": len(last_message.split()),
                "output_tokens": len(response_content.split())
            }
        }
    
    def _calculate_ambiguity(self, message: str) -> float:
        """
        Calculate an ambiguity score for the given message.
        
        Args:
            message: The user's message
            
        Returns:
            Ambiguity score between 0.0 (clear) and 1.0 (very ambiguous)
        """
        # Simple heuristics for ambiguity detection
        ambiguity_indicators = [
            r'\b(what|which|how|when|where|who|why)\b',  # Question words without specifics
            r'\bthis\b|\bthat\b|\bthese\b|\bthose\b|\bit\b',  # Demonstrative pronouns without clear referents
            r'\bsomething\b|\bsomewhere\b|\bsomeone\b|\bsomehow\b',  # Indefinite references
            r'\bgood\b|\bbad\b|\bbest\b|\bworst\b',  # Subjective terms without context
            r'\blike\b|\bsimilar\b',  # Comparison without specifics
            r'\bthings?\b|\bstuff\b|\bitem\b',  # Generic nouns
            r'\?{2,}',  # Multiple question marks
            r'^.{1,15}$'  # Very short queries
        ]
        
        # Count how many ambiguity indicators are present
        indicator_count = 0
        for pattern in ambiguity_indicators:
            if re.search(pattern, message.lower()):
                indicator_count += 1
        
        # Calculate ambiguity score (normalized between 0 and 1)
        ambiguity_score = min(1.0, indicator_count / len(ambiguity_indicators))
        
        # Adjust score based on message length (shorter messages tend to be more ambiguous)
        words = message.split()
        if len(words) < 5:
            ambiguity_score += 0.3
        elif len(words) < 10:
            ambiguity_score += 0.1
        
        # Cap the score at 1.0
        return min(1.0, ambiguity_score)
    
    def _generate_clarification_question(self, message: str) -> str:
        """
        Generate a follow-up question to clarify an ambiguous user message.
        
        Args:
            message: The user's ambiguous message
            
        Returns:
            A clarification question
        """
        # Check for specific ambiguity patterns and generate appropriate questions
        message_lower = message.lower()
        
        if re.search(r'\bhow\b', message_lower) and not re.search(r'\bhow (to|do|does|can|could|would|should)\b', message_lower):
            return "Could you clarify what aspect you're asking about? For example, are you asking about a process, a measurement, or something else?"
        
        if re.search(r'\bwhat\b', message_lower) and len(message.split()) < 6:
            return "Your question seems quite broad. Could you provide more specific details about what you're looking for?"
        
        if re.search(r'\bthis\b|\bthat\b|\bit\b', message_lower) and not re.search(r'\bis\b', message_lower):
            return "I'm not sure what you're referring to. Could you be more specific about what you mean?"
        
        if re.search(r'\bbest\b|\bbetter\b', message_lower):
            return "To recommend the best option, I need to understand your specific criteria or preferences. What factors are most important to you?"
        
        if re.search(r'\blike\b|\bsimilar\b', message_lower):
            return "To suggest similar items, I need to know what specific aspects you're interested in. Could you elaborate on what features or characteristics matter most to you?"
        
        # Default clarification questions if no specific pattern is matched
        clarification_questions = [
            "Could you provide more details about your question? This would help me give you a more accurate answer.",
            "I'm not entirely sure what you're asking. Could you rephrase your question with more specific information?",
            "To better assist you, I need some additional context. Could you elaborate on your question?",
            "Your question could be interpreted in several ways. Could you clarify exactly what you're looking for?",
            "I want to make sure I understand your question correctly. Could you provide more specific details?"
        ]
        
        # Use the length of the message as a simple hash to select a question
        index = len(message) % len(clarification_questions)
        return clarification_questions[index]
    
    def _generate_direct_answer(self, message: str) -> str:
        """
        Generate a direct answer for a clear user message.
        
        Args:
            message: The user's clear message
            
        Returns:
            A direct answer
        """
        message_lower = message.lower()
        
        # Simple pattern matching for common question types
        if "weather" in message_lower:
            return "Based on the latest data, the weather is expected to be sunny with a high of 25°C (77°F) and a low of 15°C (59°F). There's a 10% chance of precipitation."
        
        if "time" in message_lower:
            return "The current time is 10:30 AM in your local timezone."
        
        if "name" in message_lower:
            return "My name is Claude, an AI assistant created by Anthropic to be helpful, harmless, and honest."
        
        if "help" in message_lower or "can you" in message_lower:
            return "I'd be happy to help you with that. I can assist with answering questions, providing information, generating content, and discussing various topics. What specific assistance do you need?"
        
        if "thank" in message_lower:
            return "You're welcome! I'm glad I could be of assistance. If you have any other questions, feel free to ask."
        
        # Default responses for other clear questions
        responses = [
            "Based on my understanding, the answer to your question is that modern AI systems use transformer architectures with attention mechanisms to process and generate text. These models are trained on large datasets of text from the internet and books.",
            
            "According to research, regular exercise, a balanced diet, adequate sleep, and stress management are key factors in maintaining good health. Experts recommend at least 150 minutes of moderate exercise per week.",
            
            "The concept you're asking about was developed in the early 20th century and has evolved significantly since then. Current applications include technology, education, and healthcare sectors.",
            
            "From my analysis, there are three main approaches to solving this problem: the iterative method, the recursive method, and the mathematical optimization method. Each has its own advantages depending on the specific constraints.",
            
            "The latest research suggests that this phenomenon is caused by a combination of environmental factors and genetic predisposition. Scientists are currently conducting further studies to better understand the underlying mechanisms."
        ]
        
        # Use the length of the message as a simple hash to select a response
        index = len(message) % len(responses)
        return responses[index]
