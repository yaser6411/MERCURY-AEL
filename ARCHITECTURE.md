# MERCURY-AEL Architecture

## System Design Principles

1. **Offline-First**: Never requires internet. Deterministic fallback when LLM unavailable.
2. **Verification-First**: LLM generates, independent validators judge. Self-judging prohibited.
3. **Isolation**: All candidates run in sandbox. No host OS modification.
4. **Reproducibility**: Every result tagged with hash, timestamp, hardware, config.
5. **Safety**: Resource limits enforced before execution. STOP mechanism responsive.
6. **Transparency**: All decisions logged. No opaque acceptance.

---

## Core Modules

### `core/evolution_engine.py`

**Responsibility**: Orchestrate the complete evolution loop for a campaign.

```python
class EvolutionEngine:
    def __init__(self, config: dict, hardware: dict):
        self.config = config
        self.hardware = hardware
        self.generator = Generator(config)
        self.validator = Validator(config)
        self.scorer = Scorer(config)
        self.resource_monitor = ResourceMonitor(config)
        self.snapshot_mgr = SnapshotManager()
        self.rollback_mgr = RollbackManager()
        self.failure_analyzer = FailureAnalyzer()

    def run_campaign(self, num_generations: int) -> CampaignResult:
        """Main evolution loop."""
        for generation in range(num_generations):
            # 1. Check resource limits
            if self.resource_monitor.exceeded_limits():
                self.stop("Resource limits exceeded")
                break

            # 2. Analyze failure history
            failure_context = self.failure_analyzer.analyze()

            # 3. Generate candidate
            candidate = self.generator.generate(context=failure_context)

            # 4. Validate
            validation_result = self.validator.validate(candidate)
            if not validation_result.passed:
                self.reject_candidate(candidate, validation_result)
                continue

            # 5. Score
            score = self.scorer.score(candidate)

            # 6. Apply policy gates
            if self.apply_policy(candidate, score, validation_result):
                # Accept
                self.accept_candidate(candidate, score, validation_result)
                self.snapshot_mgr.create_snapshot(candidate, generation)
            else:
                # Reject
                self.reject_candidate(candidate, validation_result)

        return self.generate_report()

    def accept_candidate(self, candidate, score, validation):
        """Move to verified/ and record metadata."""
        pass

    def reject_candidate(self, candidate, reason):
        """Move to rejected/ and record metadata."""
        pass

    def apply_policy(self, candidate, score, validation) -> bool:
        """Apply configurable acceptance gates."""
        policy = self.config['policies']
        
        # All gates must pass
        if not validation.syntax_pass:
            return False
        if policy.get('require_compilation') and not validation.compilation_pass:
            return False
        if not validation.unit_tests_pass:
            return False
        if not validation.property_tests_pass:
            return False
        if not validation.edge_tests_pass:
            return False
        if not validation.security_pass:
            return False
        if not self.resource_monitor.within_limits(candidate):
            return False
        if score < policy.get('minimum_score', 0.80):
            return False

        return True

    def stop(self, reason: str):
        """Immediately halt generation and save state."""
        self.snapshot_mgr.save_state()
        logger.info(f"Campaign stopped: {reason}")
```

**Integration Points**:
- Uses Generator, Validator, Scorer, ResourceMonitor, SnapshotManager, RollbackManager
- Reads config/policies.yaml, config/limits.yaml
- Writes to candidates/, verified/, rejected/, logs/, reports/

---

### `core/generator.py`

**Responsibility**: Generate candidate algorithms from failure history and templates.

```python
class Generator:
    def __init__(self, config: dict):
        self.config = config
        self.provider = self._load_provider()
        self.fallback = DeterministicFallback()

    def generate(self, context: dict = None) -> Candidate:
        """Generate a new candidate algorithm."""
        # Use LLM if available; fall back to deterministic pool
        try:
            code = self.provider.generate(
                prompt=self._build_prompt(context),
                context=context
            )
        except (OfflineError, ModelUnavailable):
            code = self.fallback.generate(context)

        candidate = Candidate(
            source_code=code,
            generation=context.get('generation', 0),
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        return candidate

    def _build_prompt(self, context: dict) -> str:
        """Build generation prompt from failure history."""
        # Include:
        # - Failure patterns from previous generations
        # - Project requirements
        # - Hardware constraints
        # - Compilation requirements
        prompt = f"""
        Generate a Python algorithm that:
        {context.get('requirements', '')}
        
        Recent failures to avoid:
        {context.get('failure_patterns', '')}
        
        Hardware constraints:
        {context.get('hardware', '')}
        """
        return prompt
```

