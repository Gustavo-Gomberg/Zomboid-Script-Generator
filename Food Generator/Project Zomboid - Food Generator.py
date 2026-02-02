import os
import tkinter as tk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def p(path):
    return os.path.join(BASE_DIR, path)

def ensure_dir(path):
    """Ensure a directory exists, create if it doesn't."""
    os.makedirs(path, exist_ok=True)

def insert_inside_last_brace(filepath, block, module_name=None):
    """
    Insert a block of text inside the last closing brace of a file.
    If the file doesn't exist, create it with an optional module header.
    """
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

# ===== Dark Theme Colors =====
DARK_BG = "#2b2b2b"
DARK_FG = "#f0f0f0"

# ===== Main Window =====
root = tk.Tk()
root.title("Project Zomboid - Food Generator")
root.geometry("720x920")
root.resizable(False, False)

main_frame = tk.Frame(root, bg=DARK_BG)
main_frame.pack(fill="both", expand=True)

tk.Label(main_frame, text="Project Zomboid - Food Generator",
         font=("Segoe UI", 15, "bold"), bg=DARK_BG, fg=DARK_FG).pack(pady=10)

# ===== Input Fields Wrapper =====
fields_wrapper = tk.Frame(main_frame, bg=DARK_BG)
fields_wrapper.pack(pady=5, fill="x")
fields_frame = tk.Frame(fields_wrapper, bg=DARK_BG)
fields_frame.pack(anchor="center")

def add_row(label_text, default=""):
    """Add a labeled text entry row."""
    row = tk.Frame(fields_frame, bg=DARK_BG)
    row.pack(pady=4, fill="x")
    tk.Label(row, text=label_text, width=20, anchor="e", bg=DARK_BG, fg=DARK_FG).pack(side="left")
    entry = tk.Entry(row, width=40, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG)
    entry.insert(0, default)
    entry.pack(side="left", fill="x", expand=True, padx=(5,5))
    entry.xview_moveto(0)
    return entry

# ===== Basic Fields =====
entry_module = add_row("Module Name")
entry_item = add_row("Item Internal Name")
entry_category = add_row("DisplayCategory", default="Food")
entry_weight = add_row("Weight")
entry_ingame = add_row("Item In-Game Name")
entry_asset = add_row("Model / Texture / Icon")

# ===== Increase/Decrease Numeric Fields =====
def add_inc_dec_row(parent_frame, label_text):
    """Add a numeric field with Increase/Decrease checkboxes."""
    frame = tk.Frame(parent_frame, bg=DARK_BG)
    frame.pack(pady=2, fill="x")
    tk.Label(frame, text=label_text, width=20, anchor="e", bg=DARK_BG, fg=DARK_FG).pack(side="left")
    entry = tk.Entry(frame, width=20, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG)
    entry.pack(side="left", padx=5)
    inc_var = tk.BooleanVar(value=True)
    dec_var = tk.BooleanVar(value=False)
    def toggle_inc(): 
        if inc_var.get(): dec_var.set(False)
    def toggle_dec(): 
        if dec_var.get(): inc_var.set(False)
    tk.Checkbutton(frame, text="Increase", variable=inc_var, command=toggle_inc,
                   bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG).pack(side="left", padx=2)
    tk.Checkbutton(frame, text="Decrease", variable=dec_var, command=toggle_dec,
                   bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG).pack(side="left", padx=2)
    return entry, inc_var, dec_var

hunger_frame = tk.Frame(fields_frame, bg=DARK_BG); hunger_frame.pack()
thirst_frame = tk.Frame(fields_frame, bg=DARK_BG); thirst_frame.pack()
unhappy_frame = tk.Frame(fields_frame, bg=DARK_BG); unhappy_frame.pack()

entry_hunger, hunger_inc, hunger_dec = add_inc_dec_row(hunger_frame, "HungerChange")
entry_thirst, thirst_inc, thirst_dec = add_inc_dec_row(thirst_frame, "ThirstChange")
entry_unhappy, unhappy_inc, unhappy_dec = add_inc_dec_row(unhappy_frame, "UnhappyChange")

