import random
import tkinter as tk
from tkinter import messagebox
import math

# Ukuran papan
BOARD_ROWS = 10
BOARD_COLS = 10
CELL_SIZE = 50

# Inisialisasi papan
papan = [[" " for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
macan_count = 0
selected_macan = None  # Untuk menyimpan posisi Macan yang dipilih
placing_macan = True  # Mode untuk menempatkan Macan

def draw_board(canvas):
    for i in range(BOARD_ROWS):
        for j in range(BOARD_COLS):
            x0, y0 = j * CELL_SIZE, i * CELL_SIZE
            x1, y1 = x0 + CELL_SIZE, y0 + CELL_SIZE
            canvas.create_rectangle(x0, y0, x1, y1, fill="white", outline="black")
            if papan[i][j] == "M":
                canvas.create_text(x0 + CELL_SIZE // 2, y0 + CELL_SIZE // 2, text="M", font=("Arial", 24), fill="red")
            elif papan[i][j] == "W":
                canvas.create_text(x0 + CELL_SIZE // 2, y0 + CELL_SIZE // 2, text="W", font=("Arial", 24), fill="blue")

def place_macan(event):
    global macan_count, placing_macan
    if placing_macan and macan_count < 2:
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS and papan[row][col] == " ":
            papan[row][col] = "M"
            macan_count += 1
            canvas.delete("all")
            draw_board(canvas)
            if macan_count == 2:
                placing_macan = False  # Selesai menempatkan Macan
                place_wong()  # Tempatkan Wong setelah Macan selesai
                messagebox.showinfo("Info", "Macan telah ditempatkan. Sekarang giliran Macan untuk bergerak.")
                canvas.unbind("<Button-1>")  # Hapus binding untuk place_macan
                canvas.bind("<Button-1>", move_macan)  # Binding baru untuk move_macan
        else:
            messagebox.showinfo("Info", "Posisi tidak valid atau sudah terisi. Silakan pilih posisi lain.")
    else:
        messagebox.showinfo("Info", "Anda sudah menempatkan 2 Macan.")

def place_wong():
    wong_count = 0
    while wong_count < 8:
        row = random.randint(0, BOARD_ROWS - 1)
        col = random.randint(0, BOARD_COLS - 1)
        if papan[row][col] == " ":
            papan[row][col] = "W"
            wong_count += 1
    canvas.delete("all")
    draw_board(canvas)

def move_macan(event):
    global selected_macan
    col = event.x // CELL_SIZE
    row = event.y // CELL_SIZE

    if selected_macan is None:
        # Pilih Macan yang akan dipindahkan
        if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS and papan[row][col] == "M":
            selected_macan = (row, col)
            messagebox.showinfo("Info", f"Macan dipilih di posisi ({row}, {col}). Pilih kotak tujuan.")
        else:
            messagebox.showinfo("Info", "Silakan pilih Macan yang valid.")
    else:
        # Pindahkan Macan ke kotak tujuan
        current_row, current_col = selected_macan
        if (row == current_row and abs(col - current_col) == 1) or (col == current_col and abs(row - current_row) == 1):
            if papan[row][col] == " ":
                papan[current_row][current_col] = " "
                papan[row][col] = "M"
                selected_macan = None
                canvas.delete("all")
                draw_board(canvas)
                move_wong()  # Panggil fungsi untuk memindahkan Wong setelah Macan bergerak
            else:
                messagebox.showinfo("Info", "Kotak tujuan sudah terisi. Silakan pilih kotak lain.")
        else:
            messagebox.showinfo("Info", "Macan hanya bisa berpindah satu kotak ke atas, bawah, kiri, atau kanan.")

def move_wong():
    best_move = find_best_move_wong()
    if best_move:
        (start_row, start_col), (end_row, end_col) = best_move
        papan[start_row][start_col] = " "
        papan[end_row][end_col] = "W"
        canvas.delete("all")
        draw_board(canvas)

def find_best_move_wong():
    best_move = None
    best_value = -math.inf

    for i in range(BOARD_ROWS):
        for j in range(BOARD_COLS):
            if papan[i][j] == "W":
                moves = get_possible_moves(i, j)
                for move in moves:
                    row, col = move
                    if papan[row][col] == " ":
                        # Simulasikan langkah
                        papan[i][j] = " "
                        papan[row][col] = "W"
                        move_value = min_max(MAX_DEPTH, False)
                        papan[row][col] = " "
                        papan[i][j] = "W"

                        if move_value > best_value:
                            best_value = move_value
                            best_move = ((i, j), (row, col))

    return best_move

def min_max(depth, is_maximizing):
    if depth == 0:
        return evaluate_board()

    if is_maximizing:
        best_value = -math.inf
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                if papan[i][j] == "W":
                    moves = get_possible_moves(i, j)
                    for move in moves:
                        row, col = move
                        if papan[row][col] == " ":
                            # Simulasikan langkah
                            papan[i][j] = " "
                            papan[row][col] = "W"
                            value = min_max(depth - 1, False)
                            papan[row][col] = " "
                            papan[i][j] = "W"
                            best_value = max(best_value, value)
        return best_value
    else:
        best_value = math.inf
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                if papan[i][j] == "M":
                    moves = get_possible_moves(i, j)
                    for move in moves:
                        row, col = move
                        if papan[row][col] == " ":
                            # Simulasikan langkah
                            papan[i][j] = " "
                            papan[row][col] = "M"
                            value = min_max(depth - 1, True)
                            papan[row][col] = " "
                            papan[i][j] = "M"
                            best_value = min(best_value, value)
        return best_value

def evaluate_board():
    # Fungsi evaluasi sederhana: jumlah Wong - jumlah Macan
    wong_count = sum(row.count("W") for row in papan)
    macan_count = sum(row.count("M") for row in papan)
    return wong_count - macan_count

def get_possible_moves(row, col):
    moves = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < BOARD_ROWS and 0 <= new_col < BOARD_COLS:
            moves.append((new_row, new_col))
    return moves

# Membuat window Tkinter
root = tk.Tk()
root.title("Game Macanan Jogja")

# Membuat canvas untuk menggambar papan
canvas = tk.Canvas(root, width=BOARD_COLS * CELL_SIZE, height=BOARD_ROWS * CELL_SIZE)
canvas.pack()

# Mengikat event klik mouse ke fungsi place_macan
canvas.bind("<Button-1>", place_macan)  # Klik kiri untuk menempatkan Macan

# Menampilkan papan awal
draw_board(canvas)

# Menjalankan aplikasi
root.mainloop()