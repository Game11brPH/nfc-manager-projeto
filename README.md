# ◈ NFC Manager

[![Arduino](https://img.shields.io/badge/Arduino-Uno-00979D?style=flat&logo=arduino)](https://www.arduino.cc/)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat&logo=python)](https://www.python.org/)
[![HTML](https://img.shields.io/badge/Interface-Web%20Serial%20API-E34F26?style=flat&logo=html5)](https://developer.mozilla.org/en-US/docs/Web/API/Web_Serial_API)

**NFC Manager** é um sistema embarcado de gerenciamento de tags NFC/RFID desenvolvido com Arduino Uno e módulo MFRC522, voltado para registro e controle de acesso via CPF. O projeto nasceu como exercício prático de engenharia de computação e evoluiu para uma solução completa com três camadas de interface: firmware em C para Arduino, GUI desktop em Python e interface web moderna com Web Serial API.

O sistema permite **gravar, ler, verificar e apagar** dados de tags NFC do tipo MIFARE Classic 1K, sendo capaz de armazenar CPFs (11 dígitos) diretamente na memória da tag, no bloco 1, usando autenticação por chave padrão. Durante o desenvolvimento foram investigadas também as limitações de tags com chaves de acesso desconhecidas, leitura de dados binários proprietários de sistemas de condomínio, e análise completa de dump de memória das tags.

A interface web, acessível via GitHub Pages, comunica-se diretamente com o Arduino pela porta serial do computador usando a **Web Serial API** nativa do Chrome, eliminando a necessidade de qualquer instalação adicional. O design foi desenvolvido com estética cyberpunk/tech dark, animações em CSS, grid animado de fundo, cards com bordas coloridas por ação e terminal de saída estilo macOS.

**Hardware utilizado:** Arduino Uno, módulo RFID-RC522, protoboard, jumpers e tags MIFARE Classic 1K (cartão e chaveiro). Tensão de operação do módulo: 3.3V. Comunicação via protocolo SPI nos pinos 9 a 13.

**Stack:** C (Arduino/AVR) · Python 3 + Tkinter + PySerial · HTML5 + CSS3 + JavaScript (Web Serial API)

---

## 🖥️ Interface Web (GitHub Pages)

Acesse direto pelo navegador (Chrome/Edge):

**[▶ Abrir NFC Manager](https://PedrosHttps.github.io/nfc-manager-projeto/nfc_manager.html)**

---

## 📦 Componentes Necessários

| Componente | Descrição |
|---|---|
| Arduino Uno | Microcontrolador principal |
| MFRC522 | Módulo leitor NFC/RFID |
| Protoboard | Para conexões |
| Jumpers | Fios de conexão |
| Tags NFC | MIFARE Classic 1K |
| Cabo USB | Comunicação com PC |

---

## 🔌 [Conexão dos Pinos]
[Link para visualização da conexão](esquema_ligacoes.svg)
| MFRC522 | Arduino Uno |
|---|---|
| VCC | 3.3V |
| GND | GND |
| RST | Pino 9 |
| SDA | Pino 10 |
| MOSI | Pino 11 |
| MISO | Pino 12 |
| SCK | Pino 13 |
| IRQ | Opcional |


---

## 🚀 Como Usar

### Opção 1: Interface Web (Recomendado)

1. Abra o link do GitHub Pages acima no **Chrome** ou **Edge**
2. Faça upload do `arduino_nfc_serial.ino` no Arduino
3. Feche o Arduino IDE
4. Clique em **⚡ Conectar Arduino** na interface
5. Selecione a porta COM na janela do Chrome
6. Use as 4 ações disponíveis

### Opção 2: Interface Python

```bash
pip install pyserial
python gui_nfc.py
```

---

## ⚙️ Funcionalidades

| Ação | Descrição |
|---|---|
| ◉ Verificar | Verifica se a tag está apta para registro |
| ✎ Escrever | Grava CPF (11 dígitos) na tag |
| ◎ Ler Tag | Lê e exibe o conteúdo gravado |
| ✕ Apagar | Apaga todos os dados da tag |

---

## 📁 Arquivos do Projeto

```
nfc-manager/
├── nfc_manager.html        ← Interface Web (GitHub Pages)
├── gui_nfc.py              ← Interface Python (alternativa)
├── arduino_nfc_serial.ino  ← Código do Arduino
└── README.md
```


## 🔧 Dependências

### Arduino IDE
- Biblioteca: **MFRC522** (instalar via Library Manager)

### Python
```bash
pip install pyserial
```

### Web
- Navegador: **Google Chrome** ou **Microsoft Edge**
- API: Web Serial API (nativa, sem instalação)

---

## ⚠️ Observações

- A interface Web **não funciona no Firefox** (Web Serial API não suportada)
- Feche o **Arduino IDE** antes de usar a interface (conflito de porta COM)
- Tags compatíveis: **MIFARE Classic 1K** (as mais comuns)
- Tensão do módulo MFRC522: **3.3V** (não use 5V neste módulo)

---

## 📝 Licença

MIT License — livre para uso e modificação.
