from flask import Flask, request, send_file, render_template, redirect, url_for, session, jsonify, flash
import pandas as pd
from werkzeug.utils import secure_filename
import time
from controllers.changePass import ChangePassController
from controllers.addContasFixas import AddContasFixasController
from controllers import vencidos
from controllers import verbasAcoes
from controllers.login import LoginController
from controllers.addContas import AddContasController
from controllers.editContas import EditContasController
from controllers.delContas import DeleteContasController
from controllers.viewContas import ViewContasController
from config.logs import Logs
import os 

app = Flask(__name__)
LOG_FILE = r"/root/sistema-geral/execution_log.txt"
def save_to_log(process_name, status, start_time, duration):
    """Salva o log de execução em um arquivo."""
    with open(LOG_FILE, "a") as log_file:
        log_file.write(
            f"Processo: {process_name} | Status: {status} | Início: {start_time} | Duração: {duration:.2f} segundos\n"
        )

app.secret_key = 'your_secret_key'  # Replace with your secret key
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = LoginController.login(username)
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['avatar'] = user['avatar']
            return redirect(url_for('home'))
        else:
            flash(f'Nome de usuário ou senha inválidos {user} eeee {request.form}', 'danger')
    return render_template('login.html')

@app.route('/change-password/', methods=['GET', 'POST'])
def change_password():
    # Verifica se o usuário está logado
    if 'user_id' not in session:
        flash('Você precisa estar logado para trocar a senha.', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_password = request.form['password']
        # Obtém o usuário da sessão
        user_id = session['user_id']
        # Altera a senha do usuário
        #ChangePassController.change_pass(user_id, new_password)
        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('login'))        
                
    return render_template('changePassword.html')

@app.route('/')
def home():
    if session:
        return render_template('/home.html')
    else:
        return redirect(url_for('login'))

@app.route('/logoff/')
def logoff():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Você saiu com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/add/', methods=['POST'])
def add_record():
    if request.method == 'POST':
        params, detalhes=AddContasController.add_contas(request)
        # Registrar log da operação
        Logs.logs(session['username'], 'INSERT', 'contas_pagar', detalhes)
    return redirect(url_for('view_records', **params))

@app.route('/edit_record', methods=['POST'])
def edit_record():
    if request.method == 'POST':
        params, detalhes=EditContasController.edit_contas(request)
        # Registrar log da operação
        Logs.logs(session['username'], 'EDIT', 'contas_pagar', detalhes)
    return redirect(url_for('view_records', **params))
    
@app.route('/contasPagar/')
def view_records():
    if session:
        records, total_records, total_pages, page, page_size, filter_emp, filter_by, filter_value, sort_by, order, categorias, tipos_conta_json, total_hj, total_amanha, total_semana, total_mes, total_atraso, filter_card, start_date, end_date = ViewContasController.view_contas(request)
        return render_template(
            'contasPagar.html',
            rows=records,
            sort_by=sort_by,
            order=order,
            filter_by=filter_by,
            filter_emp=filter_emp,
            filter_value=filter_value,
            categorias=categorias,
            tipos_conta=tipos_conta_json,
            total_records=total_records,
            page=page,
            page_size=page_size,
            filter_card=filter_card,
            total_pages=total_pages,
            start_date=start_date,
            end_date=end_date,
            total_hj = total_hj,
            total_amanha = total_amanha,
            total_semana = total_semana,
            total_mes = total_mes,
            total_atraso = total_atraso
        )
    else:
        return redirect(url_for('login'))
    
@app.route('/delete/<int:id>/', methods=['POST'])
def delete_record(id):
    params, detalhes=DeleteContasController.del_conta(id, request)
    Logs.logs(session['username'], 'DELETE', 'contas_pagar', detalhes)
    return redirect(url_for('view_records', **params))

    
@app.route('/delete_records/', methods=['POST'])
def delete_records():
    params, detalhes=DeleteContasController.del_contas(request)
    Logs.logs(session['username'], 'DELETE', 'contas_pagar', detalhes)
    
    return redirect(url_for('view_records', **params))

@app.route('/pay_records/', methods=['POST'])
def pay_records():
    params, detalhes=EditContasController.pay_contas(request)
    # Registrar log da operação
    Logs.logs(session['username'], 'PAGOS', 'contas_pagar', detalhes)
   
    return redirect(url_for('view_records', **params))
    
