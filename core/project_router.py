"""Project detection and routing for different project types."""
import os
from pathlib import Path
from typing import Optional

from core.evolution_logger import EvolutionLogger


class ProjectRouter:
    """Detects project type and routes to appropriate validators/harnesses."""

    def __init__(self, logger: EvolutionLogger = None):
        self.logger = logger or EvolutionLogger()
        self.project_type = self.detect_project_type()

    def detect_project_type(self) -> str:
        """Infer project type from filesystem markers.
        
        Returns:
            Project type string
        """
        root = Path.cwd()
        
        # Check for kernel project
        if (root / 'kernel_lab').exists():
            self.logger.info("Detected: Kernel project")
            return 'kernel'
        
        # Check for Python package
        if (root / 'setup.py').exists() or (root / 'pyproject.toml').exists():
            self.logger.info("Detected: Python package")
            return 'python_package'
        
        # Check for Rust project
        if (root / 'Cargo.toml').exists():
            self.logger.info("Detected: Rust project")
            return 'rust'
        
        # Check for Go project
        if (root / 'go.mod').exists():
            self.logger.info("Detected: Go project")
            return 'go'
        
        # Check for C/C++ project
        if (root / 'CMakeLists.txt').exists() or (root / 'Makefile').exists():
            self.logger.info("Detected: C/C++ project")
            return 'cpp'
        
        self.logger.info("Detected: Generic project")
        return 'generic'

    def get_test_harness(self) -> str:
        """Get test harness template for current project type.
        
        Returns:
            Test harness code as string
        """
        harnesses = {
            'generic': self._generic_harness(),
            'python_package': self._python_harness(),
            'kernel': self._kernel_harness(),
            'rust': self._rust_harness(),
            'go': self._go_harness(),
            'cpp': self._cpp_harness()
        }
        
        return harnesses.get(self.project_type, harnesses['generic'])

    @staticmethod
    def _generic_harness() -> str:
        """Generic test harness for Python algorithms."""
        return '''
import sys
import candidate

# Import candidate function
if hasattr(candidate, 'main'):
    result = candidate.main()
    sys.exit(0 if result else 1)
else:
    print("No main function found")
    sys.exit(1)
'''

    @staticmethod
    def _python_harness() -> str:
        """Python package test harness."""
        return '''
import sys
import pytest

# Run pytest on candidate
exit_code = pytest.main(['-v', 'candidate.py'])
sys.exit(exit_code)
'''

    @staticmethod
    def _kernel_harness() -> str:
        """Kernel experiment harness."""
        return '''
# Kernel harness - would compile and test in isolated environment
# Placeholder for QEMU/container testing
print("Kernel candidate queued for isolated testing")
'''

    @staticmethod
    def _rust_harness() -> str:
        """Rust project harness."""
        return '''
# Rust harness - compile and run tests
print("Rust candidate queued for compilation")
'''

    @staticmethod
    def _go_harness() -> str:
        """Go project harness."""
        return '''
# Go harness - compile and run tests
print("Go candidate queued for compilation")
'''

    @staticmethod
    def _cpp_harness() -> str:
        """C/C++ project harness."""
        return '''
// C/C++ harness - compile and run
int main() {
    return 0;
}
'''
