import RPi.GPIO as GPIO
import datetime
import time
from flask import Flask, render_template, request
from pymongo import MongoClient
from werkzeug.utils import redirect
import smbus
#ligação mongodb
username = ""
password =""
led_off = False
client = MongoClient("mongodb+srv://led_user:8CEFaHv60DCRlAB0@cluster0.i3isdwt.mongodb.net/?retryWrites=true&w=majority")
db = client["leds"]
collection = db["users"]

db_logs = client["leds"]
collection_logs = db_logs["log"]

address = 0x29

# Inicializa o barramento I2C
bus = smbus.SMBus(1)  # Use 0 se estiver usando o Raspberry Pi 1

# Configuração do sensor
bus.write_byte_data(address, 0x80, 0x03)  # Power ON
bus.write_byte_data(address, 0x81, 0x12)  # Ganho 16x, tempo de integração de 402ms

# Configurar os pinos dos LEDs
led_pins = [18, 23, 24]  # Substitua pelos pinos corretos
GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
for led_pin in led_pins:
    GPIO.setup(led_pin, GPIO.OUT)

app = Flask(__name__)
ledLigado = True

def registrar_log(acao):
    global username
    data_hora = datetime.datetime.now()
    log_entry = {"user": username ,"data_hora": data_hora, "acao": acao}
    collection_logs.insert_one(log_entry)

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

def controlar_leds_sensor():
    while True:
        # Leitura dos dados
        data = bus.read_i2c_block_data(address, 0x8C | 0x80, 2)  # Registro de dados de luz visível
        vis_data = data[1] * 256 + data[0]
        data = bus.read_i2c_block_data(address, 0x8E | 0x80, 2)  # Registro de dados de luz infravermelha
        ir_data = data[1] * 256 + data[0]

        # Cálculo da porcentagem de luz
        total_light = vis_data
        percentage = (total_light / 65535) * 100

        # Exibição dos resultados
        print("Porcentagem de luz: {:.2f}%".format(total_light))

        if total_light <= 2000:
            for led_pin in led_pins:
                GPIO.output(led_pin, GPIO.HIGH)  # Liga todos os LEDs
        elif 2000 < total_light <= 5000:
            GPIO.output(led_pins[0], GPIO.HIGH)  # Liga o primeiro LED
            GPIO.output(led_pins[1], GPIO.HIGH)  # Liga o segundo LED
            GPIO.output(led_pins[2], GPIO.LOW)  # Desliga o terceiro LED
        elif 5000 < total_light <= 10000:
            GPIO.output(led_pins[0], GPIO.HIGH)  # Liga o primeiro LED
            GPIO.output(led_pins[1], GPIO.LOW)  # Desliga o segundo LED
            GPIO.output(led_pins[2], GPIO.LOW)  # Desliga o terceiro LED
        elif total_light > 10000:
            for led_pin in led_pins:
                GPIO.output(led_pin, GPIO.LOW)  # Desliga todos os LEDs
        else:
            # Ação padrão caso nenhuma das condições seja atendida
            # Por exemplo, você pode desligar todos os LEDs
            for led_pin in led_pins:
                GPIO.output(led_pin, GPIO.LOW)
                
