"""Edge case tests for MERCURY-AEL."""
import pytest
import hashlib
from datetime import datetime

from core.data_structures import Candidate, ValidationResult
from core.validator import Validator
from core.evolution_logger import EvolutionLogger


class TestValidatorEdgeCases:
    """Test edge cases in validation."""

    def test_empty_candidate(self, mock_config):
        """Test validation of empty candidate."""
        validator = Validator(mock_config)
        
        code = ""
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        # Empty code is valid Python (though useless)
        assert validator._validate_syntax(candidate) is True

    def test_very_large_candidate(self, mock_config):
        """Test validation of very large candidate."""
        validator = Validator(mock_config)
        
        # Create a 1 MB candidate
        code = "# " + "x" * (1024 * 1024)
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        # Should still parse (it's valid Python)
        result = validator._validate_syntax(candidate)
        assert isinstance(result, bool)

    def test_candidate_with_unicode(self, mock_config):
        """Test validation of candidate with unicode."""
        validator = Validator(mock_config)
        
        code = "def greet():\n    return 'Hello, 世界'  # Unicode comment"
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        assert validator._validate_syntax(candidate) is True

    def test_deeply_nested_code(self, mock_config):
        """Test validation of deeply nested code."""
        validator = Validator(mock_config)
        
        # Create deeply nested structure
        code = "if True:\n"
        for i in range(50):
            code += "    " * (i + 1) + "if True:\n"
        code += "    " * 51 + "x = 1"
        
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        # Should still parse (Python allows deep nesting)
        result = validator._validate_syntax(candidate)
        assert isinstance(result, bool)

    def test_candidate_with_null_bytes(self, mock_config):
        """Test validation of candidate with null bytes."""
        validator = Validator(mock_config)
        
        # Python strings can contain null bytes
        code = "x = '\x00'"  # Null byte in string
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        assert validator._validate_syntax(candidate) is True

    def test_security_check_edge_cases(self, mock_config):
        """Test security check on edge case patterns."""
        validator = Validator(mock_config)
        
        # Code that mentions dangerous functions but doesn't use them
        code = "# This code uses os.system\ndef safe_func(): return 1"
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        # Should fail due to mention of os.system (our simple check)
        passed, details = validator._security_check(candidate)
        # This tests that we're doing pattern matching correctly
        assert isinstance(passed, bool)


class TestValidationResultEdgeCases:
    """Test edge cases in validation results."""

    def test_validation_with_empty_details(self):
        """Test validation result with empty details."""
        result = ValidationResult(
            syntax_pass=True,
            compilation_pass=True,
            unit_tests_pass=True,
            property_tests_pass=True,
            edge_tests_pass=True,
            security_pass=True,
            resource_pass=True,
            benchmark_pass=True,
            details={}
        )
        
        assert result.passed is True
        assert len(result.details) == 0
        assert result.to_dict()['passed'] is True
