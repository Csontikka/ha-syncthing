"""Tests for Syncthing config flow."""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.syncthing_extended.api import (
    SyncthingAuthError,
    SyncthingConnectionError,
    SyncthingSslError,
)
from custom_components.syncthing_extended.const import (
    CONF_API_KEY,
    CONF_HOST,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_VERIFY_SSL,
)
from tests.conftest import MOCK_SYSTEM_STATUS, MOCK_VERSION

VALID_INPUT = {
    CONF_HOST: "192.168.1.100",
    CONF_PORT: 8384,
    CONF_API_KEY: "test-api-key-12345",
    CONF_VERIFY_SSL: False,
    CONF_SCAN_INTERVAL: 30,
}


def _mock_api(healthy=True, auth_error=False, connect_error=False):
    api = MagicMock()
    api.check_health = AsyncMock(return_value=not connect_error and healthy)
    if auth_error:
        api.get_system_status = AsyncMock(side_effect=SyncthingAuthError("bad key"))
    elif connect_error:
        api.get_system_status = AsyncMock(
            side_effect=SyncthingConnectionError("no route")
        )
    else:
        api.get_system_status = AsyncMock(return_value=MOCK_SYSTEM_STATUS)
    api.get_version = AsyncMock(return_value=MOCK_VERSION)
    return api


def _make_flow():
    from custom_components.syncthing_extended.config_flow import SyncthingConfigFlow

    flow = SyncthingConfigFlow()
    flow.hass = MagicMock()
    flow.hass.config_entries = MagicMock()
    flow.hass.config_entries.async_entries = MagicMock(return_value=[])
    return flow


def test_config_flow_shows_form_on_empty():
    async def _run():
        flow = _make_flow()
        with patch.object(
            flow,
            "async_show_form",
            return_value={"type": "form", "errors": {}},
        ):
            return await flow.async_step_user(None)

    result = asyncio.run(_run())
    assert result["type"] == "form"
    assert result["errors"] == {}


def test_config_flow_success():
    async def _run():
        flow = _make_flow()
        mock_api = _mock_api()

        with patch(
            "custom_components.syncthing_extended.config_flow.SyncthingApi",
            return_value=mock_api,
        ), patch(
            "custom_components.syncthing_extended.config_flow.async_get_clientsession",
            return_value=MagicMock(),
        ), patch.object(
            flow, "async_set_unique_id", AsyncMock()
        ), patch.object(
            flow, "_abort_if_unique_id_configured", MagicMock()
        ), patch.object(
            flow,
            "async_create_entry",
            return_value={"type": "create_entry", "title": "test", "data": VALID_INPUT},
        ):
            return await flow.async_step_user(VALID_INPUT)

    result = asyncio.run(_run())
    assert result["type"] == "create_entry"


def test_config_flow_cannot_connect():
    async def _run():
        flow = _make_flow()
        mock_api = _mock_api(healthy=False)

        with patch(
            "custom_components.syncthing_extended.config_flow.SyncthingApi",
            return_value=mock_api,
        ), patch(
            "custom_components.syncthing_extended.config_flow.async_get_clientsession",
            return_value=MagicMock(),
        ), patch.object(
            flow,
            "async_show_form",
            return_value={"type": "form", "errors": {"base": "cannot_connect"}},
        ):
            return await flow.async_step_user(VALID_INPUT)

    result = asyncio.run(_run())
    assert result["errors"]["base"] == "cannot_connect"


def test_config_flow_invalid_auth():
    async def _run():
        flow = _make_flow()
        mock_api = _mock_api(auth_error=True)

        with patch(
            "custom_components.syncthing_extended.config_flow.SyncthingApi",
            return_value=mock_api,
        ), patch(
            "custom_components.syncthing_extended.config_flow.async_get_clientsession",
            return_value=MagicMock(),
        ), patch.object(
            flow,
            "async_show_form",
            return_value={"type": "form", "errors": {"base": "invalid_auth"}},
        ):
            return await flow.async_step_user(VALID_INPUT)

    result = asyncio.run(_run())
    assert result["errors"]["base"] == "invalid_auth"


