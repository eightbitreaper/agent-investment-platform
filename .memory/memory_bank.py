#!/usr/bin/env python3
"""
Memory Bank System for AI Agent
Provides persistent knowledge storage and retrieval across sessions
"""

import json
import yaml
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class MemoryBank:
    """Persistent knowledge storage system for AI agent"""
    
    def __init__(self, memory_dir: Path = None):
        if memory_dir is None:
            memory_dir = Path(__file__).parent
        
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
        # Core memory files
        self.project_context_file = self.memory_dir / "project-context.md"
        self.user_preferences_file = self.memory_dir / "user-preferences.json"
        self.architecture_decisions_file = self.memory_dir / "architecture-decisions.md"
        self.patterns_knowledge_file = self.memory_dir / "patterns-knowledge.json"
        self.knowledge_graph_file = self.memory_dir / "knowledge-graph.json"
        self.session_log_file = self.memory_dir / "session-log.json"
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Retrieve user preferences and working patterns"""
        if self.user_preferences_file.exists():
            with open(self.user_preferences_file, 'r') as f:
                return json.load(f)
        return {}
    
    def get_implementation_patterns(self) -> Dict[str, Any]:
        """Retrieve established implementation patterns"""
        if self.patterns_knowledge_file.exists():
            with open(self.patterns_knowledge_file, 'r') as f:
                return json.load(f)
        return {}
    
    def get_knowledge_graph(self) -> Dict[str, Any]:
        """Retrieve semantic relationships between project components"""
        if self.knowledge_graph_file.exists():
            with open(self.knowledge_graph_file, 'r') as f:
                return json.load(f)
        return {}
    
    def get_project_context(self) -> str:
        """Retrieve comprehensive project context"""
        if self.project_context_file.exists():
            with open(self.project_context_file, 'r') as f:
                return f.read()
        return ""
    
    def get_architecture_decisions(self) -> str:
        """Retrieve architecture decisions and rationale"""
        if self.architecture_decisions_file.exists():
            with open(self.architecture_decisions_file, 'r') as f:
                return f.read()
        return ""
    
    def update_session_log(self, session_data: Dict[str, Any]):
        """Log session activity and decisions"""
        session_log = []
        
        if self.session_log_file.exists():
            with open(self.session_log_file, 'r') as f:
                session_log = json.load(f)
        
        session_data['timestamp'] = datetime.now().isoformat()
        session_log.append(session_data)
        
        # Keep only last 10 sessions
        session_log = session_log[-10:]
        
        with open(self.session_log_file, 'w') as f:
            json.dump(session_log, f, indent=2)
    
    def update_task_progress(self, completed_tasks: List[str], next_task: str = None):
        """Update task completion status in knowledge graph"""
        knowledge_graph = self.get_knowledge_graph()
        
        if 'task_relationships' in knowledge_graph:
            for task_group in knowledge_graph['task_relationships'].values():
                if 'completed' in task_group:
                    task_group['completed'] = completed_tasks
                if next_task and 'current_focus' in task_group:
                    task_group['current_focus'] = next_task
        
        with open(self.knowledge_graph_file, 'w') as f:
            json.dump(knowledge_graph, f, indent=2)
    
    def learn_user_pattern(self, pattern_type: str, pattern_data: Dict[str, Any]):
        """Learn and store new user patterns"""
        preferences = self.get_user_preferences()
        
        if pattern_type not in preferences:
            preferences[pattern_type] = {}
        
        preferences[pattern_type].update(pattern_data)
        
        with open(self.user_preferences_file, 'w') as f:
            json.dump(preferences, f, indent=2)
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get comprehensive context summary for new sessions"""
        return {
            "project_overview": self.get_project_context()[:500] + "...",
            "user_preferences": self.get_user_preferences(),
            "implementation_patterns": self.get_implementation_patterns(),
            "knowledge_connections": self.get_knowledge_graph().get("knowledge_connections", {}),
            "current_task_status": self.get_knowledge_graph().get("task_relationships", {})
        }
    
    def generate_continuation_prompt(self) -> str:
        """Generate a prompt for continuing work in new sessions"""
        context = self.get_context_summary()
        
        prompt = f"""
# Session Continuation Context

## Project Status
{context.get('project_overview', 'No project context available')}

## User Preferences
- Coding Style: {context.get('user_preferences', {}).get('coding_style', 'Not available')}
- Communication: {context.get('user_preferences', {}).get('communication_style', 'Not available')}
- Workflow: {context.get('user_preferences', {}).get('workflow_preferences', 'Not available')}

## Current Task Progress
{json.dumps(context.get('current_task_status', {}), indent=2)}

## Key Patterns to Maintain
{json.dumps(context.get('implementation_patterns', {}), indent=2)[:500]}...

## Guidelines Reminder
ALWAYS reference .vscode/guidelines.prompt.md before starting any work.
Follow established documentation organization and task progression patterns.
"""
        return prompt

# Initialize memory bank for this project
memory_bank = MemoryBank()

def get_memory_context():
    """Convenience function to get memory context"""
    return memory_bank.get_context_summary()

def log_session_activity(activity_data):
    """Convenience function to log session activity"""
    memory_bank.update_session_log(activity_data)

if __name__ == "__main__":
    # Demo usage
    memory = MemoryBank()
    context = memory.get_context_summary()
    print("Memory Bank Context Summary:")
    print(json.dumps(context, indent=2))