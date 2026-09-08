# MERCURY-AEL

**Autonomous Evolution Loop for AI-driven software and kernel research**

An offline-first, deterministic platform for autonomous algorithm generation, validation, and improvement. MERCURY-AEL generates candidate source code, tests them through independent validators (not self-judging), and iteratively improves through scored evolution cycles.

## Quick Start

### Prerequisites
- Linux (Ubuntu 20.04+, Debian 11+, or similar)
- Python 3.9+
- Optional: available C/C++ compiler, optional Java/Rust compilers

### Installation

```bash
git clone https://github.com/yaser6411/MERCURY-AEL.git
cd MERCURY-AEL
chmod +x install.sh start.sh
./install.sh
```

### Run Evolution Campaign

```bash
# Single 10-round verification
./start.sh

# 100-round research campaign
./start.sh --campaign 100

# 1000-round extended campaign
./start.sh --campaign 1000

# Custom resource limits
./start.sh --campaign 100 --max-ram 2048 --max-cpu 2 --max-disk 5120
```

### Stop Running Campaign

Press `Ctrl+C` or send SIGTERM. The engine will safely halt and save state.

## Architecture

```
MERCURY-AEL/
  core/
    evolution_engine.py       # Main orchestration loop
    generator.py              # Candidate algorithm generation
    validator.py              # Static & dynamic validation
    scorer.py                 # Candidate scoring engine
    benchmark.py              # Performance benchmarking
    resource_monitor.py       # CPU/RAM/disk tracking
    sandbox.py                # Execution isolation
    snapshot_manager.py       # Immutable generation snapshots
    rollback_manager.py       # State rollback capability
    project_router.py         # Project detection & routing
    failure_analyzer.py       # Failure history analysis

  model/
    provider_interface.py     # LLM provider abstraction
    local_model_adapter.py    # Local LLM connection (future)
    deterministic_fallback.py # Offline algorithm pool

  kernel_lab/
    __init__.py
    candidate_kernel_code/    # Kernel candidate storage
    kernel_experiments/       # Kernel test harness
    kernel_build_specs/       # Kernel compile configs

  tests/
    unit/
      test_generator.py
      test_validator.py
      test_scorer.py
      test_evolution_engine.py
    property/
      test_properties.py      # Property-based tests
    edge/
      test_edge_cases.py      # Edge case suite
    performance/
      test_benchmark.py
    security/
      test_security.py

  config/
    hardware.yaml             # Hardware profile
    limits.yaml               # Resource policy
    projects.yaml             # Project definitions
    policies.yaml             # Acceptance policy gates

  candidates/                 # Current generation candidates
  verified/                   # Accepted candidates (immutable)
  rejected/                   # Rejected candidates
  snapshots/                  # Immutable snapshots
  reports/                    # JSON & Markdown reports
  logs/                       # Execution logs

  .github/workflows/
    syntax-check.yml
    unit-tests.yml
    static-analysis.yml
    security-scan.yml
    deterministic-verify.yml
    campaign-10.yml
    campaign-100.yml
    report-gen.yml

  .devcontainer/
    devcontainer.json
    Dockerfile

  requirements.txt
  install.sh
  start.sh
  README.md
  ARCHITECTURE.md
  MANIFEST.md
```

## Evolution Loop

```
FOR EACH GENERATION:
  1. Read current project state
  2. Analyze failure history
  3. Generate candidate code
  4. Static validation (syntax, imports)
  5. Compile (if applicable)
  6. Unit tests
  7. Property-based tests
  8. Edge case tests
  9. Performance benchmark
  10. Security validation
  11. Resource validation
  12. Score candidate
  13. Apply policy gates
  14. Accept/reject decision
  15. Snapshot if accepted
  16. Update evolution memory
  → NEXT GENERATION
```

## Verification Policy (Default)

A candidate is accepted only if it passes **all** gates:

| Gate | Policy |
|------|--------|
| Syntax | PASS |
| Compilation | PASS (when applicable) |
| Unit Tests | PASS |
| Property Tests | PASS |
| Edge Tests | PASS |
| Security Checks | PASS |
| Resource Limits | PASS |
| Benchmark | PASS |
| Minimum Score | ≥ 0.80 |

Configurable in `config/policies.yaml`.

## Resource Policy

Before launching a campaign, specify hard limits:

```yaml
# config/limits.yaml
max_ram_mb: 2048          # Maximum RAM consumption
max_cpu_percent: 50       # Maximum CPU utilization
max_cpu_time_sec: 300     # Maximum wall-clock time per generation
max_disk_mb: 5120         # Maximum disk usage
max_generations: 100      # Stop after N generations
max_candidate_size_kb: 512 # Maximum candidate size
max_execution_time_sec: 3600 # Campaign timeout
```

The engine **exits safely** when limits are reached.

## Campaign Sizes

