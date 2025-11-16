from flask import Flask, render_template, request, jsonify
import yt_dlp
import os
import json

app = Flask(__name__)

# --- Configuración ---
# Los videos se guardarán en una carpeta llamada 'descargas_servidor'
# al lado de tu 'app.py'
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'descargas_servidor')
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# --- Rutas de la App ---

@app.route('/')
def index():
    """ Sirve el archivo principal index.html """
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def handle_download():
    """
    Ruta API que recibe los datos del frontend y ejecuta yt-dlp.
    """
    try:
        # 1. Obtener los datos enviados desde JavaScript
        data = request.json
        url = data.get('url')
        formato = data.get('formato')
        calidad = data.get('calidad')
        nombre = data.get('nombre')

        if not url or not formato or not calidad or not nombre:
            return jsonify({'status': 'error', 'message': 'Error: Faltan datos (url, formato, calidad o nombre).'}), 400

        # 2. Preparar las opciones para yt-dlp
        # Traducimos las opciones del frontend a comandos de yt-dlp
        
        # Opciones base
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'{nombre}.%(ext)s'),
            'noplaylist': not url.lower().includes('playlist'), # Manejar playlists
        }

        # Lógica de Formato y Calidad
        audio_formats = ['mp3', 'wav', 'flac']
        
        if formato in audio_formats:
            # Es Audio
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': formato,
                    'preferredquality': calidad.replace('kbps', ''),
                }],
            })
        else:
            # Es Video (mp4, mkv, avi, webm)
            # Formato de video con la calidad + el mejor audio
            ydl_opts.update({
                'format': f'bestvideo[height<={calidad.replace("p", "")}][ext={formato}]+bestaudio/best[height<={calidad.replace("p", "")}][ext={formato}]/best'
            })


        # 3. Ejecutar la descarga
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # 4. Enviar respuesta de éxito
        message = f"Descarga de '{nombre}' completada. Guardado en (servidor): {DOWNLOAD_FOLDER}"
        return jsonify({'status': 'success', 'message': message})

    except Exception as e:
        # 5. Enviar respuesta de error
        print(f"Error en yt-dlp: {e}") # Para debugging en la consola de Python
        return jsonify({'status': 'error', 'message': f'Error en el servidor: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)