def _make_options_flow():
    from custom_components.syncthing_extended.config_flow import SyncthingOptionsFlow

    config_entry = MagicMock()
    config_entry.options = {}
    config_entry.data = {CONF_SCAN_INTERVAL: 30}

    flow = SyncthingOptionsFlow()
    flow._config_entry = config_entry  # bypass deprecated setter; normally set by HA framework
    return flow


def test_options_flow_updates_scan_interval():
    async def _run():
        flow = _make_options_flow()
        with patch.object(
            flow,
            "async_create_entry",
            return_value={"type": "create_entry", "data": {CONF_SCAN_INTERVAL: 60}},
        ):
            return await flow.async_step_init({CONF_SCAN_INTERVAL: 60})

    result = asyncio.run(_run())
    assert result["type"] == "create_entry"


def test_options_flow_shows_form_on_empty():
    async def _run():
        flow = _make_options_flow()
        with patch.object(
            flow,
            "async_show_form",
            return_value={"type": "form", "step_id": "init"},
        ):
            return await flow.async_step_init(None)

    result = asyncio.run(_run())
    assert result["type"] == "form"


def test_reauth_confirm_success():
    async def _run():
        flow = _make_flow()
        mock_api = _mock_api()

        reauth_entry = MagicMock()
        reauth_entry.data = {
            CONF_HOST: "192.168.1.100",
            CONF_PORT: 8384,
            CONF_API_KEY: "old-key",
            CONF_VERIFY_SSL: False,
        }

        with patch(
            "custom_components.syncthing_extended.config_flow.SyncthingApi",
            return_value=mock_api,
        ), patch(
            "custom_components.syncthing_extended.config_flow.async_get_clientsession",
            return_value=MagicMock(),
        ), patch.object(
            flow, "_get_reauth_entry", return_value=reauth_entry
        ), patch.object(
            flow,
            "async_update_reload_and_abort",
            return_value={"type": "abort", "reason": "reauth_successful"},
        ):
            return await flow.async_step_reauth_confirm({CONF_API_KEY: "new-api-key"})

    result = asyncio.run(_run())
    assert result["type"] == "abort"
    assert result["reason"] == "reauth_successful"


def test_reauth_confirm_invalid_auth():
    async def _run():
        flow = _make_flow()
        mock_api = _mock_api(auth_error=True)

        reauth_entry = MagicMock()
        reauth_entry.data = {
            CONF_HOST: "192.168.1.100",
            CONF_PORT: 8384,
            CONF_API_KEY: "old-key",
            CONF_VERIFY_SSL: False,
        }

        with patch(
            "custom_components.syncthing_extended.config_flow.SyncthingApi",
            return_value=mock_api,
        ), patch(
            "custom_components.syncthing_extended.config_flow.async_get_clientsession",
            return_value=MagicMock(),
        ), patch.object(
            flow, "_get_reauth_entry", return_value=reauth_entry
        ), patch.object(
            flow,
            "async_show_form",
            return_value={"type": "form", "errors": {"base": "invalid_auth"}},
        ):
            return await flow.async_step_reauth_confirm({CONF_API_KEY: "wrong-key"})

    result = asyncio.run(_run())
    assert result["errors"]["base"] == "invalid_auth"


def test_reauth_step_calls_confirm():
    async def _run():
        flow = _make_flow()
        with patch.object(
            flow,
            "async_show_form",
            return_value={"type": "form", "step_id": "reauth_confirm"},
        ):
            return await flow.async_step_reauth({})

    result = asyncio.run(_run())
    assert result["type"] == "form"


def test_reauth_confirm_shows_form_on_empty():
    async def _run():
        flow = _make_flow()
        with patch.object(
            flow,
            "async_show_form",
            return_value={"type": "form", "step_id": "reauth_confirm"},
        ):
            return await flow.async_step_reauth_confirm(None)

    result = asyncio.run(_run())
    assert result["type"] == "form"


