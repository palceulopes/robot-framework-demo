# Documentação Técnica (curated)

Este documento foca no **caminho crítico da demo** (REST + MQTT + Listener) e explica onde fazer mudanças rápidas (live-coding).

## Arquitetura (caminho crítico da demo)

```
RobotTests (network_stack.robot)
  ├─ uses Resources (rest_ecu_keywords.resource, mqtt_keywords.resource)
  ├─ loads Variables (variables/config.py)
  ├─ starts Processes:
  │    ├─ FlaskMockEcu (mock_servers/ecu_rest_server.py)  -> HTTP/REST
  │    └─ MqttBroker (mock_servers/mqtt_broker_helper.py) -> MQTT pub/sub
  └─ drives Libraries (Python):
       ├─ libraries/rest_ecu_api.py
       ├─ libraries/mqtt_vehicle_network.py
       └─ libraries/automotive_listener.py (metrics)
```

## “Microservices” no contexto do repo

- O **Flask mock ECU** é um processo com contrato HTTP (`/api/health`, `/api/signals/...`).
- O **broker MQTT** é outro processo (infra pub/sub).
- Os testes Robot são o **cliente** (com libraries Python finas), exercitando os contratos.

Isso é suficiente para uma conversa de “everyday work”: subir serviços, rodar testes, lidar com falhas, alterar contrato/config.

## Componentes principais (demo)

### 1) `variables/config.py` (config central)

Onde ficam host/port/base URL. Se o Vitor pedir para mudar endpoint/porta, é um dos primeiros lugares.

### 2) `mock_servers/ecu_rest_server.py` (mock ECU)

Servidor Flask “standalone” com estado em memória. Útil para simular mudanças de contrato e cenários de erro.

### 3) `libraries/rest_ecu_api.py` (client REST)

Client com retry e logging. É o lado “técnico” em Python (Robot chama keywords, library faz HTTP).

### 4) `libraries/mqtt_vehicle_network.py` + `mock_servers/mqtt_broker_helper.py`

Pub/sub para tópicos de sensores/alertas. Bom para discutir eventual consistency, timeouts e testes resilientes.

### 5) `libraries/automotive_listener.py`

Gera métricas (JSON/CSV) para além do report padrão do Robot — história boa de observabilidade.

## Bonus (automotivo / CAN)

O CAN/DBC continua disponível (keywords em `resources/vehicle_keywords.resource`, DBC em `resources/vehicle_signals.dbc`), mas não é necessário para o caminho crítico.

### 1. AdbMock - Simulação de Dispositivo

**Responsabilidade**: Simular comandos ADB sem hardware real

**Propriedades Simuladas**:
```python
{
    "ro.build.version.release": "13.0",
    "ro.product.model": "VirtualCluster",
    "ro.serialno": "test_device_001",
    # ... mais propriedades
}
```

**Extensão para Hardware Real**:
```python
from adb_shell.adb_device import AdbDeviceTcp

class AdbReal(AdbMock):
    def __init__(self, device_id: str, host: str = "localhost"):
        self.device = AdbDeviceTcp(host=host)
        self.device_id = device_id
    
    def get_property(self, property_name: str) -> str:
        return self.device.shell(f"getprop {property_name}").strip()
```

### 2. CanBusManager - Gerenciador CAN

**Responsabilidade**: Carregar DBC, injetar sinais e gerenciar barramento CAN

**Fluxo**:
1. Valida arquivo DBC
2. Carrega database com cantools
3. Inicializa interface virtual (ou real)
4. Permite envio de sinais

**Métodos Principais**:
```python
# Injetar velocidade
manager.inject_speed_signal(120)

# Enviar sinal genérico
manager.send_signal("WheelSpeed", "Speed", 100)

# Listar mensagens
messages = manager.get_message_names()
```

**Tratamento de Erros**:
- Se cantools não está instalado: RuntimeError
- Se DBC inválido: RuntimeError
- Se interface CAN falha: Mock fallback
- Todos os erros são logados

### 3. DBC (vehicle_signals.dbc)

**Formato**: CAN Database in ASCII format

**Mensagens**:
```
WheelSpeed (ID: 0x64)
├── Speed [0|16] - Velocidade em km/h
├── WheelSpeedFL [16|16] - Roda frontal esquerda
├── WheelSpeedFR [32|16] - Roda frontal direita
└── WheelSpeedRL [48|16] - Roda traseira esquerda

ClusterAlert (ID: 0x65)
├── AlertType [0|8] - Tipo de alerta
├── AlertActive [8|1] - Alerta ativo?
└── AlertPriority [9|3] - Prioridade

SystemStatus (ID: 0x66)
├── SystemReady [0|1] - Sistema pronto?
├── SoftwareVersion [8|24] - Versão do software
└── DiagnosticCode [32|16] - Código de diagnóstico
```

**Adicionar Nova Mensagem**:
```dbc
BO_ <ID> <Name>: <Size> <Transmitter>
 SG_ <SignalName> : <StartBit>|<BitLength>@<ByteOrder><Sign> (<Scale>,<Offset>) [<Min>|<Max>] "<Unit>" <Receivers>
```

