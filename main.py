import mysql.connector
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random
from PIL import Image, ImageTk
import io

# Replace these with your actual MySQL connection details
config = {
    'user': 'your_username',
    'password': 'your_password',
    'host': 'localhost',
    'database': 'criminal_db',
    'raise_on_warnings': True
}


def create_connection():
    return mysql.connector.connect(**config)


def execute_query(query, params=None):
    connection = create_connection()
    cursor = connection.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()
        return cursor
    finally:
        cursor.close()
        connection.close()


def fetch_query(query, params=None):
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def gen_uuid():
    keys = "abcdefghijklmnopqrstuvwxyz1234567890"
    return ''.join(random.choice(keys) for _ in range(8))


def create_tables():
    create_crimes_table = """
    CREATE TABLE IF NOT EXISTS crimes (
        id VARCHAR(8) PRIMARY KEY,
        serial_number VARCHAR(8),
        caught BOOLEAN,
        crime VARCHAR(255),
        date DATE,
        notes TEXT
    );
    """

    create_criminals_table = """
    CREATE TABLE IF NOT EXISTS criminals (
        serial_number VARCHAR(8) PRIMARY KEY,
        name VARCHAR(255),
        dob DATE,
        race VARCHAR(50),
        is_married BOOLEAN
    );
    """

    create_evidence_table = """
    CREATE TABLE IF NOT EXISTS evidence (
        id INT AUTO_INCREMENT PRIMARY KEY,
        crime_id VARCHAR(8),
        image_data LONGBLOB,
        FOREIGN KEY (crime_id) REFERENCES crimes(id) ON DELETE CASCADE
    );
    """

    execute_query(create_crimes_table)
    execute_query(create_criminals_table)
    execute_query(create_evidence_table)


def add_criminal():
    name = name_entry.get()
    dob = dob_entry.get()
    race = race_entry.get()
    is_married = married_var.get()

    if not name or not dob or not race:
        messagebox.showerror("Error", "Please fill all fields")
        return

    serial_number = gen_uuid()
    query = """
    INSERT INTO criminals (serial_number, name, dob, race, is_married)
    VALUES (%s, %s, %s, %s, %s);
    """
    execute_query(query, (serial_number, name, dob, race, is_married))

    messagebox.showinfo("Success", f"Criminal added with serial number: {serial_number}")
    refresh_criminal_list()


def update_criminal():
    selection = criminal_listbox.curselection()
    if not selection:
        messagebox.showerror("Error", "Please select a criminal to update")
        return

    serial_number = criminal_listbox.get(selection[0]).split()[0]
    name = name_entry.get()
    dob = dob_entry.get()
    race = race_entry.get()
    is_married = married_var.get()

    if not name or not dob or not race:
        messagebox.showerror("Error", "Please fill all fields")
        return

    query = """
    UPDATE criminals
    SET name = %s, dob = %s, race = %s, is_married = %s
    WHERE serial_number = %s;
    """
    execute_query(query, (name, dob, race, is_married, serial_number))

    messagebox.showinfo("Success", f"Criminal updated: {serial_number}")
    refresh_criminal_list()


def delete_criminal():
    selection = criminal_listbox.curselection()
    if not selection:
        messagebox.showerror("Error", "Please select a criminal to delete")
        return

    serial_number = criminal_listbox.get(selection[0]).split()[0]

    if messagebox.askyesno("Confirm", "Are you sure you want to delete this criminal and all associated crimes?"):
        query = "DELETE FROM criminals WHERE serial_number = %s;"
        execute_query(query, (serial_number,))

        messagebox.showinfo("Success", f"Criminal deleted: {serial_number}")
        refresh_criminal_list()
        refresh_crime_list()


