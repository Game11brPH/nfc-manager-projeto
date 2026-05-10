"""
GERENCIADOR NFC - GUI v2
Interface redesenhada com visual moderno
Requer: pip install pyserial
"""

import tkinter as tk
from tkinter import messagebox
import serial
import serial.tools.list_ports
import threading
import time

BAUD = 9600

C = {
    "bg":        "#0A0E1A",
    "panel":     "#111827",
    "card":      "#1A2235",
    "border":    "#1E3A5F",
    "primary":   "#00D4FF",
    "success":   "#00FF88",
    "danger":    "#FF4757",
    "warning":   "#FFB300",
    "purple":    "#B44FFF",
    "text":      "#E8F4FD",
    "muted":     "#5A7A99",
    "dim":       "#2A3F55",
}

FONT = "Consolas"


class GerenciadorNFC:
    def __init__(self, root):
        self.root = root
        self.root.title("NFC Manager")
        self.root.geometry("720x680")
        self.root.resizable(False, False)
        self.root.configure(bg=C["bg"])

        self.serial = None
        self.conectado = False
        self.lendo = False

        self._build()
        self._refresh_ports()

    # ──────────────────────────────────────
    # BUILD UI
    # ──────────────────────────────────────
    def _build(self):
        self._header()
        self._connection_bar()
        self._cpf_section()
        self._action_cards()
        self._log_section()
        self._statusbar()

    def _header(self):
        h = tk.Canvas(self.root, height=90, bg=C["bg"], highlightthickness=0)
        h.pack(fill="x")

        for i in range(90):
            r = int(10 + i * 0.3)
            g = int(14 + i * 0.2)
            b = int(26 + i * 0.5)
            cor = f"#{r:02x}{g:02x}{b:02x}"
            h.create_rectangle(0, i, 720, i+1, fill=cor, outline="")

        h.create_rectangle(0, 0, 720, 2, fill=C["primary"], outline="")
        h.create_text(46, 45, text="◈", font=(FONT, 32, "bold"),
                      fill=C["primary"], anchor="center")
        h.create_text(200, 30, text="NFC MANAGER",
                      font=(FONT, 22, "bold"), fill=C["text"], anchor="w")
        h.create_text(200, 58, text="Sistema de Gerenciamento de Tags RFID/NFC",
                      font=(FONT, 9), fill=C["muted"], anchor="w")

        self.canvas_status = tk.Canvas(h, width=120, height=30,
                                       bg=C["bg"], highlightthickness=0)
        h.create_window(590, 45, window=self.canvas_status)
        self._draw_status(False)

    def _draw_status(self, ativo):
        c = self.canvas_status
        c.delete("all")
        cor = C["success"] if ativo else C["danger"]
        txt = "ONLINE" if ativo else "OFFLINE"
        c.create_oval(5, 7, 21, 23, fill=cor, outline="")
        c.create_text(30, 15, text=txt, font=(FONT, 10, "bold"),
                      fill=cor, anchor="w")

    def _connection_bar(self):
        f = tk.Frame(self.root, bg=C["panel"], pady=10, padx=16)
        f.pack(fill="x")

        tk.Label(f, text="⚡ PORTA:", font=(FONT, 9, "bold"),
                 bg=C["panel"], fg=C["muted"]).pack(side="left", padx=(0, 6))

        self.var_porta = tk.StringVar()
        self.combo = tk.OptionMenu(f, self.var_porta, "")
        self.combo.config(
            font=(FONT, 9), bg=C["card"], fg=C["text"],
            activebackground=C["dim"], activeforeground=C["primary"],
            relief="flat", bd=0, highlightthickness=0,
            padx=10, pady=4, cursor="hand2", indicatoron=False
        )
        self.combo["menu"].config(bg=C["card"], fg=C["text"],
                                   activebackground=C["border"],
                                   activeforeground=C["primary"],
                                   font=(FONT, 9))
        self.combo.pack(side="left", padx=(0, 6))

        tk.Button(f, text="↻", font=(FONT, 11),
                  bg=C["dim"], fg=C["text"], relief="flat", bd=0,
                  padx=8, pady=2, cursor="hand2",
                  command=self._refresh_ports,
                  activebackground=C["border"]).pack(side="left", padx=(0, 16))

        self.btn_con = tk.Button(
            f, text="  ⚡  CONECTAR  ",
            font=(FONT, 9, "bold"),
            bg=C["primary"], fg=C["bg"],
            relief="flat", bd=0, padx=12, pady=6,
            cursor="hand2", command=self._toggle,
            activebackground=C["primary"]
        )
        self.btn_con.pack(side="left")

        tk.Frame(self.root, bg=C["border"], height=1).pack(fill="x")

    def _cpf_section(self):
        f = tk.Frame(self.root, bg=C["bg"], pady=14, padx=16)
        f.pack(fill="x")

        tk.Label(f, text="🪪  CPF PARA GRAVACAO",
                 font=(FONT, 9, "bold"),
                 bg=C["bg"], fg=C["muted"]).pack(anchor="w", pady=(0, 8))

        row = tk.Frame(f, bg=C["bg"])
        row.pack(fill="x")

        inp_frame = tk.Frame(row, bg=C["border"], padx=1, pady=1)
        inp_frame.pack(side="left", padx=(0, 10))

        self.var_cpf = tk.StringVar()
        self.var_cpf.trace("w", self._on_cpf)
        self.entry = tk.Entry(
            inp_frame, textvariable=self.var_cpf,
            width=14, font=(FONT, 16, "bold"),
            bg=C["card"], fg=C["primary"],
            insertbackground=C["primary"],
            relief="flat", bd=8,
        )
        self.entry.pack()

        self.lbl_cpf = tk.Label(row, text="",
                                  font=(FONT, 9),
                                  bg=C["bg"], fg=C["muted"])
        self.lbl_cpf.pack(side="left")

        tk.Frame(self.root, bg=C["border"], height=1).pack(fill="x")

    def _action_cards(self):
        f = tk.Frame(self.root, bg=C["bg"], padx=16, pady=16)
        f.pack(fill="x")

        tk.Label(f, text="ACOES",
                 font=(FONT, 9, "bold"),
                 bg=C["bg"], fg=C["muted"]).pack(anchor="w", pady=(0, 12))

        grid = tk.Frame(f, bg=C["bg"])
        grid.pack(fill="x")

        cards = [
            ("◉", "VERIFICAR",  "Verifica se a tag esta\napta para registro",    C["primary"], self._verificar),
            ("✎", "ESCREVER",   "Grava o CPF digitado\nna tag NFC",              C["success"],  self._escrever),
            ("◎", "LER TAG",    "Le e exibe o conteudo\ngravado na tag",         C["purple"],   self._ler),
            ("✕", "APAGAR",     "Apaga todos os dados\nda tag completamente",     C["danger"],   self._apagar),
        ]

        for i, (icone, titulo, desc, cor, cmd) in enumerate(cards):
            col = i % 2
            row = i // 2
            grid.columnconfigure(col, weight=1)

            card = tk.Frame(grid, bg=C["card"],
                            highlightthickness=1,
                            highlightbackground=C["dim"])
            card.grid(row=row, column=col, padx=6, pady=6, sticky="ew")

            tk.Frame(card, bg=cor, height=3).pack(fill="x")

            inner = tk.Frame(card, bg=C["card"], padx=14, pady=12)
            inner.pack(fill="x")

            tk.Label(inner, text=icone,
                     font=(FONT, 28, "bold"),
                     bg=C["card"], fg=cor).pack(side="left", padx=(0, 12))

            info = tk.Frame(inner, bg=C["card"])
            info.pack(side="left", fill="x", expand=True)

            tk.Label(info, text=titulo,
                     font=(FONT, 12, "bold"),
                     bg=C["card"], fg=C["text"],
                     anchor="w").pack(fill="x")

            tk.Label(info, text=desc,
                     font=(FONT, 8),
                     bg=C["card"], fg=C["muted"],
                     anchor="w", justify="left").pack(fill="x")

            tk.Button(
                inner, text="▶",
                font=(FONT, 12, "bold"),
                bg=cor, fg=C["bg"],
                relief="flat", bd=0,
                padx=12, pady=6,
                cursor="hand2",
                command=cmd,
                activebackground=cor
            ).pack(side="right")

        tk.Frame(self.root, bg=C["border"], height=1).pack(fill="x")

    def _log_section(self):
        f = tk.Frame(self.root, bg=C["bg"], padx=16, pady=10)
        f.pack(fill="both", expand=True)

        top = tk.Frame(f, bg=C["bg"])
        top.pack(fill="x", pady=(0, 6))

        tk.Label(top, text="TERMINAL",
                 font=(FONT, 9, "bold"),
                 bg=C["bg"], fg=C["muted"]).pack(side="left")

        tk.Button(top, text="LIMPAR",
                  font=(FONT, 8),
                  bg=C["dim"], fg=C["muted"],
                  relief="flat", bd=0, padx=8, pady=2,
                  cursor="hand2", command=self._clear_log,
                  activebackground=C["border"]).pack(side="right")

        frame_txt = tk.Frame(f, bg=C["border"], padx=1, pady=1)
        frame_txt.pack(fill="both", expand=True)

        self.log = tk.Text(
            frame_txt, font=(FONT, 9),
            bg=C["panel"], fg=C["text"],
            relief="flat", bd=0, state="disabled",
            wrap="word", height=7, padx=10, pady=8,
        )
        self.log.pack(fill="both", expand=True)

        self.log.tag_config("ok",   foreground=C["success"])
        self.log.tag_config("err",  foreground=C["danger"])
        self.log.tag_config("info", foreground=C["primary"])
        self.log.tag_config("warn", foreground=C["warning"])
        self.log.tag_config("dim",  foreground=C["muted"])
        self.log.tag_config("uid",  foreground=C["purple"])

    def _statusbar(self):
        self.statusbar = tk.Label(
            self.root, text="Aguardando conexao...",
            font=(FONT, 8), bg=C["panel"], fg=C["muted"],
            pady=6, anchor="w", padx=16
        )
        self.statusbar.pack(fill="x", side="bottom")

    # ──────────────────────────────────────
    # CONEXAO
    # ──────────────────────────────────────
    def _refresh_ports(self):
        portas = [p.device for p in serial.tools.list_ports.comports()]
        menu = self.combo["menu"]
        menu.delete(0, "end")
        for p in portas:
            menu.add_command(label=p, command=lambda v=p: self.var_porta.set(v))
        if portas:
            self.var_porta.set(portas[0])

    def _toggle(self):
        if self.conectado: self._disconnect()
        else: self._connect()

    def _connect(self):
        porta = self.var_porta.get()
        if not porta:
            messagebox.showerror("Erro", "Selecione uma porta COM!")
            return
        try:
            self.serial = serial.Serial(porta, BAUD, timeout=1)
            time.sleep(2)
            self.conectado = True
            self.lendo = True
            self.btn_con.config(text="  ✕  DESCONECTAR  ", bg=C["danger"], fg="white")
            self._draw_status(True)
            self._set_status(f"Conectado em {porta} @ {BAUD} baud")
            self._log(f"Conectado em {porta}", "ok")
            threading.Thread(target=self._serial_loop, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _disconnect(self):
        self.lendo = False
        if self.serial: self.serial.close()
        self.conectado = False
        self.btn_con.config(text="  ⚡  CONECTAR  ", bg=C["primary"], fg=C["bg"])
        self._draw_status(False)
        self._set_status("Desconectado")
        self._log("Desconectado", "warn")

    def _serial_loop(self):
        while self.lendo:
            try:
                if self.serial and self.serial.in_waiting:
                    linha = self.serial.readline().decode("utf-8").strip()
                    if linha:
                        self.root.after(0, self._on_response, linha)
            except: pass
            time.sleep(0.05)

    # ──────────────────────────────────────
    # ACOES
    # ──────────────────────────────────────
    def _verificar(self):
        if not self._check(): return
        self._log("── VERIFICAR ─────────────────────", "info")
        self._log("Aproxime a tag do leitor...", "warn")
        self._set_status("Aguardando tag para verificacao...")
        self._send("VER")

    def _escrever(self):
        if not self._check(): return
        cpf = self.var_cpf.get().strip()
        if len(cpf) != 11 or not cpf.isdigit():
            messagebox.showerror("CPF Invalido", "Digite exatamente 11 digitos numericos!")
            return
        self._log("── ESCREVER CPF ──────────────────", "info")
        self._log(f"CPF: {cpf}", "dim")
        self._log("Aproxime a tag do leitor...", "warn")
        self._set_status("Aguardando tag para gravar CPF...")
        self._send(f"ESC:{cpf}")

    def _ler(self):
        if not self._check(): return
        self._log("── LER CONTEUDO ──────────────────", "info")
        self._log("Aproxime a tag do leitor...", "warn")
        self._set_status("Aguardando tag para leitura...")
        self._send("LER")

    def _apagar(self):
        if not self._check(): return
        if not messagebox.askyesno("Confirmar Exclusao",
            "Tem certeza que deseja APAGAR todos os dados?\n\nEsta acao NAO pode ser desfeita!"
        ): return
        self._log("── APAGAR TAG ────────────────────", "info")
        self._log("Aproxime a tag do leitor...", "warn")
        self._set_status("Aguardando tag para apagar...")
        self._send("APA")

    # ──────────────────────────────────────
    # RESPOSTAS
    # ──────────────────────────────────────
    def _on_response(self, linha):
        if linha == "PRONTO":
            self._log("Arduino pronto!", "ok")
            self._set_status("Pronto. Escolha uma acao.")
        elif linha.startswith("UID:"):
            self._log(f"UID: {linha[4:]}", "uid")
        elif linha.startswith("VER:APTA"):
            self._log(f"✓ TAG APTA - {linha.split(':')[2]}", "ok")
            self._set_status("Tag apta para registro!")
        elif linha.startswith("VER:INAPTA"):
            self._log(f"✗ TAG INAPTA - {linha.split(':')[2]}", "err")
            self._set_status("Tag nao esta apta.")
        elif linha.startswith("ESC:OK"):
            self._log(f"✓ CPF GRAVADO - {linha.split(':')[2]}", "ok")
            self._set_status("CPF gravado com sucesso!")
        elif linha.startswith("ESC:ERRO"):
            self._log(f"✗ ERRO AO GRAVAR - {linha.split(':')[2]}", "err")
            self._set_status("Erro ao gravar CPF.")
        elif linha.startswith("LER:OK"):
            self._log(f"✓ CONTEUDO: {linha.split(':')[2]}", "ok")
            self._set_status(f"Lido: {linha.split(':')[2]}")
        elif linha.startswith("LER:VAZIO"):
            self._log("Tag sem dados gravados", "warn")
            self._set_status("Tag vazia.")
        elif linha.startswith("LER:ERRO"):
            self._log(f"✗ ERRO - {linha.split(':')[2]}", "err")
        elif linha.startswith("APA:OK"):
            self._log(f"✓ TAG APAGADA - {linha.split(':')[2]}", "ok")
            self._set_status("Tag apagada com sucesso!")
        elif linha.startswith("APA:ERRO"):
            self._log(f"✗ ERRO AO APAGAR - {linha.split(':')[2]}", "err")
            self._set_status("Erro ao apagar tag.")

    # ──────────────────────────────────────
    # UTILITARIOS
    # ──────────────────────────────────────
    def _send(self, msg):
        try: self.serial.write((msg + "\n").encode())
        except Exception as e: self._log(f"Erro: {e}", "err")

    def _log(self, msg, tag=""):
        ts = time.strftime("%H:%M:%S")
        self.log.config(state="normal")
        self.log.insert("end", f"[{ts}] ", "dim")
        self.log.insert("end", f"{msg}\n", tag)
        self.log.see("end")
        self.log.config(state="disabled")

    def _clear_log(self):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")

    def _set_status(self, msg):
        self.statusbar.config(text=f"  {msg}")

    def _on_cpf(self, *_):
        cpf = self.var_cpf.get()
        if not cpf.isdigit() and cpf:
            self.var_cpf.set(''.join(c for c in cpf if c.isdigit()))
            return
        n = len(cpf)
        if n == 11:
            self.lbl_cpf.config(text="✓ valido", fg=C["success"])
        elif n > 0:
            self.lbl_cpf.config(text=f"{11 - n} digitos restantes", fg=C["warning"])
        else:
            self.lbl_cpf.config(text="")

    def _check(self):
        if not self.conectado:
            messagebox.showwarning("Sem Conexao", "Conecte o Arduino primeiro!")
            return False
        return True


if __name__ == "__main__":
    root = tk.Tk()
    app = GerenciadorNFC(root)
    root.mainloop()
