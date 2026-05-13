from dotenv import load_dotenv
from pywinauto import Application, mouse
import json
import os
import time

load_dotenv()

with open("coordenadas.json") as f:
    C = json.load(f)

ESPERA_CURTA = 1
ESPERA_MEDIA = 2
ESPERA_LONGA = 6
ESPERA_GRAVACAO = 20


def executar():
    caminho = r"C:\Nasajon Sistemas\Integratto2\nsjEstoque.exe"
    usuario = os.environ.get("USUARIO")
    senha = os.environ.get("SENHA")

    if not usuario or not senha:
        print("ERRO: credenciais não encontradas no .env")
        return

    print("Abrindo sistema...")
    app = Application(backend="win32").start(caminho)

    janela = app.window(title="Acesso do Usuário")
    janela.wait('visible', timeout=30)

    janela.child_window(class_name="TEdit",
                        found_index=1).set_edit_text(usuario)
    janela.child_window(class_name="TEdit", found_index=0).set_edit_text(senha)
    time.sleep(1)

    janela.child_window(title="&Confirmar",
                        class_name="TcxButton").click_input()
    print("Login enviado")

    janela.wait_not('visible', timeout=20)

    print("Chamando notafiscal...")
    notafiscal(app)


def notafiscal(app):
    try:
        window = _abrir_janela_principal(app)
        _navegar_ate_nota_fiscal(window)
        _copiar_nota()
        _gravar_nota()
        _emitir_nota()
    except Exception as e:
        print(f"ERRO na navegação: {e}")
        raise


def _abrir_janela_principal(app):
    print("Aguardando janela principal...")
    window = app.window(title_re=".*Nasajon.*Estoque Sql.*")
    window.wait('visible', timeout=40)
    window.set_focus()
    time.sleep(ESPERA_CURTA)
    return window


def _navegar_ate_nota_fiscal(window):
    print("Navegando até Nota Fiscal de Entrada...")
    ribbon = window.child_window(class_name="TdxRibbon")
    ribbon_rect = ribbon.rectangle()
    win_rect = window.rectangle()

    y_aba = ribbon_rect.top + C["aba_nfe_y_offset"]
    x_aba_nfe = win_rect.left + C["aba_nfe_x"]

    mouse.click(coords=(x_aba_nfe, y_aba))
    time.sleep(ESPERA_MEDIA)

    mouse.click(coords=tuple(C["menu_documento"]))
    time.sleep(ESPERA_MEDIA)

    mouse.click(coords=tuple(C["nfe_entrada_1"]))
    time.sleep(ESPERA_LONGA)

    mouse.click(coords=tuple(C["nfe_entrada_2"]))
    time.sleep(ESPERA_LONGA)


def _copiar_nota():
    print("Copiando nota...")
    mouse.move(coords=tuple(C["hover_acoes"]))
    time.sleep(ESPERA_LONGA)
    mouse.click(coords=tuple(C["copiar_nota"]))
    time.sleep(15)


def _gravar_nota():
    print("Gravando nota...")
    mouse.click(coords=tuple(C["gravar_nota"]))
    time.sleep(ESPERA_GRAVACAO)
    mouse.click(coords=tuple(C["confirmar_gravacao"]))
    time.sleep(ESPERA_LONGA)


def _emitir_nota():
    print("Emitindo nota...")
    mouse.click(coords=tuple(C["emitir_nota"]))
    time.sleep(ESPERA_LONGA)
    print("Nota emitida com sucesso!")


executar()
