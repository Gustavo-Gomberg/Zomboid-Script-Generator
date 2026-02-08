import os
import tkinter as tk
from tkinter import ttk

# ===== Path Utilities =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def p(path):
    return os.path.join(BASE_DIR, path)

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


# ===== File Insertion Utility =====
def insert_inside_last_brace(filepath, block, module_name=None):
    if not os.path.exists(filepath):
        header = f"module {module_name}\n{{\n    imports {{\n        Base\n    }}\n\n" if module_name else ""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(header + block + "\n}\n")
        return
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if block.strip() in content:
        return
    last_brace = content.rfind("}")
    if last_brace == -1:
        raise RuntimeError(f"Invalid file structure: {filepath}")
    new_content = content[:last_brace].rstrip() + "\n\n" + block.rstrip() + "\n" + content[last_brace:]
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)


# ===== GUI Setup =====
DARK_BG = "#2C2C2C"
DARK_FG = "#E7E7E7"
root = tk.Tk()
root.title("Project Zomboid - Consumables Creator")
root.geometry("800x800")
root.resizable(False, False)


# ===== Global Lists =====
toggle_buttons = []          
evolved_cbs_buttons = []    


# ===== Scrollable Frame Setup =====
canvas = tk.Canvas(root, bg=DARK_BG, highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

canvas.configure(yscrollcommand=scrollbar.set)

main_frame = tk.Frame(canvas, bg=DARK_BG)

main_frame_window = canvas.create_window(
    (0, 0),
    window=main_frame,
    anchor="nw"
)

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

def on_canvas_configure(event):
    canvas.itemconfig(main_frame_window, width=event.width)

main_frame.bind("<Configure>", on_frame_configure)
canvas.bind("<Configure>", on_canvas_configure)

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
main_frame.bind("<Configure>", on_frame_configure)

def _on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
canvas.bind_all("<MouseWheel>", _on_mousewheel) 


# ===== Title and Credits =====
tk.Label(main_frame, text="Project Zomboid - Consumables Creator",
         font=("Segoe UI", 12, "bold"), bg=DARK_BG, fg=DARK_FG).pack(pady=10)

tk.Label(main_frame, 
         text="Made with ChatGPT by TehaGP for Project Zomboid Build 42.13.2",
         font=("Segoe UI", 8), bg=DARK_BG, fg="#ff5555").pack(side="top", anchor="n", pady=5)


# ===== Toggle Fullscreen =====
is_fullscreen = False

def toggle_fullscreen(event=None):
    global is_fullscreen
    is_fullscreen = not is_fullscreen
    root.attributes("-fullscreen", is_fullscreen)

    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

    if is_fullscreen:
        canvas_width = root.winfo_width()
        content_width = main_frame.winfo_reqwidth()
        x_offset = max((canvas_width - content_width)//2, 0)
        canvas.coords(main_frame_window, x_offset, 0)
    else:
        canvas.coords(main_frame_window, 0, 0)
        canvas.configure(scrollregion=canvas.bbox("all"))

def exit_fullscreen(event=None):
    global is_fullscreen
    is_fullscreen = False
    root.attributes("-fullscreen", False)
    canvas.coords(main_frame_window, 0, 0)
    canvas.configure(scrollregion=canvas.bbox("all"))


# ===== Exit Fullscreen =====
def exit_fullscreen(event=None):
    root.attributes('-fullscreen', False)
    root.state('normal')


# ===== Tooltip for Fullscreen =====
fullscreen_label = tk.Label(
    root,
    text="Press F11 to toggle Fullscreen. Press Esc to Exit",
    font=("Segoe UI", 8, "bold"),
    bg=DARK_BG,
    fg="#AAAAAA"
)
fullscreen_label.place(relx=1.0, y=5, x=-20, anchor="ne")


# ===== Bind Keys =====
root.bind("<F11>", toggle_fullscreen)
root.bind("<Escape>", exit_fullscreen)


# ===== Tooltip Class =====
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True) 
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify="left",
                         background="#ffffe0", relief="solid", borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=5, ipady=3)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


# ===== Input Fields =====
fields_wrapper = tk.Frame(main_frame, bg=DARK_BG)
fields_wrapper.pack(pady=5, fill="x")
fields_frame = tk.Frame(fields_wrapper, bg=DARK_BG)
fields_frame.pack(anchor="center")

def add_row(label_text, default=""):
    row = tk.Frame(fields_frame, bg=DARK_BG)
    row.pack(pady=4, fill="x")
    tk.Label(row, text=label_text, width=20, anchor="e", bg=DARK_BG, fg=DARK_FG).pack(side="left")
    entry = tk.Entry(row, width=40, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG)
    entry.insert(0, default)
    entry.pack(side="left", fill="x", expand=True, padx=(5,5))
    entry.xview_moveto(0)
    return entry            

ttk.Separator(fields_frame, orient="horizontal").pack(fill="x", pady=8)


# ===== Generic Row with Toggle =====
def add_row_with_toggle(label_text, default=""):
    row = tk.Frame(fields_frame, bg=DARK_BG)
    row.pack(pady=2, anchor="center") 

    tk.Label(row, text=label_text, width=20, anchor="e", bg=DARK_BG, fg=DARK_FG).pack(side="left", padx=5)

    entry = tk.Entry(row, width=20, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG)
    entry.pack(side="left", padx=5)
    entry.insert(0, default)        
    entry.config(state="disabled")

    active_var = tk.BooleanVar(value=False) 

    def toggle_active():
        state = "normal" if active_var.get() else "disabled"
        entry.config(state=state)

    tk.Checkbutton(row, text="Active", variable=active_var, command=toggle_active,
                   takefocus=False, bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG).pack(side="left", padx=5)

    return entry, active_var


# ===== Stat Rows with Dropdown =====
def add_stat_dropdown_row(parent_frame, label_text):
    frame = tk.Frame(parent_frame, bg=DARK_BG)
    frame.pack(pady=2, fill="x")

    tk.Label(frame, text=label_text, width=20, anchor="e", bg=DARK_BG, fg=DARK_FG).pack(side="left")

    entry = tk.Entry(frame, width=20, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG)
    entry.pack(side="left", padx=5)

    choice_var = tk.StringVar(value="Inactive")
    dropdown = ttk.Combobox(frame, textvariable=choice_var,
                            values=["Inactive", "Increase", "Decrease"],
                            width=10, state="readonly",
                            takefocus=0)
    dropdown.pack(side="left", padx=5)

    def update_entry_state(event=None):
        if choice_var.get() == "Inactive":
            entry.config(state="disabled")
            entry.delete(0, tk.END)
        else:
            entry.config(state="normal")

    dropdown.bind("<<ComboboxSelected>>", update_entry_state)
    update_entry_state()

    return entry, choice_var


# ===== Decrease-Only Stat Rows =====
def add_decrease_only_row(parent_frame, label_text):
    frame = tk.Frame(parent_frame, bg=DARK_BG)
    frame.pack(pady=2, fill="x")
    tk.Label(frame, text=label_text, width=20, anchor="e", bg=DARK_BG, fg=DARK_FG).pack(side="left")
    entry = tk.Entry(frame, width=20, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG, state="disabled")
    entry.pack(side="left", padx=5)
    active_var = tk.BooleanVar(value=False)

    def toggle_active():
        state = "normal" if active_var.get() else "disabled"
        entry.config(state=state)
        if state == "disabled":
            entry.delete(0, tk.END)

    tk.Checkbutton(frame, text="Active", variable=active_var, command=toggle_active,
                   takefocus=False, bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG).pack(side="left", padx=4)
    return entry, active_var


# ===== Basic Info Fields =====
entry_module = add_row("Module Name:")
ToolTip(entry_module, "The name of your module. Usually lowercase, no spaces.")

