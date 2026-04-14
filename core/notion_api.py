import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_notion_data():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    response = requests.post(url, headers=headers)
    data = response.json()
    rows = []
    has_more = True
    next_cursor = None
    
    while has_more:
        # Si hay un cursor, lo pasamos para pedir la siguiente página
        payload = {"start_cursor": next_cursor} if next_cursor else {}
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"❌ Error de Notion API ({response.status_code}): {response.text}")
            break

        if "results" not in data:
            print("❌ Error: La respuesta no contiene 'results'.")
            print("Respuesta completa de Notion:", data)
            return pd.DataFrame()
        
            
        data = response.json()
        results = data.get("results", [])
        
        for page in results:
            props = page["properties"]
            try:
                row = {
                    "Nombre": props["Nombre"]["title"][0]["text"]["content"] if props["Nombre"]["title"] else "Sin Título",
                    "Rating_Raw": props["Rating"]["select"]["name"] if props["Rating"]["select"] else "None",
                    "Status": props["Status"]["status"]["name"] if "Status" in props and props["Status"]["status"] else "Sin Estado",
                    "Genero": props["Género"]["select"]["name"] if props["Género"]["select"] else "None",
                    "Path": props["Dirección"]["rich_text"][0]["plain_text"] if props["Dirección"]["rich_text"] else "",
                    "ProjectName": props["Nombre del proyecto"]["rich_text"][0]["plain_text"] if props["Nombre del proyecto"]["rich_text"] else ""
                }
                rows.append(row)
            except Exception as e:
                continue # Omitimos filas mal formadas para no frenar el proceso

        # Verificamos si hay más datos
        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")
        print(f"📦 Cargadas {len(rows)} canciones...")

    df = pd.DataFrame(rows)
    
    if not df.empty:
        star_map = {"⭐⭐⭐⭐⭐": 5, "⭐⭐⭐⭐": 4, "⭐⭐⭐": 3, "⭐⭐": 2, "⭐": 1, "None": 0}
        df["Rating_Num"] = df["Rating_Raw"].map(star_map).fillna(0)
    
    return df