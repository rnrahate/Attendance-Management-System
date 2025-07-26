import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import numpy as np
import sqlite3
from PIL import Image, ImageTk
import os
import datetime
import json
import base64
import face_recognition

# Define paths
IMAGE_FOLDER = 'images/'
DATA_FOLDER = 'student_data/'
DB_FILE = 'attendance.db'
os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

# Database setup
def create_database():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT,
                    student_name TEXT,
                    timestamp TEXT)''')
    conn.commit()
    conn.close()

# Save student image and encoding in JSON
def save_student_data(student_id, student_name, frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb_frame)
    if not encodings:
        messagebox.showerror("Error", "No face detected. Please try again.")
        return False

    _, buffer = cv2.imencode('.jpg', frame)
    image_base64 = base64.b64encode(buffer).decode('utf-8')

    student_data = {
        "student_id": student_id,
        "student_name": student_name,
        "image": image_base64,
        "encoding": encodings[0].tolist()
    }

    with open(os.path.join(DATA_FOLDER, f"{student_name}.json"), 'w') as f:
        json.dump(student_data, f, indent=4)

    return True

# Mark attendance if match found
def mark_attendance():
    # Load all encodings
    encodings_list = []
    names = []
    ids = []

    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".json"):
            with open(os.path.join(DATA_FOLDER, filename), 'r') as f:
                data = json.load(f)
                enc = np.array(data["encoding"])
                encodings_list.append(enc)
                names.append(data["student_name"])
                ids.append(data["student_id"])

    if not encodings_list:
        messagebox.showerror("Error", "No registered users found.")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Cannot access webcam.")
        return

    messagebox.showinfo("Instructions", "Camera will capture your face in 3 seconds.")
    cv2.waitKey(3000)

    ret, frame = cap.read()
    cap.release()

    if not ret:
        messagebox.showerror("Error", "Failed to capture image.")
        return

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(encodings_list, face_encoding)
        face_distances = face_recognition.face_distance(encodings_list, face_encoding)
        best_match_index = np.argmin(face_distances)

        if matches[best_match_index]:
            student_name = names[best_match_index]
            student_id = ids[best_match_index]

            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO attendance (student_id, student_name, timestamp) VALUES (?, ?, ?)",
                      (student_id, student_name, now))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Attendance marked for {student_name}.")
            return

    messagebox.showwarning("Not Found", "Face not recognized!")

# View attendance records for the current month in tabular format
def view_attendance():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    current_month = datetime.datetime.now().strftime("%Y-%m")
    c.execute("SELECT student_id, student_name, timestamp FROM attendance WHERE timestamp LIKE ?", (f"{current_month}%",))
    records = c.fetchall()
    conn.close()

    if not records:
        messagebox.showinfo("Monthly Attendance", "No attendance records found.")
        return

    table_window = tk.Toplevel()
    table_window.title("Monthly Attendance Records")
    table_window.geometry("600x400")

    tree = ttk.Treeview(table_window, columns=("ID", "Name", "Timestamp"), show='headings')
    tree.heading("ID", text="Student ID")
    tree.heading("Name", text="Student Name")
    tree.heading("Timestamp", text="Timestamp")

    for row in records:
        tree.insert("", "end", values=row)

    tree.pack(fill=tk.BOTH, expand=True)

# GUI Setup
def main():
    create_database()
    root = tk.Tk()
    root.title("Face Recognition Attendance System")
    root.geometry("400x350")

    tk.Label(root, text="Attendance System", font=("Arial", 16, "bold")).pack(pady=20)

    def on_register():
        def capture():
            name = name_entry.get().strip()
            sid = id_entry.get().strip()
            if not name or not sid:
                messagebox.showerror("Error", "Please fill all fields.")
                return

            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                messagebox.showerror("Error", "Cannot access webcam.")
                return

            while True:
                ret, frame = cap.read()
                if not ret:
                    messagebox.showerror("Error", "Failed to read from webcam.")
                    break

                cv2.putText(frame, "Press C to capture, Q to quit", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.imshow("Register", frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('c'):
                    if save_student_data(sid, name, frame):
                        messagebox.showinfo("Saved", "Student registered successfully.")
                        cap.release()
                        cv2.destroyAllWindows()
                        return
                elif key == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()

        reg_window = tk.Toplevel(root)
        reg_window.title("Register Student")
        reg_window.geometry("300x200")

        tk.Label(reg_window, text="Name").pack(pady=5)
        name_entry = tk.Entry(reg_window)
        name_entry.pack(pady=5)

        tk.Label(reg_window, text="Student ID").pack(pady=5)
        id_entry = tk.Entry(reg_window)
        id_entry.pack(pady=5)

        tk.Button(reg_window, text="Capture & Register", command=capture).pack(pady=10)

    tk.Button(root, text="Register Student", command=on_register, font=("Arial", 12)).pack(pady=10)
    tk.Button(root, text="Mark Attendance", command=mark_attendance, font=("Arial", 12)).pack(pady=10)
    tk.Button(root, text="View Monthly Attendance", command=view_attendance, font=("Arial", 12)).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
# This code implements a face recognition attendance system using OpenCV, face_recognition, and Tkinter.
# It allows users to register students, capture their images, and mark attendance based on face recognition