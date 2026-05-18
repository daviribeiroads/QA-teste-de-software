import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os


TEMPLATE_DESKTOP = '''from pywinauto.application import Application
from pywinauto import mouse
import pyautogui
import time

CAMINHO_SISTEMA = r"{caminho}"

USUARIO = "{usuario}"
SENHA = "{senha}"

ESPERA_CURTA = 1
ESPERA_MEDIA = 3
ESPERA_LONGA = 8
ESPERA_LOGIN = 10

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5


def iniciar_sistema():

    print("Abrindo sistema...")

    app = Application(
        backend="win32"
    ).start(CAMINHO_SISTEMA)

    time.sleep(ESPERA_LOGIN)

    try:

        janela = app.top_window()

        janela.set_focus()

    except Exception as erro:

        print(f"Erro ao focar janela: {{erro}}")

    return app


{funcoes}


def executar():

    iniciar_sistema()

{chamadas}


if __name__ == "__main__":

    executar()
'''


TEMPLATE_WEB = '''from selenium import webdriver
from selenium.webdriver.common.by import By
import pyautogui
import time

USUARIO = "{usuario}"
SENHA = "{senha}"

ESPERA_MEDIA = 3
ESPERA_LONGA = 8


{funcoes}


def executar(driver):

{chamadas}


if __name__ == "__main__":

    driver = webdriver.Chrome()

    driver.maximize_window()

    executar(driver)

    driver.quit()
'''


def gerar_funcao_desktop(nome, identificador):

    nome_funcao = (
        nome
        .strip()
        .lower()
        .replace(" ", "_")
    )

    if nome_funcao == "digitar_usuario":

        return '''
def digitar_usuario():

    print("Digitando usuário")

    pyautogui.write(
        USUARIO,
        interval=0.05
    )

    time.sleep(ESPERA_MEDIA)
'''

    if nome_funcao == "digitar_senha":

        return '''
def digitar_senha():

    print("Digitando senha")

    pyautogui.write(
        SENHA,
        interval=0.05
    )

    time.sleep(ESPERA_MEDIA)
'''

    try:

        partes = (
            identificador
            .replace("(", "")
            .replace(")", "")
            .split(",")
        )

        x = int(partes[0].strip())
        y = int(partes[1].strip())

        espera = "ESPERA_MEDIA"

        palavras_espera_longa = [
            "confirmar",
            "gravar",
            "emitir",
            "salvar",
            "processar",
            "fechar",
            "ok",
            "sim"
        ]

        for palavra in palavras_espera_longa:

            if palavra in nome_funcao:

                espera = "ESPERA_LONGA"
                break

        return f'''
def {nome_funcao}():

    print("Executando: {nome_funcao}")

    mouse.move(coords=({x}, {y}))

    time.sleep(1)

    mouse.click(coords=({x}, {y}))

    time.sleep({espera})
'''

    except Exception:

        return f'''
def erro_{nome_funcao}():

    print("Coordenada inválida")
'''


def gerar_funcao_web(nome, identificador):

    nome_funcao = (
        nome
        .strip()
        .lower()
        .replace(" ", "_")
    )

    ident = identificador.strip()

    if ident.startswith("//"):

        by = "By.XPATH"
        valor = ident

    elif ident.startswith("#"):

        by = "By.CSS_SELECTOR"
        valor = ident

    elif "=" in ident:

        tipo, val = ident.split("=", 1)

        tipo = tipo.strip().lower()
        val = val.strip()

        mapa = {
            "id": "By.ID",
            "class": "By.CLASS_NAME",
            "name": "By.NAME",
            "css": "By.CSS_SELECTOR",
            "xpath": "By.XPATH",
            "text": "By.LINK_TEXT",
        }

        by = mapa.get(tipo, "By.ID")
        valor = val

    else:

        by = "By.ID"
        valor = ident

    return f'''
def {nome_funcao}(driver):

    print("Executando: {nome_funcao}")

    driver.find_element(
        {by},
        "{valor}"
    ).click()

    time.sleep(ESPERA_MEDIA)
'''


def gerar_codigo(
    tipo,
    caminho,
    usuario,
    senha,
    acoes
):

    funcoes = ""
    chamadas = ""

    for nome, identificador in acoes:

        nome_funcao = (
            nome
            .strip()
            .lower()
            .replace(" ", "_")
        )

        if tipo == "Desktop":

            funcoes += gerar_funcao_desktop(
                nome,
                identificador
            )

            chamadas += f"    {nome_funcao}()\n"

        else:

            funcoes += gerar_funcao_web(
                nome,
                identificador
            )

            chamadas += f"    {nome_funcao}(driver)\n"

    if tipo == "Desktop":

        return TEMPLATE_DESKTOP.format(
            caminho=caminho,
            usuario=usuario,
            senha=senha,
            funcoes=funcoes,
            chamadas=chamadas
        )

    return TEMPLATE_WEB.format(
        usuario=usuario,
        senha=senha,
        funcoes=funcoes,
        chamadas=chamadas
    )