@app.route('/resolve_notification/<int:id>/', methods=['POST'])
def resolve_notification(id):
    params=NotifyContasController.resolve_conta(request)
    return redirect(url_for('view_records', **params))

    
@app.route('/send_notification/', methods=['POST'])
def send_notification():
    params=NotifyContasController.send_conta(request)
    
    return redirect(url_for('view_records', **params))
    
@app.route('/download/')
def download_records():
    excel_file_path = ViewContasController.download_contas()
    return send_file(excel_file_path, as_attachment=True)

@app.route('/gerenciadorProcessos')
def gerenciadorProcessos():
    if(session):
        return render_template('gerenciadorProcessos.html')
    else:
        return redirect(url_for('login'))
    

@app.route('/start', methods=['POST'])
def start_process():
    try:
        if request.is_json:
            data = request.json
        else:
            data = {}
        process_name = data.get("process") or request.form.get("process", "Processo Desconhecido")
        # Marca o início do processo
        start_time = time.time()
        status = "Falha - Processo não encontrado"

        if process_name == "Vencidos":
            execution_date = request.form.get("executionDate")
            if not execution_date:
                return jsonify({"process": process_name, "status": "Erro - Data de execução não fornecida"}), 400
            
            year, month, day = execution_date.split('-')
            UPLOAD_FOLDER = f'uploads/Vencidos/{day}-{month}-{year}'

            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
            # Ensure the upload folder exists
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            uploaded_files = request.files.getlist('file')  # Obtém a lista de arquivos do formulário

            if not uploaded_files or len(uploaded_files) == 0:
                return jsonify({"status": "Erro - Nenhum arquivo foi enviado"}), 400

            saved_files = []
            for uploaded_file in uploaded_files:
                if uploaded_file.filename == '':
                    continue  # Ignora arquivos sem nome
                filename = secure_filename(uploaded_file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                uploaded_file.save(file_path)
                saved_files.append(file_path)
                print(f"Arquivo salvo em: {file_path}")

            if len(saved_files) == 0:
                return jsonify({"status": "Erro - Nenhum arquivo válido foi enviado"}), 400
            
            directory = rf'/root/sistema-geral/uploads/Vencidos/{day}-{month}-{year}'
            files = rf'{directory}/Vencidos*.bbt'

            if os.path.isdir(directory):
                # Exemplo de execução do processo
                s = vencidos.Vencidos.vencidos(files)
                status = f"Concluído - {s}"
            else:
                status = f"Erro - Diretório {directory} não existe!"
        
        elif process_name == "Verba para Ações":
            UPLOAD_FOLDER = 'uploads'

            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
            # Ensure the upload folder exists
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            uploaded_file = request.files.get('file')
            if not uploaded_file:
                return jsonify({"process": process_name, "status": "Erro - Nenhum arquivo foi enviado"}), 400
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            uploaded_file.save(file_path)
            print(f"Arquivo salvo em: {file_path}")
            df = pd.read_excel(file_path)
            df_rows = df.to_numpy().tolist()
            val = []
            val.append(list(df.columns))
            for row in df_rows:
                val.append(row)
            # Exemplo de execução do processo
            s = file_path  # Chamaria sua função de processo aqui
            status = f"Concluído - {request.files}"
        
        elif process_name == "Contas Fixas":
            # Simula o processo de "Contas Fixas"
            mesStart = request.form.get("mesStart")
            mesEnd = request.form.get("mesEnd")
            s = AddContasFixasController.add_contas_fixas(mesStart, mesEnd)
            status = f"Concluído - {s} para o mês {mesEnd}."
        
        # Calcula o tempo de execução
        duration = time.time() - start_time
        start_time_formatted = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
        save_to_log(process_name, status, start_time_formatted, duration)

    except Exception as e:
        # Tratamento de erros gerais
        duration = time.time() - start_time
        start_time_formatted = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
        status = f"Erro - {str(e)}"
        save_to_log(process_name, status, start_time_formatted, duration)
        return jsonify({"process": process_name, "status": status}), 500

    return jsonify({"process": process_name, "status": status})
if __name__ == '__main__':
    app.run(debug=True)