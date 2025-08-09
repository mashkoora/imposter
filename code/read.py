import cv2
import serial
import time
import face_recognition
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(SCRIPT_DIR)

KNOWN_FACES_DIR = 'faces'
known_face_encodings = []
known_face_names = []

# Load Mashkoor's face image
print("Loading known face: mashkoor.jpg")
image_path = os.path.join(KNOWN_FACES_DIR, 'mashkoor.jpg')

try:
    image = face_recognition.load_image_file(image_path)
    face_encodings_in_image = face_recognition.face_encodings(image)
    if face_encodings_in_image:
        known_face_encodings.append(face_encodings_in_image[0])
        known_face_names.append("Mashkoor")
        print("Loaded Mashkoor's face successfully!")
    else:
        print(f"Error: No face found in {image_path}. Please use a clear image.")
        exit()
except FileNotFoundError:
    print(f"Error: The file '{image_path}' was not found.")
    exit()

try:
    arduino = serial.Serial('COM11', 9600)
    time.sleep(2)
    print("Serial connection established.")
except serial.SerialException as e:
    print(f"Error: Could not open serial port 'COM11'.")
    print(e)
    exit()

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0)

mashkoor_start_time = None
MASHKOOR_TRIGGER_TIME = 5  # seconds

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    height, width = frame.shape[:2]

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    extra_servo_trigger = 0
    faces_found = False

    if len(faces) > 0:
        faces_found = True
        (x, y, w, h) = faces[0]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        face_locations = face_recognition.face_locations(frame)
        if face_locations:
            face_encoding = face_recognition.face_encodings(frame, face_locations)[0]
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                name = "Mashkoor"
                # Start or continue timer for Mashkoor
                if mashkoor_start_time is None:
                    mashkoor_start_time = time.time()
                elif time.time() - mashkoor_start_time >= MASHKOOR_TRIGGER_TIME:
                    extra_servo_trigger = 1

                # Track Mashkoor's face position
                cx = x + w // 2
                cy = y + h // 2
                raw_x = (cx / width) * 180
                raw_y = (cy / height) * 180
                servo_x = int(raw_x * 0.6)
                servo_y = int(180 - raw_y)
                servo_x = max(0, min(180, servo_x))
                servo_y = max(0, min(180, servo_y))
            else:
                # Unknown face detected, reset timer and send neutral servo position
                mashkoor_start_time = None
                servo_x, servo_y = 90, 90

            # Send servo commands
            arduino.write(bytes([servo_x, servo_y, extra_servo_trigger]))

            cv2.putText(frame, name, (x, y - 10),
                        cv2.FONT_HERSHEY_DUPLEX, 0.6,
                        (0, 255, 0) if name == "Mashkoor" else (0, 0, 255), 2)

    else:
        mashkoor_start_time = None
        print("No face detected")
        arduino.write(bytes([90, 90, 0]))

    cv2.imshow("Face Tracker", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()