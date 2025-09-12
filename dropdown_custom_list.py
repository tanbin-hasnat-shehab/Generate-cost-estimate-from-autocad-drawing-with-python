import json
import os
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import textwrap


def create_searchable_dropdown(root, x, y, width=600, height=400, data_file="rates_full.json"):
    """
    Create a searchable dropdown grid widget with tooltip.

    Parameters:
        root   : parent CTk window/frame
        x, y   : position to place widget
        width  : total widget width
        height : total widget height
        data_file : JSON file path with item data
    """

    # ---------------- Load Items ----------------
    def load_items(path=data_file):
        if not os.path.exists(path):
            return []
        with open(path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception:
                return []
        items = []
        for obj in data:
            code = str(obj.get('ItemCode', '')).strip()
            desc = str(obj.get('Description', '')).strip()
            unit = str(obj.get('Unit', '')).strip()
            rate = str(obj.get('Rate', ''))

            # Wrap description into multiple lines for brief display
            brief = desc[:200] + ("..." if len(desc) > 200 else "")
            brief_lines = textwrap.wrap(brief, 80)
            brief_multiline = "\n".join(brief_lines)

            items.append({
                'code': code,
                'brief': brief_multiline,
                'full': desc,
                'unit': unit,
                'rate': rate,
                'brief_lines': len(brief_lines)
            })
        return items

    items = load_items(data_file)

    # ---------------- Container ----------------
    container = ctk.CTkFrame(root, width=width, height=height, corner_radius=12)
    container.place(x=x, y=y)

    # Space allocation
    search_bar_height = 40
    list_height = max(40, height - search_bar_height)

    # ---------------- Search Bar ----------------
    search_var = tk.StringVar()
    # pass width/height into constructor (CustomTk requirement)
    top_frame = ctk.CTkFrame(container, width=width, height=search_bar_height, corner_radius=8)
    top_frame.place(x=0, y=0)

    lbl = ctk.CTkLabel(top_frame, text="Search:", font=ctk.CTkFont(size=14, weight="bold"))
    lbl.pack(side='left', padx=(12, 6), pady=6)

    search_entry = ctk.CTkEntry(
        top_frame, textvariable=search_var,
        placeholder_text="Type to search...", font=ctk.CTkFont(size=13),
        width=max(100, width - 140), height=search_bar_height - 10
    )
    search_entry.pack(side='left', fill='x', expand=True, padx=(0, 12), pady=6)

    # ---------------- Treeview ----------------
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview",
                    background="#d1d1e2",
                    foreground="white",
                    fieldbackground="#ffffff",
                    bordercolor="#ffffff",
                    borderwidth=1,
                    font=("Consolas", 11))
    style.map('Treeview', background=[('selected', '#4a90e2')])

    frame = ctk.CTkFrame(container, width=width, height=list_height, corner_radius=8)
    frame.place(x=0, y=search_bar_height)

    cols = ("ItemCode", "Description", "Unit", "Rate")
    tree = ttk.Treeview(frame, columns=cols, show="headings", selectmode="browse")

    tree.heading("ItemCode", text="ItemCode")
    tree.heading("Description", text="Brief Description")
    tree.heading("Unit", text="Unit")
    tree.heading("Rate", text="Rate")

    # size columns relative to 'width'
    desc_col_width = max(100, width - 340)
    tree.column("ItemCode", width=120, anchor="w")
    tree.column("Description", width=desc_col_width, anchor="w")
    tree.column("Unit", width=100, anchor="center")
    tree.column("Rate", width=100, anchor="center")

    # insert items and set per-row height styles
    for idx, it in enumerate(items):
        tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
        iid = tree.insert("", "end",
                          values=(it['code'], it['brief'], it['unit'], it['rate']),
                          tags=(tag,))
        # compute rowheight and store in style for that row
        line_count = it['brief_lines'] if it['brief_lines'] > 0 else 1
        rowheight = max(20 * line_count, 25)
        style.configure(f"Custom.Treeview.Row{idx}", rowheight=rowheight)
        tree.item(iid, tags=(tag, f"Custom.Treeview.Row{idx}"))

    tree.tag_configure('evenrow', background="#2a2a40")
    tree.tag_configure('oddrow', background="#26263d")

    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side='right', fill='y')
    tree.pack(fill='both', expand=True)

    # ---------------- Tooltip ----------------
    tooltip = None

    def show_tooltip(event, text):
        nonlocal tooltip
        if tooltip:
            tooltip.destroy()
        tooltip = tk.Toplevel(root)
        tooltip.wm_overrideredirect(True)
        tooltip.attributes('-alpha', 0.85)
        tooltip.configure(bg="#ff0000")
        label = tk.Label(tooltip, text=text, justify='left', wraplength=600,
                         bg="#850000", fg="white", font=("Consolas", 11),
                         relief='solid', bd=1)
        label.pack(ipadx=8, ipady=4)
        x_ = root.winfo_pointerx() + 20
        y_ = root.winfo_pointery() + 20
        tooltip.wm_geometry(f"+{x_}+{y_}")

    def hide_tooltip(event=None):
        nonlocal tooltip
        if tooltip:
            tooltip.destroy()
            tooltip = None

    # ---------------- Logic ----------------
    IGNORE_KEYSYMS = {
        'Alt_L', 'Alt_R', 'Shift_L', 'Shift_R', 'Control_L', 'Control_R',
        'Tab', 'ISO_Left_Tab', 'Caps_Lock', 'Num_Lock', 'Scroll_Lock',
        'Meta_L', 'Meta_R'
    }

    match_indices = []
    current_match_pos = [0]

    def focus_match(index):
        children = tree.get_children()
        if index < 0 or index >= len(children):
            return
        tree.selection_remove(tree.selection())
        iid = children[index]
        tree.selection_set(iid)
        tree.see(iid)

    def on_search(event=None):
        # ignore modifier key releases so releasing Alt doesn't reset matches
        if event is not None and hasattr(event, "keysym") and event.keysym in IGNORE_KEYSYMS:
            return
        q = search_var.get().strip().lower()
        match_indices.clear()
        if q == '':
            return
        query_words = q.split()
        for i, it in enumerate(items):
            row_text = f"{it['code']} {it['brief']} {it['unit']} {it['rate']} {it['full']}".lower()
            if all(word in row_text for word in query_words):
                match_indices.append(i)
        if not match_indices:
            return
        current_match_pos[0] = 0
        focus_match(match_indices[0])

    def on_next_match(event=None):
        if not match_indices:
            return 'break'
        current_match_pos[0] = (current_match_pos[0] + 1) % len(match_indices)
        focus_match(match_indices[current_match_pos[0]])
        return 'break'

    def on_prev_match(event=None):
        if not match_indices:
            return 'break'
        # move backward with wrap-around
        current_match_pos[0] = (current_match_pos[0] - 1) % len(match_indices)
        focus_match(match_indices[current_match_pos[0]])
        return 'break'

    def on_hover(event):
        region = tree.identify("region", event.x, event.y)
        if region == "cell":
            row_id = tree.identify_row(event.y)
            if row_id:
                idx = tree.index(row_id)
                item = items[idx]
                full_text = f"ItemCode: {item['code']} | Unit: {item['unit']} | Rate: {item['rate']}\n\n{item['full']}"
                show_tooltip(event, full_text)
        else:
            hide_tooltip()

    def on_leave(event):
        hide_tooltip()

    def on_double_click(event=None):
        row_id = tree.identify_row(event.y)
        if not row_id:
            return
        idx = tree.index(row_id)
        item_code = items[idx]['code']
        search_var.set(item_code)
        root.clipboard_clear()
        root.clipboard_append(item_code)
        root.update()
        hide_tooltip()

    # ---------------- Bindings ----------------
    search_entry.bind('<KeyRelease>', on_search)
    search_entry.bind('<Tab>', on_next_match)
    search_entry.bind('<KeyRelease-Tab>', lambda e: 'break')

    # Bind Alt key presses to previous-match. Bind both on search_entry and tree so it works in either focus.
    search_entry.bind('<KeyPress-Alt_L>', on_prev_match)
    search_entry.bind('<KeyPress-Alt_R>', on_prev_match)
    tree.bind('<KeyPress-Alt_L>', on_prev_match)
    tree.bind('<KeyPress-Alt_R>', on_prev_match)

    # Also make Alt available when focus is elsewhere inside the dropdown frame
    container.bind('<KeyPress-Alt_L>', on_prev_match)
    container.bind('<KeyPress-Alt_R>', on_prev_match)

    tree.bind('<Motion>', on_hover)
    tree.bind('<Leave>', on_leave)
    tree.bind('<Double-1>', on_double_click)

    return container