# ===== Food-specific Fields =====
entry_foodtype = add_row("FoodType", default="NoExplicit")
entry_eattype = add_row("EatType", default="EatSmall")
entry_carbs = add_row("Carbohydrates")
entry_proteins = add_row("Proteins")
entry_lipids = add_row("Lipids")
entry_calories = add_row("Calories")

# ===== Cookable =====
cook_frame = tk.Frame(fields_frame, bg=DARK_BG)
cook_frame.pack(pady=2, fill="x")
iscookable_var = tk.BooleanVar(value=False)
minutes_to_cook_entry = tk.Entry(cook_frame, width=6, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG, state="disabled")
minutes_to_burn_entry = tk.Entry(cook_frame, width=6, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG, state="disabled")

def toggle_cookable():
    state = "normal" if iscookable_var.get() else "disabled"
    minutes_to_cook_entry.config(state=state)
    minutes_to_burn_entry.config(state=state)
    if state == "disabled":
        minutes_to_cook_entry.delete(0, tk.END)
        minutes_to_burn_entry.delete(0, tk.END)

tk.Checkbutton(cook_frame, text="Is Cookable", variable=iscookable_var, command=toggle_cookable,
               bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG).pack(side="left", padx=5)
tk.Label(cook_frame, text="Minutes To Cook:", bg=DARK_BG, fg=DARK_FG).pack(side="left", padx=2)
minutes_to_cook_entry.pack(side="left", padx=2)
tk.Label(cook_frame, text="Minutes To Burn:", bg=DARK_BG, fg=DARK_FG).pack(side="left", padx=2)
minutes_to_burn_entry.pack(side="left", padx=2)

# ===== Perishable Options =====
perishable_frame = tk.Frame(fields_frame, bg=DARK_BG)
perishable_frame.pack(pady=2, fill="x")
perishable_var = tk.BooleanVar(value=False)

tk.Checkbutton(perishable_frame, text="Is Perishable", variable=perishable_var,
               command=lambda: toggle_perishable(),
               bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG).pack(side="left", padx=5)

tk.Label(perishable_frame, text="Days Fresh:", bg=DARK_BG, fg=DARK_FG).pack(side="left", padx=2)
entry_days_fresh = tk.Entry(perishable_frame, width=8, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG, state="disabled")
entry_days_fresh.pack(side="left", padx=2)
entry_days_fresh.insert(0, "0")

tk.Label(perishable_frame, text="Days Until Rotten:", bg=DARK_BG, fg=DARK_FG).pack(side="left", padx=2)
entry_days_rotten = tk.Entry(perishable_frame, width=8, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG, state="disabled")
entry_days_rotten.pack(side="left", padx=2)
entry_days_rotten.insert(0, "0")

# ===== ReplaceOnRotten (depends on perishable) =====
replace_frame = tk.Frame(fields_frame, bg=DARK_BG)
replace_frame.pack(pady=2, fill="x")
replace_var = tk.BooleanVar(value=False)
entry_replace = tk.Entry(replace_frame, width=30, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG, state="disabled")

def toggle_replace():
    state = "normal" if replace_var.get() and perishable_var.get() else "disabled"
    entry_replace.config(state=state)
    if state == "disabled":
        entry_replace.delete(0, tk.END)

tk.Checkbutton(replace_frame, text="ReplaceOnRotten", variable=replace_var, command=toggle_replace,
               bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG).pack(side="left", padx=5)
entry_replace.pack(side="left", padx=5, fill="x", expand=True)

# Save old toggle_perishable
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
    # Disable ReplaceOnRotten if not perishable
    if not perishable_var.get():
        replace_var.set(False)
        entry_replace.config(state="disabled")

# ===== Custom Eat Sound =====
customsound_frame = tk.Frame(fields_frame, bg=DARK_BG)
customsound_frame.pack(pady=2, fill="x")
customsound_var = tk.BooleanVar(value=False)
def toggle_customsound():
    state = "normal" if customsound_var.get() else "disabled"
    customsound_entry.config(state=state)
    if state == "disabled": customsound_entry.delete(0, tk.END)
tk.Checkbutton(customsound_frame, text="CustomEatSound", variable=customsound_var, command=toggle_customsound,
               bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG).pack(side="left", padx=5)
