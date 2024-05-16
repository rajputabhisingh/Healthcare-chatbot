from flask import Flask, render_template, request, jsonify
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import os
import speech_recognition as sr
from gtts import gTTS
import playsound

from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

# import pdb;pdb.set_trace();
filenumber = int(os.listdir('saved_conversations')[-1])
filenumber += 1
print(filenumber)
file = open('saved_conversations/' + str(filenumber), "w+")
print(file)
file.write('bot : Hi there! I am a medical chatbot. You can begin a conversation by typing a message and pressing enter.\n')
file.close()

app = Flask(__name__, template_folder='templates')
# Set the static folder
app.static_folder = 'static'

english_bot = ChatBot('Bot',
                      storage_adapter='chatterbot.storage.SQLStorageAdapter',
                      logic_adapters=[
                          {'import_path': 'chatterbot.logic.BestMatch'},
                      ],
                      trainer='chatterbot.trainers.ListTrainer')
english_bot.set_trainer(ListTrainer)


def record_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        user_audio = recognizer.recognize_google(audio)
        print("You said:", user_audio)
        return user_audio
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return ""
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
        return ""


def speak_text(text):
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    playsound.playsound("response.mp3")
    os.remove('response.mp3')


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    # import pdb;pdb.set_trace();
    user_text = request.args.get('msg')
    is_speech = request.args.get('isSpeech')  # Check if input is from speech
    response = str(english_bot.get_response(user_text))

    # Save conversation to file
    append_file = os.listdir('saved_conversations')[-1]
    append_file = open('saved_conversations/' + str(filenumber), "a")
    append_file.write('user : ' + user_text + '\n')
    append_file.write('bot : ' + response + '\n')
    append_file.close()
    
    # Speak response
    if is_speech == 'true':
        speak_text(response)
        
    # Prepare conversation data to return
    conversation = [{'speaker': 'user', 'message': user_text},
                    {'speaker': 'bot', 'message': response}]
    
    print("Response:", response)  # Print the response for debugging

    # Return the response as JSON
    return jsonify({'text': response, 'audio': 'response.mp3'})


@app.route("/voice_input")
def get_voice_input():
    user_audio = record_audio()
    return user_audio




if __name__ == "__main__":
    app.run(debug=True)
