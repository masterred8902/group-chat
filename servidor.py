import socket
import threading

# Diccionario para almacenar clientes por sala
salas = {}

# Manejo de cliente
def manejar_cliente(cliente_socket, direccion):
    global salas
    try:
        # Pedir nombre y sala inicial
        cliente_socket.send("Ingrese su nombre: ".encode())
        nombre = cliente_socket.recv(1024).decode().strip()
        cliente_socket.send("Ingrese la sala a la que desea unirse: ".encode())
        sala_actual = cliente_socket.recv(1024).decode().strip()

        # Función para cambiar de sala
        def cambiar_sala(nueva_sala):
            nonlocal sala_actual
            if sala_actual in salas:
                # Verificar si el cliente sigue en la sala antes de eliminarlo
                if (cliente_socket, nombre) in salas[sala_actual]:
                    salas[sala_actual].remove((cliente_socket, nombre))
                if not salas[sala_actual]:  # Si la sala queda vacía, eliminarla
                    del salas[sala_actual]

            if nueva_sala not in salas:
                salas[nueva_sala] = []
            salas[nueva_sala].append((cliente_socket, nombre))
            sala_actual = nueva_sala
            cliente_socket.send(f"Cambiaste a la sala: {sala_actual}\n".encode())

        cambiar_sala(sala_actual)  # Unirse a la sala inicial
        print(f"{nombre} se unió a la sala {sala_actual}")

        while True:
            mensaje = cliente_socket.recv(1024).decode().strip()
            if mensaje.lower().startswith("/cambiar "):  # Comando para cambiar de sala
                nueva_sala = mensaje.split(" ", 1)[1]
                cambiar_sala(nueva_sala)
                continue  # Evitar enviar el mensaje de comando a la sala

            print(f"[{sala_actual}] {nombre}: {mensaje}")
            for cliente, cliente_nombre in salas.get(sala_actual, []):
                if cliente != cliente_socket:
                    cliente.send(f"[{sala_actual}] {nombre}: {mensaje}\n".encode())
    except:
        print(f"{nombre} en sala {sala_actual} desconectado")
        if sala_actual in salas:
            # Verificar si el cliente sigue en la sala antes de eliminarlo
            if (cliente_socket, nombre) in salas[sala_actual]:
                salas[sala_actual].remove((cliente_socket, nombre))
            if not salas[sala_actual]:  # Si la sala queda vacía, eliminarla
                del salas[sala_actual]
        cliente_socket.close()

# Configuración del servidor
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind(("192.168.106.89", 12345))
servidor.listen(5)
print("Servidor en espera de conexiones...")

while True:
    cliente_socket, direccion = servidor.accept()
    hilo = threading.Thread(target=manejar_cliente, args=(cliente_socket, direccion))
    hilo.start()