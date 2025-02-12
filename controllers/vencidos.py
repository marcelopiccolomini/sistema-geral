from datetime import date
import glob
import ntpath
import pandas as pd # type: ignore
from config.google_connect import Connect
from googleapiclient.errors import HttpError # type: ignore
import csv
import logging

# Configuração do logging
logging.basicConfig(
    filename='/root/sistema-geral/vencidos.log',  # Arquivo de log
    level=logging.INFO,        # Nível de log (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class Vencidos():

    def vencidos(files): 
        pd.options.mode.copy_on_write = True
        today = date.today()
        hoje = today.strftime("%d/%m/%Y")
        service = Connect.connect()
        sheet = service.spreadsheets()
        spreadsheetId='10LcJ7ubudB-bbujyWwysBMd3IdwgJrv-GnBF0MkaiLE'
        range='Vencidos!A:K'
        result = sheet.values().get(spreadsheetId=spreadsheetId, range=range).execute()
        values = result.get('values', [])
        if not values:
            logging.warning('Nenhum dado encontrado na planilha.')
        else:
            logging.info(f'{len(values)} linhas carregadas da planilha.')
            dfg = pd.DataFrame(values[1:], columns=values[0][0:12])
        dfa = pd.DataFrame()
        dfa = dfg.loc[(dfg['status'].isin(['Pago/Baixado','PROTESTADO', 'Expirado']))]
        exclude = dfa['Nro boleto'].to_numpy().tolist()
        status = []
        for n in glob.glob(files):
            _, tail = ntpath.split(n)
            with open("/root/sistema-geral/pedidoRep1.csv", "r") as f:
                reader = csv.reader(f, delimiter=";")
                for i, line in enumerate(reader):
                    if line[0].upper().replace('_',' ') in tail.upper().replace('_',' '):
                        origem = line[0]
                        status.append(origem)
                        dfv = pd.read_csv(n, sep=';', header=None)
                        dfv.columns = ['carteira','variacao','Vencimento', 'Nome do Pagador', 'Nosso numero', 'Nro boleto', 'Valor titulo', '0']
                        dfv['Valor titulo'] = dfv['Valor titulo']/100
                        dfv['Vencimento'] = dfv['Vencimento'].astype('str').str.zfill(8)
                        dfv['Vencimento'] = pd.to_datetime(dfv['Vencimento'], format='%d%m%Y').dt.strftime('%d/%m/%Y')
                        dfv['origem'] = origem
                        dfv['Nro boleto'] = dfv['Nro boleto'].astype(str).str.zfill(10)
                        df = dfv
                        if origem == "BB WLA":
                            df['NF'] = df['Nro boleto']
                            df7 = df[df['Nro boleto'].str.contains(" ", na=False)]
                            df8 = df[~df['Nro boleto'].str.contains(" ", na=False)]
                            df7['NF'] = df7['NF'].str.slice(0, -2)
                            df = pd.concat([df7,df8])
                            df['NF'] = df['NF'].str.replace(r'\D+', '', regex=True).astype('int')
                        else:
                            df['NF'] = df['Nro boleto'].str.replace(r'\D+', '', regex=True).astype('int')

                        dfn = dfg.loc[(dfg['origem']==origem)&(~dfg['status'].isin(['Pago/Baixado','PROTESTADO','Expirado']))]
                        dfn['Nro boleto'] = dfn['Nro boleto'].str.zfill(10)
                        df2 = dfn.merge(df,on=['Nro boleto'],how='outer')
                        dfn = df2.loc[(df2['Vencimento_x'].isnull())&(df2['Vencimento_y'].notnull())]
                        dfn['status'] = 'NOVO'
                        dfp = df2.loc[(df2['Vencimento_y'].isnull())]
                        dfp['status'] = 'Pago/Baixado'
                        dfp['Data Pgto'] = hoje
                        dfold = df2.loc[((df2['Vencimento_x'].notnull())&(df2['Vencimento_y'].notnull()))]
                        dfold['status'] = 'Sem alteracao'
                        dfp.columns = dfp.columns.str.rstrip('_x')
                        dfn.columns = dfn.columns.str.rstrip('_y')
                        dfold.columns = dfold.columns.str.rstrip('_y')
                        dfs1 = dfold[['Vencimento', 'Nome do Pagador', 'Representante', 'Nro boleto', 'NF', 'Pedido' ,'Valor titulo', 'origem', 'status', 'Obs','Data Pgto']]
                        dfn1 = dfn[['Vencimento', 'Nome do Pagador', 'Representante', 'Nro boleto', 'NF', 'Pedido' ,'Valor titulo', 'origem', 'status', 'Obs','Data Pgto']]
                        dfp1 = dfp[['Vencimento', 'Nome do Pagador', 'Representante', 'Nro boleto', 'NF', 'Pedido' ,'Valor titulo', 'origem', 'status', 'Obs','Data Pgto']]
                        dfFinal = pd.concat([dfn1,dfp1,dfs1])
                        spreadsheetId=line[1]
                        range=line[2]
                        result = sheet.values().get(spreadsheetId=spreadsheetId, range=range).execute()
                        values = result.get('values', [])
                        if not values:
                                print('No data found.')
                        else:
                            df1 = pd.DataFrame(values[1:], columns=values[0])
                        dfrep = dfFinal.loc[dfFinal['Representante'].isnull()]
                        df3 = dfFinal.loc[dfFinal['Representante'].notnull()]
                        col = df1.columns.values
                        df1['NF'] = df1[col[len(col)-1]].apply(pd.to_numeric, errors='coerce').fillna(True).astype('int')
                        dfrep['NF'] = dfrep[['NF']].apply(pd.to_numeric, errors='coerce').fillna(True).astype('int')
                        dft = dfrep.merge(df1,on=['NF'],how='left')
                        dft['Pedido'] = dft['PEDIDO']
                        dft['Representante']=dft[col[len(col)-2]]
                        dff = dft[['Vencimento', 'Nome do Pagador', 'Representante', 'Nro boleto', 'NF', 'Pedido' ,'Valor titulo', 'origem', 'status', 'Obs','Data Pgto']]
                        df3.columns = df3.columns.str.rstrip(' ')
                        dff = pd.concat([df3,dff])
                        dff.drop_duplicates()     
                    
                dfpr = dfa.loc[dfa['status']=='PROTESTADO']
                df = dff.loc[~dff['Nro boleto'].isin(dfpr['Nro boleto'].to_numpy().tolist())]
                df.columns = df.columns.str.rstrip(' ')
                dfa.columns = dfa.columns.str.rstrip(' ')
                dfa = pd.concat([dfa,df])
                dfa = dfa.fillna('')
                dfa.drop_duplicates()
                df_rows = dfa.to_numpy().tolist()
                val = []
                val.append(list(dfa.columns))
                for row in df_rows:
                    val.append(row)
                #dfa.to_csv('/root/sistema-geral/teste.csv', sep=';', index=False)
                try:
                   result = sheet.values().update(
                               spreadsheetId='10LcJ7ubudB-bbujyWwysBMd3IdwgJrv-GnBF0MkaiLE', range='1Vencidos!A:K',
                               valueInputOption="USER_ENTERED", body={'values':val}, ).execute()
                except HttpError as error:
                   logging.error(f"Erro ao acessar Google Sheets: {error}")
        return status