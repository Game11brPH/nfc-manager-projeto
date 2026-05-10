/*
 * GERENCIADOR NFC - MODO SERIAL
 * Recebe comandos da GUI Python
 * Comandos: VER | ESC:cpf | LER | APA
 */

#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN 9
#define SS_PIN 10

MFRC522 mfrc522(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key chave;

String comando = "";
boolean aguardandoTag = false;
String cpfPendente = "";
int acaoPendente = 0; // 1=VER 2=ESC 3=LER 4=APA

void setup() {
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();
  for (byte i = 0; i < 6; i++) chave.keyByte[i] = 0xFF;
  Serial.println("PRONTO");
}

void loop() {
  // Ler comando do Python
  if (Serial.available()) {
    comando = Serial.readStringUntil('\n');
    comando.trim();
    processarComando(comando);
  }

  // Se aguardando tag, verificar presenca
  if (aguardandoTag) {
    if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
      executarAcao();
      mfrc522.PICC_HaltA();
      mfrc522.PCD_StopCrypto1();
      aguardandoTag = false;
      acaoPendente = 0;
      cpfPendente = "";
    }
  }
}

void processarComando(String cmd) {
  if (cmd == "VER") {
    Serial.println("AGUARDANDO_TAG");
    acaoPendente = 1;
    aguardandoTag = true;
  }
  else if (cmd.startsWith("ESC:")) {
    cpfPendente = cmd.substring(4);
    if (cpfPendente.length() != 11) {
      Serial.println("ERRO:CPF invalido");
      return;
    }
    Serial.println("AGUARDANDO_TAG");
    acaoPendente = 2;
    aguardandoTag = true;
  }
  else if (cmd == "LER") {
    Serial.println("AGUARDANDO_TAG");
    acaoPendente = 3;
    aguardandoTag = true;
  }
  else if (cmd == "APA") {
    Serial.println("AGUARDANDO_TAG");
    acaoPendente = 4;
    aguardandoTag = true;
  }
  else if (cmd == "CANCELAR") {
    aguardandoTag = false;
    acaoPendente = 0;
    Serial.println("CANCELADO");
  }
}

void executarAcao() {
  String uid = getUID();
  Serial.println("UID:" + uid);

  switch (acaoPendente) {
    case 1: verificarAptidao(); break;
    case 2: escreverCPF(); break;
    case 3: lerTag(); break;
    case 4: apagarTag(); break;
  }
}

String getUID() {
  String uid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (mfrc522.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(mfrc522.uid.uidByte[i], HEX);
    if (i < mfrc522.uid.size - 1) uid += ":";
  }
  uid.toUpperCase();
  return uid;
}

void verificarAptidao() {
  boolean autentica = false;
  int livres = 0;

  if (mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, 1, &chave, &mfrc522.uid) == MFRC522::STATUS_OK) {
    autentica = true;
    for (byte b = 1; b < 4; b++) {
      byte buf[18]; byte tam = 18;
      if (mfrc522.MIFARE_Read(b, buf, &tam) == MFRC522::STATUS_OK) {
        boolean vazio = true;
        for (byte i = 0; i < 16; i++) {
          if (buf[i] != 0x00 && buf[i] != 0xFF) { vazio = false; break; }
        }
        if (vazio) livres++;
      }
    }
  }

  if (autentica && livres > 0) {
    Serial.println("VER:APTA:" + String(livres) + " blocos livres");
  } else {
    Serial.println("VER:INAPTA:Falha na autenticacao");
  }
}

void escreverCPF() {
  byte buf[16];
  for (byte i = 0; i < 16; i++) {
    buf[i] = (i < cpfPendente.length()) ? (byte)cpfPendente[i] : 0x20;
  }

  if (mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, 1, &chave, &mfrc522.uid) != MFRC522::STATUS_OK) {
    Serial.println("ESC:ERRO:Falha na autenticacao");
    return;
  }

  if (mfrc522.MIFARE_Write(1, buf, 16) == MFRC522::STATUS_OK) {
    Serial.println("ESC:OK:" + cpfPendente);
  } else {
    Serial.println("ESC:ERRO:Falha na escrita");
  }
}

void lerTag() {
  if (mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, 1, &chave, &mfrc522.uid) != MFRC522::STATUS_OK) {
    Serial.println("LER:ERRO:Falha na autenticacao");
    return;
  }

  byte buf[18]; byte tam = 18;
  if (mfrc522.MIFARE_Read(1, buf, &tam) != MFRC522::STATUS_OK) {
    Serial.println("LER:ERRO:Falha na leitura");
    return;
  }

  String conteudo = "";
  boolean temDado = false;
  for (byte i = 0; i < 16; i++) {
    if (buf[i] >= 32 && buf[i] <= 126) {
      conteudo += (char)buf[i];
      temDado = true;
    }
  }

  if (temDado) {
    conteudo.trim();
    Serial.println("LER:OK:" + conteudo);
  } else {
    Serial.println("LER:VAZIO:Tag sem dados");
  }
}

void apagarTag() {
  byte vazio[16] = {0};
  int apagados = 0;

  // Chaves para tentar
  byte chaves[][6] = {
    {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF},
    {0x00, 0x00, 0x00, 0x00, 0x00, 0x00},
    {0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5},
    {0xD3, 0xF7, 0xD3, 0xF7, 0xD3, 0xF7},
  };
  int numChaves = 4;

  for (byte bloco = 1; bloco < 64; bloco++) {
    if (bloco % 4 == 3) continue;

    // Tentar cada chave
    for (int c = 0; c < numChaves; c++) {
      MFRC522::MIFARE_Key chaveAtual;
      for (byte i = 0; i < 6; i++) chaveAtual.keyByte[i] = chaves[c][i];

      if (mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, bloco, &chaveAtual, &mfrc522.uid) == MFRC522::STATUS_OK) {
        if (mfrc522.MIFARE_Write(bloco, vazio, 16) == MFRC522::STATUS_OK) {
          apagados++;
        }
        break; // Chave funcionou, ir pro próximo bloco
      }
    }
  }

  if (apagados > 0) {
    Serial.println("APA:OK:" + String(apagados) + " blocos apagados");
  } else {
    Serial.println("APA:ERRO:Nenhum bloco apagado - chave desconhecida");
  }
}
