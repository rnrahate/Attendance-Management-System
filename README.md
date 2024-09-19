# Face Recognition Attendance Management System

## Overview

The **Face Recognition Attendance Management System** is designed to allow users to upload their images and use face recognition to mark attendance. It provides an easy-to-use interface for uploading images or capturing them via a camera, and then compares the captured image during attendance marking with the stored data. If the face matches an existing entry, attendance is recorded for that person.

---

## Technologies Used

- **Python**: Core language for the system.
- **Tkinter**: Used for building the graphical user interface (GUI).
- **OpenCV**: Used for capturing images from the camera.
- **SQLite**: A lightweight database to store attendance records.
- **Face_Recognition Library**: Used for face detection and comparison.

---

## Features

- **Image Upload**: Users can either upload an image file or capture one via a camera.
- **Face Matching**: When marking attendance, the system captures an image from the camera and compares it with the stored images.
- **Automatic Attendance Recording**: If a match is found, attendance is marked in the database, and the user's name is displayed.
- **Monthly Attendance Records**: Users can view attendance records for the current month.

---

## System Flow

1. **Uploading Image**:
   - Users either upload an image file or capture their photo using the camera.
   - The uploaded or captured image is saved in a local directory and renamed with the user's name.
   
2. **Marking Attendance**:
   - The system captures a real-time image using the camera.
   - The captured image is compared with all the stored images using the `face_recognition` library.
   - If a match is found, the system marks attendance for the user and stores the information in the SQLite database, displaying a "Welcome" message with the user's name.
   
3. **Viewing Attendance**:
   - The user can view the attendance records for the current month.
   

## Example Screenshot

![alt text](<Screenshot 2024-09-19 143721.png>) ![alt text](<Screenshot 2024-09-19 143757.png>)

- ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
- ![Tkinter](https://img.shields.io/badge/Tkinter-007ACC?style=for-the-badge&logo=python&logoColor=white)
- ![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
- ![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)

---

## License

This project is open-source and available under the MIT License.

HAPPY CODING! 