customsound_entry = tk.Entry(customsound_frame, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG, state="disabled", width=30)
customsound_entry.pack(side="left", padx=5, fill="x", expand=True)

# ===== Tags =====
tags_frame = tk.Frame(fields_frame, bg=DARK_BG)
tags_frame.pack(pady=4, fill="x")
tags_var = tk.BooleanVar(value=False)
def toggle_tags():
    if tags_var.get():
        entry_tags.config(state="normal")
    else:
        entry_tags.delete(0, tk.END)
        entry_tags.config(state="disabled")
tags_cb = tk.Checkbutton(tags_frame, text="Add Tags", variable=tags_var, command=toggle_tags,
                         bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG)
tags_cb.pack(side="left", padx=5)
entry_tags = tk.Entry(tags_frame, width=40, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG, state="disabled")
entry_tags.pack(side="left", padx=5, fill="x", expand=True)

# ===== PoisonPower =====
poison_frame = tk.Frame(fields_frame, bg=DARK_BG)
poison_frame.pack(pady=2, fill="x")
poison_var = tk.BooleanVar(value=False)
entry_poison = tk.Entry(poison_frame, width=10, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG, state="disabled")
def toggle_poison():
    state = "normal" if poison_var.get() else "disabled"
    entry_poison.config(state=state)
    if state == "disabled":
        entry_poison.delete(0, tk.END)
tk.Checkbutton(poison_frame, text="Poison Power", variable=poison_var, command=toggle_poison,
               bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG).pack(side="left", padx=5)
entry_poison.pack(side="left", padx=5, fill="x", expand=True)

# ===== Evolved Recipes =====
evolved_frame = tk.Frame(fields_frame, bg=DARK_BG)
evolved_frame.pack(pady=4, fill="x")
evolved_var = tk.BooleanVar(value=False)
def toggle_evolved():
    evolved_name_entry.config(state="normal" if evolved_var.get() else "disabled")
    for cb in evolved_cbs:
        cb.config(state="normal" if evolved_var.get() else "disabled")
    sweet_toggle_cb.config(state="normal" if evolved_var.get() else "disabled")
    salty_toggle_cb.config(state="normal" if evolved_var.get() else "disabled")
evolved_cb = tk.Checkbutton(evolved_frame, text="EvolvedRecipe", variable=evolved_var, command=toggle_evolved,
                            bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG)
evolved_cb.pack(side="left", padx=5)

tk.Label(evolved_frame, text="Evolved Recipe Name:", bg=DARK_BG, fg=DARK_FG).pack(side="left", padx=2)
evolved_name_entry = tk.Entry(evolved_frame, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG, state="disabled", width=20)
evolved_name_entry.pack(side="left", padx=0, fill="x", expand=True)

# Sweet and Salty recipes
sweet_list = ["Pancakes","Muffin","ConeIcecream","Cake","PieSweet","Oatmeal","Toast"]
salty_list = ["Sandwich","Stir fry","Pasta","Taco","Burrito","Salad","Soup","Stew","Bread"]

sweet_frame = tk.Frame(fields_frame, bg=DARK_BG)
sweet_frame.pack(pady=3, fill="x")
salty_frame = tk.Frame(fields_frame, bg=DARK_BG)
salty_frame.pack(pady=3, fill="x")

sweet_var = tk.BooleanVar(value=False)
salty_var = tk.BooleanVar(value=False)

def toggle_all_sweet():
    if evolved_var.get():
        for cb in evolved_cbs:
            if cb.cget("text") in sweet_list:
                cb.var.set(sweet_var.get())

def toggle_all_salty():
    if evolved_var.get():
        for cb in evolved_cbs:
            if cb.cget("text") in salty_list:
                cb.var.set(salty_var.get())

sweet_toggle_cb = tk.Checkbutton(sweet_frame, text="Mark All Sweet", variable=sweet_var, command=toggle_all_sweet,
                                 bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG, state="disabled")
sweet_toggle_cb.pack(side="left", padx=5)
salty_toggle_cb = tk.Checkbutton(salty_frame, text="Mark All Salty", variable=salty_var, command=toggle_all_salty,
                                 bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_BG, activebackground=DARK_BG, state="disabled")
