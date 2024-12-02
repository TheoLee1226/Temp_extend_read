import csv
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog, Button, Label, Listbox, MULTIPLE, Scrollbar, VERTICAL, END, Entry
import tkinter as tk

def read_csv(filename):
    data = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)  # 讀取標題行
        for row in reader:
            data.append([float(value) for value in row])
    return headers, data

def plot_data(headers, data, selected_columns):
    plt.figure(figsize=(10, 6))
    
    time_data = [row[0] for row in data]
    for col in selected_columns:
        col_data = [row[col] for row in data]
        plt.plot(time_data, col_data, label=headers[col])
    
    plt.xlabel('Time (s)')
    plt.ylabel('Value')
    plt.legend()
    plt.title('Selected Data')
    plt.show()

def save_selected_data(headers, data, selected_columns, filename):
    selected_headers = ["Time"] + [ headers[col] for col in selected_columns]
    selected_data = [[row[0]] + [row[col] for col in selected_columns] for row in data]
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(selected_headers)
        writer.writerows(selected_data)

    print(f"數據已保存到 {filename}")

def select_file_and_plot():
    filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if filename:
        headers, data = read_csv(filename)
        show_column_selection(headers, data)

def show_column_selection(headers, data):
    selection_window = tk.Toplevel()
    selection_window.title("Select Columns")
    selection_window.geometry("300x400")

    label = Label(selection_window, text="選擇要繪製的列")
    label.pack(pady=10)

    scrollbar = Scrollbar(selection_window, orient=VERTICAL)
    listbox = Listbox(selection_window, selectmode=MULTIPLE, yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side="right", fill="y")
    listbox.pack(pady=10, padx=10, fill="both", expand=True)
   
    for i, header in enumerate(headers):
        if header == "Time":
            continue
        listbox.insert(END, header)

    def on_plot():
        selected_indices = listbox.curselection()
        selected_columns = [int(index) + 1 for index in selected_indices]
        plot_data(headers, data, selected_columns)

    def on_save():
        selected_indices = listbox.curselection()
        selected_columns = [int(index) + 1 for index in selected_indices]
        save_filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if save_filename:
            save_selected_data(headers, data, selected_columns, save_filename)

    def select_all():
        listbox.select_set(0, END)
    
    def deselect_all():
        listbox.select_clear(0, END)

    select_all_button = Button(selection_window, text="全選", command=select_all)
    select_all_button.pack(pady=5)

    deselect_all_button = Button(selection_window, text="全不選", command=deselect_all)
    deselect_all_button.pack(pady=5)

    plot_button = Button(selection_window, text="繪製圖表", command=on_plot)
    plot_button.pack(pady=5)

    save_button = Button(selection_window, text="匯出選擇的數據", command=on_save)
    save_button.pack(pady=5)

    selection_window.mainloop()

root = Tk()
root.title("CSV Plotter")
root.geometry("300x200") 

label = Label(root, text="選擇CSV檔案並繪製圖表")
label.pack(pady=10)

button = Button(root, text="選擇檔案", command=select_file_and_plot)
button.pack(pady=10)

label.place(relx=0.5, rely=0.4, anchor='center')
button.place(relx=0.5, rely=0.6, anchor='center')

root.mainloop()