**Fallback Pool** (`deterministic_fallback.py`):
- Library of hand-crafted algorithms
- No LLM required
- Varies by context (sorting, search, encoding, etc.)
- System always works offline

---

### `core/validator.py`

**Responsibility**: Run static and dynamic tests; return pass/fail verdict.

```python
class ValidationResult:
    syntax_pass: bool
    compilation_pass: bool
    unit_tests_pass: bool
    property_tests_pass: bool
    edge_tests_pass: bool
    security_pass: bool
    resource_pass: bool
    benchmark_pass: bool
    details: dict

class Validator:
    def __init__(self, config: dict):
        self.config = config
        self.compilers = self._detect_compilers()

    def validate(self, candidate: Candidate) -> ValidationResult:
        """Run complete validation suite."""
        result = ValidationResult()

        # 1. Syntax
        result.syntax_pass = self._validate_syntax(candidate)
        if not result.syntax_pass:
            return result  # Fail fast

        # 2. Compilation
        if self._requires_compilation(candidate):
            result.compilation_pass = self._compile(candidate)
            if not result.compilation_pass:
                return result

        # 3. Unit tests
        result.unit_tests_pass, result.details['unit'] = self._run_unit_tests(candidate)

        # 4. Property tests
        result.property_tests_pass, result.details['property'] = self._run_property_tests(candidate)

        # 5. Edge case tests
        result.edge_tests_pass, result.details['edge'] = self._run_edge_tests(candidate)

        # 6. Security
        result.security_pass, result.details['security'] = self._security_check(candidate)

        # 7. Resource limits
        result.resource_pass = self._check_resource_usage(candidate)

        # 8. Benchmark
        result.benchmark_pass, result.details['benchmark'] = self._benchmark(candidate)

        return result

    def _validate_syntax(self, candidate: Candidate) -> bool:
        """Check syntax using AST parsing."""
        try:
            ast.parse(candidate.source_code)
            return True
        except SyntaxError:
            return False

    def _run_unit_tests(self, candidate) -> tuple:
        """Execute unit test suite against candidate."""
        # Run tests/unit/*.py against candidate
        pass

    def _security_check(self, candidate) -> tuple:
        """Static security analysis."""
        # Check for: os.system, subprocess, file writes outside sandbox, etc.
        pass
```

**Validators Included**:
- **Syntax**: AST parsing
- **Compilation**: GCC/Clang/etc. (if needed)
- **Unit Tests**: pytest against candidate
- **Property Tests**: hypothesis-based generative testing
- **Edge Cases**: boundary condition test suite
- **Security**: static analysis (bandit, custom rules)
- **Benchmark**: performance scoring

---

### `core/scorer.py`

**Responsibility**: Assign a score [0, 1] to a candidate based on test results and performance.

```python
class Scorer:
    def __init__(self, config: dict):
        self.config = config
        self.weights = config.get('scoring_weights', {
            'correctness': 0.40,      # Unit + property tests
            'edge_coverage': 0.15,    # Edge case handling
            'performance': 0.20,      # Benchmark score
            'security': 0.15,         # Security validation
            'efficiency': 0.10        # Resource usage
        })

    def score(self, candidate: Candidate, validation: ValidationResult, benchmark: dict) -> float:
        """Calculate composite score [0, 1]."""
        if not validation.syntax_pass or not validation.compilation_pass:
            return 0.0

        scores = {
            'correctness': self._score_correctness(validation),
            'edge_coverage': self._score_edge_coverage(validation),
            'performance': self._score_performance(benchmark),
            'security': self._score_security(validation),
            'efficiency': self._score_efficiency(candidate, benchmark)
        }

        # Weighted composite
        total = sum(
            scores[key] * self.weights[key]
            for key in scores
        )
        return min(max(total, 0.0), 1.0)  # Clamp [0, 1]

    def _score_correctness(self, validation: ValidationResult) -> float:
        """Score from unit + property test results."""
        unit_ratio = validation.details['unit'].get('pass_ratio', 0)
        property_ratio = validation.details['property'].get('pass_ratio', 0)
        return (unit_ratio + property_ratio) / 2.0

    def _score_performance(self, benchmark: dict) -> float:
        """Normalize benchmark metrics against baseline."""
        # Compare execution time, memory, etc. to baseline
        pass
```

