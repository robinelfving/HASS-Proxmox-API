from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    print("Nodes config:", coordinator.nodes_config)  # <--- lägg till detta

    # Skapa sensorer från nodkonfigurationen, inte coordinator.data
    for node in coordinator.nodes_config:
        node_name = node["node"]
        entities.extend([
            ProxmoxNodeCpuSensor(coordinator, node_name),
            ProxmoxNodeMemorySensor(coordinator, node_name),
            ProxmoxNodeUptimeSensor(coordinator, node_name),
        ])

    async_add_entities(entities)
    

class ProxmoxNodeBaseSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, node_name):
        super().__init__(coordinator)
        self.node_name_display = node_name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.node_name_display)},
            name=f"Proxmox Node {self.node_name_display}",
            manufacturer="Proxmox",
            model="Proxmox VE Node",
        )

    def _node_data(self):
        """Hämta data för noden från coordinator, returnerar tom dict om inget finns ännu."""
        for node in self.coordinator.data:
            if node["node"] == self.node_name_display:
                return node
        return {}


class ProxmoxNodeCpuSensor(ProxmoxNodeBaseSensor):
    _attr_icon = "mdi:cpu-64-bit"
    _attr_state_class = "measurement"

    def __init__(self, coordinator, node_name):
        super().__init__(coordinator, node_name)
        self._attr_name = f"{self.node_name_display} CPU"
        self._attr_unique_id = f"{self.node_name_display}_cpu"

    @property
    def native_value(self):
        data = self._node_data()
        if not data:
            return None
        return round(data.get("cpu", 0) * 100, 1)


class ProxmoxNodeMemorySensor(ProxmoxNodeBaseSensor):
    _attr_icon = "mdi:memory"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = "measurement"

    def __init__(self, coordinator, node_name):
        super().__init__(coordinator, node_name)
        self._attr_name = f"{self.node_name_display} Minne"
        self._attr_unique_id = f"{self.node_name_display}_memory"

    @property
    def native_value(self):
        data = self._node_data()
        if not data:
            return None
        mem = data.get("mem", 0)
        maxmem = data.get("maxmem", 1)
        return round((mem / maxmem) * 100, 1)


class ProxmoxNodeUptimeSensor(ProxmoxNodeBaseSensor):
    _attr_icon = "mdi:clock-outline"
    _attr_native_unit_of_measurement = "dagar"
    _attr_state_class = "measurement"

    def __init__(self, coordinator, node_name):
        super().__init__(coordinator, node_name)
        self._attr_name = f"{self.node_name_display} Uppetid"
        self._attr_unique_id = f"{self.node_name_display}_uptime"

    @property
    def native_value(self):
        data = self._node_data()
        uptime_seconds = data.get("uptime")
        if uptime_seconds is None:
            return None
        return round(uptime_seconds / 86400, 0)
