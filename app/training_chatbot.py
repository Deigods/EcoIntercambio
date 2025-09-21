import json
import pickle
import numpy as np
import os
import nltk
from nltk.stem import WordNetLemmatizer
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import SGD
from nltk.tokenize import WhitespaceTokenizer

# -----------------------------------------------------------
# Configuración de rutas y NLTK
# -----------------------------------------------------------

# Carpeta donde está este script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# La ruta a la raíz del proyecto
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..'))

# Carpeta para nltk_data
NLTK_DATA_DIR = os.path.join(PROJECT_ROOT, 'nltk_data')
os.makedirs(NLTK_DATA_DIR, exist_ok=True)
nltk.data.path.append(NLTK_DATA_DIR)

# Descargar los recursos necesarios de NLTK
# Solo se descarga 'wordnet' porque WhitespaceTokenizer no necesita otros recursos
required_packages = ['wordnet']
for package in required_packages:
    try:
        nltk.data.find(f'corpora/{package}')
    except LookupError:
        print(f"Descargando el recurso '{package}'...")
        nltk.download(package, download_dir=NLTK_DATA_DIR)

# Inicializar lematizador
lemmatizer = WordNetLemmatizer()

# Crear una instancia del tokenizer simple
tokenizer = WhitespaceTokenizer()

# Carpeta donde estarán los archivos del chatbot
CHATBOT_DIR = os.path.join(PROJECT_ROOT, 'EcoIntercambio', 'app', 'templates', 'app', 'chatbot')
os.makedirs(CHATBOT_DIR, exist_ok=True)

# -----------------------------------------------------------
# Cargar intents
# -----------------------------------------------------------
intents_path = os.path.join(CHATBOT_DIR, 'intents_spanish.json')
if not os.path.isfile(intents_path):
    raise FileNotFoundError(f"No se encontró el archivo intents_spanish.json en: {intents_path}")

with open(intents_path, 'r', encoding='utf-8') as f:
    intents = json.load(f)

# -----------------------------------------------------------
# Preparar datos
# -----------------------------------------------------------
words = []
classes = []
documents = []

for intent in intents['intents']:
    for pattern in intent['patterns']:
        # Usar el tokenizer simple en lugar de word_tokenize
        w = tokenizer.tokenize(pattern)
        w = [lemmatizer.lemmatize(word.lower()) for word in w]
        words.extend(w)
        documents.append((w, intent['tag']))
    if intent['tag'] not in classes:
        classes.append(intent['tag'])

words = sorted(list(set(words)))
classes = sorted(list(set(classes)))

# Guardar words y classes
pickle.dump(words, open(os.path.join(CHATBOT_DIR, 'words.pkl'), 'wb'))
pickle.dump(classes, open(os.path.join(CHATBOT_DIR, 'classes.pkl'), 'wb'))

# -----------------------------------------------------------
# Preparar datos de entrenamiento
# -----------------------------------------------------------
training = []
output_empty = [0] * len(classes)

for doc in documents:
    bag = []
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in doc[0]]
    for w in words:
        bag.append(1 if w in pattern_words else 0)

    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1
    training.append([bag, output_row])

training = np.array(training, dtype=object)
train_x = np.array(list(training[:, 0]))
train_y = np.array(list(training[:, 1]))

# -----------------------------------------------------------
# Crear modelo
# -----------------------------------------------------------
model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))

# Compilar modelo
sgd = SGD(learning_rate=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

# -----------------------------------------------------------
# Entrenar modelo
# -----------------------------------------------------------
hist = model.fit(train_x, train_y, epochs=200, batch_size=5, verbose=1)

# Guardar modelo
model_path = os.path.join(CHATBOT_DIR, 'chatbot_model.h5')
model.save(model_path)

print("Entrenamiento completado. Modelo y pickles generados correctamente.")