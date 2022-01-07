import os
import cv2

import numpy as np
import time

import face_recognition


class FaceSearch:
    def __init__(self, query, source) -> None:

        if query=='C' or query=='capture':
            
            print("Capturing image in 3 seconds...")
            time.sleep(3)
            _, image = cv2.VideoCapture(0).read()
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        elif query.endswith('.jpg') or query.endswith('.png'):
            image = face_recognition.load_image_file(query)
        else:
            print("Query arguement is not valid")
            exit(1)

        self.encodeQueryFace(image)
        self.source = source
        
    
    def encodeQueryFace(self, image) -> None:
        face_locations = face_recognition.face_locations(image)
        self.query_face_encodings = face_recognition.face_encodings(image, face_locations)
        
        self.query_face_names = [f'face #{i}' for i in range(len(face_locations))]


    def liveSearch(self):

        video_capture = cv2.VideoCapture(0)
        process_this_frame = True

        while True:
            ret, frame = video_capture.read()
            
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # BGR to RGB
            image = small_frame[:, :, ::-1]

            if process_this_frame:
                face_locations, face_names = self.search(image)
            process_this_frame = not process_this_frame

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            cv2.imshow('Video', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video_capture.release()
        cv2.destroyAllWindows()


    def search(self, image):
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(self.query_face_encodings, face_encoding)
            name = "Unknown"

            # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                first_match_index = matches.index(True)
                name = self.query_face_names[first_match_index]

            # Or instead, use the query face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(self.query_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.query_face_names[best_match_index]

            face_names.append(name)

        return face_locations, face_names


    def directorySearch(self):
        import pandas as pd

        df = pd.DataFrame()
        for filename in os.listdir(self.source):
            if filename.endswith('.jpg') or filename.endswith('.png'):
                image = cv2.imread(os.path.join(self.source, filename))
                small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
                image = small_frame[:, :, ::-1]
                face_locations, face_names = self.search(image)                
                df = pd.concat([df, pd.Series(face_names, name=filename)], axis=1)
        
        df.to_csv('results.csv')
        return df

    def run(self):
        if self.source=='L' or self.source=='live':
            self.liveSearch()
        else:
            self.directorySearch()
