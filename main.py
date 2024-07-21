import mysql.connector
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import io
import random
import ctypes
import base64

ctypes.windll.shcore.SetProcessDpiAwareness(1)
ctypes.windll.user32.SetProcessDPIAware()
# Make it so that the window icon is not python's icon
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("dev.krish.CriminalDatabase")

# Replace these with your actual MySQL connection details
config = {
    'user': 'advik',
    'password': 'wHFPa%!x:n2pzh79uBQ*>b',
    'host': 'advik-mysqlsrv.mysql.database.azure.com',
    'database': 'criminal_db',
    'raise_on_warnings': True
}


def startup():
    # Create the database if it doesn't exist
    conn = mysql.connector.connect(
        user=config['user'],
        password=config['password'],
        host=config['host']
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS criminal_db;")
    cursor.close()
    conn.close()


def create_connection():
    return mysql.connector.connect(**config)

def delete_evidences():
    query = "DELETE FROM evidence;"
    execute_query(query)

def execute_query(query, params=None):
    connection = create_connection()
    cursor = connection.cursor()
    try:
        if params is not None:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()
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


def table_exists(table_name):
    query = "SHOW TABLES LIKE %s;"
    result = fetch_query(query, (table_name,))
    return len(result) > 0


def create_tables():
    if not table_exists('crimes'):
        create_crimes_table = """
        CREATE TABLE crimes (
            id VARCHAR(8) PRIMARY KEY,
            serial_number VARCHAR(8),
            caught BOOLEAN,
            crime VARCHAR(255),
            date DATE,
            notes TEXT
        );
        """
        execute_query(create_crimes_table)

    if not table_exists('criminals'):
        create_criminals_table = """
        CREATE TABLE criminals (
            serial_number VARCHAR(8) PRIMARY KEY,
            name VARCHAR(255),
            dob DATE,
            race VARCHAR(50),
            is_married BOOLEAN
        );
        """
        execute_query(create_criminals_table)

    if not table_exists('evidence'):
        create_evidence_table = """
        CREATE TABLE evidence (
            id INT AUTO_INCREMENT PRIMARY KEY,
            crime_id VARCHAR(8),
            image_data TEXT,
            FOREIGN KEY (crime_id) REFERENCES crimes(id) ON DELETE CASCADE
        );
        """
        execute_query(create_evidence_table)


def add_criminal():
    name = name_entry.get()
    dob = dob_entry.get_date()
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
    selected_item = criminal_tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a criminal to update")
        return

    selected = criminal_tree.item(selected_item[0])['values']
    serial_number = selected[0]
    name = name_entry.get()
    dob = dob_entry.get_date()
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
    selected_item = criminal_tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a criminal to delete")
        return

    serial_number = criminal_tree.item(selected_item[0])['values'][0]

    if messagebox.askyesno("Confirm", "Are you sure you want to delete this criminal and all associated crimes?"):
        query = "DELETE FROM criminals WHERE serial_number = %s;"
        execute_query(query, (serial_number,))

        messagebox.showinfo("Success", f"Criminal deleted: {serial_number}")
        refresh_criminal_list()
        refresh_crime_list()


def add_crime():
    selected_item = criminal_tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a criminal")
        return

    serial_number = criminal_tree.item(selected_item[0])['values'][0]
    crime = crime_entry.get()
    date = date_entry.get_date()
    notes = notes_entry.get("1.0", tk.END).strip()

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
            image_data = base64.b64encode(image_data).decode('utf-8')
            query = """INSERT INTO evidence (crime_id, image_data) VALUES (%s, %s);"""
            execute_query(query, (crime_id, image_data))

    messagebox.showinfo("Success", f"Crime added with ID: {crime_id}")
    refresh_crime_list()


def update_crime():
    selected_item = crime_tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a crime to update")
        return

    crime_id = crime_tree.item(selected_item[0])['values'][0]
    crime = crime_entry.get()
    date = date_entry.get_date()
    notes = notes_entry.get("1.0", tk.END).strip()

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
            data = base64.b64encode(image_data)


        query = """
        INSERT INTO evidence (crime_id, image_data)
        VALUES (%s, %s);
        """
        execute_query(query, (crime_id, data))

    messagebox.showinfo("Success", f"Crime updated: {crime_id}")
    refresh_crime_list()


def delete_crime():
    selected_item = crime_tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a crime to delete")
        return

    crime_id = crime_tree.item(selected_item[0])['values'][0]

    if messagebox.askyesno("Confirm", "Are you sure you want to delete this crime?"):
        query = "DELETE FROM crimes WHERE id = %s;"
        execute_query(query, (crime_id,))

        messagebox.showinfo("Success", f"Crime deleted: {crime_id}")
        refresh_crime_list()


def refresh_criminal_list():
    for item in criminal_tree.get_children():
        criminal_tree.delete(item)

    query = "SELECT * FROM criminals;"
    criminals = fetch_query(query)

    for criminal in criminals:
        criminal_tree.insert("", "end", values=(criminal['serial_number'], criminal['name']))

    # Update the criminal selector combobox
    criminal_selector['values'] = [f"{c['serial_number']} - {c['name']}" for c in criminals]


def refresh_crime_list():
    for item in crime_tree.get_children():
        crime_tree.delete(item)

    query = """
    SELECT crimes.id, crimes.crime, criminals.name
    FROM crimes
    JOIN criminals ON crimes.serial_number = criminals.serial_number;
    """
    crimes = fetch_query(query)

    for crime in crimes:
        crime_tree.insert("", "end", values=(crime['id'], crime['crime'], crime['name']))


def add_crime():
    selected_criminal = criminal_selector.get()
    if not selected_criminal:
        messagebox.showerror("Error", "Please select a criminal")
        return

    serial_number = selected_criminal.split(' - ')[0]
    crime = crime_entry.get()
    date = date_entry.get_date()
    notes = notes_entry.get("1.0", tk.END).strip()

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
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            query = """INSERT INTO evidence (crime_id, image_data) VALUES (%s, %s);"""
            execute_query(query, (crime_id, image_b64))

    messagebox.showinfo("Success", f"Crime added with ID: {crime_id}")
    refresh_crime_list()


def update_crime():
    selected_item = crime_tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a crime to update")
        return

    crime_id = crime_tree.item(selected_item[0])['values'][0]
    selected_criminal = criminal_selector.get()
    if not selected_criminal:
        messagebox.showerror("Error", "Please select a criminal")
        return

    serial_number = selected_criminal.split(' - ')[0]
    crime = crime_entry.get()
    date = date_entry.get_date()
    notes = notes_entry.get("1.0", tk.END).strip()

    if not crime or not date:
        messagebox.showerror("Error", "Please fill all fields")
        return

    query = """
    UPDATE crimes
    SET serial_number = %s, crime = %s, date = %s, notes = %s
    WHERE id = %s;
    """
    execute_query(query, (serial_number, crime, date, notes, crime_id))

    # Update evidence
    query = "DELETE FROM evidence WHERE crime_id = %s;"
    execute_query(query, (crime_id,))

    for image_path in evidence_paths:
        image_data = Image.open(image_path)
        # Convert the image to base64
        dat = io.BytesIO()
        image_data.save(dat, format='PNG')
        dat.seek(0)
        data = dat.getvalue()
        data = base64.b64encode(data).decode('utf-8')

        query = """
        INSERT INTO evidence (crime_id, image_data)
        VALUES (%s, %s);
        """
        execute_query(query, (crime_id, data))

    messagebox.showinfo("Success", f"Crime updated: {crime_id}")
    refresh_crime_list()


def select_evidence():
    global evidence_paths
    evidence_paths = list(filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg *.png")]))
    evidence_label.config(text=f"{len(evidence_paths)} images selected")

def view_crime():
    selected_item = crime_tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a crime to view")
        return

    crime_id = crime_tree.item(selected_item[0])['values'][0]

    query = "SELECT * FROM crimes WHERE id = %s;"
    crime = fetch_query(query, (crime_id,))[0]

    query = "SELECT image_data FROM evidence WHERE crime_id = %s;"
    evidence = fetch_query(query, (crime_id,))

    if crime:
        # Fill in the fields
        fill_crime_fields(crime)

        # Display evidence
        for i, img_data in enumerate(evidence):
            image = Image.open(io.BytesIO(base64.b64decode(img_data['image_data'])))
            image.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(image)

            top = tk.Toplevel()
            top.title(f"Evidence {i + 1}")
            label = tk.Label(top, image=photo)
            label.image = photo
            label.pack()
    else:
        messagebox.showerror("Error", "Crime not found")

def fill_crime_fields(crime):
    # Set the criminal selector
    query = "SELECT name FROM criminals WHERE serial_number = %s;"
    criminal = fetch_query(query, (crime['serial_number'],))[0]
    criminal_selector.set(f"{crime['serial_number']} - {criminal['name']}")

    # Set the crime entry
    crime_entry.delete(0, tk.END)
    crime_entry.insert(0, crime['crime'])

    # Set the date entry
    date_entry.set_date(crime['date'])

    # Set the notes entry
    notes_entry.delete('1.0', tk.END)
    notes_entry.insert('1.0', crime['notes'])

    # Clear evidence selection
    global evidence_paths
    evidence_paths = []
    evidence_label.config(text="No images selected")


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
ttk.Label(criminals_tab, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
name_entry = ttk.Entry(criminals_tab)
name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

ttk.Label(criminals_tab, text="Date of Birth:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
dob_entry = DateEntry(criminals_tab, date_pattern='yyyy-mm-dd')
dob_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)

ttk.Label(criminals_tab, text="Race:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
race_entry = ttk.Entry(criminals_tab)
race_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

married_var = tk.BooleanVar()
ttk.Checkbutton(criminals_tab, text="Married", variable=married_var).grid(row=3, column=0, columnspan=2, padx=5, pady=5,
                                                                          sticky=tk.W)

ttk.Button(criminals_tab, text="Add Criminal", command=add_criminal).grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
ttk.Button(criminals_tab, text="Update Criminal", command=update_criminal).grid(row=4, column=1, padx=5, pady=5,
                                                                                sticky=tk.W)
ttk.Button(criminals_tab, text="Delete Criminal", command=delete_criminal).grid(row=4, column=2, padx=5, pady=5,
                                                                                sticky=tk.W)

criminal_tree = ttk.Treeview(criminals_tab, columns=("serial_number", "name"), show="headings")
criminal_tree.heading("serial_number", text="Serial Number")
criminal_tree.heading("name", text="Name")
criminal_tree.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky=tk.NSEW)


# Crimes tab
ttk.Label(crimes_tab, text="Criminal:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
criminal_selector = ttk.Combobox(crimes_tab, state="readonly")
criminal_selector.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

ttk.Label(crimes_tab, text="Crime:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
crime_entry = ttk.Entry(crimes_tab)
crime_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)

ttk.Label(crimes_tab, text="Date:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
date_entry = DateEntry(crimes_tab, date_pattern='yyyy-mm-dd')
date_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

ttk.Label(crimes_tab, text="Notes:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
notes_entry = tk.Text(crimes_tab, height=3, width=20)
notes_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)

ttk.Button(crimes_tab, text="Select Evidence", command=select_evidence).grid(row=4, column=0, padx=5, pady=5,
                                                                             sticky=tk.W)
evidence_label = ttk.Label(crimes_tab, text="No images selected")
evidence_label.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

ttk.Button(crimes_tab, text="Add Crime", command=add_crime).grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
ttk.Button(crimes_tab, text="Update Crime", command=update_crime).grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)
ttk.Button(crimes_tab, text="Delete Crime", command=delete_crime).grid(row=5, column=2, padx=5, pady=5, sticky=tk.W)

crime_tree = ttk.Treeview(crimes_tab, columns=("id", "crime", "criminal"), show="headings")
crime_tree.heading("id", text="ID")
crime_tree.heading("crime", text="Crime")
crime_tree.heading("criminal", text="Criminal")
crime_tree.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky=tk.NSEW)
crime_tree.bind('<<TreeviewSelect>>', lambda e: view_crime())

ttk.Button(crimes_tab, text="View Crime", command=view_crime).grid(row=7, column=0, columnspan=3, padx=5, pady=5,
                                                                   sticky=tk.W)

# Configure column weights
criminals_tab.grid_columnconfigure(1, weight=1)
crimes_tab.grid_columnconfigure(1, weight=1)

# Initialize
# delete_evidences()
startup()
create_tables()
refresh_criminal_list()
refresh_crime_list()

evidence_paths = []

# Center window
root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

# Start the main event loop
root.mainloop()
