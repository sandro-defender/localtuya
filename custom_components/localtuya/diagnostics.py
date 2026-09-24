"""Diagnostics support for LocalTuya."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_DEVICES
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry

from .const import CONF_LOCAL_KEY, CONF_USER_ID, DATA_CLOUD, DOMAIN

CLOUD_DEVICES = "cloud_devices"
DEVICE_CONFIG = "device_config"
DEVICE_CLOUD_INFO = "device_cloud_info"
REDACTED = "**REDACTED**"
SENSITIVE_FIELDS = {
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_LOCAL_KEY,
    CONF_USER_ID,
    "access_token",
    "refresh_token",
    "password",
    "secret",
    "token",
}

_LOGGER = logging.getLogger(__name__)


def _redact(value: Any) -> Any:
    """Remove credentials from nested diagnostic data without changing live data."""
    if isinstance(value, dict):
        return {
            key: REDACTED if key in SENSITIVE_FIELDS else _redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = dict(entry.data)
    tuya_api = hass.data[DOMAIN].get(DATA_CLOUD)
    data[CLOUD_DEVICES] = tuya_api.device_list if tuya_api else {}
    return _redact(data)


async def async_get_device_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry, device: DeviceEntry
) -> dict[str, Any]:
    """Return diagnostics for a device entry."""
    dev_id = list(device.identifiers)[0][1].split("_")[-1]
    data = {DEVICE_CONFIG: entry.data[CONF_DEVICES][dev_id]}
    tuya_api = hass.data[DOMAIN].get(DATA_CLOUD)
    if tuya_api and dev_id in tuya_api.device_list:
        data[DEVICE_CLOUD_INFO] = tuya_api.device_list[dev_id]
    return _redact(data)
