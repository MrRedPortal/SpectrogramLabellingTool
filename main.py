import tkinter as tk
from tkinter import filedialog

import librosa
import librosa.display
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
from matplotlib.widgets import RectangleSelector

# Create a DataFrame to store the labeled data
data = {'Time Start': [], 'Time End': [], 'Frequency Start': [], 'Frequency End': [], 'Label': []}
df = pd.DataFrame(data)

# Load your audio file and create the spectrogram
audio_file = "16.wav"
y, sr = librosa.load(audio_file)
spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)

# Create a Tkinter window
root = tk.Tk()
root.title("Spectrogram Labeling Tool")

# Create a Figure and a canvas for the spectrogram
fig = plt.figure(figsize=(10, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack()

# Create a subplot for the spectrogram
ax_spectrogram = fig.add_subplot(111)

# Create a label to display the mouse coordinates
coord_label = tk.Label(root, text="")
coord_label.pack()

# Display the spectrogram on the subplot
librosa.display.specshow(librosa.power_to_db(spectrogram, ref=np.max), y_axis='mel', x_axis='time', ax=ax_spectrogram)


# Function to update the rectangle coordinates and label data
def on_select(eclick, erelease):
    ax = plt.gca()

    # Transform mouse coordinates to spectrogram data coordinates
    x_start, y_start = ax.transData.inverted().transform((eclick.x, eclick.y))
    x_end, y_end = ax.transData.inverted().transform((erelease.x, erelease.y))

    # Update the input fields
    time_start_entry.delete(0, 'end')
    time_start_entry.insert(0, f"{x_start:.3f}")
    time_end_entry.delete(0, 'end')
    time_end_entry.insert(0, f"{x_end:.3f}")
    freq_start_entry.delete('end')
    freq_start_entry.insert(0, f"{y_start:.3f}")
    freq_end_entry.delete(0, 'end')
    freq_end_entry.insert(0, f"{y_end:.3f}")

    # Get the name for the square
    label = label_entry.get()

    rect = Rectangle((x_start, y_start), x_end - x_start, y_end - y_start, fill=False, edgecolor='red', linewidth=2,
                     label=label)
    ax.add_patch(rect)
    canvas.draw()

    # Add the rectangle coordinates and label to the DataFrame
    df.loc[len(df)] = [x_start, x_end, y_start, y_end, label]

    # Clear the input fields
    label_entry.delete(0, 'end')


# Bind the on_select function to the RectangleSelector
RS = RectangleSelector(ax=ax_spectrogram, onselect=on_select, useblit=True, button=[1], spancoords='data')


# Function to display the spectrogram and previously drawn rectangles
def display_spectrogram():
    plt.clf()
    librosa.display.specshow(librosa.power_to_db(spectrogram, ref=np.max), y_axis='mel', x_axis='time')
    plt.colorbar(format='%+2.0f dB')

    for index, row in df.iterrows():
        x_start, x_end, y_start, y_end, label = row
        rect = Rectangle((x_start, y_start), x_end - x_start, y_end - y_start, fill=False, edgecolor='red', linewidth=2,
                         label=label)
        ax_spectrogram.add_patch(rect)

    ax_spectrogram.legend()
    canvas.draw()


# Function to update the coordinate label
def update_coords(event):
    x, y = event.xdata, event.ydata
    if x is not None and y is not None:
        coord_label.config(text=f"Time: {x:.2f}, Hz: {y:.2f}")
    else:
        coord_label.config(text="")


# Function to save the DataFrame to a CSV file
def save_to_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])

    if file_path:
        df.to_csv(file_path, index=False)
        print(f"Data saved to {file_path}")


# Function to edit a saved rectangle
def edit_rectangle():
    try:
        # Get the selected index from the listbox
        selected_index = saved_rectangles_listbox.curselection()[0]

        # Get the values from the DataFrame
        x_start, x_end, y_start, y_end, label = df.loc[selected_index]

        # Update the input fields
        time_start_entry.delete(0, 'end')
        time_start_entry.insert(0, f"{x_start:.3f}")
        time_end_entry.delete(0, 'end')
        time_end_entry.insert(0, f"{x_end:.3f}")
        freq_start_entry.delete('end')
        freq_start_entry.insert(0, f"{y_start:.3f}")
        freq_end_entry.delete(0, 'end')
        freq_end_entry.insert(0, f"{y_end:.3f}")
        label_entry.delete(0, 'end')
        label_entry.insert(0, label)

        # Remove the selected item from the DataFrame
        df.drop(selected_index, inplace=True)

        # Clear the input fields
        clear_input_fields()

        # Clear the listbox and redraw it
        saved_rectangles_listbox.delete(0, tk.END)
        for index, row in df.iterrows():
            saved_rectangles_listbox.insert(tk.END, f"Label: {row['Label']}")

        # Redraw the spectrogram
        display_spectrogram()

    except IndexError:
        pass


# Create a listbox to show saved rectangles
saved_rectangles_listbox = tk.Listbox(root)
saved_rectangles_listbox.pack()

# Button to edit a saved rectangle
edit_button = tk.Button(root, text="Edit Selected", command=edit_rectangle)
edit_button.pack()

# Create input fields for time start and stop
time_start_label = tk.Label(root, text="Time Start:")
time_start_label.pack()
time_start_entry = tk.Entry(root)
time_start_entry.pack()

time_end_label = tk.Label(root, text="Time End:")
time_end_label.pack()
time_end_entry = tk.Entry(root)
time_end_entry.pack()

# Create input fields for frequency start and stop
freq_start_label = tk.Label(root, text="Frequency Start:")
freq_start_label.pack()
freq_start_entry = tk.Entry(root)
freq_start_entry.pack()

freq_end_label = tk.Label(root, text="Frequency End:")
freq_end_label.pack()
freq_end_entry = tk.Entry(root)
freq_end_entry.pack()

# Create an input field for square label
label_label = tk.Label(root, text="Label:")
label_label.pack()
label_entry = tk.Entry(root)
label_entry.pack()

# Button to add labels
add_button = tk.Button(root, text="Add Coords", command=RS.set_active(True))
add_button.pack()

# Button to save the labeled data to a CSV file
save_button = tk.Button(root, text="Save to CSV", command=save_to_csv)
save_button.pack()


# Function to save data to a CSV file when the window is closed
def on_closing():
    save_to_csv()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)


# Function to clear the input fields
def clear_input_fields():
    time_start_entry.delete(0, 'end')
    time_end_entry.delete(0, 'end')
    freq_start_entry.delete(0, 'end')
    freq_end_entry.delete(0, 'end')
    label_entry.delete(0, 'end')


# Bind the update_coords function to the mouse motion event on the Figure
fig.canvas.mpl_connect('motion_notify_event', update_coords)

display_spectrogram()

root.mainloop()
