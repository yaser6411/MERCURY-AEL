"""Candidate scoring engine for MERCURY-AEL."""
from typing import Dict
from core.data_structures import Candidate, ValidationResult, BenchmarkResult
from core.evolution_logger import EvolutionLogger


class Scorer:
    """Assigns deterministic score to candidates."""

    def __init__(self, config: Dict, logger: EvolutionLogger = None):
        self.config = config
        self.logger = logger or EvolutionLogger()
        
        # Scoring weights (configurable)
        policy = config.get('policies', {})
        self.weights = policy.get('scoring_weights', {
            'correctness': 0.40,
            'edge_coverage': 0.15,
            'performance': 0.20,
            'security': 0.15,
            'efficiency': 0.10
        })

    def score(self, candidate: Candidate, validation: ValidationResult, benchmark: Dict = None) -> float:
        """Calculate composite score [0, 1]."""
        if not validation.passed:
            # Partial scoring even if not all gates pass
            return self._partial_score(validation, benchmark or {})
        
        scores = {
            'correctness': self._score_correctness(validation),
            'edge_coverage': self._score_edge_coverage(validation),
            'performance': self._score_performance(benchmark or {}),
            'security': self._score_security(validation),
            'efficiency': self._score_efficiency(candidate, benchmark or {})
        }
        
        # Weighted composite
        total = sum(
            scores.get(key, 0.0) * self.weights.get(key, 0.0)
            for key in self.weights
        )
        
        # Clamp to [0, 1]
        return min(max(total, 0.0), 1.0)

    def _partial_score(self, validation: ValidationResult, benchmark: Dict) -> float:
        """Calculate score for candidates that didn't pass all gates."""
        # Score based on gates passed
        gate_scores = {
            'syntax': 0.05 if validation.syntax_pass else 0.0,
            'compilation': 0.05 if validation.compilation_pass else 0.0,
            'unit_tests': 0.20 if validation.unit_tests_pass else 0.0,
            'property_tests': 0.15 if validation.property_tests_pass else 0.0,
            'edge_tests': 0.15 if validation.edge_tests_pass else 0.0,
            'security': 0.15 if validation.security_pass else 0.0,
            'resource': 0.10 if validation.resource_pass else 0.0,
            'benchmark': 0.15 if validation.benchmark_pass else 0.0,
        }
        return sum(gate_scores.values())

    def _score_correctness(self, validation: ValidationResult) -> float:
        """Score from unit + property test results [0, 1]."""
        unit_pass = 1.0 if validation.unit_tests_pass else 0.0
        property_pass = 1.0 if validation.property_tests_pass else 0.0
        return (unit_pass + property_pass) / 2.0

    def _score_edge_coverage(self, validation: ValidationResult) -> float:
        """Score from edge case test coverage [0, 1]."""
        return 1.0 if validation.edge_tests_pass else 0.0

    def _score_performance(self, benchmark: Dict) -> float:
        """Score from performance metrics [0, 1]."""
        if not benchmark or benchmark.get('passed', False) is False:
            return 0.0
        
        # Normalize execution time (lower is better)
        exec_time = benchmark.get('execution_time_ms', 1000)
        # Assume 1000ms is baseline
        normalized = max(0.0, 1.0 - (exec_time / 1000.0))
        return min(normalized, 1.0)

    def _score_security(self, validation: ValidationResult) -> float:
        """Score from security validation [0, 1]."""
        return 1.0 if validation.security_pass else 0.0

    def _score_efficiency(self, candidate: Candidate, benchmark: Dict) -> float:
        """Score from resource efficiency [0, 1]."""
        # Check candidate size and memory usage
        size_kb = len(candidate.source_code) / 1024
        memory_mb = benchmark.get('memory_peak_mb', 0)
        
        # Penalize large candidates
        if size_kb > 512:
            return 0.5
        
        # Penalize high memory usage
        if memory_mb > 512:
            return 0.5
        
        return 0.8

    def get_detailed_scores(self, candidate: Candidate, validation: ValidationResult, benchmark: Dict = None) -> Dict[str, float]:
        """Get detailed breakdown of scores."""
        return {
            'correctness': self._score_correctness(validation),
            'edge_coverage': self._score_edge_coverage(validation),
            'performance': self._score_performance(benchmark or {}),
            'security': self._score_security(validation),
            'efficiency': self._score_efficiency(candidate, benchmark or {}),
            'composite': self.score(candidate, validation, benchmark)
        }
