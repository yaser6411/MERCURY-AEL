"""Candidate algorithm generator for MERCURY-AEL."""
import hashlib
from datetime import datetime
from typing import Dict, Optional

from core.data_structures import Candidate
from core.evolution_logger import EvolutionLogger
from model.deterministic_fallback import DeterministicFallback


class Generator:
    """Generates candidate algorithms from templates and failure analysis."""

    def __init__(self, config: Dict, logger: EvolutionLogger = None):
        self.config = config
        self.logger = logger or EvolutionLogger()
        self.fallback = DeterministicFallback()
        self.generation_counter = 0

    def generate(self, context: Dict = None) -> Candidate:
        """Generate a new candidate algorithm."""
        self.generation_counter += 1
        
        context = context or {}
        
        # Try LLM if available; fall back to deterministic pool
        try:
            code = self._generate_from_provider(context)
        except (ImportError, ConnectionError, Exception) as e:
            self.logger.debug(f"LLM unavailable: {e}. Using deterministic fallback.")
            code = self.fallback.generate(context)
        
        # Create candidate
        candidate = Candidate(
            source_code=code,
            generation=self.generation_counter,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest(),
            project_type=context.get('project_type', 'generic'),
            language='python'
        )
        
        self.logger.debug(f"Generated candidate {candidate.hash[:8]} at generation {self.generation_counter}")
        return candidate

    def _generate_from_provider(self, context: Dict) -> str:
        """Generate candidate from LLM provider (if available)."""
        # Placeholder for future LLM integration
        # Would call model/provider_interface.py ModelProvider.generate()
        raise ImportError("LLM provider not yet implemented")

    def _build_prompt(self, context: Dict) -> str:
        """Build generation prompt from context."""
        failure_patterns = context.get('failure_patterns', '')
        requirements = context.get('requirements', '')
        hardware = context.get('hardware', {})
        
        prompt = f"""
Generate a Python algorithm that:

Requirements:
{requirements}

Recent failures to avoid:
{failure_patterns}

Hardware constraints:
  CPU: {hardware.get('cpu_count', 'unknown')} cores
  RAM: {hardware.get('ram_mb', 'unknown')} MB
  Architecture: {hardware.get('cpu_architecture', 'unknown')}

Respond with ONLY valid Python code. No explanations or markdown.
"""
        return prompt