entry_item = add_row("Item Internal Name:")
ToolTip(entry_item, "Internal identifier for the item. Used in scripts. No spaces or special characters.")

entry_category = add_row("Display Category:")
ToolTip(entry_category, "Category in the game. Example: Food, Weapons, Tools.")

entry_itemtype = add_row("Item Type:")
ToolTip(entry_itemtype, "The base item type. Example: Base:Food, Base:FirstAid, etc.")

entry_weight = add_row("Weight:")
ToolTip(entry_weight, "Item weight in the game. Use numbers only.")

entry_ingame = add_row("Item In-Game Name:")
ToolTip(entry_ingame, "The name that players will see in-game. It can have spaces and capitalization.")

entry_asset = add_row("Model / Texture / Icon:")
ToolTip(entry_asset, "Specify your model, texture, and icon files here.")

ttk.Separator(fields_frame, orient="horizontal").pack(fill="x", pady=8)


# ===== Specialized Fields with Toggles =====
entry_foodtype, foodtype_active = add_row_with_toggle("FoodType:")
ToolTip(entry_foodtype, "Type of food item. Example: NoExplicit, Egg, Berry, Vegetables.")

entry_eattype, eattype_active = add_row_with_toggle("EatType:")
ToolTip(entry_eattype, "Defines the eating animation. Example: EatSmall, CanDrink, EatOffStick.")

entry_cookingsound, cookingsound_active = add_row_with_toggle("CookingSound:")
ToolTip(entry_cookingsound, "Sound played when cooking this item. Example: FryingFood, BoilingFood.")

entry_eatingsound, eatingsound_active = add_row_with_toggle("CustomEatSound:")
ToolTip(entry_eatingsound, "Sound played when the item is eaten. Example: EatingCrispy, EatingMushy.")


hunger_frame = tk.Frame(fields_frame, bg=DARK_BG); hunger_frame.pack()
thirst_frame = tk.Frame(fields_frame, bg=DARK_BG); thirst_frame.pack()
unhappy_frame = tk.Frame(fields_frame, bg=DARK_BG); unhappy_frame.pack()
stress_frame = tk.Frame(fields_frame, bg=DARK_BG); stress_frame.pack()
boredom_frame = tk.Frame(fields_frame, bg=DARK_BG); boredom_frame.pack()
fatigue_frame = tk.Frame(fields_frame, bg=DARK_BG); fatigue_frame.pack()
endurance_frame = tk.Frame(fields_frame, bg=DARK_BG); endurance_frame.pack()
flu_frame = tk.Frame(fields_frame, bg=DARK_BG); flu_frame.pack()
pain_frame = tk.Frame(fields_frame, bg=DARK_BG); pain_frame.pack()
sickness_frame = tk.Frame(fields_frame, bg=DARK_BG); sickness_frame.pack()
infection_frame = tk.Frame(fields_frame, bg=DARK_BG); infection_frame.pack()


ttk.Separator(hunger_frame, orient="horizontal").pack(fill="x", pady=8)

entry_hunger, hunger_choice = add_stat_dropdown_row(hunger_frame, "HungerChange:")
ToolTip(entry_hunger.master.children['!combobox'], 
        "Decrease: reduces hunger (fills you up)\nIncrease: increases hunger")

entry_thirst, thirst_choice = add_stat_dropdown_row(thirst_frame, "ThirstChange:")
ToolTip(entry_thirst.master.children['!combobox'], 
        "Decrease: reduces thirst (quenches you)\nIncrease: increases thirst")

entry_unhappy, unhappy_choice = add_stat_dropdown_row(unhappy_frame, "UnhappyChange:")
ToolTip(entry_unhappy.master.children['!combobox'], 
        "Decrease: reduces unhappiness\nIncrease: increases unhappiness")

entry_stress, stress_choice = add_stat_dropdown_row(stress_frame, "StressChange:")
ToolTip(entry_stress.master.children['!combobox'], 
        "Decrease: reduces stress\nIncrease: increases stress")

entry_boredom, boredom_choice = add_stat_dropdown_row(boredom_frame, "BoredomChange:")
ToolTip(entry_boredom.master.children['!combobox'], 
        "Decrease: reduces boredom\nIncrease: increases boredom")

entry_fatigue, fatigue_choice = add_stat_dropdown_row(fatigue_frame, "FatigueChange:")
ToolTip(entry_fatigue.master.children['!combobox'], 
        "Decrease: reduces fatigue\nIncrease: increases fatigue")

entry_endurance, endurance_choice = add_stat_dropdown_row(endurance_frame, "EnduranceChange:")
ToolTip(entry_endurance.master.children['!combobox'], 
        "Decrease: reduces endurance\nIncrease: increases endurance")

entry_flu, flu_active = add_decrease_only_row(flu_frame, "FluReduction:")
ToolTip(entry_flu, "Reduces the flu status when consumed.")

entry_pain, pain_active = add_decrease_only_row(pain_frame, "PainReduction:")
ToolTip(entry_pain, "Reduces the pain status when consumed.")

entry_food_sick, food_sick_active = add_decrease_only_row(sickness_frame, "ReduceFoodSickness:")
ToolTip(entry_food_sick, "Reduces the food sickness level.")

entry_infection, infection_active = add_decrease_only_row(infection_frame, "ReduceInfectionPower:")
ToolTip(entry_infection, "Reduces infection power.")

ttk.Separator(infection_frame, orient="horizontal").pack(fill="x", pady=8)

entry_poisonpower, poisonpower_active = add_decrease_only_row(infection_frame, "PoisonPower:")
ToolTip(entry_poisonpower, "Determines how poisonous the item is.")

entry_usedelta, usedelta_active = add_decrease_only_row(infection_frame, "UseDelta:")
ToolTip(entry_usedelta, "Determines how much of the drainable item's value is spent on a single use.")

entry_herbalisttype, herbalisttype_active = add_row_with_toggle("HerbalistType:")
ToolTip(entry_herbalisttype, "To recognize an item with this parameter, you need to know the Herbalist recipe. Example: Mushroom, Berry, Poison.")

ttk.Separator(fields_frame, orient="horizontal").pack(fill="x", pady=8)

# ===== Nutrition Fields =====
def add_inline_row(fields):
    row = tk.Frame(fields_frame, bg=DARK_BG)
    row.pack(pady=0, anchor="center")
    entries = []
    for label_text, width in fields:
        tk.Label(row, text=label_text, bg=DARK_BG, fg=DARK_FG).pack(side="left", padx=(5,2))
        entry = tk.Entry(row, width=width, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG, state="disabled")
        entry.pack(side="left", padx=(0,8))
        entries.append(entry)
    active_var = tk.BooleanVar(value=False) 
    def toggle_active():
        state = "normal" if active_var.get() else "disabled"
        for entry in entries:
            entry.config(state=state)
        if state == "disabled":
            for entry in entries:
                entry.delete(0, tk.END)

    tk.Checkbutton(row, text="Active", variable=active_var, command=toggle_active,
                   takefocus=False, bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG).pack(side="left", padx=5)

    return (*entries, active_var)

entry_carbs, entry_proteins, entry_lipids, entry_calories, nutrition_active = add_inline_row([
    ("Carbohydrates:", 8),
    ("Proteins:", 8),
    ("Lipids:", 8),
    ("Calories:", 8),
])
ToolTip(entry_carbs, "Amount of carbohydrates in the item. Use numbers only.")
ToolTip(entry_proteins, "Amount of proteins in the item. Use numbers only.")
ToolTip(entry_lipids, "Amount of lipids/fats in the item. Use numbers only.")
ToolTip(entry_calories, "Total calories provided by the item. Use numbers only.")

ttk.Separator(fields_frame, orient="horizontal").pack(fill="x", pady=8)

