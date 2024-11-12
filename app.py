import os
import sys
from flask import Flask, flash, redirect, render_template, request, session, url_for, get_flashed_messages
from flask_session import Session
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
from functools import wraps
from flask import jsonify
from helper import register_user, send_notice_email, valid_email, login_required, generate_hash_token, valid_password
import secrets
import datetime
import re
from dotenv import find_dotenv, load_dotenv
import random
from faker import Faker
import requests
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.io import to_json

dotenv_path= find_dotenv()
load_dotenv(dotenv_path)
secretkey= os.environ.get("SECRET_KEY")
mailuser= os.environ.get("MAIL_USERNAME")
mailpass= os.environ.get("MAIL_PASSWORD")
password1 = os.environ.get("PASSWORD")

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["SECRET_KEY"] = secretkey 
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = mailuser
app.config["MAIL_PASSWORD"] = mailpass
app.config["MAIL_DEFAULT_SENDER"] = mailuser
mail = Mail(app)
db = SQL("sqlite:///deviator.db")

add_org= False

def send_invite_email(mail, email, role, token):
    auth_url= url_for('authenticate', _external=True, token=token, role=role, email=email)
    msg= Message("Registration for Deviator System",
                 recipients=[email],
                 sender="deviator.test123@gmail.com")  
    msg.body = f"Click the following link to complete your registration: {auth_url}"
 
    mail.send(msg)
    

def send_2fa_email(email, code):
    subject= "Deviator Verification Code"
    msg= Message(subject= subject, recipients=[email])
    msg.body= f"Please enter the following code in your browser: {code}"
    mail.send(msg)
    

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    return render_template("index.html")

#login page and send verification code to email in order to login
@app.route("/login", methods=["GET", "POST"])
def login():
    
    session.clear()
    if request.method == "POST":    
        if not (request.form.get("username") and request.form.get("password")):
            flash("Invalid username and/or password")
            return render_template("login.html")
        
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            flash("Invalid username and/or password")
            return render_template("login.html")
        
        session["email"] = rows[0]["email"]
        session["code"] = str(random.randint(100000, 999999))
        send_2fa_email(email=session["email"], code= session["code"])
        return render_template("verify.html")
    else:
        return render_template("login.html")
    
#verify code sent to email via login or reset password
@app.route("/verify", methods=["POST"])
def verify():
    if "attempts" in session:
        if session["attempts"] == 3:
            session.clear()
            flash("Maximum attempts exceeded. Redirected to login page.")
            return render_template("login.html")
    else:
        session["attempts"] = 0
        
    if "email" in session and "code" in session:
        user_code= request.form.get("code") 
        if user_code == session["code"]:
            if "status" in session and session["status"] == "reset":
                session["verified"] = True
                return render_template("reset_pass.html")
            else:
                session["user_id"]= db.execute("SELECT id FROM users WHERE email = ?", session["email"])[0]["id"]
                session["role"]= db.execute("SELECT role FROM users WHERE email = ?", session["email"])[0]["role"]
                del_keys= []
                for key in session:
                    if key == "user_id" or key == "role":
                        continue
                    else:
                        del_keys.append(key)
                        
                for key in del_keys:
                    session.pop(key)
                del_keys.clear()
                return redirect("/")
        else:
            session["attempts"] += 1
            flash("Invalid code, try again")
            return render_template("verify.html")
        
#allow user to reset password by sending code via email
@app.route("/reset_password/<verified_status>", methods=["POST"])
@app.route("/reset_password", methods=["GET"])
def reset(verified_status=None):
    if request.method == "POST": 
        if verified_status == "verified" and "verified" in session and session["verified"] == True:   
            user_pass= request.form.get("password")
            confirm= request.form.get("confirm")
            if not user_pass or not confirm or not valid_password(password=user_pass, confirm=confirm):
                flash("Invalid password!")
                return render_template("reset_pass.html")
            else:
                try:
                    db.execute("UPDATE users SET password = ? WHERE email = ?", generate_password_hash(user_pass), session["email"])
                except:
                    session.clear()
                    flash("Unable to update password. Please try again.")
                    return render_template("login.html")
                session.clear()
                flash("Successfully updated password! Please log in.")
                return render_template("login.html")
        
        elif verified_status == 'not_verified':
            user= db.execute("SELECT * FROM users WHERE email = ? AND username = ?", request.form.get("email"), request.form.get("username"))
            if len(user) != 1:
                flash("Cannot find user with that email address and username. Please try again.")
                return render_template("forgot_pass.html")
            else:
                session["email"] = user[0]["email"]
                session["code"] = str(random.randint(100000, 999999))
                session["status"] = "reset"
                send_2fa_email(email=session["email"], code= session["code"])
                return render_template("verify.html")
            
        else:
            session.clear()
            flash("That is not allowed!")
            return render_template("login.html")    
        
    else:
        return render_template("forgot_pass.html")

