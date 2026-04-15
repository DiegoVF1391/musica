import pandas as pd
from datetime import datetime
import os

HISTORY_FILE = "data/progreso_history.csv"

def save_snapshot(df):
    if df.empty:
        return
    
    # Creamos carpeta data si no existe
    if not os.path.exists("data"):
        os.makedirs("data")
        
    # Solo nos interesa: Fecha, Nombre, Status y Rating
    snapshot = df[["Nombre", "Status", "Rating_Num"]].copy()
    snapshot["Fecha_Snapshot"] = datetime.now().strftime("%Y-%m-%d")
    
    if os.path.exists(HISTORY_FILE):
        history_df = pd.read_csv(HISTORY_FILE)
        # Solo añadimos si es un día nuevo para no duplicar
        if snapshot["Fecha_Snapshot"].iloc[0] not in history_df["Fecha_Snapshot"].values:
            history_df = pd.concat([history_df, snapshot], ignore_index=True)
            history_df.to_csv(HISTORY_FILE, index=False)
    else:
        snapshot.to_csv(HISTORY_FILE, index=False)

def get_stagnant_songs(current_df):
    # Esta función te dirá qué canciones llevan más de 7 días sin cambiar de Status
    if not os.path.exists(HISTORY_FILE):
        return []
    
    history_df = pd.read_csv(HISTORY_FILE)
    # Lógica para comparar el status de hace una semana vs hoy
    # (La implementaremos en el Dashboard en el siguiente paso)
    return history_df