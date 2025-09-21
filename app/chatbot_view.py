from django.shortcuts import render
from django.http import JsonResponse

import json
import pickle
import numpy as np
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
import nltk
from nltk.tokenize import WhitespaceTokenizer
import random
import os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# Configuración de NLTK
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

NLTK_DATA_DIR = os.path.join(BASE_DIR, 'nltk_data')
nltk.data.path.append(NLTK_DATA_DIR)

# Verifica que wordnet exista
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    print("Descargando el recurso 'wordnet'...")
    nltk.download('wordnet', download_dir=NLTK_DATA_DIR)

lemmatizer = WordNetLemmatizer()
tokenizer = WhitespaceTokenizer()

# Carga de archivos con rutas absolutas en app/templates/app/chatbot/
chatbot_dir = os.path.join(settings.BASE_DIR, 'app', 'templates', 'app', 'chatbot')
intents_path = os.path.join(chatbot_dir, 'intents_spanish.json')
words_path = os.path.join(chatbot_dir, 'words.pkl')
classes_path = os.path.join(chatbot_dir, 'classes.pkl')
model_path = os.path.join(chatbot_dir, 'chatbot_model.h5')

intents = json.loads(open(intents_path, encoding='utf-8').read())
words = pickle.load(open(words_path, 'rb'))
classes = pickle.load(open(classes_path, 'rb'))
model = load_model(model_path)

# Funciones del chatbot
def clean_up_sentence(sentence):
    # Usar el tokenizer simple en lugar de nltk.word_tokenize
    sentence_words = tokenizer.tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    p = bow(sentence, words)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = []
    for i, r in enumerate(res):
        if r > ERROR_THRESHOLD:
            results.append({"intent": classes[i], "probability": str(r)})
    results.sort(key=lambda x: float(x["probability"]), reverse=True)
    return results

def get_response(intents_list, intents_json):
    if len(intents_list) == 0:
        return "Lo siento, no entendí eso."
    tag = intents_list[0]['intent']
    for i in intents_json['intents']:
        if i['tag'] == tag:
            return random.choice(i['responses'])

# Vista para mostrar el HTML
def chatbot_view(request):
    return render(request, 'app/chatbot/chatbot.html')

# Endpoint para recibir mensajes vía AJAX
@csrf_exempt
def chatbot_response(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = data.get('message')
            ints = predict_class(message)
            res = get_response(ints, intents)
            return JsonResponse({"response": res})
        except Exception as e:
            # Imprime el error en consola y devuélvelo en la respuesta
            import traceback
            traceback.print_exc()
            return JsonResponse({"response": f"Error interno: {str(e)}"})
    return JsonResponse({"response": "Error"})