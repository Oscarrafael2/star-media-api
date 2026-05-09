from fastapi import FastAPI
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
    StreamingResponse
)
from fastapi.middleware.cors import CORSMiddleware

import yt_dlp
import requests

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PAGINA PRINCIPAL
@app.get("/", response_class=HTMLResponse)
def inicio():

    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


# FUNCION PARA FORMATEAR VIDEOS
def formatear_video(v):

    video_id = v.get("id")

    return {
        "title": v.get("title", "Sin título"),

        "duration": v.get("duration", 0),

        "thumbnail": v.get("thumbnail") or (
            f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
        ),

        "url":
        f"/stream?url=https://youtube.com/watch?v={video_id}",

        "download":
        f"/download?url=https://youtube.com/watch?v={video_id}",

        "channel": v.get("uploader", "Desconocido"),

        "views": v.get("view_count", 0)
    }


# BUSCADOR
@app.get("/buscar")
def buscar(q: str):

    ydl_opts = {
        "quiet": True
    }

    resultados = []

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                f"ytsearch10:{q}",
                download=False
            )

        if "entries" not in info:
            return []

        for v in info["entries"]:

            if not v:
                continue

            resultados.append(
                formatear_video(v)
            )

        return resultados

    except Exception as e:

        return {
            "error": str(e)
        }


# TENDENCIAS
@app.get("/trending")
def trending():

    ydl_opts = {
        "quiet": True
    }

    resultados = []

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                "https://www.youtube.com/feed/trending",
                download=False
            )

        if "entries" not in info:
            return []

        for v in info["entries"][:20]:

            if not v:
                continue

            resultados.append(
                formatear_video(v)
            )

        return resultados

    except Exception as e:

        return {
            "error": str(e)
        }


# STREAM VIDEO
@app.get("/stream")
def stream(url: str):

    ydl_opts = {
        "quiet": True,
        "format": "best"
    }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

            video_url = info["url"]

        return RedirectResponse(video_url)

    except Exception as e:

        return {
            "error": str(e)
        }


# DESCARGAR VIDEO
@app.get("/download")
def download(url: str):

    ydl_opts = {
        "quiet": True,
        "format": "best"
    }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

            video_url = info["url"]

            titulo = info.get(
                "title",
                "video"
            ).replace("/", "_")

        r = requests.get(
            video_url,
            stream=True
        )

        return StreamingResponse(
            r.iter_content(chunk_size=1024),
            media_type="video/mp4",
            headers={
                "Content-Disposition":
                f'attachment; filename="{titulo}.mp4"'
            }
        )

    except Exception as e:

        return {
            "error": str(e)
        }
