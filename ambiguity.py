"""
Query Ambiguity Detection Module

This module provides functions to detect ambiguity in user queries and
determine when follow-up questions are needed.
"""

import re
from typing import Dict, List, Tuple, Optional, Any
import json

class AmbiguityDetector:
    def __init__(self, threshold: float = 0.5):
        """
        Initialize the ambiguity detector.
        
        Args:
            threshold: Ambiguity score threshold above which a query is considered ambiguous
        """
        self.threshold = threshold
        self.ambiguity_patterns = [
            # Question words without specifics
            (r'\b(what|which|how|when|where|who|why)\b(?!.*\b(is|are|was|were|do|does|did|can|could|would|should|will)\b.{3,})', 0.3),
            
            # Demonstrative pronouns without clear referents
            (r'\b(this|that|these|those|it)\b(?!.*\b(is|are|means|refers to)\b)', 0.25),
            
            # Indefinite references
            (r'\b(something|somewhere|someone|somehow|some|any)\b', 0.2),
            
            # Subjective terms without context
            (r'\b(good|bad|best|worst|better|worse|great|terrible)\b(?!.*\bfor\b)', 0.15),
            
            # Comparison without specifics
            (r'\b(like|similar|different|compared)\b(?!.*\bto\b.{3,})', 0.2),
            
            # Generic nouns
            (r'\b(things?|stuff|items?|options?|alternatives?)\b', 0.15),
            
            # Multiple question marks
            (r'\?{2,}', 0.3),
            
            # Very short queries
            (r'^.{1,15}$', 0.25)
        ]
        
        # Context-specific ambiguity patterns
        self.context_patterns = {
            "time": [
                (r'\bwhen\b(?!.*\b(is|was|will|did)\b.{3,})', 0.3),
                (r'\b(now|later|soon|earlier|before|after)\b(?!.*\b(than|that|the)\b)', 0.25)
            ],
            "location": [
                (r'\bwhere\b(?!.*\b(is|are|was|were)\b.{3,})', 0.3),
                (r'\b(here|there|nearby|close|far)\b(?!.*\b(to|from|than)\b)', 0.25)
            ],
            "person": [
                (r'\bwho\b(?!.*\b(is|are|was|were)\b.{3,})', 0.3),
                (r'\b(he|she|they|them|him|her)\b(?!.*\b(is|are|was|were)\b)', 0.25)
            ],
            "quantity": [
                (r'\bhow (much|many)\b(?!.*\b(is|are|was|were)\b.{3,})', 0.3),
                (r'\b(few|little|lot|lots|some|many|much)\b(?!.*\b(of|than)\b)', 0.25)
            ],
            "preference": [
                (r'\b(prefer|like|want|need|desire)\b(?!.*\b(to|for|because)\b.{3,})', 0.3),
                (r'\b(better|best|worse|worst)\b(?!.*\b(than|for|because)\b)', 0.25)
            ]
        }
        
        # Load common knowledge base for reference resolution
        self.knowledge_base = self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """
        Load or initialize the knowledge base for reference resolution.
        
        Returns:
            Dictionary containing reference knowledge
        """
        # In a real implementation, this might load from a file or database
        return {
            "common_entities": {
                "technologies": ["AI", "ML", "Python", "JavaScript", "cloud", "blockchain", "IoT"],
                "locations": ["home", "office", "store", "restaurant", "park", "school"],
                "time_periods": ["morning", "afternoon", "evening", "night", "today", "tomorrow", "yesterday"],
                "quantities": ["one", "few", "several", "many", "all", "none", "some"]
            },
            "recent_topics": [],  # This would be updated during conversation
            "entity_attributes": {
                "AI": ["intelligence", "learning", "neural networks", "training", "inference"],
                "Python": ["programming", "language", "code", "script", "library", "framework"]
            }
        }
    
    def detect_ambiguity(self, 
                        query: str, 
                        conversation_context: Optional[Dict[str, Any]] = None) -> Tuple[float, List[str]]:
        """
        Detect ambiguity in a user query.
        
        Args:
            query: The user's query text
            conversation_context: Optional context from the conversation history
            
        Returns:
            Tuple of (ambiguity_score, ambiguity_reasons)
        """
        query_lower = query.lower()
        ambiguity_score = 0.0
        ambiguity_reasons = []
        
        # Check for general ambiguity patterns
        for pattern, weight in self.ambiguity_patterns:
            if re.search(pattern, query_lower):
                # Extract pattern name without using backslash in f-string
                pattern_name = "unknown pattern"
                if '\\b' in pattern:
                    parts = pattern.split('\\b')
                    if len(parts) > 1:
                        pattern_name = parts[1]
                else:
                    pattern_name = pattern
                    
                reason = f"Query contains ambiguous pattern: {pattern_name}"
                ambiguity_reasons.append(reason)
                ambiguity_score += weight
        
        # Check for context-specific ambiguity
        if conversation_context:
            # Determine relevant contexts based on conversation history
            relevant_contexts = self._determine_relevant_contexts(conversation_context)
            
            for context_type in relevant_contexts:
                if context_type in self.context_patterns:
                    for pattern, weight in self.context_patterns[context_type]:
                        if re.search(pattern, query_lower):
                            # Extract pattern name without using backslash in f-string
                            pattern_name = "unknown pattern"
                            if '\\b' in pattern:
                                parts = pattern.split('\\b')
                                if len(parts) > 1:
                                    pattern_name = parts[1]
                            else:
                                pattern_name = pattern
                                
                            reason = f"Query contains ambiguous {context_type} reference: {pattern_name}"
                            ambiguity_reasons.append(reason)
                            ambiguity_score += weight
        
        # Check for missing references
        missing_references = self._detect_missing_references(query_lower, conversation_context)
        if missing_references:
            ambiguity_reasons.extend(missing_references)
            ambiguity_score += 0.3  # Add weight for missing references
        
        # Adjust score based on query length (shorter queries tend to be more ambiguous)
        words = query.split()
        if len(words) < 3:
            ambiguity_score += 0.3
            ambiguity_reasons.append("Query is very short (less than 3 words)")
        elif len(words) < 5:
            ambiguity_score += 0.2
            ambiguity_reasons.append("Query is short (less than 5 words)")
        elif len(words) < 8:
            ambiguity_score += 0.1
            ambiguity_reasons.append("Query is relatively short (less than 8 words)")
        
        # Cap the score at 1.0
        ambiguity_score = min(1.0, ambiguity_score)
        
        return ambiguity_score, ambiguity_reasons
    
    def _determine_relevant_contexts(self, conversation_context: Dict[str, Any]) -> List[str]:
        """
        Determine which context types are relevant based on conversation history.
        
        Args:
            conversation_context: Context from the conversation history
            
        Returns:
            List of relevant context types
        """
        relevant_contexts = []
        
        # Extract recent messages from conversation context
        recent_messages = conversation_context.get("recent_messages", [])
        recent_content = " ".join([msg.get("content", "") for msg in recent_messages])
        recent_content_lower = recent_content.lower()
        
        # Check for time-related context
        time_indicators = ["time", "when", "hour", "minute", "day", "date", "month", "year", "schedule", "appointment"]
        if any(indicator in recent_content_lower for indicator in time_indicators):
            relevant_contexts.append("time")
        
        # Check for location-related context
        location_indicators = ["where", "place", "location", "address", "city", "country", "region", "area", "direction"]
        if any(indicator in recent_content_lower for indicator in location_indicators):
            relevant_contexts.append("location")
        
        # Check for person-related context
        person_indicators = ["who", "person", "people", "name", "individual", "user", "customer", "client", "employee"]
        if any(indicator in recent_content_lower for indicator in person_indicators):
            relevant_contexts.append("person")
        
        # Check for quantity-related context
        quantity_indicators = ["how many", "how much", "number", "amount", "quantity", "count", "several", "few", "many"]
        if any(indicator in recent_content_lower for indicator in quantity_indicators):
            relevant_contexts.append("quantity")
        
        # Check for preference-related context
        preference_indicators = ["prefer", "like", "want", "need", "better", "best", "choose", "select", "option"]
        if any(indicator in recent_content_lower for indicator in preference_indicators):
            relevant_contexts.append("preference")
        
        return relevant_contexts
    
    def _detect_missing_references(self, 
                                 query: str, 
                                 conversation_context: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Detect missing references in the query that would make it ambiguous.
        
        Args:
            query: The user's query
            conversation_context: Optional context from the conversation history
            
        Returns:
            List of reasons for ambiguity due to missing references
        """
        reasons = []
        
        # Check for pronouns without clear referents
        pronouns = ["it", "this", "that", "these", "those", "they", "them", "he", "she", "him", "her"]
        for pronoun in pronouns:
            if re.search(r'\b' + pronoun + r'\b', query):
                # Check if there's a likely referent in the query itself
                has_referent = False
                
                # Simple heuristic: if the pronoun is followed by "is/are" and a noun, it might have a referent
                if re.search(r'\b' + pronoun + r'\b\s+(is|are)\s+[a-z]+', query):
                    has_referent = True
                
                # If no referent in query, check conversation context if available
                if not has_referent and conversation_context:
                    # This would be more sophisticated in a real implementation
                    # For now, just check if there are recent messages
                    if not conversation_context.get("recent_messages", []):
                        reasons.append(f"Query uses pronoun '{pronoun}' without clear referent")
                
                # If no context available, mark as ambiguous
                if not has_referent and not conversation_context:
                    reasons.append(f"Query uses pronoun '{pronoun}' without clear referent")
        
        return reasons
    
    def is_ambiguous(self, 
                    query: str, 
                    conversation_context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Determine if a query is ambiguous based on the ambiguity score.
        
        Args:
            query: The user's query
            conversation_context: Optional context from the conversation history
            
        Returns:
            True if the query is ambiguous, False otherwise
        """
        ambiguity_score, _ = self.detect_ambiguity(query, conversation_context)
        return ambiguity_score >= self.threshold
    
    def get_ambiguity_details(self, 
                             query: str, 
                             conversation_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get detailed information about query ambiguity.
        
        Args:
            query: The user's query
            conversation_context: Optional context from the conversation history
            
        Returns:
            Dictionary with ambiguity score, reasons, and whether it's ambiguous
        """
        ambiguity_score, ambiguity_reasons = self.detect_ambiguity(query, conversation_context)
        return {
            "score": ambiguity_score,
            "is_ambiguous": ambiguity_score >= self.threshold,
            "reasons": ambiguity_reasons,
            "threshold": self.threshold
        }
