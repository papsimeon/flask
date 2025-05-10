from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///etudiants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Etudiant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    sexe = db.Column(db.String(10))
    option = db.Column(db.String(100))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    etudiants = Etudiant.query.all()
    return render_template('index.html', etudiants=etudiants)

@app.route('/add', methods=['POST'])
def add():
    nom = request.form['nom']
    prenom = request.form['prenom']
    sexe = request.form['sexe']
    option = request.form['option']
    new_etudiant = Etudiant(nom=nom, prenom=prenom, sexe=sexe, option=option)
    db.session.add(new_etudiant)
    db.session.commit()
    return redirect('/')


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    etudiant = Etudiant.query.get_or_404(id)
    if request.method == 'POST':
        etudiant.nom = request.form['nom']
        etudiant.prenom = request.form['prenom']
        etudiant.sexe = request.form['sexe']
        etudiant.option = request.form['option']
        db.session.commit()
        return redirect('/')
    return render_template('update.html', etudiant=etudiant)

@app.route('/delete/<int:id>')
def delete(id):
    etu = Etudiant.query.get(id)
    db.session.delete(etu)
    db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
