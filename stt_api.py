import os
import tempfile

from flask import Flask, request, jsonify
from flask_cors import CORS
from sarvamai import SarvamAI

app = Flask(__name__)

# Allow the SIH frontend to call this API
CORS(app)

# Limit uploaded audio to 20 MB
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


# --------------------------------------------------
# SARVAM CONFIGURATION
# --------------------------------------------------

API_KEY = os.environ.get("SARVAM_API_KEY")

API_KEY = "sk_o7traexv_jZJHv9LCBg2DkK6P6Dvu5CKR"

client = SarvamAI(
    api_subscription_key=API_KEY
)

MODEL = "saaras:v3"


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/api/health")
def health():

    return jsonify({
        "success": True,
        "status": "ok",
        "service": "SIH Speech-to-Text",
        "model": MODEL
    })


# --------------------------------------------------
# SPEECH TO TEXT
# --------------------------------------------------

@app.post("/api/transcribe")
def transcribe():

    # Check whether frontend sent audio
    if "audio" not in request.files:

        return jsonify({
            "success": False,
            "error": "No audio received"
        }), 400

    audio = request.files["audio"]

    # Empty upload check
    if not audio or audio.filename == "":

        return jsonify({
            "success": False,
            "error": "Empty audio file"
        }), 400

    # Language can be supplied by frontend.
    # "unknown" = automatic language detection.
    language_code = request.form.get(
        "language_code",
        "unknown"
    )

    # Only allow supported language values
    supported_languages = {
        "unknown",
        "en-IN",
        "te-IN",
        "hi-IN",
        "ta-IN",
        "kn-IN",
        "ml-IN",
        "mr-IN",
        "bn-IN",
        "gu-IN",
        "pa-IN",
        "od-IN",
        "as-IN",
        "ur-IN",
        "ne-IN",
        "kok-IN",
        "ks-IN",
        "sd-IN",
        "sa-IN",
        "sat-IN",
        "mni-IN",
        "brx-IN",
        "mai-IN",
        "doi-IN"
    }

    if language_code not in supported_languages:

        return jsonify({
            "success": False,
            "error": "Unsupported language code"
        }), 400

    temp_path = None

    try:

        # --------------------------------------------------
        # CREATE TEMPORARY AUDIO FILE
        # --------------------------------------------------
        #
        # IMPORTANT:
        # We do NOT depend on a filename such as r6.m4a.
        #
        # The browser can send a new recording every time.
        #

        original_name = audio.filename.lower()


        if original_name.endswith(".m4a"):
            suffix = ".m4a"

        elif original_name.endswith(".wav"):
            suffix = ".wav"

        elif original_name.endswith(".mp3"):
            suffix = ".mp3"

        elif original_name.endswith(".webm"):
            suffix = ".webm"
        elif original_name.endswith(".ogg"):
            suffix = ".ogg"


        else:
            suffix = ".webm"

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:

            audio.save(temp_file.name)
            temp_path = temp_file.name


        # --------------------------------------------------
        # SEND AUDIO TO SARVAM
        # --------------------------------------------------

        with open(temp_path, "rb") as audio_file:

            response = client.speech_to_text.transcribe(
                file=audio_file,
                model=MODEL,
                mode="transcribe",
                language_code=language_code
            )


        # --------------------------------------------------
        # GET TEXT
        # --------------------------------------------------

        transcript = response.transcript
        detected_language = response.language_code


        # --------------------------------------------------
        # DELETE TEMPORARY AUDIO
        # --------------------------------------------------

        if os.path.exists(temp_path):
            os.remove(temp_path)

            temp_path = None


        # --------------------------------------------------
        # SEND RESULT TO FRONTEND
        # --------------------------------------------------

        return jsonify({

            "success": True,

            "text": transcript,

            "language": detected_language,

            "model": MODEL

        })


    except Exception as e:

        # Always remove temporary audio
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        print("STT ERROR:", str(e))

        return jsonify({

            "success": False,

            "error": "Speech recognition failed",

            "details": str(e)

        }), 500


# --------------------------------------------------
# SERVER
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 50)
    print("SIH MULTILINGUAL SPEECH-TO-TEXT")
    print("=" * 50)
    print("Model :", MODEL)
    print("API   : http://127.0.0.1:5000")
    print("=" * 50)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )