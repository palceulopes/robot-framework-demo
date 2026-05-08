# 📋 Índice de Arquivos - Automotive Test Framework

## 📁 Estrutura Completa do Projeto

```
robot-framework/
│
├── 📚 DOCUMENTAÇÃO
│   ├── README.md ........................... Documentação completa (comece aqui!)
│   ├── QUICKSTART.md ....................... Guia de 5 passos para começar
│   ├── TECHNICAL_DOCUMENTATION.md ......... Arquitetura, padrões, extensibilidade
│   ├── CI_CD_SETUP.md ...................... Integração contínua (GitHub, Jenkins, GitLab)
│   ├── COMPLETION_CHECKLIST.md ............ Checklist de conclusão
│   └── INDEX.md (este arquivo) ........... Índice de navegação
│
├── 📖 INÍCIO RÁPIDO
│   ├── setup_project.py ................... Verificação automática de setup
│   ├── quickstart.py ...................... Menu interativo
│   ├── run.bat ............................ Batch helper para Windows
│   ├── examples.py ........................ 6 exemplos de uso
│   └── Makefile ........................... Targets para automação
│
├── 🔧 CONFIGURAÇÃO
│   ├── pyproject.toml ..................... Dependências e metadata
│   ├── robot.yaml ......................... Configuração Robot Framework
│   └── .gitignore ......................... Git ignore rules
│
├── 📦 BIBLIOTECAS PYTHON (libraries/)
│   ├── __init__.py ........................ Package initialization
│   └── automotive_lib.py .................. ⭐ CORE
│       ├── AdbMock (200 linhas) ........... Simula Android Debug Bridge
│       ├── CanBusManager (400 linhas) .... Gerencia barramento CAN
│       ├── SpeedSignal .................... Classe de dados para sinais
│       └── AutomotiveLibrary .............. Integração Robot Framework
│
├── 🎯 CONFIGURAÇÃO (variables/)
│   ├── __init__.py ........................ Package initialization
│   └── config.py ......................... ⭐ Variáveis globais
│       ├── DBC_PATH ....................... Caminho para arquivo DBC
│       ├── DEFAULT_DEVICE_ID ............. ID do dispositivo virtual
│       ├── CAN_CHANNEL .................... vcan0 (canal virtual)
│       ├── MAX_SPEED_THRESHOLD ........... 120 km/h
│       ├── CLUSTER_VERSION ............... 1.2.3
│       └── INFOTAINMENT_VERSION .......... 2.1.0
│
├── 🎨 KEYWORDS ROBOT (resources/)
│   ├── vehicle_keywords.resource ......... ⭐ Keywords de alto nível (10+)
│   │   ├── Initialize System Mocks
│   │   ├── Validate Software Version
│   │   ├── Inject Speed Signal
│   │   ├── Simulate Gradual Speed Increase
│   │   ├── Validate High Speed Alert Triggered
│   │   ├── Get System Status Report
│   │   ├── Verify CAN Message Available
│   │   └── Cleanup System Resources
│   │
│   └── vehicle_signals.dbc ............... ⭐ Banco de dados CAN
│       ├── WheelSpeed (ID: 100)
│       │   ├── Speed [0|16] - Velocidade em km/h
│       │   ├── WheelSpeedFL [16|16] - Roda FL
│       │   ├── WheelSpeedFR [32|16] - Roda FR
│       │   └── WheelSpeedRL [48|16] - Roda RL
│       │
│       ├── ClusterAlert (ID: 101)
│       │   ├── AlertType [0|8]
│       │   ├── AlertActive [8|1]
│       │   └── AlertPriority [9|3]
│       │
│       └── SystemStatus (ID: 102)
│           ├── SystemReady [0|1]
│           ├── SoftwareVersion [8|24]
│           └── DiagnosticCode [32|16]
│
├── 🧪 TESTES (tests/)
│   ├── smoke_tests.robot ................. ⭐ 4 testes smoke (COMECE AQUI!)
│   │   ├── Verify High Speed Behavior ... Injeta 120 km/h e valida
│   │   ├── Verify Speed Simulation Profile
│   │   ├── Verify Device Properties
│   │   └── Verify System Status Report
│   │
│   └── integration_tests.robot ........... ⭐ 5 testes de integração
│       ├── Complete Speed Profile Test
│       ├── System Diagnostics Test
│       ├── Multiple Speed Threshold Test
│       ├── Stress Test: Rapid Speed Changes
│       └── Signal Injection Sequence Test
│
└── 📊 RESULTADOS (criada automaticamente)
    └── results/ .......................... Relatórios HTML após testes
        ├── report.html ................... Relatório principal
        ├── log.html ...................... Logs detalhados
        └── output.xml .................... Dados estruturados
```

---

## 🚀 Por Onde Começar?

### 1️⃣ Primeira Vez? (15 minutos)
```
1. Ler: QUICKSTART.md
2. Executar: python setup_project.py
3. Testar: robot tests/smoke_tests.robot
4. Ver: results/report.html no navegador
```

### 2️⃣ Entender a Arquitetura? (30 minutos)
```
1. Ler: README.md (estrutura geral)
2. Ler: TECHNICAL_DOCUMENTATION.md (padrões)
3. Ver: examples.py (python examples.py)
4. Explorar: libraries/automotive_lib.py (código)
```

### 3️⃣ Adicionar Seus Testes? (1 hora)
```
1. Criar novo arquivo em tests/
2. Importar resources/vehicle_keywords.resource
3. Escrever Test Case
4. Executar: robot tests/seu_arquivo.robot
5. Ver relatório
```

