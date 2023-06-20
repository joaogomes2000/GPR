import smbus
import RPi.GPIO as GPIO

# Endereço I2C do sensor
address = 0x29

# Inicializa o barramento I2C
bus = smbus.SMBus(1)  # Use 0 se estiver usando o Raspberry Pi 1

# Configuração do sensor
bus.write_byte_data(address, 0x80, 0x03)  # Power ON
bus.write_byte_data(address, 0x81, 0x12)  # Ganho 16x, tempo de integração de 402ms

# Configuração dos pinos dos LEDs
led_pins = [18, 23, 24]
GPIO.setmode(GPIO.BCM)
for led_pin in led_pins:
    GPIO.setup(led_pin, GPIO.OUT)

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
