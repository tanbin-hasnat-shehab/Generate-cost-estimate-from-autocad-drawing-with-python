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


try:
    sdb = Request_Firebase_Storage(project_id='requestfirebase108')
    f_names = sdb.folder_list()
except:
    print('check internet connection')

import pypyodbc
rseps = RSEPS()


def success_messege(msgs):
    success_bar = ctk.CTkLabel(
        master=root,
        text=msgs,
        fg_color="green",
        text_color="white",
        corner_radius=10,
        font=("Arial", 14),
        height=30
    )
    success_bar.place(x=500, y=100, anchor="s")
    root.after(3000, success_bar.destroy)


def test_fn(text_to_insert, block_name):
    file_path = "src.txt"
    with open(file_path, "r") as file:
        file_content = file.read()

    marker1 = "#definition_here"
    marker_position = file_content.find(marker1)
    try:
        os.remove('test_src.txt')
    except:
        pass
    if marker_position != -1:
        updated_content = file_content[:marker_position] + text_to_insert + '\n' + file_content[marker_position:]
        with open('test_src.txt', "w") as file:
            file.write(updated_content)
        with open('test_src.txt', "a") as file:
            file.write(f"\n\tif data['name']=='{block_name}':\n\t\t{block_name}_fn(index,data)")
    global rseps
    with open("test_src.txt", 'r') as s:
        get_all = s.read()
    try:
        exec(get_all)
        tkmb.showinfo(title="Success", message="You have Injected data Successfully")
    except Exception:
        tkmb.showerror(title="Failed", message="Failed!! Check your Codes")
        logging.exception("Error occurred during test_fn execution")
    rseps = RSEPS()


def update_src_file():
    user_id_no = user_id.get()
    if os.path.isfile("test_src.txt"):
        os.remove('src.txt')
        os.rename('test_src.txt', 'src.txt')
    sdb.upload_file(path=user_id_no, attribute='txt', random_name_extention=False, file_name='src.txt')
    sdb.upload_file(path=user_id_no, attribute='dwg', random_name_extention=False, file_name='ss.dwg')
    sdb.upload_file(path=user_id_no, attribute='dxe', random_name_extention=False, file_name='ss.dxe')
    sdb.upload_file(path=user_id_no, attribute='mdb', random_name_extention=False, file_name='ss.mdb')


def download_from_web_fn():
    for f in ['src.txt', 'ss.dwg', 'ss.dxe', 'ss.mdb']:
        try:
            os.remove(f)
        except:
            pass
    user_id_no = user_id.get()
    for ext in ['txt', 'dwg', 'dxe', 'mdb']:
        sdb.download_files(path=user_id_no, attribute=ext, name_as_db=False)
    success_messege('Downloaded')


def serial(index):
    with open("serial.txt", "r") as f:
        ext_serial = f.read()
    new_serial = int(ext_serial) + 1
    with open("serial.txt", "w") as f:
        f.write(str(new_serial))
    return new_serial


def toggle_dropdown():
    if dropdown_menu.winfo_ismapped():
        dropdown_menu.place_forget()
        yy = 50
    else:
        dropdown_menu.place(x=10, y=60)
        global rs
        options = rs.get_block_names_in_src_txt()
        for i, option in enumerate(options):
            ctk.CTkLabel(options_frame, text=option, width=400).pack(fill=ctk.BOTH)
        yy = 400

    run_items.place(x=10, y=yy - 10)
    user_id.place(x=10, y=yy + 20)
    block_name.place(x=220, y=yy + 20)
    test_run_btn.place(x=440, y=yy + 20)
    up_to_web_btn.place(x=540, y=yy + 20)
    login_btn.place(x=650, y=yy + 20)
    ed_box.place(x=10, y=yy + 100)


def update_selected_options():
    global rseps
    with open("src.txt", 'r') as s:
        get_all = s.read()
    try:
        exec(get_all)
        success_messege('Success')
    except Exception:
        logging.exception("Error occurred during exec of src.txt")
    rseps = RSEPS()


def on_canvas_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))


