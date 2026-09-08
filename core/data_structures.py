"""Core data structures for MERCURY-AEL."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
import json


@dataclass
class Candidate:
    """A generated algorithm candidate."""
    source_code: str
    generation: int
    timestamp: datetime
    hash: str  # SHA256(source_code)
    project_type: str = 'generic'
    tags: List[str] = field(default_factory=list)
    language: str = 'python'

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'source_code': self.source_code[:100] + '...' if len(self.source_code) > 100 else self.source_code,
            'generation': self.generation,
            'timestamp': self.timestamp.isoformat(),
            'hash': self.hash,
            'project_type': self.project_type,
            'tags': self.tags,
            'language': self.language
        }


@dataclass
class ValidationResult:
    """Result of validating a candidate."""
    syntax_pass: bool
    compilation_pass: bool
    unit_tests_pass: bool
    property_tests_pass: bool
    edge_tests_pass: bool
    security_pass: bool
    resource_pass: bool
    benchmark_pass: bool
    details: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def passed(self) -> bool:
        """True if all mandatory gates passed."""
        return (
            self.syntax_pass
            and self.compilation_pass
            and self.unit_tests_pass
            and self.property_tests_pass
            and self.edge_tests_pass
            and self.security_pass
            and self.resource_pass
            and self.benchmark_pass
        )

    @property
    def pass_count(self) -> int:
        """Count of gates passed."""
        return sum([
            self.syntax_pass,
            self.compilation_pass,
            self.unit_tests_pass,
            self.property_tests_pass,
            self.edge_tests_pass,
            self.security_pass,
            self.resource_pass,
            self.benchmark_pass
        ])

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'syntax_pass': self.syntax_pass,
            'compilation_pass': self.compilation_pass,
            'unit_tests_pass': self.unit_tests_pass,
            'property_tests_pass': self.property_tests_pass,
            'edge_tests_pass': self.edge_tests_pass,
            'security_pass': self.security_pass,
            'resource_pass': self.resource_pass,
            'benchmark_pass': self.benchmark_pass,
            'passed': self.passed,
            'pass_count': self.pass_count,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class ExecutionResult:
    """Result of executing a candidate in sandbox."""
    returncode: int = -1
    stdout: str = ""
    stderr: str = ""
    success: bool = False
    execution_time_ms: float = 0.0
    memory_peak_mb: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'returncode': self.returncode,
            'stdout': self.stdout[:500],  # Truncate for logging
            'stderr': self.stderr[:500],
            'success': self.success,
            'execution_time_ms': self.execution_time_ms,
            'memory_peak_mb': self.memory_peak_mb,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class BenchmarkResult:
    """Performance benchmark result."""
    execution_times: List[float] = field(default_factory=list)
    memory_peak_mb: float = 0.0
    memory_avg_mb: float = 0.0
    throughput: float = 0.0  # ops/sec
    cpu_percent: float = 0.0
    passed: bool = True
    details: Dict = field(default_factory=dict)

    @property
    def avg_execution_time(self) -> float:
        """Average execution time in ms."""
        if not self.execution_times:
            return 0.0
        return sum(self.execution_times) / len(self.execution_times)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'execution_times_ms': self.execution_times,
            'avg_execution_time_ms': self.avg_execution_time,
            'memory_peak_mb': self.memory_peak_mb,
            'memory_avg_mb': self.memory_avg_mb,
            'throughput_ops_per_sec': self.throughput,
            'cpu_percent': self.cpu_percent,
            'passed': self.passed,
            'details': self.details
        }


@dataclass
class CampaignResult:
    """Results of a complete evolution campaign."""
    total_generations: int
    accepted_count: int
    rejected_count: int
    failed_count: int
    best_score: float
    best_candidate: Optional[Candidate]
    average_score: float
    snapshots: List[str] = field(default_factory=list)
    report_path: str = ""
    duration_sec: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    hardware_info: Dict = field(default_factory=dict)
    policy_config: Dict = field(default_factory=dict)
    generations_data: List[Dict] = field(default_factory=list)

    @property
    def acceptance_rate(self) -> float:
        """Percentage of candidates accepted."""
        total = self.accepted_count + self.rejected_count
        if total == 0:
            return 0.0
        return (self.accepted_count / total) * 100

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'total_generations': self.total_generations,
            'accepted_count': self.accepted_count,
            'rejected_count': self.rejected_count,
            'failed_count': self.failed_count,
            'acceptance_rate_percent': self.acceptance_rate,
            'best_score': self.best_score,
            'average_score': self.average_score,
            'snapshots': self.snapshots,
            'report_path': self.report_path,
            'duration_sec': self.duration_sec,
            'timestamp': self.timestamp.isoformat(),
            'hardware_info': self.hardware_info,
            'policy_config': self.policy_config
        }
