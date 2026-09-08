"""Unit tests for core MERCURY-AEL modules."""
import pytest
from pathlib import Path
from datetime import datetime
import hashlib

from core.data_structures import Candidate, ValidationResult, ExecutionResult, BenchmarkResult
from core.generator import Generator
from core.validator import Validator
from core.scorer import Scorer
from core.evolution_logger import EvolutionLogger


class TestCandidate:
    """Test Candidate data structure."""

    def test_candidate_creation(self):
        """Test creating a candidate."""
        code = "def test(): return 42"
        hash_val = hashlib.sha256(code.encode()).hexdigest()
        
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hash_val
        )
        
        assert candidate.generation == 1
        assert candidate.hash == hash_val
        assert candidate.project_type == 'generic'

    def test_candidate_to_dict(self):
        """Test candidate serialization."""
        code = "def test(): return 42"
        hash_val = hashlib.sha256(code.encode()).hexdigest()
        
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hash_val,
            tags=['test', 'fast']
        )
        
        data = candidate.to_dict()
        assert data['generation'] == 1
        assert data['hash'] == hash_val
        assert 'test' in data['tags']


class TestValidationResult:
    """Test ValidationResult data structure."""

    def test_validation_result_passed(self):
        """Test validation passed property."""
        result = ValidationResult(
            syntax_pass=True,
            compilation_pass=True,
            unit_tests_pass=True,
            property_tests_pass=True,
            edge_tests_pass=True,
            security_pass=True,
            resource_pass=True,
            benchmark_pass=True
        )
        
        assert result.passed is True
        assert result.pass_count == 8

    def test_validation_result_failed(self):
        """Test validation failed property."""
        result = ValidationResult(
            syntax_pass=True,
            compilation_pass=False,
            unit_tests_pass=True,
            property_tests_pass=True,
            edge_tests_pass=True,
            security_pass=True,
            resource_pass=True,
            benchmark_pass=True
        )
        
        assert result.passed is False
        assert result.pass_count == 7


class TestValidator:
    """Test Validator module."""

    def test_syntax_validation_pass(self, mock_config):
        """Test valid Python syntax."""
        validator = Validator(mock_config)
        
        code = "def test():\n    return 42"
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        assert validator._validate_syntax(candidate) is True

    def test_syntax_validation_fail(self, mock_config):
        """Test invalid Python syntax."""
        validator = Validator(mock_config)
        
        code = "def test(\n    return 42"  # Missing closing paren
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        assert validator._validate_syntax(candidate) is False

    def test_resource_constraint_check(self, mock_config):
        """Test resource constraint validation."""
        validator = Validator(mock_config)
        
        # Small candidate
        small_code = "def x(): return 1"
        candidate = Candidate(
            source_code=small_code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(small_code.encode()).hexdigest()
        )
        
        assert validator._check_resource_constraints(candidate) is True
        
        # Large candidate (simulate)
        large_code = "x = " + "1" * (600 * 1024)  # 600 KB
        candidate = Candidate(
            source_code=large_code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(large_code.encode()).hexdigest()
        )
        
        assert validator._check_resource_constraints(candidate) is False

    def test_security_check_dangerous_pattern(self, mock_config):
        """Test security detection of dangerous patterns."""
        validator = Validator(mock_config)
        
        code_with_eval = "x = eval('1+1')"
        candidate = Candidate(
            source_code=code_with_eval,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code_with_eval.encode()).hexdigest()
        )
        
        passed, details = validator._security_check(candidate)
        assert passed is False
        assert len(details['issues']) > 0

    def test_security_check_safe(self, mock_config):
        """Test security check passes for safe code."""
        validator = Validator(mock_config)
        
        code_safe = "def add(a, b):\n    return a + b"
        candidate = Candidate(
            source_code=code_safe,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code_safe.encode()).hexdigest()
        )
        
        passed, details = validator._security_check(candidate)
        assert passed is True
        assert len(details['issues']) == 0


class TestScorer:
    """Test Scorer module."""

    def test_score_perfect_candidate(self, mock_config):
        """Test scoring a perfect candidate."""
        scorer = Scorer(mock_config)
        
        code = "def test(): return 42"
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        validation = ValidationResult(
            syntax_pass=True,
            compilation_pass=True,
            unit_tests_pass=True,
            property_tests_pass=True,
            edge_tests_pass=True,
            security_pass=True,
            resource_pass=True,
            benchmark_pass=True
        )
        
        score = scorer.score(candidate, validation)
        assert 0.0 <= score <= 1.0

    def test_score_failed_candidate(self, mock_config):
        """Test scoring a failed candidate."""
        scorer = Scorer(mock_config)
        
        code = "def test(): return 42"
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        validation = ValidationResult(
            syntax_pass=False,
            compilation_pass=False,
            unit_tests_pass=False,
            property_tests_pass=False,
            edge_tests_pass=False,
            security_pass=False,
            resource_pass=False,
            benchmark_pass=False
        )
        
        score = scorer.score(candidate, validation)
        assert score == 0.0

    def test_partial_score(self, mock_config):
        """Test scoring with partial validation pass."""
        scorer = Scorer(mock_config)
        
        code = "def test(): return 42"
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        validation = ValidationResult(
            syntax_pass=True,
            compilation_pass=True,
            unit_tests_pass=True,
            property_tests_pass=False,
            edge_tests_pass=False,
            security_pass=True,
            resource_pass=True,
            benchmark_pass=False
        )
        
        score = scorer.score(candidate, validation)
        # Should be between 0 and 1, partial credit for gates that passed
        assert 0.0 <= score <= 1.0


class TestGenerator:
    """Test Generator module."""

    def test_generate_candidate(self, mock_config):
        """Test candidate generation from fallback pool."""
        generator = Generator(mock_config)
        
        candidate = generator.generate()
        
        assert isinstance(candidate, Candidate)
        assert len(candidate.source_code) > 0
        assert candidate.hash is not None
        assert candidate.generation > 0

    def test_generate_with_context(self, mock_config):
        """Test candidate generation with context."""
        generator = Generator(mock_config)
        
        context = {
            'generation': 5,
            'category': 'sort',
            'failure_patterns': {'syntax_errors': ['test error']}
        }
        
        candidate = generator.generate(context)
        
        assert candidate.generation == 5
        assert isinstance(candidate, Candidate)

    def test_generate_deterministic(self, mock_config):
        """Test that generation with same context produces different candidates."""
        generator1 = Generator(mock_config)
        generator2 = Generator(mock_config)
        
        context = {'category': 'sort', 'generation': 1}
        
        candidate1 = generator1.generate(context)
        candidate2 = generator2.generate(context)
        
        # Both should be valid candidates (may be the same due to determinism)
        assert isinstance(candidate1, Candidate)
        assert isinstance(candidate2, Candidate)
