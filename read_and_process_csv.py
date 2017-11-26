import time 
import requests
import cv2
import operator
import numpy as np
from flask import Flask, request, Response
import jsonpickle
import numpy as np
import cv2
import re

# Initialize the Flask application


# Import library to display results
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
# %matplotlib inline 
# Display images within Jupyter

app = Flask(__name__)

# Variables

_url = 'https://westcentralus.api.cognitive.microsoft.com/vision/v1.0/RecognizeText'
_key = "b3883e8ddecc4c13acbc625f3c2ef10b"  #Here you have to paste your primary key
_maxNumRetries = 10

def MS_processRequest( json, data, headers, params ):

    """
    Helper function to process the request to Project Oxford
a
    Parameters:
    json: Used when processing images from its URL. See API Documentation
    data: Used when processing image read from disk. See API Documentation
    headers: Used to pass the key information and the data type request
    """

    retries = 0
    result = None

    while True:
        response = requests.request( 'post', _url, json = json, data = data, headers = headers, params = params )

        if response.status_code == 429:
            print( "Message: %s" % ( response.json() ) )
            if retries <= _maxNumRetries: 
                time.sleep(1) 
                retries += 1
                continue
            else: 
                print( 'Error: failed after retrying!' )
                break
        elif response.status_code == 202:
            result = response.headers['Operation-Location']
        else:
            print( "Error code: %d" % ( response.status_code ) )
            print( "Message: %s" % ( response.json() ) )
        break
        
    return result

def MS_getOCRTextResult( operationLocation, headers ):
    """
    Helper function to get text result from operation location

    Parameters:
    operationLocation: operationLocation to get text result, See API Documentation
    headers: Used to pass the key information
    """

    retries = 0
    result = None

    while True:
        response = requests.request('get', operationLocation, json=None, data=None, headers=headers, params=None)
        if response.status_code == 429:
            print("Message: %s" % (response.json()))
            if retries <= _maxNumRetries:
                time.sleep(1)
                retries += 1
                continue
            else:
                print('Error: failed after retrying!')
                break
        elif response.status_code == 200:
            result = response.json()
        else:
            print("Error code: %d" % (response.status_code))
            print("Message: %s" % (response.json()))
        break

    return result

def showResultOnImage( result, img ):
    
    """Display the obtained results onto the input image"""
    img = img[:, :, (2, 1, 0)]
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.imshow(img, aspect='equal')

    lines = result['recognitionResult']['lines']
    # print lines
    for i in range(len(lines)):
        words = lines[i]['words']
        for j in range(len(words)):
            tl = (words[j]['boundingBox'][0], words[j]['boundingBox'][1])
            tr = (words[j]['boundingBox'][2], words[j]['boundingBox'][3])
            br = (words[j]['boundingBox'][4], words[j]['boundingBox'][5])
            bl = (words[j]['boundingBox'][6], words[j]['boundingBox'][7])
            text = words[j]['text']
            x = [tl[0], tr[0], tr[0], br[0], br[0], bl[0], bl[0], tl[0]]
            y = [tl[1], tr[1], tr[1], br[1], br[1], bl[1], bl[1], tl[1]]
            line = Line2D(x, y, linewidth=3.5, color='red')
            ax.add_line(line)
            ax.text(tl[0], tl[1] - 2, '{:s}'.format(text),
            bbox=dict(facecolor='blue', alpha=0.5),
            fontsize=14, color='white')

    plt.axis('off')
    plt.tight_layout()
    plt.draw()
    plt.show()

