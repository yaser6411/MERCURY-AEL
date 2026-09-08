"""Security-focused tests for MERCURY-AEL."""
import pytest
import hashlib
from datetime import datetime

from core.data_structures import Candidate
from core.validator import Validator


class TestSecurityValidation:
    """Test security validation features."""

    def test_detect_eval_usage(self, mock_config):
        """Test detection of eval() usage."""
        validator = Validator(mock_config)
        
        code = "result = eval('2 + 2')"
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        passed, details = validator._security_check(candidate)
        assert not passed
        assert any('eval' in issue.lower() for issue in details.get('issues', []))

    def test_detect_exec_usage(self, mock_config):
        """Test detection of exec() usage."""
        validator = Validator(mock_config)
        
        code = "exec('x = 1')"
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        passed, details = validator._security_check(candidate)
        assert not passed

    def test_detect_subprocess_call(self, mock_config):
        """Test detection of subprocess usage."""
        validator = Validator(mock_config)
        
        code = "subprocess.call(['ls', '/'])"
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        passed, details = validator._security_check(candidate)
        assert not passed

    def test_detect_os_system(self, mock_config):
        """Test detection of os.system usage."""
        validator = Validator(mock_config)
        
        code = "os.system('rm -rf /')"
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        passed, details = validator._security_check(candidate)
        assert not passed

    def test_safe_file_operations(self, mock_config):
        """Test that safe file operations pass security."""
        validator = Validator(mock_config)
        
        code = "with open('local.txt', 'w') as f: f.write('test')"
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        passed, details = validator._security_check(candidate)
        # Local file operations should pass
        assert passed

    def test_detect_import_abuse(self, mock_config):
        """Test detection of __import__ usage."""
        validator = Validator(mock_config)
        
        code = "m = __import__('os')"
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        passed, details = validator._security_check(candidate)
        assert not passed

    def test_safe_library_imports(self, mock_config):
        """Test that safe library usage passes security."""
        validator = Validator(mock_config)
        
        code = "import json\nimport hashlib\ndata = json.dumps({'test': 1})"
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        passed, details = validator._security_check(candidate)
        assert passed
