import json
from config.mysql_connect import create_connection, close_connection
from datetime import datetime, date, timedelta
from math import ceil
class ViewContasController():

    def view_contas(request):
        filter_emp = []
        hoje = date.today()
        ontem = hoje - timedelta(days=1)
        ontem_formatado = ontem.strftime('%Y-%m-%d')
        sort_by = request.args.get('sort_by', 'id')
        order = request.args.get('order', 'asc')
        filter_by = request.args.get('filter_by', None)
        filter_value = request.args.get('filter_value', "")
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 50))
        filter_emp = request.args.getlist('filter_emp')
        filter_card = int(request.args.get('icard', 0))
        end_date = request.args.get('end_date',(datetime.today() + timedelta(days=3)).strftime('%Y-%m-%d'))
        start_date = request.args.get('start_date', datetime.today().strftime('%Y-%m-%d'))

        con = create_connection()
        cur = con.cursor(dictionary=True)
        print('Conectado com sucesso!', 'success')

        query = "SELECT a.*, b.categoria FROM contas_pagar a LEFT JOIN tipo_contas b ON a.tipoConta = b.tipo_conta"
        where_clauses = []

        if filter_by and filter_value:
            where_clauses.append(f"{filter_by} LIKE '%{filter_value}%'")
        if filter_card==1:
            page_size = 1000
            where_clauses.append(f"data <= '{ontem_formatado}' AND formatacao <> '#000000'")
        elif filter_card==2:
            page_size = 1000
            where_clauses.append(f"data = CURDATE()")
        elif filter_card==3:
            page_size = 1000
            where_clauses.append(f"data = CURDATE()+1")
        elif filter_card==4:
            page_size = 1000
            where_clauses.append(f"week(data) = week(CURDATE()) and year(data) = year(CURDATE())")
        elif filter_card==5:
            page_size = 1000
            where_clauses.append(f"month(data) = month(CURDATE()) and year(data) = year(CURDATE())")
        else:
            filter_card = 0
            where_clauses.append(f"data BETWEEN '{start_date}' AND '{end_date}'")
        if filter_emp:
            where_clauses.append(f"empresa IN ({str(filter_emp)[1:-1]})")
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += f" ORDER BY {sort_by} {order.upper()}"
        cur.execute(f"SELECT COUNT(*) as total FROM ({query}) as subquery")
        total_records = cur.fetchone()['total']
        total_pages = ceil(total_records / page_size)

        offset = (page - 1) * page_size
        query += f" LIMIT {page_size} OFFSET {offset}"
        cur.execute(query)
        rows = cur.fetchall()
        hoje = " data = CURDATE() and formatacao <> '#000000'"
        query1 = f"select sum(valor) as total from contas_pagar where{hoje}"
        if filter_emp:
            query1 = f"select sum(valor) as total from contas_pagar where empresa IN ({str(filter_emp)[1:-1]}) and{hoje}"
        cur.execute(query1)
        total_hj = cur.fetchone()['total']
        amanha = " data = CURDATE()+1 and formatacao <> '#000000'"
        query1 = f"select sum(valor) as total from contas_pagar where{amanha}"
        if filter_emp:
            query1 = f"select sum(valor) as total from contas_pagar where empresa IN ({str(filter_emp)[1:-1]}) and{amanha}"
        cur.execute(query1)
        total_amanha = cur.fetchone()['total']
        semana = " week(data) = week(CURDATE()) and year(data) = year(CURDATE()) and formatacao <> '#000000'"
        query1 = f"select sum(valor) as total from contas_pagar where{semana}"
        if filter_emp:
            query1 = f"select sum(valor) as total from contas_pagar where empresa IN ({str(filter_emp)[1:-1]}) and{semana}"
        cur.execute(query1)
        total_semana = cur.fetchone()['total']
        mes = " month(data) = month(CURDATE()) and year(data) = year(CURDATE()) and formatacao <> '#000000'"
        query1 = f"select sum(valor) as total from contas_pagar where{mes}"
        if filter_emp:
            query1 = f"select sum(valor) as total from contas_pagar where empresa IN ({str(filter_emp)[1:-1]}) and{mes}"
        cur.execute(query1)
        total_mes = cur.fetchone()['total']
        atraso = """ formatacao <> '#000000' and data BETWEEN (
                            SELECT MIN(data)
                            FROM contas_pagar
                            WHERE data <= CURDATE() - 1
                        ) and CURDATE()-1"""
        query1 = f"select sum(valor) as total from contas_pagar where{atraso}"
        if filter_emp:
            query1 = f"select sum(valor) as total from contas_pagar where empresa IN ({str(filter_emp)[1:-1]}) and{atraso}"
        cur.execute(query1)
        total_atraso = cur.fetchone()['total']
        records = []
        for row in rows:
            record = dict(row)
            if record['data']:
                if isinstance(row['data'], (datetime, date)):
                    record['data'] = row['data'].strftime('%d/%m/%Y')
                else:
                    record['data'] = datetime.strptime(row['data'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
            records.append(record)
        cur.execute("SELECT DISTINCT categoria FROM tipo_contas")
        categorias = [row['categoria'] for row in cur.fetchall()]
        cur.execute("SELECT categoria, tipo_conta FROM tipo_contas")
        tipos_conta = cur.fetchall()
        tipos_conta_json = json.dumps(tipos_conta)
        close_connection(con)
        return records, total_records, total_pages, page, page_size, filter_emp, filter_by, filter_value, sort_by, order, categorias, tipos_conta_json, total_hj, total_amanha, total_semana, total_mes, total_atraso, filter_card, start_date, end_date