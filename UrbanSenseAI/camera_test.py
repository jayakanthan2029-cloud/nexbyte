import cv2

url = "http://10.54.205.62:8080/video"

cap = cv2.VideoCapture(url)

if not cap.isOpened():
    print("❌ Could not connect to phone")
    exit()

print("✅ Phone camera connected")

while True:
    ret, frame = cap.read()

    if not ret:
        print("❌ Frame failed")
        break

    cv2.imshow("UrbanSenseAI - Phone Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()