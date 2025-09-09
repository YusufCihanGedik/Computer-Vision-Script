import os
import cv2
import shutil

# ======= AYARLAR =======
IMAGE_DIR = "images"             # Görsellerin klasörü
LABEL_DIR = "labels"             # Label dosyalarının klasörü (YOLO format: cls cx cy w h [0-1])
DELETE_DIR = "deleted"           # Silinenlerin taşınacağı klasör
REVISE_DIR = "revise"            # Revizeye gidenlerin klasörü
# ========================

os.makedirs(DELETE_DIR, exist_ok=True)
os.makedirs(REVISE_DIR, exist_ok=True)

# (Opsiyonel) Sınıf adlarını oku: labels/classes.txt (her satır bir sınıf adı)
CLASS_NAMES = None
classes_txt = os.path.join(LABEL_DIR, "classes.txt")
if os.path.exists(classes_txt):
    with open(classes_txt, "r", encoding="utf-8") as f:
        CLASS_NAMES = [line.strip() for line in f if line.strip()]

def yolo_to_xyxy(line, img_w, img_h):
    """
    YOLO formatı: cls cx cy w h (hepsi normalize)
    Dönen: (cls_id, x1, y1, x2, y2) piksel koordinatı
    """
    parts = line.strip().split()
    if len(parts) < 5:
        return None
    cls_id = int(float(parts[0]))
    cx, cy, w, h = map(float, parts[1:5])

    px_w, px_h = w * img_w, h * img_h
    px_cx, px_cy = cx * img_w, cy * img_h

    x1 = int(max(0, px_cx - px_w / 2))
    y1 = int(max(0, px_cy - px_h / 2))
    x2 = int(min(img_w - 1, px_cx + px_w / 2))
    y2 = int(min(img_h - 1, px_cy + px_h / 2))
    return cls_id, x1, y1, x2, y2

# Görselleri topla
image_files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
image_files.sort()
index = 0

print("Sınıf Listesi:")
if CLASS_NAMES:
    for i, name in enumerate(CLASS_NAMES):
        print(f"{i}: {name}")
else:
    print("classes.txt bulunamadı. Etiketlerde sınıf adları yerine ID gösterilecek.")

while 0 <= index < len(image_files):
    img_name = image_files[index]
    img_path = os.path.join(IMAGE_DIR, img_name)
    label_path = os.path.join(LABEL_DIR, os.path.splitext(img_name)[0] + ".txt")

    frame = cv2.imread(img_path)
    if frame is None:
        print(f"❌ Görsel okunamadı: {img_path}")
        # bozuk görseli atla
        image_files.pop(index)
        if index >= len(image_files):
            index = len(image_files) - 1
        continue

    h, w = frame.shape[:2]

    # Etiketleri çiz
    if os.path.exists(label_path):
        try:
            with open(label_path, "r", encoding="utf-8") as lf:
                lines = [ln for ln in lf if ln.strip()]
            for ln in lines:
                parsed = yolo_to_xyxy(ln, w, h)
                if not parsed:
                    continue
                cls_id, x1, y1, x2, y2 = parsed
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 2)
                name = CLASS_NAMES[cls_id] if (CLASS_NAMES and 0 <= cls_id < len(CLASS_NAMES)) else str(cls_id)
                label_text = f"{name}"
                cv2.putText(frame, label_text, (x1, max(0, y1 - 7)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 0), 2)
        except Exception as e:
            print(f"⚠️ Label okunamadı ({label_path}): {e}")
    else:
        cv2.putText(frame, "No label file", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (20, 20, 220), 2)

    # Sayaç overlay (opsiyonel)
    info = f"{index+1}/{len(image_files)}  |  {img_name}"
    cv2.putText(frame, info, (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (50, 180, 255), 2)

    cv2.imshow("Etiket Kontrol", frame)
    key = cv2.waitKey(0) & 0xFF

    if key == ord("q"):  # çıkış
        break
    elif key == ord("d"):  # ileri
        index = (index + 1) % len(image_files)
    elif key == ord("a"):  # geri
        index = (index - 1) % len(image_files)
    elif key == ord("w"):  # silinen klasörüne taşı
        try:
            shutil.move(img_path, os.path.join(DELETE_DIR, img_name))
            if os.path.exists(label_path):
                shutil.move(label_path, os.path.join(DELETE_DIR, os.path.basename(label_path)))
            print(f"🗑️ Silindi -> {img_name}")
        except Exception as e:
            print(f"Taşıma hatası (deleted): {e}")
        image_files.pop(index)
        if index >= len(image_files):
            index = len(image_files) - 1
    elif key == ord("s"):  # revize klasörüne taşı
        try:
            shutil.move(img_path, os.path.join(REVISE_DIR, img_name))
            if os.path.exists(label_path):
                shutil.move(label_path, os.path.join(REVISE_DIR, os.path.basename(label_path)))
            print(f"✏️ Revizeye yollandı -> {img_name}")
        except Exception as e:
            print(f"Taşıma hatası (revise): {e}")
        image_files.pop(index)
        if index >= len(image_files):
            index = len(image_files) - 1

cv2.destroyAllWindows()
