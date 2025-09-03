import json
import pickle
import numpy as np
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
import nltk

nltk.download('punkt')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

# Carga de archivos necesarios
intents = json.loads(open('c:/EcoIntercambio/app/templates/app/intents_spanish.json', 'r', encoding='utf-8').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbot_model.h5')

# Función para limpiar y tokenizar el texto
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# Función para crear la bolsa de palabras
def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0]*len(words)
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print(f"Found in bag: {w}")
    return np.array(bag)

# Función para predecir la clase
def predict_class(sentence):
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = []
    for i,r in enumerate(res):
        if r > ERROR_THRESHOLD:
            results.append({"intent": classes[i], "probability": str(r)})
    results.sort(key=lambda x: float(x["probability"]), reverse=True)
    return results

# Función para obtener una respuesta
def get_response(intents_list, intents_json):
    if len(intents_list) == 0:
        return "Lo siento, no entendí eso."
    tag = intents_list[0]['intent']
    for i in intents_json['intents']:
        if i['tag'] == tag:
            return np.random.choice(i['responses'])
