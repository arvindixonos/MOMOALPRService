import time
import sys
from multiprocessing import Process, Queue
from momoalprservice.alprservice import alprservice
import momoalprservice
import base64
from io import BytesIO
from PIL import Image

alprserviceinstance = alprservice()

inputqueue = Queue()
outputqueue = Queue()


if __name__ == '__main__':
    testprocess = Process(target=alprserviceinstance.startservice, args=(inputqueue, outputqueue))
    testprocess.start()

    with open("indiancar.jpg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        inputqueue.put(encoded_string)
        val = outputqueue.get()
        pass

    testprocess.join()

    time.sleep(100)

