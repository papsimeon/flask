from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from flask import send_file
from io import BytesIO
from flask import render_template_string
from xhtml2pdf import pisa
from flask import Flask, render_template, request, redirect, url_for
import plotly.graph_objects as go
from collections import Counter
from flask import render_template
import plotly.graph_objs as go


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///etudiants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definition du model Etudiant
class Etudiant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    sexe = db.Column(db.String(10))
    option = db.Column(db.String(100))

with app.app_context():
    db.create_all()

# Creation de la route d'accueil
@app.route('/')
def index():
    etudiants = Etudiant.query.all()
    return render_template('index.html', etudiants=etudiants)

# Creation de la route pour l'ajout des données
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

# Creation de la route pour la mise à jour des données
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



@app.route('/dashboard')
def dashboard():
    data = Etudiant.query.all()

    option_count = Counter([e.option for e in data])
    sexe_count = Counter([e.sexe for e in data])

    # Graphique 1 : Répartition par filière
    fig1 = go.Figure(data=[go.Pie(
        labels=list(option_count.keys()),
        values=list(option_count.values()),
        textinfo='value',  # uniquement le total
        insidetextorientation='radial',
        marker=dict(line=dict(color='#000000', width=1))
    )])
    fig1.update_layout(
        title_text='Répartition par filière',
        height=350,
        width=450
    )

    # Graphique 2 : Répartition par sexe
    fig2 = go.Figure(data=[go.Pie(
        labels=list(sexe_count.keys()),
        values=list(sexe_count.values()),
        textinfo='value',
        insidetextorientation='radial',
        marker=dict(line=dict(color='#000000', width=1))
    )])
    fig2.update_layout(
        title_text='Répartition par sexe',
        height=350,
        width=450
    )

    graph1_html = fig1.to_html(full_html=False)
    graph2_html = fig2.to_html(full_html=False)
    total_etudiants = len(data)

    return render_template("dashboard.html",
                           graph1=graph1_html,
                           graph2=graph2_html,
                           total_etudiants=total_etudiants)


    return render_template(
        "dashboard.html",
        graph1=fig1.to_html(full_html=False),
        graph2=fig2.to_html(full_html=False)
    )

    
#Creation des routes pour l'export des données
@app.route('/export-excel')
def export_excel():
    etudiants = Etudiant.query.all()
    data = [{
        "ID": e.id,
        "Nom": e.nom,
        "Prénom": e.prenom,
        "Sexe": e.sexe,
        "Option": e.option
    } for e in etudiants]

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Étudiants')
    output.seek(0)
    
    return send_file(output, download_name="etudiants.xlsx", as_attachment=True)

# Creation de la route pour l'export PDF
@app.route('/export-pdf')
def export_pdf():
    etudiants = Etudiant.query.all()

    html = render_template_string("""
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; font-size: 12px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #000; padding: 8px; text-align: center; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h2 style="text-align: center;">Liste des Étudiants</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th><th>Nom</th><th>Prénom</th><th>Sexe</th><th>Option</th>
                </tr>
            </thead>
            <tbody>
                {% for e in etudiants %}
                <tr>
                    <td>{{ e.id }}</td>
                    <td>{{ e.nom }}</td>
                    <td>{{ e.prenom }}</td>
                    <td>{{ e.sexe }}</td>
                    <td>{{ e.option }}</td>f
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    """, etudiants=etudiants)

    result = BytesIO()
    pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=result)
    result.seek(0)
    return send_file(result, download_name="etudiants.pdf", as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
