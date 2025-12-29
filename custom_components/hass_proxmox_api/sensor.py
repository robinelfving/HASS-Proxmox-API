from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

# Sensorer för noder
NODE_SENSOR_TYPES = [
    ("cpu", "CPU", "mdi:cpu-64-bit", "%"),
    ("memory", "RAM", "mdi:memory", "%"),
    ("uptime", "Uptime", "mdi:clock-outline", "d"),
    ("pveversion", "PVE Version", "mdi:new-box", None)
]

# Sensorer för VMs
VM_SENSOR_TYPES = [
    ("cpu", "CPU", "mdi:cpu-64-bit", "%"),
    ("memory", "RAM", "mdi:memory", "%"),
    ("uptime", "Uptime", "mdi:clock-outline", "d"),
    ("status", "Status", "mdi:server-network", None),
]

async def async_setup_entry(hass, entry, async_add_entities):
    """Registrerar både nod- och VM-sensorer."""
    
    entities = []

    # --- NOD-SENSORER ---
    node_coordinator = hass.data[DOMAIN][entry.entry_id]["node"]
    for node in node_coordinator.nodes_config:
        node_name_api = node["node"]
        display_name = node["display_name"]

        for key, label, icon, unit in NODE_SENSOR_TYPES:
            entities.append(
                ProxmoxNodeSensor(node_coordinator, node_name_api, display_name, key, label, icon, unit)
            )

    # --- VM-SENSORER ---
    qemu_coordinator = hass.data[DOMAIN][entry.entry_id]["qemu"]
    for vm in qemu_coordinator.data:
        vmid = vm["vmid"]
        display_name = vm.get("name", f"VM {vmid}")
        for key, label, icon, unit in VM_SENSOR_TYPES:
            entities.append(
                ProxmoxVMSensor(qemu_coordinator, vmid, display_name, key, label, icon, unit)
            )

    async_add_entities(entities)


class ProxmoxNodeSensor(CoordinatorEntity, SensorEntity):
    """Sensorer för en Proxmox-nod."""
    def __init__(self, coordinator, node_name_api, display_name, key, label, icon, unit):
        super().__init__(coordinator)
        self.node_name_api = node_name_api
        self.node_name_display = display_name
        self.key = key
        self._attr_name = f"{display_name} {label}"
        self._attr_unique_id = f"{node_name_api}_{key}"
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
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
            self._attr_state_class = "measurement"
            return round(cpu * 100, 1)

        if self.key == "memory":
            memory = data.get("memory", {})
            used = memory.get("used")
            total = memory.get("total")
            self._attr_state_class = "measurement"
            if used is None or total in (None, 0):
                return None
            return round((used / total) * 100, 1)

        if self.key == "uptime":
            uptime = data.get("uptime")
            if uptime is None:
                return None
            return round(uptime / 86400, 0)  # sekunder → dagar

        if self.key == "pveversion":
            self._attr_entity_category = "diagnostic"
            return data.get("pveversion")

        return None


class ProxmoxVMSensor(CoordinatorEntity, SensorEntity):
    """Sensorer för en Proxmox-VM."""
    def __init__(self, coordinator, vmid, display_name, key, label, icon, unit):
        super().__init__(coordinator)
        self.vmid = vmid
        self.display_name = display_name
        self.key = key
        self._attr_name = f"{display_name} {label}"
        self._attr_unique_id = f"vm_{vmid}_{key}"
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"vm_{vmid}")},
            name=f"Proxmox VM {display_name}",
            manufacturer="Proxmox",
            model="QEMU/KVM VM",
        )

    def _vm_data(self):
        if not self.coordinator.data:
            return {}
        for vm in self.coordinator.data:
            if vm.get("vmid") == self.vmid:
                return vm
        return {}

    @property
    def native_value(self):
        data = self._vm_data()
        if not data:
            return None

        if self.key == "cpu":
            self._attr_state_class = "measurement"
            return round(data.get("cpu", 0) * 100, 1)

        if self.key == "memory":
            mem = data.get("memory", {})
            used = mem.get("used")
            total = mem.get("total")
            self._attr_state_class = "measurement"
            if used is None or total in (None, 0):
                return None
            return round((used / total) * 100, 1)

        if self.key == "uptime":
            uptime = data.get("uptime")
            if uptime is None:
                return None
            return round(uptime / 86400, 0)

        if self.key == "status":
            return data.get("status")

        return None
