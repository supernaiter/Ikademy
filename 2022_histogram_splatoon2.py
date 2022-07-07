import cv2
import time
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
import tkinter
import numpy as np
import random

# USBカメラのID番号
no = 1

sequence = ""

# USBカメラから映像を取り込む
cap_0 = cv2.VideoCapture("1080p2.mp4")

cap_0.set(3, 1920)
cap_0.set(4, 1080)
cap_0.set(5, 30)

count = 0
def detect_loading_screen(img):
    hist_value = cv2.calcHist([img],[0],None,[256],[0,256])
    if hist_value[0] > 30000:
        if np.sum(hist_value[50:]) < 1000:
            return True

def main_screen_detection(img, sequence):
    gray_raw_img = cv2.cvtColor(img[50:110, 900:1020], cv2.COLOR_BGR2GRAY)
    img_hist, img_bins = np.histogram(np.array(gray_raw_img).flatten(), bins=np.arange(256+1))
    if np.sum(img_hist[:50]) > 3000:
        if np.sum(img_hist[50:200]) < 2000:
            if np.sum(img_hist[250:]) > 200:
                return True

def kill_detection(img, sequence):
    gray_raw_img = cv2.cvtColor(img[1000:1030, 750:1170], cv2.COLOR_BGR2GRAY)
    img_hist, img_bins = np.histogram(np.array(gray_raw_img).flatten(), bins=np.arange(256+1))
    if np.sum(img_hist[:25]) > 3000:
        #print("g1")
        if np.sum(img_hist[100:200]) < 3000:
            #print("g2")
            if np.sum(img_hist[253:]) > 200:
                return True

def calculate_special_point(img):
    ret, th = cv2.threshold(img[40:190,1700:1840], 127, 255, cv2.THRESH_BINARY)
    img_hist, img_bins = np.histogram(th.flatten(), bins=np.arange(256+1))
    #special_point = 4000//img_hist[0]
    #print(img_hist[0]-5000)
    print((60000 - img_hist[0])//200)

def find_rankmatch_title(img):
    hist_value = cv2.calcHist([img[240:500, 800:1100]],[0],None,[256],[0,256])
    if hist_value[0] > 5000:
        if hist_value[255] > 500:
            if np.all(hist_value[20:200]<1000):
                return True

def detect_map(img, sequence):
    hist1 = cv2.calcHist([img[480:600, 50:450]],[0],None,[256],[0,256])
    hist2 = cv2.calcHist([img[490:590, 1470:1850]],[0],None,[256],[0,256])
    hist3 = cv2.calcHist([img[50:140, 750:1150]],[0],None,[256],[0,256])
    hist4 = cv2.calcHist(img[950:1030, 750:1150],[0],None,[256],[0,256])
    if (np.any(hist1[0:70]>1000)) and (np.any(hist1[250:]>1000)):
        if np.any(hist2[0:70]>1000) and np.any(hist2[250:]>1000):
            if np.any(hist3[0:70]>1000) and np.any(hist3[250:]>1000) :
                if np.any(hist4[0:70]>100):
                    return True
    
def detect_whiteout(img):
    hist_value = cv2.calcHist([img],[0],None,[256],[0,256])
    if hist_value[254] > 30000:
        if np.sum(hist_value[:200]) < 1000:
            print("white_out")

if cap_0.isOpened() is False:
    raise("IO Error")

colors = ("r", "g", "b")
cnt = 0

while True:
    # 時間測定開始
    t1 = time.time()

    is_ok_0, img_0 = cap_0.read()
    #print(is_ok_0)
    if cnt < 3:
        cnt += 1
        continue

    cnt = 0

    if is_ok_0 == False:
        continue
    title_flag = False
    map_flag = False
    black_screen_flag = False
    main_flag= False
    kill_flag = False


    # 画像の切り抜き（取り込み画像を1：1にする, Y:X）
    title_flag = find_rankmatch_title(img_0)
    map_flag = detect_map(img_0, sequence)
    black_screen_flag = detect_loading_screen(img_0)
    main_flag = main_screen_detection(img_0,sequence)
    kill_flag = kill_detection(img_0, sequence)
    detect_whiteout(img_0)
    img_a = img_0
    #img_a = img_0[400:600, 0:500]
    if title_flag:
        print("title")
    if map_flag:
        print("map detected")
        main_flag = False
    if black_screen_flag:
        print("black out...")
    if main_flag:
        #print("main_screen")
        special_point = calculate_special_point(img_0)
    if kill_flag:
        if main_flag:
            print("GOTCHA!")

    # プロットの初期化
    plt.clf()

    # RGBごとにヒストグラムを計算しプロット
    for i, channel in enumerate(colors):
        histgram = cv2.calcHist([img_a], [i], None, [256], [0, 256])
        plt.plot(histgram, color = channel)
        plt.xlim([0, 256])

    # プロットの更新間隔。カッコの中は時間(msec)
    plt.pause(0.01)

    # 時間計測終了
    elapsedTime = time.time() - t1

    # フレームレートの計算
    fps = "{:.0f}FPS".format(1/elapsedTime)

    # 画面にfpsを表示させる
    cv2.putText(img_a, fps, (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2, cv2.LINE_AA)
    
    # USBカメラから取り込んだ映像を表示
    cv2.imshow('cap_test_a', img_a)

    # 画面表示位置の指定(表示画面の名前, x座標, y座標)
    cv2.moveWindow('cap_test_a', 200, 50)  

    # グラフの表示位置を指定
    fig_place = plt.get_current_fig_manager()

    # カッコの中(windows画面のx座標，y座標，表示させる図の幅，図の高さ)
    #ig_place.window.setGeometry(1112, 85, 640, 480)  

    k = cv2.waitKey(1)
    
    if k == ord('q'):
        break

cap_0.release()
cv2.destroyAllWindows()