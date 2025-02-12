import glob
import re
import numpy as np
import pandas as pd
from tabula import read_pdf
import ntpath
import os
from datetime import date
from pypdf import PdfReader as PdfReader2
from src.config.google_connect import Connect

class ExtractPdf:
    def __init__(self) -> None:
        pass
    
    def extract(path):
        today = date.today()
        d1 = today.strftime("%d/%m/%Y")
        df4 = pd.DataFrame()
        arquivos = []
        for file in glob.glob(path+"\Vencidos*"):
            if 'BB' in file:
                arquivos.append(file)
                df2 = pd.DataFrame()
                reader = PdfReader2(file)
                n = len(reader.pages)
                r = np.arange(1, n+1)
                for i in r:
                    if i==1:
                        dfs = read_pdf(file,pages=1)
                        list1=[]
                        for item in dfs:
                            for info in item.values:
                                list1.append(info)
                        df1 = pd.DataFrame(list1)
                        _, tail = ntpath.split(file)
                        df1.to_csv(file[0:-3]+'csv', index=False,encoding='ISO-8859-1')
                        df2 = pd.read_csv(file[0:-3]+'csv', skiprows=2,encoding='ISO-8859-1')
                        os.remove(file[0:-3]+'csv')
                        df2 = df2.rename(columns={'Valor título': 'Valor titulo', 'Nro beneficiário': 'Nro beneficiario', 'Nosso número': 'Nosso numero'})
                        df2['dt_valid'] = df2['Vencimento'].astype(str).str.contains('/', na=False, case=False)
                        df2 = df2[(df2.dt_valid == True)]
                        df2['NF'] = df2['Nro beneficiario'].astype(str).str.replace(r'[^0-9]+', '', regex=True)
                        df2['origem'] = tail[0:-4]
                    else:
                        allin = []
                        try: 
                            table = read_pdf(file, pages=int(i),output_format='json')
                            top = table[0]["top"]
                            left = table[0]["left"]
                            bottom = table[0]["height"] + top
                            _ = table[0]["width"] + left                           
                            table = read_pdf(file, pages=int(i),multiple_tables=True,
                                        silent=True,guess=True,stream=True,area = [0, 0, bottom, 1100],
                                        pandas_options={'header': None})[0]
                        except:
                            break
                        allin.append(table)
                        df = pd.DataFrame(None)
                        df = pd.concat(allin)
                        df = df.rename(columns={0: 'Vencimento', 1: 'Nome pagador', 2: 'Nosso numero', 3: 'Nro beneficiario', 4: 'Valor titulo',})
                        df['dt_valid'] = df['Vencimento'].astype(str).str.contains('/', na=False, case=False)
                        df = df[(df.dt_valid == True)]
                        if df.empty:
                            break
                        df['NF'] = df['Nro beneficiario'].astype(str).str.replace(r'[^0-9]+', '', regex=True)
                        df['origem'] = tail[0:-4]
                        df2 = pd.concat([df2,df])
                        
                if df4.empty:
                        df4 = df2
                else:
                    df4 = pd.concat([df4,df2]) 
                
            else:
                arquivos.append(file)
                dfss = pd.read_excel(file, skiprows=9)
                _, tail = ntpath.split(file)
                dfss = dfss.rename(columns={'Pagador': 'Nome pagador', 'Data de Vencim.': 'Vencimento', 
                                        'Valor': 'Valor titulo', 'Seu número': 'Nro beneficiario', 'Nosso número': 'Nosso numero'})
                dfss['dt_valid'] = dfss['Vencimento'].astype(str).str.contains('/', na=False, case=False)
                dfss = dfss[(dfss.dt_valid == True)]
                dfss['NF'] = dfss['Nro beneficiario'].astype(str).str.replace(r'[^0-9]+', '', regex=True)
                dfss['origem'] = tail[0:-4]
                dfss = dfss[['Vencimento','Nome pagador','Nosso numero','Nro beneficiario','Valor titulo','dt_valid','NF','origem']]
                if df4.empty:
                    df4 = dfss
                else:
                    df4 = pd.concat([df4,dfss]) 
        #Relatorio dia anterior
        service = Connect.connect()
        sheet = service.spreadsheets()
        spreadsheetId='10LcJ7ubudB-bbujyWwysBMd3IdwgJrv-GnBF0MkaiLE'
        range='Vencidos!A:L'
        result = sheet.values().get(spreadsheetId=spreadsheetId, range=range).execute()
        values = result.get('values', [])
        if not values:
                print('No data found.')
        else:
            df_old = pd.DataFrame(values)
            col = ['Vencimento','Nome pagador','Representante','Nro beneficiario','NF','Valor titulo','origem','status','Obs','Pagamento','Dias em atraso','Região']
            df_old.columns = col
            df_old.drop(df_old.index[0], inplace=True)
        df4['NF'] = df4['NF'].astype(float)
        df_old['NF'] = df_old['NF'].astype(float)
        df4['Nro beneficiario'] = df4['Nro beneficiario'].astype(str)
        df_old['Nro beneficiario'] = df_old['Nro beneficiario'].astype(str)
        df_old['Nro beneficiario'] = df_old['Nro beneficiario'].apply(lambda x: re.sub(r'\s', '', x))
        df4['Nro beneficiario'] = df4['Nro beneficiario'].apply(lambda x: re.sub(r'\s', '', x))
        df_old['Nro beneficiario'] = df_old['Nro beneficiario'].str.replace('.','',regex=True)
        df4['Nro beneficiario'] = df4['Nro beneficiario'].str.replace('.','',regex=True)
        df3 = df_old.merge(df4,on='Nro beneficiario',how='outer')
        dfd = df3.copy()
        dfd['Dias em atraso'] = dfd['Dias em atraso'].fillna(0)
        dfd['Pagamento'] = dfd['Pagamento'].fillna('')
        data = ((dfd['Vencimento_y'].isnull())&(dfd['Pagamento']==''))
        novo = dfd['Vencimento_x'].isnull()
        pago = ((dfd['Vencimento_y'].isnull())&(dfd['Dias em atraso'].astype(int)<360)&(dfd['status']!='PROTESTADO')&(dfd['status']!='Expirado'))
        old = ((dfd['Vencimento_x'].notnull())&(dfd['Vencimento_y'].notnull()))
        dfd.to_excel('Relatorio1.xlsx')
        dfd.loc[data,'Pagamento'] = d1
        dfd.loc[novo,'status'] = 'NOVO'
        dfd.loc[pago,'status'] = 'Pago/Baixado'
        dfd.loc[old,'status'] = 'Sem alteracao'
        
        dfold = dfd.loc[dfd['status']=='Sem alteracao']
        dfn = dfd.loc[dfd['status']=='NOVO']
        dfp = dfd.loc[dfd['status']=='Pago/Baixado']
        dfpr = dfd.loc[dfd['status'].isin(['PROTESTADO','Expirado']) ]
        dfp.columns = dfp.columns.str.rstrip('_x')
        dfn.columns = dfn.columns.str.rstrip('_y')
        dfold.columns = dfold.columns.str.rstrip('_x')
        dfpr.columns = dfpr.columns.str.rstrip('_x')
        dfs = dfold[['Vencimento', 'Nome pagador', 'Representante', 'Nro beneficiario', 'NF', 'Valor titulo', 'origem', 'status','Obs', 'Pagamento']]
        dfn = dfn[['Vencimento', 'Nome pagador', 'Representante', 'Nro beneficiario', 'NF', 'Valor titulo', 'origem', 'status','Obs', 'Pagamento']]
        dfp = dfp[['Vencimento', 'Nome pagador', 'Representante', 'Nro beneficiario', 'NF', 'Valor titulo', 'origem', 'status','Obs', 'Pagamento']]
        dfpr = dfpr[['Vencimento', 'Nome pagador', 'Representante', 'Nro beneficiario', 'NF', 'Valor titulo', 'origem', 'status','Obs', 'Pagamento']]
        
        df = pd.DataFrame(None)
        if dfn.empty:
            df = pd.concat([dfp,dfs,dfpr])
        else:
            df = pd.concat([dfn,dfp,dfs,dfpr])
        df = df.drop_duplicates()
        dfc = df.copy()
        data1 = ((dfc['status']!='Pago/Baixado'))
        dfc.loc[data1,'Pagamento'] = ''
        d1 = today.strftime("%d-%m-%Y")
        dfc.to_excel('Relatorio_Vencidos_'+str(d1)+'.xlsx')
        return arquivos
    
    
