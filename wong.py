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
selected_wong = None  # Untuk menyimpan posisi Wong yang dipilih
placing_wong = True  # Mode untuk menempatkan Wong
start_time = None
timer_label = None

# Konstanta untuk Min-Max
MAX_DEPTH = 4  # Kedalaman rekursi ditingkatkan

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

def place_wong(event):
    global placing_wong
    if placing_wong:
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS and papan[row][col] == " ":
            papan[row][col] = "W"
            canvas.delete("all")
            draw_board(canvas)
            if count_wong() == 8:  # Semua Wong sudah ditempatkan
                placing_wong = False
                place_macan()  # Tempatkan Macan setelah Wong selesai
                messagebox.showinfo("Info", "Wong telah ditempatkan. Sekarang giliran Wong untuk bergerak.")
                canvas.unbind("<Button-1>")  # Hapus binding untuk place_wong
                canvas.bind("<Button-1>", move_wong)  # Binding baru untuk move_wong
                start_timer()
        else:
            messagebox.showinfo("Info", "Posisi tidak valid atau sudah terisi. Silakan pilih posisi lain.")

def place_macan():
    # Tempatkan 2 Macan secara acak
    global macan_count
    macan_count = 0
    while macan_count < 2:
        row = random.randint(0, BOARD_ROWS - 1)
        col = random.randint(0, BOARD_COLS - 1)
        if papan[row][col] == " ":
            papan[row][col] = "M"
            macan_count += 1
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
            return (mid_row, start_col)  # Kembalikan posisi Wong yang dilompati
    # Gerakan vertikal
    elif abs(start_col - end_col) == 2 and start_row == end_row:
        mid_col = (start_col + end_col) // 2
        if papan[start_row][mid_col] == "W" and papan[end_row][end_col] == " ":
            return (start_row, mid_col)  # Kembalikan posisi Wong yang dilompati
    # Gerakan diagonal (seperti "X" atas-bawah)
    elif abs(start_row - end_row) == 2 and abs(start_col - end_col) == 2:
        mid_row = (start_row + end_row) // 2
        mid_col = (start_col + end_col) // 2
        if papan[mid_row][mid_col] == "W" and papan[end_row][end_col] == " ":
            return (mid_row, mid_col)  # Kembalikan posisi Wong yang dilompati
    return None  # Tidak ada Wong yang bisa dimakan

def move_wong(event):
    global selected_wong
    col = event.x // CELL_SIZE
    row = event.y // CELL_SIZE

    if selected_wong is None:
        # Pilih Wong yang akan dipindahkan
        if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS and papan[row][col] == "W":
            selected_wong = (row, col)
            messagebox.showinfo("Info", f"Wong dipilih di posisi ({row}, {col}). Pilih kotak tujuan.")
        else:
            messagebox.showinfo("Info", "Silakan pilih Wong yang valid.")
    else:
        # Pindahkan Wong ke kotak tujuan
        current_row, current_col = selected_wong
        if (abs(row - current_row) == 1 and abs(col - current_col) == 1) or \
           (row == current_row and abs(col - current_col) == 1) or \
           (col == current_col and abs(row - current_row) == 1):
            if papan[row][col] == " ":
                papan[current_row][current_col] = " "
                papan[row][col] = "W"
                selected_wong = None
                canvas.delete("all")
                draw_board(canvas)
                if is_macan_trapped():  # Cek apakah Macan dikepung
                    messagebox.showinfo("Info", "Wong menang! Macan dikepung.")
                    root.quit()
                else:
                    move_macan_bot()  # Panggil fungsi untuk memindahkan Macan setelah Wong bergerak
            else:
                messagebox.showinfo("Info", "Kotak tujuan sudah terisi. Silakan pilih kotak lain.")
        else:
            messagebox.showinfo("Info", "Wong hanya bisa berpindah satu kotak.")