# ===== Cooking and Perishable Fields =====
cook_perishable_frame = tk.Frame(fields_frame, bg=DARK_BG)
cook_perishable_frame.pack(pady=2, anchor="center")
iscookable_var = tk.BooleanVar(value=False)
perishable_var = tk.BooleanVar(value=False)

def toggle_cookable():
    state = "normal" if iscookable_var.get() else "disabled"
    minutes_to_cook_entry.config(state=state, takefocus=iscookable_var.get())
    minutes_to_burn_entry.config(state=state, takefocus=iscookable_var.get())
    if state == "disabled":
        minutes_to_cook_entry.delete(0, tk.END)
        minutes_to_burn_entry.delete(0, tk.END)

cook_check = tk.Checkbutton(
    cook_perishable_frame,
    text="Is Cookable:",
    variable=iscookable_var,
    command=toggle_cookable,
    bg=DARK_BG, fg=DARK_FG,
    selectcolor=DARK_BG,
    activebackground=DARK_BG,
    takefocus=False
)
cook_check.pack(side="left", padx=(5, 2))
ToolTip(cook_check, "If checked, this item can be cooked. Enables the cooking time entries.")

minutes_to_cook_entry = tk.Entry(
    cook_perishable_frame, width=6,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled", takefocus=False
)

minutes_to_burn_entry = tk.Entry(
    cook_perishable_frame, width=6,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled", takefocus=False
)

tk.Label(
    cook_perishable_frame,
    text="Minutes To Cook:",
    bg=DARK_BG, fg=DARK_FG
).pack(side="left", padx=(2, 2))
minutes_to_cook_entry.pack(side="left", padx=(0, 6))
ToolTip(minutes_to_cook_entry, "Time in minutes it takes to fully cook this item.")

tk.Label(
    cook_perishable_frame,
    text="Minutes To Burn:",
    bg=DARK_BG, fg=DARK_FG
).pack(side="left", padx=(2, 2))
minutes_to_burn_entry.pack(side="left", padx=(0, 15))
ToolTip(minutes_to_burn_entry, "Time in minutes before the cooked item burns. Must be greater than 'Minutes To Cook'.")



def toggle_perishable():
    state = "normal" if perishable_var.get() else "disabled"
    entry_days_fresh.config(state=state, takefocus=perishable_var.get())
    entry_days_rotten.config(state=state, takefocus=perishable_var.get())
    if state == "disabled":
        entry_days_fresh.delete(0, tk.END)
        entry_days_rotten.delete(0, tk.END)
        entry_days_fresh.insert(0, "0")
        entry_days_rotten.insert(0, "0")

perishable_check = tk.Checkbutton(
    cook_perishable_frame,
    text="Is Perishable:",
    variable=perishable_var,
    command=toggle_perishable,
    bg=DARK_BG, fg=DARK_FG,
    selectcolor=DARK_BG,
    activebackground=DARK_BG,
    takefocus=False
)
perishable_check.pack(side="left", padx=(5, 2))
ToolTip(perishable_check, "If checked, this item will spoil over time. Enables 'Days Fresh' and 'Days Rotten'.")


entry_days_fresh = tk.Entry(
    cook_perishable_frame, width=6,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled", takefocus=False
)
entry_days_fresh.insert(0, "0")

entry_days_rotten = tk.Entry(
    cook_perishable_frame, width=6,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled", takefocus=False
)
entry_days_rotten.insert(0, "0")

tk.Label(
    cook_perishable_frame,
    text="Days Fresh:",
    bg=DARK_BG, fg=DARK_FG
).pack(side="left", padx=(2, 2))
entry_days_fresh.pack(side="left", padx=(0, 6))
ToolTip(entry_days_fresh, "Number of in-game days this item stays fresh before starting to rot.")

tk.Label(
    cook_perishable_frame,
    text="Days Rotten:",
    bg=DARK_BG, fg=DARK_FG
).pack(side="left", padx=(2, 2))
entry_days_rotten.pack(side="left", padx=(0, 5))
ToolTip(entry_days_rotten, "Number of in-game days after which the item is completely rotten and useless.")

ttk.Separator(fields_frame, orient="horizontal").pack(fill="x", pady=8)

# ===== Replace Fields =====
replace_row = tk.Frame(fields_frame, bg=DARK_BG)
replace_row.pack(pady=2, anchor="center")

# ===== ReplaceOnCooked ======
replace_cooked_var = tk.BooleanVar(value=False)
entry_replace_cooked = tk.Entry(
    replace_row, width=28,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled", takefocus=False
)

def toggle_replace_cooked():
    if replace_cooked_var.get():
        iscookable_var.set(True)
        toggle_cookable()

    state = "normal" if replace_cooked_var.get() else "disabled"
    entry_replace_cooked.config(state=state, takefocus=replace_cooked_var.get())
    if state == "disabled":
        entry_replace_cooked.delete(0, tk.END)

replace_cooked_check = tk.Checkbutton(
    replace_row,
    text="ReplaceOnCooked:",
    variable=replace_cooked_var,
    command=toggle_replace_cooked,
    bg=DARK_BG, fg=DARK_FG,
    selectcolor=DARK_BG,
    activebackground=DARK_BG,
    takefocus=False
)
replace_cooked_check.pack(side="left", padx=(5, 2))
ToolTip(replace_cooked_check, "When checked, the item is replaced with this value when cooked.")

entry_replace_cooked.pack(side="left", padx=(0, 5))
ToolTip(entry_replace_cooked, "Internal item name to replace this item with when cooked.")

# ===== ReplaceOnRotten =====
replacerotten_var = tk.BooleanVar(value=False)
entry_replace_rotten = tk.Entry(
    replace_row, width=28,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled", takefocus=False
)

def toggle_replace_rotten():
    if replacerotten_var.get():
        perishable_var.set(True)
        toggle_perishable()

    state = "normal" if replacerotten_var.get() and perishable_var.get() else "disabled"
    entry_replace_rotten.config(state=state, takefocus=replacerotten_var.get() and perishable_var.get())
    if state == "disabled":
        entry_replace_rotten.delete(0, tk.END)

replace_check = tk.Checkbutton(
    replace_row,
    text="ReplaceOnRotten:",
    variable=replacerotten_var,
    command=toggle_replace_rotten,
    bg=DARK_BG, fg=DARK_FG,
    selectcolor=DARK_BG,
    activebackground=DARK_BG,
    takefocus=False
)
replace_check.pack(side="left", padx=(5, 2))
ToolTip(replace_check, "When checked, the item is replaced with this entry when it becomes rotten.")

entry_replace_rotten.pack(side="left", padx=(0, 20))
ToolTip(entry_replace_rotten, "Internal item name to replace this item with when it rots.")

# ===== ReplaceOnUse =====
use_sound_row = tk.Frame(fields_frame, bg=DARK_BG)
use_sound_row.pack(pady=2, anchor="center")

replace_use_var = tk.BooleanVar(value=False)
entry_replace_use = tk.Entry(
    use_sound_row, width=26,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled", takefocus=False
)

def toggle_replace_use():
    state = "normal" if replace_use_var.get() else "disabled"
    entry_replace_use.config(state=state, takefocus=replace_use_var.get())
    if state == "disabled":
        entry_replace_use.delete(0, tk.END)

replace_use_check = tk.Checkbutton(
    use_sound_row,
    text="ReplaceOnUse:",
    variable=replace_use_var,
    command=toggle_replace_use,
    bg=DARK_BG, fg=DARK_FG,
    selectcolor=DARK_BG,
    activebackground=DARK_BG,
    takefocus=False
)
replace_use_check.pack(side="left", padx=(5, 2))
ToolTip(replace_use_check, "When checked, the item is replaced with this value when used.")

entry_replace_use.pack(side="left", padx=(0, 20))
ToolTip(entry_replace_use, "Internal item name to replace this item with when used.")

