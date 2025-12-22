from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

SENSOR_TYPES = [
    ("cpu", "CPU", "mdi:cpu-64-bit", "%"),
    ("memory", "Minne", "mdi:memory", "%"),
    ("uptime", "Upptid", "mdi:clock-outline", "dagar"),
]

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for node in coordinator.nodes_config:
        node_name_api = node["node"]
        display_name = node["display_name"]

        for key, label, icon, unit in SENSOR_TYPES:
            entities.append(
                ProxmoxNodeSensor(coordinator, node_name_api, display_name, key, label, icon, unit)
            )

    async_add_entities(entities)


class ProxmoxNodeSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, node_name_api, display_name, key, label, icon, unit):
        super().__init__(coordinator)
        self.node_name_api = node_name_api
        self.node_name_display = display_name
        self.key = key
        self._attr_name = f"{display_name} {label}"
        self._attr_unique_id = f"{node_name_api}_{key}"
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = "measurement"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, node_name_api)},
            name=f"Proxmox Node {display_name}",
            manufacturer="Proxmox",
            model="Proxmox VE Node",
        )

    def _node_data(self):
        if not self.coordinator.data:
            return {}
        for node in self.coordinator.data:
            if node.get("node") == self.node_name_api:
                return node
        return {}

    @property
    def native_value(self):
        data = self._node_data()
        if not data:
            return None

        if self.key == "cpu":
            cpu = data.get("cpu", 0)

            if cpu is None:
                return None
            
            return round(cpu * 100, 1)

        if self.key == "memory":
            memory = data.get("memory", {})
            used = memory.get("used")
            total = memory.get("total")

            if used is None or total in (None, 0):
                return None

            return round((used / total) * 100, 1)

        if self.key == "uptime":
            uptime = data.get("uptime")

            if uptime is None:
                return None
            
            return round(uptime / 86400, 0)  # omvandla sekunder → dagar

        return None 