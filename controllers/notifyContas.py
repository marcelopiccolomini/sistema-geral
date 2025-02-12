from config.mysql_connect import create_connection, close_connection
from datetime import datetime
class NotifyContasController():
    def resolve_conta(id, request):
        
        con = create_connection()
        cur = con.cursor()
        cur.execute("UPDATE notificacao SET status = 1 WHERE idRecord = %s", (id,))
        con.commit()
        con.close()
        query_params = {
        'filter_emp': request.form.getlist('filter_emp'),
        'filter_by': request.form.get('filter_by'),
        'filter_value': request.form.get('filter_value'),
        'start_date': request.form.get('start_date'),
        'end_date': request.form.get('end_date'),
        'sort_by': request.form.get('sort_by'),
        'order': request.form.get('order'),
        'page': request.form.get('page'),
        'page_size': request.form.get('page_size'),
        }
        return query_params
    def send_conta(request):
        record_ids = request.form['record_ids2']
        notificacao = request.form['notificacao']
        username = request.form['username']
        con = create_connection()
        cur = con.cursor()
        query = """
                    INSERT INTO notificacao (descricao, idRecord, username, status, dataCriacao)
                    VALUES (%s, %s, %s, %s, %s)
                """
        valores = (notificacao, record_ids, username, 0, datetime.now())
        cur.execute(query, valores)
        con.commit()
        con.close()
        query_params = {
        'filter_emp': request.form.getlist('filter_emp'),
        'filter_by': request.form.get('filter_by'),
        'filter_value': request.form.get('filter_value'),
        'start_date': request.form.get('start_date'),
        'end_date': request.form.get('end_date'),
        'sort_by': request.form.get('sort_by'),
        'order': request.form.get('order'),
        'page': request.form.get('page'),
        'page_size': request.form.get('page_size'),
        }
        return query_params