ttk.Separator(fields_frame, orient="horizontal").pack(fill="x", pady=8)

# ===== Tags Field =====
tags_frame = tk.Frame(fields_frame, bg=DARK_BG)
tags_frame.pack(pady=4, fill="x")

tags_var = tk.BooleanVar(value=False)

entry_tags = tk.Entry(
    tags_frame, width=40,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled", takefocus=False
)

def toggle_tags():
    state = "normal" if tags_var.get() else "disabled"
    entry_tags.config(state=state, takefocus=tags_var.get())
    if state == "disabled":
        entry_tags.delete(0, tk.END)

tags_cb = tk.Checkbutton(
    tags_frame,
    text="Add Tags:",
    variable=tags_var,
    command=toggle_tags,
    bg=DARK_BG, fg=DARK_FG,
    selectcolor=DARK_BG,
    activebackground=DARK_BG,
    takefocus=False
)
tags_cb.pack(side="left", padx=5)
ToolTip(tags_cb, "Enable this to add custom tags to the item. Tags can affect gameplay or mods.")

entry_tags.pack(side="left", padx=5, fill="x", expand=True)
ToolTip(entry_tags, "Separated list of tags. Example: base:herbaltea;base:commonmallow")


# ===== Tooltip Field =====
tooltip_frame = tk.Frame(fields_frame, bg=DARK_BG)
tooltip_frame.pack(pady=4, fill="x")

tooltip_var = tk.BooleanVar(value=False)

entry_tooltip = tk.Entry(
    tooltip_frame, width=40,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled", takefocus=False
)

def toggle_tooltip():
    state = "normal" if tooltip_var.get() else "disabled"
    entry_tooltip.config(state=state, takefocus=tooltip_var.get())
    if state == "disabled":
        entry_tooltip.delete(0, tk.END)

tooltip_cb = tk.Checkbutton(
    tooltip_frame,
    text="Add Tooltip:",
    variable=tooltip_var,
    command=toggle_tooltip,
    bg=DARK_BG, fg=DARK_FG,
    selectcolor=DARK_BG,
    activebackground=DARK_BG,
    takefocus=False
)
tooltip_cb.pack(side="left", padx=5)
ToolTip(tooltip_cb, "Enable this to add a tooltip for the item. Tooltips appear in-game when hovering.")

entry_tooltip.pack(side="left", padx=5, fill="x", expand=True)
ToolTip(entry_tooltip, 'Example: "Tooltip_Mallow" located in Translation Files (ToolTip_EN)')


# ===== OnEat Field =====
oneat_frame = tk.Frame(fields_frame, bg=DARK_BG)
oneat_frame.pack(pady=4, fill="x")

oneat_var = tk.BooleanVar(value=False)

entry_oneat = tk.Entry(
    oneat_frame, width=40,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled", takefocus=False
)

def toggle_oneat():
    state = "normal" if oneat_var.get() else "disabled"
    entry_oneat.config(state=state, takefocus=oneat_var.get())
    if state == "disabled":
        entry_oneat.delete(0, tk.END)

oneat_cb = tk.Checkbutton(
    oneat_frame,
    text="Add OnEat:",
    variable=oneat_var,
    command=toggle_oneat,
    bg=DARK_BG, fg=DARK_FG,
    selectcolor=DARK_BG,
    activebackground=DARK_BG,
    takefocus=False
)
oneat_cb.pack(side="left", padx=5)
ToolTip(oneat_cb, "Enable this to add a custom OnEat script for this item. Requires a Lua function.")

entry_oneat.pack(side="left", padx=5, fill="x", expand=True)
ToolTip(entry_oneat, 'Enter the Lua function name to run on consumption. Example: "RecipeCodeOnEat_MyItem".')


# ===== CustomContextMenu Field =====
customcontextmenu_frame = tk.Frame(fields_frame, bg=DARK_BG)
customcontextmenu_frame.pack(pady=4, fill="x")

customcontextmenu_var = tk.BooleanVar(value=False)

entry_customcontextmenu = tk.Entry(
    customcontextmenu_frame, width=40,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled", takefocus=False
)

def toggle_customcontextmenu():
    state = "normal" if customcontextmenu_var.get() else "disabled"
    entry_customcontextmenu.config(state=state, takefocus=customcontextmenu_var.get())
    if state == "disabled":
        entry_customcontextmenu.delete(0, tk.END)

customcontextmenu_cb = tk.Checkbutton(
    customcontextmenu_frame,
    text="Add CustomContextMenu:",
    variable=customcontextmenu_var,
    command=toggle_customcontextmenu,
    bg=DARK_BG, fg=DARK_FG,
    selectcolor=DARK_BG,
    activebackground=DARK_BG,
    takefocus=False
)
customcontextmenu_cb.pack(side="left", padx=5)
ToolTip(customcontextmenu_cb, "Enable this to add a custom context menu for this item in-game.")

entry_customcontextmenu.pack(side="left", padx=5, fill="x", expand=True)
ToolTip(entry_customcontextmenu, 'Enter the Lua function or menu name. Example: "CustomContextMenu_MyItem".')


# ===== Additional Flags =====
flags_frame = tk.Frame(fields_frame, bg=DARK_BG)
flags_frame.pack(pady=2, fill="x")
fishing_var = tk.BooleanVar(value=False)
dangerous_raw_var = tk.BooleanVar(value=False)
badcold_var = tk.BooleanVar(value=False)
badmicrowave_var = tk.BooleanVar(value=False)
goodhot_var = tk.BooleanVar(value=False)
cantbefrozen_var = tk.BooleanVar(value=False)
spice_var = tk.BooleanVar(value=False)
packaged_var = tk.BooleanVar(value=False)
cannedfood_var = tk.BooleanVar(value=False)
canteat_var = tk.BooleanVar(value=False)
medical_var = tk.BooleanVar(value=False)
remove_unhappy_cooked_var = tk.BooleanVar(value=False)
remove_negative_effects_cooked_var = tk.BooleanVar(value=False)

SMALL_FONT = ("Segoe UI", 8)
ACTIVE_GREEN = "#2ecc71"
INACTIVE_BG = DARK_BG
SMALL_FONT = ("Segoe UI", 8)

def toggle_button(parent, text, var, width):
    btn = tk.Button(
        parent,
        text=text,
        width=width,
        font=SMALL_FONT,
        bg=INACTIVE_BG,
        fg=DARK_FG,
        relief="raised",
        bd=2
    )
    btn.pack(side="left", padx=1, pady=1)

    def on_click():
        var.set(not var.get())
        if var.get():
            btn.config(bg=ACTIVE_GREEN, relief="sunken")
        else:
            btn.config(bg=INACTIVE_BG, relief="raised")

    btn.config(command=on_click)


    on_click() if var.get() else btn.config(bg=INACTIVE_BG, relief="raised")

    return btn

ttk.Separator(fields_frame, orient="horizontal").pack(fill="x", pady=8)


# ===== Evolved Recipes =====
evolved_frame = tk.Frame(fields_frame, bg=DARK_BG)
evolved_frame.pack(pady=4, fill="x")

evolved_var = tk.BooleanVar(value=False)

tk.Label(evolved_frame, text="Evolved Recipe Name:", bg=DARK_BG, fg=DARK_FG).pack(side="left", padx=2)
evolved_name_entry = tk.Entry(
    evolved_frame, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled", width=25, takefocus=False
)
evolved_name_entry.pack(side="left", padx=0, fill="x", expand=True)
ToolTip(evolved_name_entry, "Internal name for the evolved recipe. Example: 'ChocolateCakeEvolved'.")

# Sweet and Salty frames
sweet_frame = tk.Frame(fields_frame, bg=DARK_BG)
sweet_frame.pack(pady=3, fill="x")
salty_frame = tk.Frame(fields_frame, bg=DARK_BG)
salty_frame.pack(pady=3, fill="x")

