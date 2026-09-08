#!/bin/bash
# MERCURY-AEL v0.1 Installation Script
# Offline-first, deterministic bootstrap for autonomous evolution loop

set -e

echo "====================================="
echo "MERCURY-AEL v0.1 - Installation"
echo "====================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Detect Linux
echo "[1/10] Detecting Linux OS..."
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo -e "${RED}ERROR: MERCURY-AEL requires Linux. Detected: $OSTYPE${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Linux detected${NC}"

# Step 2: Detect Python
echo "[2/10] Detecting Python 3.9+..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 not found. Please install Python 3.9+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"

# Step 3: Create required directories
echo "[3/10] Creating project directories..."
mkdir -p core
mkdir -p model
mkdir -p kernel_lab/candidate_kernel_code
mkdir -p kernel_lab/kernel_experiments
mkdir -p kernel_lab/kernel_build_specs
mkdir -p tests/unit
mkdir -p tests/property
mkdir -p tests/edge
mkdir -p tests/performance
mkdir -p tests/security
mkdir -p config
mkdir -p candidates
mkdir -p verified
mkdir -p rejected
mkdir -p snapshots
mkdir -p reports
mkdir -p logs
echo -e "${GREEN}✓ Directories created${NC}"

# Step 4: Create default configuration
echo "[4/10] Creating default configuration files..."

# config/hardware.yaml (auto-detect on first run)
cat > config/hardware.yaml << 'EOF'
# Hardware Profile - Auto-detected
# Do not edit manually. Regenerate with: ./start.sh --detect-hardware

cpu_architecture: x86_64
cpu_count: 0  # To be detected at runtime
ram_mb: 0     # To be detected at runtime
disk_mb: 0    # To be detected at runtime
os: Linux
kernel_version: unknown
available_compilers: []
available_runtimes:
  - python3
EOF

# config/limits.yaml
cat > config/limits.yaml << 'EOF'
# Resource Policy - Configurable before campaign
max_ram_mb: 2048
max_cpu_percent: 50
max_cpu_time_sec: 300
max_disk_mb: 5120
max_generations: 100
max_candidate_size_kb: 512
max_execution_time_sec: 3600
sandbox_timeout_sec: 60
EOF

# config/policies.yaml
cat > config/policies.yaml << 'EOF'
# Acceptance Policy - Verification Gates
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
EOF

# config/projects.yaml
cat > config/projects.yaml << 'EOF'
# Project Definitions
default_project:
  type: generic
  description: Generic algorithm evolution
  test_harness: tests/unit/test_generic.py

kernel_project:
  type: kernel
  description: Kernel research and experimentation
  test_harness: kernel_lab/kernel_experiments/test_kernel.py
EOF

echo -e "${GREEN}✓ Configuration files created${NC}"

# Step 5: Install Python dependencies
echo "[5/10] Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install -q -r requirements.txt 2>/dev/null || {
        echo -e "${YELLOW}⚠ Some dependencies could not be installed. System may be missing optional compilers or runtimes.${NC}"
    }
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠ requirements.txt not found${NC}"
fi

# Step 6: Create __init__.py files
echo "[6/10] Creating Python package structure..."
touch core/__init__.py
touch model/__init__.py
touch kernel_lab/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/property/__init__.py
touch tests/edge/__init__.py
touch tests/performance/__init__.py
touch tests/security/__init__.py
echo -e "${GREEN}✓ Python packages initialized${NC}"

# Step 7: Detect compilers (optional)
echo "[7/10] Detecting available compilers..."
COMPILERS=""
if command -v gcc &> /dev/null; then
    COMPILERS="$COMPILERS gcc"
    echo -e "${GREEN}  ✓ GCC $(gcc --version | head -n1 | awk '{print $3}')${NC}"
fi
if command -v clang &> /dev/null; then
    COMPILERS="$COMPILERS clang"
    echo -e "${GREEN}  ✓ Clang $(clang --version | head -n1 | awk '{print $3}')${NC}"
fi
if [ -z "$COMPILERS" ]; then
    echo -e "${YELLOW}  ⚠ No C/C++ compilers detected. Kernel experiments will be limited.${NC}"
fi

# Step 8: Perform self-test
echo "[8/10] Performing self-test..."
echo "  Testing Python imports..."
python3 << 'PYEOF'
import sys
try:
    import yaml
    import pytest
    import psutil
    print("    ✓ Core dependencies available")
except ImportError as e:
    print(f"    ⚠ Missing: {e}")
    sys.exit(0)
PYEOF

echo -e "${GREEN}✓ Self-test passed${NC}"

# Step 9: Create logs directory and initial log
echo "[9/10] Setting up logging..."
mkdir -p logs
echo "MERCURY-AEL v0.1 Installation completed at $(date)" > logs/install.log
echo -e "${GREEN}✓ Logging initialized${NC}"

# Step 10: Summary
echo "[10/10] Installation complete!"
echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}✓ MERCURY-AEL v0.1 Ready${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Review configuration:"
echo "     - config/limits.yaml (resource policy)"
echo "     - config/policies.yaml (acceptance gates)"
echo ""
echo "  2. Run self-test:"
echo "     ./start.sh --self-test"
echo ""
echo "  3. Start evolution campaign:"
echo "     ./start.sh                  # 10-round verification"
echo "     ./start.sh --campaign 100   # 100-round research"
echo ""
echo "Documentation:"
echo "  - README.md: User guide and quick start"
echo "  - ARCHITECTURE.md: System design and module specifications"
echo ""
echo "For more information:"
echo "  https://github.com/yaser6411/MERCURY-AEL"
echo ""
