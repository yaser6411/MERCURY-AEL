#!/bin/bash
# MERCURY-AEL v0.1 Campaign Launcher
# Offline-first autonomous evolution loop

set -e

echo "====================================="
echo "MERCURY-AEL v0.1 - Campaign Launcher"
echo "====================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default campaign size
CAMPAIGN_SIZE=10
SELF_TEST=false
DETECT_HW=false
MAX_RAM=""
MAX_CPU=""
MAX_DISK=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --campaign)
            CAMPAIGN_SIZE="$2"
            shift 2
            ;;
        --self-test)
            SELF_TEST=true
            shift
            ;;
        --detect-hardware)
            DETECT_HW=true
            shift
            ;;
        --max-ram)
            MAX_RAM="$2"
            shift 2
            ;;
        --max-cpu)
            MAX_CPU="$2"
            shift 2
            ;;
        --max-disk)
            MAX_DISK="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--campaign N] [--self-test] [--detect-hardware] [--max-ram MB] [--max-cpu %] [--max-disk MB]"
            exit 1
            ;;
    esac
done

# Verify Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 not found${NC}"
    exit 1
fi

# Verify configuration exists
if [ ! -d "config" ]; then
    echo -e "${RED}ERROR: config/ directory not found. Run ./install.sh first${NC}"
    exit 1
fi

# Hardware detection
if [ "$DETECT_HW" = true ] || [ ! -f "config/hardware.yaml" ]; then
    echo "[*] Detecting hardware..."
    python3 << 'PYEOF'
import os
import yaml
import platform
import psutil
import subprocess

hardware = {
    'cpu_architecture': platform.machine(),
    'cpu_count': psutil.cpu_count(),
    'ram_mb': int(psutil.virtual_memory().total / 1024 / 1024),
    'disk_mb': int(psutil.disk_usage('/').total / 1024 / 1024),
    'os': platform.system(),
    'kernel_version': platform.release(),
    'available_compilers': [],
    'available_runtimes': ['python3']
}

# Check for compilers
for compiler in ['gcc', 'clang', 'g++', 'rustc', 'go']:
    try:
        result = subprocess.run(['which', compiler], capture_output=True)
        if result.returncode == 0:
            hardware['available_compilers'].append(compiler)
    except:
        pass

with open('config/hardware.yaml', 'w') as f:
    yaml.dump(hardware, f, default_flow_style=False)

print(f"CPU: {hardware['cpu_architecture']} ({hardware['cpu_count']} cores)")
print(f"RAM: {hardware['ram_mb']} MB")
print(f"Disk: {hardware['disk_mb']} MB")
print(f"Compilers: {', '.join(hardware['available_compilers']) or 'None'}")
PYEOF
fi

# Self-test mode
if [ "$SELF_TEST" = true ]; then
    echo ""
    echo -e "${BLUE}[SELF-TEST MODE]${NC}"
    echo ""
    
    echo "[1] Checking environment setup..."
    if [ -d "core" ] && [ -d "tests" ] && [ -d "config" ]; then
        echo -e "${GREEN}  ✓ Directory structure OK${NC}"
    else
        echo -e "${RED}  ✗ Missing directories${NC}"
        exit 1
    fi
    
    echo "[2] Checking Python modules..."
    python3 << 'PYEOF'
import sys
try:
    import yaml
    import pytest
    import psutil
    print("  ✓ Python modules OK")
except ImportError as e:
    print(f"  ✗ Missing module: {e}")
    sys.exit(1)
PYEOF
    
    echo "[3] Checking configuration validity..."
    python3 << 'PYEOF'
import yaml
import sys

try:
    with open('config/policies.yaml') as f:
        policies = yaml.safe_load(f)
    with open('config/limits.yaml') as f:
        limits = yaml.safe_load(f)
    with open('config/hardware.yaml') as f:
        hardware = yaml.safe_load(f)
    print("  ✓ Configuration files valid")
except Exception as e:
    print(f"  ✗ Config error: {e}")
    sys.exit(1)
