# SIH Multilingual Continuous Speech-to-Text

This project is the Speech-to-Text (STT) module developed for the SIH project.

The module converts human speech from a microphone into text. It supports multiple Indian languages, automatically detects the spoken language, reduces background noise, and uses Sarvam Saaras v3 for speech recognition.

The STT module is designed as an independent component so that the SIH backend and frontend team can integrate it with the Brain Model and Text-to-Speech module.

## Model

Sarvam Saaras v3

Saaras v3 is used for multilingual Indian Speech-to-Text.

## Features

- Direct microphone speech input
- Continuous microphone listening
- Automatic speech detection
- Automatic speech-end detection
- Background noise calibration
- Background noise reduction
- Automatic language detection
- Multilingual Indian language support
- Fast speech transcription
- REST API for integration
- Temporary audio processing
- Temporary audio files are automatically deleted
- Multiple speech inputs can be processed without restarting the program

## Complete System Flow

User speaks into microphone
        ↓
Continuous microphone capture
        ↓
Speech detection
        ↓
Temporary audio recording
        ↓
Background noise reduction
        ↓
Sarvam Saaras v3
        ↓
Recognized text + detected language
        ↓
Brain Model
        ↓
Response text
        ↓
Text-to-Speech
        ↓
Voice response

## Project Structure

SIH_STT/
│
├── stt_api.py
├── continuous_stt.py
├── requirements.txt
├── README.md
└── .gitignore

## File Description

### stt_api.py

This is the Flask-based Speech-to-Text API.

It receives audio from the frontend or another application and sends the audio to Sarvam Saaras v3 for transcription.

Main endpoints:

GET /api/health

POST /api/transcribe

### continuous_stt.py

This is the continuous microphone Speech-to-Text program.

It directly captures speech from the microphone.

The user does not need to manually select or provide an audio filename for every speech input.

The program continuously performs the following process:

1. Calibrates the microphone background noise.
2. Activates the microphone.
3. Detects when the user starts speaking.
4. Captures the speech temporarily.
5. Detects when the user stops speaking.
6. Reduces background noise.
7. Sends the speech to the STT API.
8. Sarvam Saaras v3 converts the speech into text.
9. The detected language is returned.
10. The temporary audio file is deleted.
11. The microphone starts listening again.

### requirements.txt

This file contains the Python packages required to run the STT module.

Install the packages using:

pip install -r requirements.txt

### README.md

This file contains the documentation and instructions for using and integrating the STT module.

### .gitignore

This file prevents unwanted files such as audio recordings, temporary files, Python cache files, environment files, and other private files from being uploaded to GitHub.

## Supported Languages

The STT API supports the following language codes:

en-IN - English

te-IN - Telugu

hi-IN - Hindi

ta-IN - Tamil

kn-IN - Kannada

ml-IN - Malayalam

mr-IN - Marathi

bn-IN - Bengali

gu-IN - Gujarati

pa-IN - Punjabi

od-IN - Odia

as-IN - Assamese

ur-IN - Urdu

ne-IN - Nepali

kok-IN - Konkani

ks-IN - Kashmiri

sd-IN - Sindhi

sa-IN - Sanskrit

sat-IN - Santali

mni-IN - Manipuri

brx-IN - Bodo

mai-IN - Maithili

doi-IN - Dogri

The language value can also be set to:

unknown

When unknown is used, the system automatically detects the spoken language.

## Installation

Open a terminal inside the project folder.

Install all required packages using:

pip install -r requirements.txt

Make sure the computer has a working microphone and that microphone access is allowed for Python.

## API Key

The STT module requires a Sarvam API key to use Saaras v3.

The API key should be configured as an environment variable.

For Windows PowerShell:

$env:SARVAM_API_KEY="YOUR_API_KEY"

The real API key must never be uploaded to GitHub.

The API key should remain private.

## Running the STT API

Start the STT API using:

python stt_api.py

The API will run at:

http://127.0.0.1:5000

Keep this terminal running while using the continuous microphone STT program.

## Health Check

The health-check endpoint is:

GET /api/health

Example response:

{
    "success": true,
    "status": "ok",
    "service": "SIH Speech-to-Text",
    "model": "saaras:v3"
}

This endpoint can be used to check whether the STT API is running correctly.

## Speech-to-Text API

The main endpoint is:

POST /api/transcribe

The frontend or backend application should send the microphone audio using the form field:

audio

The API processes the audio and returns the recognized text and detected language.

Example response:

{
    "success": true,
    "text": "నాకు జ్వరం ఉంది",
    "language": "te-IN",
    "model": "saaras:v3"
}

## API Response

The API returns the following important values.

success

Indicates whether the transcription was successful.

Example:

true

text

Contains the speech converted into text.

Example:

"నాకు జ్వరం ఉంది"

This is the main output that should be passed to the Brain Model.

language

Contains the detected language code.

Example:

"te-IN"

model

Contains the name of the STT model used.

Example:

"saaras:v3"

## Continuous Microphone STT

The continuous microphone STT is started using:

python continuous_stt.py

The STT API must already be running before starting continuous_stt.py.

The complete process is:

Microphone
    ↓
Speech detection
    ↓
Temporary recording
    ↓
Noise reduction
    ↓
STT API
    ↓
Sarvam Saaras v3
    ↓
Text
    ↓
Language detection
    ↓
Temporary audio deleted
    ↓
Microphone listens again

The user can speak multiple times without restarting the program.

Example:

User speaks
    ↓
Text is generated
    ↓
Microphone listens again
    ↓
User speaks again
    ↓
