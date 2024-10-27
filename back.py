from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import pygame
from dotenv import load_dotenv
import google.generativeai as gai
from PIL import Image
from gtts import gTTS

# Initialize Flask app
app = Flask(__name__)

# Directory to save images, text, and audio files
save_directory = r'C:\Users\aksml\Development\Hardware\Iot_Ignite\public'

# Ensure the directory exists, if not, create it
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

# Load environment variables
load_dotenv()

# Configure the Google Generative AI API
gai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Create a model instance
model = gai.GenerativeModel("gemini-1.5-flash-latest")
chat = model.start_chat(history=[])

# Store the last switch state globally as a boolean
switch_state = False

# Function to play audio when the state is toggled to True
def play_audio():
    audio_path = os.path.join(os.path.dirname(__file__), 'public', 'audio.wav')
    if os.path.exists(audio_path):
        pygame.mixer.init()
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
    else:
        print("Audio file not found!")

# Function to process the image using Gemini model
def gemini_img_bot(image_path):
    # Open the image
    image = Image.open(image_path)

    input_message = "Describe the image for blind people short and clear within 75-80 words."
    
    response = chat.send_message([input_message, image]) 
    
    return response.text

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return "No image file found in the request.", 400

    image_file = request.files['image']
    if image_file.filename == '':
        return "No selected file.", 400

    image_path = os.path.join(save_directory, 'input.jpg')

    image_file.save(image_path)
    print(f"Image received and saved to {image_path}")

    response_text = gemini_img_bot(image_path)

    output_text_path = os.path.join(save_directory, "output.txt")
    with open(output_text_path, "w") as f:
        f.write(response_text)

    output_audio_path = os.path.join(save_directory, "output.mp3")
    tts = gTTS(text=response_text, lang='en')
    tts.save(output_audio_path)

    audio_url = f'http://192.168.55.200:5000/audio/output.mp3'
    text_url = f'http://192.168.55.200:5000/text/output.txt'

    return jsonify({
        "message": "Image successfully processed.",
        "description": response_text,
        "text_file": text_url,
        "audio_file": audio_url
    }), 200

# Route to serve the audio file
@app.route('/audio/<filename>', methods=['GET'])
def serve_audio(filename):
    return send_from_directory(save_directory, filename)

# Route to serve the text file
@app.route('/text/<filename>', methods=['GET'])
def serve_text(filename):
    return send_from_directory(save_directory, filename)

# Route to update the switch state and play audio when necessary
@app.route('/update', methods=['POST'])
def update():
    global switch_state
    data = request.get_json()
    if 'state' in data:
        new_state = True if data['state'] == "True" else False
        if new_state and not switch_state:  
            print("Switch State Updated to True - Playing Audio")
            play_audio()
        switch_state = new_state  
        return jsonify({'status': 'success', 'message': f'State updated to {switch_state}'}), 200
    return jsonify({'status': 'failed', 'message': 'Invalid data'}), 400


@app.route('/state')
def state():
    global switch_state
    return jsonify({'switch_state': switch_state})  

@app.route('/')
def index():
    return render_template('index.html')  

if __name__ == '__main__':
    pygame.init()
    app.run(host='0.0.0.0', port=5000) 