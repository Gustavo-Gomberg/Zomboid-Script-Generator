import os
import tkinter as tk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def p(path):
    return os.path.join(BASE_DIR, path)

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

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
root.geometry("820x820")
root.resizable(False, False)

# ===== Scrollable Frame Setup =====
canvas = tk.Canvas(root, bg=DARK_BG)
canvas.pack(side="left", fill="both", expand=True)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scrollbar.set)
main_frame = tk.Frame(canvas, bg=DARK_BG)
canvas.create_window((0,0), window=main_frame, anchor="nw")

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
main_frame.bind("<Configure>", on_frame_configure)

def _on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows / Mac

# ===== Title and Credits =====
tk.Label(main_frame, text="Project Zomboid - Consumables Creator",
         font=("Segoe UI", 12, "bold"), bg=DARK_BG, fg=DARK_FG).pack(pady=10)

tk.Label(main_frame, 
         text="Made with ChatGPT by TehaGP for Project Zomboid Build 42.13.2",
         font=("Segoe UI", 8), bg=DARK_BG, fg="#ff5555").pack(side="top", anchor="n", pady=5)

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




entry_module = add_row("Module Name:")
entry_item = add_row("Item Internal Name:")
entry_category = add_row("Display Category:")
entry_itemtype = add_row("Item Type:")
entry_weight = add_row("Weight:")
entry_ingame = add_row("Item In-Game Name:")
entry_asset = add_row("Model / Texture / Icon:")


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

entry_foodtype, foodtype_active = add_row_with_toggle("FoodType:", default="NoExplicit")
entry_eattype, eattype_active = add_row_with_toggle("EatType:", default="EatSmall")
entry_cookingsound, cookingsound_active = add_row_with_toggle("CookingSound:", default="FryingFood")
entry_eatingsound, eatingsound_active = add_row_with_toggle("CustomEatSound:", default="EatingCrispy")
entry_herbalisttype, herbalisttype_active = add_row_with_toggle("HerbalistType:", default="None")

# ===== Hunger/Thirst/Stats Fields =====
def add_inc_dec_row(parent_frame, label_text):
    frame = tk.Frame(parent_frame, bg=DARK_BG)
    frame.pack(pady=2, fill="x")
    tk.Label(frame, text=label_text, width=20, anchor="e", bg=DARK_BG, fg=DARK_FG).pack(side="left")
    entry = tk.Entry(frame, width=20, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG, state="disabled")
    entry.pack(side="left", padx=5)
    active_var = tk.BooleanVar(value=False)
    inc_var = tk.BooleanVar(value=False)
    dec_var = tk.BooleanVar(value=False)
    inc_cb = tk.Checkbutton(frame, text="Increase", variable=inc_var, takefocus=False,
                            bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG, state="disabled")
    dec_cb = tk.Checkbutton(frame, text="Decrease", variable=dec_var, takefocus=False,
                            bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG, state="disabled")
    inc_cb.pack(side="left", padx=2)
    dec_cb.pack(side="left", padx=2)

    def toggle_inc():
        if inc_var.get(): dec_var.set(False)
    def toggle_dec():
        if dec_var.get(): inc_var.set(False)

    inc_var.trace_add("write", lambda *args: toggle_inc())
    dec_var.trace_add("write", lambda *args: toggle_dec())

    def toggle_active():
        state = "normal" if active_var.get() else "disabled"
        entry.config(state=state)
        inc_cb.config(state=state)
        dec_cb.config(state=state)
        if state == "disabled":
            inc_var.set(False)
            dec_var.set(False)

    tk.Checkbutton(frame, text="Active", variable=active_var, command=toggle_active,
                   takefocus=False, bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG).pack(side="left", padx=2)
    return entry, active_var, inc_var, dec_var

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

# ===== Stat Change Fields =====
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
poisonpower_frame = tk.Frame(fields_frame, bg=DARK_BG); infection_frame.pack()

