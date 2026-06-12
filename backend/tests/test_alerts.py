from __future__ import annotations
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.alerts import _send_webhook, _send_email


@pytest.mark.asyncio
async def test_send_webhook_payload():
    """Test webhook sends correct payload structure."""
    mock_job = MagicMock()
    mock_job.source = "openai"
    mock_job.error_message = "Page structure changed"
    mock_job.id = "test-uuid"
    mock_job.finished_at = "2025-01-15T02:15:00Z"

    with patch("app.alerts.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock()

        await _send_webhook("https://hooks.example.com/alert", mock_job)

        mock_client.post.assert_called_once()
        call_kwargs = mock_client.post.call_args
        payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert payload["source"] == "openai"
        assert payload["error"] == "Page structure changed"


@pytest.mark.asyncio
async def test_send_email_skips_when_no_smtp():
    """Email sending skips when SMTP not configured."""
    mock_job = MagicMock()
    mock_job.source = "openai"
    mock_job.error_message = "Failed"
    mock_job.finished_at = None

    with patch("app.alerts.settings") as mock_settings:
        mock_settings.smtp_host = ""
        await _send_email("admin@example.com", mock_job)
        # Should return without error when smtp_host is empty
