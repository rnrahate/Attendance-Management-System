import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
import sqlite3
from PIL import Image, ImageTk
import os
import datetime
import face_recognition

# Define paths
IMAGE_FOLDER = 'images/'

# Ensure image folder exists
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Database setup
def create_database():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (id INTEGER PRIMARY KEY, name TEXT, date TEXT)''')
    conn.commit()
    conn.close()

# Save uploaded image
def save_image(image, name):
    file_path = os.path.join(IMAGE_FOLDER, f"{name}.jpg")
    cv2.imwrite(file_path, image)

# Register a face in the database by uploading image
def upload_image(name):
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
    if file_path:
        image = cv2.imread(file_path)
        save_image(image, name)
        messagebox.showinfo("Success", "Image uploaded successfully!")

# Capture and save image from camera
def capture_image(name):
    video_capture = cv2.VideoCapture(0)
    ret, frame = video_capture.read()
    if ret:
        save_image(frame, name)
        messagebox.showinfo("Success", "Image captured successfully!")
    video_capture.release()
    cv2.destroyAllWindows()

# Mark attendance based on face recognition
def mark_attendance():
    video_capture = cv2.VideoCapture(0)
    known_faces = []
    known_names = []
    
    # Load known faces
    for filename in os.listdir(IMAGE_FOLDER):
        if filename.endswith('.jpg'):
            name = os.path.splitext(filename)[0]
            image_path = os.path.join(IMAGE_FOLDER, filename)
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)[0]
            known_faces.append(encoding)
            known_names.append(name)
    
    while True:
        ret, frame = video_capture.read()
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_faces, face_encoding)
            face_distances = face_recognition.face_distance(known_faces, face_encoding)
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index]:
                name = known_names[best_match_index]
                today_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                messagebox.showinfo("Attendance", f"Attendance marked for {name}")
                conn = sqlite3.connect('attendance.db')
                c = conn.cursor()
                c.execute("INSERT INTO attendance (name, date) VALUES (?, ?)", (name, today_date))
                conn.commit()
                conn.close()

                video_capture.release()
                cv2.destroyAllWindows()
                return
        
        if not face_encodings:
            messagebox.showerror("Error", "No matching face found.")
            break

    video_capture.release()
    cv2.destroyAllWindows()

# Display monthly attendance
def view_attendance():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT name, date FROM attendance WHERE date LIKE ?", (f'%{datetime.datetime.now().strftime("%Y-%m")}%',))
    attendance_data = c.fetchall()
    conn.close()
    
    if attendance_data:
        attendance_info = "\n".join([f"{row[0]}: {row[1]}" for row in attendance_data])
        messagebox.showinfo("Attendance Records", attendance_info)
    else:
        messagebox.showinfo("Attendance Records", "No attendance records for this month.")

# Tkinter GUI setup
def main():
    create_database()
    
    window = tk.Tk()
    window.title("Face Recognition Attendance System")
    window.geometry("400x400")
    
    label = tk.Label(window, text="Attendance System", font=("Arial", 16, "bold"))
    label.pack(pady=20)
    
    upload_button = tk.Button(window, text="Upload Image", command=lambda: show_upload_options(), font=("Arial", 12))
    upload_button.pack(pady=10)
    
    mark_attendance_button = tk.Button(window, text="Mark Attendance", command=mark_attendance, font=("Arial", 12))
    mark_attendance_button.pack(pady=10)
    
    view_attendance_button = tk.Button(window, text="View Monthly Attendance", command=view_attendance, font=("Arial", 12))
    view_attendance_button.pack(pady=10)
    
    window.mainloop()

def show_upload_options():
    def on_upload():
        name = name_entry.get()
        if capture_var.get():
            capture_image(name)
        else:
            upload_image(name)
    
    upload_window = tk.Toplevel()
    upload_window.title("Upload Image")
    upload_window.geometry("400x200")
    
    tk.Label(upload_window, text="Enter Name", font=("Arial", 12)).pack(pady=5)
    name_entry = tk.Entry(upload_window, font=("Arial", 12))
    name_entry.pack(pady=5)
    
    tk.Label(upload_window, text="Choose upload method", font=("Arial", 12)).pack(pady=10)
    
    capture_var = tk.BooleanVar()
    tk.Radiobutton(upload_window, text="Capture Using Camera", variable=capture_var, value=True).pack()
    tk.Radiobutton(upload_window, text="Upload File", variable=capture_var, value=False).pack()
    
    upload_button = tk.Button(upload_window, text="Submit", command=on_upload, font=("Arial", 12))
    upload_button.pack(pady=10)

if __name__ == "__main__":
    main()
