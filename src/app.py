import os
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

# Select the resource to download
url = "https://en.wikipedia.org/wiki/List_of_Spotify_streaming_records"

# Read all tables from the page into a list of DataFrames
tables = pd.read_html(url)

# Store the first table in a dataframe
df = tables[0]

# Limpieza de datos
# Renombramos columnas si es necesario
df.columns = ["Rank", "Song", "Artist", "Streams (billions)", "Date released", "Reference"]

# Eliminamos notas entre corchetes
df["Song"] = df["Song"].str.replace(r"\[.*?\]", "", regex=True)
df["Artist"] = df["Artist"].str.replace(r"\[.*?\]", "", regex=True)

df = df[df["Streams (billions)"].astype(str).str.contains(r"^\d+(?:\.\d+)?$", na=False)].copy()

# Convertimos Streams a números flotantes
df["Streams (billions)"] = df["Streams (billions)"].astype(float)

# Convertimos fechas a datetime
df["Date released"] = pd.to_datetime(df["Date released"], errors="coerce")

# Create the database
conn = sqlite3.connect("spotify_top_songs.db")

# Create table in SQLite
df.to_sql("top_songs", conn, if_exists="replace", index=False)
cursor = conn.cursor()

# Insert data into the database
cursor.execute("SELECT COUNT(*) FROM top_songs")
print("Rows inserted:", cursor.fetchone()[0])

conn.commit()
conn.close()

# Ordenar y tomar el top 10
top_10 = df.sort_values("Streams (billions)", ascending=False).head(10)

# Gráfico de barras
plt.figure(figsize=(12, 6))
plt.barh(top_10["Song"] + " - " + top_10["Artist"], top_10["Streams (billions)"], color="skyblue")
plt.xlabel("Streams (en billones)")
plt.title("Top 10 canciones más escuchadas")
plt.gca().invert_yaxis()  # Ordenar de mayor a menor
plt.grid(axis="x", linestyle="--", alpha=0.7)
plt.show()

# Contar canciones por artista (limpiar colaboraciones)
df["Main Artist"] = df["Artist"].str.split(" and| with| &|,").str[0]
artist_counts = df["Main Artist"].value_counts().head(10)

# Gráfico de barras (Seaborn)
plt.figure(figsize=(12, 6))
sns.barplot(x=artist_counts.values, y=artist_counts.index, palette="viridis")
plt.xlabel("Número de canciones en el top 100")
plt.title("Artistas con más canciones en el ranking")
plt.grid(axis="x", linestyle="--", alpha=0.5)
plt.show()

# Crear columnas por década
df["Decade"] = (df["Year"] // 10) * 10

# Boxplot
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x="Decade", y="Streams (billions)", palette="pastel")
plt.title("Distribución de streams por década")
plt.xlabel("Década")
plt.ylabel("Streams (billones)")
plt.show()


