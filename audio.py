from flask import Flask, request
import os

app = Flask(__name__)

# Directory where the audio file will be saved
save_directory = r'C:\Users\aksml\Development\Hardware\Iot_Ignite\public'

@app.route('/save_audio', methods=['POST'])
def save_audio():
    file = request.files['file']
    if file:
        file_path = os.path.join(save_directory, "received_audio.wav")
        file.save(file_path)
        return "File saved successfully.", 200
    return "Failed to receive file.", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
