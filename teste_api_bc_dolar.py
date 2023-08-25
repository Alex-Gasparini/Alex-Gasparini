import requests
import csv
import pandas as pd
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkcalendar import DateEntry
from tkinter import font
import os

# FORMATA A DATA RECEBIDA P/ PESQUISAR NA API
def format_date(start_date, end_date):
    # Formatar data
    data_start = datetime.strptime(start_date, "%d/%m/%Y")
    data_end   = datetime.strptime(end_date, "%d/%m/%Y")

    data_f_start = data_start.strftime("%m-%d-%Y")
    data_f_end   = data_end.strftime("%m-%d-%Y")
    conect_api_bc(data_f_start, data_f_end)

# CHECAGEM SE ARQUIVO CSV JÁ EXISTE
def check_csv_exists(file_name):
    if os.path.exists(file_name):
        return True
    else:
        return False

# CONECTA API BC
def conect_api_bc(start_date, end_date):

    if start_date and end_date:
        url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@dataInicial='{start_date}'&@dataFinalCotacao='{end_date}'&$top=100&$format=json"
        response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        # DEFINI O NOME DO ARQUIVO
        csv_filename = f"cotacao_dolar_periodo_{start_date}_a_{end_date}.csv"
        
        if check_csv_exists(csv_filename):
            #print(f"O arquivo {csv_filename} já existe.")
            #print(f"Vamos analisar os dados")
            analisar_dados(csv_filename)
        else:
            response = create_csv(data, csv_filename)
            if response:
                analisar_dados(csv_filename)
                #print(f"Vamos analisar os dados")
            else:
                print(f"ERRO")
            
    else:  
        result_label.config(text="Error: Unable to fetch data.")

# CRIA ARQUIVO CSV
def create_csv(data_json, csv_filename):

    header = data_json['value'][0].keys()

    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()

        for entry in data_json['value']:
            writer.writerow(entry)

    if csv_filename:
        return True   
    else:
        return False

# ANALISA OS DADOS
def analisar_dados(csv):
    dados = pd.read_csv(csv)
    dados = dados.dropna()
    dados = dados.drop("dataHoraCotacao", axis=1)
    dados = dados.drop("cotacaoCompra", axis=1)
 
    qtd_dias = len(dados)
    media = dados["cotacaoVenda"].mean()
    # Calcular a variação manualmente
    variacao = dados["cotacaoVenda"].diff() / dados["cotacaoVenda"].shift() * 100
    soma_var = variacao.sum()
    if soma_var < 0:
        result = f"O dólar teve uma queda de: {soma_var:.2f}%"
    else:
        result = f"O dólar teve um aumento de: {soma_var:.2f}%"

    result_label.config(text= f"""
                        Para o periodo de {qtd_dias} dias
                        A média de valor é: R${media:.2f}
                        {result}
                        """)

  
# INTERFACE TKINTER
root = tk.Tk()
root.title("Cotação do Dólar")
root.configure(background="#6495ED")

window_width = 500
window_height = 400
window_geometry = f"{window_width}x{window_height}"
root.geometry(window_geometry)

custom_font = font.Font(family="Garamond", size=15, weight="bold")

start_date_label = tk.Label(root, text="Data inicial", bg="#F5F5F5", font=custom_font)
start_date_label.pack(padx=5, pady=6)
start_date_entry = DateEntry(root, date_pattern="dd/mm/yyyy")
start_date_entry.pack(pady=6)

end_date_label = tk.Label(root, text="Data final", bg="#F5F5F5", font=custom_font)
end_date_label.pack(padx=5, pady=6)
end_date_entry = DateEntry(root, date_pattern="dd/mm/yyyy")
end_date_entry.pack(pady=6)

fetch_button = tk.Button(root, cursor="hand2", text="Enviar", command=lambda: format_date(start_date_entry.get(), end_date_entry.get()), bg="#F0F8FF", font=custom_font)
fetch_button.pack(pady=10)

# RESULTADO
result_label = tk.Label(root, text="", font=custom_font)
result_label.pack(pady=6)

root.mainloop()



    






