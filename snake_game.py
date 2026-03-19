"""Simple Snake game implemented with tkinter.

Run:
    python snake_game.py
"""

from __future__ import annotations

import random
import tkinter as tk


CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT
INITIAL_SPEED_MS = 120
MIN_SPEED_MS = 60
SPEED_STEP_MS = 2


class SnakeGame:
    """Manage game state, rendering, and input handling."""

    def __init__(self, root: tk.Tk) -> None:
        """Initialize the game window and state.

        Args:
            root: Root tkinter window.
        """
        self.root = root
        self.root.title("Snake")
        self.root.resizable(False, False)

        self.score_var = tk.StringVar()
        self.status_var = tk.StringVar()

        info_frame = tk.Frame(self.root, padx=10, pady=8)
        info_frame.pack(fill="x")

        tk.Label(
            info_frame,
            textvariable=self.score_var,
            font=("Consolas", 12, "bold"),
        ).pack(side="left")
        tk.Label(
            info_frame,
            textvariable=self.status_var,
            font=("Consolas", 11),
        ).pack(side="right")

        self.canvas = tk.Canvas(
            self.root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg="#111111",
            highlightthickness=0,
        )
        self.canvas.pack(padx=10, pady=(0, 10))

        self.root.bind("<KeyPress>", self.on_key_press)

        self.after_id: str | None = None
        self.is_game_over = False
        self.restart()

    def restart(self) -> None:
        """Reset the game to its initial state."""
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        center_x = GRID_WIDTH // 2
        center_y = GRID_HEIGHT // 2

        self.snake = [
            (center_x, center_y),
            (center_x - 1, center_y),
            (center_x - 2, center_y),
        ]
        self.direction = (1, 0)
        self.pending_direction = self.direction
        self.score = 0
        self.speed_ms = INITIAL_SPEED_MS
        self.is_game_over = False
        self.food = self.spawn_food()

        self.update_labels()
        self.draw()
        self.schedule_next_tick()

    def update_labels(self) -> None:
        """Refresh score and status text."""
        self.score_var.set(f"Score: {self.score}")
        if self.is_game_over:
            self.status_var.set("Game Over - Press R to Restart")
        else:
            self.status_var.set("Arrows/WASD to Move")

    def spawn_food(self) -> tuple[int, int]:
        """Create food on a free cell.

        Returns:
            A random empty grid position.
        """
        empty_cells = [
            (x, y)
            for y in range(GRID_HEIGHT)
            for x in range(GRID_WIDTH)
            if (x, y) not in self.snake
        ]
        return random.choice(empty_cells)

    def on_key_press(self, event: tk.Event) -> None:
        """Handle movement and restart keys.

        Args:
            event: Keyboard event object.
        """
        key = event.keysym.lower()

        if key == "r" and self.is_game_over:
            self.restart()
            return

        direction_map = {
            "up": (0, -1),
            "w": (0, -1),
            "down": (0, 1),
            "s": (0, 1),
            "left": (-1, 0),
            "a": (-1, 0),
            "right": (1, 0),
            "d": (1, 0),
        }

        if key not in direction_map or self.is_game_over:
            return

        new_direction = direction_map[key]
        if not self.is_opposite_direction(new_direction):
            self.pending_direction = new_direction

    def is_opposite_direction(self, new_direction: tuple[int, int]) -> bool:
        """Check whether the new direction reverses movement.

        Args:
            new_direction: Candidate direction vector.

        Returns:
            True if it directly opposes the current direction.
        """
        return (
            new_direction[0] == -self.direction[0]
            and new_direction[1] == -self.direction[1]
        )

    def schedule_next_tick(self) -> None:
        """Schedule the next game update."""
        self.after_id = self.root.after(self.speed_ms, self.tick)

    def tick(self) -> None:
        """Advance the game by one frame."""
        if self.is_game_over:
            return

        self.direction = self.pending_direction
        head_x, head_y = self.snake[0]
        delta_x, delta_y = self.direction
        new_head = (head_x + delta_x, head_y + delta_y)

        if self.has_collision(new_head):
            self.game_over()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.speed_ms = max(MIN_SPEED_MS, self.speed_ms - SPEED_STEP_MS)
            self.food = self.spawn_food()
        else:
            self.snake.pop()

        self.update_labels()
        self.draw()
        self.schedule_next_tick()

    def has_collision(self, position: tuple[int, int]) -> bool:
        """Check wall and self collisions.

        Args:
            position: Position to validate.

        Returns:
            True when the position collides with a wall or the snake body.
        """
        x, y = position
        hits_wall = x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT
        hits_body = position in self.snake
        return hits_wall or hits_body

    def game_over(self) -> None:
        """Stop the game and show the final state."""
        self.is_game_over = True
        self.after_id = None
        self.update_labels()
        self.draw()

    def draw(self) -> None:
        """Render the snake, food, and optional overlay."""
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_food()
        self.draw_snake()

        if self.is_game_over:
            self.draw_overlay()

    def draw_grid(self) -> None:
        """Render a subtle background grid."""
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            self.canvas.create_line(x, 0, x, WINDOW_HEIGHT, fill="#1c1c1c")
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            self.canvas.create_line(0, y, WINDOW_WIDTH, y, fill="#1c1c1c")

    def draw_food(self) -> None:
        """Draw the current food item."""
        x1, y1, x2, y2 = self.cell_to_pixels(self.food)
        self.canvas.create_oval(
            x1 + 3,
            y1 + 3,
            x2 - 3,
            y2 - 3,
            fill="#ff5c5c",
            outline="",
        )

    def draw_snake(self) -> None:
        """Draw the snake body and head."""
        for index, segment in enumerate(self.snake):
            x1, y1, x2, y2 = self.cell_to_pixels(segment)
            fill = "#7CFC00" if index == 0 else "#3cb043"
            self.canvas.create_rectangle(
                x1 + 1,
                y1 + 1,
                x2 - 1,
                y2 - 1,
                fill=fill,
                outline="",
            )

    def draw_overlay(self) -> None:
        """Render the game over message."""
        self.canvas.create_rectangle(
            40,
            WINDOW_HEIGHT // 2 - 50,
            WINDOW_WIDTH - 40,
            WINDOW_HEIGHT // 2 + 50,
            fill="#000000",
            outline="#ffffff",
        )
        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 - 12,
            text="Game Over",
            fill="#ffffff",
            font=("Consolas", 20, "bold"),
        )
        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 + 18,
            text="Press R to Restart",
            fill="#cccccc",
            font=("Consolas", 12),
        )

    def cell_to_pixels(self, cell: tuple[int, int]) -> tuple[int, int, int, int]:
        """Convert a grid cell to canvas pixel coordinates.

        Args:
            cell: Grid cell coordinate.

        Returns:
            Rectangle coordinates for the canvas.
        """
        x, y = cell
        return (
            x * CELL_SIZE,
            y * CELL_SIZE,
            (x + 1) * CELL_SIZE,
            (y + 1) * CELL_SIZE,
        )


def main() -> None:
    """Start the tkinter application."""
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
