from flask import Flask, render_template, request, redirect, send_file, session
import sqlite3
from openpyxl import Workbook

app = Flask(__name__)

app.secret_key = "sanwar_secret_key"


# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")


# GALLERY PAGE
@app.route("/gallery")
def gallery():
    return render_template("gallery.html")


# SERVICES PAGE
@app.route("/services")
def services():
    return render_template("services.html")


# CONTACT PAGE
@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form.get("name")
        phone = request.form.get("phone")
        message = request.form.get("message")

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            message TEXT
        )
        """)

        cursor.execute("""
        INSERT INTO inquiries (name, phone, message)
        VALUES (?, ?, ?)
        """, (name, phone, message))

        conn.commit()
        conn.close()

        return redirect("/contact")

    return render_template("contact.html")


# LOGIN PAGE
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # SIMPLE LOGIN
        if username == "admin" and password == "1234":

            session["admin"] = True

            return redirect("/admin")

    return render_template("login.html")


# ADMIN DASHBOARD
@app.route("/admin")
def admin():

    if not session.get("admin"):
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM inquiries")
    inquiries = cursor.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        inquiries=inquiries
    )


# DELETE INQUIRY
@app.route("/delete/<int:id>")
def delete(id):

    if not session.get("admin"):
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM inquiries WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")


# LOGOUT
@app.route("/logout")
def logout():

    session.pop("admin", None)

    return redirect("/login")


# EXPORT TO EXCEL
@app.route("/export")
def export_excel():

    if not session.get("admin"):
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM inquiries")
    inquiries = cursor.fetchall()

    conn.close()

    workbook = Workbook()
    sheet = workbook.active

    sheet.title = "Customer Inquiries"

    sheet.append([
        "ID",
        "Customer Name",
        "Phone Number",
        "Message"
    ])

    for inquiry in inquiries:
        sheet.append(inquiry)

    file_name = "customer_inquiries.xlsx"

    workbook.save(file_name)

    return send_file(
        file_name,
        as_attachment=True,
        download_name=file_name
    )


# RUN APP
if __name__ == "__main__":
    app.run(debug=True)