**Scoring Model**:
- Weighted composite across multiple dimensions
- Baseline comparison (vs. previous generations)
- Configurable weights in `config/policies.yaml`

---

### `core/resource_monitor.py`

**Responsibility**: Track CPU, RAM, disk usage; enforce limits; trigger safe stop.

```python
class ResourceMonitor:
    def __init__(self, config: dict):
        self.limits = config.get('limits', {})
        self.process = psutil.Process()
        self.start_time = time.time()

    def exceeded_limits(self) -> bool:
        """Check if any resource limit exceeded."""
        ram_usage = self.process.memory_info().rss / 1024 / 1024  # MB
        if ram_usage > self.limits.get('max_ram_mb', 2048):
            logger.warning(f"RAM limit exceeded: {ram_usage}MB > {self.limits['max_ram_mb']}MB")
            return True

        cpu_percent = self.process.cpu_percent(interval=1)
        if cpu_percent > self.limits.get('max_cpu_percent', 50):
            logger.warning(f"CPU limit exceeded: {cpu_percent}% > {self.limits['max_cpu_percent']}%")
            return True

        elapsed = time.time() - self.start_time
        if elapsed > self.limits.get('max_execution_time_sec', 3600):
            logger.warning(f"Campaign timeout: {elapsed}s > {self.limits['max_execution_time_sec']}s")
            return True

        disk_usage = self._get_disk_usage() / 1024 / 1024  # MB
        if disk_usage > self.limits.get('max_disk_mb', 5120):
            logger.warning(f"Disk limit exceeded: {disk_usage}MB > {self.limits['max_disk_mb']}MB")
            return True

        return False

    def within_limits(self, candidate: Candidate) -> bool:
        """Check if candidate itself exceeds resource constraints."""
        size_kb = len(candidate.source_code) / 1024
        if size_kb > self.limits.get('max_candidate_size_kb', 512):
            return False
        return True

    def _get_disk_usage(self) -> float:
        """Get total disk usage of project directory."""
        total = 0
        for dirpath, dirnames, filenames in os.walk(os.getcwd()):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total += os.path.getsize(filepath)
        return total
```

**Enforcement**:
- Checks occur at start of each generation
- On limit exceeded: save state, log, exit gracefully
- Responsive to SIGTERM (Ctrl+C)

---

### `core/sandbox.py`

**Responsibility**: Execute candidate code in isolated, bounded environment.

```python
class Sandbox:
    def __init__(self, config: dict):
        self.config = config
        self.tempdir = tempfile.mkdtemp(prefix='mercury_')

    def run_candidate(self, candidate: Candidate, test_harness: str) -> ExecutionResult:
        """Execute candidate in isolated sandbox."""
        result = ExecutionResult()

        try:
            # Write candidate to temp file
            candidate_path = os.path.join(self.tempdir, 'candidate.py')
            with open(candidate_path, 'w') as f:
                f.write(candidate.source_code)

            # Write test harness
            harness_path = os.path.join(self.tempdir, 'test.py')
            with open(harness_path, 'w') as f:
                f.write(test_harness)

            # Execute with timeout
            timeout = self.config.get('sandbox_timeout_sec', 60)
            process = subprocess.Popen(
                ['python', harness_path],
                cwd=self.tempdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout
            )
            stdout, stderr = process.communicate()

            result.returncode = process.returncode
            result.stdout = stdout.decode('utf-8', errors='replace')
            result.stderr = stderr.decode('utf-8', errors='replace')
            result.success = process.returncode == 0

        except subprocess.TimeoutExpired:
            result.success = False
            result.stderr = f"Timeout after {timeout}s"
        except Exception as e:
            result.success = False
            result.stderr = str(e)
        finally:
            shutil.rmtree(self.tempdir)

        return result
```

