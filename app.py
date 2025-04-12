import os
import openai
from dotenv import load_dotenv
from flask import Flask,jsonify,request
from flask_cors import CORS

#load env file

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Initialize Flask app
app = Flask(__name__)
CORS(app=app)
app.config["UPLOAD_FOLDER"] = "static"

# main route
@app.route('/', methods=['GET'])
def main():
    return jsonify({"message": "Flask API is running!"})

@app.route("/audio-to-text-translate",methods=["POST"])
def audio_to_text_translate():
    language = request.form.get("language")
    file = request.files.get("file")
    
    if not file:
        return jsonify({"error": "No file provided"}),400
    if not language:
        return jsonify({"error": "No language provided"}),400
    filename = file.filename
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)
    try:
        with open(file_path,"rb") as audio_file:
            transcript = openai.Audio.translate("whisper-1",audio_file)
        response = openai.ChatCompletion.create(
            model = "gpt-4",
            messages = [{ "role": "system", "content": f"You will be provided with a sentence in English, and your task is to translate it into {language}" }, 
                                { "role": "user", "content": transcript.text }],
            temperature=0,
            max_tokens=256
        )
        translated_text = response['choices'][0]['message']['content']  
        return jsonify({"translation": translated_text})

    except Exception as e:
        return jsonify({"error":str(e)}),500


if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    app.run()
    # app.run(debug=True, host="0.0.0.0", port=8080)