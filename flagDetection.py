import numpy as np
import cv2
import tensorflow as tf
import os
from models.research.object_detection.utils import label_map_util
from models.research.object_detection.utils import visualization_utils as vis_util

import Video_Capture

class FlagDetectionModule:

    def __init__(self):
        self.detectedReferenceFlag  = None
        self.isReferenceFlagDetected = False
        self.imageWarpingSize = (128, 128)

        self.L2Norm = 0

        # Grab path to current working directory
        CWD_PATH = os.getcwd()
        # Path to frozen detection graph .pb file, which contains the model that is used
        # for object detection.
        PATH_TO_CKPT = os.path.join(CWD_PATH,'IG','frozen_inference_graph.pb')
        # Path to label map file
        PATH_TO_LABELS = os.path.join(CWD_PATH,'IG','label.pbtxt')
        # Number of classes the object detector can identify
        NUM_CLASSES = 1

        # Load the label map.
        label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
        category_index = label_map_util.create_category_index(categories)


        # Load the Tensorflow model into memory.
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

            self.sess = tf.Session(graph=self.detection_graph)

        # Define input and output tensors (i.e. data) for the object detection classifier

        # Input tensor is the image
        self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')

        # Output tensors are the detection boxes, scores, and classes
        # Each box represents a part of the image where a particular object was detected
        self.detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')

        # Each score represents level of confidence for each of the objects.
        # The score is shown on the result image, together with the class label.
        self.detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')

        # Number of objects detected
        self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')


    def detectReferenceFlag(self, image):
        """Detect the reference flag. If a there is a valid detection,
        set the corresponding flag."""
        detectedFlags = self.performDetection(image)
        if len(detectedFlags):
            maxScore = 0
            idx = 0
            for i in range(len(detectedFlags)):
                if detectedFlags[i][0] > maxScore:
                    maxScore = detectedFlags[i][0]
                    idx = i
            y1 = detectedFlags[idx][1]
            x1 = detectedFlags[idx][2]
            y2 = detectedFlags[idx][3]
            x2 = detectedFlags[idx][4]

            self.detectedReferenceFlag = image[y1:y2,x1:x2].copy()
            self.isReferenceFlagDetected = True
        return self.isReferenceFlagDetected

    def detectCandidateFlag(self, image):
        """Detect the reference flag. If a there is a valid detection,
        set the corresponding flag."""
        if not self.isReferenceFlagDetected:
            return []

        detectedFlags = self.performDetection(image)

        if len(detectedFlags):
            flags = []
            for i in range(len(detectedFlags)):
                y1 = detectedFlags[i][1]
                x1 = detectedFlags[i][2]
                y2 = detectedFlags[i][3]
                x2 = detectedFlags[i][4]

                crop = image[y1:y2,x1:x2].copy()
                flags.append(crop)
            idx = self.matchFlags(self.detectedReferenceFlag, flags)

            if idx != -1 and idx < len(detectedFlags):
                return(detectedFlags[idx][1:])
            else:
                return []

    def performDetection(self, image):
        """This function performs detection of the flag using faster RCNN.
        Two levels of detections are done to get the best output."""
        image_expanded = np.expand_dims(image, axis=0)
        (boxes, scores, classes, num) = self.sess.run(
            [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: image_expanded})

        detectedFlags = []
        #print("S: " ,scores)
        for i in range(len(scores[0])):

            if scores[0][i] > 0.5:
                y1 = int(boxes[0][i][0] * 480)
                x1 = int(boxes[0][i][1] * 640)
                y2 = int(boxes[0][i][2] * 480)
                x2 = int(boxes[0][i][3] * 640)

                if y2-y1 <10 and x2- x1 < 10:
                    continue
                else:
                    detectedFlags.append([scores[0][i],y1,x1,y2,x2])

        return detectedFlags

    def resizeToWarpingsize(self, image):
        """Warps the image to the predefined size"""
        warpedImage = cv2.resize(image, self.imageWarpingSize)
        return warpedImage


    def calculateL2Norm(self, flag1, flag2):
        """Calculates the L2 norm between the two warped images"""

        # Vectorize the Flags
        vectorizedFlag1 = flag1.flatten()
        vectorizedFlag2 = flag2.flatten()

        # Calculate normalized vectors
        if np.std(vectorizedFlag1) == 0.0:
            stdDevFalg1 = 1
        else:
            stdDevFalg1 = np.std(vectorizedFlag1)

        if np.std(vectorizedFlag2) == 0.0:
            stdDevFalg2 = 1
        else:
            stdDevFalg2 = np.std(vectorizedFlag2)

        normalizedFlag1 = (vectorizedFlag1-np.mean(vectorizedFlag1))/stdDevFalg1
        normalizedFlag2 = (vectorizedFlag2-np.mean(vectorizedFlag2))/stdDevFalg2

        # Calculate L2-Norm
        self.L2Norm = np.sqrt(np.sum(np.square(normalizedFlag1.__sub__(normalizedFlag2))))

        return self.L2Norm


    def matchFlags(self, referenceFlag, candidateFlags):
        """Match the flags based on L2-norm. Candidate Flags is a list
        of all the flags that needs to matched with the reference
        flag. All the flags are warped to (128, 128) before calculating
        L2-norm."""

        # Make sure reference flag and candidate flags are valid
        if self.isReferenceFlagDetected and len(candidateFlags) != 0:
            L2_error = []

            # Warp the images to same size
            warpedReferenceImage = self.resizeToWarpingsize(referenceFlag)

            # Match all the candidate flags and store the scores
            for candidateFlag in candidateFlags:
                warpedCandidateFlag = self.resizeToWarpingsize(candidateFlag)
                L2_error.append(self.calculateL2Norm(warpedReferenceImage, warpedCandidateFlag))

            # Choose the one with minimum error
            if min(L2_error) < 200:
                index = L2_error.index(min(L2_error))
            else:
                return -1
            return index
        else:
            return -1

if __name__=='__main__':

    #video = Video_Capture.MyVideoCapture(0, True, 'fpv')
    #video.start()
    cap = cv2.VideoCapture(0)
    inst = FlagDetectionModule()
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            val = inst.detectReferenceFlag(frame)
            print(val)

            # Display the resulting frame
            cv2.imshow('Frame', frame)

            # Press Q on keyboard to  exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()