import numpy as np, cv2, zmq

TEXT, SCALE, COLOR, THICK = "TEXT", 1.0, (0, 0, 255), 2
ALPHA = 0.8


ctx = zmq.Context()
sock = ctx.socket(zmq.SUB); sock.setsockopt(zmq.SUBSCRIBE, b""); sock.connect("tcp://84.237.21.36:6002")
cv2.namedWindow("Stream")

def draw_text_perspective(frame, pts, text, scale, color, thick):
    h, w = frame.shape[:2]
    rect = pts.reshape(4, 2).astype(np.float32)

    s = rect.sum(1); rect = rect[np.argsort(s)][[0, -1, -1, 0]]  # упрощённая сортировка
    rect[1] = rect[np.argmin(np.diff(rect, axis=1))]  # TR
    rect[3] = rect[np.argmax(np.diff(rect, axis=1))]  # BL
    
  
    tw, th = int(np.linalg.norm(rect[1]-rect[0])), int(np.linalg.norm(rect[3]-rect[0]))
    canvas = np.zeros((max(th,30), max(tw,100), 3), np.uint8)
    

    font = cv2.FONT_HERSHEY_SIMPLEX
    (tw_text, th_text), bl = cv2.getTextSize(text, font, scale, thick)
    x, y = (canvas.shape[1]-tw_text)//2, (canvas.shape[0]+th_text)//2
    cv2.putText(canvas, text, (x-2,y-2), font, scale, (0,0,0), thick+2, cv2.LINE_AA)
    cv2.putText(canvas, text, (x,y), font, scale, color, thick, cv2.LINE_AA)
    

    src = np.array([[0,0],[canvas.shape[1],0],[canvas.shape[1],canvas.shape[0]],[0,canvas.shape[0]]], np.float32)
    M = cv2.getPerspectiveTransform(src, rect)
    warped = cv2.warpPerspective(canvas, M, (w, h))
    

    mask = warped > 0
    if mask.any(): frame[mask] = cv2.addWeighted(frame, 1-ALPHA, warped, ALPHA, 0)[mask]
    return frame

print("AR Text Projection - Started\nPress 'q' to quit")
count = 0

while True:
    msg = sock.recv()
    if cv2.waitKey(1) & 0xFF == ord("q"): break
    
    frame = cv2.imdecode(np.frombuffer(msg, np.uint8), -1)
    if frame is None: continue
    

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edged = cv2.Canny(cv2.GaussianBlur(gray, (5,5), 0), 75, 200)
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    paper = None
    for c in sorted(contours, key=cv2.contourArea, reverse=True):
        if cv2.contourArea(c) > 5000:
            approx = cv2.approxPolyDP(c, 0.02*cv2.arcLength(c,True), True)
            if len(approx)==4: paper = approx; break

    if paper is not None:
        cv2.drawContours(frame, [paper], -1, (0,255,0), 3)
        cv2.putText(frame, "Paper detected", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        frame = draw_text_perspective(frame, paper, TEXT, SCALE, COLOR, THICK)
    
    cv2.putText(frame, f"Count {count}", (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
    cv2.imshow("Stream", frame)
    count += 1

cv2.destroyAllWindows()