# ===== Create Stat Entry Rows =====
entry_hunger, hunger_active, hunger_inc, hunger_dec = add_inc_dec_row(hunger_frame, "HungerChange:")
entry_thirst, thirst_active, thirst_inc, thirst_dec = add_inc_dec_row(thirst_frame, "ThirstChange:")
entry_unhappy, unhappy_active, unhappy_inc, unhappy_dec = add_inc_dec_row(unhappy_frame, "UnhappyChange:")
entry_stress, stress_active, stress_inc, stress_dec = add_inc_dec_row(stress_frame, "StressChange:")
entry_boredom, boredom_active, boredom_inc, boredom_dec = add_inc_dec_row(boredom_frame, "BoredomChange:")
entry_fatigue, fatigue_active, fatigue_inc, fatigue_dec = add_inc_dec_row(fatigue_frame, "FatigueChange:")
entry_endurance, endurance_active, endurance_inc, endurance_dec = add_inc_dec_row(endurance_frame, "EnduranceChange:")
entry_flu, flu_active = add_decrease_only_row(flu_frame, "FluReduction:")
entry_pain, pain_active = add_decrease_only_row(pain_frame, "PainReduction:")
entry_food_sick, food_sick_active = add_decrease_only_row(sickness_frame, "ReduceFoodSickness:")
entry_infection, infection_active = add_decrease_only_row(infection_frame, "ReduceInfectionPower:")
entry_poisonpower, poisonpower_active = add_decrease_only_row(infection_frame, "PoisonPower:")
entry_usedelta, usedelta_active = add_decrease_only_row(infection_frame, "UseDelta:")

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
    ("Carbs:", 8),
    ("Proteins:", 8),
    ("Lipids:", 8),
    ("Calories:", 8),
])

cook_perishable_frame = tk.Frame(fields_frame, bg=DARK_BG)
cook_perishable_frame.pack(pady=2, anchor="center")

iscookable_var = tk.BooleanVar(value=False)

minutes_to_cook_entry = tk.Entry(
    cook_perishable_frame, width=6,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled"
)

minutes_to_burn_entry = tk.Entry(
    cook_perishable_frame, width=6,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled"
)

def toggle_cookable():
    state = "normal" if iscookable_var.get() else "disabled"
    minutes_to_cook_entry.config(state=state)
    minutes_to_burn_entry.config(state=state)
    if state == "disabled":
        minutes_to_cook_entry.delete(0, tk.END)
        minutes_to_burn_entry.delete(0, tk.END)

tk.Checkbutton(
    cook_perishable_frame,
    text="Is Cookable:",
    variable=iscookable_var,
    command=toggle_cookable,
    bg=DARK_BG, fg=DARK_FG,
    selectcolor=DARK_BG,
    activebackground=DARK_BG,
    takefocus=False
).pack(side="left", padx=(5, 2))

tk.Label(
    cook_perishable_frame,
    text="Minutes To Cook:",
    bg=DARK_BG, fg=DARK_FG
).pack(side="left", padx=(2, 2))

minutes_to_cook_entry.pack(side="left", padx=(0, 6))

tk.Label(
    cook_perishable_frame,
    text="Minutes To Burn:",
    bg=DARK_BG, fg=DARK_FG
).pack(side="left", padx=(2, 2))

minutes_to_burn_entry.pack(side="left", padx=(0, 15))


# ======================
# Is Perishable
# ======================
perishable_var = tk.BooleanVar(value=False)

def toggle_perishable():
    state = "normal" if perishable_var.get() else "disabled"
    entry_days_fresh.config(state=state)
    entry_days_rotten.config(state=state)
    if state == "disabled":
        entry_days_fresh.delete(0, tk.END)
        entry_days_rotten.delete(0, tk.END)

tk.Checkbutton(
    cook_perishable_frame,
    text="Is Perishable:",
    variable=perishable_var,
    command=toggle_perishable,
    bg=DARK_BG, fg=DARK_FG,
    selectcolor=DARK_BG,
    activebackground=DARK_BG,
    takefocus=False
).pack(side="left", padx=(5, 2))

tk.Label(
    cook_perishable_frame,
    text="Days Fresh:",
    bg=DARK_BG, fg=DARK_FG
).pack(side="left", padx=(2, 2))

entry_days_fresh = tk.Entry(
    cook_perishable_frame, width=6,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled"
)
entry_days_fresh.pack(side="left", padx=(0, 6))
entry_days_fresh.insert(0, "0")

