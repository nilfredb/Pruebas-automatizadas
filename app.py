from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = "super_secret_key"
DB_NAME = "database.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Todos los campos son obligatorios.", "error")
            return render_template("login.html")

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email, password)
        ).fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["user_email"] = user["email"]
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Credenciales inválidas.", "error")

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    if "user_email" not in session:
        return redirect(url_for("login"))
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("dashboard.html", tasks=tasks)


@app.route("/tasks/create", methods=["GET", "POST"])
@login_required
def create_task():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()

        if not title:
            flash("El título es obligatorio.", "error")
            return render_template("create_task.html")

        if len(title) > 100:
            flash("El título no puede tener más de 100 caracteres.", "error")
            return render_template("create_task.html")

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO tasks (title, description) VALUES (?, ?)",
            (title, description)
        )
        conn.commit()
        conn.close()

        flash("Tarea creada correctamente.", "success")
        return redirect(url_for("dashboard"))

    return render_template("create_task.html")


@app.route("/tasks/edit/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    if "user_email" not in session:
        return redirect(url_for("login"))
    conn = get_db_connection()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()

    if not task:
        conn.close()
        flash("La tarea no existe.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()

        if not title:
            conn.close()
            flash("El título es obligatorio.", "error")
            return render_template("edit_task.html", task=task)

        if len(title) > 100:
            conn.close()
            flash("El título no puede tener más de 100 caracteres.", "error")
            return render_template("edit_task.html", task=task)

        conn.execute(
            "UPDATE tasks SET title = ?, description = ? WHERE id = ?",
            (title, description, task_id)
        )
        conn.commit()
        conn.close()

        flash("Tarea actualizada correctamente.", "success")
        return redirect(url_for("dashboard"))

    conn.close()
    return render_template("edit_task.html", task=task)


@app.route("/tasks/delete/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
    conn = get_db_connection()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()

    if not task:
        conn.close()
        flash("La tarea no existe.", "error")
        return redirect(url_for("dashboard"))

    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    flash("Tarea eliminada correctamente.", "success")
    return redirect(url_for("dashboard"))


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)