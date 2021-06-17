from flask import Flask, render_template, redirect, url_for, flash, request
from solucion.Mochila import Mochila
from solucion.Item import Item

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

soluciones = None

@app.route('/nuevo-problema', methods = ['GET', 'POST'])
def nuevo_problema():
    global soluciones
    soluciones = None
    print(request)
    if request.method == 'POST':
        nombre = request.form['nombre']
        capacidad = request.form['capacidad']
        cantidad = request.form['cantidad']
        # print(nombre, capacidad, cantidad)
        return redirect(f'/ingreso-datos/{nombre}/{capacidad}/{cantidad}')
    return render_template('nuevo_problema.html')

@app.route('/ingreso-datos/<nombre>/<capacidad>/<cantidad>', methods = ['GET', 'POST'])
def ingreso_datos(nombre, capacidad, cantidad):
    if request.method == 'POST':
        items = []
        for i in range(int(cantidad)):
            items.append(Item(request.form[f'nombre{i}'], int(request.form[f'peso{i}']), int(request.form[f'utilidad{i}'])))

        mochila = Mochila(int(capacidad), items)
        mochila.set_nombre(nombre)
        mochila.crear_etapas()
        mochila.resolver()
        global soluciones
        soluciones = mochila.get_soluciones()
        return redirect('/respuesta/1')
    return render_template('ingreso_datos.html', nombre = nombre, cantidad = int(cantidad), capacidad = int(capacidad))

@app.route('/respuesta/<indice>')
def respuesta(indice):
    indice = int(indice)
    print(soluciones)
    solucion = soluciones[indice-1]
    return render_template('respuesta.html', solucion = solucion, indice = indice, total_soluciones = len(soluciones))

if __name__ == '__main__':
    app.run(port=3000, debug=True, threaded=True)