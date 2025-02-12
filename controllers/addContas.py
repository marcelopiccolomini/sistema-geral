from config.mysql_connect import create_connection, close_connection
from datetime import datetime
class AddContasController():
   
    def add_contas(request):
        empresa = request.form['empresa']
        origem = request.form['origem']
        data = datetime.strptime(request.form['data'], '%Y-%m-%d')
        valor = request.form['valor']
        formaPgto = request.form['formaPgto']
        tipoConta = request.form['tipo_conta']
        beneficiario = request.form['beneficiario']
        obs = request.form['obs']
        formatacao = request.form['corSelecionada']
        timestamp = datetime.now()
        con = create_connection()
        cur = con.cursor()
        query = """
                    INSERT INTO contas_pagar (empresa, origem, data, valor, formaPgto, tipoConta, beneficiario, nfParc, formatacao, dataCriacao)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
        valores = (empresa, origem, data, formatar_valor(valor), formaPgto, tipoConta, beneficiario, obs, formatacao, timestamp)        
        cur.execute(query, valores)
        con.commit()
        close_connection(con)
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

def formatar_valor(valor):
    """Remove o símbolo "R$", pontos, vírgulas e espaços de uma string de valor monetário."""
    if not isinstance(valor, str):
        raise ValueError("O valor deve ser uma string.")
    valor_limpo = valor.replace("R$", "").replace(".", "").replace(",", ".").replace(" ", "").replace(".", "")
    valor_final = valor_limpo[:-2] + "." + valor_limpo[-2:]
    return float(valor_final)