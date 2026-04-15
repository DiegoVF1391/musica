import pandas as pd

def apply_prioritization_engine(df, target_album="Depre"):
    if df.empty:
        return df

    # NUEVO PIPELINE PROFESIONAL
    status_weights = {
        "Terminada": 12,
        "Masterización": 11,
        "Mezcla": 11,
        "Grabación": 10,
        "Grabar voz": 10, # Alias para lo que pusiste
        "Producción/Arreglos": 8,
        "Producción": 8,
        "Escritura/Compos": 6,
        "Falta letra": 6,
        "Idea/Boceto": 3,
        "Idea": 3,
        "Sin Estado": 0
    }

    # Asignar peso. Si no existe el estado, ponemos 1 para que no desaparezca
    df['Progress_Score'] = df['Status'].map(status_weights).fillna(1)

    # REGLA DE NEGOCIO: El Rating importa, pero la cercanía al final es clave
    # Le damos un poco más de peso al progreso para que "termines" cosas
    df['Final_Priority'] = (df['Rating_Num'] * 1.5) + (df['Progress_Score'] * 1.0)

    # Filtro de Album y Calidad
    mask_album = df['Album'].apply(lambda x: any(target_album.lower() in str(a).lower() for a in x))
    mask_quality = df['Rating_Num'] >= 3
    mask_not_finished = (df['Status'] != "En plataformas") & (df['Status'] != "Terminada")

    elite_df = df[mask_album & mask_quality & mask_not_finished].copy()
    elite_df = elite_df.sort_values(by=['Final_Priority', 'Rating_Num'], ascending=False)

    return elite_df