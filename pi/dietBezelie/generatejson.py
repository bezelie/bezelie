#!/usr/bin/env python

# Copyright 2016 Google, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''This script generates request JSON for the Vision API.
Run the script using the following command:

  python generatejson.py \
      -i <input_file> \
      -o <output_file.json>

where the input file contains information on how to process a set of URIs, and
the output is a JSON request file.

The Python script reads an input text file that contains one line for each
image to process. Each line in the input file contains the URI of an image--for
example, its file location--and a space-separated list of
Feature:max_results to request for the image. The script associates each
Feature with an integer value from 1-6 (see the 'get_detection_type' function
definition).

For example, the following input file content requests face and label
detection annotations for image1, and landmark and logo detection annotations
for image2; each with a maximum of 10 results per annotation.

filepath_to_image1.jpg 1:10 4:10
filepath_to_image2.png 2:10 3:10

See https://cloud.google.com/vision/docs/concepts for more detail, and for
information on using the generated result to send a request to the Vision API.
'''
# [START generate_json]
import argparse
import base64
import json
import sys


def imageRecog(input_file):    
    request_list = []
    try:
        with open(input_file, 'r') as inputfile:                        
            for line in inputfile:
        # The first value of a line is the image. The rest are features.
                image_filename, features = line.lstrip().split(' ', 1)
        # First, get the image data
                with open(image_filename, 'rb') as image_file:
                    content_json_obj = {
                        'content': base64.b64encode(image_file.read()).decode('UTF-8')}

        # Then parse out all the features we want to compute on this image
                feature_json_obj = []
                for word in features.split(' '):
                    feature, max_results = word.split(':', 1)
                    feature_json_obj.append({
                        'type': get_detection_type(feature),
                        'maxResults': int(max_results),
                    })

                request_list.append({
                    'features': feature_json_obj,
                    'image': content_json_obj,
                })

    # Write the object to a file, as json
            return (json.dumps({'requests': request_list}))
    except ValueError as e:
        sys.exit('Invalid input file format.\n' + FILE_FORMAT_DESCRIPTION)

DETECTION_TYPES = [
    'TYPE_UNSPECIFIED',
    'FACE_DETECTION',
    'LANDMARK_DETECTION',
    'LOGO_DETECTION',
    'LABEL_DETECTION',
    'TEXT_DETECTION',
    'SAFE_SEARCH_DETECTION',
]


def get_detection_type(detect_num):
    detect_num = int(detect_num)
    if 0 < detect_num < len(DETECTION_TYPES):
        return DETECTION_TYPES[detect_num]
    else:
        return DETECTION_TYPES[0]
# [END generate_json]

FILE_FORMAT_DESCRIPTION = '''
Each line in the input file must be of the form:

    file_path feature:max_results feature:max_results ....

where 'file_path' is the path to the image file you'd like
to annotate, 'feature' is a number from 1 to %s,
corresponding to the feature to detect, and max_results is a
number specifying the maximum number of those features to
detect.

The valid values - and their corresponding meanings - for
'feature' are:

    %s
'''.strip() % (
    len(DETECTION_TYPES) - 1,
    # The numbered list of detection types
    '\n    '.join(
        # Don't present the 0th detection type ('UNSPECIFIED') as an option.
        '%s: %s' % (i + 1, detection_type)
        for i, detection_type in enumerate(DETECTION_TYPES[1:])))