**Key Properties**:
- Temporary isolated directory per execution
- Timeout enforcement
- No access to host filesystem (except project root, read-only)
- Cleaned up after execution
- Stdout/stderr captured

---

### `core/snapshot_manager.py`

**Responsibility**: Create immutable snapshots of accepted generations.

```python
class SnapshotManager:
    def __init__(self, base_dir: str = 'snapshots'):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def create_snapshot(self, candidate: Candidate, generation: int, 
                       validation: ValidationResult, score: float):
        """Create immutable snapshot of accepted candidate."""
        snapshot_id = f"gen-{generation:06d}-{candidate.hash[:8]}"
        snapshot_dir = os.path.join(self.base_dir, snapshot_id)
        os.makedirs(snapshot_dir, exist_ok=True)

        # Write candidate source
        with open(os.path.join(snapshot_dir, 'source.py'), 'w') as f:
            f.write(candidate.source_code)

        # Write metadata
        metadata = {
            'generation': generation,
            'timestamp': candidate.timestamp.isoformat(),
            'hash': candidate.hash,
            'score': score,
            'validation': validation.to_dict(),
            'immutable': True
        }
        with open(os.path.join(snapshot_dir, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)

        # Make immutable
        os.chmod(os.path.join(snapshot_dir, 'source.py'), 0o444)
        os.chmod(os.path.join(snapshot_dir, 'metadata.json'), 0o444)

        logger.info(f"Snapshot created: {snapshot_id}")
        return snapshot_id

    def list_snapshots(self) -> list:
        """List all snapshots in order."""
        return sorted(os.listdir(self.base_dir))

    def get_latest_snapshot(self) -> dict:
        """Retrieve most recent snapshot."""
        snapshots = self.list_snapshots()
        if not snapshots:
            return None
        latest_id = snapshots[-1]
        return self.load_snapshot(latest_id)

    def load_snapshot(self, snapshot_id: str) -> dict:
        """Load snapshot metadata and source."""
        snapshot_dir = os.path.join(self.base_dir, snapshot_id)
        with open(os.path.join(snapshot_dir, 'metadata.json')) as f:
            metadata = json.load(f)
        with open(os.path.join(snapshot_dir, 'source.py')) as f:
            source = f.read()
        return {'id': snapshot_id, 'metadata': metadata, 'source': source}
```

**Immutability**:
- Files written with read-only permissions (0o444)
- Separate snapshot per generation
- Indexed by generation number and candidate hash

---

### `core/rollback_manager.py`

**Responsibility**: Restore state to previous generation.

```python
class RollbackManager:
    def __init__(self, snapshot_mgr: SnapshotManager):
        self.snapshot_mgr = snapshot_mgr

    def rollback_to_generation(self, generation: int):
        """Restore state to specified generation."""
        snapshots = self.snapshot_mgr.list_snapshots()
        target = None
        for snapshot_id in snapshots:
            if snapshot_id.startswith(f"gen-{generation:06d}"):
                target = snapshot_id
                break

        if not target:
            logger.error(f"No snapshot found for generation {generation}")
            return False

        snapshot = self.snapshot_mgr.load_snapshot(target)

        # Copy verified candidate back to candidates/
        candidate_id = snapshot['id']
        dst = os.path.join('candidates', f'{candidate_id}.py')
        with open(dst, 'w') as f:
            f.write(snapshot['source'])

        logger.info(f"Rolled back to generation {generation} ({target})")
        return True

    def rollback_to_latest(self):
        """Restore to most recent verified snapshot."""
        latest = self.snapshot_mgr.get_latest_snapshot()
        if not latest:
            logger.error("No snapshots available for rollback")
            return False

        generation = int(latest['id'].split('-')[1])
        return self.rollback_to_generation(generation)
```

---

### `core/benchmark.py`

**Responsibility**: Measure performance: execution time, memory, resource efficiency.

```python
class Benchmark:
    def __init__(self, config: dict):
        self.config = config

    def run_benchmark(self, candidate: Candidate, test_cases: list) -> dict:
        """Run candidate through benchmark suite."""
        results = {
            'execution_times': [],
            'memory_peak': 0,
            'memory_avg': 0,
            'throughput': 0,
            'energy_efficiency': 0
        }

        for test_case in test_cases:
            start = time.time()
            start_mem = psutil.Process().memory_info().rss

            # Execute candidate
            # (implementation depends on candidate type)

            elapsed = time.time() - start
            peak_mem = psutil.Process().memory_info().rss

            results['execution_times'].append(elapsed)
            results['memory_peak'] = max(results['memory_peak'], peak_mem)

        results['memory_avg'] = np.mean([...])
        results['throughput'] = len(test_cases) / sum(results['execution_times'])

        return results
```

