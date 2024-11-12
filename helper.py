import os
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
from functools import wraps
import secrets
import datetime
import re

import subprocess
import csv
import urllib
import uuid
import hashlib  

def generate_hash_token(token):
    hash_object= hashlib.sha256(token.encode())
    hashed_token= hash_object.hexdigest()
    return hashed_token



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


mailuser= os.environ.get("mail_username")

db = SQL("sqlite:///deviator.db")
'''admin_role = db.execute("SELECT role FROM users WHERE id = ?", session["user_id"])[0]["role"]

def invite_admin():
    if admin_role == "admin":
        pass


def map_dealers(dealer, site):
    if admin_role == "admin":
        db.execute("INSERT INTO sites (site_id, user_id, role)")
    
'''
'''def send_invite_email(mail, email, role, token, mailuser):
    auth_url= url_for('authenticate')
    subject= "Registration for Deviator System"
    body= f"Click the following link to complete your registration: <form action='{auth_url}' method='post'><input='hidden' name ='token' value='{token}'><input type ='hidden' name='role' value='{role}'><button type='submit'>{auth_url}</button></form>"
    recipient_email= email
    msg= Message(subject=subject, body=body, recipients=recipient_email, sender=mailuser)
    mail.send(msg)
'''    
    
def send_notice_email(mail, email, notice):
    subject= "Deviator Account Change Notice"
    body= f"{notice}"
    recipient_email= email
    msg= Message(subject=subject, body=body, recipients=[recipient_email], sender=mailuser)
    mail.send(msg)
     

def valid_password(password, confirm):
    str(password)
    str(confirm)
    if not password:
        return False
    if len(password) < 8 or len(password) > 64:
        return False
    if not any((i.isascii() or i.isspace()) for i in password):
        return False
    if password != confirm:
        return False      
    return True


def valid_username(username):
    if not username:
        return False
    if len(username) < 6:
        return False
    return True

def valid_name(first_name, last_name):
    if not first_name:
        return False
    if not last_name:
        return False
    if not first_name.isalpha():
        return False
    if not last_name.isalpha():
        return False
    return True

def valid_email(email):
    if re.search("[a-zA-Z0-9._]+@[a-z]+.com|.edu|.org|.net", email) == None:
        return False
    else:
        return True
    

def register_user(email, role):
    if valid_email(email):
        if valid_password(request.form.get("password"), request.form.get("confirm")) and valid_username(username=request.form.get("username")):
            if valid_name(request.form.get("first_name"), request.form.get("last_name")):
                    try: 
                        db.execute("INSERT INTO users (username, password, role, email, address, phone_number, first_name, last_name) VALUES (?,?,?,?,?,?,?,?)", request.form.get("username"), generate_password_hash(request.form.get("password")), role, email.lower(), request.form.get("address"), request.form.get("phone_number"), request.form.get("first_name").upper(), request.form.get("last_name").upper())
                    except:
                        return False, f"unsuccessful"
                    
                    return True, f"success!"
            else:
                return False, f"Please enter your first and last name!"
        else:
            return False, f"Invalid username and/or password!"
    else:
        return False, f"Invalid email!"



