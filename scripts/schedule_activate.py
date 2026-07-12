from apscheduler.schedulers.blocking import BlockingScheduler
from scripts.drive_upload import upload
from scripts.docker import list_containers
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

scheduler = BlockingScheduler()

folder = "temp"

def _del_files():
   for file in os.listdir(folder):
      path = os.path.join(folder, file)

      if os.path.isfile(path):
         os.remove(path)

def backup():
   os.makedirs("temp", exist_ok=True)
 
   _del_files()
   list_containers();

   files = [
        os.path.join(folder, file)
        for file in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, file))
    ]

   with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(upload, file) for file in files]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Erro no upload: {e}")

   _del_files()

def start():
    scheduler.add_job(backup, "cron", hour=3, minute=0)
    print("Agendador iniciado.")
    scheduler.start()