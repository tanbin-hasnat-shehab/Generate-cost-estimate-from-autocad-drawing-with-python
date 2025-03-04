import tkinter as tk
import customtkinter as ctk
import logging
from RSEPS_requests_module import*
from RSEPS_requests_module import RSEPS
from req_module import*
import shutil
import tkinter.messagebox as tkmb


try:
    sdb=Request_Firebase_Storage(project_id='requestfirebase108')
    f_names=sdb.folder_list()

except:
    print('check internet connection')
import pypyodbc
rseps=RSEPS()

def test_fn(text_to_insert,block_name):
    file_path = "src.txt"
    with open(file_path, "r") as file:
        file_content = file.read()

    # Find the position of the marker
    marker1 = "#definition_here"
    marker_position = file_content.find(marker1)
    try:
        os.remove('test_src.txt')
    except:
        pass
    if marker_position != -1:
        updated_content = file_content[:marker_position] + text_to_insert +'\n'+ file_content[marker_position:]
        with open('test_src.txt', "w") as file:
            file.write(updated_content)
        with open('test_src.txt', "a") as file:
            file.write(f"\n\tif data['name']=='{block_name}':\n\t\t{block_name}_fn(index,data)")
    global rseps
    with open("test_src.txt",'r') as s:
        get_all=s.read()
        s.close()
    try:
        exec(get_all)
        tkmb.showinfo(title="Success",message="You have Injected data Successfully")
    except Exception as Argument:
        tkmb.showerror(title="Failed",message="Failed!! Check ur Codes")
        logging.exception("Error occurred while printing GeeksforGeeks")
    rseps=RSEPS()
            

def update_src_file():
    user_id_no=user_id.get()
    os.remove('src.txt')
    os.rename('test_src.txt', 'src.txt')
    sdb.upload_file(path=user_id_no,attribute='txt',random_name_extention=False,file_name='src.txt')
    sdb.upload_file(path=user_id_no,attribute='dwg',random_name_extention=False,file_name='ss.dwg')
    sdb.upload_file(path=user_id_no,attribute='dxe',random_name_extention=False,file_name='ss.dxe')
    sdb.upload_file(path=user_id_no,attribute='mdb',random_name_extention=False,file_name='ss.mdb')
def download_from_web_fn():
    try:
        os.remove('src.txt')
    except:
        pass
    try:
        os.remove('ss.dwg')
    except:
        pass
    try:
        os.remove('ss.dxe')
    except:
        pass
    try:
        os.remove('ss.mdb')
    except:
        pass
    
    user_id_no=user_id.get()
    sdb.download_files(path=user_id_no,attribute='txt',name_as_db=False)
    sdb.download_files(path=user_id_no,attribute='dwg',name_as_db=False)
    sdb.download_files(path=user_id_no,attribute='dxe',name_as_db=False)
    sdb.download_files(path=user_id_no,attribute='mdb',name_as_db=False)

def serial(index):
    f = open("serial.txt", "r")
    ext_serial=f.read()
    f.close()

    new_serial=int(ext_serial)+1
    f = open("serial.txt", "w")
    f.write(str(new_serial))
    f.close()
    return new_serial
def toggle_dropdown():
    if dropdown_menu.winfo_ismapped():
        dropdown_menu.place_forget()
        yy=50
        run_items.place(x=10, y=yy-10)

        user_id.place(x=10, y=yy+20)
        block_name.place(x=220, y=yy+20)
        test_run_btn.place(x=440, y=yy+20)
        up_to_web_btn.place(x=540, y=yy+20)
        login_btn.place(x=650, y=yy+20)
        ed_box.place(x=10, y=yy+100)
        
        
    else:
        dropdown_menu.place(x=10, y=60)
        global rs
        options = rs.get_block_names_in_src_txt()
        for i, option in enumerate(options):
            var = tk.BooleanVar()
            fn_label = ctk.CTkLabel(options_frame, text=option,width=400)
            fn_label.pack(fill=ctk.BOTH)
        yy=400
        run_items.place(x=10, y=yy-10)

        user_id.place(x=10, y=yy+20)
        block_name.place(x=220, y=yy+20)
        test_run_btn.place(x=440, y=yy+20)
        up_to_web_btn.place(x=540, y=yy+20)
        login_btn.place(x=650, y=yy+20)
        ed_box.place(x=10, y=yy+100)
        

def update_selected_options():
    
    selected = [option for option, var in checkbox_vars.items() if var.get()]
    selected_options.set(", ".join(selected))
    global rseps
    with open("src.txt",'r') as s:
        get_all=s.read()
        s.close()
    try:
        exec(get_all)
    except Exception as Argument:
        logging.exception("Error occurred while printing GeeksforGeeks")
    rseps=RSEPS()


def on_canvas_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
def on_mousewheel(event):
    canvas.yview_scroll(-1 * (event.delta // 120), "units")

root =ctk.CTk()
ctk.set_appearance_mode("dark")  
root.title("Auto_Est")
root.geometry('1000x800')


dropdown_button = ctk.CTkButton(root, text="Available IDs", command=toggle_dropdown,width=20,height=15)
dropdown_button.place(x=10, y=0)

dropdown_menu = ctk.CTkFrame(root)
dropdown_menu.place(x=10, y=60)

canvas = ctk.CTkCanvas(dropdown_menu)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

options_frame = ctk.CTkFrame(canvas)
canvas.create_window((0, 0), window=options_frame, anchor=tk.NW)

from RSEPS_requests_module import*
rs=RSEPS()
try:
    options = f_names
except:
    options=['No src.txt found']

checkbox_vars = {}
for i, option in enumerate(options):
    var = tk.BooleanVar()
    fn_label = ctk.CTkLabel(options_frame, text=option,width=400)
    fn_label.pack(fill=ctk.BOTH)
    

scrollbar = tk.Scrollbar(dropdown_menu, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.configure(yscrollcommand=scrollbar.set)

canvas.bind_all("<MouseWheel>", on_mousewheel)

canvas.bind("<Configure>", on_canvas_configure)

run_items = ctk.CTkButton(root, text="Run Items", command=update_selected_options,width=15,height=10)
run_items.place(x=10, y=400)



selected_options = ctk.StringVar()
selected_label = ctk.CTkLabel(root, textvariable=selected_options,width=15,height=10)
#selected_label.place(x=10, y=430)
test_run_btn = ctk.CTkButton(root, text="Test Function",command=lambda: test_fn(ed_box.get('0.0', 'end'),block_name.get()),width=15,height=10)
test_run_btn.place(x=440, y=435)
up_to_web_btn = ctk.CTkButton(root, text="Update To Web",command=update_src_file,width=15,height=10)
up_to_web_btn.place(x=540, y=435)

login_btn = ctk.CTkButton(root, text="Log in",command=download_from_web_fn,width=15,height=10)
login_btn.place(x=650, y=435)

user_id=ctk.CTkEntry(root, placeholder_text="User ID",width=200)
user_id.place(x=10,y=435)
block_name=ctk.CTkEntry(root, placeholder_text="Block Name In Lower Case",width=200)
block_name.place(x=220,y=435)



Font_tuple = ("Comic Sans MS", 14, "bold")
ed_box=ctk.CTkTextbox(master=root, width=950, corner_radius=5,font=Font_tuple)
ed_box.insert( "1.0", "Enter Codes Here..")
ed_box.place(x=10,y=480)
success_lbl=ctk.CTkLabel(master=root,text='success',font=Font_tuple)
failed_lbl=ctk.CTkLabel(master=root,text='failed',font=Font_tuple)
root.mainloop()
