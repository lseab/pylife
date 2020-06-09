"""
If a box is dead and has EXACTLY 3 live neighbours, then it is born at the next turn.
If a box is alive:
    - if you have 4 or more live neighbours, you die
    - if you have 1 or fewer live neighbours, you die
"""

import tkinter as tk
from presets import Presets


class GameOfLife(tk.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_started = False
        self.resizable(False, False)
        self.grid = Grid(self, borderwidth=0)
        self.grid.pack(side="top", fill="both", expand="true")
        self.controls_frame()
        
    def controls_frame(self):
        controls_frame = tk.Frame(self)
        controls_frame.pack(side="top", pady=20)
        on_off_var = tk.StringVar(value=0)
        play_btn = tk.Radiobutton(controls_frame, text='Play', variable=on_off_var, value=1, indicatoron=False, command=self.play)
        play_btn.grid(row=0, column=0, padx=10)
        stop_btn = tk.Radiobutton(controls_frame, text='Stop', variable=on_off_var, value=0, indicatoron=False, command=self.stop)
        stop_btn.grid(row=0, column=1, padx=10)
        next_btn = tk.Button(controls_frame, text='Next', command=self.next)
        next_btn.grid(row=0, column=2, padx=10)
        reset_btn = tk.Button(controls_frame, text='Reset', command=self.reset)
        reset_btn.grid(row=0, column=3, padx=10)

        self.presets = Presets(self.grid)
        self.input_preset = tk.StringVar()
        self.presets_menu = tk.OptionMenu(controls_frame, self.input_preset, *self.presets.options.keys(), command=self.set_preset)
        self.presets_menu.grid(row=0, column=4, padx=10)

    def set_preset(self, *args):
        preset_func = self.presets.options[self.input_preset.get()]
        preset_func()

    def play(self, *args):
        self.game_started = True

    def stop(self, *args):
        self.game_started = False

    def next(self, *args):
        if not self.game_started: self.grid.update_grid()

    def reset(self, *args):
        self.grid.reset_grid()


class Box:

    def __init__(self, canvas, box_id, row, column):
        self.canvas = canvas
        self.id = box_id
        self.row = row
        self.column = column
        self.alive = False
        self.to_switch = False
        self.neighbours = []
    
    def __repr__(self):
        return f'Box(row={self.row}, column={self.column})'

    def switch_state(self):
        if self.alive:
            self.canvas.itemconfigure(self.id, fill="light gray")
        else:
            self.canvas.itemconfigure(self.id, fill="gray40")
        self.alive = not self.alive
        self.to_switch = False

    def get_live_neighbours(self):
        live_neighbours = 0
        for n in self.neighbours:
            if n.alive: live_neighbours += 1
        return live_neighbours

    def check_future_state(self):
        live_neighbours = self.get_live_neighbours()
        if self.alive:
            if live_neighbours >= 4 or live_neighbours <= 1: self.to_switch = True
        elif live_neighbours == 3: self.to_switch = True   


class Grid(tk.Canvas):

    def __init__(self, root, width=800, height=800, **kwargs):
        super().__init__(root, width=width, height=height, **kwargs)
        self.root = root
        self.width = width
        self.height = height
        self.rows = self.columns = 40
        self.cellwidth = int(self.width/self.columns)
        self.cellheight = int(self.height/self.columns)     
        self.boxes = {}
        self.draw()
        self.bind("<B1-Motion>", self.click_and_drag)
        self.time()

    def draw(self, event=None):
        # Create boxes
        for column in range(self.columns):
            for row in range(self.rows):
                x1 = column * self.cellwidth
                y1 = row * self.cellheight
                x2 = x1 + self.cellwidth
                y2 = y1 + self.cellheight
                box_id = self.create_rectangle(x1,y1,x2,y2, fill="light gray")
                self.boxes[row, column] = Box(self, box_id, row, column)
                self.tag_bind(box_id, "<Button-1>", lambda event, row=row, column=column: self.select_box(self.boxes[row,column]))

        # Add neighbours
        for (row, column) in self.boxes.keys():
            for c in range(column-1, column+2):
                for r in range(row-1, row+2):
                    if (r, c) != (row, column):
                        try:
                            self.boxes[row, column].neighbours.append(self.boxes[r, c])
                        except:
                            continue

    def click_and_drag(self, event):
        row = int(event.y / self.cellheight)
        column = int(event.x / self.cellwidth)
        try:
            box = self.boxes[row,column]
        except:
            return

        if not box.alive:
            self.select_box(box)

    def select_box(self, box):
        box.switch_state()
    
    def time(self):
        if self.root.game_started: self.update_grid()
        self.root.after(100, self.time)

    def update_grid(self):
        for box in self.boxes.values():
            box.check_future_state()
        for box in self.boxes.values():
            if box.to_switch: box.switch_state()

    def reset_grid(self):
        for box in self.boxes.values():
            if box.alive: box.switch_state()