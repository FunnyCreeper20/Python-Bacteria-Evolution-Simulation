import tkinter as tk
from random import randint, choice, random, uniform

# --- Configuration & Data ---
effects_data = {
    "Weakness": "You attack weaker", "Slowness": "You move slower",
    "Aquatic": "You can only breathe underwater", "Carnivore": "You can only eat meat",
    "Herbivore": "You can only eat vegetables", "Poison": "You are poisoned",
    "Butterfingers": "You occasionally drop your items", "Pescatarian": "You can only eat fish",
    "Ender Eyes": "You see colors inversed", "Scatterbrained": "Your inventory gets messed up",
    "Decayed": "You lose your maximum health", "Midas Touch": "Anything you touch turns to gold",
    "Superjump": "You jump extremely high", "Explosive": "You randomly explode",
    "Acceleration": "Your speed randomly changes", "Inexperienced": "You lose all your advancements",
    "Deaf": "You cannot hear well", "Blind": "You have blindness",
    "Amnesic": "Your items can go to previously opened storage", "Dimensional": "You can phase into other dimensions",
    "Insomniac": "You cannot sleep", "Filled": "You cannot eat",
    "Bilingual":"The language changes", "Tweaking":"Your camera randomly turns on its own",
    "Irreproducibility":"You cannot hold the same item 2x", "Electric":"You provide a redstone current",
    "Loud":"You randomly blow a goat horn", "Schizophrenic":"You randomly hear noises",
    "Materialistic":"You cannot drink potions", "Skeptical":"All enchanted gear gets unenchanted",
}


def to_roman(n):
    return ["", "I", "II", "III", "IV", "V"][n] if n < 6 else str(n)


def flattenList(list1):
    tempL = []
    for item in list1:
        if isinstance(item, (list, tuple)):
            tempL.extend(flattenList(item))
        else:
            tempL.append(item)
    return tempL


class Virus:
    def __init__(self, name=None, strength=None, spreadability=None,
                 potency=None, beneficiality=None, mutationChance=None,
                 *effects_input, prev=None):
        self.strength = strength if strength is not None else ((randint(0, 100) / 10) ** 2) / 100
        self.spreadability = spreadability if spreadability is not None else ((randint(0, 100) / 10) ** 2) / 100
        self.potency = potency if potency is not None else randint(10, 150)
        self.beneficiality = beneficiality if beneficiality is not None else randint(-50, 50)
        self.mutationChance = mutationChance if mutationChance is not None else randint(0, 60) / 100
        self.branches = []
        self.prev = prev
        self.effects = flattenList(effects_input) if effects_input else [choice(list(effects_data.keys())) for _ in
                                                                         range(randint(1, 3))]
        self.name = name if name else self.encode_effects(self.effects)
        self.ui_coords = [0, 0]
        self.subtree_width = 25

    def replicate(self):
        new_mut_chance = max(0.01, min(0.95, self.mutationChance + uniform(-0.02, 0.02)))
        if random() < self.mutationChance:
            new_v = self.mutate()
            new_v.mutationChance = new_mut_chance
        else:
            new_v = Virus(self.name,
                          self.strength + uniform(-0.05, 0.05),
                          self.spreadability + uniform(-0.05, 0.05),
                          self.potency + randint(-2, 2),
                          self.beneficiality + randint(-2, 2),
                          new_mut_chance, *self.effects)
        new_v.prev = self
        if (abs(new_v.strength - self.strength) >= 0.10 or set(new_v.effects) != set(self.effects)):
            self.branches.append(new_v)
            new_v.name = self.encode_effects(new_v.effects) if set(new_v.effects) != set(
                self.effects) else f"{self.name}.{len(self.branches)}"
            return new_v, True
        return new_v, False

    def mutate(self):
        magnitude = self.potency / 25
        str_change = magnitude * ((random() - 0.5) / 2 + (self.beneficiality / 50))
        spr_change = magnitude * ((random() - 0.5) / 2 + (self.beneficiality / 50))

        new_effects = self.effects[:]

        # --- GAIN OR LOSE (EXCLUSIVE) ---
        # Beneficiality increases the floor for gaining and decreases the floor for losing
        gain_roll = random() * 200
        lose_roll = random() * 400

        # Chance to gain is boosted by beneficiality
        if gain_roll < (self.potency + self.beneficiality):
            new_key = choice(list(effects_data.keys()))
            new_effects.append(new_key)
        # Chance to lose is suppressed by beneficiality
        elif len(new_effects) > 1 and lose_roll < (self.potency - self.beneficiality):
            new_effects.remove(choice(new_effects))

        return Virus(None, max(0, self.strength + str_change), max(0, self.spreadability + spr_change),
                     self.potency + randint(-10, 10), self.beneficiality + randint(-10, 10),
                     self.mutationChance, *new_effects)

    @staticmethod
    def encode_effects(*effects2):
        effect_keys = list(effects_data.keys())
        sorted_effects = sorted(list(set(flattenList(effects2))))
        return "".join([f"{effect_keys.index(e):02x}" for e in sorted_effects if e in effect_keys])


class VirusTreeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Virus Evolution Lab")
        self.is_paused = False
        self.side_panel = tk.Frame(root, width=300, bg="#252525", padx=10, pady=10)
        self.side_panel.pack(side=tk.LEFT, fill=tk.Y)
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(self.canvas_frame, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.side_panel, text="VIRUS INSPECTOR", fg="cyan", bg="#252525", font=("Arial", 12, "bold")).pack(
            pady=10)
        self.stat_text = tk.Text(self.side_panel, height=25, width=35, bg="#1a1a1a", fg="white", font=("Consolas", 10),
                                 bd=0, padx=5, pady=5)
        self.stat_text.pack()
        self.stat_text.tag_config("faded_green", foreground="#7bed9f")
        self.stat_text.tag_config("faded_red", foreground="#ff6b81")
        self.stat_text.tag_config("light_desc", foreground="#a4b0be")
        self.stat_text.tag_config("label", foreground="cyan")

        self.pause_btn = tk.Button(self.side_panel, text="PAUSE SIMULATION", command=self.toggle_pause, bg="#ff5e57",
                                   fg="black", font=("Arial", 10, "bold"), relief="raised", bd=3)
        self.pause_btn.pack(side=tk.BOTTOM, fill=tk.X, pady=20)

        self.patient_zero = Virus()
        self.population = [self.patient_zero]
        self.gen_count = 0
        self.render_loop()
        self.evolve()

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.pause_btn.config(text="RESUME SIMULATION" if self.is_paused else "PAUSE SIMULATION",
                              bg="#2ed573" if self.is_paused else "#ff5e57")

    def get_quality(self, parent, offspring):
        score = 0
        score += (len(offspring.effects) - len(parent.effects)) * 15
        if len(parent.effects) == len(offspring.effects) and set(parent.effects) != set(offspring.effects):
            score += 5
        score += (offspring.strength - parent.strength) * 2
        score += (offspring.spreadability - parent.spreadability) * 2
        score += (offspring.potency - parent.potency) / 10
        score += (offspring.mutationChance - parent.mutationChance) * 20
        # Increased Beneficiality impact on score (Weight: 3 per 10 units instead of 1)
        score += (offspring.beneficiality - parent.beneficiality) * 0.3

        threshold = 10
        if score >= threshold:
            return "GREEN"
        elif score <= -threshold:
            return "RED"
        else:
            return "BLUE"

    def calculate_positions(self, node, x_start, y_level):
        node.ui_coords = [x_start + (node.subtree_width / 2), y_level]
        current_x = x_start
        for branch in node.branches:
            self.calculate_positions(branch, current_x, y_level + 40)
            current_x += branch.subtree_width

    def update_subtree_widths(self, node):
        if not node.branches:
            node.subtree_width = 25
            return 25
        total_w = sum(self.update_subtree_widths(b) for b in node.branches)
        node.subtree_width = max(25, total_w)
        return node.subtree_width

    def show_info(self, v):
        self.stat_text.config(state=tk.NORMAL)
        self.stat_text.delete(1.0, tk.END)
        self.stat_text.insert(tk.END, f"NAME: {v.name}\n", "label")
        self.stat_text.insert(tk.END, "-" * 25 + "\n")

        def insert_stat(label, current, parent_val, is_percent=False):
            delta = current - parent_val if parent_val is not None else 0
            sym = "%" if is_percent else ""
            mult = 100 if is_percent else 1
            self.stat_text.insert(tk.END, f"{label}: {current * mult:.1f}{sym} ")
            if abs(delta) > 0.001:
                color = "faded_green" if delta > 0 else "faded_red"
                sign = "+" if delta > 0 else ""
                self.stat_text.insert(tk.END, f"{sign}{delta * mult:.1f}{sym}\n", color)
            else:
                self.stat_text.insert(tk.END, "\n")

        p = v.prev
        insert_stat("STR", v.strength, p.strength if p else None)
        insert_stat("SPR", v.spreadability, p.spreadability if p else None)
        insert_stat("POT", float(v.potency), float(p.potency) if p else None)
        insert_stat("MUT", v.mutationChance, p.mutationChance if p else None, True)
        insert_stat("BEN", float(v.beneficiality), float(p.beneficiality) if p else None)
        self.stat_text.insert(tk.END, "\nTRAITS:\n", "label")
        trait_counts = {}
        for e in v.effects: trait_counts[e] = trait_counts.get(e, 0) + 1
        for effect, count in trait_counts.items():
            desc = effects_data.get(effect, '')
            roman = f" {to_roman(count)}" if count > 1 else ""
            self.stat_text.insert(tk.END, f"• {effect}{roman}: ")
            self.stat_text.insert(tk.END, f"{desc}\n", "light_desc")
        self.stat_text.config(state=tk.DISABLED)

    def render_loop(self):
        self.canvas.delete("all")
        self.update_subtree_widths(self.patient_zero)
        cw = self.canvas.winfo_width()
        canvas_width = cw if cw > 1 else 1000
        self.calculate_positions(self.patient_zero, (canvas_width - self.patient_zero.subtree_width) / 2, 50)

        def get_power(v):
            return (len(v.effects) * 15) + (v.strength * 2) + (v.spreadability * 2) + (v.potency / 10) + (
                        v.beneficiality / 10)

        powers = {v: get_power(v) for v in self.population}
        max_v = max(powers, key=powers.get)
        min_v = min(powers, key=powers.get)
        for v in self.population:
            if v.prev: self.canvas.create_line(v.prev.ui_coords[0], v.prev.ui_coords[1], v.ui_coords[0], v.ui_coords[1],
                                               fill="#3d3d3d")
        colors = {"WHITE": "white", "RED": "#ff4757", "BLUE": "#3498db", "GREEN": "#2ecc71"}
        for v in self.population:
            q = "WHITE" if not v.prev else self.get_quality(v.prev, v)
            fill_color = colors.get(q, "white")
            outline_color, thickness = "white", 1
            if v == max_v and len(self.population) > 1:
                fill_color, outline_color, thickness = "#f1c40f", "cyan", 2
            elif v == min_v and len(self.population) > 1:
                fill_color, outline_color = "black", "#555"
            x, y = v.ui_coords
            dot = self.canvas.create_oval(x - 6, y - 6, x + 6, y + 6, fill=fill_color, outline=outline_color,
                                          width=thickness)
            self.canvas.tag_bind(dot, "<Enter>", lambda e, v=v: self.show_info(v))
        self.root.after(200, self.render_loop)

    def evolve(self):
        if not self.is_paused and self.gen_count < 250:
            parent = choice(self.population)
            offspring, is_significant = parent.replicate()
            if is_significant and offspring.name not in [v.name for v in self.population]:
                self.population.append(offspring)
                self.gen_count += 1
        self.root.after(200, self.evolve)


if __name__ == "__main__":
    app = VirusTreeApp(tk.Tk())
    app.root.mainloop()