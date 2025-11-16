import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from pypdf import PdfReader
import re
import requests
from datetime import datetime

def exibir_resultados(titulo, texto):
    janela_texto = tk.Toplevel()
    janela_texto.title(titulo)
    janela_texto.geometry("600x400")
    area_texto = scrolledtext.ScrolledText(janela_texto, wrap=tk.WORD, font=("Arial", 10))
    area_texto.pack(expand=True, fill='both', padx=10, pady=10)
    area_texto.insert(tk.INSERT, texto)
    area_texto.config(state=tk.DISABLED)

def buscar_feriados(ano):
    url = f"https://date.nager.at/api/v3/PublicHolidays/{ano}/BR"
    
    headers = {
      'accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers)
    
    response.raise_for_status() 
    
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
        exibir_resultados("Resultado da Verificação", "Nenhuma data no formato AAAA-MM-DD foi encontrada no PDF.")
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
    
    resultados = "Datas Encontradas e Status de Feriado:\n\n"
    feriados_encontrados = []
    
    for original, iso in datas_formatadas.items():
        ano_data = int(iso[:4])
        
        if ano_data in feriados_por_ano and iso in feriados_por_ano[ano_data]:
            resultados += f"{original} - É FERIADO!\n"
            feriados_encontrados.append(original)
        else:
            resultados += f"{original} - Não é feriado.\n"

    resultados += f"\n--- RESUMO ---\nTotal de datas únicas encontradas: {len(datas_encontradas)}\nTotal de feriados encontrados: {len(feriados_encontrados)}\n"
    exibir_resultados("Resultado da Verificação de Feriados", resultados)

janela = tk.Tk()
janela.title("Verificador de Feriados em PDF")
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