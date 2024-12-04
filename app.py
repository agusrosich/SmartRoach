from flask import Flask, request, render_template
import joblib
import numpy as np
import pandas as pd
import json
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

app = Flask(__name__)

# Cargar el modelo entrenado
model = joblib.load('modelo_smart_roach.pkl')

# Cargar los nombres de las características
with open('feature_names.json', 'r') as f:
    feature_names = json.load(f)

# Imprimir los nombres de las características para verificar
print("Nombres de las características en el modelo:", feature_names)

# Función para preparar los datos en el formato necesario para el modelo
def prepare_input_data(edad, t, race, psa, gleason):
    # Crear un diccionario con las características inicializadas en cero
    input_dict = dict.fromkeys(feature_names, 0)
    
    # Asignar los valores numéricos
    # Verificar y asignar 'Age' o 'Edad'
    if 'Age' in input_dict:
        input_dict['Age'] = edad
    elif 'Edad' in input_dict:
        input_dict['Edad'] = edad
    else:
        print("Advertencia: La característica 'Age' o 'Edad' no se encuentra en el modelo.")
    
    # Asignar 'PSA'
    if 'PSA' in input_dict:
        input_dict['PSA'] = psa
    else:
        print("Advertencia: La característica 'PSA' no se encuentra en el modelo.")
    
    # Verificar y asignar 'Gleason Score'
    if 'Gleason Score' in input_dict:
        input_dict['Gleason Score'] = gleason
    elif 'Gleason_Score' in input_dict:
        input_dict['Gleason_Score'] = gleason
    elif 'GleasonScore' in input_dict:
        input_dict['GleasonScore'] = gleason
    elif 'Gleason' in input_dict:
        input_dict['Gleason'] = gleason
    else:
        print("Advertencia: La característica 'Gleason Score' no se encuentra en el modelo.")
    
    # Codificar la variable 'T'
    t_feature_name = f'T_{t}'
    if t_feature_name in input_dict:
        input_dict[t_feature_name] = 1
    else:
        print(f"Advertencia: '{t_feature_name}' no se encuentra en las características del modelo.")
    
    # Codificar la variable 'Race'
    race_feature_name = f'Race_{race}'
    if race_feature_name in input_dict:
        input_dict[race_feature_name] = 1
    else:
        print(f"Advertencia: '{race_feature_name}' no se encuentra en las características del modelo.")
    
    # Crear un DataFrame con las características en el mismo orden
    input_df = pd.DataFrame([input_dict], columns=feature_names)
    
    # Verificar el número de características y el contenido
    print("Número de características de entrada:", len(input_df.columns))  # Debe coincidir con el modelo
    print("Características de entrada:\n", input_df)
    
    return input_df

# Ruta para el formulario principal
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Obtener los datos del formulario
        edad = int(request.form['edad'])
        t = request.form['t']
        race = request.form['race']
        psa = float(request.form['psa'])
        gleason = int(request.form['gleason'])
        
        # Preparar los datos para el modelo
        input_data = prepare_input_data(edad, t, race, psa, gleason)
        
        # Realizar la predicción
        prediction = model.predict_proba(input_data)[0][1]  # Probabilidad de tener ganglios positivos
        
        # Mostrar el resultado como porcentaje
        risk_percentage = round(prediction * 100, 2)
        
        # Enviar datos al template con los valores ingresados
        return render_template('index.html', result=risk_percentage, edad=edad, t=t, race=race, psa=psa, gleason=gleason)
    
    # Solicitud GET: Inicializar valores predeterminados para evitar errores de "UndefinedError"
    return render_template('index.html', result=None, edad='', t='T1a', race='Unknown', psa='', gleason=6)

if __name__ == '__main__':
    app.run(debug=True)