from config.mysql_connect import create_connection, close_connection
from datetime import datetime
class DeleteContasController():
    def del_conta(id, request):
        
        con = create_connection()
        cur = con.cursor()
        cur.execute("SELECT * FROM contas_pagar WHERE id = %s", (id,))
        record = cur.fetchone()
        cur.execute("DELETE FROM contas_pagar WHERE id = %s", (id,))
        con.commit()
        # Registrar log da operação
        detalhes = f"Registro: {record}"

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
        return query_params, detalhes
    def del_contas(request):
        record_ids = request.form['record_ids1']
        record_ids = record_ids.split(',')
        con = create_connection()
        cur = con.cursor()
        cur.execute("SELECT * FROM contas_pagar WHERE id IN (%s)" % ','.join(['%s'] * len(record_ids)), tuple(record_ids))
        record = cur.fetchall()
        cur.execute("DELETE FROM contas_pagar WHERE id IN (%s)" % ','.join(['%s'] * len(record_ids)), tuple(record_ids))
        con.commit()
        # Registrar log da operação
        detalhes = f"Registro: {record}"
        close_connection(con)
        detalhes = f"Ids alterados: {record_ids}"
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
        return query_params, detalhes