import tkinter as tk
from tkinter import messagebox
import sqlite3
import bcrypt
import subprocess

def create_db():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def register_user():
    username = username_entry.get()
    password = password_entry.get()
    
    if not username or not password:
        messagebox.showerror("Error", "Username and password cannot be empty")
        return
    
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
    try:
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "User registered successfully")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists")
    
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)

def login_user():
    username = username_entry.get()
    password = password_entry.get()
    
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    db_password = cursor.fetchone()
    
    conn.close()
    
    if db_password and bcrypt.checkpw(password.encode(), db_password[0]):
        messagebox.showinfo("Success", "Login successful")
        root.destroy()
        subprocess.Popen(["python", "3rd.py"])
    else:
        messagebox.showerror("Error", "Invalid username or password")
    
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)

root = tk.Tk()
root.title("Login and Registration")
root.configure(bg='black')  # Set background color of the root window to black

create_db()  # Ensure the database and table are created

# GUI Enhancements with better layout management and color themes
main_frame = tk.Frame(root, bg='black')  # Set the frame background to black
main_frame.pack(padx=10, pady=10)

username_label = tk.Label(main_frame, text="Username:", bg='black', fg='white')
username_label.grid(row=0, column=0, padx=5, pady=5)
username_entry = tk.Entry(main_frame)
username_entry.grid(row=0, column=1, padx=5, pady=5)

password_label = tk.Label(main_frame, text="Password:", bg='black', fg='white')
password_label.grid(row=1, column=0, padx=5, pady=5)
password_entry = tk.Entry(main_frame, show="*")
password_entry.grid(row=1, column=1, padx=5, pady=5)

register_button = tk.Button(main_frame, text="Register", command=register_user)
register_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

login_button = tk.Button(main_frame, text="Login", command=login_user)
login_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

root.mainloop()