sweet_list = ["Pancakes","Muffin","ConeIcecream","Cake","PieSweet","Oatmeal","Toast"]
salty_list = ["Sandwich","Stir fry","Pasta","Taco","Burrito","Salad","Soup","Stew","Bread"]

sweet_var = tk.BooleanVar(value=False)
salty_var = tk.BooleanVar(value=False)

# "Mark All" toggles
def toggle_all_sweet():
    if evolved_var.get():
        for btn in evolved_cbs_buttons:
            if btn.cget("text") in sweet_list:
                btn.var.set(sweet_var.get())
                btn.config(bg=ACTIVE_GREEN if sweet_var.get() else INACTIVE_BG)

def toggle_all_salty():
    if evolved_var.get():
        for btn in evolved_cbs_buttons:
            if btn.cget("text") in salty_list:
                btn.var.set(salty_var.get())
                btn.config(bg=ACTIVE_GREEN if salty_var.get() else INACTIVE_BG)

sweet_toggle_cb = tk.Checkbutton(
    sweet_frame, text="Mark All Sweet", variable=sweet_var, command=toggle_all_sweet,
    bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG, state="disabled",
    takefocus=False
)
sweet_toggle_cb.pack(side="left", padx=5)
ToolTip(sweet_toggle_cb, "Check to mark all sweet recipes in this evolved recipe.")

salty_toggle_cb = tk.Checkbutton(
    salty_frame, text="Mark All Salty", variable=salty_var, command=toggle_all_salty,
    bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG, state="disabled",
    takefocus=False
)
salty_toggle_cb.pack(side="left", padx=5)
ToolTip(salty_toggle_cb, "Check to mark all salty recipes in this evolved recipe.")