def on_mousewheel(event):
    canvas.yview_scroll(-1 * (event.delta // 120), "units")


root = ctk.CTk()
ctk.set_appearance_mode("dark")
root.title("Auto_Est")
root.geometry('1000x1000')

dropdown_button = ctk.CTkButton(root, text="Available IDs", command=toggle_dropdown, width=20, height=15)
dropdown_button.place(x=10, y=0)

dropdown_menu = ctk.CTkFrame(root)
dropdown_menu.place(x=10, y=60)

canvas = ctk.CTkCanvas(dropdown_menu)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

options_frame = ctk.CTkFrame(canvas)
canvas.create_window((0, 0), window=options_frame, anchor=tk.NW)

rs = RSEPS()
try:
    options = f_names
except:
    options = ['No src.txt found']

checkbox_vars = {}
for i, option in enumerate(options):
    var = tk.BooleanVar()
    ctk.CTkLabel(options_frame, text=option, width=400).pack(fill=ctk.BOTH)

scrollbar = tk.Scrollbar(dropdown_menu, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.configure(yscrollcommand=scrollbar.set)

canvas.bind_all("<MouseWheel>", on_mousewheel)
canvas.bind("<Configure>", on_canvas_configure)

run_items = ctk.CTkButton(root, text="Run Items", command=update_selected_options, width=15, height=10)
run_items.place(x=10, y=400)

selected_options = ctk.StringVar()
selected_label = ctk.CTkLabel(root, textvariable=selected_options, width=15, height=10)

test_run_btn = ctk.CTkButton(root, text="Test Function",
                             command=lambda: test_fn(ed_box.get('0.0', 'end'), block_name.get()), width=15, height=10)
test_run_btn.place(x=440, y=435)
up_to_web_btn = ctk.CTkButton(root, text="Update To Web", command=update_src_file, width=15, height=10)
up_to_web_btn.place(x=540, y=435)

login_btn = ctk.CTkButton(root, text="Log in", command=download_from_web_fn, width=15, height=10)
login_btn.place(x=650, y=435)

user_id = ctk.CTkEntry(root, placeholder_text="User ID", width=200)
user_id.place(x=10, y=435)
block_name = ctk.CTkEntry(root, placeholder_text="Block Name In Lower Case", width=200)
block_name.place(x=220, y=435)

Font_tuple = ("Times New Roman", 14)

color_options = {
    "White": "#FFFFFF",
    "Black": "#000000",
    "Dark Gray": "#2E2E2E",
    "Light Yellow": "#FFFFE0",
    "Solarized Dark": "#002b36",
    "Dracula": "#282a36"
}


def change_editor_bg(choice):
    ed_box.configure(fg_color=color_options[choice])


bg_color_menu = ctk.CTkOptionMenu(root, width=7, values=list(color_options.keys()), command=change_editor_bg)
bg_color_menu.set("Dark Gray")
bg_color_menu.place(x=710, y=430)

ed_box = ctk.CTkTextbox(master=root, width=950, height=400, corner_radius=5,
                        font=Font_tuple, fg_color=color_options["Dark Gray"])
ed_box.insert("1.0", "Enter Codes Here..")
ed_box.place(x=10, y=480)

# Floating input form
input_frame = ctk.CTkFrame(root, fg_color="transparent", corner_radius=0)
input_entries = []
placeholders = ["Item Code", "Description", "Length", "Width", "Height", "Deduction?", "No of Item"]
for i, placeholder in enumerate(placeholders):
    width = 100 if i < 2 else 50
    entry = ctk.CTkEntry(input_frame, placeholder_text=placeholder, width=width)
    entry.grid(row=0, column=i, padx=4, pady=5)
    input_entries.append(entry)
input_frame.place_forget()


def process_value(val: str, is_description=False, is_itemcode=False):
    if val is None:
        return "None"
    v = val.strip()
    if v == "":
        return "None"

    if is_itemcode:
        if v.startswith("@"):
            return v[1:]
        safe = v.replace("'", "\\'")
        return f"'{safe}'"

    if is_description:
        if v.startswith(":"):
            desc_text = v[1:].strip()
            return f'f"{desc_text} {{block[\'id\']}}"'
        if v.startswith("@"):
            return v[1:]
        try:
            if '.' in v or 'e' in v.lower():
                fnum = float(v)
                return str(int(fnum)) if fnum.is_integer() else str(fnum)
            else:
                inum = int(v)
                return str(inum)
        except Exception:
            safe = v.replace('"', '\\"')
            return f'"{safe}"'

    if v.startswith("@"):
        return v[1:]
    try:
        if '.' in v or 'e' in v.lower():
            fnum = float(v)
            return str(int(fnum)) if fnum.is_integer() else str(fnum)
        else:
            inum = int(v)
            return str(inum)
    except Exception:
        safe = v.replace("'", "\\'")
        return f"block['{safe}']"


def focus_next_entry(event, index):
    next_index = (index + 1) % len(input_entries)
    input_entries[next_index].focus()
    return "break"


def submit_form(event=None):
    try:
        values = []
        for i, entry in enumerate(input_entries):
            raw = entry.get()
            values.append(process_value(raw, is_description=(i == 1), is_itemcode=(i == 0)))
    except Exception:
        ed_box.insert("end", "⚠️ Error in processing values.\n")
        return

    description = values[1]
    dims = [values[2], values[3], values[4]]

    volume_parts = [d for d in dims if d != "None"]
    volume_expr = " * ".join(volume_parts) if volume_parts else "1"

    snippet = (
        "rseps.input_data(estimate_input=[ "
        f"{values[0]} , serial(index) , {values[5]} , "
        f"{description} , {dims[0]} , {dims[1]} , {dims[2]} , "
        f"{volume_expr} , {values[6]}*block['no_of_item'] ])\n"
    )

    cursor_pos = ed_box.index("insert")
    content = ed_box.get("0.0", cursor_pos)
    rseps_index = content.rfind("rseps")

    if rseps_index != -1:
        line = content.count("\n", 0, rseps_index)
        col = rseps_index - content.rfind("\n", 0, rseps_index) - 1
        rseps_start = f"{line + 1}.{col}"
        ed_box.delete(rseps_start, cursor_pos)
        ed_box.insert(rseps_start, snippet)

    for entry in input_entries:
        entry.delete(0, "end")
    input_frame.place_forget()


def check_for_trigger(event=None):
    cursor_pos = ed_box.index("insert")
    content = ed_box.get("0.0", cursor_pos)
    if content.endswith("rseps"):
        x, y = 100, 500
        input_frame.place(x=x, y=y)
        input_entries[0].focus()
    else:
        input_frame.place_forget()


ed_box.bind("<KeyRelease>", check_for_trigger)
for i, entry in enumerate(input_entries):
    entry.bind("<Tab>", lambda e, idx=i: focus_next_entry(e, idx))
    entry.bind("<Return>", submit_form)

success_lbl = ctk.CTkLabel(master=root, text='success', font=Font_tuple)
failed_lbl = ctk.CTkLabel(master=root, text='failed', font=Font_tuple)
dropdown_rate = create_searchable_dropdown(
    root,
    width=500,
    height=300,
    data_file="rates_full.json",
    x=450, y=50
)

root.mainloop()
