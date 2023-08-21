import sys
import cv2

def read_cam():
    cap = cv2.VideoCapture("nvarguscamerasrc ! video/x-raw(memory:NVMM),format=NV12,width=640,height=480,framerate=30/1 ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! video/x-raw,format=BGR ! appsink drop=1", cv2.CAP_GSTREAMER)
    if cap.isOpened():
        cv2.namedWindow("demo", cv2.WINDOW_AUTOSIZE)
        while True:
            ret_val, img = cap.read()
            cv2.imshow('demo',img)
            cv2.waitKey(10)
    else:
     print("camera open failed")

    cv2.destroyAllWindows()


if __name__ == '__main__':
    read_cam()