- **Verification** (default): 10 rounds
- **Research**: 100 rounds
- **Extended Research**: 1000+ rounds

All configurable via `--campaign N`.

## Reports

Generated automatically in `reports/`:

- `campaign_TIMESTAMP.json` — Machine-readable results
- `campaign_TIMESTAMP.md` — Human-readable summary
- `candidates_TIMESTAMP.json` — All candidate metadata
- `evolution_tree_TIMESTAMP.json` — Generation lineage

Each report includes:
- Generation number
- Candidate hash
- Timestamp
- Hardware info
- Configuration
- Test results
- Benchmark scores
- Security validation
- Accept/reject decision
- Failure reasons (if applicable)

## GitHub Codespaces

Open in Codespaces and run:

```bash
./install.sh
./start.sh --campaign 10
```

The `.devcontainer/` environment includes all dependencies.

## LLM Architecture

MERCURY-AEL uses a **verification-first** model:

```
LLM
  ↓
Generate Candidate
  ↓
Independent Deterministic Validators
  ↓
Policy Engine
  ↓
Accept / Reject
```

**Key principle:** The LLM does NOT judge its own code. External validators make final decisions.

- **v0.1**: Deterministic fallback engine (no LLM required)
- **Future**: Optional local LLM via `model/provider_interface.py`
- **Always**: Works offline without internet

## Kernel Research

Kernel-focused candidates go to `kernel_lab/`:

- Candidates compiled but **not installed** on host
- Tested in isolated environments (QEMU, VM, container)
- Host kernel and bootloader **never modified**
- Deterministic kernel build specs in `kernel_build_specs/`

## Configuration

### Hardware Profile (`config/hardware.yaml`)

Automatically detected:

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
  - python
```

### Resource Limits (`config/limits.yaml`)

User-configurable before campaign:

```yaml
max_ram_mb: 2048
max_cpu_percent: 50
max_cpu_time_sec: 300
max_disk_mb: 5120
max_generations: 100
max_candidate_size_kb: 512
max_execution_time_sec: 3600
```

### Acceptance Policy (`config/policies.yaml`)

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
```

## Self-Test

```bash
./start.sh --self-test
```

Verifies:
- Environment setup ✓
- Python modules ✓
- Compiler detection ✓
- File permissions ✓
- Configuration validity ✓
- Sample generation ✓
- Sample validation ✓

## Testing

Run all test suites:

```bash
python -m pytest tests/ -v
```

Run specific suites:

```bash
python -m pytest tests/unit/ -v
python -m pytest tests/property/ -v
python -m pytest tests/edge/ -v
python -m pytest tests/security/ -v
python -m pytest tests/performance/ -v
```

## Success Criteria (v0.1)

- [x] Architecture defined
- [ ] Bootstrap (install.sh, start.sh)
- [ ] Core engine modules
- [ ] Configuration system
- [ ] Test framework
- [ ] Sandbox & isolation
- [ ] Snapshot/rollback
- [ ] Resource monitoring
- [ ] Report generation
- [ ] GitHub Actions workflows
- [ ] Codespaces integration
- [ ] Scientific integrity verified

## No Host Modifications

MERCURY-AEL **never**:
- Modifies host kernel
- Changes bootloader
- Updates BIOS/UEFI
- Modifies system configuration
- Installs candidates to host OS
- Runs unelevated code with sudo (unless explicit kernel_lab isolation)

All experiments remain within `MERCURY-AEL/` directory tree.

## Scientific Integrity

Every result includes:
- Generation number
- Candidate hash (SHA256)
- Timestamp (ISO 8601)
- Hardware information
- Configuration snapshot
- All test results
- Benchmark data
- Security validation output
- Score and accept/reject decision
- Failure reason (if applicable)

**Never fabricate results. Never omit tests. Reproducibility over speed.**

## Long-Term Vision

MERCURY-AEL is a research foundation toward AI-native systems:

```
AI
 ↓
software reasoning
 ↓
algorithm generation
 ↓
automated verification
 ↓
hardware-aware optimization
 ↓
isolated kernel experimentation
 ↓
microkernel research
 ↓
AI-native operating system research
```

## Contributing

MERCURY-AEL v0.1 is a research prototype. Contributions welcome:

1. Fork the repository
2. Create a feature branch
3. Add tests (unit + property)
4. Ensure all tests pass
5. Submit PR with generation history

## License

MIT (specify in LICENSE file)

## Questions?

- 📖 [ARCHITECTURE.md](./ARCHITECTURE.md) — Deep dive into components
- 🔧 [INSTALL.md](./INSTALL.md) — Installation troubleshooting
- 📊 [MANIFEST.md](./MANIFEST.md) — Candidate format & report spec

---

**MERCURY-AEL v0.1**  
*Autonomous Evolution Loop for AI-driven Research*
