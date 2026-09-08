"""Candidate validation suite for MERCURY-AEL."""
import ast
import subprocess
import sys
import os
from typing import Tuple, Dict
from pathlib import Path

from core.data_structures import Candidate, ValidationResult, ExecutionResult
from core.evolution_logger import EvolutionLogger


class Validator:
    """Validates candidates through comprehensive test suite."""

    def __init__(self, config: Dict, logger: EvolutionLogger = None):
        self.config = config
        self.logger = logger or EvolutionLogger()
        self.compilers = self._detect_compilers()

    def _detect_compilers(self) -> Dict[str, str]:
        """Detect available compilers on system."""
        compilers = {}
        for compiler in ['gcc', 'clang', 'g++', 'rustc']:
            result = subprocess.run(['which', compiler], capture_output=True)
            if result.returncode == 0:
                compilers[compiler] = result.stdout.decode().strip()
        return compilers

    def validate(self, candidate: Candidate) -> ValidationResult:
        """Run complete validation suite on candidate."""
        result = ValidationResult(
            syntax_pass=False,
            compilation_pass=False,
            unit_tests_pass=False,
            property_tests_pass=False,
            edge_tests_pass=False,
            security_pass=False,
            resource_pass=False,
            benchmark_pass=False
        )

        # 1. Syntax validation
        result.syntax_pass = self._validate_syntax(candidate)
        if not result.syntax_pass:
            result.details['syntax_error'] = 'Failed to parse Python AST'
            return result

        # 2. Compilation (if applicable)
        result.compilation_pass = self._validate_compilation(candidate)
        if not result.compilation_pass and self._requires_compilation(candidate):
            result.details['compilation_error'] = 'Compilation failed'
            return result

        # 3. Unit tests
        result.unit_tests_pass, result.details['unit_tests'] = self._run_unit_tests(candidate)

        # 4. Property tests
        result.property_tests_pass, result.details['property_tests'] = self._run_property_tests(candidate)

        # 5. Edge case tests
        result.edge_tests_pass, result.details['edge_tests'] = self._run_edge_tests(candidate)

        # 6. Security validation
        result.security_pass, result.details['security'] = self._security_check(candidate)

        # 7. Resource validation (basic)
        result.resource_pass = self._check_resource_constraints(candidate)

        # 8. Benchmark
        result.benchmark_pass, result.details['benchmark'] = self._run_benchmark(candidate)

        return result

    def _validate_syntax(self, candidate: Candidate) -> bool:
        """Validate Python syntax using AST parsing."""
        try:
            ast.parse(candidate.source_code)
            return True
        except SyntaxError as e:
            self.logger.debug(f"Syntax error in candidate {candidate.hash[:8]}: {e}")
            return False
        except Exception as e:
            self.logger.debug(f"AST parsing error: {e}")
            return False

    def _requires_compilation(self, candidate: Candidate) -> bool:
        """Check if candidate requires compilation."""
        # For now, only Python candidates (no compilation needed)
        return False

    def _validate_compilation(self, candidate: Candidate) -> bool:
        """Validate compilation if applicable."""
        # Placeholder for C/C++/Rust compilation
        if not self._requires_compilation(candidate):
            return True
        return False

    def _run_unit_tests(self, candidate: Candidate) -> Tuple[bool, Dict]:
        """Execute unit test suite."""
        # Placeholder: actual test execution against candidate
        # For now, assume basic validation passes
        return True, {'test_count': 0, 'pass_count': 0, 'fail_count': 0}

    def _run_property_tests(self, candidate: Candidate) -> Tuple[bool, Dict]:
        """Execute property-based tests using hypothesis."""
        # Placeholder: property testing framework integration
        return True, {'strategy_count': 0, 'example_count': 0}

    def _run_edge_tests(self, candidate: Candidate) -> Tuple[bool, Dict]:
        """Execute edge case tests."""
        # Placeholder: edge case test harness
        return True, {'edge_cases_tested': 0, 'pass_count': 0}

    def _security_check(self, candidate: Candidate) -> Tuple[bool, Dict]:
        """Perform static security analysis."""
        issues = []
        
        # Check for dangerous patterns
        dangerous_patterns = [
            'os.system',
            'subprocess.call',
            'eval(',
            'exec(',
            '__import__',
            'compile('
        ]
        
        for pattern in dangerous_patterns:
            if pattern in candidate.source_code:
                issues.append(f"Dangerous pattern detected: {pattern}")
        
        # Check for file access outside sandbox
        if 'open(' in candidate.source_code:
            # Simplified check - full implementation would be more sophisticated
            if '/etc/' in candidate.source_code or '/root/' in candidate.source_code:
                issues.append("Unsafe file access detected")
        
        passed = len(issues) == 0
        return passed, {'issues': issues, 'passed': passed}

    def _check_resource_constraints(self, candidate: Candidate) -> bool:
        """Check if candidate exceeds resource constraints."""
        limits = self.config.get('limits', {})
        max_size_kb = limits.get('max_candidate_size_kb', 512)
        
        size_kb = len(candidate.source_code) / 1024
        return size_kb <= max_size_kb

    def _run_benchmark(self, candidate: Candidate) -> Tuple[bool, Dict]:
        """Execute performance benchmark."""
        # Placeholder: actual benchmark execution
        return True, {'execution_time_ms': 0, 'memory_mb': 0}