## Padrões de Design Implementados

### 1. Singleton Pattern (para Hardware Real)
```python
class CanBusManager:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### 2. Factory Pattern (para seleção de interface)
```python
def create_can_manager(interface_type: str, **kwargs):
    if interface_type == "virtual":
        return CanBusManagerVirtual(**kwargs)
    elif interface_type == "real":
        return CanBusManagerReal(**kwargs)
```

### 3. Mock Pattern (usando unittest.mock)
```python
adb = AdbMock()  # Implementação de teste
# Fácil trocar por:
# from real_adb import AdbReal
# adb = AdbReal()
```

## Logging Estruturado

**Configuração Automática**:
```python
logger = logging.getLogger(__name__)
# DEBUG: Info de desenvolvimento
# INFO: Operações normais
# ERROR: Problemas que afetam testes
```

**Exemplo**:
```
2024-05-08 10:30:45 - automotive_lib.AdbMock - DEBUG - getprop ro.product.model => VirtualCluster
2024-05-08 10:30:46 - automotive_lib.CanBusManager - INFO - CAN bus initialized on vcan0
2024-05-08 10:30:47 - automotive_lib.CanBusManager - DEBUG - Signal sent: WheelSpeed.Speed = 120
```

## Exemplo: Criar Novo Teste

### 1. Adicionar Keyword em `vehicle_keywords.resource`

```robot
Check Maintenance Alert
    [Documentation]    Verifica alerta de manutenção
    [Arguments]    ${alert_type}=2    ${expected}=true
    [Tags]    alert    maintenance
    [Return]    ${result}
    
    Log    Verificando alerta de manutenção...
    # Implementar lógica
    [Return]    true
```

### 2. Usar em Teste

```robot
*** Test Cases ***
Verify Maintenance Alert System
    [Tags]    critical
    
    Initialize System Mocks
    ${alert_result}=    Check Maintenance Alert    alert_type=2
    Should Be True    ${alert_result}
```

## Exemplo: Integrar Hardware Real

### 1. Criar classe para hardware real

```python
# libraries/automotive_lib_real.py
from automotive_lib import CanBusManager as CanBusBase

class CanBusManagerReal(CanBusBase):
    def __init__(self, dbc_path: str, channel: str = "can0"):
        super().__init__(dbc_path, channel, interface="can")
        self.logger.info("Real CAN bus initialized")
```

### 2. Usar em testes

```robot
*** Settings ***
Library    libraries.automotive_lib_real    interface=can

*** Test Cases ***
Real Hardware Test
    Initialize System Mocks
    # Teste com hardware real...
```

## Boas Práticas de Teste

### ✅ DOs:

1. **Use Keywords de Alto Nível**
```robot
# ✅ BOM
Inject Speed Signal    120
Validate High Speed Alert Triggered

# ❌ EVITAR
${result}=    Inject Speed Kmh    120
```

2. **Implemente Teardown Apropriado**
```robot
Suite Teardown    Cleanup System Resources
```

3. **Use Tags Apropriadas**
```robot
[Tags]    smoke    critical    speed_validation
```

4. **Documente Testes**
```robot
[Documentation]    Testa resposta do sistema a velocidades altas.
...                Injeta 120 km/h e valida alerta.
```

### ❌ DON'Ts:

1. **Não misture Python e Robot**
```robot
# ❌ EVITAR
${result}=    Evaluate    some_python_code()

# ✅ BOM
${result}=    Get System Status Report
```

2. **Não use valores hardcoded**
```robot
# ❌ EVITAR
Inject Speed Signal    120

# ✅ BOM
Inject Speed Signal    ${MAX_SPEED_THRESHOLD}
```

3. **Não ignore erros**
```robot
# ❌ EVITAR
Inject Speed Signal    120    # sem verificação

# ✅ BOM
${success}=    Inject Speed Signal    120
Should Be True    ${success}
```

## Configuração de Ambiente

### Requisitos Mínimos:
- Python 3.12+
- Robot Framework 7.0+
- cantools 4.0+
- python-can 4.0+

### Instalação com uv:
```bash
uv venv .venv
uv pip install robotframework cantools python-can pytest
```

### Variáveis de Ambiente:
```bash
# Windows
set PYTHONPATH=%PYTHONPATH%;c:\src\robot-framework

# Linux/macOS
export PYTHONPATH=$PYTHONPATH:/path/to/robot-framework
```

## Troubleshooting

### Problema: "DBC file not found"
**Solução**: Verificar caminho relativo em `config.py`

### Problema: "cantools is not installed"
**Solução**: `uv pip install cantools`

### Problema: "Failed to initialize real CAN bus"
**Solução**: Use interface "virtual" para testes sem hardware

## Roadmap Futuro

- [ ] Integração com CAN real (SocketCAN)
- [ ] Simulação de falhas de hardware
- [ ] Dashboard com resultados em tempo real
- [ ] Integração com CI/CD (GitHub Actions, Jenkins)
- [ ] Cobertura de código automática
- [ ] Suporte a múltiplos ECUs

---

**Documentação Técnica v1.0 - Framework Automotivo com Robot Framework**