#redirect from authenticate, allow user to set up account
@app.route("/register", methods=["POST"])
def register():
    session.clear()
    email = request.form.get("email")
    role = request.form.get("role")
     
    if request.method == "POST":
        registration= register_user(email=email, role=role)
        
        if registration[0] == False:
            flash(f"{registration[1]}")
            return render_template("register.html", email=email, role=role)
        
        elif registration[0] == True:
            db.execute("UPDATE invites SET used = 1 WHERE email = ?", email)
            db.execute("DELETE FROM invites WHERE used = 1")
            db.execute("DELETE FROM invites WHERE expiration < ?", datetime.datetime.now())
            first_name, last_name= request.form.get("first_name"), request.form.get("last_name")
            notice= f"Account has been successfully created for {first_name} {last_name}."
             
            if role == "dealer_admin" or "admin":
                emails= db.execute("SELECT email FROM users WHERE role = ?", "admin")[0]["email"]
                send_notice_email(mail, email=emails, notice=notice)
            else:
                emails= db.execute("SELECT email FROM users WHERE role = ? OR role = ?", "admin", "dealer_admin")
                send_notice_email(mail, email=emails, notice=notice)
                
            flash("Successfully Registered!")
            return redirect("/")
    else:
            session.clear()
            flash("invalid page!")
            return render_template("login.html")

#authenticate user token and redirect to register page if valid
@app.route("/authenticate", methods=["GET"])
def authenticate():
    token= generate_hash_token(request.args.get("token"))
    email= request.args.get("email")
    role= request.args.get("role")
    if db.execute("SELECT token FROM invites WHERE token = ?", token)[0]["token"] and db.execute("SELECT used FROM invites WHERE token = ?", token)[0]["used"] == 0 and datetime.datetime.strptime(db.execute("SELECT expiration FROM invites WHERE token = ?", token)[0]["expiration"], "%Y-%m-%d %H:%M:%S") > datetime.datetime.now() and role == db.execute("SELECT role FROM invites WHERE token = ?", token)[0]["role"]:
            return render_template("register.html", email=email, role=role)
    else:
        session.clear()
        flash("Link is either expired or invalid!")
        return render_template("login.html")

#invite people given users permissions
@app.route("/invite", methods=["GET", "POST"])
@login_required
def invite():
    
    if request.method == "POST":
        email, role = request.form.get("invite_email"), request.form.get("role")
        
        if valid_email(email=email) == False:
            flash("Invalid email!")
            redirect("/invite")
        
        if role == "admin" or role == "dealer_admin":
            if db.execute("SELECT role FROM users WHERE id = ?", session["user_id"])[0]["role"] != "admin":
                flash("You do not have permissions to invite this role!")
                return redirect("/invite")
        token= secrets.token_urlsafe(16)    
        hashed_token= generate_hash_token(token)
        expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=15)
        db.execute("INSERT INTO invites (email, token, used, expiration, role) VALUES (?,?,?,?,?)", email, hashed_token, 0, expiration_time, role)
        send_invite_email(email=email, role=role, token=token, mail=mail)
        flash("Invite successfully sent!")
        
        return redirect("/")
    
    else:
        if db.execute("SELECT role FROM users WHERE id = ?", session["user_id"])[0]["role"] in ("admin", "dealer_admin"):
            return render_template("invite.html")
        else: 
            flash("You do not have permission to send invitations!")
            return redirect("/")    
        
#log user out          
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/login")

