import tkinter as tk
from tkinter import messagebox
import subprocess
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

class AnalysisGUI:
    def __init__(self, master):
        self.master = master
        master.title("Game Analysis")
        master.geometry("400x200")

        self.label = tk.Label(master, text="Enter Player Name for Analysis", font=("Arial", 14))
        self.label.pack(pady=10)

        self.player_name = tk.StringVar()
        self.player_entry = tk.Entry(master, textvariable=self.player_name, font=("Arial", 14))
        self.player_entry.pack(pady=10)

        self.analyze_button = tk.Button(master, text="Analyze", command=self.analyze_game, font=("Arial", 14))
        self.analyze_button.pack(pady=10)

        self.restart_button = tk.Button(master, text="Restart", command=self.restart_game, font=("Arial", 14))
        self.restart_button.pack(pady=10)

        self.exit_button = tk.Button(master, text="Exit", command=master.quit, font=("Arial", 14))
        self.exit_button.pack(pady=10)

    def restart_game(self):
        self.master.destroy()
        subprocess.run(["python", "gui.py"])

    def analyze_game(self):
        player_name = self.player_name.get()
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
    gui = AnalysisGUI(root)
    root.mainloop()