---

### `core/failure_analyzer.py`

**Responsibility**: Analyze patterns in rejected/failed candidates to guide next generation.

```python
class FailureAnalyzer:
    def __init__(self, base_dir: str = 'rejected'):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def analyze(self) -> dict:
        """Identify failure patterns to avoid in next generation."""
        patterns = {
            'syntax_errors': [],
            'compilation_errors': [],
            'test_failures': [],
            'security_issues': [],
            'performance_degradation': []
        }

        for filename in os.listdir(self.base_dir):
            metadata_path = os.path.join(self.base_dir, filename, 'metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path) as f:
                    meta = json.load(f)
                    failure_type = meta.get('failure_type')
                    if failure_type in patterns:
                        patterns[failure_type].append(meta.get('details', ''))

        return patterns
```

---

### `core/project_router.py`

**Responsibility**: Detect project type and route to appropriate test/validation suite.

```python
class ProjectRouter:
    def detect_project_type(self) -> str:
        """Infer project type from structure."""
        if os.path.exists('kernel_lab'):
            return 'kernel'
        if os.path.exists('setup.py'):
            return 'python_package'
        if os.path.exists('Cargo.toml'):
            return 'rust'
        if os.path.exists('go.mod'):
            return 'go'
        return 'generic'

    def get_validator_for_project(self, project_type: str) -> Validator:
        """Return appropriate validator for project type."""
        # Kernel projects → kernel validator
        # Python → Python validator
        # etc.
        pass

    def get_test_harness(self, project_type: str) -> str:
        """Return test harness template for project type."""
        pass
```

---

## Model Layer

### `model/provider_interface.py`

```python
class ModelProvider(ABC):
    """Interface for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, context: dict = None) -> str:
        """Generate candidate source code from prompt."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is configured and reachable."""
        pass
```

### `model/deterministic_fallback.py`

```python
class DeterministicFallback:
    """Offline algorithm pool (no LLM required)."""

    ALGORITHM_POOL = {
        'sort': [
            # Quicksort variants
            # Mergesort variants
            # Insertion sort variants
        ],
        'search': [
            # Binary search variants
            # Linear search variants
        ],
        'encode': [
            # Base64 variants
            # Hash function variants
        ]
    }

    def generate(self, context: dict = None) -> str:
        """Return candidate from deterministic pool."""
        category = context.get('category', 'generic')
        pool = self.ALGORITHM_POOL.get(category, [])
        if pool:
            return random.choice(pool)
        return self.generic_algorithm()
```

---

## Data Structures

### `Candidate`

```python
@dataclass
class Candidate:
    source_code: str
    generation: int
    timestamp: datetime
    hash: str  # SHA256(source_code)
    project_type: str = 'generic'
    tags: list = field(default_factory=list)
```

### `ValidationResult`

```python
@dataclass
class ValidationResult:
    syntax_pass: bool
    compilation_pass: bool
    unit_tests_pass: bool
    property_tests_pass: bool
    edge_tests_pass: bool
    security_pass: bool
    resource_pass: bool
    benchmark_pass: bool
    details: dict = field(default_factory=dict)
    passed: property  # True if all mandatory gates passed
```

### `CampaignResult`

```python
@dataclass
class CampaignResult:
    total_generations: int
    accepted_count: int
    rejected_count: int
    failed_count: int
    best_score: float
    best_candidate: Candidate
    average_score: float
    snapshots: list
    report_path: str
```

---

## Configuration Files

### `config/policies.yaml`

```yaml
verification_cycles: 10
gates:
  syntax: required
  compilation: required
  unit_tests: required
  property_tests: required
  edge_tests: required
  security_checks: required
  resource_limits: required
  benchmark: required
minimum_score: 0.80

scoring_weights:
  correctness: 0.40
  edge_coverage: 0.15
  performance: 0.20
  security: 0.15
  efficiency: 0.10
```

