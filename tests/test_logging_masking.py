"""
tests/test_logging_masking.py -- E-02: Secret masking filter
10 tests covering API key masking, Bearer token masking, env-var assignment
masking, false-positive avoidance, and no-crash guarantees.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

from scripts.comprehensive_logging import _mask_secrets, _SecretMaskingFilter
import logging


class TestMaskSecrets:

    def test_sk_api_key_masked(self):
        line = "Calling API with key sk-abcdefghijklmnopqrstuvwxyz123456"
        result = _mask_secrets(line)
        assert "sk-" not in result or "[REDACTED]" in result
        assert "abcdefghijklmnopqrstuvwxyz123456" not in result

    def test_bearer_token_masked(self):
        line = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9abc123xyz"
        result = _mask_secrets(line)
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9abc123xyz" not in result
        assert "[REDACTED]" in result

    def test_api_key_env_assignment_masked(self):
        line = "Loaded PRIMARY_API_KEY=sk-super-secret-value-here-12345"
        result = _mask_secrets(line)
        assert "sk-super-secret-value-here-12345" not in result
        assert "[REDACTED]" in result

    def test_password_env_assignment_masked(self):
        line = "DB_PASSWORD=mysupersecretpassword123"
        result = _mask_secrets(line)
        assert "mysupersecretpassword123" not in result
        assert "[REDACTED]" in result

    def test_short_value_not_masked(self):
        # Values < 8 chars should NOT be masked (too short to be a real secret)
        line = "RETRY_COUNT=3"
        result = _mask_secrets(line)
        assert result == line

    def test_normal_text_untouched(self):
        line = "User asked about rune Thurisaz and its meaning in the Elder Futhark."
        result = _mask_secrets(line)
        assert result == line

    def test_bearer_prefix_preserved(self):
        line = "Header: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9verylongtoken"
        result = _mask_secrets(line)
        assert "Bearer" in result
        assert "[REDACTED]" in result

    def test_multiple_secrets_in_one_line(self):
        line = ("key=sk-aaabbbcccdddeeefffggghhh and also "
                "SECRET=averylongsecretvaluethatshouldbemasked")
        result = _mask_secrets(line)
        assert "sk-aaabbbcccdddeeefffggghhh" not in result
        assert "averylongsecretvaluethatshouldbemasked" not in result

    def test_mask_never_raises_on_garbage_input(self):
        # Must not raise even with bizarre input
        result = _mask_secrets(None)  # type: ignore[arg-type]
        # Either returns original or empty string — no exception
        assert result is not None or result == ""

    def test_secret_masking_filter_mutates_record(self):
        filt = _SecretMaskingFilter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="API key is sk-secretabcdefghijklmnopqrstu",
            args=(), exc_info=None,
        )
        filt.filter(record)
        assert "sk-secretabcdefghijklmnopqrstu" not in record.msg
        assert "[REDACTED]" in record.msg
