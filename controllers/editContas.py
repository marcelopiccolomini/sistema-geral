from config.mysql_connect import create_connection, close_connection
from datetime import datetime
class EditContasController():
    def edit_contas(request):
        record_id = request.form['id']
        empresa = request.form['empresa']
        origem = request.form['origem']
        beneficiario = request.form['beneficiario']
        data = datetime.strptime(request.form['data'], '%Y-%m-%d')
        valor = request.form['valor']
        tipoConta = request.form['editTipoConta']
        formaPgto = request.form['formaPgto']
        obs = request.form['obs']
        formatacao = request.form['editCorSelecionada']
        timestamp = datetime.now()
        con = create_connection()
        cur = con.cursor()
        if 'Alterar' in request.form:
            query = """
                UPDATE contas_pagar
                SET empresa = %s, origem = %s, beneficiario = %s, data = %s, valor = %s, formaPgto = %s, nfParc = %s, tipoConta = %s, formatacao = %s
                WHERE id = %s
            """
            valores = (empresa, origem, beneficiario, data, formatar_valor(valor), formaPgto, obs, tipoConta, formatacao, record_id)
            cur.execute(query, valores)
            con.commit()
            # Registrar log da operação
            detalhes = f"ID: {record_id}, Empresa: {empresa}, Origem: {origem}, Valor: {valor}, Beneficiário: {beneficiario}"
        if 'Salvar' in request.form:
            query = """
                INSERT INTO contas_pagar (empresa, origem, data, valor, formaPgto, tipoConta, beneficiario, nfParc, formatacao, dataCriacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (empresa, origem, data, formatar_valor(valor), formaPgto, tipoConta, beneficiario, obs, formatacao, timestamp)
            cur.execute(query, valores)
            con.commit()
            # Registrar log da operação
            detalhes = f"Empresa: {empresa}, Origem: {origem}, Valor: {valor}, Beneficiário: {beneficiario}"

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
    def pay_contas(request):
        record_ids = request.form['record_ids1']
        record_ids = record_ids.split(',')
        con = create_connection()
        cur = con.cursor()
        cur.execute("UPDATE contas_pagar SET formatacao = '#000000' WHERE id IN (%s)" % ','.join(['%s'] * len(record_ids)), tuple(record_ids))
        con.commit()
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
def formatar_valor(valor):
    """Remove o símbolo "R$", pontos, vírgulas e espaços de uma string de valor monetário."""
    if not isinstance(valor, str):
        raise ValueError("O valor deve ser uma string.")
    valor_limpo = valor.replace("R$", "").replace(".", "").replace(",", ".").replace(" ", "").replace(".", "")
    valor_final = valor_limpo[:-2] + "." + valor_limpo[-2:]
    return float(valor_final)