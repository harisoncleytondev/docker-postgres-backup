from datetime import datetime

def upload():
    agora = datetime.now()
    print(f"[{agora.strftime('%d/%m/%Y %H:%M:%S')}] Realizando upload diário.")