tk.Label(
    cook_perishable_frame,
    text="Days Rotten:",
    bg=DARK_BG, fg=DARK_FG
).pack(side="left", padx=(2, 2))

entry_days_rotten = tk.Entry(
    cook_perishable_frame, width=6,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled"
)
entry_days_rotten.pack(side="left", padx=(0, 5))
entry_days_rotten.insert(0, "0")

replace_row = tk.Frame(fields_frame, bg=DARK_BG)
replace_row.pack(pady=2, anchor="center")

# ======================
# ReplaceOnCooked
# ======================
replace_cooked_var = tk.BooleanVar(value=False)

entry_replace_cooked = tk.Entry(
    replace_row, width=28,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled"
)

def toggle_replace_cooked():
    if replace_cooked_var.get():
        iscookable_var.set(True)
        toggle_cookable()

    state = "normal" if replace_cooked_var.get() else "disabled"
    entry_replace_cooked.config(state=state)

    if state == "disabled":
        entry_replace_cooked.delete(0, tk.END)

tk.Checkbutton(
    replace_row,
    text="ReplaceOnCooked:",
    variable=replace_cooked_var,
    command=toggle_replace_cooked,
    bg=DARK_BG, fg=DARK_FG,
    selectcolor=DARK_BG,
    activebackground=DARK_BG,
    takefocus=False
).pack(side="left", padx=(5, 2))

entry_replace_cooked.pack(side="left", padx=(0, 5))

# ======================
# ReplaceOnRotten
# ======================
replace_var = tk.BooleanVar(value=False)

entry_replace = tk.Entry(
    replace_row, width=28,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled"
)

def toggle_replace():
    if replace_var.get():
        perishable_var.set(True)
        toggle_perishable()

    state = "normal" if replace_var.get() and perishable_var.get() else "disabled"
    entry_replace.config(state=state)

    if state == "disabled":
        entry_replace.delete(0, tk.END)

tk.Checkbutton(
    replace_row,
    text="ReplaceOnRotten:",
    variable=replace_var,
    command=toggle_replace,
    bg=DARK_BG, fg=DARK_FG,
    selectcolor=DARK_BG,
    activebackground=DARK_BG,
    takefocus=False
).pack(side="left", padx=(5, 2))

entry_replace.pack(side="left", padx=(0, 20))

old_toggle_perishable = lambda: None
try: old_toggle_perishable = toggle_perishable
except: pass
def toggle_perishable():
    state = "normal" if perishable_var.get() else "disabled"
    entry_days_fresh.config(state=state)
    entry_days_rotten.config(state=state)
    if state == "disabled":
        entry_days_fresh.delete(0, tk.END)
        entry_days_rotten.delete(0, tk.END)

    if not perishable_var.get():
        replace_var.set(False)
        entry_replace.config(state="disabled")


use_sound_row = tk.Frame(fields_frame, bg=DARK_BG)
use_sound_row.pack(pady=2, anchor="center")

# ======================
# ReplaceOnUse
# ======================
replace_use_var = tk.BooleanVar(value=False)

entry_replace_use = tk.Entry(
    use_sound_row, width=26,
    bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled"
)

def toggle_replace_use():
    state = "normal" if replace_use_var.get() else "disabled"
    entry_replace_use.config(state=state)
    if state == "disabled":
        entry_replace_use.delete(0, tk.END)

tk.Checkbutton(
    use_sound_row,
    text="ReplaceOnUse:",
    variable=replace_use_var,
    command=toggle_replace_use,
    bg=DARK_BG, fg=DARK_FG,
    selectcolor=DARK_BG,
    activebackground=DARK_BG,
    takefocus=False
).pack(side="left", padx=(5, 2))

entry_replace_use.pack(side="left", padx=(0, 20))

# ===== Tags Field =====
tags_frame = tk.Frame(fields_frame, bg=DARK_BG)
tags_frame.pack(pady=4, fill="x")
tags_var = tk.BooleanVar(value=False)
def toggle_tags():
    if tags_var.get():
        entry_tags.config(state="normal")
    else:
        entry_tags.delete(0, tk.END)
        entry_tags.config(state="disabled")
tags_cb = tk.Checkbutton(tags_frame, text="Add Tags:", variable=tags_var, command=toggle_tags,
                         bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG)
