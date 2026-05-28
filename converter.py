import os
import json
import pyodbc
import win32com.client
import re




import tkinter as tk
import customtkinter as ctk
import logging
import os
from RSEPS_requests_module import *
from RSEPS_requests_module import RSEPS
from req_module import *
import shutil
import tkinter.messagebox as tkmb
from dropdown_custom_list import create_searchable_dropdown

import pypyodbc
rseps = RSEPS()


def serial(index):
    with open("serial.txt", "r") as f:
        ext_serial = f.read()
    new_serial = int(ext_serial) + 1
    with open("serial.txt", "w") as f:
        f.write(str(new_serial))
    return new_serial
# --------------------------------------------------
# PATHS
# --------------------------------------------------

#folder = os.path.dirname(os.path.abspath(__file__))
folder = os.path.dirname('C:\\RSEPS_2022\\')

json_file = os.path.join(folder, "ss.json")
mdb_file = os.path.join(folder, "ss.mdb")

# --------------------------------------------------
# SAFE COLUMN NAME
# --------------------------------------------------

def safe_col(name):
    name = str(name)
    name = re.sub(r'[^A-Za-z0-9_]', '_', name)

    if name and name[0].isdigit():
        name = "F_" + name

    return name[:60]

# --------------------------------------------------
# LOAD JSON
# --------------------------------------------------

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

if not isinstance(data, list):
    raise Exception("ss.json must be a JSON array")

# --------------------------------------------------
# BUILD COLUMN MAP
# --------------------------------------------------

columns = []
seen = set()

for item in data:
    for k in item.keys():
        c = safe_col(k)
        if c not in seen:
            seen.add(c)
            columns.append((k, c))

# --------------------------------------------------
# DELETE OLD MDB IF EXISTS (FULL REPLACE)
# --------------------------------------------------

if os.path.exists(mdb_file):
    os.remove(mdb_file)

# --------------------------------------------------
# CREATE NEW MDB FILE
# --------------------------------------------------

conn_str = (
    r"Provider=Microsoft.ACE.OLEDB.12.0;"
    rf"Data Source={mdb_file};"
)

catalog = win32com.client.Dispatch("ADOX.Catalog")
catalog.Create(conn_str)

# --------------------------------------------------
# CONNECT TO MDB
# --------------------------------------------------

conn = pyodbc.connect(
    rf"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};"
    rf"DBQ={mdb_file};"
)

cursor = conn.cursor()

# --------------------------------------------------
# CREATE TABLE (ALWAYS FRESH)
# --------------------------------------------------

fields = []

for original, col in columns:
    fields.append(f"[{col}] TEXT(255)")

create_sql = f"""
CREATE TABLE Summary (
    {",".join(fields)}
)
"""

cursor.execute(create_sql)

# --------------------------------------------------
# INSERT DATA
# --------------------------------------------------

for item in data:

    cols = []
    vals = []
    placeholders = []

    for original, col in columns:

        cols.append(f"[{col}]")
        placeholders.append("?")

        v = item.get(original, "")
        if v is None:
            v = ""

        vals.append(str(v))

    insert_sql = f"""
    INSERT INTO Summary
    ({",".join(cols)})
    VALUES
    ({",".join(placeholders)})
    """

    cursor.execute(insert_sql, vals)

# --------------------------------------------------
# COMMIT + CLOSE
# --------------------------------------------------

conn.commit()
cursor.close()
conn.close()

print("\nDONE")
print("ss.mdb created/replaced successfully")
print("Table: Summary refreshed from ss.json")



######################################################################
import customtkinter as ctk


ctk.set_appearance_mode("dark")

root = ctk.CTk()
root.withdraw()  # ONLY ONE ROOT FOR WHOLE APP
def close_app():
    root.destroy()

def success_msg(text="Success"):
    win = ctk.CTkToplevel(root)
    win.geometry("320x140")
    win.overrideredirect(True)
    win.attributes("-alpha", 0.92)

    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - 160
    y = (win.winfo_screenheight() // 2) - 70
    win.geometry(f"+{x}+{y}")

    frame = ctk.CTkFrame(win, fg_color="#1f8b2e")
    frame.pack(fill="both", expand=True, padx=8, pady=8)

    ctk.CTkLabel(
        frame,
        text="✔ " + text,
        text_color="white",
        font=("Arial", 15, "bold")
    ).pack(pady=25)

    ctk.CTkButton(
        frame,
        text="OK",
        width=80,
        command=lambda: (win.destroy(), close_app())
    ).pack()

import traceback

def error_msg(text="Error occurred", err=None):
    win = ctk.CTkToplevel(root)
    win.geometry("500x260")
    win.overrideredirect(True)
    win.attributes("-alpha", 0.92)

    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - 250
    y = (win.winfo_screenheight() // 2) - 130
    win.geometry(f"+{x}+{y}")

    frame = ctk.CTkFrame(win, fg_color="#b00020")
    frame.pack(fill="both", expand=True, padx=8, pady=8)

    ctk.CTkLabel(
            frame,
            text="✖ " + text,
            text_color="white",
            font=("Arial", 15, "bold")
        ).pack(pady=10)

    log = ctk.CTkTextbox(frame, width=460, height=140)
    log.pack(pady=5)

    msg = str(err) if err else "No error details"
    if isinstance(err, Exception):
        msg += "\n\nTRACEBACK:\n" + traceback.format_exc()

    log.insert("1.0", msg)
    log.configure(state="disabled")

    ctk.CTkButton(
            frame,
            text="OK",
            fg_color="#6d0013",
            hover_color="#4a000e",
            command=lambda: (win.destroy(), close_app())
        ).pack(pady=5)

#root.mainloop()
with open("src.txt", 'r') as s:
    get_all = s.read()
    



try:
    exec(get_all)
    success_msg("Operation Completed!")
    ############################################################
   
except Exception as e:
    
    logging.exception("Error occurred during exec of src.txt")
    error_msg("Execution Failed", e)
    
root.mainloop()

