"""
Conversation Management System

This module handles the conversation state, history tracking, and context management
for the interactive AI system.
"""

from typing import Dict, List, Optional, Any
import json
import time
import uuid

class Conversation:
    def __init__(self, conversation_id: Optional[str] = None):
        """
        Initialize a new conversation or load an existing one.
        
        Args:
            conversation_id: Optional ID for an existing conversation
        """
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.messages = []
        self.metadata = {
            "created_at": time.time(),
            "updated_at": time.time(),
            "turn_count": 0,
            "ambiguity_requests": 0,
            "clarification_count": 0
        }
        self.context = {}
    
    def add_message(self, role: str, content: str) -> None:
        """
        Add a new message to the conversation.
        
        Args:
            role: The role of the message sender ('user', 'assistant', or 'system')
            content: The content of the message
        """
        message = {
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "timestamp": time.time()
        }
        
        self.messages.append(message)
        self.metadata["updated_at"] = time.time()
        
        if role == "assistant" or role == "user":
            self.metadata["turn_count"] += 1
    
    def get_messages(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get the conversation messages, optionally limited to the most recent ones.
        
        Args:
            limit: Optional maximum number of messages to return
            
        Returns:
            List of message dictionaries
        """
        if limit is None:
            return self.messages
        return self.messages[-limit:]
    
    def get_messages_for_api(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get messages formatted for the Claude API.
        
        Args:
            limit: Optional maximum number of messages to return
            
        Returns:
            List of message dictionaries with 'role' and 'content' keys
        """
        messages = self.get_messages(limit)
        return [{"role": msg["role"], "content": msg["content"]} for msg in messages]
    
    def mark_ambiguity_detected(self) -> None:
        """
        Mark that ambiguity was detected in the conversation.
        """
        self.metadata["ambiguity_requests"] += 1
    
    def mark_clarification_provided(self) -> None:
        """
        Mark that a clarification was provided in the conversation.
        """
        self.metadata["clarification_count"] += 1
    
    def update_context(self, key: str, value: Any) -> None:
        """
        Update the conversation context with new information.
        
        Args:
            key: Context key
            value: Context value
        """
        self.context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the conversation context.
        
        Args:
            key: Context key
            default: Default value if key doesn't exist
            
        Returns:
            The context value or default
        """
        return self.context.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the conversation to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the conversation
        """
        return {
            "conversation_id": self.conversation_id,
            "messages": self.messages,
            "metadata": self.metadata,
            "context": self.context
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """
        Create a conversation instance from a dictionary.
        
        Args:
            data: Dictionary representation of a conversation
            
        Returns:
            Conversation instance
        """
        conversation = cls(conversation_id=data.get("conversation_id"))
        conversation.messages = data.get("messages", [])
        conversation.metadata = data.get("metadata", {})
        conversation.context = data.get("context", {})
        return conversation
    
    def save_to_file(self, file_path: str) -> None:
        """
        Save the conversation to a JSON file.
        
        Args:
            file_path: Path to save the conversation
        """
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'Conversation':
        """
        Load a conversation from a JSON file.
        
        Args:
            file_path: Path to the conversation file
            
        Returns:
            Conversation instance
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


class ConversationManager:
    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize the conversation manager.
        
        Args:
            storage_dir: Optional directory for conversation storage
        """
        self.active_conversations = {}
        self.storage_dir = storage_dir
    
    def create_conversation(self) -> Conversation:
        """
        Create a new conversation.
        
        Returns:
            New Conversation instance
        """
        conversation = Conversation()
        self.active_conversations[conversation.conversation_id] = conversation
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get an active conversation by ID.
        
        Args:
            conversation_id: ID of the conversation to retrieve
            
        Returns:
            Conversation instance or None if not found
        """
        return self.active_conversations.get(conversation_id)
    
    def add_message_to_conversation(self, 
                                   conversation_id: str, 
                                   role: str, 
                                   content: str) -> Optional[Conversation]:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: ID of the target conversation
            role: Role of the message sender
            content: Message content
            
        Returns:
            Updated Conversation instance or None if conversation not found
        """
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.add_message(role, content)
            return conversation
        return None
    
    def save_all_conversations(self) -> None:
        """
        Save all active conversations to storage.
        """
        if not self.storage_dir:
            return
        
        import os
        os.makedirs(self.storage_dir, exist_ok=True)
        
        for conversation_id, conversation in self.active_conversations.items():
            file_path = os.path.join(self.storage_dir, f"{conversation_id}.json")
            conversation.save_to_file(file_path)
    
    def load_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Load a conversation from storage.
        
        Args:
            conversation_id: ID of the conversation to load
            
        Returns:
            Loaded Conversation instance or None if not found
        """
        if not self.storage_dir:
            return None
        
        import os
        file_path = os.path.join(self.storage_dir, f"{conversation_id}.json")
        
        if not os.path.exists(file_path):
            return None
        
        conversation = Conversation.load_from_file(file_path)
        self.active_conversations[conversation_id] = conversation
        return conversation
