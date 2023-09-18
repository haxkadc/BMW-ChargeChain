#!/usr/bin/python3
from flask import Flask, render_template, request
from admin_class import admin
app = Flask(__name__)

app.config['DEBUG'] = True
app.config['LC_ALL'] = "C.UTF-8"
app.config['LANG'] = "C.UTF-8"

@app.route("/")
def fun1():
    return render_template('driver.html')





@app.route('/rent', methods=['POST', 'GET'])
def rent():
	a = admin()
	id = request.form['id']
	k = a.rent(id,"true")
	if(k == "COMMITTED"):
		return render_template('alert.html', command="Colonna Noleggiata correttamente", port="5012")
	else:
		return render_template('alert.html', command="Qualcosa è andato storto! sei sicuro che la colonna esista o sia disponibile?", port="5012")

@app.route('/cancel', methods=['POST', 'GET'])
def cancel():
	a = admin()
	id = request.form['id']
	k = a.rent(id,"false")
	if(k == "COMMITTED"):
		return render_template('alert.html', command="Colonna Disdetta correttamente", port="5012")
	else:
		return render_template('alert.html', command="Qualcosa è andato storto! sei sicuro che la colonna esista o sia noleggiata?", port="5012")

@app.route('/listCol', methods=['POST', 'GET'])
def listCol():
	a = admin()
	try:
		result = a.listCol()
		if (result == "" or result == " "):
				return render_template('alert.html', command = "Nessuna Colonna inserita", port="5012")
		else:
			return render_template('alert.html', command = result, port="5012")
	except:
		return render_template('alert.html', command = "Nessuna Colonna inserita", port="5012")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="5012")
    
    