salty_toggle_cb.pack(side="left", padx=5)

# Individual recipe checkboxes
evolved_cbs = []
for lst, frame in [(sweet_list, sweet_frame), (salty_list, salty_frame)]:
    for r in lst:
        var = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(frame, text=r, variable=var, bg=DARK_BG, fg=DARK_FG,
                            selectcolor=DARK_BG, activebackground=DARK_BG, state="disabled")
        cb.var = var
        cb.pack(side="left", padx=2)
        evolved_cbs.append(cb)

# ===== CantBeFrozen, Spice, Packaged =====
# ===== New Boolean Fields =====
flags_frame = tk.Frame(fields_frame, bg=DARK_BG)
flags_frame.pack(pady=2, fill="x")
fishing_var = tk.BooleanVar(value=False)
dangerous_var = tk.BooleanVar(value=False)
badcold_var = tk.BooleanVar(value=False)
badmicrowave_var = tk.BooleanVar(value=False)
goodhot_var = tk.BooleanVar(value=False)
cantbe_frame = tk.Frame(fields_frame, bg=DARK_BG)
cantbe_frame.pack(pady=4, fill="x")
cantbe_var = tk.BooleanVar(value=False)
spice_var = tk.BooleanVar(value=False)
packaged_var = tk.BooleanVar(value=False)
tk.Checkbutton(cantbe_frame, text="Cant Be Frozen", variable=cantbe_var, bg=DARK_BG, fg=DARK_FG, 
               selectcolor=DARK_BG, activebackground=DARK_BG).pack(side="left", padx=5)
tk.Checkbutton(cantbe_frame, text="Spice", variable=spice_var, bg=DARK_BG, fg=DARK_FG, 
               selectcolor=DARK_BG, activebackground=DARK_BG).pack(side="left", padx=5)
tk.Checkbutton(cantbe_frame, text="Packaged", variable=packaged_var, bg=DARK_BG, fg=DARK_FG, 
               selectcolor=DARK_BG, activebackground=DARK_BG).pack(side="left", padx=5)
tk.Checkbutton(cantbe_frame, text="Fishing Lure", variable=fishing_var, bg=DARK_BG, fg=DARK_FG,
               selectcolor=DARK_BG, activebackground=DARK_BG).pack(side="left", padx=5)
tk.Checkbutton(flags_frame, text="Dangerous Uncooked", variable=dangerous_var, bg=DARK_BG, fg=DARK_FG,
               selectcolor=DARK_BG, activebackground=DARK_BG).pack(side="left", padx=5)
tk.Checkbutton(flags_frame, text="Bad Cold", variable=badcold_var, bg=DARK_BG, fg=DARK_FG,
               selectcolor=DARK_BG, activebackground=DARK_BG).pack(side="left", padx=5)
tk.Checkbutton(flags_frame, text="Good Hot", variable=goodhot_var, bg=DARK_BG, fg=DARK_FG,
               selectcolor=DARK_BG, activebackground=DARK_BG).pack(side="left", padx=5)
tk.Checkbutton(flags_frame, text="Bad In Microwave", variable=badmicrowave_var, bg=DARK_BG, fg=DARK_FG,
               selectcolor=DARK_BG, activebackground=DARK_BG).pack(side="left", padx=5)





# ===== Buttons & Status =====
buttons_frame = tk.Frame(main_frame, bg=DARK_BG)
buttons_frame.pack(pady=10)
status_label = tk.Label(main_frame, text="", bg=DARK_BG, fg="#00ff00", font=("Segoe UI", 10, "bold"))
status_label.pack(pady=2)