tags_cb.pack(side="left", padx=5)
entry_tags = tk.Entry(tags_frame, width=40, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG, state="disabled")
entry_tags.pack(side="left", padx=5, fill="x", expand=True)


# ===== Tooltip Field =====
tooltip_frame = tk.Frame(fields_frame, bg=DARK_BG)
tooltip_frame.pack(pady=4, fill="x")
tooltip_var = tk.BooleanVar(value=False)
def toggle_tooltip():
    if tooltip_var.get():
        entry_tooltip.config(state="normal")
    else:
        entry_tooltip.delete(0, tk.END)
        entry_tooltip.config(state="disabled")
tooltip_cb = tk.Checkbutton(tooltip_frame, text="Add Tooltip:", variable=tooltip_var, command=toggle_tooltip,
                         bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG)
tooltip_cb.pack(side="left", padx=5)
entry_tooltip = tk.Entry(tooltip_frame, width=40, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG, state="disabled")
entry_tooltip.pack(side="left", padx=5, fill="x", expand=True)



# ===== OnEat Field =====
oneat_frame = tk.Frame(fields_frame, bg=DARK_BG)
oneat_frame.pack(pady=4, fill="x")
oneat_var = tk.BooleanVar(value=False)
def toggle_oneat():
    if oneat_var.get():
        entry_oneat.config(state="normal")
    else:
        entry_oneat.delete(0, tk.END)
        entry_oneat.config(state="disabled")
oneat_cb = tk.Checkbutton(oneat_frame, text="Add OnEat:", variable=oneat_var, command=toggle_oneat,
                         bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG)
oneat_cb.pack(side="left", padx=5)
entry_oneat = tk.Entry(oneat_frame, width=40, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG, state="disabled")
entry_oneat.pack(side="left", padx=5, fill="x", expand=True)

# ===== CustomContextMenu Field =====
customcontextmenu_frame = tk.Frame(fields_frame, bg=DARK_BG)
customcontextmenu_frame.pack(pady=4, fill="x")
customcontextmenu_var = tk.BooleanVar(value=False)
def toggle_customcontextmenu():
    if customcontextmenu_var.get():
        entry_customcontextmenu.config(state="normal")
    else:
        entry_customcontextmenu.delete(0, tk.END)
        entry_customcontextmenu.config(state="disabled")
customcontextmenu_cb = tk.Checkbutton(customcontextmenu_frame, text="Add CustomContextMenu:", variable=customcontextmenu_var, command=toggle_customcontextmenu,
                         bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG)
customcontextmenu_cb.pack(side="left", padx=5)
entry_customcontextmenu = tk.Entry(customcontextmenu_frame, width=40, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG, state="disabled")
entry_customcontextmenu.pack(side="left", padx=5, fill="x", expand=True)

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
alcoholic_var = tk.BooleanVar(value=False)
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

# ===== Evolved Recipes =====
evolved_frame = tk.Frame(fields_frame, bg=DARK_BG)
evolved_frame.pack(pady=4, fill="x")

evolved_var = tk.BooleanVar(value=False)

def toggle_evolved():
    evolved_name_entry.config(state="normal" if evolved_var.get() else "disabled")
    for btn in evolved_cbs_buttons:
        btn.config(state="normal" if evolved_var.get() else "disabled")
    sweet_toggle_cb.config(state="normal" if evolved_var.get() else "disabled")
    salty_toggle_cb.config(state="normal" if evolved_var.get() else "disabled")

evolved_cb = tk.Checkbutton(
    evolved_frame,
    text="EvolvedRecipe:",
    variable=evolved_var,
    command=toggle_evolved,
    bg=DARK_BG,
    fg=DARK_FG,
    selectcolor=DARK_BG,
    activebackground=DARK_BG
)
evolved_cb.pack(side="left", padx=5)

# Evolved Recipe Name Entry
tk.Label(evolved_frame, text="Evolved Recipe Name:", bg=DARK_BG, fg=DARK_FG).pack(side="left", padx=2)
evolved_name_entry = tk.Entry(
    evolved_frame, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG,
    state="disabled", width=25
)
evolved_name_entry.pack(side="left", padx=0, fill="x", expand=True)