def is_macan_trapped():
    # Cek apakah Macan tidak bisa bergerak lagi
    for i in range(BOARD_ROWS):
        for j in range(BOARD_COLS):
            if papan[i][j] == "M":
                moves = get_possible_moves(i, j)
                if any(papan[row][col] == " " for (row, col) in moves):
                    return False  # Masih ada langkah yang bisa dilakukan
    return True  # Macan dikepung

def move_macan_bot():
    best_move = find_best_move_macan()
    if best_move:
        (start_row, start_col), (end_row, end_col) = best_move
        # Cek apakah Macan bisa memakan Wong
        eaten_wong = can_eat_wong(start_row, start_col, end_row, end_col)
        if eaten_wong:
            # Hapus Wong yang dilompati
            wong_row, wong_col = eaten_wong
            papan[wong_row][wong_col] = " "
        # Pindahkan Macan
        papan[start_row][start_col] = " "
        papan[end_row][end_col] = "M"
        canvas.delete("all")
        draw_board(canvas)
        if count_wong() <= 2:
            messagebox.showinfo("Info", "Macan menang! Wong hampir habis.")
            root.quit()

def find_best_move_macan():
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
                if papan[i][j] == "M":
                    moves = get_possible_moves(i, j)
                    for move in moves:
                        row, col = move
                        if papan[row][col] == " ":
                            # Simulasikan langkah
                            papan[i][j] = " "
                            papan[row][col] = "M"
                            # Cek apakah Macan bisa memakan Wong
                            eaten_wong = can_eat_wong(i, j, row, col)
                            if eaten_wong:
                                wong_row, wong_col = eaten_wong
                                papan[wong_row][wong_col] = " "  # Hapus Wong yang dilompati
                            value, _ = min_max(depth - 1, False, alpha, beta)
                            # Kembalikan papan ke keadaan semula
                            papan[row][col] = " "
                            papan[i][j] = "M"
                            if eaten_wong:
                                papan[wong_row][wong_col] = "W"  # Kembalikan Wong yang dihapus

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
                if papan[i][j] == "W":
                    moves = get_possible_moves(i, j)
                    for move in moves:
                        row, col = move
                        if papan[row][col] == " ":
                            # Simulasikan langkah
                            papan[i][j] = " "
                            papan[row][col] = "W"
                            value, _ = min_max(depth - 1, True, alpha, beta)
                            papan[row][col] = " "
                            papan[i][j] = "W"

                            if value < best_value:
                                best_value = value
                                best_move = ((i, j), (row, col))
                            beta = min(beta, value)
                            if beta <= alpha:
                                break
        return best_value, best_move

def evaluate_board():
    # Fungsi evaluasi: Macan mencoba memakan Wong dan menghindari pengepungan
    wong_positions = [(i, j) for i in range(BOARD_ROWS) for j in range(BOARD_COLS) if papan[i][j] == "W"]
    macan_positions = [(i, j) for i in range(BOARD_ROWS) for j in range(BOARD_COLS) if papan[i][j] == "M"]

    total_distance = 0
    for macan in macan_positions:
        for wong in wong_positions:
            total_distance += abs(macan[0] - wong[0]) + abs(macan[1] - wong[1])  # Jarak Manhattan

    # Bonus untuk posisi yang memungkinkan makan Wong dalam jumlah genap
    eat_score = 0
    for macan in macan_positions:
        for move in get_possible_moves(macan[0], macan[1]):
            if can_eat_wong(macan[0], macan[1], move[0], move[1]):
                # Cek apakah jumlah Wong yang bisa dimakan adalah genap
                if count_wong() % 2 == 0:
                    eat_score += 10

    return -total_distance + eat_score  # Semakin kecil jarak dan semakin banyak kesempatan makan, semakin baik untuk Macan

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

# Mengikat event klik mouse ke fungsi place_wong
canvas.bind("<Button-1>", place_wong)  # Klik kiri untuk menempatkan Wong

# Menampilkan papan awal
draw_board(canvas)

# Menjalankan aplikasi
root.mainloop()