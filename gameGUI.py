import tkinter as tk
from tkinter import messagebox
from gameLogic import GameLogic

class GameGUI:
    def __init__(self, root, mode, board_size):
        self.root = root
        self.root.title("Connect 6")
        self.mode = mode.lower()
        self.board_size = board_size

        # Initialize game logic
        self.game_logic = GameLogic(mode=self.mode, user_board_size=self.board_size)

        # GUI settings
        self.cell_size = 30
        # margin so stones drawn on intersections don't get clipped
        self.margin = self.cell_size // 2

        # Canvas size must include margins and spacing between intersections
        canvas_size = self.margin * 2 + (self.board_size - 1) * self.cell_size

        # Create canvas
        self.canvas = tk.Canvas(self.root,
                width=canvas_size,
                height=canvas_size,
                bg="white")
        self.canvas.pack()

        # Draw initial grid
        self.draw_grid()

        # Bind mouse clicks
        self.canvas.bind("<Button-1>", self.handle_click)

    def draw_grid(self):
        # Draw grid lines with a half-cell margin so intersections are inset
        for i in range(self.board_size):
            x = self.margin + i * self.cell_size
            self.canvas.create_line(x, self.margin, x, self.margin + (self.board_size - 1) * self.cell_size, fill="black")
            self.canvas.create_line(self.margin, x, self.margin + (self.board_size - 1) * self.cell_size, x, fill="black")


    def handle_click(self, event):
        # Map click to nearest intersection (grid line crossing)
        col = int(round((event.x - self.margin) / self.cell_size))
        row = int(round((event.y - self.margin) / self.cell_size))

        # clamp to board indices
        col = max(0, min(self.board_size - 1, col))
        row = max(0, min(self.board_size - 1, row))

        self.logic(row, col)


    def logic(self, row, col):
        if not self.game_logic.is_valid_move(row, col):
            return

        # Place player's stone
        self.place_piece(row, col)

        # Check for win or draw after placing
        if self.game_logic.check_win(row, col):
            self.declare_winner()
            return

        if self.game_logic.check_draw():
            self.declare_draw()
            return

        # If user placed two stones -> switch to AI
        if self.game_logic.moves_made >= self.game_logic.max_moves_per_turn:
            self.game_logic.switch_player()

            if self.game_logic.current_player == 2:
                self.handle_ai_turn()


    def place_piece(self, row, col):
        self.game_logic.place_piece(row, col)
        # Draw stone centered on the intersection
        cx = self.margin + col * self.cell_size
        cy = self.margin + row * self.cell_size
        r = max(6, self.cell_size // 3)
        x1, y1 = cx - r, cy - r
        x2, y2 = cx + r, cy + r
        color = "black" if self.game_logic.current_player == 1 else "green"
        self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="")

    def handle_ai_turn(self):
        moves = self.game_logic.ai_plays()

        for (row, col) in moves:
            self.place_piece(row, col)

            # Check win
            if self.game_logic.check_win(row, col):
                self.declare_winner()
                return

            # Check draw
            if self.game_logic.check_draw():
                self.declare_draw()
                return

        # Switch back to player 1
        self.game_logic.switch_player()

    def declare_winner(self):
        if self.mode != "pvp":
            winner = "AI wins!" if self.game_logic.current_player == 2 else "You Win!"
        else:
            winner = f"Player {self.game_logic.current_player} wins!"
        # Show message then close the window
        messagebox.showinfo("Game Over", winner)
        try:
            self.root.destroy()
        except Exception:
            pass

    def declare_draw(self):
        draw = "It's a draw!"
        messagebox.showinfo("Game Over", draw)
        try:
            self.root.destroy()
        except Exception:
            pass


    

class GameMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Connect 6")
        self.root.geometry("520x550")


        # Title label
        self.title_label = tk.Label(self.root, text="Connect6", font=("Courier", 30, "bold"), fg="#1a73e8")
        self.title_label.grid(row=0, column=0, columnspan=4, pady=(30, 20))


        # Board size label + entry
        self.board_size_label = tk.Label(self.root, text="Board size:", font=("Courier", 18))
        self.board_size_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.board_entry = tk.Entry(self.root, width=15, font=("Courier", 16))
        self.board_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.enter_button = tk.Button(self.root, text="Set", font=("Courier", 14, "bold"), bg="#4CAF50", fg="white", command=self.read_board_size)
        self.enter_button.grid(row=1, column=2, padx=10, pady=10)


        # Game mode buttons
        ai_button_style = {
            "font": ("Courier", 14, "bold"),
            "width": 15,
            "bg": "#1a73e8",
            "fg": "white",
            "padx": 5,
            "pady": 5
        }

        self.heuristic1_button = tk.Button(self.root, text="AI Heuristic1", command=self.ai_heuristic1, **ai_button_style)
        self.heuristic1_button.grid(row=3, column=0, pady=10, padx=10)

        self.heuristic2_button = tk.Button(self.root, text="AI Heuristic2", command=self.ai_heuristic2, **ai_button_style)
        self.heuristic2_button.grid(row=3, column=1, pady=10, padx=10)

        self.minimax_button = tk.Button(self.root, text="AI Alphabeta1", command=self.ai_alphabeta1, **ai_button_style)
        self.minimax_button.grid(row=4, column=0, pady=10, padx=10)

        self.alpha_beta_button = tk.Button(self.root, text="AI Alphabeta2", command=self.ai_alphabeta2, **ai_button_style)
        self.alpha_beta_button.grid(row=4, column=1, pady=10, padx=10)


        # Credits button
        self.credits_button = tk.Button(self.root, text="Credits", font=("Courier", 14, "bold"), bg="#d93025", fg="white", width=15, command=self.credits)
        self.credits_button.grid(row=5, column=0, columnspan=3, pady=(10, 30))


    # -------------------------------------------------------------------------------
    # Methods
    # -------------------------------------------------------------------------------
    def read_board_size(self):
        """Validates and returns board size."""
        size_text = self.board_entry.get()

        if not size_text.isdigit():
            messagebox.showerror("Invalid Input", "Board size must be a number.")
            return None

        size = int(size_text)

        if size < 6:
            messagebox.showerror("Invalid Size", "Board size must be 6 or larger.")
            return None

        print(f"Board size entered: {size}")
        return size


    def start_game(self, mode):
        """Starts GameGUI with a validated board size."""
        board_size = self.read_board_size()

        if board_size is None:
            return  # invalid input, stop

        new_root = tk.Tk()
        GameGUI(new_root, mode=mode, board_size=board_size)
        try:
            self.root.destroy()
        except Exception:
            pass
        new_root.mainloop()


    # ---- Mode wrappers ---- #
    def ai_heuristic1(self):
        self.start_game("heuristics1")

    def ai_heuristic2(self):
        self.start_game("heuristics2")

    def ai_alphabeta1(self):
        self.start_game("alphabeta1")
    
    def ai_alphabeta2(self):
        self.start_game("alphabeta2")


    def run(self):
        self.root.mainloop()


    def credits(self):
        """Open a small credits popup window."""
        credits_win = tk.Toplevel(self.root)
        credits_win.title("Credits")
        credits_win.geometry("450x350")
        credits_win.resizable(False, False)

        # Center text
        label = tk.Label(
            credits_win,
            text="Connect6 Project\n\nDeveloped by:\n- Omar Ayman\n- Asmaa Maher \n- Dana Mohamed \n- Abdelrahman Adel \n- Malk Mostafa \n- Yahia Mohamed\n\nHelwan University",
            font=("Courier", 14),
            justify="center"
        )
        label.pack(pady=20)

        # Close button
        close_btn = tk.Button(
            credits_win,
            text="Close",
            font=("Courier", 12),
            command=credits_win.destroy
        )
        close_btn.pack(pady=10)

        # Make popup appear above main window
        credits_win.transient(self.root)
        credits_win.grab_set()




# Create and run the UI
launch = GameMenu()
launch.run()