from flask import Flask, render_template, request, redirect, session
from db_config import get_connection
from ehr_encryption import encrypt, decrypt
from rbac_utils import has_access

app = Flask(__name__)
app.secret_key = "your_secret_key"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session['user'] = user
            return redirect("/dashboard")
        return "Invalid credentials"
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    if 'user' not in session:
        return redirect("/")
    
    role = session['user']['role']
    if not has_access(role, f"{role}_dashboard"):
        return "Access denied"
    
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    
    if role == 'doctor':
        cur.execute("SELECT * FROM health_records")
        records = cur.fetchall()
        for r in records:
            r['data'] = decrypt(r['data'])
        return render_template("dashboard.html", role=role, records=records)
    
    elif role == 'patient':
        uid = session['user']['id']
        cur.execute("SELECT * FROM health_records WHERE patient_id = %s", (uid,))
        records = cur.fetchall()
        for r in records:
            r['data'] = decrypt(r['data'])
        return render_template("dashboard.html", role=role, records=records)

    return render_template("dashboard.html", role=role, records=[])

@app.route("/add_record", methods=["POST"])
def add_record():
    if 'user' not in session or session['user']['role'] != 'doctor':
        return "Access denied"

    patient_id = request.form["patient_id"]
    data = request.form["data"]
    encrypted_data = encrypt(data)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO health_records (patient_id, doctor_id, data) VALUES (%s, %s, %s)",
                (patient_id, session['user']['id'], encrypted_data))
    conn.commit()
    conn.close()

    return redirect("/dashboard")

if __name__ == "__main__":
    app.run(debug=True)