### 4️⃣ Integrar com CI/CD? (2 horas)
```
1. Ler: CI_CD_SETUP.md
2. Escolher: GitHub Actions / Jenkins / GitLab
3. Copiar exemplo
4. Ajustar para seu projeto
5. Testar no pipeline
```

---

## 📖 Guias por Tópico

### 🎯 Testes
- **Smoke Tests**: `tests/smoke_tests.robot` (Testes rápidos e essenciais)
- **Integration Tests**: `tests/integration_tests.robot` (Testes complexos)
- **Executar**: `robot tests/`

### 🔌 Hardware
- **ADB (Android)**: `libraries/automotive_lib.py` → `AdbMock` (linhas 50-150)
- **CAN Bus**: `libraries/automotive_lib.py` → `CanBusManager` (linhas 175-400)
- **Database CAN**: `resources/vehicle_signals.dbc`

### 🎨 Keywords
- **Disponíveis**: `resources/vehicle_keywords.resource`
- **Usar em testes**: `tests/smoke_tests.robot` (exemplos)
- **Criar novas**: Adicionar em `vehicle_keywords.resource`

### 🔧 Configuração
- **Variáveis**: `variables/config.py`
- **Path DBC**: `config.py` linha 6
- **Threshold**: `config.py` linha 13

### 📚 Documentação
- **Rápido**: `QUICKSTART.md` (5 min)
- **Completo**: `README.md` (15 min)
- **Técnico**: `TECHNICAL_DOCUMENTATION.md` (30 min)
- **CI/CD**: `CI_CD_SETUP.md` (20 min)

### 🚀 Setup
- **Verificar**: `python setup_project.py`
- **Menu**: `python quickstart.py`
- **Batch (Windows)**: `run.bat` ou `run.bat test`

---

## 💡 Tarefas Comuns

### Adicionar Novo Sinal CAN
1. Editar: `resources/vehicle_signals.dbc`
2. Adicionar linha BO_ e SG_
3. Referenciar em: `libraries/automotive_lib.py`
4. Criar keyword em: `resources/vehicle_keywords.resource`
5. Testar em: `tests/`

### Criar Novo Teste
1. Editar: `tests/smoke_tests.robot` ou criar novo arquivo
2. Copiar padrão de outro teste
3. Usar keywords de: `resources/vehicle_keywords.resource`
4. Executar: `robot tests/seu_teste.robot`

### Estender para Hardware Real
1. Criar: `libraries/automotive_lib_real.py`
2. Herdar de: `AdbMock` → implementar com real ADB
3. Herdar de: `CanBusManager` → usar interface="can"
4. Testar com hardware real

### Integrar com CI/CD
1. Ler: `CI_CD_SETUP.md`
2. Escolher plataforma: GitHub / Jenkins / GitLab
3. Copiar template
4. Ajustar para seu projeto

---

## 📊 Estatísticas do Projeto

| Métrica | Valor |
|---------|-------|
| **Arquivos Criados** | 21 |
| **Linhas de Código Python** | ~800 |
| **Linhas de Testes Robot** | ~300 |
| **Linhas de Documentação** | ~1500 |
| **Keywords Robot** | 10+ |
| **Testes Inclusos** | 9 |
| **Classes Python** | 4 |
| **Mensagens CAN** | 3 |
| **Sinais CAN** | 10+ |

---

## 🎓 Conceitos Chave

| Conceito | Localização | Explicação |
|----------|-------------|-----------|
| **Mock** | `AdbMock` | Simula hardware sem equipamento real |
| **CAN Bus** | `CanBusManager` | Protocolo automotivo de comunicação |
| **DBC** | `vehicle_signals.dbc` | Descrição de banco de dados CAN |
| **Keywords** | `vehicle_keywords.resource` | Palavras-chave de alto nível Robot |
| **Setup** | `Suite Setup` | Inicialização de teste |
| **Teardown** | `Suite Teardown` | Limpeza após testes |
| **Tags** | `[Tags]` | Categorização de testes |

---

## ✨ Arquivos Essenciais (Comece Por Estes)

| Ordem | Arquivo | Ação |
|-------|---------|------|
| 1️⃣ | `QUICKSTART.md` | Ler (5 min) |
| 2️⃣ | `setup_project.py` | Executar (2 min) |
| 3️⃣ | `tests/smoke_tests.robot` | Explorar |
| 4️⃣ | `robot tests/` | Executar |
| 5️⃣ | `results/report.html` | Visualizar |
| 6️⃣ | `README.md` | Ler (15 min) |
| 7️⃣ | `libraries/automotive_lib.py` | Estudar |
| 8️⃣ | `examples.py` | Executar |

---

## 🆘 Quick Troubleshooting

| Erro | Solução |
|------|---------|
| "Module not found" | Ler `QUICKSTART.md` seção Setup |
| "DBC not found" | Verificar `config.py` linha 6 |
| "Robot not found" | `uv pip install robotframework` |
| Tests não rodam | `python setup_project.py` |

---

## 📞 Recursos Rápidos

```bash
# Verificar setup
python setup_project.py

# Rodar todos os testes
robot tests/

# Testar específico
robot -t "Verify High Speed Behavior" tests/smoke_tests.robot

# Ver exemplos
python examples.py

# Menu interativo
python quickstart.py

# Abrir relatório
start results\report.html  # Windows
open results/report.html   # macOS
xdg-open results/report.html  # Linux
```

---

## 🎉 Parabéns!

Você tem um framework completo, profissional e pronto para usar!

**Próximo passo**: Execute `robot tests/` e veja seus testes passarem! 🚀

---

**Documentação v1.0 - Automotive Test Framework**  
**Python 3.12 + Robot Framework 7.0+**  
**Status: PRONTO PARA PRODUÇÃO** ✅
