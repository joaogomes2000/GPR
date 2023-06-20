import RPi.GPIO as GPIO
import datetime
import time
from flask import Flask, render_template, request
from pymongo import MongoClient
from werkzeug.utils import redirect
#ligação mongodb

client = MongoClient("mongodb+srv://led_user:8CEFaHv60DCRlAB0@cluster0.i3isdwt.mongodb.net/?retryWrites=true&w=majority")
db = client["leds"]
collection = db["users"]

# Configurar os pinos dos LEDs
ledLigado = False
led_pins = [18, 23, 24]  # Substitua pelos pinos corretos
GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
GPIO.setup(led_pins, GPIO.OUT)

app = Flask(__name__)
ledLigado = True
def controlar_leds():
    hora_atual = datetime.datetime.now().time()
    hora = hora_atual.hour

    # Desligar todos os LEDs
    GPIO.output(led_pins, GPIO.LOW)

    # Definir o estado dos LEDs com base na hora do dia
    if hora >= 9 and hora < 12:
        GPIO.output(led_pins[:2], GPIO.HIGH)
    elif hora >= 12 and hora < 13:
        GPIO.output(led_pins[:3], GPIO.HIGH)
    elif hora >= 13 and hora < 18:
        GPIO.output(led_pins[:2], GPIO.HIGH)
    elif hora >= 18 and hora < 20:
        GPIO.output(led_pins[:1], GPIO.HIGH)
    elif hora >= 20 and hora < 22:
        GPIO.output(led_pins[:2], GPIO.HIGH)
        
@app.route('/ligar_leds')
def ligar_leds():
    global ledLigado
    ledLigado = True
    while ledLigado == True:
        #print("ola")
        controlar_leds()
        time.sleep(2)
    #controlar_leds()
    return "leds ligados"
    

@app.route('/desligar_leds')
def desligar_leds():
    global ledLigado
    ledLigado= False
    GPIO.output(led_pins, GPIO.LOW)
    return 'LEDs desligados!'

username = ""
password =""
@app.route('/login', methods=['GET', 'POST'])
def login():
    global username, password
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = collection.find_one({'username': username})
        if user and user['password'] == password:
            # Login bem-sucedido
            return redirect("/interface")
        else:
            # Login inválido
            return render_template('login.html', error_message='Nome de utilizador ou senha inválidos!')
    return render_template('login.html')

@app.route('/interface')
def mostrar_interface():
    global username, password
    if(username != "" and password !=""):
        return render_template('interface.html')
    else:
        return render_template('login.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = collection.find_one({'username': username})
        if user:
            # Nome de utilizador já existente
            return render_template('register.html', error_message='Nome de utilizador já existe!')
        else:
            # Cadastrar novo usuário
            new_user = {'username': username, 'password': password}
            collection.insert_one(new_user)
            return render_template('login.html')
            

    return render_template('register.html')




if __name__ == '__main__':
    app.run(host='0.0.0.0')

