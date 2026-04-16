"""Tests for Syncthing diagnostics module."""
from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from custom_components.syncthing_extended.diagnostics import (
    TO_REDACT,
    async_get_config_entry_diagnostics,
)
from tests.conftest import build_mock_coordinator_data


def _make_entry():
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.as_dict.return_value = {
        "entry_id": "test_entry",
        "data": {"host": "192.168.1.1", "api_key": "secret-key"},
        "options": {},
    }
    coordinator = MagicMock()
    coordinator.data = build_mock_coordinator_data()
    entry.runtime_data = coordinator
    return entry


def test_diagnostics_redacts_api_key():
    async def _run():
        entry = _make_entry()
        return await async_get_config_entry_diagnostics(MagicMock(), entry)

    diag = asyncio.run(_run())
    config = diag["config_entry"]["data"]
    assert config["api_key"] == "**REDACTED**"
    assert config["host"] == "192.168.1.1"


def test_diagnostics_contains_system_data():
    async def _run():
        entry = _make_entry()
        return await async_get_config_entry_diagnostics(MagicMock(), entry)

    diag = asyncio.run(_run())
    assert diag["system"]["version"]["version"] == "v1.29.0"
    # myID redacted in system block
    assert diag["system"]["status"]["myID"] == "**REDACTED**"


def test_diagnostics_includes_folders():
    async def _run():
        entry = _make_entry()
        return await async_get_config_entry_diagnostics(MagicMock(), entry)

    diag = asyncio.run(_run())
    assert len(diag["folders"]) == 2
    folder_ids = [f["id"] for f in diag["folders"]]
    assert "abcd-1234" in folder_ids
    assert "efgh-5678" in folder_ids
    doc_folder = next(f for f in diag["folders"] if f["id"] == "abcd-1234")
    assert doc_folder["label"] == "Documents"
    assert "status" in doc_folder
    assert "completion" in doc_folder
    assert "stats" in doc_folder


def test_diagnostics_includes_devices_and_redacts_device_id():
    async def _run():
        entry = _make_entry()
        return await async_get_config_entry_diagnostics(MagicMock(), entry)

    diag = asyncio.run(_run())
    assert len(diag["devices"]) >= 1
    for device in diag["devices"]:
        assert device["deviceID"] == "**REDACTED**"


def test_to_redact_contains_api_key():
    assert "api_key" in TO_REDACT
    assert "myID" in TO_REDACT
    assert "deviceID" in TO_REDACT