# ===== Auto-fill In-Game Name and Asset =====
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
    weight = entry_weight.get().strip()
    hunger = entry_hunger.get().strip()
    thirst = entry_thirst.get().strip()
    unhappy = entry_unhappy.get().strip()
    foodtype = entry_foodtype.get().strip()
    eattype = entry_eattype.get().strip()
    carbs = entry_carbs.get().strip()
    proteins = entry_proteins.get().strip()
    lipids = entry_lipids.get().strip()
    calories = entry_calories.get().strip()
    tags = entry_tags.get().strip() if tags_var.get() else ""
    customsound = customsound_entry.get().strip() if customsound_var.get() else ""
    evolved = evolved_var.get()
    evolved_name = evolved_name_entry.get().strip() if evolved_var.get() else ""
    evolved_recipes = [cb.cget("text") for cb in evolved_cbs if cb.var.get()] if evolved else []
    cantbe = cantbe_var.get()
    spice = spice_var.get()
    packaged = packaged_var.get()
    # New fields
    replaceonrotten = replace_var.get()
    replace_text = entry_replace.get().strip()
    poisonpower = poison_var.get()
    poison_value = entry_poison.get().strip()
    iscookable = iscookable_var.get()
    cook_minutes = minutes_to_cook_entry.get().strip()
    burn_minutes = minutes_to_burn_entry.get().strip()
    fishing = fishing_var.get()
    dangerous = dangerous_var.get()
    badcold = badcold_var.get()
    badmicrowave = badmicrowave_var.get()
    goodhot = goodhot_var.get()

    # ===== Validate required fields =====
    required = [module_name, item_name, ingame_name, asset_name, weight, hunger, thirst, unhappy,
                foodtype, eattype, carbs, proteins, lipids, calories]
    if not all(required):
        status_label.config(text="Fill all required fields!", fg="red")
        return

    # ===== Directories =====
    scripts_dir = p("media/scripts/generated")
    items_dir = os.path.join(scripts_dir, "items")
    models_dir = p("media/models_X/WorldItems")
    textures_dir = p("media/textures/WorldItems")
    icon_dir = p("media/textures")
    for d in [scripts_dir, items_dir, models_dir, textures_dir, icon_dir]:
        ensure_dir(d)

    # ===== Check for duplicate item =====
    item_file = os.path.join(items_dir, f"{module_name}_Food.txt")
    if os.path.exists(item_file):
        with open(item_file, "r", encoding="utf-8") as f:
            if f"item {item_name}" in f.read():
                status_label.config(text=f"Item '{item_name}' already exists!", fg="red")
                return

    # ===== Translation file =====
    translation_dir = p("media/lua/shared/translate/EN")
    ensure_dir(translation_dir)
    translation_file = os.path.join(translation_dir, f"{module_name}_ItemName_EN.txt")
    with open(translation_file, "w", encoding="utf-8") as f:
        f.write(f"ItemName_EN = {{\n    ItemName_{module_name}.{item_name} = \"{ingame_name}\",\n}}\n")

    # ===== Create Model Script Block =====
    model_script_file = os.path.join(scripts_dir, f"{module_name}_Models.txt")
    model_block = f"""model {asset_name}
{{
    mesh = WorldItems/{asset_name},
    texture = WorldItems/{asset_name},
    scale = 1.0,
}}"""
    insert_inside_last_brace(model_script_file, model_block, module_name=module_name)

    # ===== Create Food Item Block =====
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
        "    ItemType = base:food,",
        f"    Icon = Item_{asset_name},",
        f"    Weight = {weight},",
        f"    HungerChange = {process_value(hunger, hunger_inc, hunger_dec)},",
        f"    ThirstChange = {process_value(thirst, thirst_inc, thirst_dec)},",
        f"    UnhappyChange = {process_value(unhappy, unhappy_inc, unhappy_dec)},",
        f"    FoodType = {foodtype},",
        f"    EatType = {eattype},",
        f"    Carbohydrates = {carbs},",
        f"    Proteins = {proteins},",
        f"    Lipids = {lipids},",
        f"    Calories = {calories},",
    ]
    if customsound:
        item_block_lines.append(f"    CustomEatSound = {customsound},")
    if tags:
        item_block_lines.append(f"    Tags = {tags},")
    if perishable_var.get():
        days_fresh = entry_days_fresh.get().strip()
        days_rotten = entry_days_rotten.get().strip()
        item_block_lines.append(f"    DaysFresh = {days_fresh},")
        item_block_lines.append(f"    DaysTotallyRotten = {days_rotten},")
    if perishable_var.get() and replaceonrotten and replace_text:
        item_block_lines.append(f"    ReplaceOnRotten = {replace_text},")
    if poisonpower:
        item_block_lines.append(f"    PoisonPower = {poison_value},")
    if iscookable:
        item_block_lines.append(f"    IsCookable = true,")
        item_block_lines.append(f"    MinutesToCook = {cook_minutes},")
        item_block_lines.append(f"    MinutesToBurn = {burn_minutes},")
    else:
        item_block_lines.append(f"    IsCookable = false,")
    if fishing: item_block_lines.append("    FishingLure = true,")
    if dangerous: item_block_lines.append("    DangerousUncooked = true,")
    if badcold: item_block_lines.append("    BadCold = true,")
    if badmicrowave: item_block_lines.append("    BadInMicrowave = true,")
    if goodhot: item_block_lines.append("    GoodHot = true,")
