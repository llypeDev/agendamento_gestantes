from flask import Flask, render_template, request, redirect, flash, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "sua_chave_secreta_aqui"  # Altere para uma chave segura

HORARIOS_DISPONIVEIS = [
    "08:00", "08:45", "09:30", "10:15", "11:00", "11:45",
    "12:30", "13:15", "14:00", "14:45", "15:30", "16:15",
    "17:00", "17:45", "18:30"
]

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "senha123"  # Altere para uma senha segura

def init_db():
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        # Drop tabelas existentes para garantir recriação limpa
        c.execute("DROP TABLE IF EXISTS agendamentos")
        c.execute("DROP TABLE IF EXISTS gestantes")
        # Criar tabela de gestantes
        c.execute('''CREATE TABLE gestantes
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      nome TEXT NOT NULL,
                      setor TEXT NOT NULL,
                      matricula TEXT NOT NULL UNIQUE,
                      username TEXT NOT NULL UNIQUE,
                      password TEXT NOT NULL)''')
        # Criar tabela de agendamentos com gestante_id
        c.execute('''CREATE TABLE agendamentos
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      gestante_id INTEGER NOT NULL,
                      data TEXT NOT NULL,
                      horario1 TEXT NOT NULL,
                      horario2 TEXT NOT NULL,
                      FOREIGN KEY (gestante_id) REFERENCES gestantes(id))''')
        conn.commit()

def get_horarios_ocupados(data):
    try:
        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute("SELECT horario1, horario2 FROM agendamentos WHERE data = ?", (data,))
            agendamentos = c.fetchall()
            return [horario for agendamento in agendamentos for horario in (agendamento[0], agendamento[1])]
    except sqlite3.Error:
        return []

def is_admin_logged_in():
    return session.get("admin_logged_in", False)

def is_gestante_logged_in():
    return session.get("gestante_id") is not None

