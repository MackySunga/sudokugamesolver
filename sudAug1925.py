
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import font as tkfont
from typing import List, Tuple, Optional, Set
import random
import time

Board = List[List[int]]


# ------------- Sudoku Solvers & Utilities ------------- #
class SudokuLogic:
    @staticmethod
    def deep_copy(board: Board) -> Board:
        return [row[:] for row in board]

    @staticmethod
    def is_valid_move(board: Board, r: int, c: int, v: int) -> bool:
        if v == 0:
            return True
        if any(board[r][x] == v for x in range(9) if x != c):
            return False
        if any(board[x][c] == v for x in range(9) if x != r):
            return False
        br, bc = (r // 3) * 3, (c // 3) * 3
        for i in range(br, br + 3):
            for j in range(bc, bc + 3):
                if (i != r or j != c) and board[i][j] == v:
                    return False
        return True

    @staticmethod
    def find_empty(board: Board) -> Optional[Tuple[int, int]]:
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return i, j
        return None

    @staticmethod
    def candidates(board: Board, r: int, c: int) -> Set[int]:
        if board[r][c] != 0:
            return set()
        used = set(board[r])
        used |= {board[x][c] for x in range(9)}
        br, bc = (r // 3) * 3, (c // 3) * 3
        for i in range(br, br + 3):
            for j in range(bc, bc + 3):
                used.add(board[i][j])
        return {v for v in range(1, 10) if v not in used}

    @staticmethod
    def solve_bruteforce(board: Board, moves: List[str]) -> Optional[Board]:
        board = SudokuLogic.deep_copy(board)

        def bt() -> bool:
            empty = SudokuLogic.find_empty(board)
            if not empty:
                return True
            r, c = empty
            for v in range(1, 10):
                if SudokuLogic.is_valid_move(board, r, c, v):
                    moves.append(f"Try r{r+1}c{c+1} = {v}")
                    board[r][c] = v
                    if bt():
                        return True
                    moves.append(f"Backtrack r{r+1}c{c+1} (reset from {v} to 0)")
                    board[r][c] = 0
            return False

        return board if bt() else None

    @staticmethod
    def propagate_singles(board: Board, moves: List[str]) -> bool:
        changed = False
        while True:
            progress = False
            for r in range(9):
                for c in range(9):
                    if board[r][c] == 0:
                        cand = SudokuLogic.candidates(board, r, c)
                        if len(cand) == 1:
                            val = next(iter(cand))
                            board[r][c] = val
                            moves.append(f"Singleton r{r+1}c{c+1} = {val}")
                            progress = True
            if not progress:
                break
            changed = True
        return changed

    @staticmethod
    def solve_backtracking_propagation(board: Board, moves: List[str]) -> Optional[Board]:
        board = SudokuLogic.deep_copy(board)
        SudokuLogic.propagate_singles(board, moves)

        def select_mrv_cell() -> Optional[Tuple[int, int, Set[int]]]:
            best = None
            best_cands: Optional[Set[int]] = None
            for r in range(9):
                for c in range(9):
                    if board[r][c] == 0:
                        cand = SudokuLogic.candidates(board, r, c)
                        if not cand:
                            return None
                        if best is None or len(cand) < len(best_cands):  # type: ignore
                            best = (r, c)
                            best_cands = cand
            if best is None:
                return None
            return best[0], best[1], best_cands  # type: ignore

        def bt() -> bool:
            mrv = select_mrv_cell()
            if mrv is None:
                return SudokuLogic.find_empty(board) is None
            r, c, cand = mrv
            for v in sorted(cand):
                moves.append(f"MRV choose r{r+1}c{c+1} try {v}")
                if SudokuLogic.is_valid_move(board, r, c, v):
                    board[r][c] = v
                    SudokuLogic.propagate_singles(board, moves)
                    if bt():
                        return True
                    moves.append(f"Backtrack r{r+1}c{c+1} (reset from {v} to 0)")
                    board[r][c] = 0
            return False

        return board if bt() else None

    @staticmethod
    def is_complete_and_valid(board: Board) -> bool:
        for r in range(9):
            if sorted(board[r]) != list(range(1, 10)):
                return False
        for c in range(9):
            col = [board[r][c] for r in range(9)]
            if sorted(col) != list(range(1, 10)):
                return False
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                box = [board[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3)]
                if sorted(box) != list(range(1, 10)):
                    return False
        return True


EASY_PUZZLES = [
    [
        [5,3,0,0,7,0,0,0,0],
        [6,0,0,1,9,5,0,0,0],
        [0,9,8,0,0,0,0,6,0],
        [8,0,0,0,6,0,0,0,3],
        [4,0,0,8,0,3,0,0,1],
        [7,0,0,0,2,0,0,0,6],
        [0,6,0,0,0,0,2,8,0],
        [0,0,0,4,1,9,0,0,5],
        [0,0,0,0,8,0,0,7,9],
    ],
    [
        [1,0,0,4,8,9,0,0,6],
        [7,3,0,0,0,0,0,4,0],
        [0,0,0,0,0,1,2,9,5],
        [0,0,7,1,2,0,6,0,0],
        [5,0,0,7,0,3,0,0,8],
        [0,0,6,0,9,5,7,0,0],
        [9,1,4,6,0,0,0,0,0],
        [0,2,0,0,0,0,0,3,7],
        [8,0,0,9,3,4,0,0,0],
    ],
    [
        [0,0,0,2,6,0,7,0,1],
        [6,8,0,0,7,0,0,9,0],
        [1,9,0,0,0,4,5,0,0],
        [8,2,0,1,0,0,0,4,0],
        [0,0,4,6,0,2,9,0,0],
        [0,5,0,0,0,3,0,2,8],
        [0,0,9,3,0,0,0,7,4],
        [0,4,0,0,5,0,0,3,6],
        [7,0,3,0,1,8,0,0,0],
    ],
]

MEDIUM_PUZZLES = [
    [
        [0,2,0,6,0,8,0,0,0],
        [5,8,0,0,0,9,7,0,0],
        [0,0,0,0,4,0,0,0,0],
        [3,7,0,0,0,0,5,0,0],
        [6,0,0,0,0,0,0,0,4],
        [0,0,8,0,0,0,0,1,3],
        [0,0,0,0,2,0,0,0,0],
        [0,0,9,8,0,0,0,3,0],
        [0,0,0,0,0,6,0,0,5],
    ],
    [
        [0,0,0,0,0,0,2,0,0],
        [0,8,0,0,0,7,0,9,0],
        [6,0,2,0,0,0,5,0,0],
        [0,7,0,0,6,0,0,0,0],
        [0,0,0,9,0,1,0,0,0],
        [0,0,0,0,2,0,0,1,0],
        [0,0,9,0,0,0,7,0,6],
        [0,2,0,7,0,0,0,8,0],
        [0,0,6,0,0,0,0,0,0],
    ],
    [
        [0,0,0,0,0,0,0,0,0],
        [0,4,0,0,0,0,0,0,2],
        [0,0,0,0,0,7,0,0,0],
        [0,0,0,0,6,0,0,0,0],
        [0,0,0,7,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,9,0,0,0,0,0],
        [0,0,0,0,0,0,0,8,0],
        [0,0,0,0,0,0,1,0,0],
    ],
]

HARD_PUZZLES = [
    [
        [0,0,0,0,0,0,0,1,2],
        [0,0,0,0,0,0,0,0,0],
        [0,0,1,0,0,0,0,0,0],
        [0,0,0,0,0,6,0,0,0],
        [0,0,0,0,0,0,3,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,9,0,0,0,0],
        [0,0,0,4,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
    ],
    [
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,3,0,8,5],
        [0,0,1,0,2,0,0,0,0],
        [0,0,0,5,0,7,0,0,0],
        [0,0,4,0,0,0,1,0,0],
        [0,9,0,0,0,0,0,0,0],
        [5,0,0,0,0,0,0,7,3],
        [0,0,2,0,1,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
    ],
    [
        [8,0,0,0,0,0,0,0,0],
        [0,0,3,6,0,0,0,0,0],
        [0,7,0,0,9,0,2,0,0],
        [0,5,0,0,0,7,0,0,0],
        [0,0,0,0,4,5,7,0,0],
        [0,0,0,1,0,0,0,3,0],
        [0,0,1,0,0,0,0,6,8],
        [0,0,8,5,0,0,0,1,0],
        [0,9,0,0,0,0,4,0,0],
    ],
]


class SudokuApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Sudoku — Tkinter")
        self.resizable(False, False)

        self.board_vars: List[List[tk.StringVar]] = [[tk.StringVar() for _ in range(9)] for _ in range(9)]
        self.entries: List[List[tk.Entry]] = [[None for _ in range(9)] for _ in range(9)]  # type: ignore
        self.given_mask: List[List[bool]] = [[False]*9 for _ in range(9)]
        self.base_colors: List[List[str]] = [["white"]*9 for _ in range(9)]
        self.current_puzzle: Board = [[0]*9 for _ in range(9)]
        self.current_solution: Optional[Board] = None

        self.moves_count = 0
        self.hints_used = 0
        self.user_puzzles: List[Tuple[Board, Board]] = []

        self.difficulty_var = tk.StringVar(value="Easy")
        self.updating = False

        self.timer_seconds_total = 0
        self.timer_seconds_left = 0
        self.timer_running = False
        self.timer_job: Optional[str] = None

        self.font_given = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.font_user = tkfont.Font(family="Segoe UI", size=14, slant="italic")
        self.font_normal = tkfont.Font(family="Segoe UI", size=14)

        self._build_layout()
        # Fixed: load an initial puzzle via the existing restart method
        self._restart_puzzle()

    def _build_layout(self) -> None:
        main = ttk.Frame(self, padding=10)
        main.grid(row=0, column=0)

        grid_frame = ttk.Frame(main, padding=5, borderwidth=2, relief="groove")
        grid_frame.grid(row=0, column=0, sticky="n")
        self._build_grid(grid_frame)

        side = ttk.Frame(main, padding=(10, 0))
        side.grid(row=0, column=1, sticky="n")

        diff_row = ttk.Frame(side)
        diff_row.pack(anchor="w", pady=(0, 6))
        ttk.Label(diff_row, text="Difficulty:").pack(side="left", padx=(0, 6))
        ttk.OptionMenu(diff_row, self.difficulty_var, self.difficulty_var.get(),
                       "Easy", "Medium", "Hard", "User Provided",
                       command=lambda _=None: self._on_difficulty_change()).pack(side="left")

        btn_row1 = ttk.Frame(side)
        btn_row1.pack(fill="x", pady=4)
        ttk.Button(btn_row1, text="Restart Puzzle", command=self._restart_puzzle).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(btn_row1, text="Clear Puzzle", command=self._clear_puzzle).pack(side="left", fill="x", expand=True)

        btn_row2 = ttk.Frame(side)
        btn_row2.pack(fill="x", pady=4)
        ttk.Button(btn_row2, text="Hint", command=self._hint).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(btn_row2, text="Solve Puzzle", command=self._solve_puzzle_interactive).pack(side="left", fill="x", expand=True)

        timer_box = ttk.LabelFrame(side, text="Timer")
        timer_box.pack(fill="x", pady=8)
        self.timer_label = ttk.Label(timer_box, text="00:00", font=("Segoe UI", 14))
        self.timer_label.pack(side="left", padx=(6, 6), pady=6)
        ttk.Button(timer_box, text="Set Countdown", command=self._set_timer_dialog).pack(side="left", padx=(0, 4))
        ttk.Button(timer_box, text="Stop", command=self._stop_timer).pack(side="left")

        user_box = ttk.LabelFrame(side, text="User Provided")
        user_box.pack(fill="x", pady=8)
        ttk.Button(user_box, text="Save as User Puzzle", command=self._save_user_puzzle).pack(fill="x", padx=6, pady=3)
        ttk.Button(user_box, text="Verify User Solution", command=self._verify_user_solution).pack(fill="x", padx=6, pady=3)

        stats = ttk.LabelFrame(side, text="Stats")
        stats.pack(fill="x", pady=8)
        self.moves_label = ttk.Label(stats, text="Moves: 0")
        self.moves_label.pack(anchor="w", padx=6, pady=(6, 0))
        self.hints_label = ttk.Label(stats, text="Hints used: 0")
        self.hints_label.pack(anchor="w", padx=6, pady=(0, 6))

        log_box = ttk.LabelFrame(side, text="Solver Moves")
        log_box.pack(fill="both", expand=True, pady=8)
        self.moves_list = tk.Listbox(log_box, height=18, width=42)
        self.moves_list.pack(fill="both", expand=True, padx=6, pady=6)

    def _build_grid(self, parent: tk.Widget) -> None:
        self.cell_frames: List[List[ttk.Frame]] = [[None for _ in range(9)] for _ in range(9)]  # type: ignore
        for br in range(3):
            for bc in range(3):
                box = ttk.Frame(parent, padding=3, borderwidth=2, relief="ridge")
                box.grid(row=br, column=bc, padx=2, pady=2)
                for i in range(3):
                    for j in range(3):
                        r, c = br*3 + i, bc*3 + j
                        cell_frame = ttk.Frame(box, padding=1)
                        cell_frame.grid(row=i, column=j, padx=1, pady=1)
                        e = tk.Entry(cell_frame, width=2, justify="center",
                                     font=self.font_user, relief="flat")
                        e.grid(row=0, column=0, ipadx=6, ipady=6)
                        vcmd = (self.register(self._validate_digit), "%P")
                        e.configure(validate="key", validatecommand=vcmd)
                        e.bind("<Enter>", lambda _evt, rr=r, cc=c: self._on_cell_hover(rr, cc, entering=True))
                        e.bind("<Leave>", lambda _evt, rr=r, cc=c: self._on_cell_hover(rr, cc, entering=False))
                        e.bind("<FocusIn>", lambda _evt, rr=r, cc=c: self._on_cell_hover(rr, cc, entering=True))
                        e.bind("<FocusOut>", lambda _evt, rr=r, cc=c: self._on_cell_hover(rr, cc, entering=False))
                        var = self.board_vars[r][c]
                        var.trace_add("write", lambda *_args, rr=r, cc=c: self._on_cell_write(rr, cc))
                        e.configure(textvariable=var)
                        self.entries[r][c] = e
                        self.cell_frames[r][c] = ttk.Frame(box)

    # Remaining methods identical to previous version (no functional change) ---
    # For brevity, we reuse the same definitions from the last file.
    # To keep the file self-contained for you, we paste all remaining methods unchanged below.

    def _get_board(self) -> Board:
        board: Board = [[0]*9 for _ in range(9)]
        for r in range(9):
            for c in range(9):
                s = self.board_vars[r][c].get().strip()
                board[r][c] = int(s) if s.isdigit() else 0
        return board

    def _set_board(self, board: Board, as_given: bool) -> None:
        self.updating = True
        try:
            for r in range(9):
                for c in range(9):
                    v = board[r][c]
                    self.board_vars[r][c].set("" if v == 0 else str(v))
                    e = self.entries[r][c]
                    if as_given and v != 0:
                        e.configure(state="readonly", font=self.font_given, fg="black")
                        self.given_mask[r][c] = True
                        self.base_colors[r][c] = "white"
                        e.configure(readonlybackground="white")
                    else:
                        e.configure(state="normal", font=self.font_user, fg="blue")
                        self.given_mask[r][c] = False
                        self.base_colors[r][c] = "white"
                        e.configure(background="white")
            self._clear_hint_colors()
        finally:
            self.updating = False

    def _clear_hint_colors(self) -> None:
        for r in range(9):
            for c in range(9):
                e = self.entries[r][c]
                base = self.base_colors[r][c]
                if self.given_mask[r][c]:
                    e.configure(readonlybackground=base)
                else:
                    e.configure(background=base)

    def _validate_digit(self, proposed: str) -> bool:
        if proposed == "":
            return True
        if len(proposed) > 1:
            return False
        return proposed in "123456789"

    def _on_cell_write(self, r: int, c: int) -> None:
        if self.updating or self.given_mask[r][c]:
            return
        self.moves_count += 1
        self.moves_label.config(text=f"Moves: {self.moves_count}")
        e = self.entries[r][c]
        e.configure(state="normal", font=self.font_user, fg="blue")

    def _on_cell_hover(self, r: int, c: int, entering: bool) -> None:
        color = "#E6F3FF" if entering else None
        br, bc = (r // 3) * 3, (c // 3) * 3
        targets = {(r, x) for x in range(9)}
        targets |= {(x, c) for x in range(9)}
        targets |= {(i, j) for i in range(br, br + 3) for j in range(bc, bc + 3)}
        for (i, j) in targets:
            e = self.entries[i][j]
            if entering:
                if self.given_mask[i][j]:
                    e.configure(readonlybackground=color or self.base_colors[i][j])
                else:
                    e.configure(background=color or self.base_colors[i][j])
            else:
                base = self.base_colors[i][j]
                if self.given_mask[i][j]:
                    e.configure(readonlybackground=base)
                else:
                    e.configure(background=base)

    def _on_difficulty_change(self) -> None:
        messagebox.showinfo("Difficulty Changed",
                            "Difficulty updated. Click 'Restart Puzzle' to load a new one.")

    def _restart_puzzle(self) -> None:
        diff = self.difficulty_var.get()
        if diff == "Easy":
            pool = EASY_PUZZLES
        elif diff == "Medium":
            pool = MEDIUM_PUZZLES
        elif diff == "Hard":
            pool = HARD_PUZZLES
        elif diff == "User Provided":
            if not self.user_puzzles:
                messagebox.showwarning("No User Puzzles", "Save a user puzzle first.")
                return
            pool = [p for (p, _s) in self.user_puzzles]
        else:
            pool = EASY_PUZZLES

        self.current_puzzle = SudokuLogic.deep_copy(random.choice(pool))
        self._set_board(self.current_puzzle, as_given=True)
        self.moves_count = 0
        self.hints_used = 0
        self.moves_label.config(text="Moves: 0")
        self.hints_label.config(text="Hints used: 0")
        self.moves_list.delete(0, tk.END)
        self._enable_all_controls()
        self._stop_timer(reset_label=True)
        self.current_solution = self._compute_solution(self.current_puzzle)

    def _compute_solution(self, puzzle: Board) -> Optional[Board]:
        moves_dummy: List[str] = []
        solved = SudokuLogic.solve_backtracking_propagation(puzzle, moves_dummy)
        return solved

    def _clear_puzzle(self) -> None:
        self.updating = True
        try:
            for r in range(9):
                for c in range(9):
                    if not self.given_mask[r][c]:
                        self.board_vars[r][c].set("")
                        self.base_colors[r][c] = "white"
                        self.entries[r][c].configure(background="white")
            self._clear_hint_colors()
        finally:
            self.updating = False

    def _hint(self) -> None:
        if self.current_solution is None:
            self.current_solution = self._compute_solution(self._get_board())
            if self.current_solution is None:
                messagebox.showerror("No Solution", "Cannot compute a solution to compare with.")
                return

        self.hints_used += 1
        self.hints_label.config(text=f"Hints used: {self.hints_used}")

        cur = self._get_board()
        for r in range(9):
            for c in range(9):
                if self.given_mask[r][c]:
                    self.base_colors[r][c] = "white"
                    self.entries[r][c].configure(readonlybackground="white")
                else:
                    v = cur[r][c]
                    if v == 0:
                        self.base_colors[r][c] = "white"
                        self.entries[r][c].configure(background="white")
                    else:
                        if v == self.current_solution[r][c]:
                            self.base_colors[r][c] = "#FFF59D"
                            self.entries[r][c].configure(background="#FFF59D")
                        else:
                            self.base_colors[r][c] = "#FFCDD2"
                            self.entries[r][c].configure(background="#FFCDD2")

    def _solve_puzzle_interactive(self) -> None:
        if not messagebox.askyesno("Solve Puzzle?", "Are you sure you want to reveal the solution?"):
            return
        algo = self._ask_algorithm()
        if not algo:
            return
        self._run_solver_and_render(algo, disable_after=True)

    def _run_solver_and_render(self, algo: str, disable_after: bool) -> None:
        board = self._get_board()
        moves: List[str] = []
        start = time.time()
        if algo == "brute":
            solved = SudokuLogic.solve_bruteforce(board, moves)
        else:
            solved = SudokuLogic.solve_backtracking_propagation(board, moves)
        elapsed = time.time() - start

        self.moves_list.delete(0, tk.END)
        if solved is None:
            self.moves_list.insert(tk.END, "No solution found.")
            messagebox.showerror("Unsolvable", "No solution could be found.")
            return

        self._set_board(solved, as_given=True)
        self.current_solution = solved

        self.moves_list.insert(tk.END, f"[{algo.upper()}] Solved in {len(moves)} steps, {elapsed:.3f}s")
        for m in moves:
            self.moves_list.insert(tk.END, m)

        if disable_after:
            self._enable_only_restart()

    def _ask_algorithm(self) -> Optional[str]:
        dlg = tk.Toplevel(self)
        dlg.title("Choose Algorithm")
        dlg.resizable(False, False)
        ttk.Label(dlg, text="Select solving algorithm:").pack(padx=12, pady=(12, 6))
        algo_var = tk.StringVar(value="brute")

        row = ttk.Frame(dlg)
        row.pack(padx=12, pady=6, fill="x")
        ttk.Radiobutton(row, text="Brute Force", variable=algo_var, value="brute").pack(anchor="w")
        ttk.Radiobutton(row, text="Backtracking + Propagation", variable=algo_var, value="prop").pack(anchor="w")

        btns = ttk.Frame(dlg)
        btns.pack(pady=12)
        chosen = {"value": None}

        def ok():
            chosen["value"] = algo_var.get()
            dlg.destroy()

        def cancel():
            chosen["value"] = None
            dlg.destroy()

        ttk.Button(btns, text="OK", command=ok).pack(side="left", padx=6)
        ttk.Button(btns, text="Cancel", command=cancel).pack(side="left", padx=6)
        dlg.transient(self)
        dlg.grab_set()
        self.wait_window(dlg)
        return chosen["value"]  # type: ignore

    def _enable_only_restart(self) -> None:
        def walk_disable(widget: tk.Widget):
            for w in widget.winfo_children():
                if isinstance(w, (ttk.Button,)):
                    if getattr(w, "cget")("text") == "Restart Puzzle":
                        continue
                    try:
                        w.configure(state="disabled")
                    except tk.TclError:
                        pass
                walk_disable(w)
        walk_disable(self)
        for r in range(9):
            for c in range(9):
                self.entries[r][c].configure(state="readonly", font=self.font_given, fg="black")

    def _enable_all_controls(self) -> None:
        def walk_enable(widget: tk.Widget):
            for w in widget.winfo_children():
                if isinstance(w, (ttk.Button,)):
                    try:
                        w.configure(state="normal")
                    except tk.TclError:
                        pass
                walk_enable(w)
        walk_enable(self)
        for r in range(9):
            for c in range(9):
                if not self.given_mask[r][c]:
                    self.entries[r][c].configure(state="normal", font=self.font_user, fg="blue")

    def _set_timer_dialog(self) -> None:
        minutes = simpledialog.askinteger("Set Timer", "Minutes:", minvalue=0, maxvalue=999, parent=self)
        if minutes is None:
            return
        seconds = simpledialog.askinteger("Set Timer", "Seconds:", minvalue=0, maxvalue=59, parent=self)
        if seconds is None:
            return
        total = minutes * 60 + seconds
        self._start_timer(total)

    def _start_timer(self, total_seconds: int) -> None:
        self._stop_timer(reset_label=False)
        self.timer_seconds_total = total_seconds
        self.timer_seconds_left = total_seconds
        self.timer_running = True
        self._update_timer_label(red=False)
        self._tick()

    def _stop_timer(self, reset_label: bool = True) -> None:
        self.timer_running = False
        if self.timer_job is not None:
            try:
                self.after_cancel(self.timer_job)
            except Exception:
                pass
            self.timer_job = None
        if reset_label:
            self.timer_label.configure(text="00:00", foreground="black")

    def _tick(self) -> None:
        if not self.timer_running:
            return
        self._update_timer_label(red=False)
        if self.timer_seconds_left <= 0:
            self.timer_running = False
            self._on_time_up()
            return
        self.timer_seconds_left -= 1
        self.timer_job = self.after(1000, self._tick)

    def _update_timer_label(self, red: bool) -> None:
        mm = self.timer_seconds_left // 60
        ss = self.timer_seconds_left % 60
        self.timer_label.configure(text=f"{mm:02d}:{ss:02d}",
                                   foreground=("red" if red else "black"))

    def _on_time_up(self) -> None:
        cont = messagebox.askyesno("Time's Up", "Time is up! Continue playing? (Yes = continue, No = auto-solve)")
        if cont:
            self.timer_running = False
            self.timer_seconds_left = 0
            self._update_timer_label(red=True)
            return
        algo = self._ask_algorithm()
        if not algo:
            return
        self._run_solver_and_render(algo, disable_after=True)

    def _save_user_puzzle(self) -> None:
        puzzle = self._get_board()
        if all(puzzle[r][c] == 0 for r in range(9) for c in range(9)):
            messagebox.showwarning("Empty Grid", "Enter some givens before saving as a user puzzle.")
            return
        text = simpledialog.askstring(
            "Provide Solution",
            "Enter the full 9x9 solution.\n"
            "- Option A: 81 digits (rows concatenated)\n"
            "- Option B: 9 lines of 9 digits\n",
            parent=self
        )
        if text is None:
            return
        sol = self._parse_solution(text)
        if sol is None:
            messagebox.showerror("Invalid Solution", "Could not parse the provided solution.")
            return
        if not SudokuLogic.is_complete_and_valid(sol):
            messagebox.showerror("Invalid Solution", "The provided solution is not a valid Sudoku solution.")
            return
        for r in range(9):
            for c in range(9):
                if puzzle[r][c] != 0 and puzzle[r][c] != sol[r][c]:
                    messagebox.showerror("Mismatch", f"Given at r{r+1}c{c+1} conflicts with provided solution.")
                    return
        self.user_puzzles.append((puzzle, sol))
        messagebox.showinfo("Saved", f"User puzzle saved. Total saved: {len(self.user_puzzles)}")
        self.difficulty_var.set("User Provided")

    def _parse_solution(self, text: str) -> Optional[Board]:
        lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
        digits = "".join(ch for ch in text if ch.isdigit())
        if len(lines) == 9 and all(len(ln) == 9 and ln.isdigit() for ln in lines):
            return [[int(ch) for ch in ln] for ln in lines]
        if len(digits) == 81:
            return [[int(digits[r*9 + c]) for c in range(9)] for r in range(9)]
        return None

    def _verify_user_solution(self) -> None:
        board = self._get_board()
        text = simpledialog.askstring("Verify User Solution",
                                      "Paste the user-provided solution here (81 digits or 9x9 lines):",
                                      parent=self)
        if text is None:
            return
        user_sol = self._parse_solution(text)
        if user_sol is None:
            messagebox.showerror("Invalid", "Could not parse the provided solution.")
            return
        if not SudokuLogic.is_complete_and_valid(user_sol):
            messagebox.showerror("Invalid", "Provided solution is not a valid Sudoku solution.")
            return

        moves_a: List[str] = []
        moves_b: List[str] = []
        sa = SudokuLogic.solve_bruteforce(board, moves_a)
        sb = SudokuLogic.solve_backtracking_propagation(board, moves_b)

        msg = []
        if sa is None:
            msg.append("Brute Force: No solution found.")
        else:
            msg.append("Brute Force: Solved.")
            msg.append(" - Matches provided: " + str(sa == user_sol))
        if sb is None:
            msg.append("Backtracking+Prop: No solution found.")
        else:
            msg.append("Backtracking+Prop: Solved.")
            msg.append(" - Matches provided: " + str(sb == user_sol))

        messagebox.showinfo("Verification Result", "\n".join(msg))


if __name__ == "__main__":
    app = SudokuApp()
    app.mainloop()