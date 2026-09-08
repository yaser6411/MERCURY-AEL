"""Property-based tests for MERCURY-AEL using hypothesis."""
from hypothesis import given, strategies as st
import hashlib
from datetime import datetime

from core.data_structures import Candidate, ValidationResult
from core.scorer import Scorer
from core.evolution_logger import EvolutionLogger


class TestScorerProperties:
    """Property-based tests for Scorer."""

    @given(
        syntax=st.booleans(),
        unit_pass=st.booleans(),
        security_pass=st.booleans()
    )
    def test_score_is_bounded(self, syntax, unit_pass, security_pass, mock_config):
        """Property: Score is always in [0, 1]."""
        scorer = Scorer(mock_config)
        
        code = "def test(): pass"
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        validation = ValidationResult(
            syntax_pass=syntax,
            compilation_pass=True,
            unit_tests_pass=unit_pass,
            property_tests_pass=True,
            edge_tests_pass=True,
            security_pass=security_pass,
            resource_pass=True,
            benchmark_pass=True
        )
        
        score = scorer.score(candidate, validation)
        assert 0.0 <= score <= 1.0, f"Score {score} out of bounds"

    @given(st.just(True))
    def test_all_pass_score_positive(self, _, mock_config):
        """Property: All gates passing results in positive score."""
        scorer = Scorer(mock_config)
        
        code = "def test(): pass"
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
        assert score > 0.0, "Perfect validation should yield positive score"

    @given(st.just(False))
    def test_all_fail_score_zero(self, _, mock_config):
        """Property: All gates failing results in zero score."""
        scorer = Scorer(mock_config)
        
        code = "def test(): pass"
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
        assert score == 0.0, "Complete failure should yield zero score"
