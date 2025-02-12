from .mysql_connect import create_connection, close_connection
from datetime import datetime, date, timedelta
class Logs():

    def logs(usuario, operacao, tabela_afetada, detalhes):
        con = create_connection()
        cur = con.cursor()
        query = """
                INSERT INTO logs_contas_pagar (usuario, operacao, tabela_afetada, detalhes, data_hora)
                VALUES (%s, %s, %s, %s, %s)
            """
        valores = (usuario, operacao, tabela_afetada, detalhes, datetime.now())
        cur.execute(query, valores)
        con.commit()
        close_connection(con)
        