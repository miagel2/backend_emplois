from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os
from flask_cors import CORS  # Import CORS


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # SQLite database file
db = SQLAlchemy(app)

class EmploisDuTemps(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jour = db.Column(db.String(255))
    duree = db.Column(db.String(255))
    debut = db.Column(db.String(255))
    fin = db.Column(db.String(255))
    activite = db.Column(db.String(255))
    salle = db.Column(db.String(255))
    enseignant = db.Column(db.String(255))
    code = db.Column(db.String(255))
    type = db.Column(db.String(255))
    formations = db.Column(db.String(255))


# 1 Create the database tables
with app.app_context():
    db.create_all()

# Route for creating an entry in emplois_du_temps
@app.route('/api/create', methods=['POST'])
def create_entry():
    data = request.get_json()

    new_entry = EmploisDuTemps(
        jour=data['jour'],
        duree=data['duree'],
        debut=data['debut'],
        fin=data['fin'],
        activite=data['activite'],
        salle=data['salle'],
        enseignant=data['enseignant'],
        code=data['code'],
        type=data['type'],
        formations=data['formations']
    )

    db.session.add(new_entry)
    db.session.commit()

    return jsonify({"message": "Entry created successfully"}), 201

# Route to insert data from CSV file
@app.route('/api/insert_local_csv', methods=['GET'])
def insert_local_csv():
    file_path = 'planning.csv'  # Specify the path to your local CSV file

    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    try:
        # Read CSV file into a DataFrame
        df = pd.read_csv(file_path, delimiter=';')

        # Insert data into the database
        for _, row in df.iterrows():
            new_entry = EmploisDuTemps(
                jour=row['Jour'],
                duree=row['Durée (h)'],
                debut=row['Début'],
                fin=row['Fin'],
                activite=row['Activité'],
                salle=row['Salles'],
                enseignant=row['Enseignants'],
                code=row['Code'],
                type=row['Type'],
                formations=row['Formations']
            )
            db.session.add(new_entry)

        db.session.commit()

        # Return the data with headers
        return df.to_json(orient='records', date_format='iso'), 200

    except Exception as e:
        return jsonify({'error': f'Error inserting data: {str(e)}'}), 500


# Route to get all entries
@app.route('/api/get_all', methods=['GET'])
def get_all_entries():
    entries = EmploisDuTemps.query.all()
    entries_list = []
    for entry in entries:
        entries_list.append({
            'id': entry.id,
            'jour': entry.jour,
            'duree': entry.duree,
            'debut': entry.debut,
            'fin': entry.fin,
            'activite': entry.activite,
            'salle': entry.salle,
            'enseignant': entry.enseignant,
            'code': entry.code,
            'type': entry.type,
            'formations': entry.formations
        })

    if entries_list:
        return jsonify(entries_list), 200  # OK status code
    else:
        return jsonify({'message': 'la base de donnée est vide'}), 404  # Not Found status code

# Route to get entry by ID
@app.route('/api/get/<int:entry_id>', methods=['GET'])
def get_entry_by_id(entry_id):
    entry = EmploisDuTemps.query.get(entry_id)
    if entry:
        return jsonify({
            'id': entry.id,
            'jour': entry.jour,
            'duree': entry.duree,
            'debut': entry.debut,
            'fin': entry.fin,
            'activite': entry.activite,
            'salle': entry.salle,
            'enseignant': entry.enseignant,
            'code': entry.code,
            'type': entry.type,
            'formations': entry.formations
        }), 200  # OK status code
    else:
        return jsonify({'message': 'Entry not found'}), 404  # Not Found status code


if __name__ == '__main__':
    app.run(debug=True)
