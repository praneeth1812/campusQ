from flask import Flask, render_template, url_for, request,redirect,session
from flask_mail import Mail, Message
import sqlite3 as sql
app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'campusQprofessional@gmail.com'
app.config['MAIL_PASSWORD'] = 'uluu kght qvtm hfib'
app.config['MAIL_DEFAULT_SENDER'] = 'campusQprofessional@gmail.com'
mail = Mail(app)

@app.route('/send-mail/',methods=['POST','GET'])
def send_mail():
    if request.method == "POST":
        try:
            f_user = request.form["f_user"]
            print(f_user)
            with sql.connect("database.db") as conn:
                    curr = conn.cursor()
                    curr.execute("SELECT * FROM auth WHERE username = ?",(f_user,))
                    f_pass = curr.fetchall()
                    conn.close()
                    print(f_pass)
                    if f_pass:
                        row  = f_pass[0]
                        username = row[0]
                        password = row[1]
                        email = row[2]
                        print(username)
                        m =f'Hello {username} from campusQ'
                        b = f'This is a your password {password} Do not  share with any one'
                        print(m,b)
                        msg = Message(m,
                                      recipients=[email])
                        msg.body = b
                        mail.send(msg)
                        
                        return redirect(url_for('login'))
                    else:
                        return '<h1>Invalid user not found</h1>'
        except:
            err = 'err'
    return redirect(url_for('login'))



user = ""
app.secret_key = 'campusQ_key'
@app.route("/login")
def login():
    if not ('logged_in' in session and session['logged_in']):
        return render_template('login.html')
    else:
        return redirect(url_for('index'))
@app.route("/")
def index():
     if 'logged_in' in session and session['logged_in']:
        return render_template('index.html',u = session['username'])
     else:
          return redirect(url_for('login'))
@app.route("/signupreg")
def registration():
    return render_template('signup.html')
@app.route("/signup",methods = ['POST','GET'])
def signup():
    if request.method == "POST":
        try:
            r_user = request.form["username"]
            r_pas = request.form["password"]
            r_email = request.form["email"]
            with sql.connect("database.db") as conn:
                curr = conn.cursor()
                curr.execute("INSERT OR REPLACE INTO auth (username,password,email) VALUES(?,?,?)",(r_user,r_pas,r_email))
                conn.commit()
        except:
            conn.rollback()
        conn.close()
    return redirect(url_for('login'))
@app.route("/verify",methods = ['POST','GET'])
def verify():
    if request.method == "POST":
        pas = ""
        try:
            global user
            user = request.form["username"]
            pas = request.form["password"]
            with sql.connect("database.db") as conn:
                curr = conn.cursor()
                curr.execute(
                    "CREATE TABLE IF NOT EXISTS auth (username TEXT NOT NULL PRIMARY KEY,password TEXT NOT NULL,email TEXT NOT NULL)"
                )
                conn.commit()
                curr.execute("SELECT password FROM auth WHERE username = ?",(user,))
                d_pas = curr.fetchall()
                conn.close()
        except:
            print("Error occured")
        try:
            if pas == d_pas[0][0]:
                session['logged_in'] = True
                session['username'] = user
                return redirect(url_for('index'))
            else:
                return redirect(url_for('login'))
        except:
            return redirect(url_for('login'))
    return redirect(url_for('login'))
 
@app.route("/details", methods=["POST", "GET"])
def home():
    if 'logged_in' in session and session['logged_in']:
        if request.method == "POST":
            try:
                ques = request.form["q"]
                ans  = request.form["a"]
                qa = "Question Bank"
                aa = session['username'] 
                with sql.connect("database.db") as con:
                    cur = con.cursor()
                    cur.execute(
                        "CREATE TABLE IF NOT EXISTS cq (Q TEXT NOT NULL PRIMARY KEY,A TEXT NOT NULL,QA TEXT NOT NULL,AA TEXT NOT NULL )"
                    )
                    con.commit()
                    cur.execute("INSERT OR REPLACE INTO cq (Q,A,QA,AA) VALUES (?,?,?,?)", (ques,ans,qa,aa))
                    cur.execute("DELETE FROM question WHERE Ques = ?", (ques,))
                    con.commit()
            except:
                    con.rollback()
        cur.execute("SELECT * FROM cq")
        rows = cur.fetchall()
        con.close()
        return render_template("details.html", rows=rows, u = session['username'])
    else:
         return redirect(url_for('login'))



@app.route("/questions", methods=["POST", "GET"])
def ques():
    if 'logged_in' in session and session['logged_in']:
        if request.method == "POST":
            try:
                ques_q = request.form["qs"]
                
                
            except:
                ques_q = "error"
            try:
                    with sql.connect("database.db") as conn:
                        curr = conn.cursor()
                        curr.execute(
                            "CREATE TABLE IF NOT EXISTS question (Ques TEXT NOT NULL PRIMARY KEY)"
                        )
                        conn.commit()
                        curr.execute("INSERT OR REPLACE INTO question (Ques) VALUES (?)", (ques_q,))
                        conn.commit()
            except:
                    conn.rollback()
            conn.close()

        conn = sql.connect("database.db")

        curr = conn.cursor()
        curr.execute("SELECT * FROM question")
        q_rows = curr.fetchall()
        conn.close()
        print(q_rows)
        return render_template("question.html", q_rows=q_rows,u = session['username'])
    else:
        return redirect(url_for('login'))







@app.route('/info')
def info():
    if 'logged_in' in session and session['logged_in']:
        con = sql.connect("database.db")
        # con.row_factory = sql.Row

        cur = con.cursor()
        cur.execute("SELECT * FROM cq")
        rows = cur.fetchall()
        con.close()
        return render_template("details.html",rows=rows, u = session['username'])
    else:
        return redirect(url_for('login'))
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
