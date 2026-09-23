import duckdb
import polars as pl

from semestre_vii.mineria_de_datos import DATA_DIR

path_albums = DATA_DIR / "albums.csv"
path_artists = DATA_DIR / "artists.csv"
path_features = DATA_DIR / "features.csv"
path_popularity = DATA_DIR / "popularity.csv"

print(f"Loading data from {DATA_DIR}")

con = duckdb.connect()


"""
PUNTO 1)

Aquí ando cargando los datos desde un csv
después cree la tabla en memoria y luego la convertí a un dataframe de polars
"""


def create_table(path):

    table_name = path.stem

    con.sql(f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{path}')")

    df = con.sql(f"SELECT * FROM {table_name}").pl()

    return df


df_albums = create_table(path_albums)
df_artists = create_table(path_artists)
df_features = create_table(path_features)
df_popularity = create_table(path_popularity)


"""
PUNTO 2)

Describiendo un poco de las tablas y archivos
"""

print("Albums")
con.sql("DESCRIBE albums").show()

print("Artists")
con.sql("DESCRIBE artists").show()

print("Features")
con.sql("DESCRIBE features").show()

print("Popularity")
con.sql("DESCRIBE popularity").show()


"""
PUNTO 3)

La columna que relaciona albums y artists es:

artist_id

albums.artist_id = artists.artist_id
"""


"""
PUNTO 4)

La columna que relaciona features y popularity es:

track_id

features.track_id = popularity.track_id
"""


"""
PUNTO 5)

relacion 1
"""

con.sql("""
    SELECT *
    FROM albums
    JOIN artists USING (artist_id)
    LIMIT 50
""").show(max_rows=50)


"""
PUNTO 6)

relacion 2
"""

con.sql("""
    SELECT *
    FROM features
    JOIN popularity USING (track_id)
    LIMIT 50
""").show(max_rows=50)


"""
PUNTO 7)

Dejando solamente las columnas solicitadas de cada archivo.
"""




artists_final = con.sql("""
    SELECT
        artist_id,
        name,
        name_normalized,
        spotify_followers,
        spotify_popularity
    FROM artists
""")

albums_final = con.sql("""
    SELECT
        album_id,
        title,
        artist_id,
        spotify_id
    FROM albums
""")

features_final = con.sql("""
    SELECT
        track_id,
        spotify_id,
        track_artist,
        title,
        release_year,
        track_age_days
    FROM features
""")

popularity_final = con.sql("""
    SELECT
        track_id,
        streams_total,
        streams_is_estimated,
        playlist_appearances,
        chart_peak_position,
        weeks_on_chart,
        monthly_listeners
    FROM popularity
""")


"""
Generando los archivos con solamente 100 filas para entregar como evidencia.
"""

artists_final.limit(100).write_csv(str(DATA_DIR / "artists_100.csv"))
albums_final.limit(100).write_csv(str(DATA_DIR / "albums_100.csv"))
features_final.limit(100).write_csv(str(DATA_DIR / "features_100.csv"))
popularity_final.limit(100).write_csv(str(DATA_DIR / "popularity_100.csv"))



# ========================== PARTE II EXAMEN ==========================
df_artists_final = artists_final.pl()
df_albums_final = albums_final.pl()
df_features_final = features_final.pl()
df_popularity_final = popularity_final.pl()




"""
1. Los 10 artistas con mas álbumes (artista y cantidad de álbumes)
"""
top_10_artists_with_most_albums = (
    df_albums_final.join(df_artists_final, on="artist_id")
    .group_by("name")
    .agg(pl.count("album_id").alias("album_count"))
    .sort("album_count", descending=True)
    .head(10)
)
print("Top 10 artistas con más álbumes:")
print(top_10_artists_with_most_albums)

"""
2. Muestra el nombre del artista y sus álbumes de: (David Guetta, Maroon 5, Rihanna, Avicii,
Ed Sheeran y AC/DC)
"""

filtro = ["David Guetta", "Maroon 5", "Rihanna", "Avicii", "Ed Sheeran", "AC/DC"]


df_artists_albums = (
    df_albums_final.join(df_artists_final, on="artist_id")
    .filter(pl.col("name").is_in(filtro))
)
print("Artistas y sus álbumes:")
print(df_artists_albums.select(["name", "title"]))


"""
3. Los 50 artistas con mas seguidores (artista y número de seguidores)
"""
top_50_artists_with_most_followers = (
    df_artists_final.select(["name", "spotify_followers"])
    .sort("spotify_followers", descending=True, nulls_last=True)
    .head(50)
)
print("Top 50 artistas con más seguidores:")
print(top_50_artists_with_most_followers)


"""
4. Los 10 artistas mas populares
"""
top_10_artists_with_most_popularity = (
    df_artists_final.select(["name", "spotify_popularity"])
    .sort("spotify_popularity", descending=True, nulls_last=True)
    .head(10)
)
print("Top 10 artistas con más popularidad:")
print(top_10_artists_with_most_popularity)


"""
5. Las 20 canciones mas reproducidas
(nombre del artista, nombre de la canción y reproducciones)
"""

top_20_songs_with_most_streams = (
    df_features_final
    .join(df_popularity_final, on="track_id")
    .select(["track_artist", "title", "streams_total"])
    .sort("streams_total", descending=True, nulls_last=True)
    .head(20)
)

print("Top 20 canciones con más reproducciones:")
print(top_20_songs_with_most_streams)


"""
6. Las 20 canciones mas reproducidas que fueron lanzadas el año en que naciste
"""
nacimiento = 2001
top_20_songs_with_most_streams_birth_year = (
    df_features_final.filter(pl.col("release_year") == nacimiento)
    .join(df_popularity_final, on="track_id")
    .select(["track_artist", "title", "streams_total"])
    .sort("streams_total", descending=True, nulls_last=True)
    .head(20)
)
print(f"Top 20 canciones con más reproducciones lanzadas en {nacimiento}:")
print(top_20_songs_with_most_streams_birth_year)


"""
7. Las 50 canciones mas agregadas a listas de reproducción (nombre de la canción, artista y
cantidad de listas)
"""
top_50_songs_with_most_playlist_adds = (
    df_features_final
    .join(df_popularity_final, on="track_id")
    .select(["track_artist", "title", "playlist_appearances"])
    .sort("playlist_appearances", descending=True, nulls_last=True)
    .head(50)
)

print("Top 50 canciones más agregadas a listas de reproducción:")
print(top_50_songs_with_most_playlist_adds)


"""
8. Las 15 canciones con mas semanas en las listas de popularidad (nombre de la canción,
artista y semanas)
"""
top_15_songs_with_most_weeks_on_chart = (
    df_features_final
    .join(df_popularity_final, on="track_id")
    .select(["track_artist", "title", "weeks_on_chart"])
    .sort("weeks_on_chart", descending=True, nulls_last=True)
    .head(15)
)
print("Top 15 canciones con más semanas en las listas de popularidad:")
print(top_15_songs_with_most_weeks_on_chart)

"""
9. Las 10 canciones que alcanzaron el numero 1 en el año 1999 (nombre de la canción,
artista y reproducciones)
"""
top_10_songs_that_reached_number_1_in_1999 = (
    df_features_final
    .filter(pl.col("release_year") == 1999)
    .join(df_popularity_final, on="track_id")
    .filter(pl.col("chart_peak_position") == 1)
    .select(["track_artist", "title", "streams_total"])
    .sort("streams_total", descending=True, nulls_last=True)
    .head(10)
)
print("Top 10 canciones que alcanzaron el número 1 en 1999:")
print(top_10_songs_that_reached_number_1_in_1999)
