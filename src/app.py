# 💬 Nota importante:
# Este paso originalmente intentaba obtener las "audio features" reales desde la API de Spotify.
# Sin embargo, la API ahora requiere autenticación OAuth (no solo client_id y client_secret),
# por lo que este método devuelve error 403 (Forbidden).
# Se invirtieron varias horas intentando resolverlo en un entorno Docker,
# pero el problema no está en el código ni en el contenedor, sino en las nuevas restricciones del API.
# 🚫 Resultado: No es posible continuar con datos reales sin login de usuario.
# ✅ Solución alternativa: usar datos simulados para completar el análisis y los gráficos.



# app.py
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

print ("Running Spotify") 

#Step 1 – Developer Account
# Listo!

# Step 2 – Setup de las variables de entorno
# Listo!

# Step 3 – Cargar variables de entorno del .env file
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# Step 3.1. Autentico Spotify API
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Step 4 – Search Artist and Get Top Tracks 
# for artist (example: "Daft Punk")

artist_name = "Daft Punk"
result = sp.search(q=artist_name, type="artist", limit=1)
artist_id = result["artists"]["items"][0]["id"]

# Step 4.1. – Search Artist and Get Top Tracks 
top_tracks = sp.artist_top_tracks(artist_id)


# Step 5 – Transform Data to DataFrame
# Extract relevant data
data = []
for track in top_tracks["tracks"]:
    data.append({
        "name": track["name"],
        "popularity": track["popularity"],
        "duration_min": round(track["duration_ms"] / 60000, 2),
        "id": track["id"]
    })

df = pd.DataFrame(data)
df = df.sort_values(by="popularity", ascending=False)
df.head(10)


# Step 6 – Scatter plot
sns.scatterplot(data=df, x="duration_min", y="popularity")
plt.title(f"Popularity vs Duration for {artist_name}")
plt.xlabel("Duration (minutes)")
plt.ylabel("Popularity")
plt.show()

plt.savefig("popularity_vs_duration.png")



# Step 7 – Extended Analysis
try:
    valid_ids = [t for t in df["id"].tolist() if t]  # solo IDs válidos
    features = []

    for tid in valid_ids:
        try:
            f = sp.audio_features([tid])
            if f and f[0]:
                features.append(f[0])
        except Exception as e:
            print(f"⚠️ Could not fetch features for {tid}: {e}")

    if features:
        features_df = pd.DataFrame(features)[["danceability", "energy", "valence", "tempo"]]
        final_df = pd.concat([df.head(len(features)).reset_index(drop=True), features_df], axis=1)
        sns.pairplot(final_df[["popularity", "danceability", "energy", "valence", "tempo"]])
        plt.savefig("audio_features_correlation.png")
        print("✅ Audio features retrieved successfully!")
    else:
        print("⚠️ No features retrieved — check API credentials or scopes.")

except Exception as e:
    print(f"⚠️ Error retrieving audio features: {e}")