class App(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title("Gerador de Automação QA")

        self.geometry("520x700")

        self.configure(bg="#1e1e2e")

        self.resizable(False, False)

        self._acoes = []

        self.build()

    def build(self):

        pad = {"padx": 10, "pady": 4}

        titulo = tk.Label(
            self,
            text="⚙ Gerador de Automação QA",
            font=("Segoe UI", 15, "bold"),
            bg="#1e1e2e",
            fg="#cdd6f4"
        )

        titulo.grid(
            row=0,
            column=0,
            columnspan=2,
            pady=12
        )

        self.label("Modulo:", 1)

        self.ent_projeto = self.entry(
            1,
            "ex: estoque"
        )

        self.label("Tipo:", 2)

        self.cmb_tipo = ttk.Combobox(
            self,
            values=["Desktop", "Web"],
            state="readonly",
            width=37
        )

        self.cmb_tipo.current(0)

        self.cmb_tipo.grid(
            row=2,
            column=1,
            **pad
        )

        self.label("Executável oi URL:", 3)

        self.ent_caminho = self.entry(
            3,
            r"C:\Sistema\sistema.exe ou www.sistema.com.br"
        )

        self.label("Usuário:", 4)

        self.ent_usuario = self.entry(4)

        self.label("Senha:", 5)

        self.ent_senha = self.entry(5)

        self.ent_senha.config(show="*")

        self.label("Nome da Ação:", 6)

        self.ent_nome = self.entry(
            6,
            "ex: clicar_usuario"
        )

        self.label("Identificador:", 7)

        self.ent_id = self.entry(
            7,
            "coord. 782,146 ou Selet. id, class, etc..."
        )

        dica = tk.Label(
            self,
            text="Use: digitar_usuario e digitar_senha",
            bg="#1e1e2e",
            fg="#a6e3a1",
            font=("Segoe UI", 8)
        )

        dica.grid(
            row=8,
            column=1,
            sticky="w",
            padx=10
        )

        btn_add = tk.Button(
            self,
            text="+ Adicionar",
            command=self.adicionar_acao,
            bg="#89b4fa",
            fg="#1e1e2e",
            relief="flat",
            width=18,
            font=("Segoe UI", 10, "bold")
        )

        btn_add.grid(
            row=9,
            column=1,
            sticky="w",
            pady=6,
            padx=10
        )

        frame_lista = tk.Frame(
            self,
            bg="#1e1e2e"
        )

        frame_lista.grid(
            row=10,
            column=0,
            columnspan=2,
            padx=10,
            pady=5
        )

        scrollbar = tk.Scrollbar(frame_lista)

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.listbox = tk.Listbox(
            frame_lista,
            width=65,
            height=10,
            bg="#313244",
            fg="#cdd6f4",
            font=("Consolas", 10),
            yscrollcommand=scrollbar.set
        )

        self.listbox.pack()

        scrollbar.config(
            command=self.listbox.yview
        )

        btn_remover = tk.Button(
            self,
            text="Remover",
            command=self.remover_acao,
            bg="#f38ba8",
            fg="#1e1e2e",
            relief="flat",
            width=15
        )

        btn_remover.grid(
            row=11,
            column=1,
            sticky="w",
            pady=5,
            padx=10
        )

        btn_gerar = tk.Button(
            self,
            text="⚡ Gerar Código",
            command=self.gerar,
            bg="#a6e3a1",
            fg="#1e1e2e",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            width=22,
            height=2
        )

        btn_gerar.grid(
            row=12,
            column=0,
            columnspan=2,
            pady=10
        )

    def label(self, texto, row):

        tk.Label(
            self,
            text=texto,
            bg="#1e1e2e",
            fg="#cdd6f4",
            font=("Segoe UI", 10)
        ).grid(
            row=row,
            column=0,
            sticky="e",
            padx=10,
            pady=4
        )

    def entry(self, row, valor=""):

        ent = tk.Entry(
            self,
            width=40,
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="#cdd6f4",
            relief="flat",
            font=("Segoe UI", 10)
        )

        ent.grid(
            row=row,
            column=1,
            padx=10,
            pady=4
        )

        ent.insert(0, valor)

        return ent

    def adicionar_acao(self):

        nome = self.ent_nome.get().strip()

        ident = self.ent_id.get().strip()

        if not nome or not ident:

            messagebox.showwarning(
                "Atenção",
                "Informe os dados."
            )

            return

        self._acoes.append((nome, ident))

        self.listbox.insert(
            tk.END,
            f"{len(self._acoes):02d}. {nome} → {ident}"
        )

        self.ent_nome.delete(0, tk.END)

        self.ent_id.delete(0, tk.END)

    def remover_acao(self):

        sel = self.listbox.curselection()

        if not sel:
            return

        idx = sel[0]

        self.listbox.delete(idx)

        self._acoes.pop(idx)

    def gerar(self):

        projeto = self.ent_projeto.get().strip()

        tipo = self.cmb_tipo.get()

        caminho = self.ent_caminho.get().strip()

        usuario = self.ent_usuario.get().strip()

        senha = self.ent_senha.get().strip()

        if not projeto:

            messagebox.showwarning(
                "Atenção",
                "Informe o projeto."
            )

            return

        if tipo == "Desktop" and not caminho:

            messagebox.showwarning(
                "Atenção",
                "Informe o executável."
            )

            return

        if not self._acoes:

            messagebox.showwarning(
                "Atenção",
                "Adicione ações."
            )

            return

        codigo = gerar_codigo(
            tipo,
            caminho,
            usuario,
            senha,
            self._acoes
        )

        pasta = filedialog.askdirectory(
            title="Escolha a pasta"
        )

        if not pasta:
            return

        caminho_arquivo = os.path.join(
            pasta,
            f"{projeto}.py"
        )

        with open(
            caminho_arquivo,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(codigo)

        messagebox.showinfo(
            "Sucesso",
            f"Código gerado:\\n{caminho_arquivo}"
        )


if __name__ == "__main__":

    app = App()

    app.mainloop()
