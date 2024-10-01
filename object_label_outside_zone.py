import cv2
from ultralytics import YOLO
import os
import uuid


def list_avi_files(directory):
    avi_files = [f for f in os.listdir(directory) if f.endswith('.mp4')]
    print("avi2",)
    return avi_files


def is_point_in_rect(point, rect_top_left, rect_bottom_right):
    (x1,y1) = point
    (rx1, ry1) = rect_top_left
    (rx2, ry2) = rect_bottom_right

    print("(x1,y1)",(x1,y1))
    print("(rx1, ry1)",(rx1, ry1))
    print(" (rx2, ry2)", (rx2, ry2))

    
    return rx1 <= x1 <= rx2 and ry1 <= y1 <= ry2


def is_box_in_roi(box, roi_x1, roi_y1, roi_x2, roi_y2):
    """
    Tespit edilen kutunun (box) ROI alanı içinde olup olmadığını kontrol eder.
    box: (x1, y1, x2, y2) formatında tespit edilen kutu koordinatları
    ROI: Sol üst köşe (roi_x1, roi_y1) ve sağ alt köşe (roi_x2, roi_y2)
    """
    x1, y1, x2, y2 = box
    # Kutu ROI içinde mi? (Kısmi örtüşme kontrolü)
    return not (x2 < roi_x1 or x1 > roi_x2 or y2 < roi_y1 or y1 > roi_y2)

def process_video(video_path, model, frame_skip):
    home_point = ((1200, 538), (1266, 578))  # Home point tanımlaması
    home_point2 = ((152, 1027), (192, 1067))  # İkinci home point (isteğe bağlı)

    base_folder, video_file = os.path.split(video_path)
    video_folder_name, _ = os.path.splitext(video_file)
    unique_id = str(uuid.uuid4())

    labelling_base = os.path.join(base_folder, "labelling-data", video_folder_name)
    detection_images_folder = os.path.join(labelling_base, "images_with_detections")
    no_detection_images_folder = os.path.join(labelling_base, "images_without_detections")
    labels_folder = os.path.join(labelling_base, "labels")
    os.makedirs(detection_images_folder, exist_ok=True)
    os.makedirs(no_detection_images_folder, exist_ok=True)
    os.makedirs(labels_folder, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened(), "Video açılamıyor"

    frame_count = 0

    roi_x, roi_y, roi_w, roi_h = 1040, 0, 1518, 1436  

    while cap.isOpened():
        ret, frame = cap.read()
        # print(frame.shape)
        if not ret:
            break

        # roi_frame = frame[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]

        if frame_count % frame_skip == 0:
            results = model(frame, device="0", conf=0.70)  
            detection_found = False

            for result in results:
                boxes = result.boxes.xyxy
                classes = result.boxes.cls

                for box, cls in zip(boxes, classes):
                    orig_x1, orig_y1, orig_x2, orig_y2 = box
                    print("orig_x1, orig_y1:", orig_x1, orig_y1)
                    cls = int(cls)
                    if cls == 0:
                        color = (0, 0, 255)
                        # cv2.rectangle(frame, (int(orig_x1), int(orig_y1)), (int(orig_x2), int(orig_y2)), color, 2)
                        # cv2.rectangle(frame, (1200, 538), (1266, 578),(0, 255, 0))
                        leftcorner_top = (int(orig_x1) , int(orig_y1) ) 
                        # cv2.circle(frame,leftcorner_top,5,(255,255,0),-1) 

                        is_inside_home_point = is_point_in_rect(leftcorner_top, home_point[0], home_point[1])
                        inside_box = is_box_in_roi((orig_x1, orig_y1, orig_x2, orig_y2), roi_x, roi_y, (roi_x+roi_w), (roi_y+roi_h))
                        print("inside_box",inside_box)
                        if inside_box:
                            print("hey")
                            if is_inside_home_point:
                                print("Nokta home_point içinde!")
                                file_base = f"{unique_id}_{frame_count}"
                                # save_frame(frame, file_base, no_detection_images_folder)  
                            else:
                                print("1", leftcorner_top)
                                print("2", home_point[0], home_point[1])
                                print("Nokta home_point dışında, kaydediliyor!")
                                file_base = f"{unique_id}_{frame_count}"
                                write_boxes_to_txt(result.boxes, file_base, labels_folder)
                                save_frame(frame, file_base, detection_images_folder)  
                                detection_found = True
                                break
                        else : 
                            print("Nokta roi dışında!")
                           

            if not detection_found:
                file_base = f"{unique_id}_{frame_count}"
                save_frame(frame, file_base, no_detection_images_folder)

        frame_count += 1

    cap.release()




def write_boxes_to_txt(boxes, file_base, output_folder):
    file_name = f"{file_base}.txt"
    output_path = os.path.join(output_folder, file_name)
    with open(output_path, 'w') as file:
        for box, class_id in zip(boxes.xywhn, boxes.cls):
            line = f"{int(class_id)} {box[0]} {box[1]} {box[2]} {box[3]}\n"
            file.write(line)

            
def save_frame(frame, file_base, folder):
    file_name = f"{file_base}.jpg"
    output_path = os.path.join(folder, file_name)
    cv2.imwrite(output_path, frame)

model = YOLO(r"C:\Users\Gedik\Desktop\baskent_test\16_09.pt")

# Video yolu
directir_dir = r"C:\Users\Gedik\Desktop\baskent_test\result"

folder_names=os.listdir(directir_dir)
print(folder_names)
for folder_name in folder_names:
    directory_local=f"{directir_dir}/{folder_name}"
    # directory_local=f"{directir_dir}"

    print("direc",directory_local)
    avi_files = list_avi_files(directory_local)
    print("avifiles",avi_files)
    # fps_list=[90,90,90,90,15,15,15,15,15,15,15]
    # print(len(fps_list))
    # avi_files = [j for i, j in enumerate(avi_files) if i not in [7]]
    # print(len(avi_files))
    for count,video_path in enumerate(avi_files):
         print("hey burada")
         process_video(f"{directory_local}/{video_path}", model,frame_skip=60)
