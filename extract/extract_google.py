import pandas as pd
from config.google_connect import Connect

class ExtractGoogle:
     
    def __init__(self) -> None:
        pass
    def extract():
        # Call the Sheets API
        service = Connect.connect()
        sheet = service.spreadsheets()
        df21 = sheet_by_year(sheet,spreadsheetId='1Decn7Fn2kjGHZc7ANbaDTAbI9N-T2XwnwFovd174Pzk', range='2021!A:H')
        df22 = sheet_by_year(sheet,spreadsheetId='1Decn7Fn2kjGHZc7ANbaDTAbI9N-T2XwnwFovd174Pzk', range='2022!A:H')
        df23 = sheet_by_year(sheet,spreadsheetId='1Decn7Fn2kjGHZc7ANbaDTAbI9N-T2XwnwFovd174Pzk', range='2023!A:H')
        df = pd.concat([df23,df22,df21])
        df.to_csv('google.csv',sep=';' ,index=False, encoding='utf8')
        df = df[~df['Rep'].str.contains("SALDO")]
        df2 = pd.read_csv(r'C:\Users\Administrator\Documents\sistema-cobranca\Relatorio_Vencidos.csv',sep=';')
        df['NF'] = df['NF'].astype(float)
        df2['NF'] = df2['NF'].astype(float)
        df4 = pd.merge(df2,df,on='NF',how='left')
        df4['Representante'] = df4['Rep'].astype(str).str.strip()
        df4 = df4[['Vencimento', 'Nome pagador', 'Representante', 'Nro beneficiario', 'NF', 'Valor titulo', 'origem', 'status', 'Pagamento']]
        df4.to_csv('Vencimentos_NA.csv',sep=';' ,index=False, encoding='utf8')
        df3 = pd.merge(df,df2,on='NF',how='left')
        df3['Representante'] = df3['Rep'].astype(str)
        df = df3[['Data', 'Pedido', 'Vendas', 'Cliente', 'Representante','NF', 'Vencimento', 'Valor titulo','origem','Pagamento']]
        df.to_csv('Report_clientes.csv',sep=';' ,index=False, encoding='utf8')

def sheet_by_year(sheet,spreadsheetId,range):
    result = sheet.values().get(spreadsheetId=spreadsheetId, range=range).execute()
    values = result.get('values', [])
    if not values:
            print('No data found.')
    else:
        df = pd.DataFrame(values)
        col = ['Data','Pedido','Vendas','Bonif','Prov','Cliente','Rep','NF']
        df.columns = col
        df.drop(df.index[0], inplace=True) 
        df = df[pd.to_numeric(df['NF'], errors='coerce').notnull()]
        return df
    
    
