import tkinter as tk
from tkinter import filedialog, scrolledtext
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


# ------------------------------------------------------------
#  TABELA DE TRADUÇÃO DOS FERIADOS
# ------------------------------------------------------------
TRADUCOES_FERIADOS = {
    "New Year's Day": "Ano Novo",
    "Carnival": "Carnaval",
    "Good Friday": "Sexta-Feira Santa",
    "Tiradentes Day": "Dia de Tiradentes",
    "Labour Day": "Dia do Trabalho",
    "Corpus Christi": "Corpus Christi",
    "Independence Day": "Dia da Independência",
    "Our Lady of Aparecida": "Nossa Senhora Aparecida",
    "All Souls' Day": "Dia de Finados",
    "Proclamation of the Republic": "Proclamação da República",
    "Christmas Day": "Natal",
    "Black Awareness Day": "Dia da Consciência Negra",
    "Revolution Day": "Dia da Revolução Constitucionalista",
    "State Holiday": "Feriado Estadual",
}


# ------------------------------------------------------------
# Função que devolve o nome do feriado traduzido
# ------------------------------------------------------------
def identificar_feriado(data_iso, feriados_lista):
    for feriado in feriados_lista:
        if feriado["date"] == data_iso:
            nome_original = feriado["name"]
            return TRADUCOES_FERIADOS.get(nome_original, nome_original)
    return None


# ------------------------------------------------------------
# Busca a lista COMPLETA de feriados do ano
# ------------------------------------------------------------
def buscar_feriados(ano):
    url = f"https://date.nager.at/api/v3/PublicHolidays/{ano}/BR"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


# ------------------------------------------------------------
# Sistema principal de leitura do PDF e análise das datas
# ------------------------------------------------------------
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

    anos = {int(data[:4]) for data in datas_encontradas}

    # Baixa os feriados de cada ano encontrado
    feriados_por_ano = {ano: buscar_feriados(ano) for ano in anos}

    resultados = "Datas Encontradas e Status de Feriado:\n\n"
    feriados_encontrados = []

    for data_str in datas_encontradas:
        ano = int(data_str[:4])
        feriado = identificar_feriado(data_str, feriados_por_ano[ano])

        if feriado:
            resultados += f"{data_str} - É FERIADO: {feriado}\n"
            feriados_encontrados.append(data_str)
        else:
            resultados += f"{data_str} - Não é feriado.\n"

    resultados += (
        f"\n--- RESUMO ---\n"
        f"Total de datas únicas encontradas: {len(datas_encontradas)}\n"
        f"Total de feriados encontrados: {len(feriados_encontrados)}\n"
    )

    exibir_resultados("Resultado da Verificação de Feriados", resultados)


# ------------------------------------------------------------
# JANELA PRINCIPAL
# ------------------------------------------------------------
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
