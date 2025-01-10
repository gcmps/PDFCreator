from flask import Flask, render_template, request, send_file
from PIL import Image
import os
from natsort import natsorted

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist('file')
    pdf_name = request.form.get('filename', 'file')
    enable_compression = 'compression' in request.form
    
    if not files:
        return "No files uploaded"
    
    images = []
    for file in files:
        if file and allowed_file(file.filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            images.append(filepath)
    
    images = natsorted(images)

    pdf_name = f"{pdf_name}.pdf"
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_name)
    
    try:
        image_objects = []
        for img in images:
            image = Image.open(img).convert('RGB')
            
            if enable_compression:
                image = image.convert('P', palette=Image.ADAPTIVE, colors=256)
            
            image_objects.append(image)
        
        first_image = image_objects.pop(0)
        first_image.save(pdf_path, save_all=True, append_images=image_objects)
        return send_file(pdf_path, as_attachment=True)
    
    except OSError:
        return "Error converting images to PDF, please ensure all files are valid image formats.", 400
    
    except Exception as e:
        return f"Error processing files: {e}"

if __name__ == '__main__':
    app.run(debug=True)
