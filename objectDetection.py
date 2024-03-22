import tensorflow as tf
import numpy as np
import cv2
import time
import os
import tkinter

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

class objectDetection:
    def __init__(self) -> None:
        self.DATA_DIR = os.path.join(os.getcwd(), 'data')
        self.MODELS_DIR = os.path.join(self.DATA_DIR, 'models')
        self.MODEL_NAME = 'ssd_inception_v2_coco_2017_11_17'
        #self.MODEL_NAME = 'faster_rcnn_resnet101_coco_2017_11_08'
        self.PATH_TO_CKPT = os.path.join(self.MODELS_DIR, os.path.join(self.MODEL_NAME + '/frozen_inference_graph.pb'))
        self.LABEL_FILENAME = 'mscoco_label_map.pbtxt'
        self.PATH_TO_LABELS = os.path.join(self.MODELS_DIR, os.path.join(self.MODEL_NAME, self.LABEL_FILENAME))
        self.NUM_CLASSES = 10

    def load(self) -> None:
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            self.od_graph_def = tf.compat.v1.GraphDef()
        with tf.compat.v2.io.gfile.GFile(self.PATH_TO_CKPT, 'rb') as fid:
            self.serialized_graph = fid.read()
            self.od_graph_def.ParseFromString(self.serialized_graph)
            tf.import_graph_def(self.od_graph_def, name='')
            
        self.label_map = label_map_util.load_labelmap(self.PATH_TO_LABELS)
        self.categories = label_map_util.convert_label_map_to_categories(self.label_map, max_num_classes=self.NUM_CLASSES, use_display_name=True)
        self.category_index = label_map_util.create_category_index(self.categories)

        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            self.od_graph_def = tf.compat.v1.GraphDef()
            with tf.compat.v2.io.gfile.GFile(self.PATH_TO_CKPT, 'rb') as fid:
                self.serialized_graph = fid.read()
                self.od_graph_def.ParseFromString(self.serialized_graph)
                tf.import_graph_def(self.od_graph_def, name='')
        self.sess = tf.compat.v1.Session(graph=self.detection_graph)
        self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        self.detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        self.detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

    def region_of_interest(self, img, vertices) -> None:
        mask = np.zeros_like(img)   
        if len(img.shape) > 2:
            channel_count = img.shape[2]
            ignore_mask_color = (255,) * channel_count
        else:
            ignore_mask_color = 255   
        cv2.fillPoly(mask, vertices, ignore_mask_color)
        masked_image = cv2.bitwise_and(img, mask)
        return masked_image

    def writeToFile(self, text) -> None:
        f = open("voice.txt", "w")
        f.write(text)
        f.close()

    def function(self) -> None:
        video = cv2.VideoCapture(0)
        root = tkinter.Tk()
        frame_width = root.winfo_screenwidth()
        frame_height = root.winfo_screenheight()
        try:
            while(video.isOpened()):
                while os.stat("state.txt").st_size == 0:
                    try:
                        cv2.destroyAllWindows()
                        self.writeToFile("")
                    except:
                        pass
                ret, orgFrame = video.read()
                frame = cv2.flip(orgFrame, 1)
                stime = time.time()
                objects = []
                class_str = ""
                frame_width = frame.shape[0]
                frame_height = frame.shape[1]
                rows, cols = frame.shape[:2]
                left_boundary = [int(cols*0.40), int(rows*0.95)]
                left_boundary_top = [int(cols*0.40), int(rows*0.20)]
                right_boundary = [int(cols*0.60), int(rows*0.95)]
                right_boundary_top = [int(cols*0.60), int(rows*0.20)]
                bottom_left  = [int(cols*0.20), int(rows*0.95)]
                top_left     = [int(cols*0.20), int(rows*0.20)]
                bottom_right = [int(cols*0.80), int(rows*0.95)]
                top_right    = [int(cols*0.80), int(rows*0.20)]
                vertices = np.array([[bottom_left, top_left, top_right, bottom_right]], dtype=np.int32)
                cv2.line(frame,tuple(bottom_left),tuple(bottom_right), (59, 37, 120), 5)
                cv2.line(frame,tuple(bottom_right),tuple(top_right), (59, 37, 120), 5)
                cv2.line(frame,tuple(top_left),tuple(bottom_left), (59, 37, 120), 5)
                cv2.line(frame,tuple(top_left),tuple(top_right), (59, 37, 120), 5)
                copied = np.copy(frame)
                interested=self.region_of_interest(copied,vertices)
                frame_expanded = np.expand_dims(interested, axis=0)

                (boxes, scores, classes, num) = self.sess.run(
                    [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
                    feed_dict={self.image_tensor: frame_expanded})
                vis_util.visualize_boxes_and_labels_on_image_array(
                    frame,
                    np.squeeze(boxes),
                    np.squeeze(classes).astype(np.int32),
                    np.squeeze(scores),
                    self.category_index,
                    use_normalized_coordinates=True,
                    line_thickness=8,
                    min_score_thresh=0.78)
                print(frame_width,frame_height)
                ymin = int((boxes[0][0][0]*frame_width))
                xmin = int((boxes[0][0][1]*frame_height))
                ymax = int((boxes[0][0][2]*frame_width))
                xmax = int((boxes[0][0][3]*frame_height))
                Result = np.array(frame[ymin:ymax,xmin:xmax])

                ymin_str='y min  = %.2f '%(ymin)
                ymax_str='y max  = %.2f '%(ymax)
                xmin_str='x min  = %.2f '%(xmin)
                xmax_str='x max  = %.2f '%(xmax)

                cv2.putText(frame,ymin_str, (50, 50),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,0,0),2)
                cv2.putText(frame,ymax_str, (50, 70),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,0,0),2)
                cv2.putText(frame,xmin_str, (50, 90),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,0,0),2)
                cv2.putText(frame,xmax_str, (50, 110),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,0,0),2)
                print(scores.max())
                
                print("left_boundary[0],right_boundary[0] :", left_boundary[0], right_boundary[0])
                print("left_boundary[1],right_boundary[1] :", left_boundary[1], right_boundary[1])
                print("xmin, xmax :", xmin, xmax)
                print("ymin, ymax :", ymin, ymax)
                
                if scores.max() > 0.78:
                    print("inif")
                    self.writeToFile('')
                    
                if(xmin >= left_boundary[0]):
                    print("move Right - 2nd !!!")
                    self.writeToFile('move right')
                    cv2.putText(frame,'Move RIGHT!', (300, 80),cv2.FONT_HERSHEY_SIMPLEX,0.75,(0,255,0),2)

                elif(xmax <= right_boundary[0]):
                    print("move LEFT - 1st !!!")
                    self.writeToFile('move left')
                    cv2.putText(frame,'Move LEFT!', (300, 80),cv2.FONT_HERSHEY_SIMPLEX,0.75,(0, 0, 204),2)
                    
                elif(xmin <= left_boundary[0] and xmax >= right_boundary[0]):
                    print("Either move left or right")
                    self.writeToFile('either move left or right')
                    cv2.putText(frame,'Either move left or right!!!', (250, 80),cv2.FONT_HERSHEY_SIMPLEX,0.75,(0, 0, 204),2)
                    cv2.line(frame,tuple(left_boundary),tuple(left_boundary_top), (59, 37, 120), 5)
                    cv2.line(frame,tuple(right_boundary),tuple(right_boundary_top),(59, 37, 120), 5)

                cv2.imshow('object detection',cv2.resize(frame, (1080,720)))
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
            video.release()
            cv2.destroyAllWindows()
        except Exception as e:
            print(str(e))

if __name__ == "__main__":
    obj = objectDetection()
    obj.load()
    obj.function()