@app.route('/controlar_leds_sensor_horario')
def controlar_leds_sensor_horario():
    hora_atual = datetime.datetime.now().time()
    hora = hora_atual.hour
    global ledLigado
    ledLigado = True
    # Desligar todos os LEDs
    GPIO.output(led_pins, GPIO.LOW)
    registrar_log("LEDs ligados com sensor e horário")
    while ledLigado == True:
        # Leitura dos dados
        
     
        
        data = bus.read_i2c_block_data(address, 0x8C | 0x80, 2)  # Registro de dados de luz visível
        vis_data = data[1] * 256 + data[0]
        data = bus.read_i2c_block_data(address, 0x8E | 0x80, 2)  # Registro de dados de luz infravermelha
        ir_data = data[1] * 256 + data[0]

        # Cálculo da porcentagem de luz
        total_light = vis_data
        percentage = (total_light / 65535) * 100

        # Exibição dos resultados
        print("Porcentagem de luz: {:.2f}%".format(total_light))
        # Definir o estado dos LEDs com base na hora do dia
        if hora >= 9 and hora < 12:
            if total_light <= 2000:
                GPIO.output(led_pins[0], GPIO.HIGH)  # Liga o primeiro LED
                GPIO.output(led_pins[1], GPIO.HIGH)  # Liga o segundo LED
                GPIO.output(led_pins[2], GPIO.LOW)# Liga todos os LEDs
            elif 2000 < total_light <= 5000:
                GPIO.output(led_pins[0], GPIO.HIGH)  # Liga o primeiro LED
                GPIO.output(led_pins[1], GPIO.LOW)  # Liga o segundo LED
                GPIO.output(led_pins[2], GPIO.LOW)  # Desliga o terceiro LED
            elif 5000 < total_light <= 10000:
                GPIO.output(led_pins[0], GPIO.HIGH)  # Liga o primeiro LED
                GPIO.output(led_pins[1], GPIO.LOW)  # Desliga o segundo LED
                GPIO.output(led_pins[2], GPIO.LOW)  # Desliga o terceiro LED
            elif total_light > 10000:
                for led_pin in led_pins:
                    GPIO.output(led_pin, GPIO.LOW)  # Desliga todos os LEDs
            else:
                # Ação padrão caso nenhuma das condições seja atendida
                # Por exemplo, você pode desligar todos os LEDs
                for led_pin in led_pins:
                    GPIO.output(led_pin, GPIO.LOW)
        elif hora >= 12 and hora < 13:
            if total_light <= 2000:
                GPIO.output(led_pins[0], GPIO.HIGH)  # Liga o primeiro LED
                GPIO.output(led_pins[1], GPIO.HIGH)  # Liga o segundo LED
                GPIO.output(led_pins[2], GPIO.HIGH)# Liga todos os LEDs
            elif 2000 < total_light <= 5000:
                GPIO.output(led_pins[0], GPIO.HIGH)  # Liga o primeiro LED
                GPIO.output(led_pins[1], GPIO.HIGH)  # Liga o segundo LED
                GPIO.output(led_pins[2], GPIO.LOW)  # Desliga o terceiro LED
            elif 5000 < total_light <= 10000:
                GPIO.output(led_pins[0], GPIO.HIGH)  # Liga o primeiro LED
                GPIO.output(led_pins[1], GPIO.LOW)  # Desliga o segundo LED
                GPIO.output(led_pins[2], GPIO.LOW)  # Desliga o terceiro LED
            elif total_light > 10000:
                for led_pin in led_pins:
                    GPIO.output(led_pin, GPIO.LOW)  # Desliga todos os LEDs
            else:
                # Ação padrão caso nenhuma das condições seja atendida
                # Por exemplo, você pode desligar todos os LEDs
                for led_pin in led_pins:
                    GPIO.output(led_pin, GPIO.LOW)
           
        elif hora >= 13 and hora < 18:
            if total_light <= 2000:
                GPIO.output(led_pins[0], GPIO.HIGH)  # Liga o primeiro LED
                GPIO.output(led_pins[1], GPIO.HIGH)  # Liga o segundo LED
                GPIO.output(led_pins[2], GPIO.LOW)# Liga todos os LEDs
            elif 2000 < total_light <= 10000:
                GPIO.output(led_pins[0], GPIO.HIGH)  # Liga o primeiro LED
                GPIO.output(led_pins[1], GPIO.LOW)  # Desliga o segundo LED
                GPIO.output(led_pins[2], GPIO.LOW)  # Desliga o terceiro LED
            elif total_light > 10000:
                for led_pin in led_pins:
                    GPIO.output(led_pin, GPIO.LOW)  # Desliga todos os LEDs
            else:
                # Ação padrão caso nenhuma das condições seja atendida
                # Por exemplo, você pode desligar todos os LEDs
                for led_pin in led_pins:
                    GPIO.output(led_pin, GPIO.LOW)
                    
        elif hora >= 18 and hora < 20:
            if total_light <= 10000:
                GPIO.output(led_pins[0], GPIO.HIGH)  # Liga o primeiro LED
                GPIO.output(led_pins[1], GPIO.LOW)  # Desliga o segundo LED
                GPIO.output(led_pins[2], GPIO.LOW)  # Desliga o terceiro LED
            elif total_light > 10000:
                for led_pin in led_pins:
                    GPIO.output(led_pin, GPIO.LOW)  # Desliga todos os LEDs
            else:
                # Ação padrão caso nenhuma das condições seja atendida
                # Por exemplo, você pode desligar todos os LEDs
                for led_pin in led_pins:
                    GPIO.output(led_pin, GPIO.LOW)
        elif hora >= 20 and hora < 22:
            if total_light <= 2000:
                GPIO.output(led_pins[0], GPIO.HIGH)  # Liga o primeiro LED
                GPIO.output(led_pins[1], GPIO.HIGH)  # Liga o segundo LED
                GPIO.output(led_pins[2], GPIO.LOW)# Liga todos os LEDs
            elif 2000 < total_light <= 10000:
                GPIO.output(led_pins[0], GPIO.HIGH)  # Liga o primeiro LED
                GPIO.output(led_pins[1], GPIO.LOW)  # Desliga o segundo LED
                GPIO.output(led_pins[2], GPIO.LOW)  # Desliga o terceiro LED
            elif total_light > 10000:
                for led_pin in led_pins:
                    GPIO.output(led_pin, GPIO.LOW)  # Desliga todos os LEDs
            else:
                # Ação padrão caso nenhuma das condições seja atendida
                # Por exemplo, você pode desligar todos os LEDs
                for led_pin in led_pins:
                    GPIO.output(led_pin, GPIO.LOW)
        time.sleep(2)
    
@app.route('/ligar_leds')
def ligar_leds():
    global ledLigado
    ledLigado = True
    registrar_log("LEDs ligados")
    while ledLigado == True:
        #print("ola")
        controlar_leds()
        time.sleep(2)
    #controlar_leds()
    return "leds ligados"
    
@app.route('/ligar_leds_sensor')
def ligar_leds_sensor():
    global ledLigado
    ledLigado = True
    registrar_log("sensor ligado")
    while ledLigado == True:
        controlar_leds_sensor()
        time.sleep(2)
    return "sensor leds ligado"

@app.route("/controle_sensor")
def controle_sensor():
    global username, password
    if(username != "" and password !=""):
        return render_template('controlarPeloSensor.html')
    else:
        return redirect('login')

@app.route("/controle_luminosidade_hora")
def controle_luminosidade_hora():
    global username, password
    if(username != "" and password !=""):
        return render_template('controle_luminosidade_hora.html')
    else:
        return redirect('login')

@app.route('/desligar_leds')
def desligar_leds():
    global ledLigado
    registrar_log("LEDs desligados")
    ledLigado= False
    GPIO.output(led_pins, GPIO.LOW)
    return 'LEDs desligados!'


@app.route('/login', methods=['GET', 'POST'])
def login():
    global username, password
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = collection.find_one({'username': username})
        if user and user['password'] == password:
            # Login bem-sucedido
            return redirect("/menu")
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
        return redirect('login')

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

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    global username, password
    password = ""
    username = ""
    return redirect('interface')

@app.route('/menu')
def menu():
    global username, password
    if(username != "" and password !=""):
        return render_template('menu.html')
    else:
        return redirect('login')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
