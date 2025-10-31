from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_code():
    codigo = request.form['codigo']
    mensaje = "Simulación completada ✅"
    return render_template('index.html', codigo=codigo, mensaje=mensaje)

if __name__ == '__main__':
    app.run(debug=True)
