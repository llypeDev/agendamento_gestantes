from flask import Flask, render_template, request, redirect, flash, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "sua_chave_secreta_aqui"  # Altere para uma chave segura

# Horários disponíveis em intervalos de 45 minutos
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
        c.execute('''CREATE TABLE IF NOT EXISTS agendamentos
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      gestante TEXT NOT NULL,
                      data TEXT NOT NULL,
                      horario1 TEXT NOT NULL,
                      horario2 TEXT NOT NULL)''')
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

@app.route("/", methods=["GET", "POST"])
def index():
    hoje = datetime.now().strftime("%Y-%m-%d")
    data_selecionada = request.args.get("data", hoje)

    if request.method == "POST":
        gestante = request.form.get("gestante", "").strip()
        data = request.form.get("data", "")
        horario1 = request.form.get("horario1", "")
        horario2 = request.form.get("horario2", "")

        if not all([gestante, data, horario1, horario2]):
            flash("Todos os campos são obrigatórios!", "error")
            return redirect(url_for("index", data=data_selecionada))

        if horario1 == horario2:
            flash("Os horários devem ser diferentes!", "error")
            return redirect(url_for("index", data=data_selecionada))

        try:
            with sqlite3.connect("database.db") as conn:
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM agendamentos WHERE gestante = ? AND data = ?", (gestante, data))
                if c.fetchone()[0] >= 1:
                    flash(f"Você já agendou o máximo de 2 horários para {data}!", "error")
                    return redirect(url_for("index", data=data_selecionada))

                horarios_ocupados = get_horarios_ocupados(data)
                if horario1 in horarios_ocupados or horario2 in horarios_ocupados:
                    flash("Um ou mais horários já estão reservados!", "error")
                    return redirect(url_for("index", data=data_selecionada))

                c.execute("INSERT INTO agendamentos (gestante, data, horario1, horario2) VALUES (?, ?, ?, ?)",
                          (gestante, data, horario1, horario2))
                conn.commit()
                flash("Agendamento realizado com sucesso!", "success")

        except sqlite3.Error as e:
            flash(f"Erro ao salvar o agendamento: {e}", "error")

        return redirect(url_for("index", data=data))

    try:
        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute("SELECT gestante, horario1, horario2 FROM agendamentos WHERE data = ?", (data_selecionada,))
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
                           horarios_ocupados=horarios_ocupados)

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
        agendamento_id = request.form.get("id")
        try:
            with sqlite3.connect("database.db") as conn:
                c = conn.cursor()
                if action == "delete":
                    c.execute("DELETE FROM agendamentos WHERE id = ?", (agendamento_id,))
                    conn.commit()
                    flash("Agendamento excluído com sucesso!", "success")
        except sqlite3.Error as e:
            flash(f"Erro ao gerenciar agendamento: {e}", "error")
        return redirect(url_for("admin"))

    try:
        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute("SELECT id, gestante, data, horario1, horario2 FROM agendamentos ORDER BY data")
            agendamentos = c.fetchall()
    except sqlite3.Error as e:
        flash(f"Erro ao carregar agendamentos: {e}", "error")
        agendamentos = []

    return render_template("admin.html", agendamentos=agendamentos)

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)