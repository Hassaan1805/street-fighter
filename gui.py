import tkinter as tk
from tkinter import messagebox, simpledialog
import subprocess
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

class GameGUI:
    def __init__(self, master):
        self.master = master
        master.title("Street Fighter Game")
        master.geometry("720x560")  # Set the window size to 700x300

        self.label = tk.Label(master, text="Enter Player Names", font=("Arial", 24))
        self.label.pack(pady=20)

        self.player1_name = tk.StringVar()
        self.player2_name = tk.StringVar()

        self.player1_entry = tk.Entry(master, textvariable=self.player1_name, font=("Arial", 18))
        self.player1_entry.pack(pady=10)

        self.player2_entry = tk.Entry(master, textvariable=self.player2_name, font=("Arial", 18))
        self.player2_entry.pack(pady=10)

        self.start_button = tk.Button(master, text="Start Game", command=self.start_game, font=("Arial", 18))
        self.start_button.pack(pady=20)

        self.new_player_button = tk.Button(master, text="New Player", command=self.add_new_player, font=("Arial", 18))
        self.new_player_button.pack(pady=10)

        self.analyze_button = tk.Button(master, text="Analyze", command=self.analyze_game, font=("Arial", 18))
        self.analyze_button.pack(pady=10)

        self.exit_button = tk.Button(master, text="Exit", command=master.quit, font=("Arial", 18))
        self.exit_button.pack(pady=10)

    def start_game(self):
        player1 = self.player1_name.get()
        player2 = self.player2_name.get()

        if player1 and player2:
            # Connect to MySQL database
            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="tiger"
                )
                cursor = conn.cursor()

                # Create database if it doesn't exist
                cursor.execute("CREATE DATABASE IF NOT EXISTS game")
                cursor.execute("USE game")

                # Check if players already exist
                cursor.execute("SELECT * FROM players WHERE player1 = %s OR player2 = %s", (player1, player1))
                player1_exists = cursor.fetchone()
                cursor.execute("SELECT * FROM players WHERE player1 = %s OR player2 = %s", (player2, player2))
                player2_exists = cursor.fetchone()

                if player1_exists and player2_exists:
                    messagebox.showinfo("Info", "Players already exist. Starting the game.")
                    self.master.destroy()  # Close the GUI window
                    subprocess.run(["python", "main.py", player1, player2])  # Run the main.py script with player names
                    self.master.deiconify()  # Show the GUI window again after the game ends
                else:
                    messagebox.showinfo("Info", "Players do not exist. Please add new players.")
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}")
                return
        else:
            messagebox.showwarning("Input Error", "Please enter names for both players.")

    def add_new_player(self):
        new_player1 = simpledialog.askstring("New Player", "Enter name for Player 1:")
        new_player2 = simpledialog.askstring("New Player", "Enter name for Player 2:")

        if new_player1 and new_player2:
            # Connect to MySQL database
            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="tiger"
                )
                cursor = conn.cursor()

                # Create database if it doesn't exist
                cursor.execute("CREATE DATABASE IF NOT EXISTS game")
                cursor.execute("USE game")

                # Create table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS players (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        player1 VARCHAR(255) NOT NULL,
                        player2 VARCHAR(255) NOT NULL,
                        player1_wins INT DEFAULT 0,
                        player1_losses INT DEFAULT 0,
                        player2_wins INT DEFAULT 0,
                        player2_losses INT DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Insert new player names into the table
                cursor.execute("INSERT INTO players (player1, player2) VALUES (%s, %s)", (new_player1, new_player2))
                conn.commit()

                cursor.close()
                conn.close()

                messagebox.showinfo("Info", "New players added successfully.")
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}")
                return
        else:
            messagebox.showwarning("Input Error", "Please enter names for both players.")

    def analyze_game(self):
        player_name = simpledialog.askstring("Analyze", "Enter player name for analysis:")
        if not player_name:
            messagebox.showwarning("Input Error", "Please enter a player name.")
            return

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="tiger",
                database="game"
            )
            query = """
                SELECT player1, player2, player1_wins, player1_losses, player2_wins, player2_losses 
                FROM players 
                WHERE player1 = %s OR player2 = %s
            """
            df = pd.read_sql(query, conn, params=(player_name, player_name))
            conn.close()

            if df.empty:
                messagebox.showinfo("No Data", "No game data available for the given player.")
                return

            df['wins'] = df.apply(lambda row: row['player1_wins'] if row['player1'] == player_name else row['player2_wins'], axis=1)
            df['losses'] = df.apply(lambda row: row['player1_losses'] if row['player1'] == player_name else row['player2_losses'], axis=1)

            df.plot(kind='bar', x='player1', y=['wins', 'losses'], title=f"{player_name} Analysis")
            plt.show()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

if __name__ == "__main__":
    root = tk.Tk()
    gui = GameGUI(root)
    root.mainloop()