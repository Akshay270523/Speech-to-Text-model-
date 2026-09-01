import sounddevice as sd
import numpy as np
import requests
import tempfile
import os
import time
import noisereduce as nr

from scipy.io.wavfile import write


# ==================================================
# CONFIGURATION
# ==================================================

API_URL = "http://127.0.0.1:5000/api/transcribe"

SAMPLE_RATE = 16000
CHANNELS = 1

CHUNK_DURATION = 0.1
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)

# Wait this long after the user stops speaking
SILENCE_DURATION = 1.8

# Accept short words such as:
# "Hi", "Bye", "Okay", etc.
MIN_SPEECH_DURATION = 0.2

# Keep audio immediately before speech starts
PRE_BUFFER_DURATION = 0.5

PRE_BUFFER_CHUNKS = int(
    PRE_BUFFER_DURATION / CHUNK_DURATION
)

# Noise calibration
NOISE_CALIBRATION_TIME = 1.5

# Minimum threshold so normal microphone noise
# doesn't trigger speech detection
MIN_THRESHOLD = 350

# How much louder than background noise
# the speech should be
NOISE_MULTIPLIER = 2.0


# ==================================================
# AUDIO LEVEL
# ==================================================

def audio_level(audio):

    audio = audio.astype(np.float32)

    return np.sqrt(
        np.mean(audio ** 2)
    )


# ==================================================
# BACKGROUND NOISE CALIBRATION
# ==================================================

def calibrate_noise():

    print()
    print("🔇 Calibrating microphone...")
    print("Please stay silent for 1.5 seconds.")

    samples = []

    number_of_chunks = int(
        NOISE_CALIBRATION_TIME /
        CHUNK_DURATION
    )

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
        blocksize=CHUNK_SIZE
    ) as stream:

        for _ in range(number_of_chunks):

            data, overflowed = stream.read(
                CHUNK_SIZE
            )

            if overflowed:
                continue

            samples.append(
                data[:, 0].copy()
            )

    if not samples:

        print(
            "⚠️ Microphone calibration failed."
        )

        return MIN_THRESHOLD

    noise_audio = np.concatenate(
        samples
    )

    noise_level = audio_level(
        noise_audio
    )

    threshold = max(
        MIN_THRESHOLD,
        noise_level * NOISE_MULTIPLIER
    )

    print(
        f"Background level : {noise_level:.0f}"
    )

    print(
        f"Speech threshold  : {threshold:.0f}"
    )

    print(
        "✅ Noise calibration complete."
    )

    return threshold


# ==================================================
# RECORD ONE SPEECH TURN
# ==================================================

def record_speech(threshold):

    print()
    print("🎤 Listening...")

    frames = []

    pre_buffer = []

    speech_started = False

    silence_time = 0.0

    speech_time = 0.0

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
        blocksize=CHUNK_SIZE
    ) as stream:

        while True:

            data, overflowed = stream.read(
                CHUNK_SIZE
            )

            if overflowed:
                continue

            audio = data[:, 0].copy()

            level = audio_level(
                audio
            )

            # --------------------------------------
            # BEFORE SPEECH
            # --------------------------------------

            if not speech_started:

                pre_buffer.append(
                    audio
                )

                if len(pre_buffer) > PRE_BUFFER_CHUNKS:

                    pre_buffer.pop(0)

                if level > threshold:

                    speech_started = True

                    silence_time = 0.0

                    frames.extend(
                        pre_buffer
                    )

                    speech_time += (
                        len(pre_buffer)
                        * CHUNK_DURATION
                    )

                    print(
                        "🗣️",
                        end="",
                        flush=True
                    )

                continue

            # --------------------------------------
            # SPEECH CONTINUES
            # --------------------------------------

            if level > threshold:

                silence_time = 0.0

                speech_time += (
                    CHUNK_DURATION
                )

                frames.append(
                    audio
                )

                print(
                    "🗣️",
                    end="",
                    flush=True
                )

            # --------------------------------------
            # POSSIBLE SILENCE
            # --------------------------------------

            else:

                frames.append(
                    audio
                )

                silence_time += (
                    CHUNK_DURATION
                )

                # Wait 1.8 seconds of silence
                # before ending the turn
                if silence_time >= SILENCE_DURATION:

                    break

    print()
    print("⏹️ Speech finished.")

    # ------------------------------------------
    # MINIMUM SPEECH CHECK
    # ------------------------------------------

    if speech_time < MIN_SPEECH_DURATION:

        print(
            "⚠️ Very short sound ignored."
        )

        return None

    return np.concatenate(
        frames
    )


# ==================================================
# NOISE REDUCTION
# ==================================================