# ===== Inside create_food_item() function, replace the evolved section with this =====

    if evolved:
        # EvolvedRecipeName instead of EvolvedRecipe
        item_block_lines.append(f"    EvolvedRecipeName = {evolved_name},")
        if evolved_recipes:
            # Standard value 1, separated by ;
            evolved_items_str = ";".join([f"{r}:1" for r in evolved_recipes])
            item_block_lines.append(f"    EvolvedItems = {evolved_items_str},")

    if cantbe: item_block_lines.append("    CantBeFrozen = true,")
    if spice: item_block_lines.append("    Spice = true,")
    if packaged: item_block_lines.append("    Packaged = true,")
    item_block_lines.append(f"    WorldStaticModel = {asset_name},")
    item_block_lines.append(f"    StaticModel = {asset_name},")
    item_block_lines.append("}")
    insert_inside_last_brace(item_file, "\n".join(item_block_lines), module_name=module_name)

    # ===== Create Placeholders =====
    placeholders = {
        os.path.join(models_dir, f"{asset_name}.fbx"): f"Placeholder FBX for {asset_name}\n",
        os.path.join(textures_dir, f"{asset_name}.png"): f"Placeholder texture for {asset_name}\n",
        os.path.join(icon_dir, f"Item_{asset_name}.png"): f"Placeholder icon for {asset_name}\n"
    }
    for path, content in placeholders.items():
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

    # ===== Reset Fields =====
    entries_to_clear = [entry_item, entry_ingame, entry_asset, entry_weight,
                        entry_hunger, entry_thirst, entry_unhappy,
                        entry_carbs, entry_proteins, entry_lipids, entry_calories, entry_tags,
                        entry_days_fresh, entry_days_rotten, customsound_entry, evolved_name_entry,
                        entry_replace, entry_poison, minutes_to_cook_entry, minutes_to_burn_entry]
    for e in entries_to_clear:
        e.delete(0, tk.END)

    # Reset Increase/Decrease checkboxes
    hunger_inc.set(True); hunger_dec.set(False)
    thirst_inc.set(True); thirst_dec.set(False)
    unhappy_inc.set(True); unhappy_dec.set(False)
    perishable_var.set(False)
    replace_var.set(False)
    customsound_var.set(False)
    tags_var.set(False)
    evolved_var.set(False)
    sweet_var.set(False)
    salty_var.set(False)
    cantbe_var.set(False)
    spice_var.set(False)
    packaged_var.set(False)
    poison_var.set(False)
    iscookable_var.set(False)
    fishing_var.set(False)
    dangerous_var.set(False)
    badcold_var.set(False)
    badmicrowave_var.set(False)
    goodhot_var.set(False)
    for cb in evolved_cbs:
        cb.var.set(False)

    status_label.config(text=f"Food Item Created: {item_name}", fg="#00ff00")

# ===== Buttons =====
tk.Button(buttons_frame, text="Create Item", font=("Segoe UI", 12, "bold"),
          width=24, command=create_food_item).pack(pady=0)

# ===== ChatGPT Footer =====
tk.Label(main_frame, text="Made with ChatGPT by TehaGP for Project Zomboid Build 42.13.2",
         font=("Segoe UI", 8), bg=DARK_BG, fg="#ff5555").place(x=0, y=0)

root.mainloop()
