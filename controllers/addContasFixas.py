import calendar
from config.mysql_connect import create_connection, close_connection
from datetime import datetime
class AddContasFixasController():
    def add_contas_fixas(mesStart, mesEnd):
        con = create_connection()
        cur = con.cursor(dictionary=True)
        query = f"""
                    SELECT * FROM contas_pagar
                    where month(data) = {mesStart} and origem like 'contas fixas'
                """
        cur.execute(query)
        rows = cur.fetchall()
        con.commit()
        timestamp = datetime.now()
        records = []
        for row in rows:
            record = dict(row)
            record['data'] = ajustar_mes(record['data'],int(mesEnd))
            record['formaPgto'] = ''
            query = """
                    INSERT INTO contas_pagar (empresa, origem, data, valor, formaPgto, tipoConta, beneficiario, nfParc, formatacao, dataCriacao)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
            valores = (record['empresa'],record['origem'],record['data'],record['valor'],record['formaPgto'],record['tipoConta'],record['beneficiario'],record['nfParc'],record['formatacao'], timestamp)        
            cur.execute(query, valores)
            con.commit()
            records.append(record)
        close_connection(con)
        return 'Contas fixas adicionadas com sucesso'
    

# Função para ajustar a data
def ajustar_mes(data, novo_mes):
    # Verifica se o dia existe no novo mês
    ultimo_dia_do_mes = calendar.monthrange(data.year, novo_mes)[1]
    novo_dia = min(data.day, ultimo_dia_do_mes)  # Garante que o dia não ultrapasse o último dia do mês

    # Retorna a nova data com o mês ajustado
    return data.replace(month=novo_mes, day=novo_dia)
