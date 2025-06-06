import platform
import os
import shutil

def beep(frequency=1000, duration=500):
    """
    Reproduz um beep sonoro compatível com Windows, Linux (com sox) e fallback com terminal.
    """
    sistema = platform.system()

    if sistema == "Windows":
        try:
            import winsound
            winsound.Beep(frequency, duration)
        except Exception:
            print("\a")  # fallback no terminal

    elif sistema == "Linux":
        if shutil.which("play"):
            os.system(f'play -nq -t alsa synth {duration / 1000} sine {frequency} 2> /dev/null')
        else:
            print("\a")  # fallback no terminal
    else:
        print("\a")  # fallback genérico