@app.route("/", methods=["GET", "POST"])
def index():
    hoje = datetime.now().strftime("%Y-%m-%d")
    data_selecionada = request.args.get("data", hoje)

    if request.method == "POST":
        if not is_gestante_logged_in():
            flash("Você precisa estar logada para agendar!", "error")
            return redirect(url_for("gestante_login"))

        gestante_id = session["gestante_id"]
        data = request.form.get("data", "")
        horario1 = request.form.get("horario1", "")
        horario2 = request.form.get("horario2", "")

        if not all([data, horario1, horario2]):
            flash("Todos os campos são obrigatórios!", "error")
            return redirect(url_for("index", data=data_selecionada))

        if horario1 == horario2:
            flash("Os horários devem ser diferentes!", "error")
            return redirect(url_for("index", data=data_selecionada))

        try:
            with sqlite3.connect("database.db") as conn:
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM agendamentos WHERE gestante_id = ? AND data = ?", (gestante_id, data))
                if c.fetchone()[0] >= 1:
                    flash(f"Você já agendou o máximo de 2 horários para {data}!", "error")
                    return redirect(url_for("index", data=data_selecionada))

                horarios_ocupados = get_horarios_ocupados(data)
                if horario1 in horarios_ocupados or horario2 in horarios_ocupados:
                    flash("Um ou mais horários já estão reservados!", "error")
                    return redirect(url_for("index", data=data_selecionada))

                c.execute("INSERT INTO agendamentos (gestante_id, data, horario1, horario2) VALUES (?, ?, ?, ?)",
                          (gestante_id, data, horario1, horario2))
                conn.commit()
                flash("Agendamento realizado com sucesso!", "success")

        except sqlite3.Error as e:
            flash(f"Erro ao salvar o agendamento: {e}", "error")

        return redirect(url_for("index", data=data))

    try:
        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute("SELECT g.nome, a.horario1, a.horario2 FROM agendamentos a JOIN gestantes g ON a.gestante_id = g.id WHERE a.data = ?", (data_selecionada,))
            agendamentos = c.fetchall()
    except sqlite3.Error as e:
        flash(f"Erro ao carregar agendamentos: {e}", "error")
        agendamentos = []

    horarios_ocupados = get_horarios_ocupados(data_selecionada)
    return render_template("index.html", 
                           horarios=HORARIOS_DISPONIVEIS, 
                           agendamentos=agendamentos, 
                           hoje=hoje, 
                           data_selecionada=data_selecionada, 
                           horarios_ocupados=horarios_ocupados,
                           is_logged_in=is_gestante_logged_in())

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("admin"))
        else:
            flash("Credenciais inválidas!", "error")
    return render_template("login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    flash("Você saiu da área administrativa.", "success")
    return redirect(url_for("index"))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not is_admin_logged_in():
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        action = request.form.get("action")
        if action == "delete_agendamento":
            agendamento_id = request.form.get("id")
            try:
                with sqlite3.connect("database.db") as conn:
                    c = conn.cursor()
                    c.execute("DELETE FROM agendamentos WHERE id = ?", (agendamento_id,))
                    conn.commit()
                    flash("Agendamento excluído com sucesso!", "success")
            except sqlite3.Error as e:
                flash(f"Erro ao gerenciar agendamento: {e}", "error")
        elif action == "register_gestante":
            nome = request.form.get("nome")
            setor = request.form.get("setor")
            matricula = request.form.get("matricula")
            username = request.form.get("username")
            password = request.form.get("password")
            
            if not all([nome, setor, matricula, username, password]):
                flash("Todos os campos são obrigatórios!", "error")
            else:
                try:
                    with sqlite3.connect("database.db") as conn:
                        c = conn.cursor()
                        c.execute("INSERT INTO gestantes (nome, setor, matricula, username, password) VALUES (?, ?, ?, ?, ?)",
                                  (nome, setor, matricula, username, password))
                        conn.commit()
                        flash("Gestante cadastrada com sucesso!", "success")
                except sqlite3.IntegrityError:
                    flash("Matrícula ou nome de usuário já existe!", "error")
                except sqlite3.Error as e:
                    flash(f"Erro ao cadastrar gestante: {e}", "error")
        elif action == "delete_gestante":
            gestante_id = request.form.get("id")
            try:
                with sqlite3.connect("database.db") as conn:
                    c = conn.cursor()
                    # Exclui agendamentos associados primeiro devido à chave estrangeira
                    c.execute("DELETE FROM agendamentos WHERE gestante_id = ?", (gestante_id,))
                    c.execute("DELETE FROM gestantes WHERE id = ?", (gestante_id,))
                    conn.commit()
                    flash("Gestante excluída com sucesso!", "success")
            except sqlite3.Error as e:
                flash(f"Erro ao excluir gestante: {e}", "error")
        return redirect(url_for("admin"))

    try:
        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute("SELECT a.id, g.nome, a.data, a.horario1, a.horario2 FROM agendamentos a JOIN gestantes g ON a.gestante_id = g.id ORDER BY a.data")
            agendamentos = c.fetchall()
            c.execute("SELECT id, nome, setor, matricula, username FROM gestantes")
            gestantes = c.fetchall()
    except sqlite3.Error as e:
        flash(f"Erro ao carregar dados: {e}", "error")
        agendamentos = []
        gestantes = []

    return render_template("admin.html", agendamentos=agendamentos, gestantes=gestantes)

@app.route("/admin/edit_gestante/<int:gestante_id>", methods=["GET", "POST"])
def admin_edit_gestante(gestante_id):
    if not is_admin_logged_in():
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        nome = request.form.get("nome")
        setor = request.form.get("setor")
        matricula = request.form.get("matricula")
        username = request.form.get("username")
        password = request.form.get("password")

        if not all([nome, setor, matricula, username, password]):
            flash("Todos os campos são obrigatórios!", "error")
        else:
            try:
                with sqlite3.connect("database.db") as conn:
                    c = conn.cursor()
                    c.execute("UPDATE gestantes SET nome = ?, setor = ?, matricula = ?, username = ?, password = ? WHERE id = ?",
                              (nome, setor, matricula, username, password, gestante_id))
                    conn.commit()
                    flash("Gestante atualizada com sucesso!", "success")
            except sqlite3.IntegrityError:
                flash("Matrícula ou nome de usuário já existe!", "error")
            except sqlite3.Error as e:
                flash(f"Erro ao atualizar gestante: {e}", "error")
        return redirect(url_for("admin"))

    try:
        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute("SELECT nome, setor, matricula, username, password FROM gestantes WHERE id = ?", (gestante_id,))
            gestante = c.fetchone()
            if not gestante:
                flash("Gestante não encontrada!", "error")
                return redirect(url_for("admin"))
    except sqlite3.Error as e:
        flash(f"Erro ao carregar gestante: {e}", "error")
        return redirect(url_for("admin"))

    return render_template("gestante_edit_gestante.html", gestante=gestante, gestante_id=gestante_id)

@app.route("/gestante/login", methods=["GET", "POST"])
def gestante_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        try:
            with sqlite3.connect("database.db") as conn:
                c = conn.cursor()
                c.execute("SELECT id FROM gestantes WHERE username = ? AND password = ?", (username, password))
                gestante = c.fetchone()
                if gestante:
                    session["gestante_id"] = gestante[0]
                    flash("Login realizado com sucesso!", "success")
                    return redirect(url_for("index"))
                else:
                    flash("Credenciais inválidas!", "error")
        except sqlite3.Error as e:
            flash(f"Erro ao realizar login: {e}", "error")
    return render_template("gestante_login.html")

@app.route("/gestante/logout")
def gestante_logout():
    session.pop("gestante_id", None)
    flash("Você saiu da sua conta.", "success")
    return redirect(url_for("index"))

@app.route("/gestante/edit", methods=["GET", "POST"])
def gestante_edit():
    if not is_gestante_logged_in():
        return redirect(url_for("gestante_login"))

    gestante_id = session["gestante_id"]
    hoje = datetime.now().strftime("%Y-%m-%d")
    data_selecionada = request.args.get("data", hoje)

    if request.method == "POST":
        action = request.form.get("action")
        if action == "edit":
            agendamento_id = request.form.get("agendamento_id")
            data = request.form.get("data")
            horario1 = request.form.get("horario1")
            horario2 = request.form.get("horario2")

            if not all([agendamento_id, data, horario1, horario2]):
                flash("Todos os campos são obrigatórios!", "error")
                return redirect(url_for("gestante_edit", data=data_selecionada))

            if horario1 == horario2:
                flash("Os horários devem ser diferentes!", "error")
                return redirect(url_for("gestante_edit", data=data_selecionada))

            try:
                with sqlite3.connect("database.db") as conn:
                    c = conn.cursor()
                    c.execute("SELECT COUNT(*) FROM agendamentos WHERE id = ? AND gestante_id = ?", (agendamento_id, gestante_id))
                    if c.fetchone()[0] == 0:
                        flash("Você só pode editar seus próprios agendamentos!", "error")
                        return redirect(url_for("gestante_edit", data=data_selecionada))

                    horarios_ocupados = get_horarios_ocupados(data)
                    c.execute("SELECT horario1, horario2 FROM agendamentos WHERE id = ?", (agendamento_id,))
                    current_horarios = c.fetchone()
                    horarios_ocupados = [h for h in horarios_ocupados if h not in current_horarios]

                    if horario1 in horarios_ocupados or horario2 in horarios_ocupados:
                        flash("Um ou mais horários já estão reservados!", "error")
                        return redirect(url_for("gestante_edit", data=data_selecionada))

                    c.execute("UPDATE agendamentos SET data = ?, horario1 = ?, horario2 = ? WHERE id = ?",
                              (data, horario1, horario2, agendamento_id))
                    conn.commit()
                    flash("Horário atualizado com sucesso!", "success")
            except sqlite3.Error as e:
                flash(f"Erro ao atualizar horário: {e}", "error")
            return redirect(url_for("gestante_edit", data=data_selecionada))

        elif action == "delete":
            agendamento_id = request.form.get("agendamento_id")
            try:
                with sqlite3.connect("database.db") as conn:
                    c = conn.cursor()
                    c.execute("SELECT COUNT(*) FROM agendamentos WHERE id = ? AND gestante_id = ?", (agendamento_id, gestante_id))
                    if c.fetchone()[0] == 0:
                        flash("Você só pode excluir seus próprios agendamentos!", "error")
                        return redirect(url_for("gestante_edit", data=data_selecionada))

                    c.execute("DELETE FROM agendamentos WHERE id = ?", (agendamento_id,))
                    conn.commit()
                    flash("Agendamento excluído com sucesso!", "success")
            except sqlite3.Error as e:
                flash(f"Erro ao excluir agendamento: {e}", "error")
            return redirect(url_for("gestante_edit", data=data_selecionada))

    try:
        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute("SELECT id, data, horario1, horario2 FROM agendamentos WHERE gestante_id = ? AND data >= ? ORDER BY data",
                      (gestante_id, hoje))
            agendamentos = c.fetchall()
            c.execute("SELECT nome FROM gestantes WHERE id = ?", (gestante_id,))
            gestante_nome = c.fetchone()[0]
    except sqlite3.Error as e:
        flash(f"Erro ao carregar agendamentos: {e}", "error")
        agendamentos = []
        gestante_nome = "Usuário"

    horarios_ocupados = get_horarios_ocupados(data_selecionada)
    return render_template("gestante_edit.html", 
                           agendamentos=agendamentos,
                           horarios=HORARIOS_DISPONIVEIS,
                           hoje=hoje,
                           data_selecionada=data_selecionada,
                           horarios_ocupados=horarios_ocupados,
                           gestante_nome=gestante_nome)

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)