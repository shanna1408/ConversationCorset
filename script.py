from serial import Serial
import time
import requests
import speech_recognition as sr

# Hugging Face API details
API_URL = "https://api-inference.huggingface.co/models/borisn70/bert-43-multilabel-emotion-detection"
headers = {"Authorization": "Bearer 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"}

neutral_words = ["neutral", "autonomy", "empty"]
joy_words = ["approval", "excitement", "joy", "optimism", "happiness"]
anger_words = ["anger", "annoyance", "disapproval", "disgust", "hate"]
sad_words =["grief", "remorse", "sadness"]
love_words = ["admiration", "caring", "desire", "love"]
fun_words = ["amusement", "surprise", "fun", "enthusiasm", "recreation"]
unease_words = ["confusion", "disappointment", "embarrassment", "fear", "nervousness", "worry", "boredom"]
reflection_words = ["curiosity", "gratitude", "pride", "realization", "relief", "safety", "understanding", "sense of belonging", "meaning", "sustenance", "creativity"]

# Summarize text segment
def getSentiments(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

def query_huggingface(payload):
    """Send a payload to the Hugging Face API and return the response."""
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()
    except Exception as e:
        print(f"Error querying Hugging Face: {e}")
        return {"error": "API request failed"}


def get_segments():
    # Open the text file for reading
    with open("segments.txt", "r") as file:
        lines = file.readlines()

    # Extract the segment texts into a list
    segments = []
    for line in lines:
        if line.strip():  # Skip empty lines
            # Split the line at the first colon and take the part after it
            _, segment_text = line.split(":", 1)
            segments.append(segment_text.strip())
    return segments


def get_sentiment(emotion):
    if emotion in neutral_words:
        emotion = 0
    elif emotion in joy_words:
        emotion = 1
    elif emotion in anger_words:
        emotion = 2
    elif emotion in sad_words:
        emotion = 3
    elif emotion in love_words:
        emotion = 4
    elif emotion in fun_words:
        emotion = 5
    elif emotion in unease_words:
        emotion = 6
    elif emotion in reflection_words:
        emotion = 7
    return emotion
    

def send_to_arduino(list, arduino):
    #Output ex: "0 3 2 4 5 2 1 7"
    # = 0x0 3x1 2x2 4x3 5x4 2x5 1x6 7x7
    for i in range(len(list)):
            time.sleep(1)
            if (list[i]!=0):    
                arduino.write((str(list[i]) + '\n').encode('utf-8'))
                # Read data from Arduino
                data = arduino.readline()
                print(f"Received from Arduino: {data.decode('utf-8')}\n")
        
    # Close the serial connection
    arduino.close()

def real_time_speech_to_text():
    """Perform real-time speech-to-text and send text to Arduino."""
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    # Serial connection to Arduino
    serial_port = 'COM6'  # Adjust for your system (e.g., 'COM3' on Windows)
    baud_rate = 9600

    arduino = Serial(serial_port, baud_rate, timeout=1)
    time.sleep(2)  # Wait for connection to establish


    print("Listening for speech...")
    while True:
        try:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source)  # Adjust for background noise
                print("Say something...")
                audio = recognizer.listen(source)  # Listen for audio input

            # Convert speech to text
            text = recognizer.recognize_google(audio)
            print(f"Recognized: {text}")
            
            sentiment = getSentiments({
                "inputs": text,
            })
            raw_emotion = sentiment[0][0]['label']
            emotion = get_sentiment(raw_emotion)
            # print(text+": "+raw_emotion+' = '+str(emotion))
            
            arduino.write((str(emotion) + '\n').encode('utf-8'))
            # Read data from Arduino
            data = arduino.readline()
            print(f"Received from Arduino: {data.decode('utf-8')}\n")
            
            print("Sent to Arduino.")
        
        except sr.UnknownValueError:
            print("Could not understand the audio.")
        except sr.RequestError as e:
            print(f"API error: {e}")
        except KeyboardInterrupt:
            print("Stopping...")
            break


# Main Code

# real_time_speech_to_text()

# Serial connection to Arduino
serial_port = 'COM6'  # Adjust for your system (e.g., 'COM3' on Windows)
baud_rate = 9600

arduino = Serial(serial_port, baud_rate, timeout=1)
time.sleep(2)  # Wait for connection to establish

segments = get_segments()

sentiments = getSentiments({
	"inputs": segments,
})

list = []
for i in range(len(sentiments)):
    raw_emotion = sentiments[i][0]['label']
    emotion = get_sentiment(raw_emotion)
    print(segments[i]+": "+sentiments[i][0]['label']+' = '+str(emotion))
    list.append(emotion)

print(list)
send_to_arduino(list, arduino)