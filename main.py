import sqlite3
from tkinter import Tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog
from tkinter import ttk
import random


def gen_uuid():
    keys = "abcdefghijklmnopqrstuvwxyz1234567890"
    #       01234
    uuid = ""
    lenght_of_keys = len(keys)
    for i in range(8):
        rand_index = random.randint(0, lenght_of_keys - 1)
        uuid += keys[rand_index]
    return uuid


def create_tables():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    """
    Crimes
    ------
    | id (uuid) | serial_number (uuid) | caught (bool) | crime (str) | date (str) | notes (str) | evidence (images) |
    
    Criminals
    | serial_number (uuid) | name (str) | dob (date) | race (str) | is_married (bool) |
    
    
    """
    command = """
    CREATE TABLE IF NOT EXISTS crimes (
        id TEXT PRIMARY KEY,
        serial_number TEXT,
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


def add_criminal(name: str, dob: str, is_married: bool, race: str = "black"):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # First make a unique serial number
    serial_number = str(gen_uuid())[:8]
    command = f"""
    INSERT INTO criminals VALUES (
        "{serial_number}",
        "{name}",
        "{dob}",
        "{is_married}",
        "{race}"
    );
    """
    c.execute(command)
    conn.commit()
    conn.close()
    return serial_number


def add_crime(serial_number: str, crime: str, date: str, notes: str, evidence: str):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    command = f"""
    INSERT INTO crimes VALUES (
        "{serial_number}",
        0,
        "{crime}",
        "{date}",
        "{notes}",
        "{evidence}"
    );
    """
    c.execute(command)
    conn.commit()
    conn.close()


def get_crimes():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    command = """
    SELECT * FROM crimes;
    """
    c.execute(command)
    crimes = c.fetchall()
    conn.close()
    return crimes

def get_criminals():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    command = """
    SELECT * FROM criminals;
    """
    c.execute(command)
    criminals = c.fetchall()
    conn.close()
    return criminals


def get_crimes(serial_number: str):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    command = f"""
    SELECT * FROM crimes WHERE serial_number = "{serial_number}";
    """
    c.execute(command)
    crime = c.fetchall()
    conn.close()
    return crime

