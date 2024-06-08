import cv2
import mediapipe as mp


class handDetector():
    """
    A class used to detect hands in an image using MediaPipe's hand tracking solution.

    Attributes
    ----------
    mode : bool
        A flag to indicate whether to treat the input images as a batch of static and possibly unrelated images, or a
         video stream.
    maxHands : int
        Maximum number of hands to detect.
    model_complexity : int
        Complexity of the hand tracking model. Could be 0, 1 or 2. Higher value increases the model complexity and
         accuracy.
    detectionCon : float
        Minimum confidence value ([0.0, 1.0]) for the hand detection to be considered successful.
    trackCon : float
        Minimum confidence value ([0.0, 1.0]) for the hand landmarks tracking to be considered successful.
    mpHands : object
        MediaPipe Hands solution object.
    hands : object
        MediaPipe Hands object with the specified parameters.
    mpDraw : object
        MediaPipe DrawingUtils object for drawing the hand landmarks and connections.

    Methods
    -------
    findHands(img, draw=True)
        Processes the image and finds the hand landmarks in it. If draw is True, draws the landmarks and connections on
        the image.
    findPosition(img, handNo=0, draw=True, color=(255, 0, 255), z_axis=False)
        Returns a list of the hand landmarks positions. If draw is True, draws the landmarks on the image.
    """

    def __init__(self, static_image_mode=False, max_num_hands=2, model_complexity=1, min_detection_confidence=0.5,
                 min_tracking_confidence=0.5):

        """
        Constructs all the necessary attributes for the handDetector object.

        Parameters
        ----------
            static_image_mode : bool, optional
                A flag to indicate whether to treat the input images as a batch of static and possibly unrelated images,
                 or a video stream (default is False).
            max_num_hands : int, optional
                Maximum number of hands to detect (default is 2).
            model_complexity : int, optional
                Complexity of the hand tracking model. Could be 0, 1 or 2. Higher value increases the model complexity
                 and accuracy (default is 1).
            min_detection_confidence : float, optional
                Minimum confidence value ([0.0, 1.0]) for the hand detection to be considered successful
                 (default is 0.5).
            min_tracking_confidence : float, optional
                Minimum confidence value ([0.0, 1.0]) for the hand landmarks tracking to be considered successful
                 (default is 0.5).
        """

        self.mode = static_image_mode
        self.maxHands = max_num_hands
        self.model_complexity = model_complexity
        self.detectionCon = min_detection_confidence
        self.trackCon = min_tracking_confidence
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.model_complexity, self.detectionCon,
                                        self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):

        """
        Processes the image and finds the hand landmarks in it. If draw is True, draws the landmarks and connections on
         the image.

        Parameters
        ----------
            img : np.array
                The input image.
            draw : bool, optional
                A flag to indicate whether to draw the landmarks and connections on the image (default is True).

        Returns
        -------
            img : np.array
                The image with the hand landmarks and connections drawn on it.
        """

        self.results = self.hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True, color=(255, 0, 255), z_axis=False):

        """
        Returns a list of the hand landmarks positions. If draw is True, draws the landmarks on the image.

        Parameters
        ----------
            img : np.array
                The input image.
            handNo : int, optional
                The index of the hand to find the landmarks for (default is 0).
            draw : bool, optional
                A flag to indicate whether to draw the landmarks on the image (default is True).
            color : tuple, optional
                The color to use for drawing the landmarks (default is (255, 0, 255)).
            z_axis : bool, optional
                A flag to indicate whether to include the z coordinate of the landmarks in the returned list
                 (default is False).

        Returns
        -------
            lmList : list
                A list of the hand landmarks positions.
        """

        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                if not z_axis:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])
                elif z_axis:
                    cx, cy, cz = int(lm.x * w), int(lm.y * h), round(lm.z, 3)
                    lmList.append([id, cx, cy, cz])
                if draw:
                    cv2.circle(img, (cx, cy), 5, color, cv2.FILLED)
        return lmList
