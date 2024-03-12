from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from imutils.video import VideoStream
import numpy as np
import imutils
import time
import cv2
from twilio.rest import Client
from pyngrok import ngrok

class MaskPredict():
    # predicts if someone is wearing a mask
    def __init__(self, type, confidence):
        self.confidence = confidence
        self.type = type
        if self.type is None:
            self.type = "Only Thief"
        # self.twiml_url = "https://pastebin.com/raw/TwcRgfPL"
        self.url = ngrok.connect(5000)
        self.url_string = str(self.url).split("\"")[1] + "/upload/frame.jpg"
        # print(self.url_string)
        self.client = Client() # REMOVED SECRET KEYS

    def detect_and_predict_mask(self, frame, faceNet, maskNet):
    	(h, w) = frame.shape[:2]
    	blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300),
    		(104.0, 177.0, 123.0)) 

    	faceNet.setInput(blob)
    	detections = faceNet.forward()

    	faces = []
    	locs = []
    	preds = []

    	for i in range(0, detections.shape[2]):
    		confidence = detections[0, 0, i, 2]

    		if confidence > self.confidence:
    			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
    			(startX, startY, endX, endY) = box.astype("int")

    			(startX, startY) = (max(0, startX), max(0, startY))
    			(endX, endY) = (min(w - 1, endX), min(h - 1, endY))

    			face = frame[startY:endY, startX:endX]
    			face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
    			face = cv2.resize(face, (224, 224))
    			face = img_to_array(face)
    			face = preprocess_input(face)
    			face = np.expand_dims(face, axis=0)

    			faces.append(face)
    			locs.append((startX, startY, endX, endY))

    	if len(faces) > 0:
            if self.type == "Anyone who comes to my door":
                return True
            else:
                preds = maskNet.predict(faces)

    	return (locs, preds)

    def detect(self):
        prototxtPath = "src/deploy.prototxt"
        weightsPath = "src/res10_300x300_ssd_iter_140000.caffemodel"
        faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)

        maskNet = load_model("src/model.h5")

        vs = VideoStream(src=0).start()
        time.sleep(2.0)

        while True:
            frame = vs.read()
            frame = imutils.resize(frame, width=400)

            if self.type == "Anyone who comes to my door":
                self.pred = self.detect_and_predict_mask(frame, faceNet, maskNet)
                if self.pred:
                    cv2.imwrite("src/GUI/app/static/frame.jpg", frame)
                    msg = self.client.messages.create(to='', from_='', body=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " - Someone is at your door!", media_url=self.url_string)
                    # taken out phone numbers
                    vs.stop()
                    return [True, "person"]
            else:
                (locs, preds) = self.detect_and_predict_mask(frame, faceNet, maskNet)

                for (box, pred) in zip(locs, preds):
                    (startX, startY, endX, endY) = box
                    (mask, withoutMask) = pred

                    bool = True if mask > withoutMask else False

                    if bool:
                        cv2.imwrite("src/GUI/app/static/frame.jpg", frame)
                        msg = self.client.messages.create(to='', from_='', body=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " - A possible thief has been detected at your door!", media_url=self.url_string)
                        # taken out phone numbers
                        vs.stop()
                        return [True, "thief"]
