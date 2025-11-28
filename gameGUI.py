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

        # Create canvas
        self.canvas = tk.Canvas(self.root,
                                width=self.board_size * self.cell_size,
                                height=self.board_size * self.cell_size,
                                bg="white")
        self.canvas.pack()

        # Draw initial grid
        self.draw_grid()

        # Bind mouse clicks
        self.canvas.bind("<Button-1>", self.handle_click)

    def draw_grid(self):
        for i in range(self.board_size):
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, self.board_size * self.cell_size, fill="black")
            self.canvas.create_line(0, x, self.board_size * self.cell_size, x, fill="black")


    def handle_click(self, event):
        row, col = event.y // self.cell_size, event.x // self.cell_size
        self.logic(row, col)


    def logic(self, row, col):
        if not self.game_logic.is_valid_move(row, col):
            return  # ignore invalid clicks

        # Place the user's stone
        self.place_piece(row, col)

        # Check for win
        if self.game_logic.check_win(row, col):
            self.declare_winner()
            return

        # Check for draw
        if self.game_logic.check_draw():
            self.declare_draw()
            return

        # If the player has placed 2 stones, switch player
        if self.game_logic.moves_made >= self.game_logic.max_moves_per_turn:
            self.game_logic.switch_player()

            # AI turn
            if self.game_logic.current_player == 2:
                self.handle_ai_turn()

    def place_piece(self, row, col):
        self.game_logic.place_piece(row, col)
        x1, y1 = col * self.cell_size + 2, row * self.cell_size + 2
        x2, y2 = (col + 1) * self.cell_size - 2, (row + 1) * self.cell_size - 2
        color = "black" if self.game_logic.current_player == 1 else "green"
        self.canvas.create_oval(x1, y1, x2, y2, fill=color)

    def handle_ai_turn(self):
        for _ in range(self.game_logic.max_moves_per_turn):
            row, col = self.game_logic.ai_plays()
            if row is not None and col is not None:

                self.place_piece(row, col)

                # Check for win
                if self.game_logic.check_win(row, col):
                    self.declare_winner()
                    return
                
                # Check for draw
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

        self.root.destroy()
        messagebox.showinfo("Game Over", winner)

    def declare_draw(self):
        draw = "It's a draw!"
        self.root.destroy()
        messagebox.showinfo("Game Over", draw)


    

class GameMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Connect 6")
        self.root.geometry("650x600")


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
        ai_button_style = {"font": ("Courier", 14, "bold"), "width": 15, "bg": "#1a73e8", "fg": "white", "padx": 5, "pady": 5}

        self.minimax_button = tk.Button(self.root, text="AI Minimax", command=self.ai_MiniMax, **ai_button_style)
        self.minimax_button.grid(row=3, column=0, pady=10, padx=5)

        self.alpha_beta_button = tk.Button(self.root, text="AI AlphaBeta", command=self.ai_AlphBeta, **ai_button_style)
        self.alpha_beta_button.grid(row=3, column=1, pady=10, padx=5)

        self.heuristic_button = tk.Button(self.root, text="AI Heuristic", command=self.ai_Heuristic, **ai_button_style)
        self.heuristic_button.grid(row=3, column=2, pady=10, padx=5)

        self.heuristic2_button = tk.Button(self.root, text="AI Heuristic2", command=self.ai_Heuristic2, **ai_button_style)
        self.heuristic2_button.grid(row=4, column=0, columnspan=3, pady=(10, 20))

        # Credits button
        self.credits_button = tk.Button(self.root, text="Credits", font=("Courier", 14, "bold"), bg="#d93025", fg="white", width=15, command=self.credits)
        self.credits_button.grid(row=5, column=0, columnspan=3, pady=(10, 30))



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
        self.root.destroy()


    # ---- Mode wrappers ---- #
    def ai_MiniMax(self):
        self.start_game("minimax")

    def ai_AlphBeta(self):
        self.start_game("alphabeta")

    def ai_Heuristic(self):
        self.start_game("heuristics1")

    def ai_Heuristic2(self):
        self.start_game("heuristics2")


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