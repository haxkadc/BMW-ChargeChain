#!/usr/bin/python3
from flask import Flask, render_template, request
from admin_class import admin
app = Flask(__name__)

app.config['DEBUG'] = True
app.config['LC_ALL'] = "C.UTF-8"
app.config['LANG'] = "C.UTF-8"

@app.route("/")
def fun1():
    return render_template('admin.html')


@app.route('/addColonnina', methods=['POST', 'GET'])
def addColonnina():
	a = admin()
	colonna =request.form['nome']
	citta = request.form['citta']
	indirizzo = request.form['indirizzo']
	fornitore = request.form['fornitore']
	fee = request.form['fee']
	id = request.form['id']
	disp = "true"
	k = a.addColonna(colonna,citta, indirizzo, fornitore, fee, id,disp)
	if(k == "COMMITTED"):
		return render_template('alert.html', command="Colonna aggiunta correttamente", port="5000")
	else:
		return render_template('alert.html', command="Qualcosa è andato storto! Probabilmente hai inserito un id colonna già esistente", port="5000")

@app.route('/removeCol', methods=['POST', 'GET'])
def removeCol():
	a = admin()
	id = request.form['id']
	k = a.removeCol(id)
	if(k == "COMMITTED"):
		return render_template('alert.html', command="Colonna rimossa correttamente", port="5000")
	else:
		return render_template('alert.html', command="Qualcosa è andato storto! sei sicuro che la colonna esista?", port="5000")


@app.route('/rent', methods=['POST', 'GET'])
def rent():
	a = admin()
	id = request.form['id']
	k = a.rent(id,"true")
	if(k == "COMMITTED"):
		return render_template('alert.html', command="Colonna Noleggiata correttamente", port="5000")
	else:
		return render_template('alert.html', command="Qualcosa è andato storto! sei sicuro che la colonna esista o sia disponibile?", port="5000")

@app.route('/cancel', methods=['POST', 'GET'])
def cancel():
	a = admin()
	id = request.form['id']
	k = a.rent(id,"false")
	if(k == "COMMITTED"):
		return render_template('alert.html', command="Colonna Disdetta correttamente", port="5000")
	else:
		return render_template('alert.html', command="Qualcosa è andato storto! sei sicuro che la colonna esista o sia noleggiata?", port="5000")

@app.route('/listCol', methods=['POST', 'GET'])
def listCol():
	a = admin()
	try:
		result = a.listCol()
		if (result == "" or result == " "):
				return render_template('alert.html', command = "Nessuna Colonna inserita", port="5000")
		else:
			return render_template('alert.html', command = result, port="5000")
	except:
		return render_template('alert.html', command = "Nessuna Colonna inserita", port="5000")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