PYEOF
    
    echo "[4] Checking file permissions..."
    if [ -x "install.sh" ] && [ -x "start.sh" ]; then
        echo -e "${GREEN}  ✓ Script permissions OK${NC}"
    else
        echo -e "${YELLOW}  ⚠ Setting executable permissions${NC}"
        chmod +x install.sh start.sh
    fi
    
    echo ""
    echo -e "${GREEN}✓ Self-test passed!${NC}"
    echo ""
    echo "You can now run evolution campaigns:"
    echo "  ./start.sh                 # 10-round campaign"
    echo "  ./start.sh --campaign 100  # 100-round campaign"
    exit 0
fi

# Main campaign execution
echo ""
echo -e "${BLUE}Campaign Configuration:${NC}"
echo "  Generations: $CAMPAIGN_SIZE"
echo "  Policy: config/policies.yaml"
echo "  Limits: config/limits.yaml"
echo "  Hardware: config/hardware.yaml"
if [ -n "$MAX_RAM" ]; then echo "  Max RAM: $MAX_RAM MB"; fi
if [ -n "$MAX_CPU" ]; then echo "  Max CPU: $MAX_CPU %"; fi
if [ -n "$MAX_DISK" ]; then echo "  Max Disk: $MAX_DISK MB"; fi
echo ""

# Verify logs directory
mkdir -p logs

# Run evolution engine
echo -e "${BLUE}[*] Starting evolution engine...${NC}"
echo ""

python3 << PYEOF
import sys
import os
import yaml
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load configuration
with open('config/policies.yaml') as f:
    policies = yaml.safe_load(f)
with open('config/limits.yaml') as f:
    limits = yaml.safe_load(f)
with open('config/hardware.yaml') as f:
    hardware = yaml.safe_load(f)

# Override limits if specified
if "$MAX_RAM":
    limits['max_ram_mb'] = int("$MAX_RAM")
if "$MAX_CPU":
    limits['max_cpu_percent'] = int("$MAX_CPU")
if "$MAX_DISK":
    limits['max_disk_mb'] = int("$MAX_DISK")

# Import and run evolution engine
try:
    from core.evolution_engine import EvolutionEngine
    from core.evolution_logger import EvolutionLogger
    
    logger = EvolutionLogger('logs/campaign.log')
    logger.info(f"Starting campaign: {$CAMPAIGN_SIZE} generations")
    logger.info(f"Hardware: {hardware['cpu_architecture']} ({hardware['cpu_count']} cores), {hardware['ram_mb']} MB RAM")
    logger.info(f"Policy minimum score: {policies['minimum_score']}")
    
    engine = EvolutionEngine(
        config={'policies': policies, 'limits': limits},
        hardware=hardware
    )
    
    result = engine.run_campaign($CAMPAIGN_SIZE)
    
    print(f"")
    print(f"${GREEN}Campaign Complete!${NC}")
    print(f"  Total generations: {result.total_generations}")
    print(f"  Accepted: {result.accepted_count}")
    print(f"  Rejected: {result.rejected_count}")
    print(f"  Best score: {result.best_score:.2f}")
    print(f"  Report: {result.report_path}")
    print(f"")
    
except ImportError:
    print(f"${YELLOW}⚠ Evolution engine modules not yet implemented.${NC}")
    print(f"  Modules to implement:")
    print(f"    - core/evolution_engine.py")
    print(f"    - core/generator.py")
    print(f"    - core/validator.py")
    print(f"    - core/scorer.py")
    print(f"")
    print(f"  Run: python -m pytest tests/ -v")
    print(f"  to verify test infrastructure")
    sys.exit(1)
except KeyboardInterrupt:
    print(f"${YELLOW}Campaign interrupted by user (SIGTERM)${NC}")
    sys.exit(130)
except Exception as e:
    print(f"${RED}Error: {e}${NC}")
    sys.exit(1)
PYEOF

exit_code=$?

echo ""
echo "Logs: logs/campaign.log"
echo "Reports: reports/"
echo ""

exit $exit_code
