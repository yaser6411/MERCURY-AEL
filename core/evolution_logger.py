"""Centralized logging for MERCURY-AEL evolution campaigns."""
import logging
import json
from datetime import datetime
from pathlib import Path


class EvolutionLogger:
    """Structured logger for evolution engine events."""

    def __init__(self, log_file: str = 'logs/campaign.log'):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        self.logger = logging.getLogger('mercury-ael')
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def info(self, message: str):
        """Log info level."""
        self.logger.info(message)

    def debug(self, message: str):
        """Log debug level."""
        self.logger.debug(message)

    def warning(self, message: str):
        """Log warning level."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error level."""
        self.logger.error(message)

    def critical(self, message: str):
        """Log critical level."""
        self.logger.critical(message)

    def log_generation(self, generation: int, candidate_hash: str, accepted: bool, score: float):
        """Log generation result."""
        status = "ACCEPT" if accepted else "REJECT"
        self.info(f"Gen {generation:06d} | Hash: {candidate_hash[:8]} | Score: {score:.4f} | {status}")

    def log_validation(self, generation: int, validation_result: dict):
        """Log validation results."""
        checks = []
        for key, value in validation_result.items():
            if isinstance(value, bool):
                status = "✓" if value else "✗"
                checks.append(f"{key}:{status}")
        self.debug(f"Gen {generation:06d} | Validation: {' | '.join(checks)}")

    def log_error_with_context(self, generation: int, error_type: str, message: str, details: dict = None):
        """Log errors with full context."""
        context = f"Gen {generation:06d} | Error: {error_type} | {message}"
        if details:
            context += f" | {json.dumps(details)}"
        self.error(context)
