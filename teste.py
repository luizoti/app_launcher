from pynput import keyboard

def on_press(key):
    try:
        print(f"Tecla pressionada: {key.char}")
    except AttributeError:
        print(f"Tecla especial pressionada: {key}")

def on_release(key):
    print(f"Tecla liberada: {key}")
    # Finaliza o programa se a tecla 'q' for liberada
    if key == keyboard.Key.esc:
        print("Encerrando...")
        return False

# Listener para eventos de teclado
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    print("Pressione qualquer tecla. Pressione ESC para sair.")
    listener.join()

