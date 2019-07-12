import threading
import logging
import TCP_Server
import Image_Recognition
import Jarvis
import GUI
import cv2
import time

def main():

    server = TCP_Server.MAVServer("localhost", 9999)
    #image = Image_Recognition.MAVImageRecognition(server)
    #jarvis = Jarvis.Jarvis(server, image)
    gui = GUI.GUI(server)

    logging.info("RUNNING SERVER")
    server_thread = threading.Thread(target=TCP_Server.main, args=(server,))
    """
    logging.info("RUNNING IMAGE RECOGNITION")
    image_thread = threading.Thread(target=Image_Recognition.main, args=(image,))
    logging.info("RUNNING JARVIS")
    jarvis_thread = threading.Thread(target=Jarvis.main, args=(jarvis,))
    """
    logging.info("RUNNING GUI")
    gui_thread = threading.Thread(target=GUI.main, args=(gui,))

    server_thread.start()

    while not server.server_started:
        time.sleep(0.1)
    gui_thread.start()
    """
    image_thread.start()
    jarvis_thread.start()

    jarvis_thread.join()
    image_thread.join()
    """
    server_thread.join()
    gui_thread.join()

if __name__ == "__main__":
    # logging.basicConfig(filename="log.log", filemode="w", format='%(levelname)s:%(message)s', level=logging.INFO)
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    main()