def extract_text_from_image(file_path, display_image_flag):
	# pathToFileInDisk = r'resources/receipt2.jpg'
	print("[*] performing text extraction from image")
	print("--- file path is: " + file_path)
	print("--- display_image_flag is set to: " + str(display_image_flag))
	with open(file_path, 'rb') as f:
	    data = f.read()

	# Computer Vision parameters
	params = {'handwriting' : 'true'}

	headers = dict()
	headers['Ocp-Apim-Subscription-Key'] = _key
	headers['Content-Type'] = 'application/octet-stream'

	json = None

	operationLocation = MS_processRequest(json, data, headers, params)

	result = None
	if (operationLocation != None):
	    headers = {}
	    headers['Ocp-Apim-Subscription-Key'] = _key
	    while True:
	        time.sleep(1)
	        result = MS_getOCRTextResult(operationLocation, headers)
	        if result['status'] == 'Succeeded' or result['status'] == 'Failed':
	            break

	# Load the original image, fetched from the URL
	if result is not None and result['status'] == 'Succeeded':
	    # print result
	    if (display_image_flag == True):
		    data8uint = np.fromstring(data, np.uint8)  # Convert string to an unsigned int array
		    img = cv2.cvtColor(cv2.imdecode(data8uint, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
		    showResultOnImage(result, img)
	    if(len(result) > 0):
		    print("--- characters detected")
		    return result


def parse_results(raw_detection):
	detected_words = []

	recognitionResult = raw_detection["recognitionResult"]

	for key, value in recognitionResult.iteritems():
		for entry in value:
			# print(entry[u'text'])
			for entry2 in entry[u'words']:
				# print(entry2[u'text'])
				detected_words.append(entry2[u'text'])
	return detected_words

def extract_total_due(detected_words):
	found_total = 0
	found_numbers = 0

	total_row = ""
	numeral_row = ""
	for entry in detected_words:
		entry = re.sub('[.,]', '', entry)
		if ('TOT' in entry.upper() and 'SUB' not in entry.upper() and found_total == 0):
			total_row = total_row + entry + " "
			found_total = 1

		if ('TOT' in entry.upper() and 'SUB' not in entry.upper() and found_total == 1):
			total_row = ""
			numeral_row = ""
			total_row = total_row + entry + " "
			found_numbers = 0
			found_total = 1

		elif (found_total == 1):
			if(entry.isdigit() == True):
				numeral_row = numeral_row + entry
				total_row = total_row + entry
				found_numbers = 1

		elif (found_numbers == 1):
			if(entry.isdigit != True):
				break
		else:
			None
	normalized = total_row
	if(len(numeral_row) >= 3):
		print len(numeral_row)
		print len(total_row)
		normalized = total_row[0:len(total_row)-2] + "." + total_row[len(total_row) - 2: len(total_row)]
	return normalized

def extract_dates(detected_words):
	# concatenated_string = ""
	# for entry in detected_words:
	# 	concatenated_string = concatenated_string + entry
	# intermediate1 = concatenated_string.split('/')
	# date1 = intermediate1[0][len(intermediate1)-3 : len(intermediate1)]
	# date2 = intermediate1[1]
	# date3 = intermediate1[2][0:5]

	# print date1, date2, date3
	detected_words = ''.join(detected_words)
	# print detected_words
	firstSlash = detected_words.index('/')
	secondSlash = detected_words.index('/', firstSlash + 1)
	# print detected_words[firstSlash - 2: secondSlash + 5]
	
	return detected_words[firstSlash - 2: secondSlash + 5]

# if __name__ == "__main__":
# 	file_path = "resources/receipt5.png"
# 	display_image_flag = True
# 	raw_detection = extract_text_from_image(file_path, display_image_flag)
# 	detected_words = parse_results(raw_detection)
# 	total_row = extract_total_due(detected_words)

# 	print total_row

@app.after_request
def apply_caching(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type"
    return response

@app.route('/api/test', methods=['POST'])
def test():
	content = request.files['image']
	content.save("temp.jpeg")
    
	# file_path = "resources/receipt5.png"
	display_image_flag = True
	raw_detection = extract_text_from_image("temp.jpeg", display_image_flag)
	detected_words = parse_results(raw_detection)
	total_row = extract_total_due(detected_words)
	detected_date = extract_dates(detected_words)

	unique = total_row + " " + detected_date


	return unique



# start flask app
app.run(host="127.0.0.1", port=5000)
