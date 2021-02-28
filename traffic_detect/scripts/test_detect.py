import numpy as np
import cv2

cap = cv2.VideoCapture(0)

template = cv2.imread('template.png',0)
# template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)


w, h = template.shape[::-1]

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # cv2.imshow('temp',template)
    # cv2.imshow('frame',gray)

    res = cv2.matchTemplate(gray,template,cv2.TM_CCOEFF_NORMED)
    
    threshold = 0.9
    loc = np.where( res >= threshold)

    i = 0
    for pt in zip(*loc[::-1]):
        cv2.rectangle(gray, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
        i += 1
    print(i)
    # # Display the resulting frame
    cv2.imshow('frame',gray)
    cv2.imshow('temp',template)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()