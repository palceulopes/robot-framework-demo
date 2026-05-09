# Automotive Test Framework (Robot + Python)

Framework de automação com **Robot Framework** e **Python 3.12**, com um setup de “microservices simples” para demo:

- **Mock ECU via REST (Flask)**: simula endpoints de um ECU.
- **Broker MQTT embutido (aMQTT)**: pub/sub para simular rede de veículo/sensores.
- **Client libraries em Python**: keywords Robot chamam libraries técnicas.
- **Listener customizado**: métricas além de PASS/FAIL.

O foco é mostrar **workflow real**: rodar testes, interpretar falhas e ajustar rapidamente (config/resources/libraries).

## TL;DR (comandos que funcionam no demo)

```bash
uv sync --extra automotive
uv run robot --pythonpath . --listener libraries.automotive_listener tests/network_stack.robot
```

Optional on Windows: `run.bat` only deletes `results/`, `logs/`, `.robocache/` (no `uv`)—useful before a clean rerun.

## Estrutura (visão rápida)

```
robot-framework/
├── libraries/        # lógica técnica Python (REST client, MQTT client, listener, CAN bonus)
├── mock_servers/     # processos: Flask mock ECU + helper do broker MQTT
├── resources/        # keywords reutilizáveis (Robot) para REST/MQTT/CAN
├── tests/            # suites Robot (demo principal: network_stack.robot)
└── variables/        # configuração (hosts/ports/paths)
```

## Documentação

- **Guia rápido**: `QUICKSTART.md`
- **Detalhes técnicos/arquitetura**: `TECHNICAL_DOCUMENTATION.md`

## Notas (para a sessão)

- **REST + MQTT + Listener** são o caminho crítico da demo.
- **CAN/DBC** existe como “bonus” automotivo, mas não é obrigatório para a sessão.
