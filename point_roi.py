import cv2
import numpy as np

# Dört noktayı saklamak için bir liste
points = []

# Mouse callback fonksiyonu
def draw_roi(event, x, y, flags, param):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        # Sol fare butonu ile tıklama yapıldığında, nokta ekleyin
        points.append((x, y))
        # Noktayı çiz
        cv2.circle(img, (x, y), 5, (0, 255, 0), -1)
        if len(points) == 4:
            # Eğer dört nokta seçildiyse, çizgilerle birleştir
            cv2.line(img, points[0], points[1], (0, 255, 0), 2)
            cv2.line(img, points[1], points[2], (0, 255, 0), 2)
            cv2.line(img, points[2], points[3], (0, 255, 0), 2)
            cv2.line(img, points[3], points[0], (0, 255, 0), 2)
            print(points)
        cv2.imshow("Image", img)

# Görüntüyü yükleyin
img = cv2.imread(r"C:\Users\Gedik\Desktop\ComputerVision\DeepLearning\yolov8-pose\video_img\KESIM_BASKENT_20240802142046_20240802142959_2879799.jpg")  # Görüntü dosyanızın yolunu buraya yazın

# Görüntü üzerinde mouse callback fonksiyonunu tanımlayın
cv2.namedWindow("Image")
cv2.setMouseCallback("Image", draw_roi)

while True:
    cv2.imshow("Image", img)
    # Esc tuşuna basıldığında döngüyü kırın
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break

cv2.destroyAllWindows()