Text is generated
    ↓
Microphone listens again

The program can be stopped using:

CTRL + C

## Background Noise Reduction

The continuous STT system first calibrates the microphone to estimate the background noise level.

The system uses this information to distinguish speech from background noise and silence.

After speech is captured, background noise reduction is applied before the audio is sent for transcription.

This helps improve speech recognition in normal environments with background noise.

## Temporary Audio Processing

The microphone speech is captured temporarily for processing.

The temporary audio is sent to the STT API.

After the transcription is completed, the temporary audio file is deleted automatically.

The system does not depend on fixed filenames such as:

r6.m4a

sahiti.m4a

test2.m4a

The continuous microphone system creates temporary audio internally for each speech segment.

Therefore, the user does not need to manually save and name audio files.

## Important Difference Between Testing and the Final STT

During development, recorded files such as .m4a files were used to test the STT model.

Those files were only test inputs.

The final STT module is designed to work with microphone input.

The final system does not require users to save an audio file and enter its filename manually.

The microphone provides the speech input automatically.

## Integration With Brain Model

The STT module is responsible only for converting speech into text.

It does not generate the final medical response.

The recognized text is passed to the Brain Model.

Example:

User speaks:

"నాకు జ్వరం ఉంది"

        ↓

STT

        ↓

Text:

"నాకు జ్వరం ఉంది"

        ↓

Brain Model

        ↓

Response Text

        ↓

TTS

        ↓

Voice Response

The main value required by the Brain Model is the text returned by the STT module.

## Complete SIH Project Pipeline

USER
  ↓
MICROPHONE
  ↓
CONTINUOUS SPEECH-TO-TEXT
  ↓
BACKGROUND NOISE REDUCTION
  ↓
SARVAM SAARAS V3
  ↓
TEXT + LANGUAGE
  ↓
BRAIN MODEL
  ↓
RESPONSE TEXT
  ↓
TEXT-TO-SPEECH
  ↓
VOICE RESPONSE
  ↓
USER

## Responsibilities of the STT Module

The STT module handles:

Microphone speech input

Speech detection

Speech-end detection

Background noise calibration

Background noise reduction

Speech-to-Text conversion

Automatic language detection

Returning text to the next module

The STT module does not handle:

Brain Model processing

Medical response generation

Text-to-Speech generation

Website user interface

These components are handled by the other team members.

## Team Integration

The frontend/backend team can integrate this STT module into the SIH website.

The website can capture microphone audio and send it to:

POST /api/transcribe

The STT API returns:

text

language

model

Example:

User microphone speech
        ↓
Frontend
        ↓
POST /api/transcribe
        ↓
STT API
        ↓
Sarvam Saaras v3
        ↓
{
    "text": "ನನಗೆ ಜ್ವರ ಇದೆ",
    "language": "kn-IN",
    "model": "saaras:v3"
}
        ↓
Brain Model

The Brain Model should use the returned text as its input.

## Website Integration Concept

The final website can work like a voice-based AI assistant.

The user presses or activates the microphone and speaks.

The website sends the captured speech to the STT backend.

The STT backend converts the speech into text.

The text is passed to the Brain Model.

The Brain Model generates the response text.

The response text is sent to the TTS module.

The TTS module converts the response into speech.

The user hears the response.

The complete flow is:

Microphone
    ↓
STT
    ↓
Text
    ↓
Brain Model
    ↓
Response Text
    ↓
TTS
    ↓
Voice

## Testing

The STT module has been tested using multiple consecutive microphone speech inputs.

Testing included:

English

Telugu

Hindi

Tamil

Bengali

Kannada

Example English:

Language: en-IN

Text: Sahiti is a good girl

Example Telugu:

Language: te-IN

Text: ఓకే ఇప్పుడు మనం చేయాల్సిన పని ఏంటంటే

Example Hindi:

Language: hi-IN

Text: आपका नाम क्या है?

Example Bengali:

Language: bn-IN

Text: আমি তোমাকে ভালোবাসি।

Example Tamil:

Language: ta-IN

Text: என்ன தம்பி என்ன

The system can process multiple speech segments continuously without restarting.

## Important Notes for the Integration Team

The integration team does not need the recorded test audio files.

The integration team only needs the STT code and its dependencies.

The main STT output is:

text

The detected language is:

language

The STT module should be treated as an independent component.

The Brain Model does not need to know how the microphone recording or Sarvam API processing works.

The TTS module does not need to know how the STT processing works.

Each module can communicate through text.

## Security

Do not upload:

API keys

.env files

Personal audio recordings

Temporary audio files

Passwords

Authentication tokens

Private credentials

The Sarvam API key must remain private.

It should be configured using an environment variable.

## Final STT Module

The final STT module provides:

Microphone speech input

Continuous speech recognition

Automatic speech detection

Automatic speech-end detection

Background noise reduction

Automatic language detection

Multilingual Indian Speech-to-Text

Sarvam Saaras v3

REST API

Temporary audio cleanup

Text output for the Brain Model

The STT module is ready to be taken by the SIH backend/frontend team and integrated into the complete project.

## Final Architecture

                    USER
                     🎤
                     ↓
              MICROPHONE
                     ↓
             STT MODULE
                     ↓
          SPEECH DETECTION
                     ↓
          NOISE REDUCTION
                     ↓
             SAARAS V3
                     ↓
              TEXT OUTPUT
                     ↓
             BRAIN MODEL
                     ↓
            RESPONSE TEXT
                     ↓
                  TTS
                     ↓
               🔊 VOICE
                     ↓
                   USER