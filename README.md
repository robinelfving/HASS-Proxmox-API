# HASS Proxmox API

En Home Assistant-integration för att övervaka Proxmox-noder via API.  
Skapar en **enhet per nod** med tre sensorer: CPU, Memory och Uptime.

---

## Funktioner

- Enhet per Proxmox-nod
- Tre sensorer per nod:
  - CPU (%)
  - Memory (%)
  - Uptime (dagar)
- Case-insensitive identifier, men display-name behålls som användaren skrev
- API-klient separerad för enklare underhåll

---

## Installation via HACS

1. Kopiera mappen `hass_proxmox_api` till `custom_components/` i din Home Assistant installation.
2. Starta om Home Assistant.
3. Gå till **Inställningar → Integrationer → Lägg till Integration → HASS Proxmox API**.
4. Fyll i:
   - Host (eller IP)
   - Token ID
   - Token Secret
   - (Valfritt) IP-adress
   - (Valfritt) Verify SSL

---

## Config Flow

1. Home Assistant kommer att validera anslutningen mot Proxmox API med det angivna tokenet.
2. Om anslutningen lyckas skapas en config entry.
3. Sensorn hämtar automatiskt alla noder som du har listat i `nodes` (i config entry).

Exempel på config entry:
```yaml
host: pve01.example.com
token_id: "hass-api-token"
token_secret: "hemligt"
verify_ssl: true
nodes:
  - PVE01
  - PVE02