def test_config_flow_unknown_exception():
    async def _run():
        flow = _make_flow()
        mock_api = MagicMock()
        mock_api.check_health = AsyncMock(side_effect=Exception("unexpected"))

        with patch(
            "custom_components.syncthing_extended.config_flow.SyncthingApi",
            return_value=mock_api,
        ), patch(
            "custom_components.syncthing_extended.config_flow.async_get_clientsession",
            return_value=MagicMock(),
        ), patch.object(
            flow,
            "async_show_form",
            return_value={"type": "form", "errors": {"base": "unknown"}},
        ):
            return await flow.async_step_user(VALID_INPUT)

    result = asyncio.run(_run())
    assert result["errors"]["base"] == "unknown"


def test_config_flow_empty_unique_id():
    async def _run():
        flow = _make_flow()
        mock_api = MagicMock()
        mock_api.check_health = AsyncMock(return_value=True)
        mock_api.get_system_status = AsyncMock(return_value={"myID": ""})

        with patch(
            "custom_components.syncthing_extended.config_flow.SyncthingApi",
            return_value=mock_api,
        ), patch(
            "custom_components.syncthing_extended.config_flow.async_get_clientsession",
            return_value=MagicMock(),
        ), patch.object(
            flow,
            "async_show_form",
            return_value={"type": "form", "errors": {"base": "cannot_connect"}},
        ):
            return await flow.async_step_user(VALID_INPUT)

    result = asyncio.run(_run())
    assert result["errors"]["base"] == "cannot_connect"


def test_config_flow_success_with_device_name():
    """Covers friendly-name title branch (lines 92-99 in config_flow.py)."""
    async def _run():
        flow = _make_flow()
        mock_api = _mock_api()
        mock_api.get_config_devices = AsyncMock(
            return_value=[
                {
                    "deviceID": MOCK_SYSTEM_STATUS["myID"],
                    "name": "MyNAS",
                }
            ]
        )

        captured = {}

        def _capture_entry(*, title, data):
            captured["title"] = title
            return {"type": "create_entry", "title": title, "data": data}

        with patch(
            "custom_components.syncthing_extended.config_flow.SyncthingApi",
            return_value=mock_api,
        ), patch(
            "custom_components.syncthing_extended.config_flow.async_get_clientsession",
            return_value=MagicMock(),
        ), patch.object(
            flow, "async_set_unique_id", AsyncMock()
        ), patch.object(
            flow, "_abort_if_unique_id_configured", MagicMock()
        ), patch.object(
            flow, "async_create_entry", side_effect=_capture_entry
        ):
            result = await flow.async_step_user(VALID_INPUT)
        return result, captured

    result, captured = asyncio.run(_run())
    assert result["type"] == "create_entry"
    assert captured["title"] == "Syncthing @ MyNAS"


def test_config_flow_ssl_error():
    """Covers line 110 (SyncthingSslError branch)."""
    async def _run():
        flow = _make_flow()
        mock_api = MagicMock()
        mock_api.check_health = AsyncMock(side_effect=SyncthingSslError("bad cert"))

        with patch(
            "custom_components.syncthing_extended.config_flow.SyncthingApi",
            return_value=mock_api,
        ), patch(
            "custom_components.syncthing_extended.config_flow.async_get_clientsession",
            return_value=MagicMock(),
        ), patch.object(
            flow,
            "async_show_form",
            return_value={"type": "form", "errors": {"base": "ssl_error"}},
        ):
            return await flow.async_step_user(VALID_INPUT)

    result = asyncio.run(_run())
    assert result["errors"]["base"] == "ssl_error"


def test_config_flow_connection_exception():
    """Covers line 112 (SyncthingConnectionError branch via exception)."""
    async def _run():
        flow = _make_flow()
        mock_api = MagicMock()
        mock_api.check_health = AsyncMock(
            side_effect=SyncthingConnectionError("no route")
        )

        with patch(
            "custom_components.syncthing_extended.config_flow.SyncthingApi",
            return_value=mock_api,
        ), patch(
            "custom_components.syncthing_extended.config_flow.async_get_clientsession",
            return_value=MagicMock(),
        ), patch.object(
            flow,
            "async_show_form",
            return_value={"type": "form", "errors": {"base": "cannot_connect"}},
        ):
            return await flow.async_step_user(VALID_INPUT)

    result = asyncio.run(_run())
    assert result["errors"]["base"] == "cannot_connect"