### `config/limits.yaml`

```yaml
max_ram_mb: 2048
max_cpu_percent: 50
max_cpu_time_sec: 300
max_disk_mb: 5120
max_generations: 100
max_candidate_size_kb: 512
max_execution_time_sec: 3600
sandbox_timeout_sec: 60
```

### `config/hardware.yaml`

Auto-generated on first run:

```yaml
cpu_architecture: x86_64
cpu_count: 8
ram_mb: 16384
disk_mb: 500000
os: Linux
kernel_version: 5.15.0
available_compilers:
  - gcc
  - clang
available_runtimes:
  - python3
```

---

## Report Generation

### JSON Report Format

```json
{
  "campaign": {
    "timestamp": "2026-09-08T10:30:00Z",
    "duration_sec": 325,
    "total_generations": 10,
    "accepted": 3,
    "rejected": 7,
    "failed": 0
  },
  "hardware": {
    "cpu_count": 8,
    "ram_mb": 16384,
    "os": "Linux 5.15.0"
  },
  "policy": {
    "verification_cycles": 10,
    "minimum_score": 0.80
  },
  "generations": [
    {
      "number": 1,
      "timestamp": "2026-09-08T10:30:05Z",
      "candidate_hash": "a1b2c3d4...",
      "score": 0.82,
      "accepted": true,
      "validation": {
        "syntax": true,
        "compilation": true,
        "unit_tests": true,
        "property_tests": true,
        "edge_tests": true,
        "security": true,
        "benchmark": { "execution_time_ms": 42 }
      },
      "snapshot_id": "gen-000001-a1b2c3d4"
    }
  ],
  "best_candidate": {
    "generation": 7,
    "score": 0.91,
    "hash": "xyz789abc...",
    "snapshot": "gen-000007-xyz789ab"
  }
}
```

---

## Integration: Full Flow

```
User runs: ./start.sh --campaign 10

    ↓

load_config()
  load config/limits.yaml
  load config/policies.yaml
  load config/hardware.yaml (or auto-detect)

    ↓

resource_monitor.check_limits()
  verify max_ram, max_cpu, max_disk

    ↓

FOR generation 1..10:

  failure_analyzer.analyze()
    read rejected/ directory
    extract patterns

  generator.generate(context)
    LLM.generate() or DeterministicFallback.generate()
    return Candidate

  validator.validate(candidate)
    syntax ✓
    compile ✓ (if applicable)
    unit tests ✓
    property tests ✓
    edge tests ✓
    security ✓
    return ValidationResult

  IF all validation gates passed:

    benchmark.run_benchmark(candidate)
      measure execution time, memory
      return benchmark data

    scorer.score(candidate, validation, benchmark)
      weighted composite score [0, 1]
      return float

    IF score >= policy.minimum_score:

      snapshot_manager.create_snapshot(candidate, generation)
        write to snapshots/gen-XXXXXX-HASH/
        make immutable (chmod 0o444)

      resource_monitor.check_limits()
        exit if exceeded

    ELSE:
      reject_candidate()
      write to rejected/

  ELSE:
    reject_candidate()
    write to rejected/

  ↓

generate_report()
  write reports/campaign_TIMESTAMP.json
  write reports/campaign_TIMESTAMP.md
  return CampaignResult

Exit with status code (0 if success, 1 if error)
```

---

## Safety & Guarantees

1. **No Host Modification**: All work confined to `MERCURY-AEL/`
2. **Reproducible**: Every result tagged with hash, timestamp, hardware
3. **Deterministic Fallback**: Works offline without internet
4. **Resource-Bounded**: Limits enforced before execution
5. **Reversible**: Rollback to any previous snapshot
6. **Honest Reporting**: Never fabricate results, never omit tests

---

## Version 0.1 Completeness Checklist

- [ ] Bootstrap complete (install.sh, start.sh)
- [ ] Core modules implemented
- [ ] Configuration system
- [ ] Test framework
- [ ] GitHub Actions workflows
- [ ] Codespaces integration
- [ ] Report generation
- [ ] Self-test passing
- [ ] 10-round campaign passing
- [ ] 100-round campaign passing
- [ ] Snapshot/rollback verified
- [ ] No host modifications verified
