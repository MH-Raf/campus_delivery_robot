import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
from ultralytics import YOLO

class Action(Enum):
    MOVE = "двигаться"
    STOP = "остановиться"
    AVOID = "объехать"

@dataclass
class DetectedObject:
    class_name: str
    confidence: float
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def area(self):
        return (self.x2 - self.x1) * (self.y2 - self.y1)

    @property
    def center(self):
        return int((self.x1 + self.x2) / 2), int((self.y1 + self.y2) / 2)

class YOLOVisionSensor:
    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        confidence: float = 0.10,
        classes: Optional[List[str]] = None
    ):
        self.model = YOLO(model_path)
        self.confidence = confidence
        self.allowed_classes = classes

    def read(self, frame) -> List[DetectedObject]:
        results = self.model(
            frame,
            conf=self.confidence,
            verbose=False
        )

        objects: List[DetectedObject] = []

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                name = self.model.names[cls_id]

                if self.allowed_classes and name not in self.allowed_classes:
                    continue

                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                objects.append(
                    DetectedObject(
                        class_name=name,
                        confidence=conf,
                        x1=x1,
                        y1=y1,
                        x2=x2,
                        y2=y2
                    )
                )
        return objects

class SimpleVisionController:
    def __init__(self, danger_area=8000):
        self.danger_area = danger_area

    def decide(self, objects: List[DetectedObject]):
        for obj in objects:
            if obj.area > self.danger_area:
                return Action.STOP, f"Опасный объект: {obj.class_name}"
        return Action.MOVE, "Путь свободен"

def draw_objects(frame, objects: List[DetectedObject], action: Action):
    for obj in objects:
        color = (0, 255, 0)

        if obj.class_name == "person":
            color = (0, 0, 255)
        elif obj.class_name in ("sports ball", "frisbee"):
            color = (255, 0, 0)
        elif obj.class_name == "box":
            color = (0, 255, 255)

        cv2.rectangle(frame, (obj.x1, obj.y1), (obj.x2, obj.y2), color, 2)

        label = f"{obj.class_name} {obj.confidence:.2f}"
        cv2.putText(
            frame,
            label,
            (obj.x1, obj.y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )

    cv2.putText(
        frame,
        f"ACTION: {action.value}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 0),
        3
    )

if __name__ == "__main__":

    IMAGE_PATH = "camp.png" 

    frame = cv2.imread(IMAGE_PATH)
    if frame is None:
        raise RuntimeError("Изображение не загружено")

    frame = cv2.resize(frame, None, fx=1.5, fy=1.5)

    sensor = YOLOVisionSensor(
        model_path="yolov8n.pt",
        confidence=0.10,
        classes=["person", "sports ball", "box", "frisbee"]
    )

    controller = SimpleVisionController(danger_area=8000)

    objects = sensor.read(frame)
    action, reason = controller.decide(objects)

    print("[VISION]")
    for o in objects:
        print(o.class_name, f"{o.confidence:.2f}", "area:", o.area)

    print("Action:", action.value, "| Reason:", reason)

    draw_objects(frame, objects, action)

    cv2.imshow("YOLO Vision", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