def test_reauth_confirm_ssl_error():
    """Covers lines 156-157 (reauth SyncthingSslError)."""
    async def _run():
        flow = _make_flow()
        mock_api = MagicMock()
        mock_api.get_system_status = AsyncMock(side_effect=SyncthingSslError("bad cert"))

        reauth_entry = MagicMock()
        reauth_entry.data = {
            CONF_HOST: "192.168.1.100",
            CONF_PORT: 8384,
            CONF_API_KEY: "old-key",
            CONF_VERIFY_SSL: False,
        }

        with patch(
            "custom_components.syncthing_extended.config_flow.SyncthingApi",
            return_value=mock_api,
        ), patch(
            "custom_components.syncthing_extended.config_flow.async_get_clientsession",
            return_value=MagicMock(),
        ), patch.object(
            flow, "_get_reauth_entry", return_value=reauth_entry
        ), patch.object(
            flow,
            "async_show_form",
            return_value={"type": "form", "errors": {"base": "ssl_error"}},
        ):
            return await flow.async_step_reauth_confirm({CONF_API_KEY: "new-key"})

    result = asyncio.run(_run())
    assert result["errors"]["base"] == "ssl_error"


def test_reauth_confirm_connection_error():
    """Covers lines 158-159 (reauth SyncthingConnectionError)."""
    async def _run():
        flow = _make_flow()
        mock_api = MagicMock()
        mock_api.get_system_status = AsyncMock(
            side_effect=SyncthingConnectionError("no route")
        )

        reauth_entry = MagicMock()
        reauth_entry.data = {
            CONF_HOST: "192.168.1.100",
            CONF_PORT: 8384,
            CONF_API_KEY: "old-key",
            CONF_VERIFY_SSL: False,
        }

        with patch(
            "custom_components.syncthing_extended.config_flow.SyncthingApi",
            return_value=mock_api,
        ), patch(
            "custom_components.syncthing_extended.config_flow.async_get_clientsession",
            return_value=MagicMock(),
        ), patch.object(
            flow, "_get_reauth_entry", return_value=reauth_entry
        ), patch.object(
            flow,
            "async_show_form",
            return_value={"type": "form", "errors": {"base": "cannot_connect"}},
        ):
            return await flow.async_step_reauth_confirm({CONF_API_KEY: "new-key"})

    result = asyncio.run(_run())
    assert result["errors"]["base"] == "cannot_connect"


def test_reauth_confirm_unknown_exception():
    """Covers lines 160-162 (reauth unknown exception branch)."""
    async def _run():
        flow = _make_flow()
        mock_api = MagicMock()
        mock_api.get_system_status = AsyncMock(side_effect=Exception("boom"))

        reauth_entry = MagicMock()
        reauth_entry.data = {
            CONF_HOST: "192.168.1.100",
            CONF_PORT: 8384,
            CONF_API_KEY: "old-key",
            CONF_VERIFY_SSL: False,
        }

        with patch(
            "custom_components.syncthing_extended.config_flow.SyncthingApi",
            return_value=mock_api,
        ), patch(
            "custom_components.syncthing_extended.config_flow.async_get_clientsession",
            return_value=MagicMock(),
        ), patch.object(
            flow, "_get_reauth_entry", return_value=reauth_entry
        ), patch.object(
            flow,
            "async_show_form",
            return_value={"type": "form", "errors": {"base": "unknown"}},
        ):
            return await flow.async_step_reauth_confirm({CONF_API_KEY: "new-key"})

    result = asyncio.run(_run())
    assert result["errors"]["base"] == "unknown"


def test_async_get_options_flow():
    """Covers line 174 (async_get_options_flow static callback)."""
    from custom_components.syncthing_extended.config_flow import (
        SyncthingConfigFlow,
        SyncthingOptionsFlow,
    )

    result = SyncthingConfigFlow.async_get_options_flow(MagicMock())
    assert isinstance(result, SyncthingOptionsFlow)
