from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

import os
import imutils
import cv2
import time
UPLOAD_FOLDER = 'static/images/uploads' # folder where images are uploaded
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])
CONTENT_FILENAME = " "
STYLE_FILENAME = ""
TRY_NUMBER = 0

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

def model1(content_path,style_path):

    net = cv2.dnn.readNetFromTorch(style_path)

    # load the input image, resize it to have a width of 600 pixels, and
    # then grab the image dimensions
    image = cv2.imread(content_path)
    image = imutils.resize(image, width=600)
    (h, w) = image.shape[:2]

    # construct a blob from the image, set the input, and then perform a
    # forward pass of the network
    blob = cv2.dnn.blobFromImage(image, 1.0, (w, h),
            (103.939, 116.779, 123.680), swapRB=False, crop=False)
    start = time.time()
    net.setInput(blob)
    output = net.forward()
    end = time.time()
	# reshape the output tensor, add back in the mean subtraction, and
	# then swap the channel ordering
    output = output.reshape((3, output.shape[2], output.shape[3]))
    output[0] += 103.939
    output[1] += 116.779
    output[2] += 123.680
    #output /= 255.0
    output = output.transpose(1, 2, 0)
    print("[INFO] neural style transfer took {:.4f} seconds".format(
	end - start))
    return output


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app.debug = True
@app.route('/', methods = ['POST','GET'])
def index():
    image_files = []
    content_full_filename = ' '
    style_file_list = ["the_wave.jpg", "starry_night.jpg", "udnie.jpg", "la_muse.jpg", "the_scream.jpg", "composition.jpg"]
    if request.method == 'POST':

        file = request.files['file']

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('No selected file')
        #    return redirect(request.url)
    #        return redirect(request.url)
        if file and allowed_file(file.filename):
            global CONTENT_FILENAME
            CONTENT_FILENAME = secure_filename(file.filename)
            print(CONTENT_FILENAME)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], CONTENT_FILENAME))
        #    return redirect(url_for('uploaded_file',
        #                            filename=filename))
        user_answer = request.form['activity']

        print("user_answer", user_answer)
        content_full_filename = '../' + os.path.join(app.config['UPLOAD_FOLDER'], CONTENT_FILENAME)
        global STYLE_FILENAME
        global TRY_NUMBER
        TRY_NUMBER += 1
        STYLE_FILENAME = style_file_list[int(user_answer)]
    if request.method == 'GET':
        print("GET")
    return render_template ('index.html',  content_image = content_full_filename) #This line will render files from the folder templates


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

#This line is for the link About that you will use to go to about page
@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/result',methods = ['POST', 'GET'])
def result():

    if(CONTENT_FILENAME==" "):
        return "Empty"

    content_image = os.path.join(app.config['UPLOAD_FOLDER'], CONTENT_FILENAME)
    print(STYLE_FILENAME)
    style_filename = STYLE_FILENAME.split('.')
    style_filename1 = style_filename[0] + '.t7'
    style_image = os.path.join(app.config['UPLOAD_FOLDER'], style_filename1)
    print(style_image)
    print(content_image)
    generated_image = model1(content_image,style_image)
    try_number = str(TRY_NUMBER)
    #print(generated_image)
    cv2.imwrite('static/images/generated_image' + try_number + '.jpg', generated_image)

    if request.method == 'POST':
        result =  request.form
        return render_template('result.html', generated_image = '../' + "static/images/generated_image"  + try_number + ".jpg")


if __name__ == '__main__':
    app.run()
















	

