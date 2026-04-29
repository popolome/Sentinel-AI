import cv2
from detection import analyze_frame

# This will load any image from my PC
img = cv2.imread("test_image.jpg")

result = analyze_frame(img)

print("Status:", result["status"])
print("Person count:", result["person_count"])
print("Phone detected:", result["phone_detected"])

# This will save the annotated frame to see the bounding boxes
cv2.imwrite("output.jpg", result["annotated_frame"])
print("Saved annotated output to output.jpg")