#render manage users webpage with site data
@app.route("/manage_users", methods=["GET"])
@login_required
def manage():
    
    
    
    users = []

    if session["role"] == "dealer":
        return render_template("/")
    elif session["role"] == "dealer_admin":
        all_users = db.execute("SELECT * FROM users WHERE role = 'customer' OR role = 'dealer' ORDER BY first_name ASC")
    elif session["role"] == "admin":
        all_users = db.execute("SELECT * FROM users WHERE role != 'admin' ORDER BY first_name ASC")
    else:
        flash("You do not have permission to access this page!")
        return redirect("/")
    
    
    all_sites = db.execute("SELECT * FROM sites")
    i = 1
    for user in all_users:
        sites= []
        for site in all_sites:
            if site["parent_id"] == user["id"]:
                sites.append(site["title"])
                
        person= {
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "username": user["username"],
            "role": user["role"],
            "email": user["email"], 
            "sites": sites, 
            "id": user["id"],
            "safe_id": i
        }

        users.append(person)
        i+=1

    return render_template("manage_users_new.html", users=users, all_sites=all_sites)

 
#send dealer info to the webpage via API request    
@app.route("/get_user_data")
@login_required
def get_users():
    users = []
    
    if session["role"] == "dealer":
        all_users = db.execute("SELECT * FROM users WHERE role = 'customer' ORDER BY first_name ASC")
    elif session["role"] == "dealer_admin":
        all_users = db.execute("SELECT * FROM users WHERE role = 'customer' OR role = 'dealer' ORDER BY first_name ASC")
    elif session["role"] == "admin":
        all_users = db.execute("SELECT * FROM users WHERE role != 'admin' ORDER BY first_name ASC")
    else:
        flash("You do not have permission to access this page!")
        return redirect("/")
    all_sites = db.execute("SELECT * FROM sites")
    i = 1
    for user in all_users:
        sites= []
        for site in all_sites:
            if site["parent_id"] == user["id"]:
                sites.append(site["title"])
                
        person = {
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "username": user["username"],
            "role": user["role"],
            "email": user["email"], 
            "sites": sites, 
            "id": user["id"],
            "safe_id": i
        }

        users.append(person)
        i+=1
        
    return jsonify(users)


@app.route("/get_site_data")
@login_required
def test_get_sites():
    all_sites = db.execute("SELECT DISTINCT title, site_id as groupId FROM sites_master ORDER by title ASC")    
    
    return jsonify(all_sites)


#update db with data from user via API      
@app.route("/sites", methods=["PUT", "POST", "DELETE"])
@login_required
def update():
    data= request.json
    sites = db.execute("SELECT * FROM sites_master")

    if "new_group_id" in data.keys():
        title = db.execute("SELECT title FROM sites_master WHERE site_id =? ", data["new_group_id"])[0]["title"]
    else:
        old_title = db.execute("SELECT title FROM sites_master WHERE site_id = ?", data["old_group_id"])[0]["title"]
        
    def has_permission(data_id, session_role):
        role = db.execute("SELECT role FROM users WHERE id = ?", data_id)[0]["role"]
        if role == 'dealer' or role == 'customer':
            if session_role == 'dealer_admin' or session_role == 'admin':
                return True
            else:
                return False
        else:
            return False
        
    def found_old_site(sites, old_group_id: int):
        for site in sites: 
            if site["site_id"] == old_group_id:
                return True     
        return False
    
    def found_new_site(sites, new_group_id: int):
        for site in sites: 
            if site["site_id"] == new_group_id:
                return True
        return False
    
    def matched_user_site(data):
        user_sites = db.execute("SELECT group_id FROM sites WHERE parent_id = ?", data["id"])
        for result in user_sites:
            if data["old_group_id"] == result['group_id']:
                return True       
        return False
    
    def no_dup_sites(data):
        user_sites = db.execute("SELECT group_id FROM sites WHERE parent_id = ?", data["id"])
        for result in user_sites:
            if data["new_group_id"] == result["group_id"]:
                return False
        return True                           

    if request.method == "PUT":
        if found_old_site(sites, data["old_group_id"]) and found_new_site(sites, data["new_group_id"]) and matched_user_site(data=data) and no_dup_sites(data=data) and has_permission(data_id=data["id"], session_role= session["role"]):
            try:
                db.execute("UPDATE sites SET group_id = ?, title = ? WHERE (parent_id = ? AND group_id = ?)", data["new_group_id"], title, data["id"], data["old_group_id"])
            except Exception as e:
                print(e)
                return jsonify(str(e)), 404
            
            updated_sites = {'sites': [site["title"] for site in db.execute("SELECT group_id, title FROM sites WHERE parent_id = ?", data["id"])]}
            return jsonify(updated_sites), 200        
        else:
            print(found_old_site(sites, data["old_group_id"]), found_new_site(sites, data["new_group_id"]), matched_user_site(data=data), no_dup_sites(data=data), has_permission(data_id=data["id"], session_role= session["role"]))
            return jsonify("Error!"), 404
        
    elif request.method == "POST":
        if found_new_site(sites, data["new_group_id"]) and no_dup_sites(data=data) and has_permission(data_id=data["id"], session_role= session["role"]):
            try:
                db.execute("INSERT INTO sites (group_id, parent_id, group_type, title) VALUES (?, ?, ?, ?)", data["new_group_id"], data["id"], 1, title)
            except Exception as e:
                print(e)
                return jsonify(str(e)), 404
        
            updated_sites = {'sites': [site["title"] for site in db.execute("SELECT group_id, title FROM sites WHERE parent_id = ?", data["id"])]}
            return jsonify(updated_sites), 200 
        else:
            print('error!')
            return jsonify("Error!") , 404
        
    elif request.method == "DELETE":
        if has_permission(data_id=data["id"], session_role= session["role"]) and (found_old_site(sites, data["old_group_id"])):
            try:
                db.execute("DELETE FROM sites WHERE (group_id = ? AND title = ? AND parent_id = ?)", data["old_group_id"], old_title, data["id"])
            except Exception as e:
                return jsonify(str(e)), 404
            
            updated_sites = {'sites': [site["title"] for site in db.execute("SELECT group_id, title FROM sites WHERE parent_id = ?", data["id"])]}
            return jsonify(updated_sites), 200
        else:
            return jsonify("You do not have these permissions!"), 404 
    else:
        return jsonify("Invalid Method"), 400
     
    