def add_crime():
    selection = criminal_listbox.curselection()
    if not selection:
        messagebox.showerror("Error", "Please select a criminal")
        return

    serial_number = criminal_listbox.get(selection[0]).split()[0]
    crime = crime_entry.get()
    date = date_entry.get()
    notes = notes_entry.get("1.0", tk.END)

    if not crime or not date:
        messagebox.showerror("Error", "Please fill all fields")
        return

    crime_id = gen_uuid()

    query = """
    INSERT INTO crimes (id, serial_number, caught, crime, date, notes)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    execute_query(query, (crime_id, serial_number, False, crime, date, notes))

    for image_path in evidence_paths:
        with open(image_path, 'rb') as file:
            image_data = file.read()
        query = """
        INSERT INTO evidence (crime_id, image_data)
        VALUES (%s, %s);
        """
        execute_query(query, (crime_id, image_data))

    messagebox.showinfo("Success", f"Crime added with ID: {crime_id}")
    refresh_crime_list()


def update_crime():
    selection = crime_listbox.curselection()
    if not selection:
        messagebox.showerror("Error", "Please select a crime to update")
        return

    crime_id = crime_listbox.get(selection[0]).split()[0]
    crime = crime_entry.get()
    date = date_entry.get()
    notes = notes_entry.get("1.0", tk.END)

    if not crime or not date:
        messagebox.showerror("Error", "Please fill all fields")
        return

    query = """
    UPDATE crimes
    SET crime = %s, date = %s, notes = %s
    WHERE id = %s;
    """
    execute_query(query, (crime, date, notes, crime_id))

    # Update evidence
    query = "DELETE FROM evidence WHERE crime_id = %s;"
    execute_query(query, (crime_id,))

    for image_path in evidence_paths:
        with open(image_path, 'rb') as file:
            image_data = file.read()
        query = """
        INSERT INTO evidence (crime_id, image_data)
        VALUES (%s, %s);
        """
        execute_query(query, (crime_id, image_data))

    messagebox.showinfo("Success", f"Crime updated: {crime_id}")
    refresh_crime_list()


def delete_crime():
    selection = crime_listbox.curselection()
    if not selection:
        messagebox.showerror("Error", "Please select a crime to delete")
        return

    crime_id = crime_listbox.get(selection[0]).split()[0]

    if messagebox.askyesno("Confirm", "Are you sure you want to delete this crime?"):
        query = "DELETE FROM crimes WHERE id = %s;"
        execute_query(query, (crime_id,))

        messagebox.showinfo("Success", f"Crime deleted: {crime_id}")
        refresh_crime_list()


def refresh_criminal_list():
    criminal_listbox.delete(0, tk.END)
    query = "SELECT * FROM criminals;"
    criminals = fetch_query(query)

    for criminal in criminals:
        criminal_listbox.insert(tk.END, f"{criminal['serial_number']} - {criminal['name']}")


def refresh_crime_list():
    crime_listbox.delete(0, tk.END)
    query = "SELECT * FROM crimes;"
    crimes = fetch_query(query)

    for crime in crimes:
        crime_listbox.insert(tk.END, f"{crime['id']} - {crime['crime']}")


def select_evidence():
    global evidence_paths
    evidence_paths = list(filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg *.png")]))
    evidence_label.config(text=f"{len(evidence_paths)} images selected")


def view_crime():
    selection = crime_listbox.curselection()
    if not selection:
        messagebox.showerror("Error", "Please select a crime to view")
        return

    crime_id = crime_listbox.get(selection[0]).split()[0]

    query = "SELECT * FROM crimes WHERE id = %s;"
    crime = fetch_query(query, (crime_id,))[0]

    query = "SELECT image_data FROM evidence WHERE crime_id = %s;"
    evidence = fetch_query(query, (crime_id,))

    if crime:
        details = f"Crime: {crime['crime']}\nDate: {crime['date']}\nNotes: {crime['notes']}"
        messagebox.showinfo("Crime Details", details)

        for i, img_data in enumerate(evidence):
            image = Image.open(io.BytesIO(img_data['image_data']))
            image.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(image)

            top = tk.Toplevel()
            top.title(f"Evidence {i + 1}")
            label = tk.Label(top, image=photo)
            label.image = photo
            label.pack()
    else:
        messagebox.showerror("Error", "Crime not found")


# Create main window
root = tk.Tk()
root.title("Criminal Database")

# Create tabs
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

criminals_tab = ttk.Frame(notebook)
crimes_tab = ttk.Frame(notebook)

notebook.add(criminals_tab, text="Criminals")
notebook.add(crimes_tab, text="Crimes")

# Criminals tab
tk.Label(criminals_tab, text="Name:").grid(row=0, column=0)
name_entry = tk.Entry(criminals_tab)
name_entry.grid(row=0, column=1)

tk.Label(criminals_tab, text="Date of Birth:").grid(row=1, column=0)
dob_entry = tk.Entry(criminals_tab)
dob_entry.grid(row=1, column=1)

tk.Label(criminals_tab, text="Race:").grid(row=2, column=0)
race_entry = tk.Entry(criminals_tab)
race_entry.grid(row=2, column=1)

married_var = tk.BooleanVar()
tk.Checkbutton(criminals_tab, text="Married", variable=married_var).grid(row=3, column=0, columnspan=2)

tk.Button(criminals_tab, text="Add Criminal", command=add_criminal).grid(row=4, column=0)
tk.Button(criminals_tab, text="Update Criminal", command=update_criminal).grid(row=4, column=1)
tk.Button(criminals_tab, text="Delete Criminal", command=delete_criminal).grid(row=4, column=2)

criminal_listbox = tk.Listbox(criminals_tab, width=50)
criminal_listbox.grid(row=5, column=0, columnspan=3)

# Crimes tab
tk.Label(crimes_tab, text="Crime:").grid(row=0, column=0)
crime_entry = tk.Entry(crimes_tab)
crime_entry.grid(row=0, column=1)

tk.Label(crimes_tab, text="Date:").grid(row=1, column=0)
date_entry = tk.Entry(crimes_tab)
date_entry.grid(row=1, column=1)

tk.Label(crimes_tab, text="Notes:").grid(row=2, column=0)
notes_entry = tk.Text(crimes_tab, height=3, width=20)
notes_entry.grid(row=2, column=1)

tk.Button(crimes_tab, text="Select Evidence", command=select_evidence).grid(row=3, column=0)
evidence_label = tk.Label(crimes_tab, text="No images selected")
evidence_label.grid(row=3, column=1)

tk.Button(crimes_tab, text="Add Crime", command=add_crime).grid(row=4, column=0)
tk.Button(crimes_tab, text="Update Crime", command=update_crime).grid(row=4, column=1)
tk.Button(crimes_tab, text="Delete Crime", command=delete_crime).grid(row=4, column=2)

crime_listbox = tk.Listbox(crimes_tab, width=50)
crime_listbox.grid(row=5, column=0, columnspan=3)

tk.Button(crimes_tab, text="View Crime", command=view_crime).grid(row=6, column=0, columnspan=3)

# Initialize
create_tables()
refresh_criminal_list()
refresh_crime_list()

evidence_paths = []

root.mainloop()