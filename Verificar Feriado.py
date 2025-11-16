import tkinter as tk
from tkinter import filedialog
from pypdf import PdfReader
import re
import requests
from datetime import datetime

def buscar_feriados(ano):
    
    url = f"https://date.nager.at/api/v3/PublicHolidays/{ano}/BR"
    headers = {
      'accept': 'application/json'
    }
    response = requests.request("GET", url, headers=headers)
    response.raise_for_status() 
    print(f"\n--- Resposta da API para o ano {ano} ---\n{response.text}\n----------------------------------")
    feriados_data = {f['date'] for f in response.json()}
    return feriados_data

def extrair_e_verificar_pdf():
    
    caminho_arquivo = filedialog.askopenfilename(
        title="Selecione um Arquivo PDF",
        filetypes=(("Arquivos PDF", "*.pdf"), ("Todos os Arquivos", "*.*"))
    )
    reader = PdfReader(caminho_arquivo)
    texto_completo = ""
    for pagina in reader.pages:
        texto_completo += pagina.extract_text() + "\n"

    padrao_datas = re.compile(r'\b(\d{4}-\d{2}-\d{2})\b')
    datas_encontradas = set(padrao_datas.findall(texto_completo))
    
    if not datas_encontradas:
        print("Nenhuma data no formato AAAA-MM-DD foi encontrada no PDF.")
        return

    datas_formatadas = {}
    anos = set()
    
    for data_str in datas_encontradas:
        data_iso = data_str
        data_obj = datetime.strptime(data_str, '%Y-%m-%d')
        datas_formatadas[data_str] = data_iso
        anos.add(data_obj.year)

    feriados_por_ano = {}
    for ano in anos:
        feriados_por_ano[ano] = buscar_feriados(ano)
    
    resultados = "Datas Encontradas e Status de Feriado (no Console):\n\n"
    feriados_encontrados = []

janela = tk.Tk()
janela.title("Verificador de Feriados em PDF (Console)")
janela.geometry("300x120")
rotulo = tk.Label(janela, text="Selecione um PDF para verificar as datas de feriado.")
rotulo.pack(pady=15)
botao_abrir = tk.Button(
    janela, 
    text="Selecionar e Verificar PDF", 
    command=extrair_e_verificar_pdf
)
botao_abrir.pack(pady=5)

janela.mainloop()