def reduce_noise(audio):

    try:

        print(
            "🔇 Reducing background noise..."
        )

        cleaned_audio = nr.reduce_noise(

            y=audio.astype(
                np.float32
            ),

            sr=SAMPLE_RATE,

            stationary=True,

            prop_decrease=0.7
        )

        cleaned_audio = np.clip(
            cleaned_audio,
            -32768,
            32767
        )

        return cleaned_audio.astype(
            np.int16
        )

    except Exception as e:

        print(
            "⚠️ Noise reduction failed:",
            str(e)
        )

        return audio


# ==================================================
# SEND TO STT
# ==================================================

def transcribe(audio):

    temp_path = None

    try:

        # ------------------------------------------
        # REDUCE NOISE
        # ------------------------------------------

        audio = reduce_noise(
            audio
        )

        # ------------------------------------------
        # CREATE TEMPORARY WAV
        # ------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        ) as temp:

            temp_path = temp.name

        write(
            temp_path,
            SAMPLE_RATE,
            audio
        )

        # ------------------------------------------
        # SEND TO API
        # ------------------------------------------

        start = time.time()

        with open(
            temp_path,
            "rb"
        ) as audio_file:

            response = requests.post(

                API_URL,

                files={
                    "audio": (
                        "microphone.wav",
                        audio_file,
                        "audio/wav"
                    )
                },

                timeout=120
            )

        elapsed = (
            time.time() - start
        )

        # ------------------------------------------
        # CHECK RESPONSE
        # ------------------------------------------

        if response.status_code != 200:

            print()
            print(
                "❌ STT ERROR"
            )

            print(
                "HTTP Status:",
                response.status_code
            )

            print(
                response.text
            )

            return None

        result = response.json()

        # ------------------------------------------
        # STRUCTURED RESULT
        # ------------------------------------------

        stt_result = {

            "success":
                result.get(
                    "success",
                    False
                ),

            "text":
                result.get(
                    "text",
                    ""
                ),

            "language":
                result.get(
                    "language",
                    ""
                ),

            "model":
                result.get(
                    "model",
                    ""
                ),

            "processing_time":
                round(
                    elapsed,
                    2
                )
        }

        # ------------------------------------------
        # DISPLAY
        # ------------------------------------------

        print()
        print(
            "=" * 55
        )

        print(
            "                 STT RESULT"
        )

        print(
            "=" * 55
        )

        print(
            "Text     :",
            stt_result["text"]
        )

        print(
            "Language :",
            stt_result["language"]
        )

        print(
            "Model    :",
            stt_result["model"]
        )

        print(
            "Time     :",
            stt_result[
                "processing_time"
            ],
            "seconds"
        )

        print(
            "=" * 55
        )

        return stt_result

    except requests.exceptions.ConnectionError:

        print()
        print(
            "❌ Cannot connect to STT server."
        )

        print(
            "Make sure stt_api.py is running."
        )

        return None

    except requests.exceptions.Timeout:

        print()
        print(
            "❌ STT request timed out."
        )

        return None

    except Exception as e:

        print()
        print(
            "❌ ERROR:",
            str(e)
        )

        return None

    finally:

        # ------------------------------------------
        # DELETE TEMPORARY FILE
        # ------------------------------------------

        if (
            temp_path
            and os.path.exists(
                temp_path
            )
        ):

            os.remove(
                temp_path
            )


# ==================================================
# CONTINUOUS STT
# ==================================================

def main():

    print("=" * 55)

    print(
        "       SIH CONTINUOUS MICROPHONE STT"
    )

    print("=" * 55)

    print()
    print(
        "Model      : Saaras v3"
    )

    print(
        "Microphone : ACTIVE"
    )

    print(
        "Noise reduction : ENABLED"
    )

    print(
        "Speech detection : ADAPTIVE"
    )

    print()
    print(
        "Speak normally."
    )

    print(
        "The system waits 1.8 seconds after speech stops."
    )

    print(
        "Press CTRL+C to exit."
    )

    print(
        "=" * 55
    )

    try:

        # ------------------------------------------
        # CALIBRATE
        # ------------------------------------------

        threshold = calibrate_noise()

        # ------------------------------------------
        # CONTINUOUS LOOP
        # ------------------------------------------

        while True:

            audio = record_speech(
                threshold
            )

            if audio is None:

                continue

            result = transcribe(
                audio
            )

            print()
            print(
                "🎤 Ready for next speech..."
            )

            print(
                "-" * 55
            )

    except KeyboardInterrupt:

        print()
        print()

        print(
            "=" * 55
        )

        print(
            "       CONTINUOUS STT STOPPED"
        )

        print(
            "=" * 55
        )

        print(
            "Goodbye!"
        )


# ==================================================
# START
# ==================================================

if __name__ == "__main__":

    main()