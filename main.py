import cv2 as cv
import numpy as np
from blob import Blob
from blobDetection import BlobDetetction
from blobCounting import BlobCounting

totalNumberOfBlob = 0


def drawBlobCounting(numBlob, img, verticalAxis, horizontalAxis, w, h):
    if(verticalAxis!=0):
        cv.line(img, (0, verticalAxis), (w, verticalAxis), (200, 180, 0), 3)
    else:
        cv.line(img, (horizontalAxis, 0), (horizontalAxis, h), (255,0,0), 3)

    cv.putText(img,
               str(numBlob),
               (100, 100),
               fontFace=cv.FONT_HERSHEY_PLAIN,
               fontScale=3,
               color=(0, 255, 255),
               lineType=3,
               thickness=2)


def frameDiff(uri):

    video = cv.VideoCapture(uri)
    ret, pre_img = video.read()
    shape = pre_img.shape
    pre_img = cv.cvtColor(pre_img, cv.COLOR_BGR2GRAY)
    pre_img = pyrImg(pre_img, shape[1], shape[0])

    shape = pre_img.shape
    h = shape[0]
    w = shape[1]

    pre_sub = pre_img*0

    # window
    cv.namedWindow("original")
    cv.resizeWindow("original", w, h)
    cv.namedWindow("mask_diff")
    cv.resizeWindow("mask_diff", w, h)

    #write video
    out_fourcc = cv.VideoWriter_fourcc(*'XVID')
    out_diff = cv.VideoWriter("out_diff.avi", out_fourcc, 25.0, (len(pre_img[0]), len(pre_img)), True)

    # previous blobs
    blobDetection = BlobDetetction()
    blobCounting = BlobCounting(3*h//4, 3*w//4)

    # detecting region
    detectingRegion_minx = 0
    detectingRegion_miny = h//2
    detectingRegion_maxx = w
    detectingRegion_maxy = h

    #couting region
    countingRegion_minx = 0
    countingRegion_miny = h // 2
    countingRegion_maxx = w
    countingRegion_maxy = h

    while True:
        # recent frame
        ret, img = video.read()
        img = pyrImg(img, w, h)

        img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # sub 2 frame
        sub = cv.absdiff(img_gray, pre_img)

        diff = cv.absdiff(sub, pre_sub)
        # update pre_img
        pre_img = img_gray
        pre_sub = sub
        # threshode
        ret, mask = cv.threshold(diff, 20, 255, cv.THRESH_BINARY)
        # kernel = np.ones((3,3), np.uint8)
        # mask = cv.dilate(mask, kernel)
        # mask = cv.morphologyEx(mask, cv.MORPH_OPEN,kernel)
        blobs = blobDetection.blobDetection(mask, w, h, detectingRegion_minx, detectingRegion_miny, detectingRegion_maxx, detectingRegion_maxy)
        frameBlobs(blobs, img)

        numBlob = blobCounting.countVertical(blobDetection.prevBlobs, countingRegion_minx, countingRegion_miny, countingRegion_maxx, countingRegion_maxy)
        # blobDetection.prevBlobs = np.copy(countedBlobs)
        # for i in range(len(blobDetection.prevBlobs)):
        #     blobDetection.prevBlobs[i].isLabelled = False
        # print("prev len:", len(blobDetection.prevBlobs))


        drawBlobCounting(numBlob, img, blobCounting.verticalAxis, blobCounting.horizontalAxis, w, h)
        # write video
        # out_diff.write(img)

        cv.imshow("original", img)
        cv.imshow("mask_diff", mask)

        key = cv.waitKey(1)
        if key == ord('q'):
            break;
        if key == ord(' '):
            cv.waitKey()

    cv.destroyAllWindows()

def mean(n, uri):
    # kernel_2d = np.ones((7, 7), np.float32) / 49
    # kernel = np.ones((21,21),np.uint8)

    video = cv.VideoCapture(uri)
    ret, img = video.read()
    img = cv.pyrDown(img)
    img = cv.pyrDown(img)
    nframe = []
    sum = np.zeros((len(img), len(img[0])))
    for i in range(n):
        ret, img = video.read()
        img = cv.pyrDown(img)
        img = cv.pyrDown(img)

        img = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
        nframe.append(img)
        sum = sum + img
    mean = np.uint8(sum // n)

    pos = 0

    while True:
        ret, img = video.read()
        # img = cv.resize(img, (w, h))
        img = cv.pyrDown(img)
        img = cv.pyrDown(img)

        img_gray = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
        sub = cv.absdiff(img_gray, mean)
        ret, mask = cv.threshold(sub, 30, 255, cv.THRESH_BINARY)

        blobs = blobDetection(mask)
        frameBlobs(blobs, img)

        sum = (sum - nframe[pos] + img_gray)
        mean = np.uint8(sum // n)
        nframe[pos] = img_gray
        if pos < n - 1:
            pos = pos + 1
        else:
            pos = 0

        # contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        # cv.drawContours(img, contours, -1, (0,255,0), 3)

        cv.namedWindow("original")
        cv.resizeWindow("original", len(mask[0]), len(mask))
        cv.namedWindow("mask_mean")
        cv.resizeWindow("mask_mean", len(mask[0]), len(mask))
        cv.imshow("original", img)
        cv.imshow("mask_mean", mask)

        key = cv.waitKey(10)
        if key == ord('q'):
            break
        if key == ord(' '):
            cv.waitKey()

def mog(uri):
    backsub = cv.createBackgroundSubtractorMOG2()
    video = cv.VideoCapture(uri)

    while True:
        # recent frame
        ret, img = video.read()
        img = cv.pyrDown(img)
        img = cv.pyrDown(img)
        # img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        fgMask = backsub.apply(img)
        # fgMask = cv.morphologyEx(fgMask, cv.MORPH_OPEN, (11, 11))
        blobs = blobDetection(fgMask)
        frameBlobs(blobs, img)

        cv.namedWindow("original")
        cv.resizeWindow("original",len(fgMask[0]), len(fgMask))
        cv.namedWindow("mask_mog")
        cv.resizeWindow("mask_mog", len(fgMask[0]), len(fgMask))
        cv.imshow("original", img)
        cv.imshow("mask_mog", fgMask)

        key = cv.waitKey(10)
        if key == ord('q'):
            break
        if key == ord(' '):
            cv.waitKey()

def all(n, uri):
    video = cv.VideoCapture(uri)
    ret, img = video.read()
    shape = img.shape
    h = shape[0]
    w = shape[1]
    w = w // 2
    h = h // 2
    # mean
    nframe = []
    sum = np.zeros((h, w))
    for i in range(n):
        ret, img = video.read()
        img = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
        img = cv.GaussianBlur(img, (5, 5), 0)
        img = cv.resize(img, (w, h))

        nframe.append(img)
        sum = sum + img
    mean = np.uint8(sum // n)
    pos = 0

    # diff
    pre_img = img
    pre_sub = pre_img

    # mog
    backsub = cv.createBackgroundSubtractorMOG2()

    while True:
        ret, img = video.read()
        img = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
        img = cv.GaussianBlur(img, (5, 5), 0)
        img = cv.resize(img, (w, h))

        # mean
        sub_mean = cv.absdiff(img, mean)
        ret, mask_mean = cv.threshold(sub_mean, 40, 255, cv.THRESH_BINARY)

        sum = (sum - nframe[pos] + img)
        mean = np.uint8(sum // n)
        nframe[pos] = img
        if pos < n - 1:
            pos = pos + 1
        else:
            pos = 0

        # diff
        # sub 2 frame
        sub_diff = cv.absdiff(img, pre_img)

        diff = cv.absdiff(sub_diff, pre_sub)
        # update pre_img
        pre_img = img
        pre_sub = sub_diff

        # threshode
        ret, mask_diff = cv.threshold(diff, 30, 255, cv.THRESH_BINARY)

        # mog
        mask_mog = backsub.apply(img)
        mask_mog = cv.morphologyEx(mask_mog, cv.MORPH_OPEN, (5, 5))

        cv.namedWindow("original")
        cv.resizeWindow("original", w, h)
        cv.namedWindow("mask_diff")
        cv.resizeWindow("mask_diff", w, h)
        cv.namedWindow("mask_mean")
        cv.resizeWindow("mask_mean", w, h)
        cv.namedWindow("mask_mog")
        cv.resizeWindow("mask_mog", w, h)
        cv.imshow("mask_diff", mask_diff)
        cv.imshow("mask_mean", mask_mean)
        cv.imshow("mask_mog", mask_mog)
        cv.imshow("original", img)

        key = cv.waitKey(10)
        if key == ord('q'):
            break
        if key == ord(' '):
            cv.waitKey()

def frameBlobs(blobs, img):
    for i in range(len(blobs)):
        blob = blobs[i]
        cv.rectangle(img, (blob.minx-1, blob.miny-1), (blob.maxx+1, blob.maxy+1), blob.color, blob.thickness)
        cv.putText(img,
                   blob.label,
                   (blob.minx, blob.miny),
                   fontFace=cv.FONT_HERSHEY_PLAIN,
                   fontScale=2,
                   color=(0,255,255),
                   lineType=3,
                   thickness=2)

def pyrImg(img, w, h):
    # if w>=1280 and h>=720:
    #     img = cv.pyrDown(img)
    #     img = cv.pyrDown(img)
    #     return img
    # else:
    #     img = cv.pyrDown(img)
    #     return img
    return cv.pyrDown(img)

# main
uri_road = r"road.mp4"
uri_road_1D = r"road_1D.mp4"
uri_human = r"human.mp4"
uri_moto_vietnam = r"moto_vietnam_SD.mp4"
uri_topdown = r"topdownview.mp4"
uri_topdown2 = r"topdownview2.mp4"

uri_trafficgood = r"traffic_good.mp4"
uri_trafficgood3 = r"traffic_good_3.mp4"

#
# frameDiff(uri_road)
# frameDiff(uri_road_1D)
# frameDiff(uri_human)
# frameDiff(uri_topdown2)
# frameDiff(uri_trafficgood)
frameDiff(uri_trafficgood3)

# mean(5, uri_road)
# mean(5, uri_moto_vietnam)


# mog(uri_road)