#view data specfic to role permissions
@app.route("/view_data", methods=["GET"])
@login_required
def view():
    
    if session["role"] == "admin":
        sites = db.execute("SELECT site_id AS group_id FROM sites_master")
    elif session["role"] == 'dealer':
        sites = db.execute("SELECT group_id FROM sites WHERE parent_id = ?", session["user_id"])
    elif session["role"] == 'customer':
        sites = db.execute("SELECT site_id AS group_id FROM sites_mater WHERE group_id = (SELECT group_id FROM customers WHERE customer_id = ?)", session["user_id"])
    else:
        flash("You do not have permission to access this page!")
        return redirect("/")
     

    
   
    available_sites = []
    if sites:
        for site_num in range(len(sites)):
            available_sites.append(sites[site_num]["group_id"])
           
    site_data1 = db.execute(f"SELECT * FROM summary WHERE group_id IN (?)", available_sites)
    site_data = pd.DataFrame(site_data1)
    
    print(site_data)
    
    site_data.sort_values('date_occurred_start', ascending=False)
    
    date_1= pd.to_datetime(site_data["date_occurred_start"])
    most_recent_date= date_1.max()
    seven_prior= most_recent_date - datetime.timedelta(days=7)
    
    fig= px.line(site_data, x= 'date_occurred_start', y= 'activity_count', color='title', range_x=[seven_prior, most_recent_date],
                 labels= {
                     "date_occurred_start": "Date", 
                     "activity_count": "Number of Alarms", 
                     "title": "Site Name"
                 })
   
    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))
    fig.update_xaxes(dtick="D1", 
                     tickformat= "%b %d, %Y")
    
    fig_json = to_json(fig)
    
    return render_template("view_data.html", fig_json=fig_json)
            
            
@app.route("/test", methods=["GET"])
@login_required
def test():
    users = []
    
    all_users = db.execute("SELECT * FROM users ORDER BY first_name ASC")
    all_sites = db.execute("SELECT * FROM sites")
    i = 1
    for user in all_users:
        sites= []
        for site in all_sites:
            if site["parent_id"] == user["id"]:
                sites.append(site["title"])
                
        person= {
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "username": user["username"],
            "role": user["role"],
            "email": user["email"], 
            "sites": sites, 
            "id": user["id"],
            "safe_id": i
        }

        users.append(person)
        i+=1

    return render_template("manage_users_new.html", users=users, all_sites=all_sites)


@app.route("/silence_alarm", methods=["GET", "POST"])
@login_required
def silence():
    pass
