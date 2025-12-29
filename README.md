# HASS Proxmox API

A Home Assistant integration for monitoring Proxmox nodes via the API.  
Creates **one device per node** with three sensors: CPU, Memory, and Uptime.

---

## Features

- One device per Proxmox node
- Three sensors per node:
  - CPU (%)
  - Memory (%)
  - Uptime (days)
- Case-insensitive identifiers, while the display name is preserved as entered by the user
- Separate API client for easier maintenance

---

## Installation via HACS

1. Copy the `hass_proxmox_api` folder to `custom_components/` in your Home Assistant installation.
2. Restart Home Assistant.
3. Go to **Settings → Integrations → Add Integration → HASS Proxmox API**.
4. Enter:
   - Host (or IP)
   - Token ID
   - Token Secret
   - (Optional) IP address
   - (Optional) Verify SSL

---

## Config Flow

1. Home Assistant will validate the connection to the Proxmox API using the provided token.
2. If the connection is successful, a config entry is created.
3. The sensors automatically fetch all nodes listed in `nodes` (in the config entry).

Example config entry:

```yaml
host: pve01.example.com
token_id: "hass-api-token"
token_secret: "secret"
verify_ssl: true
nodes:
  - PVE01
  - PVE02
