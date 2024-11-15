from cs50 import SQL
from werkzeug.security import generate_password_hash
import getpass

def main():
    db = SQL("sqlite:///deviator.db")

    first_name = str(input(f'First Name: '))
    last_name = str(input(f'Last Name: '))
    username = str(input(f'Username: '))
    email = str(input(f'Email: '))
    while True:
        password = str(getpass.getpass(f'Password: '))
        confirm_pass = str(getpass.getpass(f'Retype Password: '))
        

        if password == confirm_pass:
            break
        else:
            print("\nPasswords do not match, try again. \n")
            
    hash_pass = generate_password_hash(password)
    try:
        db.execute("INSERT INTO users (username, password, first_name, last_name, email, role) VALUES (?,?,?,?,?,'admin')", username, hash_pass, first_name, last_name, email)
    except Exception as e:
        print("ERROR: "+str(e))
        main()
if __name__ == "__main__":
    main()