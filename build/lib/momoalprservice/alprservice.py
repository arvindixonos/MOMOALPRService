import base64

from momoservice import momoservice
from multiprocessing import Process, Queue
import os
import sys
from io import StringIO, BytesIO

from momoalprservice.ultimatealprsdk import ultimateAlprSdk

filepath = os.path.dirname(__file__)
sys.path.append("{}\\{}".format(filepath, "ultimatealprsdk"))
sys.path.append("{}\\{}".format(filepath, "ultimatealprsdkbinaries\\x86_64"))

import _ultimateAlprSdk
import argparse
import json
import platform
import os.path
from PIL import Image, ExifTags
import json
import sys


# EXIF orientation TAG
ORIENTATION_TAG = [orient for orient in ExifTags.TAGS.keys() if ExifTags.TAGS[orient] == 'Orientation']

# Defines the default JSON configuration. More information at https://www.doubango.org/SDKs/anpr/docs/Configuration_options.html
JSON_CONFIG = {
    "debug_level": "info",
    "debug_write_input_image_enabled": False,
    "debug_internal_data_path": ".",

    "num_threads": -1,
    "gpgpu_enabled": True,
    "max_latency": -1,

    "klass_vcr_gamma": 1.5,

    "detect_roi": [0, 0, 0, 0],
    "detect_minscore": 0.1,

    "car_noplate_detect_min_score": 0.8,

    "pyramidal_search_enabled": True,
    "pyramidal_search_sensitivity": 0.28,
    "pyramidal_search_minscore": 0.3,
    "pyramidal_search_min_image_size_inpixels": 800,

    "recogn_minscore": 0.3,
    "recogn_score_type": "min"
}

TAG = "[PythonRecognizer] "


class alprservice(momoservice.momoservice):

    def __init__(self):
        pass

    def checkResult(self, operation, result):
        if not result.isOK():
            print(TAG + operation + ": failed -> " + result.phrase())
            assert False
        else:
            print(TAG + operation + ": OK -> " + result.json())
        pass

    def runservice(self, image):
        # Decode the image
        image = Image.open('indiancar.jpg')
        width, height = image.size
        if image.mode == "RGB":
            format = ultimateAlprSdk.ULTALPR_SDK_IMAGE_TYPE_RGB24
        elif image.mode == "RGBA":
            format = ultimateAlprSdk.ULTALPR_SDK_IMAGE_TYPE_RGBA32
        elif image.mode == "L":
            format = ultimateAlprSdk.ULTALPR_SDK_IMAGE_TYPE_Y
        else:
            print(TAG + "Invalid mode: %s" % image.mode)
            assert False

        # Read the EXIF orientation value
        exif = image._getexif()
        exifOrientation = exif[ORIENTATION_TAG[0]] if len(ORIENTATION_TAG) == 1 and exif != None else 1

        # Update JSON options using values from the command args
        JSON_CONFIG["assets_folder"] = "assets/"
        JSON_CONFIG["charset"] = "latin"

        # Initialize the engine
        self.checkResult("Init", ultimateAlprSdk.UltAlprSdkEngine_init(json.dumps(JSON_CONFIG)))

        result = ultimateAlprSdk.UltAlprSdkEngine_process(
            format,
            image.tobytes(),  # type(x) == bytes
            width,
            height,
            0,  # stride
            exifOrientation)

        jsoned = json.loads(result.json())

        retdict = {}

        if len(jsoned['plates']) > 0:
            print("Number is: {}".format(jsoned['plates'][0]['text']))
            retdict['licence_number'] = jsoned['plates'][0]['text']
        else:
            print("NUMBER NOT FOUND")

        return json.dumps(retdict)


    def startservice(self, inputqueue, outputqueue):
        super().startservice(inputqueue, outputqueue)

        imagestring = inputqueue.get()

        img = Image.open(BytesIO(base64.b64decode(imagestring)))

        resultJSON = self.runservice(img)

        outputqueue.put(resultJSON)

        pass