# Sweet and Salty Recipes
sweet_list = ["Pancakes","Muffin","ConeIcecream","Cake","PieSweet","Oatmeal","Toast"]
salty_list = ["Sandwich","Stir fry","Pasta","Taco","Burrito","Salad","Soup","Stew","Bread"]

sweet_frame = tk.Frame(fields_frame, bg=DARK_BG)
sweet_frame.pack(pady=3, fill="x")
salty_frame = tk.Frame(fields_frame, bg=DARK_BG)
salty_frame.pack(pady=3, fill="x")

sweet_var = tk.BooleanVar(value=False)
salty_var = tk.BooleanVar(value=False)

# "Mark All" Checkboxes
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
    bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG, state="disabled"
)
sweet_toggle_cb.pack(side="left", padx=5)

salty_toggle_cb = tk.Checkbutton(
    salty_frame, text="Mark All Salty", variable=salty_var, command=toggle_all_salty,
    bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG, state="disabled"
)
salty_toggle_cb.pack(side="left", padx=5)

# ===== Individual Evolved Recipe Toggle Buttons =====
evolved_cbs_buttons = []

for lst, frame in [(sweet_list, sweet_frame), (salty_list, salty_frame)]:
    for item_name in lst:
        var = tk.BooleanVar(value=False)
        btn = toggle_button(frame, item_name, var, width=max(len(item_name)//1 + 2, 8))
        btn.var = var
        btn.config(state="disabled")  # disabled until EvolvedRecipe is checked
        evolved_cbs_buttons.append(btn)

flags_row = tk.Frame(fields_frame, bg=DARK_BG)
flags_row.pack(pady=2, anchor="center")

toggle_button(flags_row, "Can't be Eaten", canteat_var, 12)
toggle_button(flags_row, "Can't be Frozen", cantbefrozen_var, 13)
toggle_button(flags_row, "It's a Spice", spice_var, 8)
toggle_button(flags_row, "It's Packaged", packaged_var, 11)
toggle_button(flags_row, "It's Canned Food", cannedfood_var, 14)
toggle_button(flags_row, "It's Bad Cold", badcold_var, 12)
toggle_button(flags_row, "It's Good Hot", goodhot_var, 12)

flags_row2 = tk.Frame(fields_frame, bg=DARK_BG)
flags_row2.pack(pady=2, anchor="center")

toggle_button(flags_row2, "It's Dangerous Raw", dangerous_raw_var, 16)
toggle_button(flags_row2, "It's Bad Microwaved", badmicrowave_var, 18)
toggle_button(flags_row2, "Removes Unhappiness when Cooked", remove_unhappy_cooked_var, 33)
toggle_button(flags_row2, "Remove Negative Effects when Cooked", remove_negative_effects_cooked_var, 35)
    
flags_row3 = tk.Frame(fields_frame, bg=DARK_BG)
flags_row3.pack(pady=2, anchor="center")
toggle_button(flags_row3, "It's a Medical Item", medical_var, 20)
toggle_button(flags_row3, "It's Alcoholic", alcoholic_var, 14)
toggle_button(flags_row3, "Can be used as Fishing Lure", fishing_var, 24)

# ===== Template Dropdown at Top Right =====
def template_dropdown_topright():
    top_frame = tk.Frame(root, bg=DARK_BG, width=820, height=50)
    top_frame.place(x=10, y=10)


    tk.Label(top_frame, text="SELECT TEMPLATE:", bg=DARK_BG, fg=DARK_FG).pack(side="top", padx=5)

    template_var = tk.StringVar(value="None")
    options = ["None", "Food", "Medical"]
    dropdown = tk.OptionMenu(top_frame, template_var, *options)
    dropdown.config(bg=DARK_BG, fg=DARK_FG, highlightthickness=0)
    dropdown.pack(side="top", padx=5)

    def apply_template(*args):
        tmpl = template_var.get()
        if tmpl == "Food":
            entry_tags.delete(0, tk.END)
            entry_category.delete(0, tk.END)
            entry_itemtype.delete(0, tk.END)
            entry_category.insert(0, "Food")
            entry_foodtype.insert(0, "NoExplicit")
            entry_itemtype.insert(0, "Food")
            entry_eattype.insert(0, "EatSmall")
            entry_cookingsound.insert(0, "FryingFood")
            entry_eatingsound.insert(0, "EatingCrispy")
            foodtype_active.set(True)
            eattype_active.set(True)
            cookingsound_active.set(True)
            eatingsound_active.set(True)
            medical_var.set(False)
            entry_category.config(state="normal")
            entry_foodtype.config(state="normal")
            entry_itemtype.config(state="normal")
            entry_eattype.config(state="normal")
            entry_cookingsound.config(state="normal")
            entry_eatingsound.config(state="normal")

        elif tmpl == "Medical":            
            for entry in [entry_foodtype, entry_eattype, entry_cookingsound, entry_eatingsound]: 
                entry.delete(0, tk.END)     
                entry.config(state="disabled") 
            foodtype_active.set(False) 
            eattype_active.set(False) 
            cookingsound_active.set(False)
            eatingsound_active.set(False)
            entry_tags.delete(0, tk.END)
            entry_category.delete(0, tk.END)
            entry_itemtype.delete(0, tk.END)
            entry_tags.config(state="normal")
            entry_category.config(state="normal")
            entry_itemtype.config(state="normal")
            entry_category.insert(0, "FirstAid")
            entry_itemtype.insert(0, "drainable")
            entry_tags.insert(0, "base:consumable")
            medical_var.set(True)


            
        elif tmpl == "None":

            for entry in [entry_foodtype,
                          entry_eattype, entry_cookingsound, entry_eatingsound]:
                entry.config(state="disabled")
                entry.delete(0, tk.END)
            entry_category.delete(0, tk.END)
            entry_itemtype.delete(0, tk.END)
            foodtype_active.set(False)
            eattype_active.set(False)
            cookingsound_active.set(False)
            eatingsound_active.set(False)
            medical_var.set(False)
            entry_tags.delete(0, tk.END)
            entry_tags.config(state="disabled")

    template_var.trace_add("write", apply_template)
    return template_var


template_var = template_dropdown_topright()

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
    replaceonrotten = replace_var.get()
    replace_text = entry_replace.get().strip()
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
    alcoholic = alcoholic_var.get()
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
    item_file = os.path.join(items_dir, f"{module_name}_Food.txt")
    if os.path.exists(item_file):
        with open(item_file, "r", encoding="utf-8") as f:
            if f"item {item_name}" in f.read():
                status_label.config(text=f"Item '{item_name}' already exists!", fg="red")
                return

# ===== Create Translation File =====
    translation_dir = p("media/lua/shared/translate/EN")
    ensure_dir(translation_dir)
    translation_file = os.path.join(translation_dir, f"{module_name}_ItemName_EN.txt")
    with open(translation_file, "w", encoding="utf-8") as f:
        f.write(f"ItemName_EN = {{\n    ItemName_{module_name}.{item_name} = \"{ingame_name}\",\n}}\n")


    model_script_file = os.path.join(scripts_dir, f"{module_name}_Models.txt")
    model_block = f"""model {asset_name}
{{
    mesh = WorldItems/{asset_name},
    texture = WorldItems/{asset_name},
    scale = 1.0,
}}"""
    insert_inside_last_brace(model_script_file, model_block, module_name=module_name)

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
    
    if hunger_active.get():
        item_block_lines.append(f"    HungerChange = {process_value(hunger, hunger_inc, hunger_dec)},")
    if thirst_active.get():
        item_block_lines.append(f"    ThirstChange = {process_value(thirst, thirst_inc, thirst_dec)},")
    if unhappy_active.get():
        item_block_lines.append(f"    UnhappyChange = {process_value(unhappy, unhappy_inc, unhappy_dec)},")
    if stress_active.get():
        item_block_lines.append(f"    StressChange = {process_value(stress, stress_inc, stress_dec)},")
    if boredom_active.get():
        item_block_lines.append(f"    BoredomChange = {process_value(boredom, boredom_inc, boredom_dec)},")  
    if fatigue_active.get():
        item_block_lines.append(f"    FatigueChange = {process_value(fatigue, fatigue_inc, fatigue_dec)},",)
    if endurance_active.get():
        item_block_lines.append(f"    EnduranceChange = {process_value(endurance, endurance_inc, endurance_dec)},")
    if nutrition_active.get():
        item_block_lines.append(f"    Carbs = {carbs},")
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
    else:
        item_block_lines.append(f"    IsCookable = false,")

    if replace_use_var.get() and entry_replace_use.get().strip():
        item_block_lines.append(f"    ReplaceOnUse = {entry_replace_use.get().strip()},")

    if fishing: item_block_lines.append("    FishingLure = true,")
    if dangerousraw: item_block_lines.append("    DangerousUncooked = true,")
    if badcold: item_block_lines.append("    BadCold = true,")
    if badmicrowave: item_block_lines.append("    BadInMicrowave = true,")
    if goodhot: item_block_lines.append("    GoodHot = true,")
    if canteat: item_block_lines.append("    CantEat = true,")
    if alcoholic: item_block_lines.append("    Alcoholic = true,")
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


    entries_to_clear = [entry_item, entry_ingame, entry_asset, entry_weight,
                        entry_hunger, entry_thirst, entry_unhappy, entry_herbalisttype, 
                        entry_carbs, entry_proteins, entry_lipids, entry_calories, entry_tags, entry_tooltip, entry_usedelta, entry_oneat, entry_customcontextmenu,
                        entry_stress, entry_boredom, entry_fatigue, entry_endurance,
                        entry_foodtype, entry_eattype, entry_cookingsound, entry_eatingsound,
                        entry_flu, entry_pain, entry_food_sick, entry_infection,
                        entry_days_fresh, entry_days_rotten, entry_eatingsound, evolved_name_entry,
                        entry_replace, entry_poisonpower, minutes_to_cook_entry, minutes_to_burn_entry, entry_flu, entry_pain, entry_stress, entry_boredom, entry_fatigue, entry_endurance,
                        entry_food_sick, entry_infection]
    for e in entries_to_clear: 
        e.delete(0, tk.END)

# Reset all checkboxes and variables
    hunger_inc.set(True); hunger_dec.set(False)
    thirst_inc.set(True); thirst_dec.set(False)
    unhappy_inc.set(True); unhappy_dec.set(False)
    stress_inc.set(True); stress_dec.set(False)
    boredom_inc.set(True); boredom_dec.set(False)
    fatigue_inc.set(True); fatigue_dec.set(False)
    eatingsound_active.set(False)
    perishable_var.set(False)
    replace_var.set(False)
    tags_var.set(False)
    tooltip_var.set(False)
    evolved_var.set(False)
    herbalisttype_active.set(False)
    oneat_var.set(False)
    customcontextmenu_var.set(False)
    usedelta_active.set(False)
    sweet_var.set(False)
    salty_var.set(False)
    cantbefrozen_var.set(False)
    spice_var.set(False)
    packaged_var.set(False)
    poisonpower_active.set(False)
    iscookable_var.set(False)
    fishing_var.set(False)
    dangerous_raw_var.set(False)
    badcold_var.set(False)
    badmicrowave_var.set(False)
    goodhot_var.set(False)
    canteat_var.set(False)
    alcoholic_var.set(False)
    medical_var.set(False)
    remove_unhappy_cooked_var.set(False)
    remove_negative_effects_cooked_var.set(False)
    cannedfood_var.set(False)
    flu_active.set(False)
    pain_active.set(False)
    food_sick_active.set(False)
    infection_active.set(False)
    foodtype_active.set(False)
    eattype_active.set(False)
    cookingsound_active.set(False)
    hunger_active.set(False)
    thirst_active.set(False)  
    unhappy_active.set(False)
    stress_active.set(False)
    boredom_active.set(False)
    fatigue_active.set(False)
    endurance_active.set(False)
    nutrition_active.set(False)


    for cb in evolved_cbs_buttons:
        cb.var.set(False)
        cb.config(bg=INACTIVE_BG, relief="raised")


# ==== Update Status =====
    status_label.config(text=f"Food Item Created: {item_name}", fg="#00ff00")

# ===== Create Item Button =====
tk.Button(buttons_frame, text="Create Item", font=("Segoe UI", 12, "bold"),
          width=15, command=create_food_item).pack(pady=0)

# ===== Start Main Loop =====
root.mainloop()