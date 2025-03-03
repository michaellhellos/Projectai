import random
import tkinter as tk
from tkinter import messagebox
import math
import time

# Ukuran papan
BOARD_ROWS = 10
BOARD_COLS = 10
CELL_SIZE = 50

# Inisialisasi papan
papan = [[" " for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
macan_count = 0
selected_macan = None  # Untuk menyimpan posisi Macan yang dipilih
placing_macan = True  # Mode untuk menempatkan Macan
start_time = None
timer_label = None
wong_count = 0  # Jumlah Wong yang sudah ditempatkan

# Konstanta untuk Min-Max
MAX_DEPTH = 3  # Kedalaman rekursi untuk Min-Max

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
                start_timer()
        else:
            messagebox.showinfo("Info", "Posisi tidak valid atau sudah terisi. Silakan pilih posisi lain.")
    else:
        messagebox.showinfo("Info", "Anda sudah menempatkan 2 Macan.")

def place_wong():
    global wong_count
    while wong_count < 8:
        row = random.randint(0, BOARD_ROWS - 1)
        col = random.randint(0, BOARD_COLS - 1)
        if papan[row][col] == " ":
            papan[row][col] = "W"
            wong_count += 1
            break  # Hanya tambahkan satu Wong per giliran
    canvas.delete("all")
    draw_board(canvas)

def count_wong():
    return sum(row.count("W") for row in papan)

def can_eat_wong(start_row, start_col, end_row, end_col):
    # Periksa apakah Macan bisa melompati Wong dan memakannya
    # Gerakan horizontal
    if abs(start_row - end_row) == 2 and start_col == end_col:
        mid_row = (start_row + end_row) // 2
        if papan[mid_row][start_col] == "W" and papan[end_row][end_col] == " ":
            return True
    # Gerakan vertikal
    elif abs(start_col - end_col) == 2 and start_row == end_row:
        mid_col = (start_col + end_col) // 2
        if papan[start_row][mid_col] == "W" and papan[end_row][end_col] == " ":
            return True
    # Gerakan diagonal (seperti "X" atas-bawah)
    elif abs(start_row - end_row) == 2 and abs(start_col - end_col) == 2:
        mid_row = (start_row + end_row) // 2
        mid_col = (start_col + end_col) // 2
        if papan[mid_row][mid_col] == "W" and papan[end_row][end_col] == " ":
            return True
    return False

def move_macan(event):
    global selected_macan, wong_count
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
        if (abs(row - current_row) == 1 and abs(col - current_col) == 1) or \
           (row == current_row and abs(col - current_col) == 1) or \
           (col == current_col and abs(row - current_row) == 1):
            if papan[row][col] == " ":
                papan[current_row][current_col] = " "
                papan[row][col] = "M"
                selected_macan = None
                canvas.delete("all")
                draw_board(canvas)
                if is_macan_trapped():  # Cek apakah Macan dikepung
                    messagebox.showinfo("Info", "Macan dikepung! Wong menang.")
                    root.quit()
                else:
                    if wong_count < 8:
                        place_wong()  # Tambahkan satu Wong setelah Macan bergerak
                    move_wong()  # Panggil fungsi untuk memindahkan Wong setelah Macan bergerak
            else:
                messagebox.showinfo("Info", "Kotak tujuan sudah terisi. Silakan pilih kotak lain.")
        elif abs(row - current_row) == 2 or abs(col - current_col) == 2:
            if can_eat_wong(current_row, current_col, row, col):
                mid_row = (current_row + row) // 2
                mid_col = (current_col + col) // 2
                papan[current_row][current_col] = " "
                papan[mid_row][mid_col] = " "
                papan[row][col] = "M"
                selected_macan = None
                canvas.delete("all")
                draw_board(canvas)
                if count_wong() <= 2:
                    messagebox.showinfo("Info", "Macan menang! Wong hampir habis.")
                    root.quit()
                if wong_count < 8:
                    place_wong()  # Tambahkan satu Wong setelah Macan bergerak
                move_wong()  # Panggil fungsi untuk memindahkan Wong setelah Macan bergerak
            else:
                messagebox.showinfo("Info", "Tidak bisa memakan Wong.")
        else:
            messagebox.showinfo("Info", "Macan hanya bisa berpindah satu kotak atau melompati Wong.")

def is_macan_trapped():
    # Cek apakah Macan tidak bisa bergerak lagi
    for i in range(BOARD_ROWS):
        for j in range(BOARD_COLS):
            if papan[i][j] == "M":
                moves = get_possible_moves(i, j)
                if any(papan[row][col] == " " for (row, col) in moves):
                    return False  # Masih ada langkah yang bisa dilakukan
    return True  # Macan dikepung

def move_wong():
    best_move = find_best_move_wong()
    if best_move:
        (start_row, start_col), (end_row, end_col) = best_move
        papan[start_row][start_col] = " "
        papan[end_row][end_col] = "W"
        canvas.delete("all")
        draw_board(canvas)

def find_best_move_wong():
    _, best_move = min_max(MAX_DEPTH, True, -math.inf, math.inf)
    return best_move

def min_max(depth, is_maximizing, alpha, beta):
    if depth == 0 or count_wong() <= 2 or is_macan_trapped():  # Kondisi terminal
        return evaluate_board(), None

    if is_maximizing:
        best_value = -math.inf
        best_move = None
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
                            value, _ = min_max(depth - 1, False, alpha, beta)
                            papan[row][col] = " "
                            papan[i][j] = "W"

                            if value > best_value:
                                best_value = value
                                best_move = ((i, j), (row, col))
                            alpha = max(alpha, value)
                            if beta <= alpha:
                                break
        return best_value, best_move
    else:
        best_value = math.inf
        best_move = None
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
                            value, _ = min_max(depth - 1, True, alpha, beta)
                            papan[row][col] = " "
                            papan[i][j] = "M"

                            if value < best_value:
                                best_value = value
                                best_move = ((i, j), (row, col))
                            beta = min(beta, value)
                            if beta <= alpha:
                                break
        return best_value, best_move

def evaluate_board():
    # Fungsi evaluasi: Wong mencoba menjauh dari Macan dan mengepungnya
    wong_positions = [(i, j) for i in range(BOARD_ROWS) for j in range(BOARD_COLS) if papan[i][j] == "W"]
    macan_positions = [(i, j) for i in range(BOARD_ROWS) for j in range(BOARD_COLS) if papan[i][j] == "M"]

    total_distance = 0
    surround_score = 0

    for wong in wong_positions:
        for macan in macan_positions:
            total_distance += abs(wong[0] - macan[0]) + abs(wong[1] - macan[1])  # Jarak Manhattan

    # Hitung formasi pengepungan
    for macan in macan_positions:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = macan[0] + dr, macan[1] + dc
                if 0 <= nr < BOARD_ROWS and 0 <= nc < BOARD_COLS:
                    if papan[nr][nc] == "W":
                        surround_score += 1

    return total_distance + surround_score * 10  # Semakin besar jarak dan pengepungan, semakin baik untuk Wong

def get_possible_moves(row, col):
    moves = []
    # Gerakan horizontal, vertikal, dan diagonal
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue  # Skip posisi saat ini
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < BOARD_ROWS and 0 <= new_col < BOARD_COLS:
                moves.append((new_row, new_col))
    return moves

def start_timer():
    global start_time, timer_label
    start_time = time.time()
    timer_label = tk.Label(root, text="Time: 0", font=("Arial", 16))
    timer_label.pack()
    update_timer()

def update_timer():
    elapsed_time = int(time.time() - start_time)
    timer_label.config(text=f"Time: {elapsed_time}")
    if count_wong() > 2 and not is_macan_trapped():
        root.after(1000, update_timer)
    else:
        if is_macan_trapped():
            timer_label.config(text=f"Time: {elapsed_time} - Wong Menang! Macan dikepung.")
        else:
            timer_label.config(text=f"Time: {elapsed_time} - Macan Menang!")

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