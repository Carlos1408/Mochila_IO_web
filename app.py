from flask import Flask, render_template, redirect, url_for, flash, request, send_file
from solucion.Mochila import Mochila
from solucion.Item import Item
from export.PDF import generarPDF
from ast import literal_eval
import werkzeug

app = Flask(__name__)

@app.route('/')
def home():
    return redirect('nuevo-problema')

mochila = None

@app.route('/nuevo-problema', methods = ['GET', 'POST'])
def nuevo_problema():
    if request.method == 'POST':
        nombre = request.form['nombre']
        capacidad = request.form['capacidad']
        cantidad = request.form['cantidad']
        return redirect(f'/ingreso-datos/{nombre}/{capacidad}/{cantidad}')
    return render_template('nuevo_problema.html')

@app.route('/ingreso-datos/<nombre>/<capacidad>/<cantidad>', methods = ['GET', 'POST'])
def ingreso_datos(nombre, capacidad, cantidad):
    if request.method == 'POST':
        items = []
        for i in range(int(cantidad)):
            items.append(Item(request.form[f'nombre{i}'], int(request.form[f'peso{i}']), int(request.form[f'utilidad{i}'])))

        global mochila
        mochila = Mochila(int(capacidad), items)
        mochila.set_nombre(nombre)
        mochila.crear_etapas()
        mochila.resolver()
        return redirect('/respuesta/1')
    return render_template('ingreso_datos.html', nombre = nombre, cantidad = int(cantidad), capacidad = int(capacidad))

@app.route('/respuesta/<indice>')
def respuesta(indice):
    indice = int(indice)
    soluciones = mochila.get_soluciones()
    solucion = soluciones[indice-1]
    return render_template('respuesta.html', solucion = solucion, indice = indice, total_soluciones = len(soluciones))

@app.route('/guardar')
def guardar():
    archivo = open(f'saves\\{mochila.nombre_problema}' + ".txt", "w", encoding="utf-8")
    archivo.write(mochila.get_formulacion_problema_dicc())
    archivo.close()
    archivo = f'saves\\{mochila.nombre_problema}.txt'
    return send_file(archivo, as_attachment=True)

@app.route('/cargar', methods = ['POST'])
def cargar():
    if request.method == 'POST':
        archivo = request.files['archivo']
        contenido = str(archivo.read())[1:]
        formulacion = literal_eval(literal_eval(contenido))
        print(formulacion, type(formulacion))
        return render_template('problema_cargado.html',
                                nombre = formulacion['nombre'],
                                capacidad = formulacion['capacidad'],
                                cantidad = formulacion['cantidad_items'],
                                items = formulacion['items'])

@app.route('/exportar')
def exportar():
    archivo = f'export\\files\\{mochila.nombre_problema}.pdf'
    nombre = mochila.nombre_problema+".pdf"
    generarPDF(archivo, mochila.get_formulacion_problema(), mochila.get_soluciones(), mochila.get_utilidad_neta())
    return send_file(archivo, as_attachment=True)

if __name__ == '__main__':
    app.run(port=3000, debug=True, threaded=True)