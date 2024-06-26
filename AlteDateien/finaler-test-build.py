import tkinter as tk
from tkinter import ttk
import random
from pynput import keyboard
from pynput.keyboard import Key

#def on_key_release(key):
#    if key == Key.right:
#        print("Rechte Taste gedrückt")

#Rundenstart
print("Die Runde wird gestartet")

#Spielername
spielerName = input("Wie heißt du? ")
print("Willkommen", spielerName, "zu BUZZWORD")

#Einlesen der Buzzwords-Datei
print("Nenne den Namen der Datei:") #C:\Users\covrk\Documents\GitHub\BSRN-Gruppenaufgabe\Buzzwords-Datei.txt
roundfile = input()
roudnfileOpener = open(roundfile, 'r') #Variabeln umbenennen!


#TEST EINER GRID mit Tkinter:   
def generate_grid(rows, columns, buzzwords):
    #Erzeugung des Tkinter-Fensters
    root = tk.Tk()
    root.title("Buzzword Bingo")

    #Frame für das Raster
    grid_frame = tk.Frame(root) 
    grid_frame.pack()


#Erzeugung des Rasters
    for i in range(rows):
         for j in range(columns):
                label = tk.Label(grid_frame, text= random.choice(buzzwords), borderwidth=1, relief="solid", width=25, height=15)
                label.grid(row=i, column=j)
    root.mainloop()


def read_buzzword(roundfile):
    with open(roundfile, 'r') as f:
        lines = f.readlines()
        return lines
buzzwords = read_buzzword(roundfile)

def main():
    rows = int(input("Anzahl der Zeilen:"))
    columns = int(input("Anzahl der Spalten:"))
    generate_grid(rows, columns, buzzwords)


if __name__ == "__main__":
        main()

