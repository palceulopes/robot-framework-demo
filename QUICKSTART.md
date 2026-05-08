# 🚀 Guia de Início Rápido

## ⚡ 5 Passos para Começar

### 1️⃣ Ativar Ambiente Virtual

```bash
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### 2️⃣ Instalar Dependências

```bash
# Com uv (recomendado)
uv pip install robotframework cantools python-can

# Ou com pip padrão
pip install robotframework cantools python-can
```

### 3️⃣ Verificar Instalação

```bash
python setup_project.py
```

Espere ver:
```
✓ Python 3.12
✓ robotframework
✓ cantools
✓ python-can
✓ Setup verification complete!
```

### 4️⃣ Executar Testes

```bash
# Todos os testes
robot tests/

# Teste específico
robot -t "Verify High Speed Behavior" tests/smoke_tests.robot

# Com relatório HTML
robot --outputdir ./results tests/
# Abra results/report.html no navegador
```

### 5️⃣ Ver Exemplos de Uso

```bash
python examples.py
```

---

## 📁 Estrutura de Arquivos

```
robot-framework/
├── libraries/
│   ├── __init__.py
│   └── automotive_lib.py .................. Mocks (ADB e CAN)
├── resources/
│   ├── vehicle_keywords.resource ......... Keywords Robot
│   └── vehicle_signals.dbc ............... Banco de dados CAN
├── tests/
│   └── smoke_tests.robot ................. Testes
├── variables/
│   ├── __init__.py
│   └── config.py ........................ Configuração global
├── setup_project.py ...................... Setup
├── examples.py .......................... Exemplos
├── quickstart.py ........................ Menu interativo
└── README.md ........................... Documentação completa
```

---

## 📚 O Que Está Implementado?

### ✅ Classe `AdbMock`
Simula comandos Android Debug Bridge:
```python
adb = AdbMock(device_id="test_device_001")
version = adb.get_property("ro.build.version.release")
```

### ✅ Classe `CanBusManager`
Gerencia barramento CAN virtual:
```python
can_mgr = CanBusManager("vehicle_signals.dbc")
can_mgr.inject_speed_signal(120)  # 120 km/h
```

### ✅ Keywords Robot Framework
Palavras-chave de alto nível:
```robot
Initialize System Mocks
Inject Speed Signal    120
Validate High Speed Alert Triggered
```

### ✅ Banco de Dados CAN (DBC)
3 mensagens predefinidas:
- **WheelSpeed** (ID: 100) - Velocidade dos pneus
- **ClusterAlert** (ID: 101) - Alertas do cluster
- **SystemStatus** (ID: 102) - Status do sistema

### ✅ Testes de Exemplo
4 testes smoke já implementados

---

## 🔍 Visualizar Resultados

Após executar `robot tests/`, abra no navegador:

```
file:///C:/src/robot-framework/results/report.html
```

Você verá:
- ✓ Testes passando/falhando
- ⏱️ Tempo de execução
- 📊 Gráficos de cobertura
- 📋 Logs detalhados

---

## 🎯 Teste Rápido (30 segundos)

```bash
# 1. Ativar ambiente
.venv\Scripts\activate

# 2. Rodar teste
robot -t "Verify High Speed Behavior" tests/smoke_tests.robot

# 3. Ver resultado
# Procure por "PASS" no output
```

---

## 🛠️ Próximos Passos

### Criar Novo Teste

1. Abra `tests/smoke_tests.robot`
2. Adicione novo `Test Case`:

```robot
Verify My Feature
    [Documentation]    Descrição do teste
    [Tags]    smoke    meu_teste
    
    Initialize System Mocks
    Inject Speed Signal    150
    Validate High Speed Alert Triggered
    Log    Teste passou!
```

3. Execute:
```bash
robot -t "Verify My Feature" tests/smoke_tests.robot
```

### Adicionar Nova Mensagem CAN

1. Edite `resources/vehicle_signals.dbc`
2. Adicione mensagem:

```dbc
BO_ 200 MyMessage: 8 Engine
 SG_ MySignal : 0|16@1+ (1,0) [0|65535] "" Cluster
```

3. Use em testes:

```robot
Inject My Signal
    ${result}=    Inject Speed Kmh    100
    Should Be True    ${result}
```

---

## ❓ Troubleshooting

### "Module not found"
```bash
# Solução: Adicionar ao PYTHONPATH
# Windows
set PYTHONPATH=%PYTHONPATH%;C:\src\robot-framework
# Linux/macOS
export PYTHONPATH=$PYTHONPATH:/path/to/robot-framework
```

### "cantools not installed"
```bash
uv pip install cantools
```

### "DBC file not found"
- Verificar caminho em `variables/config.py`
- Usar caminho absoluto se necessário

### "Virtual CAN channel not available"
- Normal em ambiente de testes
- O framework usa mock automaticamente
- Para usar CAN real, instale drivers SocketCAN

---

## 📞 Suporte

- 📖 Documentação completa: `README.md`
- 🔧 Técnico: `TECHNICAL_DOCUMENTATION.md`
- 💡 Exemplos: `python examples.py`
- 🐛 Setup: `python setup_project.py`

---

## ⏱️ Tempo Estimado

| Tarefa | Tempo |
|--------|-------|
| Setup inicial | 5 min |
| Primeiro teste | 2 min |
| Adicionar teste | 10 min |
| Entender arquitetura | 20 min |

---

## 🎓 Conceitos Principais

### Mock (Simulação)
Simulamos hardware sem precisar de equipamento real

### CAN Bus
Protocolo de comunicação automotivo simulado via arquivo DBC

### Robot Framework
Linguagem de testes com palavras-chave simples

### Keywords
Funções de alto nível para testes (ex: `Inject Speed Signal`)

---

## ✨ Boas Práticas

✅ Use keywords de alto nível  
✅ Documente seus testes com `[Documentation]`  
✅ Use tags com `[Tags]` para organizar  
✅ Implemente `Suite Setup` e `Suite Teardown`  
✅ Verifique resultados em `results/report.html`  

---

**Pronto! Agora execute `robot tests/` e veja seus testes rodarem! 🎉**

Para mais informações, veja o arquivo README.md completo.
