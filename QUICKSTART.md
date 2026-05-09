# 🚀 Quickstart (demo-ready)

O objetivo aqui é ter um caminho **curto e confiável** para a sessão com screen share: subir 2 processos (REST + MQTT) e rodar um suite Robot que valida os dois.

## 1) Instalar dependências (com `uv`)

```bash
uv sync --extra automotive
```

## 2) Rodar a demo (REST + MQTT + Listener)

```bash
uv run robot --listener libraries.automotive_listener tests/network_stack.robot
```

O suite `tests/network_stack.robot` sobe:
- `mock_servers/ecu_rest_server.py` (Flask) em `http://127.0.0.1:8765`
- `mock_servers/mqtt_broker_helper.py` (aMQTT) em `127.0.0.1:1883`

E valida conectividade + payloads via:
- `resources/rest_ecu_keywords.resource`
- `resources/mqtt_keywords.resource`

## 3) Onde mexer quando ele pedir mudança ao vivo

- **Mudança de host/port/URL**: `variables/config.py` (ex.: `ECU_BASE_URL`, `MQTT_BROKER_HOST`)
- **Mudança de contrato de API (ex.: campo JSON)**: `libraries/rest_ecu_api.py` ou `mock_servers/ecu_rest_server.py`
- **Mudança de tópicos MQTT / payload**: `libraries/mqtt_vehicle_network.py` ou `resources/mqtt_keywords.resource`

## Bonus

O repo também inclui CAN/DBC em `resources/vehicle_signals.dbc` e keywords em `resources/vehicle_keywords.resource`, mas isso não é necessário para o caminho crítico da demo.
