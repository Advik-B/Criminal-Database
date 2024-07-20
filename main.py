import sqlite3
from tkinter import Tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog
from tkinter import ttk

def create_tables():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    """
    Crimes
    ------
    | serial_number (uuid) | caught (bool) | crime (str) | date (str) | notes (str) | evidence (images) |
    
    Criminals
    | serial_number (uuid) | name (str) | dob (date) | race (str) | is_married (bool) |
    
    
    """
    command = """
    CREATE TABLE IF NOT EXISTS crimes (
        serial_number TEXT PRIMARY KEY,
        caught BOOLEAN,
        crime TEXT,
        date TEXT,
        notes TEXT,
        evidence TEXT
    );
    """
    command2 = """
    CREATE TABLE IF NOT EXISTS criminals (
        serial_number TEXT PRIMARY KEY,
        name TEXT,
        dob TEXT,
        race TEXT,
        is_married BOOLEAN
    );
    """
    c.execute(command)
    c.execute(command2)
    conn.commit()
    conn.close()

