from flask import Flask, request, jsonify
import os
from util import Sonify

app = Flask(__name__)

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        # Check if the request contains a file with the key 'image'
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files['image']

        # Check if the file has a valid file name
        if image_file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # You can save the image file to a specific location if needed
        # image_file.save('path/to/save/image.png')
        # Alternatively, you can process the image directly
        # For example, you can use a library like Pillow to work with the image
        # from PIL import Image
        # img = Image.open(image_file)

        return jsonify({"message": "Image uploaded successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    sonify = Sonify(image=image_file)
    sonify.run()
    result = sonify.output_video_path
    os.remove(result)
    return sendfile(result, as_attachment=True, mimetype='video/mp4')

    

if __name__ == '__main__':
    app.run(debug=True)