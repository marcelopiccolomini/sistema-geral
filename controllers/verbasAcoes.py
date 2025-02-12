from datetime import date
import calendar
import pandas as pd # type: ignore
from config.google_connect import Connect
from googleapiclient.errors import HttpError
import csv
class VerbasAcoes():

    def verbasAcoes(files): 
        pd.options.mode.copy_on_write = True
        today = date.today()
        hoje = today.strftime("%d/%m/%Y")
        service = Connect.connect()
        sheet = service.spreadsheets()
        with open("planilhas.csv", "r") as f:
                reader = csv.reader(f, delimiter=";")
                for i, line in enumerate(reader):
                    print(line)
                    spreadsheetId=line[1]
                    range='2024!A:I'
                    result = sheet.values().get(spreadsheetId=spreadsheetId, range=range).execute()
                    values = result.get('values', [])
                    if not values:
                            print('No data found.')
                    else:
                        df2 = pd.DataFrame(values[1:], columns=values[0])
                    spreadsheetId=line[1]
                    range='Verba para Ações!D8:H'
                    result = sheet.values().get(spreadsheetId=spreadsheetId, range=range).execute()
                    values = result.get('values', [])
                    if not values:
                            print('No data found.')
                    else:
                        df4 = pd.DataFrame(values[1:], columns=['Data', 'Descrição', 'Tipo Gasto','Total', 'Origem'])
                    
                    dfOld = df4[~df4['Origem'].isin(['Vendas','Contas à pagar'])]
                    dfOld['Descrição'] = dfOld['Descrição'].str.strip()
                    dfOld['Total'] = dfOld['Total'].str.replace('R$', '',regex=False).str.replace('-', '0',regex=False).str.replace('.', '',regex=False).str.replace(',', '.',regex=False).apply(pd.to_numeric, errors='coerce')
                    df1 = pd.read_excel(r"C:\Users\Administrator\Downloads\CONTAS A PAGAR (4).xlsx",skiprows=3, sheet_name=line[0])
                    df1 = df1.loc[df1['TIPO CONTA'].isin(['4.01.01.05.22 - Feiras e Exposições','4.01.01.05.38 - Feiras e Exposições - Hospedagem','4.01.01.05.39 - Feiras e Exposições - Alimentação','4.01.01.05.40 - Feiras e Exposições - Transporte',"4.01.01.03.05 - Uniformes, Vestuários e EPI's",'4.01.01.06.06 - Gastos Relacionados a Comercialização','4.01.01.05.96 - Brindes','4.01.01.05.18 - Propaganda, Publicidade e Patrocínio','4.01.01.06.07 - Móvel Expositor'])]
                    df1 = df1[(df1['DATA VCTO'] > '2024-08-01') & (df1['DATA VCTO'] < '2024-12-31')]
                    df1['TIPO CONTA'] = df1['TIPO CONTA'].str.slice(16, 200)
                    df1['DATA VCTO'] = pd.to_datetime(df1['DATA VCTO'], format='%d%m%Y').dt.strftime('%d/%m/%Y')
                    dfContas = df1[['DATA VCTO','FORNECEDOR','TIPO CONTA','VLR PAGAR']]
                    df2['DATA'] = pd.to_datetime(df2['DATA'], format='%d/%m/%Y', errors='coerce')
                    df2 = df2[(df2['DATA'] > '2024-08-01') & (df2['DATA'] < '2024-12-31')]
                    df2['BONIF.'] = df2['BONIF.'].str.replace(',', '.').apply(pd.to_numeric, errors='coerce')
                    df2['DATA'] = pd.to_datetime(df2['DATA'], format='%d%m%Y').dt.strftime('%d/%m/%Y')
                    dfCd = df2.groupby(['DATA','CLIENTE']).sum().reset_index()
                    dfCd = dfCd.loc[dfCd['BONIF.']>0]
                    dfCd['Tipo'] = 'Bonificação'
                    dfCd['Origem'] = 'Vendas'
                    dfContas['Origem'] = 'Contas à pagar'
                    pd.options.display.float_format = "{:.2f}".format
                    df2 = dfContas.rename(columns={'DATA VCTO': 'Data', 'FORNECEDOR': 'Descrição','TIPO CONTA': 'Tipo Gasto', 'VLR PAGAR': 'Total'})
                    df3 = dfCd[['DATA','CLIENTE','Tipo','BONIF.','Origem']].rename(columns={'DATA': 'Data', 'CLIENTE': 'Descrição','Tipo': 'Tipo Gasto', 'BONIF.': 'Total'})
                    df = pd.concat([df2,df3,dfOld])
                    df = df.fillna('')
                    df1 = df[['Data','Total']][df['Data'].str.contains('/2024', na=False)]
            
                    df1['Data'] = df1['Data'].str.slice(3,5)
                    df1['Total'] = df1['Total'].apply(pd.to_numeric, errors='coerce')
                    df1 = df1.groupby(['Data']).sum().reset_index()
                    
                    df_rows = df1['Total'].to_numpy().tolist()
                    val = []
                    for row in df_rows:
                        val.append([row])
                    
                    try:
                        result = sheet.values().update(
                                    spreadsheetId=line[1], range='Verba para Ações!F3:F7',
                                    valueInputOption="USER_ENTERED", body={'values':val}, ).execute()
                    except HttpError as error:
                        print(f"An error occurred: {error}")
                    
                    df_rows = df.to_numpy().tolist()
                    val = []
                    val.append(['Data','Descrição','Tipo Gasto', 'Total', 'Origem'])
                    for row in df_rows:
                        val.append(row)

                    try:
                        result = sheet.values().update(
                                    spreadsheetId=line[1], range='Verba para Ações!D8:H',
                                    valueInputOption="USER_ENTERED", body={'values':val}, ).execute()
                    except HttpError as error:
                        print(f"An error occurred: {error}")
        return 1