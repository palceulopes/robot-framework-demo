# Automotive Test Framework

Framework de testes automotivos com **Robot Framework** e **Python 3.12**, simulando validação de componentes veiculares como Cluster (painel de instrumentos) e Infotainment através de mocks de hardware (CAN e ADB).

## 📋 Estrutura do Projeto

```
robot-framework/
├── libraries/
│   ├── __init__.py
│   └── automotive_lib.py          # Classes AdbMock e CanBusManager
├── resources/
│   ├── vehicle_keywords.resource   # Keywords de alto nível
│   └── vehicle_signals.dbc         # Configuração CAN com mensagens
├── tests/
│   └── smoke_tests.robot           # Suite de testes
├── variables/
│   ├── __init__.py
│   └── config.py                   # Variáveis globais
├── pyproject.toml                  # Configuração do projeto
└── README.md
```

## 🚀 Início Rápido

### 1. Configurar Ambiente Virtual com `uv`

```bash
# Criar e ativar ambiente virtual
uv venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Instalar dependências
uv pip install -r pyproject.toml
```

### 2. Executar Testes

```bash
# Executar todos os testes
robot tests/

# Executar teste específico
robot -t "Verify High Speed Behavior" tests/smoke_tests.robot

# Com reportes detalhados
robot --outputdir ./results tests/
```

## 📦 Dependências

- **robotframework**: Framework de testes
- **cantools**: Manipulação de arquivos DBC
- **python-can**: Comunicação CAN virtual
- **unittest.mock**: Mocks internos do Python

### Instalar com uv:

```bash
uv pip install robotframework cantools python-can
```

## 🏗️ Componentes Principais

### `automotive_lib.py`

#### Classe `AdbMock`
Simula comandos ADB (Android Debug Bridge) para comunicação com dispositivos:

```python
adb = AdbMock(device_id="test_device_001")
version = adb.get_property("ro.build.version.release")
output = adb.shell_command("pm list packages")
```

**Métodos:**
- `get_property(property_name)` - Retorna propriedade do dispositivo
- `shell_command(command)` - Executa comando shell simulado
- `set_property(property_name, value)` - Define propriedade

#### Classe `CanBusManager`
Gerencia comunicação CAN virtual usando DBC:

```python
can_mgr = CanBusManager(
    dbc_path="resources/vehicle_signals.dbc",
    channel="vcan0",
    interface="virtual"
)

# Injetar sinal de velocidade
can_mgr.inject_speed_signal(120)  # 120 km/h

# Enviar sinal customizado
can_mgr.send_signal("WheelSpeed", "Speed", 100)

# Listar mensagens
messages = can_mgr.get_message_names()
signals = can_mgr.get_message_signals("WheelSpeed")
```

**Métodos:**
- `inject_speed_signal(speed_km_h)` - Injeta sinal de velocidade
- `send_signal(message_name, signal_name, value)` - Envia sinal genérico
- `get_message_names()` - Lista mensagens disponíveis
- `get_message_signals(message_name)` - Lista sinais da mensagem
- `close()` - Fecha conexão CAN

#### Classe `AutomotiveLibrary`
Biblioteca integrada para Robot Framework:

```robot
*** Settings ***
Library    libraries.automotive_lib

*** Test Cases ***
Test Speed Alert
    ${version}=    Get Device Property    ro.build.version.release
    ${result}=    Inject Speed Kmh    120
```

### `vehicle_keywords.resource`

Keywords de alto nível para testes:

#### Initialize System Mocks
Inicializa todos os mocks do sistema (ADB e CAN).

```robot
Initialize System Mocks
```

#### Validate Software Version
Valida versão de software contra versão esperada.

```robot
${version}=    Validate Software Version    expected_version=1.2.3
```

#### Inject Speed Signal
Injeta sinal de velocidade no barramento CAN.

```robot
Inject Speed Signal    120
```

#### Simulate Gradual Speed Increase
Simula aumento gradual de velocidade para validar comportamento.

```robot
Simulate Gradual Speed Increase    start_speed=0    end_speed=150    step=10
```

#### Get System Status Report
Gera relatório com informações do dispositivo.

```robot
${status}=    Get System Status Report
```

### `vehicle_signals.dbc`

Configuração CAN com 3 mensagens principais:

| Mensagem | ID | Sinais |
|----------|-----|--------|
| **WheelSpeed** | 100 | Speed (km/h), WheelSpeedFL, WheelSpeedFR, WheelSpeedRL |
| **ClusterAlert** | 101 | AlertType, AlertActive, AlertPriority |
| **SystemStatus** | 102 | SystemReady, SoftwareVersion, DiagnosticCode |

### `config.py`

Variáveis globais do projeto:

```python
DBC_PATH = "resources/vehicle_signals.dbc"
DEFAULT_DEVICE_ID = "test_device_001"
CAN_CHANNEL = "vcan0"
MAX_SPEED_THRESHOLD = 120  # km/h
CLUSTER_VERSION = "1.2.3"
INFOTAINMENT_VERSION = "2.1.0"
```

## 📝 Exemplo de Teste

```robot
*** Settings ***
Resource    resources/vehicle_keywords.resource

Suite Setup    Initialize System Mocks

*** Test Cases ***
Verify High Speed Behavior
    # Setup
    Validate Software Version    expected_version=1.2.3
    Verify CAN Message Available    WheelSpeed
    
    # Execute
    Inject Speed Signal    120
    
    # Validate
    Validate High Speed Alert Triggered    threshold_kmh=120
```

## 🔧 Extensibilidade para Hardware Real

### Para integração futura com hardware real:

1. **Substituir `AdbMock` por classe real:**
```python
class AdbReal(AdbMock):
    """Real ADB implementation"""
    def __init__(self, device_id):
        self.device = DeviceManager.get_device(device_id)
```

2. **Configurar CAN interface real:**
```python
CanBusManager(
    dbc_path="...",
    interface="can",  # ao invés de "virtual"
    channel="can0"
)
```

3. **Usar fixture de factory para seleção:**
```robot
*** Settings ***
Library    libraries.automotive_lib    interface=can
```

## 🐛 Logging

Logging configurado automaticamente com nível DEBUG:

```python
import logging
logger = logging.getLogger(__name__)
logger.debug("Mensagem de debug")
logger.error("Mensagem de erro")
```

## ✅ Suite de Testes Disponíveis

Executar com: `robot tests/smoke_tests.robot`

### Testes Inclusos:
1. **Verify High Speed Behavior** - Valida resposta do sistema a 120 km/h
2. **Verify Speed Simulation Profile** - Simula perfil de velocidade de 0 a 140 km/h
3. **Verify Device Properties** - Valida propriedades do dispositivo
4. **Verify System Status Report** - Gera relatório de diagnóstico

## 📖 Boas Práticas Implementadas

✅ Type hints em Python 3.12  
✅ Docstrings completas (Google style)  
✅ Tratamento de erros robusto  
✅ Logging estruturado  
✅ Separação clara de responsabilidades  
✅ Padrão Factory para extensibilidade  
✅ Mock objects para testes sem hardware  
✅ Keywords Robot profissionais com `[Arguments]` e `[Return]`  

## 🤝 Contribuindo

1. Adicionar novos sinais ao `vehicle_signals.dbc`
2. Estender `CanBusManager` com novos tipos de mensagens
3. Criar keywords específicas em `vehicle_keywords.resource`
4. Adicionar testes em `tests/`

## 📄 Licença

MIT - Livre para uso comercial e pessoal

---

**Desenvolvido para validação de sistemas automotivos com Robot Framework 7.0+ e Python 3.12**
