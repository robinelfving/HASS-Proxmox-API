from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for node in coordinator.data:
        node_name = node["node"]

        entities.extend(
            [
                ProxmoxNodeCpuSensor(coordinator, node_name),
                ProxmoxNodeMemorySensor(coordinator, node_name),
                ProxmoxNodeUptimeSensor(coordinator, node_name),
            ]
        )

    async_add_entities(entities)


class ProxmoxNodeBaseSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, node_name):
        super().__init__(coordinator)
        self.node_name = node_name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, node_name)},
            name=f"Proxmox Node {node_name}",
            manufacturer="Proxmox",
            model="Proxmox VE Node",
        )

    def _node_data(self):
        for node in self.coordinator.data:
            if node["node"] == self.node_name:
                return node
        return {}


class ProxmoxNodeCpuSensor(ProxmoxNodeBaseSensor):
    _attr_icon = "mdi:cpu-64-bit"

    def __init__(self, coordinator, node_name):
        super().__init__(coordinator, node_name)
        self._attr_name = f"{node_name} CPU"

    @property
    def native_value(self):
        return round(self._node_data().get("cpu", 0) * 100, 1)


class ProxmoxNodeMemorySensor(ProxmoxNodeBaseSensor):
    _attr_icon = "mdi:memory"

    def __init__(self, coordinator, node_name):
        super().__init__(coordinator, node_name)
        self._attr_name = f"{node_name} Memory Usage"

    @property
    def native_value(self):
        data = self._node_data()
        if not data:
            return None
        return round((data["mem"] / data["maxmem"]) * 100, 1)


class ProxmoxNodeUptimeSensor(ProxmoxNodeBaseSensor):
    _attr_icon = "mdi:clock-outline"
    _attr_unit_of_measurement = "s"

    def __init__(self, coordinator, node_name):
        super().__init__(coordinator, node_name)
        self._attr_name = f"{node_name} Uptime"

    @property
    def native_value(self):
        return self._node_data().get("uptime")
