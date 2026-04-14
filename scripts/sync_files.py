import sys
import os

# Esto añade la carpeta raíz al camino de búsqueda de Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.notion_api import get_notion_data
from dotenv import load_dotenv

load_dotenv()

# Leemos las rutas y las convertimos en una lista
DAW_PATHS = os.getenv("DAW_PATHS").split(",")

def sync_check():
    df = get_notion_data()
    notion_songs = df["ProjectName"].tolist()
    
    print("--- CHEQUEO MULTI-DAW ---")
    
    all_missing = []
    
    for path in DAW_PATHS:
        path = path.strip() # Limpiar espacios
        if not os.path.exists(path):
            print(f"⚠️ Alerta: La ruta no existe: {path}")
            continue
            
        print(f"Escaneando: {path}...")
        local_songs = os.listdir(path)
        
        for song in local_songs:
            # Filtramos para ignorar archivos sueltos y quedarnos con carpetas
            if os.path.isdir(os.path.join(path, song)) and song not in notion_songs:
                all_missing.append((song, path))
    
    if all_missing:
        print(f"\n❌ Tienes {len(all_missing)} proyectos NO registrados:")
        for song, location in all_missing:
            print(f"- {song} (en {location})")
    else:
        print("\n✅ Todo en orden. Todos tus proyectos de ambos DAWs están en Notion.")

if __name__ == "__main__":
    sync_check()