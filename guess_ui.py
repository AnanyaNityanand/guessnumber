import tkinter as tk
from tkinter import ttk, messagebox
import random, time, json, os, platform

# ----------------------------
# CONFIG
# ----------------------------
BEST_FILE = "best_scores.json"
DIFFICULTIES = {
    "Easy": (1, 20),
    "Medium": (1, 100),
    "Hard": (1, 1000),
}

# ----------------------------
# LOAD / SAVE BEST SCORES
# ----------------------------
def load_best_scores():
    if os.path.exists(BEST_FILE):
        try:
            with open(BEST_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_best_scores(scores):
    try:
        with open(BEST_FILE, "w") as f:
            json.dump(scores, f, indent=2)
    except:
        pass

best_scores = load_best_scores()

# ----------------------------
# MAIN WINDOW
# ----------------------------
root = tk.Tk()
root.title("Guess The Number — Modern UI")
root.geometry("900x600")
root.minsize(700, 500)

canvas = tk.Canvas(root, highlightthickness=0)
canvas.pack(fill="both", expand=True)

def hex_to_rgb(hx):
    hx = hx.lstrip("#")
    return tuple(int(hx[i:i+2], 16) for i in (0,2,4))

def draw_gradient(w, h):
    canvas.delete("grad")
    c1 = "#071227"  # dark blue
    c2 = "#003b45"  # teal
    r1,g1,b1 = hex_to_rgb(c1)
    r2,g2,b2 = hex_to_rgb(c2)
    steps = 120
    for i in range(steps):
        t = i/steps
        r = int(r1 + (r2-r1)*t)
        g = int(g1 + (g2-g1)*t)
        b = int(b1 + (b2-b1)*t)
        color = f"#{r:02x}{g:02x}{b:02x}"
        y1 = int(h * i/steps)
        y2 = int(h*(i+1)/steps)
        canvas.create_rectangle(0, y1, w, y2, fill=color, outline="", tags="grad")

# ----------------------------
# MAIN CARD FRAME
# ----------------------------
card = tk.Frame(canvas, bg="#0b1620")

def place_card():
    w = root.winfo_width()
    h = root.winfo_height()
    cw = min(600, w-60)
    ch = min(420, h-80)
    canvas.create_window(w//2, h//2, window=card, width=cw, height=ch)

# ----------------------------
# WIDGETS INSIDE CARD
# ----------------------------
title = tk.Label(card, text="🎯 Guess The Number", font=("Segoe UI", 20, "bold"), bg="#0b1620", fg="#d9f5f1")
title.pack(pady=(20,5))

subtitle = tk.Label(card, text="A polished modern UI game", font=("Segoe UI", 10), bg="#0b1620", fg="#9fdfe0")
subtitle.pack()

top_frame = tk.Frame(card, bg="#0b1620")
top_frame.pack(pady=(15,5))

diff_var = tk.StringVar(value="Medium")

tk.Label(top_frame, text="Difficulty:", bg="#0b1620", fg="white").pack(side="left")
diff_menu = ttk.Combobox(top_frame, textvariable=diff_var, values=list(DIFFICULTIES.keys()), state="readonly", width=8)
diff_menu.pack(side="left", padx=10)

timer_var = tk.StringVar(value="Time: 00:00:00")
attempts_var = tk.StringVar(value="Attempts: 0")
best_var = tk.StringVar(value="Best: —")

tk.Label(top_frame, textvariable=timer_var, bg="#0b1620", fg="white").pack(side="left", padx=10)
tk.Label(top_frame, textvariable=attempts_var, bg="#0b1620", fg="white").pack(side="left", padx=10)
tk.Label(top_frame, textvariable=best_var, bg="#0b1620", fg="#ffcf91").pack(side="left", padx=10)

message_label = tk.Label(card, text="Press START to begin", bg="#0b1620", fg="white", font=("Segoe UI", 12))
message_label.pack(pady=10)

entry = tk.Entry(card, font=("Segoe UI", 18), justify="center")
entry.pack(pady=5)

# ----------------------------
# GAME LOGIC VARIABLES
# ----------------------------
random_number = None
attempts = 0
running = False
start_time = None
timer_job = None

# ----------------------------
# TIMER FUNCTIONS
# ----------------------------
def format_time(s):
    s = int(s)
    return f"{s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}"

def update_timer():
    global timer_job
    if running:
        elapsed = time.time() - start_time
        timer_var.set("Time: " + format_time(elapsed))
        timer_job = root.after(200, update_timer)

def stop_timer():
    global timer_job
    if timer_job:
        root.after_cancel(timer_job)
        timer_job = None

# ----------------------------
# START GAME
# ----------------------------
def start_game():
    global random_number, attempts, running, start_time
    low, high = DIFFICULTIES[diff_var.get()]
    random_number = random.randint(low, high)
    attempts = 0
    attempts_var.set("Attempts: 0")
    message_label.config(text=f"I've chosen a number between {low} and {high}. Good luck!")
    entry.delete(0, tk.END)
    entry.focus_set()
    running = True
    start_time = time.time()
    update_timer()
    update_best_label()

def update_best_label():
    diff = diff_var.get()
    data = best_scores.get(diff)
    if not data:
        best_var.set("Best: —")
    else:
        best_var.set(f"Best: {data['attempts']} attempts, {data['time']}")

# ----------------------------
# CHECK GUESS
# ----------------------------
def check_guess():
    global attempts, running
    if not running:
        return
    txt = entry.get().strip()
    if not txt.isdigit():
        message_label.config(text="Enter a valid number.")
        return

    guess = int(txt)
    attempts += 1
    attempts_var.set(f"Attempts: {attempts}")

    if guess == random_number:
        running = False
        stop_timer()
        elapsed = time.time() - start_time
        time_str = format_time(elapsed)
        message_label.config(text=f"🎉 Correct! {guess} in {attempts} attempts and {time_str}")
        save_best_score(diff_var.get(), attempts, elapsed)
    elif guess < random_number:
        message_label.config(text="⬆ Too low")
    else:
        message_label.config(text="⬇ Too high")
    entry.delete(0, tk.END)

# ----------------------------
# SAVE BEST SCORE
# ----------------------------
def save_best_score(diff, attempts_count, elapsed):
    global best_scores
    new = False
    tstr = format_time(elapsed)
    old = best_scores.get(diff)

    if not old or attempts_count < old["attempts"] or (attempts_count == old["attempts"] and elapsed < old["elapsed"]):
        new = True

    if new:
        best_scores[diff] = {"attempts": attempts_count, "time": tstr, "elapsed": elapsed}
        save_best_scores(best_scores)
        update_best_label()

# ----------------------------
# BUTTONS
# ----------------------------
btn_frame = tk.Frame(card, bg="#0b1620")
btn_frame.pack(pady=10)

start_btn = tk.Button(btn_frame, text="Start", command=start_game, bg="#00d4e0", fg="black", font=("Segoe UI", 11, "bold"))
start_btn.pack(side="left", padx=10)

check_btn = tk.Button(btn_frame, text="Check", command=check_guess, bg="#90eeef", fg="black", font=("Segoe UI", 11, "bold"))
check_btn.pack(side="left", padx=10)

def reset_game():
    global running
    running = False
    stop_timer()
    message_label.config(text="Press START to begin")
    entry.delete(0, tk.END)
    attempts_var.set("Attempts: 0")
    timer_var.set("Time: 00:00:00")

reset_btn = tk.Button(btn_frame, text="Reset", command=reset_game, bg="#063b45", fg="white", font=("Segoe UI", 11))
reset_btn.pack(side="left", padx=10)

# ----------------------------
# RESIZE HANDLERS
# ----------------------------
def on_resize(event):
    draw_gradient(event.width, event.height)
    place_card()

canvas.bind("<Configure>", on_resize)

# ----------------------------
# ENTER KEY
# ----------------------------
root.bind("<Return>", lambda e: check_guess())

# ----------------------------
# START
# ----------------------------
draw_gradient(900, 600)
place_card()

root.mainloop()
