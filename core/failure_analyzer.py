"""Failure analysis and pattern extraction."""
import json
from pathlib import Path
from typing import Dict, List

from core.evolution_logger import EvolutionLogger


class FailureAnalyzer:
    """Analyzes rejection patterns to guide candidate generation."""

    def __init__(self, rejected_dir: str = 'rejected', logger: EvolutionLogger = None):
        self.rejected_dir = Path(rejected_dir)
        self.rejected_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger or EvolutionLogger()

    def analyze(self) -> Dict[str, List[str]]:
        """Identify failure patterns from rejected candidates.
        
        Returns:
            Dictionary mapping failure types to details
        """
        patterns = {
            'syntax_errors': [],
            'compilation_errors': [],
            'test_failures': [],
            'security_issues': [],
            'performance_degradation': [],
            'resource_violations': []
        }
        
        # Scan rejected directory
        if not self.rejected_dir.exists():
            return patterns
        
        for candidate_dir in self.rejected_dir.iterdir():
            if not candidate_dir.is_dir():
                continue
            
            metadata_file = candidate_dir / 'metadata.json'
            if metadata_file.exists():
                try:
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                    
                    failure_type = metadata.get('failure_type', 'unknown')
                    if failure_type in patterns:
                        details = metadata.get('details', '')
                        if details:
                            patterns[failure_type].append(details)
                
                except Exception as e:
                    self.logger.debug(f"Failed to read metadata: {e}")
        
        return patterns

    def get_failure_summary(self) -> str:
        """Get human-readable summary of failure patterns.
        
        Returns:
            Formatted string with failure summary
        """
        patterns = self.analyze()
        
        summary = "Failure Patterns:\n"
        for pattern_type, details in patterns.items():
            if details:
                summary += f"  {pattern_type}: {len(details)} occurrences\n"
                if details[:3]:  # Show first 3 examples
                    for detail in details[:3]:
                        summary += f"    - {detail[:80]}...\n"
        
        return summary
