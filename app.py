from flask import Flask, render_template, redirect, url_for, flash, request, send_file, make_response
from solucion.Mochila import Mochila
from solucion.Item import Item
from export.PDF import generarPDF
from ast import literal_eval
import werkzeug

app = Flask(__name__)

@app.route('/')
def home():
    return redirect('nuevo-problema')

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
    dir(request)
    if request.method == 'POST':
        items = []
        for i in range(int(cantidad)):
            items.append(Item(request.form[f'nombre{i}'], int(request.form[f'peso{i}']), int(request.form[f'utilidad{i}'])))
            
        mochila = Mochila(int(capacidad), items)
        mochila.set_nombre(nombre)
        mochila.crear_etapas()
        mochila.resolver()
        response = make_response(redirect('/respuesta/1'))
        response.set_cookie('nombre_problema', str(mochila.nombre_problema))
        response.set_cookie('soluciones', str(mochila.get_soluciones()))
        response.set_cookie('formulacion', str(mochila.get_formulacion_problema()))
        response.set_cookie('utilidad_neta', str(mochila.get_utilidad_neta()))
        response.set_cookie('formulacion_dic', str(mochila.get_formulacion_problema_dicc()))
        # return redirect('/respuesta/1')
        return response
    return render_template('ingreso_datos.html', nombre = nombre, cantidad = int(cantidad), capacidad = int(capacidad))

@app.route('/respuesta/<indice>')
def respuesta(indice):
    indice = int(indice)
    soluciones = literal_eval(request.cookies.get('soluciones'))
    print(soluciones, type(soluciones))
    solucion = soluciones[indice-1]
    return render_template('respuesta.html', solucion = solucion, indice = indice, total_soluciones = len(soluciones))

@app.route('/guardar')
def guardar():
    formulacion = request.cookies.get('formulacion_dic')
    nombre_problema = request.cookies.get('nombre_problema')
    print('formulacion ', formulacion, type(formulacion))
    print('nombre problema', nombre_problema, type(nombre_problema))
    archivo = open(f'saves\\{nombre_problema}' + ".txt", "w", encoding="utf-8")
    archivo.write(formulacion)
    archivo.close()
    archivo = f'saves\\{nombre_problema}.txt'
    return send_file(archivo, as_attachment=True)

@app.route('/cargar', methods = ['POST'])
def cargar():
    if request.method == 'POST':
        archivo = request.files['archivo']
        contenido = str(archivo.read())[1:]
        formulacion = literal_eval(literal_eval(contenido))
        print('formulacion ', formulacion, type(formulacion))
        return render_template('problema_cargado.html',
                                nombre = formulacion['nombre'],
                                capacidad = formulacion['capacidad'],
                                cantidad = formulacion['cantidad_items'],
                                items = formulacion['items'])

@app.route('/exportar')
def exportar():
    nombre_problema = request.cookies.get('nombre_problema')+".pdf"
    formulacion = literal_eval(request.cookies.get('formulacion'))
    soluciones = literal_eval(request.cookies.get('soluciones'))
    utilidad_neta = literal_eval(request.cookies.get('utilidad_neta'))
    archivo = f'export\\files\\{nombre_problema}.pdf'
    print('formulacion ', formulacion, type(formulacion))
    print('soluciones', soluciones, type(soluciones))
    print('utilidad_neta ', utilidad_neta, type(utilidad_neta))
    generarPDF(archivo, formulacion, soluciones, utilidad_neta)
    return send_file(archivo, as_attachment=True)

if __name__ == '__main__':
    app.run(port=3000, debug=True, threaded=True)