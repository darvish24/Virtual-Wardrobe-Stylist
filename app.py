# import os
# import cvzone
# import cv2
# from cvzone.PoseModule import PoseDetector

# # 1. Initialize Webcam
# cap = cv2.VideoCapture(0)
# cap.set(3, 1280)
# cap.set(4, 720)

# detector = PoseDetector()

# # 2. Setup Paths and Resources
# shirtFolderPath = "Resources/Shirts"
# listShirts = os.listdir(shirtFolderPath)
# print(f"Shirts found: {listShirts}")

# # Ratios and variables
# fixedRatio = 262 / 190  # Ratio of Shirt Width / Shoulder Width
# shirtRatioHeightWidth = 581 / 440
# imageNumber = 0

# while True:
#     success, img = cap.read()
#     if not success:
#         break
    
#     # Flip the image horizontally for a "Mirror" effect
#     img = cv2.flip(img, 1)

#     # Detect Pose
#     img = detector.findPose(img)
#     lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False, draw=False)

#     if lmList:
#         # Get Shoulder Coordinates
#         lm11 = lmList[11][0:2] # Left Shoulder
#         lm12 = lmList[12][0:2] # Right Shoulder
        
#         # --- SHIRT OVERLAY LOGIC ---
        
#         # Load current shirt
#         imgShirt = cv2.imread(os.path.join(shirtFolderPath, listShirts[imageNumber]), cv2.IMREAD_UNCHANGED)

#         widthOfShoulders = int(abs(lm11[0] - lm12[0]))
#         widthOfShirt = int(widthOfShoulders * fixedRatio)
        
#         if widthOfShirt > 0:
#             # Resize Shirt
#             heightOfShirt = int(widthOfShirt * shirtRatioHeightWidth)
#             imgShirt = cv2.resize(imgShirt, (widthOfShirt, heightOfShirt))

#             # Calculate Center point
#             currentScale = widthOfShoulders / 190
#             offsetX = int(44 * currentScale) 
#             offsetY = int(48 * currentScale)

#             mid_shoulder_x = (lm11[0] + lm12[0]) // 2
#             shirt_x = mid_shoulder_x - widthOfShirt // 2
#             shirt_y = lm11[1] - offsetY

#             try:
#                 img = cvzone.overlayPNG(img, imgShirt, (shirt_x, shirt_y))
#             except Exception as e:
#                 pass

#     # --- UI & MANUAL CONTROLS ---
    
#     # Display instructions on screen
#     cv2.putText(img, "Press 'D' for Next, 'A' for Previous", (50, 50), 
#                 cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

#     cv2.imshow("Virtual Try-On", img)
    
#     # Key Handling
#     key = cv2.waitKey(1) & 0xFF
    
#     if key == ord('d'): # Next Shirt
#         if imageNumber < len(listShirts) - 1:
#             imageNumber += 1
#             print("Next Shirt")
            
#     elif key == ord('a'): # Previous Shirt
#         if imageNumber > 0:
#             imageNumber -= 1
#             print("Previous Shirt")
            
#     elif key == ord('q'): # Quit
#         break

# cap.release()
# cv2.destroyAllWindows()


from flask import Flask, render_template, Response, request, jsonify
import cv2
import cvzone
from cvzone.PoseModule import PoseDetector
import os

app = Flask(__name__)

# --- CONFIGURATION ---
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = PoseDetector()

shirtFolderPath = "Resources/Shirts"
listShirts = os.listdir(shirtFolderPath)
fixedRatio = 262 / 190  
shirtRatioHeightWidth = 581 / 440

# Global variables to control state from the web
global_state = {
    "image_number": 0
}

def generate_frames():
    """Video streaming generator function."""
    while True:
        success, img = cap.read()
        if not success:
            break
            
        img = cv2.flip(img, 1)

        # --- EXISTING POSE & OVERLAY LOGIC ---
        img = detector.findPose(img)
        lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False, draw=False)

        if lmList:
            lm11 = lmList[11][0:2]
            lm12 = lmList[12][0:2]
            
            # Use the global image number
            current_shirt_index = global_state["image_number"]
            imgShirt = cv2.imread(os.path.join(shirtFolderPath, listShirts[current_shirt_index]), cv2.IMREAD_UNCHANGED)
            
            # Dynamic Ratio Calculation
            current_h, current_w, _ = imgShirt.shape
            shirtRatioHeightWidth = current_h / current_w

            widthOfShoulders = int(abs(lm11[0] - lm12[0]))
            widthOfShirt = int(widthOfShoulders * fixedRatio)
            
            if widthOfShirt > 0:
                imgShirt = cv2.resize(imgShirt, (widthOfShirt, int(widthOfShirt * shirtRatioHeightWidth)))
                currentScale = widthOfShoulders / 190
                offsetY = int(48 * currentScale)

                mid_shoulder_x = (lm11[0] + lm12[0]) // 2
                shirt_x = mid_shoulder_x - widthOfShirt // 2
                shirt_y = lm11[1] - offsetY

                try:
                    img = cvzone.overlayPNG(img, imgShirt, (shirt_x, shirt_y))
                except Exception:
                    pass

        # --- ENCODE IMAGE FOR WEB ---
        # Instead of cv2.imshow, we encode the frame as a JPEG byte stream
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        
        # Yield the frame in a format the browser understands (MJPEG)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/change_shirt', methods=['POST'])
def change_shirt():
    """API to change the shirt via button click"""
    data = request.json
    action = data.get('action')
    
    current = global_state["image_number"]
    
    if action == "next":
        if current < len(listShirts) - 1:
            global_state["image_number"] += 1
    elif action == "prev":
        if current > 0:
            global_state["image_number"] -= 1
            
    return jsonify({"current_index": global_state["image_number"]})

if __name__ == '__main__':
    # Run the app
    app.run(debug=True)