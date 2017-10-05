import os
from flask import Flask, request, redirect, url_for
from flask import send_from_directory, render_template, jsonify
from flask import flash
from werkzeug.utils import secure_filename
import ios_resize
import config

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            app.logger.info('No file part')
            return jsonify({'error' : 'You must provide a file'})
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return jsonify({'error' : 'You must provide a valid file'})
            return redirect(request.url)
        if file and allowed_file(file.filename):
            ##im = Image.open(file)
            ##im = im.resize((128, 128))
            ##filename = os.path.join(app.config['UPLOAD_FOLDER'], "filename.png")
            ##im.save(filename)

            #filename = secure_filename(file.filename)
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            app.logger.info('Processing File')

            icon_id = ios_resize.resize(file)
            
            return jsonify({'icon_id' : icon_id})
        else:
            return jsonify({'error' : 'Allowed files are PNG, JPG and JPEG'})

    return render_template('index.html')

@app.route('/icons/<id>')
def icons(id):
    icon_url = url_for('generated_icons', id=id, name=config.ITUNES_ARTWORK_NAME)
    zip_url = url_for('generated_icons', id=id, name=config.IOS_APPICONSET_NAME)
    return render_template('icon.html', icon=icon_url, zip=zip_url)

@app.route('/uploads/icons/<id>/<name>')
def generated_icons(id, name):
    path = os.path.join(app.config['UPLOAD_FOLDER'], id)
    return send_from_directory(path, name)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4343, debug=True)
