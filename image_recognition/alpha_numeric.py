import cv2
import numpy as np
import time
from PIL import Image
import pytesseract
import Shared

# Must download tesseract 4.1 for whitespace to work

def detect_OCR():
    frame = np.copy(Shared.data.frame)

    text = "Detecting AN"
    cv2.putText(frame, text, (400, 50), cv2.FONT_HERSHEY_SIMPLEX,
        1, (0, 255, 0), 2)

    output = {'data': [], 'time':time.time(),'type':"AN",'imgSize':[frame.shape[0],frame.shape[1]]}
    shelf_tag_width = 130
    shelf_tag_height = 65
    aisle_tag_width = 130
    aisle_tag_height = 130

    # Preprocess image
    Gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(Gray)

    # Detect edges in the image
    edges = cv2.Canny(gray, 0, 255)

    # Close gaps in detected edges
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    edges = cv2.GaussianBlur(edges, (3, 3), 0)

    # Find contours in the image
    (cnts, hierarchy) = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    data = []
    pixel_data = []
    # We are looking for a rectangular label, hence we only look at contours with four corners
    for i in range(len(cnts)):
        cnt = cnts[i]
        # Initialise corners of tag
        bot = []
        top = []
        bl = [-1, -1]
        br = [-1, -1]
        tl = [-1, -1]
        tr = [-1, -1]
        # Approximate the contour shape
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

        # Are there only four corners - i.e. a quadrilateral?
        isConvex = cv2.isContourConvex(approx)
        if len(approx) == 4 and isConvex == True:
            # Here we assume that we are seeing the label front on, so will likely be seeing a rectangle
            # (this seems to improve ocr performance when we dewarp
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            approx = np.int0(box)

            # Does the area have approximately the right size? And aspect ratio?
            (x, y), (rectW, rectH), angle = rect
            aspect_ratio = min(rectH, rectW) / max(rectH, rectW)
            if 1.2 * 0.5 > aspect_ratio > 0.8 * (0.05 / 0.15):
                # We're pretty sure now we have the shelf label corners. Now we need to rotate and extract text
                # We then first need to extract label corners (from approx) by identifying top-left, top-right,
                # bottom-left, bottom-right
                M = cv2.moments(approx)
                cY = int(M["m01"] / M["m00"])
                for i in approx:
                    if i[1] < cY:
                        top.append(i)
                    else:
                        bot.append(i)
                if len(top) == 2 and len(bot) == 2:
                    tl = top[0] if top[0][0] < top[1][0] else top[1]
                    tr = top[1] if top[0][0] < top[1][0] else top[0]
                    bl = bot[0] if bot[0][0] < bot[1][0] else bot[1]
                    br = bot[1] if bot[0][0] < bot[1][0] else bot[0]
                else:
                    continue

                # De-rotate/warp to straighten sign
                pts1 = np.float32([tl, bl, br, tr])
                pts2 = np.float32([[0, 0], [0, shelf_tag_height], [shelf_tag_width, shelf_tag_height], [shelf_tag_width, 0]])
                warp, mask = cv2.findHomography(pts1, pts2)
                straight = cv2.warpPerspective(Gray.copy(), warp, (130, 65))

                # Convert the image to binary and remove boarders
                straight = cv2.threshold(straight, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
                straight = straight[np.int0(shelf_tag_height * 0.12):np.int0(shelf_tag_height * 0.88),
                           np.int0(shelf_tag_width * 0.12):np.int0(shelf_tag_width * 0.88)]

                # Is box likely to have text in it? (image_to_string is expensive, and we should avoid using it where possible)
                kernel = np.array([[0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0],
                                   [1, 1, 1, 1, 1],
                                   [0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0]],
                                  dtype=np.uint8)
                dilated = cv2.morphologyEx(straight, cv2.MORPH_ERODE, kernel, iterations=3)
                dilated = cv2.bitwise_not(dilated)
                (conts, _) = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                isText = False
                for cont in conts:
                    minrect = cv2.minAreaRect(cont)
                    (Cx, Cy), (w, h), angle = minrect
                    textarea = w * h
                    if 0.7 * (dilated.shape[0] * dilated.shape[1]) > textarea > 0.3 * (
                            dilated.shape[0] * dilated.shape[1]) \
                            and ((Cx - 0.5 * dilated.shape[1]) ** 2 + (Cy - 0.5 * dilated.shape[0]) ** 2) ** (
                    0.5) < 0.25 * dilated.shape[0] \
                            and 0.6 > h / w > 0.2:
                        isText = True
                        #print("HERE")
                        break

                if isText:
                    # Sharpen the image
                    blur = cv2.GaussianBlur(straight, (3, 3), 3)
                    straight = cv2.addWeighted(straight, 1.7, blur, -0.7, 0)
                    drc = cv2.copyMakeBorder(straight, top=10, bottom=10, left=10, right=10,
                                             borderType=cv2.BORDER_CONSTANT,
                                             value=(255, 255, 255))
                    # Extract text from image
                    PILimg = Image.fromarray(drc)
                    text = pytesseract.image_to_string(PILimg,
                                                       config='-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                    #print(len(text))
                    if len(text) == 3:
                        pixel_data = (x, y, rectH/frame.shape[0], rectW/frame.shape[1])
                        h = int(rectH)
                        w = int(rectW)
                        x = int(x)
                        y = int(y)
                        #print(x,y,w,h)
                        data = text
                        cv2.rectangle(frame, (x - w//2, y - h//2), (x + w//2, y + h//2), (0, 0, 255), 2)
                        #cv2.circle(frame, (x,y), 10, (0,0,255))
                        output['data'].append(["Shelf",text, np.array([x, y, rectH/frame.shape[0], rectW/frame.shape[1]])])
                        Shared.data.frame_image_recognition = frame
            elif 1.2 > aspect_ratio > 0.8:
                # We're pretty sure now we have the shelf label corners. Now we need to rotate and extract text
                # We then first need to extract label corners (from approx) by identifying top-left, top-right,
                # bottom-left, bottom-right
                M = cv2.moments(approx)
                cY = int(M["m01"] / M["m00"])
                for i in approx:
                    if i[1] < cY:
                        top.append(i)
                    else:
                        bot.append(i)
                if len(top) == 2 and len(bot) == 2:
                    tl = top[0] if top[0][0] < top[1][0] else top[1]
                    tr = top[1] if top[0][0] < top[1][0] else top[0]
                    bl = bot[0] if bot[0][0] < bot[1][0] else bot[1]
                    br = bot[1] if bot[0][0] < bot[1][0] else bot[0]
                else:
                    continue

                # De-rotate/warp to straighten sign
                pts1 = np.float32([tl, bl, br, tr])
                pts2 = np.float32(
                    [[0, 0], [0, aisle_tag_height], [aisle_tag_width, aisle_tag_height], [aisle_tag_width, 0]])
                warp, mask = cv2.findHomography(pts1, pts2)
                straight = cv2.warpPerspective(Gray.copy(), warp, (130, 130))

                # Convert the image to binary and remove boarders
                straight = cv2.threshold(straight, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
                straight = straight[np.int0(shelf_tag_height * 0.12):np.int0(shelf_tag_height * 0.88),
                           np.int0(shelf_tag_width * 0.12):np.int0(shelf_tag_width * 0.88)]

                # Is box likely to have text in it? (image_to_string is expensive, and we should avoid using it where possible)
                kernel = np.array([[0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0],
                                   [1, 1, 1, 1, 1],
                                   [0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0]],
                                  dtype=np.uint8)
                dilated = cv2.morphologyEx(straight, cv2.MORPH_ERODE, kernel, iterations=3)
                dilated = cv2.bitwise_not(dilated)
                (conts, _) = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                isText = False
                for cont in conts:
                    minrect = cv2.minAreaRect(cont)
                    (Cx, Cy), (w, h), angle = minrect
                    textarea = w * h
                    if 0.3 * (dilated.shape[0] * dilated.shape[1]) > textarea > 0.01 * (
                            dilated.shape[0] * dilated.shape[1]) \
                            and ((Cx - 0.5 * dilated.shape[1]) ** 2 + (Cy - 0.5 * dilated.shape[0]) ** 2) ** (
                            0.5) < 0.25 * dilated.shape[0] \
                            and 0.9 > h / w > 0.6:
                        isText = True
                        break

                if isText:
                    # Sharpen the image
                    blur = cv2.GaussianBlur(straight, (3, 3), 3)
                    straight = cv2.addWeighted(straight, 1.7, blur, -0.7, 0)
                    drc = cv2.copyMakeBorder(straight, top=10, bottom=10, left=10, right=10,
                                             borderType=cv2.BORDER_CONSTANT,
                                             value=(255, 255, 255))
                    # Extract text from image
                    PILimg = Image.fromarray(drc)
                    text = pytesseract.image_to_string(PILimg,
                                                       config='-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                    # print(len(text))
                    if len(text) == 2:
                        if Shared.data.find_shelf:
                            if text==Shared.data.shelf_number[1]:
                                pixel_data = (x, y, rectH / frame.shape[0], rectW / frame.shape[1])
                                h = int(rectH)
                                w = int(rectW)
                                x = int(x)
                                y = int(y)
                                # print(x,y,w,h)
                                data = text
                                cv2.rectangle(frame, (x - w // 2, y - h // 2), (x + w // 2, y + h // 2), (0, 0, 255), 2)
                                output['data'].append(
                                    ["Aisle", text, np.array([x, y, rectH / frame.shape[0], rectW / frame.shape[1]])])
                                Shared.data.frame_image_recognition = frame
                                Shared.data.image_data = {
                                    'data' : data, # List of values obtained from detection (e.g. qr code values)
                                    'time' : time.time(),
                                    'type' : 'AN',
                                    'pixel' :  pixel_data# List of pixel width and height relative to frame size
                                }
                                break

    Shared.data.frame_image_recognition = frame
    Shared.data.image_data = {
        'data' : data, # List of values obtained from detection (e.g. qr code values)
        'time' : time.time(),
        'type' : 'AN',
        'pixel' :  pixel_data# List of pixel width and height relative to frame size
    }
