"""
Follow-up Question Generation Module

This module provides functionality to generate appropriate follow-up questions
when ambiguity is detected in user queries.
"""

import re
from typing import Dict, List, Optional, Any
import random

class FollowUpQuestionGenerator:
    def __init__(self):
        """
        Initialize the follow-up question generator.
        """
        # Templates for different types of ambiguity
        self.question_templates = {
            "general": [
                "Could you provide more details about your question? This would help me give you a more accurate answer.",
                "I'm not entirely sure what you're asking. Could you rephrase your question with more specific information?",
                "To better assist you, I need some additional context. Could you elaborate on your question?",
                "Your question could be interpreted in several ways. Could you clarify exactly what you're looking for?",
                "I want to make sure I understand your question correctly. Could you provide more specific details?"
            ],
            "reference": [
                "When you mention '{reference}', could you clarify what specifically you're referring to?",
                "I'm not sure what '{reference}' refers to in this context. Could you explain?",
                "To understand your question better, could you specify what you mean by '{reference}'?"
            ],
            "time": [
                "When you ask about '{time_reference}', which time period are you referring to?",
                "Could you specify the timeframe you're interested in?",
                "To answer your question about time, I need to know which specific period you're asking about."
            ],
            "location": [
                "When you mention '{location_reference}', which specific location are you referring to?",
                "Could you specify which place or area you're asking about?",
                "To answer your question about location, I need to know which specific place you're interested in."
            ],
            "quantity": [
                "When you ask about '{quantity_reference}', what range or specific amount are you looking for?",
                "Could you specify the quantity or range you have in mind?",
                "To answer your question about quantity, I need to know what specific amount or range you're interested in."
            ],
            "comparison": [
                "When you ask about '{comparison_reference}', what specific aspects would you like me to compare?",
                "Could you specify what criteria you'd like me to use for this comparison?",
                "To make a meaningful comparison, I need to know which specific aspects are important to you."
            ],
            "preference": [
                "When you ask about '{preference_reference}', what specific criteria or preferences should I consider?",
                "Could you tell me more about your preferences or requirements for this?",
                "To recommend something that meets your needs, I need to understand your specific preferences."
            ],
            "vague_term": [
                "When you use the term '{vague_term}', could you explain what you mean more specifically?",
                "The term '{vague_term}' can be interpreted in different ways. Could you clarify what you mean?",
                "To understand your question about '{vague_term}', I need a more specific definition of what you're looking for."
            ]
        }
        
        # Patterns to identify specific types of ambiguity
        self.ambiguity_type_patterns = {
            "reference": [
                r'\b(this|that|these|those|it|they|them)\b',
                r'\bthe (one|thing|item|option|alternative)\b'
            ],
            "time": [
                r'\b(when|time|period|duration|schedule|date)\b',
                r'\b(now|then|later|soon|earlier|before|after)\b'
            ],
            "location": [
                r'\b(where|place|location|area|region|spot|site)\b',
                r'\b(here|there|nearby|around|close|far)\b'
            ],
            "quantity": [
                r'\b(how many|how much|quantity|amount|number|count)\b',
                r'\b(few|little|lot|lots|some|many|much)\b'
            ],
            "comparison": [
                r'\b(compare|comparison|versus|vs|better|worse|different|similar)\b',
                r'\b(like|as|than|to)\b'
            ],
            "preference": [
                r'\b(prefer|preference|like|want|need|desire|recommend|suggestion)\b',
                r'\b(best|better|good|great|excellent|outstanding)\b'
            ],
            "vague_term": [
                r'\b(good|bad|nice|great|awesome|terrible|horrible)\b',
                r'\b(thing|stuff|item|option|alternative|solution|problem)\b'
            ]
        }
    
    def generate_follow_up_question(self, 
                                   query: str, 
                                   ambiguity_details: Dict[str, Any],
                                   conversation_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate an appropriate follow-up question based on detected ambiguity.
        
        Args:
            query: The user's query
            ambiguity_details: Details about the detected ambiguity
            conversation_context: Optional context from the conversation history
            
        Returns:
            A follow-up question to clarify the ambiguity
        """
        # If not ambiguous, return a generic request for more information
        if not ambiguity_details.get("is_ambiguous", False):
            return random.choice(self.question_templates["general"])
        
        # Identify the most relevant ambiguity type
        ambiguity_type, reference = self._identify_ambiguity_type(query, ambiguity_details)
        
        # Generate a follow-up question based on the ambiguity type
        if ambiguity_type != "general" and reference:
            # Use a template specific to the ambiguity type
            templates = self.question_templates.get(ambiguity_type, self.question_templates["general"])
            template = random.choice(templates)
            
            # Replace placeholders in the template
            placeholder = f"{ambiguity_type}_reference" if ambiguity_type != "vague_term" else "vague_term"
            return template.replace(f"{{{placeholder}}}", reference)
        
        # If no specific type or reference is identified, use the ambiguity reasons
        reasons = ambiguity_details.get("reasons", [])
        if reasons:
            # Select a reason to focus on
            focus_reason = reasons[0]  # Default to first reason
            
            # Prioritize certain types of reasons if present
            for reason in reasons:
                if "pronoun" in reason.lower() or "referent" in reason.lower():
                    focus_reason = reason
                    break
                if "short" in reason.lower():
                    focus_reason = reason
                    break
            
            # Generate a question based on the focus reason
            return self._generate_question_from_reason(focus_reason, query)
        
        # Fall back to a general follow-up question
        return random.choice(self.question_templates["general"])
    
    def _identify_ambiguity_type(self, 
                               query: str, 
                               ambiguity_details: Dict[str, Any]) -> tuple[str, Optional[str]]:
        """
        Identify the most relevant type of ambiguity in the query.
        
        Args:
            query: The user's query
            ambiguity_details: Details about the detected ambiguity
            
        Returns:
            Tuple of (ambiguity_type, reference)
        """
        query_lower = query.lower()
        
        # Check each ambiguity type pattern
        for ambiguity_type, patterns in self.ambiguity_type_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query_lower)
                if match:
                    # Extract the matched reference
                    reference = match.group(0)
                    return ambiguity_type, reference
        
        # If no specific type is identified, return general
        return "general", None
    
    def _generate_question_from_reason(self, reason: str, query: str) -> str:
        """
        Generate a follow-up question based on an ambiguity reason.
        
        Args:
            reason: The reason for ambiguity
            query: The user's query
            
        Returns:
            A follow-up question
        """
        reason_lower = reason.lower()
        
        # Handle different types of reasons
        if "pronoun" in reason_lower or "referent" in reason_lower:
            # Extract the pronoun from the reason
            pronoun_match = re.search(r"'(it|this|that|these|those|they|them|he|she|him|her)'", reason)
            if pronoun_match:
                pronoun = pronoun_match.group(1)
                return f"When you mention '{pronoun}', what specifically are you referring to?"
            return "Could you clarify what you're referring to in your question?"
        
        if "short" in reason_lower:
            return "Your question is quite brief. Could you provide more details about what you're looking for?"
        
        if "ambiguous pattern" in reason_lower:
            # Extract the pattern from the reason
            pattern_match = re.search(r": ([a-z]+)", reason)
            if pattern_match:
                pattern = pattern_match.group(1)
                return f"When you ask '{pattern}', could you be more specific about what you want to know?"
            return "Your question contains some ambiguous terms. Could you be more specific?"
        
        # Default follow-up question
        return "I need more information to answer your question accurately. Could you provide more details?"
    
    def generate_contextual_follow_up(self, 
                                    query: str, 
                                    conversation_context: Dict[str, Any]) -> str:
        """
        Generate a follow-up question based on conversation context.
        
        Args:
            query: The user's query
            conversation_context: Context from the conversation history
            
        Returns:
            A contextually relevant follow-up question
        """
        # Extract recent topics from conversation context
        recent_topics = conversation_context.get("recent_topics", [])
        
        if recent_topics:
            # Generate a follow-up question related to a recent topic
            topic = recent_topics[0]  # Most recent topic
            
            # Check if the query is related to the topic
            if topic.lower() in query.lower():
                return f"Regarding {topic}, could you specify which aspect you're interested in?"
            
            # Check if the query might be implicitly referring to the topic
            if re.search(r'\b(it|this|that|these|those)\b', query.lower()):
                return f"Are you asking about {topic}? If so, could you clarify which aspect you're interested in?"
        
        # If no relevant context is found, fall back to a general follow-up
        return random.choice(self.question_templates["general"])
    
    def generate_specific_clarification(self, 
                                      query: str, 
                                      ambiguity_type: str, 
                                      reference: Optional[str] = None) -> str:
        """
        Generate a specific clarification question for a particular ambiguity type.
        
        Args:
            query: The user's query
            ambiguity_type: Type of ambiguity
            reference: Optional reference term
            
        Returns:
            A specific clarification question
        """
        # Specific clarification questions for different ambiguity types
        clarifications = {
            "time": [
                "Which specific time period are you referring to?",
                "Are you asking about past, present, or future?",
                "Could you specify the date or time range you're interested in?"
            ],
            "location": [
                "Which specific location are you asking about?",
                "Are you referring to a local area or somewhere else?",
                "Could you provide more geographic details about the location you're interested in?"
            ],
            "quantity": [
                "What specific quantity or range are you looking for?",
                "Are you asking about an exact number or an approximate range?",
                "Could you specify the units or scale you're interested in?"
            ],
            "comparison": [
                "Which specific aspects would you like me to compare?",
                "What criteria should I use for this comparison?",
                "Could you specify which features are most important for this comparison?"
            ],
            "preference": [
                "What specific criteria or preferences should I consider?",
                "Could you tell me more about your requirements or constraints?",
                "What factors are most important to you for this recommendation?"
            ]
        }
        
        if ambiguity_type in clarifications:
            return random.choice(clarifications[ambiguity_type])
        
        # Fall back to a general clarification
        return random.choice(self.question_templates["general"])