evolved_cbs_buttons = []
for lst, frame in [(sweet_list, sweet_frame), (salty_list, salty_frame)]:
    for item_name in lst:
        var = tk.BooleanVar(value=False)
        btn = toggle_button(frame, item_name, var, width=max(len(item_name)//1 + 2, 8))
        btn.var = var
        btn.config(state="disabled", takefocus=False)
        ToolTip(btn, f"Include {item_name} in this evolved recipe.")
        evolved_cbs_buttons.append(btn)

def toggle_evolved():
    state = "normal" if evolved_var.get() else "disabled"
    evolved_name_entry.config(state=state, takefocus=evolved_var.get())
    for btn in evolved_cbs_buttons:
        btn.config(state=state)
    sweet_toggle_cb.config(state=state)
    salty_toggle_cb.config(state=state)

evolved_cb = tk.Checkbutton(
    evolved_frame,
    text="EvolvedRecipe:",
    variable=evolved_var,
    command=toggle_evolved,
    bg=DARK_BG,
    fg=DARK_FG,
    selectcolor=DARK_BG,
    activebackground=DARK_BG,
    takefocus=False
)
evolved_cb.pack(side="left", padx=5)
ToolTip(evolved_cb, "Enable to allow this item to evolve into another recipe when crafted.")

ttk.Separator(fields_frame, orient="horizontal").pack(fill="x", pady=8)

# Toggle Button Factory with Tooltips
def add_toggle_button(frame, text, var, size, tooltip_text):
    btn = toggle_button(frame, text, var, size)
    btn.var = var 
    toggle_buttons.append(btn)
    ToolTip(frame.winfo_children()[-1], tooltip_text)
    return btn

# ===== Flags Row 1 =====
flags_row = tk.Frame(fields_frame, bg=DARK_BG)
flags_row.pack(pady=2, anchor="center")

add_toggle_button(flags_row, "It's a Canned Food", cannedfood_var, 15, "Item is canned food.")
add_toggle_button(flags_row, "It's a Spice", spice_var, 8, "Marks item as a spice ingredient.")
add_toggle_button(flags_row, "It's Packaged", packaged_var, 11, "Item is packaged.")
add_toggle_button(flags_row, "It's a Medical Item", medical_var, 14, "Item is considered a medical item.")

# ===== Flags Row 2 =====
flags_row2 = tk.Frame(fields_frame, bg=DARK_BG)
flags_row2.pack(pady=2, anchor="center")

add_toggle_button(flags_row2, "Can't be Eaten", canteat_var, 12, "Prevents the item from being eaten.")
add_toggle_button(flags_row2, "Can't be Frozen", cantbefrozen_var, 13, "Item cannot be frozen.")
add_toggle_button(flags_row2, "Can be used as Fishing Lure", fishing_var, 24, "Item can be used as a fishing lure.")

# ===== Flags Row 3 =====
flags_row3 = tk.Frame(fields_frame, bg=DARK_BG)
flags_row3.pack(pady=2, anchor="center")
add_toggle_button(flags_row3, "It's Dangerous Raw", dangerous_raw_var, 16, "Eating raw can be dangerous.")
add_toggle_button(flags_row3, "It's Bad Microwaved", badmicrowave_var, 18, "Item quality decreases if microwaved.")
add_toggle_button(flags_row3, "It's Bad Cold", badcold_var, 12, "Item is unpleasant when cold.")
add_toggle_button(flags_row3, "It's Good Hot", goodhot_var, 12, "Item is pleasant when hot.")

# ===== Flags Row 4 =====
flags_row4 = tk.Frame(fields_frame, bg=DARK_BG)
flags_row4.pack(pady=2, anchor="center")
add_toggle_button(flags_row4, "Removes Unhappiness when Cooked", remove_unhappy_cooked_var, 33, "Cooking removes unhappiness effect.")
add_toggle_button(flags_row4, "Removes Negative Effects when Cooked", remove_negative_effects_cooked_var, 35, "Cooking removes all negative effects.")


ttk.Separator(fields_frame, orient="horizontal").pack(fill="x", pady=8)

# ===== Distribution File Checkbox + Chance =====
distribution_frame = tk.Frame(fields_frame, bg=DARK_BG)
distribution_frame.pack(pady=4, fill="x")

distribution_var = tk.BooleanVar(value=False)

# Label for Item Spawning Chance
label_spawning_chance = tk.Label(
    distribution_frame, text="Item Spawning Chance:", bg=DARK_BG, fg=DARK_FG
)

# Entry for distribution lists
entry_distribution_lists = tk.Entry(
    distribution_frame, width=40,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled", takefocus=False
)

# Entry for spawning chance
entry_spawning_chance = tk.Entry(
    distribution_frame, width=6,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled", takefocus=False
)
entry_spawning_chance.insert(0, "1")  # default value

def toggle_distribution():
    state = "normal" if distribution_var.get() else "disabled"
    entry_distribution_lists.config(state=state, takefocus=distribution_var.get())
    entry_spawning_chance.config(state=state, takefocus=distribution_var.get())
    if state == "disabled":
        entry_distribution_lists.delete(0, tk.END)
        entry_spawning_chance.delete(0, tk.END)
        entry_spawning_chance.insert(0, "1")  # reset default

distribution_cb = tk.Checkbutton(
    distribution_frame,
    text="Create Distribution File:",
    variable=distribution_var,
    command=toggle_distribution,
    bg=DARK_BG, fg=DARK_FG,
    selectcolor=DARK_BG,
    activebackground=DARK_BG,
    takefocus=False
)

# Pack widgets
distribution_cb.pack(side="left", padx=5)
entry_distribution_lists.pack(side="left", padx=5, fill="x", expand=True)

# Spawning chance label and entry next to each other
label_spawning_chance.pack(side="left", padx=(10,2))
entry_spawning_chance.pack(side="left", padx=2)

ToolTip(distribution_cb, "Check to generate a Distribution file. Enter distribution list names separated by commas.")
ToolTip(entry_distribution_lists, "Example: SchoolLockers,CafeteriaDrinks,ClassroomDesk,FridgeOffice,FridgeSoda")
ToolTip(entry_spawning_chance, "Enter a value for ItemSpawningChance (default is 1)")

# ===== Foraging Distribution Checkbox + Settings =====
foraging_frame = tk.Frame(fields_frame, bg=DARK_BG)
foraging_frame.pack(pady=4, fill="x")

foraging_var = tk.BooleanVar(value=False)

# Entries
entry_foraging_category = tk.Entry(
    foraging_frame, width=22,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled", takefocus=False
)

entry_foraging_min = tk.Entry(
    foraging_frame, width=4,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled", takefocus=False
)
entry_foraging_min.insert(0, "1")

entry_foraging_max = tk.Entry(
    foraging_frame, width=4,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled", takefocus=False
)
entry_foraging_max.insert(0, "1")

entry_foraging_skill = tk.Entry(
    foraging_frame, width=4,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled", takefocus=False
)
entry_foraging_skill.insert(0, "0")


def toggle_foraging():
    state = "normal" if foraging_var.get() else "disabled"

    for entry in (
        entry_foraging_category,
        entry_foraging_min,
        entry_foraging_max,
        entry_foraging_skill
    ):
        entry.config(state=state, takefocus=foraging_var.get())

    if state == "disabled":
        entry_foraging_category.delete(0, tk.END)

        entry_foraging_min.delete(0, tk.END)
        entry_foraging_min.insert(0, "1")

        entry_foraging_max.delete(0, tk.END)
        entry_foraging_max.insert(0, "1")

        entry_foraging_skill.delete(0, tk.END)
        entry_foraging_skill.insert(0, "0")


foraging_cb = tk.Checkbutton(
    foraging_frame,
    text="Add to Foraging List:",
    variable=foraging_var,
    command=toggle_foraging,
    bg=DARK_BG, fg=DARK_FG,
    selectcolor=DARK_BG,
    activebackground=DARK_BG,
    takefocus=False
)

# Pack layout
foraging_cb.pack(side="left", padx=5)

tk.Label(foraging_frame, text="Forage Category:", bg=DARK_BG, fg=DARK_FG).pack(side="left", padx=(6,2))
entry_foraging_category.pack(side="left", padx=2)

tk.Label(foraging_frame, text="Min:", bg=DARK_BG, fg=DARK_FG).pack(side="left", padx=(8,2))
entry_foraging_min.pack(side="left", padx=2)

tk.Label(foraging_frame, text="Max:", bg=DARK_BG, fg=DARK_FG).pack(side="left", padx=(8,2))
entry_foraging_max.pack(side="left", padx=2)

tk.Label(foraging_frame, text="Skill Level Required:", bg=DARK_BG, fg=DARK_FG).pack(side="left", padx=(8,2))
entry_foraging_skill.pack(side="left", padx=2)

# Tooltips
ToolTip(foraging_cb, "Check to add this item to the Foraging (Scavenge) system.")
ToolTip(entry_foraging_category, "Example: ForestGoods,MedicinalPlants,Trash,Insects")
ToolTip(entry_foraging_min, "Minimum amount found per forage roll.")
ToolTip(entry_foraging_max, "Maximum amount found per forage roll.")
ToolTip(entry_foraging_skill, "Required Foraging skill level (0 = no requirement).")
ttk.Separator(fields_frame, orient="horizontal").pack(fill="x", pady=8)


# ===== Buttons and Status =====
buttons_frame = tk.Frame(main_frame, bg=DARK_BG)
buttons_frame.pack(pady=10)
status_label = tk.Label(main_frame, text="", bg=DARK_BG, fg="#00ff00", font=("Segoe UI", 10, "bold"))
status_label.pack(pady=2)

# ===== Autofill In-Game Name and Asset Fields =====
def autofill_fields(event=None):
    text = entry_item.get()
    entry_ingame.delete(0, tk.END)
    entry_ingame.insert(0, text)
    entry_asset.delete(0, tk.END)
    entry_asset.insert(0, text)
entry_item.bind("<KeyRelease>", autofill_fields)

# ===== Create Food Item Function =====
def create_food_item():
    module_name = entry_module.get().strip()
    item_name = entry_item.get().strip()
    ingame_name = entry_ingame.get().strip()
    asset_name = entry_asset.get().strip()
    display_category = entry_category.get().strip()
    itemtype = entry_itemtype.get().strip()
    weight = entry_weight.get().strip()

    hunger = entry_hunger.get().strip()
    thirst = entry_thirst.get().strip()
    unhappy = entry_unhappy.get().strip()
    stress = entry_stress.get().strip()
    boredom = entry_boredom.get().strip()
    fatigue = entry_fatigue.get().strip()
    endurance = entry_endurance.get().strip()

    flureduction = entry_flu.get().strip()
    painreduction = entry_pain.get().strip()
    reducefoodsickness = entry_food_sick.get().strip()
    reduceinfectionpower = entry_infection.get().strip()

    foodtype = entry_foodtype.get().strip()
    eattype = entry_eattype.get().strip()
    cookingsound = entry_cookingsound.get().strip()
    customsound = entry_eatingsound.get().strip()
    herbalisttype = entry_herbalisttype.get().strip()

    carbs = entry_carbs.get().strip()
    proteins = entry_proteins.get().strip()
    lipids = entry_lipids.get().strip()
    calories = entry_calories.get().strip()

    tags = entry_tags.get().strip() if tags_var.get() else ""
    tooltip = entry_tooltip.get().strip() if tooltip_var.get() else ""
    oneat = entry_oneat.get().strip() if oneat_var.get() else ""
    customcontextmenu = entry_customcontextmenu.get().strip() if customcontextmenu_var.get() else ""

    evolved = evolved_var.get()
    evolved_name = evolved_name_entry.get().strip() if evolved_var.get() else ""
    evolved_recipes = [btn.cget("text") for btn in evolved_cbs_buttons if btn.var.get()] if evolved_var.get() else []

    cantbefrozen = cantbefrozen_var.get()
    spice = spice_var.get()
    packaged = packaged_var.get()
    replaceonrotten = replacerotten_var.get()
    replace_text = entry_replace_rotten.get().strip()
    poisonpower = entry_poisonpower.get().strip() if poisonpower_active.get() else ""
    usedelta = entry_usedelta.get().strip() if usedelta_active.get() else ""
    iscookable = iscookable_var.get()
    
    cook_minutes = minutes_to_cook_entry.get().strip()
    burn_minutes = minutes_to_burn_entry.get().strip()

    fishing = fishing_var.get()
    dangerousraw = dangerous_raw_var.get()
    badcold = badcold_var.get()
    badmicrowave = badmicrowave_var.get()
    goodhot = goodhot_var.get()
    canteat = canteat_var.get()
    medical = medical_var.get()
    remove_unhappy_cooked = remove_unhappy_cooked_var.get()
    remove_negative_effects_cooked = remove_negative_effects_cooked_var.get()
    cannedfood = cannedfood_var.get()

# ===== Validate Required Fields =====
    required = [module_name, item_name, ingame_name, asset_name, weight, itemtype, display_category]
    if not all(required):
        status_label.config(text="Fill all required fields!", fg="red")
        return

# ===== Ensure Directories Exist =====
    scripts_dir = p("media/scripts/generated")
    items_dir = os.path.join(scripts_dir, "items")
    models_dir = p("media/models_X/WorldItems")
    textures_dir = p("media/textures/WorldItems")
    icon_dir = p("media/textures")
    for d in [scripts_dir, items_dir, models_dir, textures_dir, icon_dir]:
        ensure_dir(d)

# ===== Check for Existing Item =====
    display_category = entry_category.get().strip() 
    item_file = os.path.join(items_dir, f"{module_name}_{display_category}.txt")

    if os.path.exists(item_file):
        with open(item_file, "r", encoding="utf-8") as f:
            if f"item {item_name}" in f.read():
                status_label.config(text=f"Item '{item_name}' already exists!", fg="red")
                return

# ===== Create Translation File =====
    translation_dir = p("media/lua/shared/translate/EN")
    ensure_dir(translation_dir)
    translation_file = os.path.join(translation_dir, f"{module_name}_ItemName_EN.txt")

    existing_lines = []
    if os.path.exists(translation_file):
        with open(translation_file, "r", encoding="utf-8") as f:
            existing_lines = f.readlines()

    new_line = f'    ItemName_{module_name}.{item_name} = "{ingame_name}",\n'

    if new_line not in existing_lines:
        if not existing_lines:
            existing_lines.append("ItemName_EN = {\n")
            existing_lines.append(new_line)
            existing_lines.append("}\n")
        else:
            for i in range(len(existing_lines)-1, -1, -1):
                if existing_lines[i].strip() == "}":
                    existing_lines.insert(i, new_line)
                    break

    with open(translation_file, "w", encoding="utf-8") as f:
        f.writelines(existing_lines)

# ===== Create Model Definition =====
    model_script_file = os.path.join(scripts_dir, f"{module_name}_Models.txt")
    model_block = f"""model {asset_name}
{{
    mesh = WorldItems/{asset_name},
    texture = WorldItems/{asset_name},
    scale = 1.0,
}}"""
    insert_inside_last_brace(model_script_file, model_block, module_name=module_name)

# ===== Distribution File Generation =====
    if distribution_var.get():
        dist_file_dir = p("media/lua/server")
        ensure_dir(dist_file_dir)
        dist_file_path = os.path.join(dist_file_dir, f"{module_name}_Distributions.lua")
        
        try:
            spawning_chance = float(entry_spawning_chance.get())
        except ValueError:
            spawning_chance = 1 
        
        dist_lists = [x.strip() for x in entry_distribution_lists.get().split(",") if x.strip()]
        
        if os.path.exists(dist_file_path):
            with open(dist_file_path, "r", encoding="utf-8") as f:
                existing_lines = f.readlines()
        else:
            existing_lines = []

        requires = [
            "require 'Items/ProceduralDistributions'\n",
            "require 'Items/Distributions'\n\n"
        ]
        for req in requires:
            if req not in existing_lines:
                existing_lines.insert(0, req)

        new_lines = []
        for dist in dist_lists:
            item_var = f"{module_name}_{item_name}SpawningChance"
            line1 = f"local {item_var} = {spawning_chance}\n"
            line2 = f'table.insert(ProceduralDistributions["list"]["{dist}"].items, "{module_name}.{item_name}");\n'
            line3 = f"table.insert(ProceduralDistributions['list']['{dist}'].items, {item_var} * 0.1);\n\n"

            if line2 not in existing_lines:
                new_lines.extend([line1, line2, line3])
                existing_lines.extend([line1, line2, line3])  

        with open(dist_file_path, "w", encoding="utf-8") as f:
            f.writelines(existing_lines)

# ===== Foraging Definition File Generation =====
    if foraging_var.get():
        forage_dir = p("media/lua/shared/Foraging/Categories")
        ensure_dir(forage_dir)

        forage_file_path = os.path.join(
            forage_dir,
            f"{module_name}_ForageDefinitions.lua"
        )

        if os.path.exists(forage_file_path):
            with open(forage_file_path, "r", encoding="utf-8") as f:
                existing_lines = f.readlines()
        else:
            existing_lines = []

        requires = [
            'require "Foraging/forageDefinitions";\n',
            'require "Foraging/forageSystem";\n\n'
        ]

        for req in reversed(requires):
            if req not in existing_lines:
                existing_lines.insert(0, req)

        forage_category = entry_foraging_category.get().strip()

        try:
            min_count = int(entry_foraging_min.get())
        except ValueError:
            min_count = 1

        try:
            max_count = int(entry_foraging_max.get())
        except ValueError:
            max_count = min_count

        try:
            skill_req = int(entry_foraging_skill.get())
        except ValueError:
            skill_req = 0

        item_var = f"{module_name}_{item_name}_Forage"

        line_block = [
            f"local {item_var} = {{}}\n",
            f'{item_var}.type = "{module_name}.{item_name}"\n',
            f"{item_var}.minCount = {min_count}\n",
            f"{item_var}.maxCount = {max_count}\n",
            f"{item_var}.skill = {skill_req}\n",
            f'table.insert(scavenges.{forage_category}, {item_var})\n\n'
        ]

        type_line = f'{item_var}.type = "{module_name}.{item_name}"\n'

        if type_line not in existing_lines:
            existing_lines.extend(line_block)

        with open(forage_file_path, "w", encoding="utf-8") as f:
            f.writelines(existing_lines)

# ===== Create Item Definition =====
    def process_value(val, inc_var, dec_var):
        try:
            v = float(val)
        except:
            v = 0
        if inc_var.get(): v = -abs(v)
        if dec_var.get(): v = abs(v)
        return v

    item_block_lines = [
        f"item {item_name}",
        "{",
        f"    DisplayCategory = {display_category},",
        f"    Icon = Item_{asset_name},",
        f"    Weight = {weight},",
        f"    ItemType = base:{itemtype},",
            ]
    
    if hunger_choice.get() == "Increase":
        item_block_lines.append(f"    HungerChange = {hunger},")
    elif hunger_choice.get() == "Decrease":
        item_block_lines.append(f"    HungerChange = -{hunger},")
        
    if thirst_choice.get() == "Increase":
        item_block_lines.append(f"    ThirstChange = {thirst},")
    elif thirst_choice.get() == "Decrease":
        item_block_lines.append(f"    ThirstChange = -{thirst},")

    if unhappy_choice.get() == "Increase":
        item_block_lines.append(f"    UnhappyChange = {unhappy},")
    elif unhappy_choice.get() == "Decrease":
        item_block_lines.append(f"    UnhappyChange = -{unhappy},")

    if stress_choice.get() == "Increase":
        item_block_lines.append(f"    StressChange = {stress},")
    elif stress_choice.get() == "Decrease":
        item_block_lines.append(f"    StressChange = -{stress},")   

    if boredom_choice.get() == "Increase":
        item_block_lines.append(f"    BoredomChange = {boredom},")
    elif boredom_choice.get() == "Decrease":
        item_block_lines.append(f"    BoredomChange = -{boredom},")

    if fatigue_choice.get() == "Increase":
        item_block_lines.append(f"    FatigueChange = {fatigue},")
    elif fatigue_choice.get() == "Decrease":
        item_block_lines.append(f"    FatigueChange = -{fatigue},")

    if endurance_choice.get() == "Increase":
        item_block_lines.append(f"    EnduranceChange = {endurance},")
    elif endurance_choice.get() == "Decrease":
        item_block_lines.append(f"    EnduranceChange = -{endurance},")
        
    if nutrition_active.get():
        item_block_lines.append(f"    Carbohydrates = {carbs},")
        item_block_lines.append(f"    Proteins = {proteins},")
        item_block_lines.append(f"    Lipids = {lipids},")
        item_block_lines.append(f"    Calories = {calories},")

    if foodtype_active.get():
        item_block_lines.append(f"    FoodType = {foodtype},",)
    if eattype_active.get():
        item_block_lines.append(f"    EatType = {eattype},")
    if cookingsound_active.get():    
        item_block_lines.append(f"    CookingSound = {cookingsound},")
    if customsound:
        item_block_lines.append(f"    CustomEatSound = {customsound},")
    if herbalisttype:
        item_block_lines.append(f"    HerbalistType = {herbalisttype},")

    if flu_active.get():
        flureduction = float(entry_flu.get())
        item_block_lines.append(f"    FluReduction = {flureduction},")
    if pain_active.get():
        painreduction= float(entry_pain.get())
        item_block_lines.append(f"    PainReduction = {painreduction},")
    if food_sick_active.get():
        reducefoodsickness = float(entry_food_sick.get())
        item_block_lines.append(f"    ReduceFoodSickness = {reducefoodsickness},")
    if infection_active.get():
        reduceinfectionpower = float(entry_infection.get())
        item_block_lines.append(f"    ReduceInfectionPower = {reduceinfectionpower},")
    if poisonpower:
        item_block_lines.append(f"    PoisonPower = {poisonpower},")
    if usedelta:
        item_block_lines.append(f"    UseDelta = {usedelta},")
    if tags:
        item_block_lines.append(f"    Tags = {tags},")
    if tooltip:
        item_block_lines.append(f"    Tooltip = {entry_tooltip.get().strip()},")
    
    if oneat:
        item_block_lines.append(f"    OnEat = {oneat},")
    if customcontextmenu:
        item_block_lines.append(f"    CustomContextMenu = {customcontextmenu},")

    if perishable_var.get():
        days_fresh = entry_days_fresh.get().strip()
        days_rotten = entry_days_rotten.get().strip()
        item_block_lines.append(f"    DaysFresh = {days_fresh},")
        item_block_lines.append(f"    DaysTotallyRotten = {days_rotten},")
    if perishable_var.get() and replaceonrotten and replace_text:
        item_block_lines.append(f"    ReplaceOnRotten = {replace_text},")

    if iscookable:
        item_block_lines.append(f"    IsCookable = true,")
        item_block_lines.append(f"    MinutesToCook = {cook_minutes},")
        item_block_lines.append(f"    MinutesToBurn = {burn_minutes},")
        item_block_lines.append(f"    ReplaceOnCooked = {entry_replace_cooked.get().strip() if replace_cooked_var.get() else 'nil'},")

    if replace_use_var.get() and entry_replace_use.get().strip():
        item_block_lines.append(f"    ReplaceOnUse = {entry_replace_use.get().strip()},")

    if fishing: item_block_lines.append("    FishingLure = true,")
    if dangerousraw: item_block_lines.append("    DangerousUncooked = true,")
    if badcold: item_block_lines.append("    BadCold = true,")
    if badmicrowave: item_block_lines.append("    BadInMicrowave = true,")
    if goodhot: item_block_lines.append("    GoodHot = true,")
    if canteat: item_block_lines.append("    CantEat = true,")
    if medical: item_block_lines.append("    Medical = true,")
    if cannedfood: item_block_lines.append("    CannedFood = true,")
    if cantbefrozen: item_block_lines.append("    CantBeFrozen = true,")
    if spice: item_block_lines.append("    Spice = true,")
    if packaged: item_block_lines.append("    Packaged = true,")
    if remove_unhappy_cooked: item_block_lines.append("    RemoveUnhappinessWhenCooked = true,")
    if remove_negative_effects_cooked: item_block_lines.append("    RemoveNegativeEffectOnCooked = true,")  
    if evolved:
        item_block_lines.append(f"    EvolvedRecipeName = {evolved_name},")
        if evolved_recipes:
            evolved_items_str = ";".join([f"{r}:1" for r in evolved_recipes])
            item_block_lines.append(f"    EvolvedItems = {evolved_items_str},")


    item_block_lines.append(f"    WorldStaticModel = {asset_name},")
    item_block_lines.append(f"    StaticModel = {asset_name},")

    
    item_block_lines.append("}")
    insert_inside_last_brace(item_file, "\n".join(item_block_lines), module_name=module_name)

# ===== Create Placeholder Assets =====
    placeholders = {
        os.path.join(models_dir, f"{asset_name}.fbx"): f"Placeholder FBX for {asset_name}\n",
        os.path.join(textures_dir, f"{asset_name}.png"): f"Placeholder texture for {asset_name}\n",
        os.path.join(icon_dir, f"Item_{asset_name}.png"): f"Placeholder icon for {asset_name}\n"
    }
    for path, content in placeholders.items():
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

# ===== Update Status =====
    status_label.config(text=f"Item Created: {item_name}", fg="#00ff00")

# ===== Clear All Entries =====
def clear_all_entries():
    entries_to_clear = [
        entry_asset, entry_item, entry_ingame, entry_weight,
        entry_category, entry_itemtype, entry_foodtype, entry_eattype,
        entry_cookingsound, entry_eatingsound, entry_herbalisttype,
        entry_carbs, entry_proteins, entry_lipids, entry_calories,
        entry_days_fresh, entry_days_rotten,
        entry_poisonpower, entry_usedelta,
        entry_replace_cooked, entry_replace_rotten, entry_replace_use,
        entry_tags, entry_tooltip, entry_oneat, entry_customcontextmenu,
        evolved_name_entry, entry_flu, entry_pain, entry_food_sick, entry_infection,
        entry_hunger, entry_thirst, entry_unhappy, entry_stress, entry_boredom, entry_fatigue, entry_endurance,
        minutes_to_burn_entry, minutes_to_cook_entry, entry_asset, entry_spawning_chance, entry_distribution_lists
    ]
    for e in entries_to_clear:
        e.config(state="normal")
        e.delete(0, tk.END)
        if e in [entry_foodtype, entry_spawning_chance, entry_distribution_lists, entry_eattype, entry_cookingsound, entry_eatingsound,
                 entry_herbalisttype, entry_carbs, entry_proteins, entry_lipids,
                 entry_calories, entry_days_fresh, entry_days_rotten,
                 entry_poisonpower, entry_usedelta, entry_replace_cooked,
                 entry_replace_rotten, entry_replace_use, entry_tags, entry_tooltip,
                 entry_oneat, entry_customcontextmenu, evolved_name_entry, minutes_to_burn_entry,
                 minutes_to_cook_entry, entry_flu, entry_pain, entry_food_sick, entry_infection, entry_hunger, entry_thirst, entry_unhappy, entry_stress, entry_boredom, entry_fatigue, entry_endurance]:
            e.config(state="disabled")

    for var in [
        perishable_var, replace_cooked_var, replacerotten_var, replace_use_var, tags_var, tooltip_var, oneat_var,
        customcontextmenu_var, iscookable_var, sweet_var, salty_var,
        nutrition_active, foodtype_active, eattype_active,
        cookingsound_active, eatingsound_active, flu_active,
        pain_active, food_sick_active, infection_active,
        poisonpower_active, usedelta_active, replace_cooked_var,
        evolved_var, canteat_var, cantbefrozen_var, spice_var, packaged_var,
        cannedfood_var, badcold_var, badmicrowave_var, goodhot_var,
        dangerous_raw_var, fishing_var, medical_var,
        remove_unhappy_cooked_var, remove_negative_effects_cooked_var, replace_use_var, herbalisttype_active, distribution_var
    ]:
        var.set(False)

    for btn in toggle_buttons:
        btn.var.set(False)
        btn.config(bg=INACTIVE_BG, relief="raised")

    for btn in evolved_cbs_buttons:
        btn.var.set(False)
        btn.config(bg=INACTIVE_BG, relief="raised", state="disabled")

    for choice in [hunger_choice, thirst_choice, unhappy_choice, stress_choice,
                   boredom_choice, fatigue_choice, endurance_choice]:
        choice.set("Inactive")

    status_label.config(text="", fg="#00ff00")

# ===== Create Item Button =====
tk.Button(buttons_frame, text="Create Item", font=("Segoe UI", 12, "bold"),
          width=15, command=create_food_item).pack(pady=0)

tk.Button(buttons_frame, text="Clear All", font=("Segoe UI", 12, "bold"),
          width=15, command=clear_all_entries).pack(pady=0)

# ===== Start Main Loop =====
root.mainloop()