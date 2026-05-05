# This is Detection.py

from ultralytics import YOLO
import cv2
import numpy as np

model = YOLO('yolov8m.pt')  # This we use YOLOv8n for Cloud compatibility

COCO_PHONE = 67
COCO_PERSON = 0

def analyze_frame(frame: np.ndarray) -> dict:
  """
  Run YOLO inference on a frame and return structured detection results.

  Returns:
    dict with keys:
        - status: str ("Focused", "Phone Distraction", "Absent", "Social Distraction")
        - distraction_type: str | None
        - annotated_frame: np.ndarray
        - person_count: int
        - phone_detected: bool
  """
  results = model(frame, verbose=False)[0]

  person_count = 0
  phone_detected = False
  annotated = frame.copy()

  for box in results.boxes:
    cls = int(box.cls)
    conf = float(box.conf)
    x1, y1, x2, y2 = map(int, box.xyxy[0])

    if cls == COCO_PERSON and conf > 0.35:
      person_count += 1
      cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
      cv2.putText(annotated, f"Person ({conf:.0%})", (x1, y1 - 8),
                 cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 1)

    elif cls == COCO_PHONE and conf > 0.4:
      phone_detected = True
      cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 3)
      cv2.putText(annotated, f"Phone ({conf:.0%})", (x1, y1 - 8),
                 cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 1)

    # This will determine the status where the priority order matters
    if phone_detected:
      status = "Phone Distraction"
      distraction_type = "phone"
    elif person_count == 0:
      status = "Absent from Desk"
      distraction_type = "absent"
    elif person_count > 1:
      status = "Social Distraction"
      distraction_type = "social"
    else:
      status = "Focused ✓"
      distraction_type = None

    return {
      "status": status,
      "distraction_type": distraction_type,
      "annotated_frame": annotated,
      "person_count": person_count,
      "phone_detected": phone_detected
    }
