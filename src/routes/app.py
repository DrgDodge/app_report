# app.py
import sqlite3
import json
from flask import Flask, request, jsonify, Response, send_file, render_template_string
from flask_cors import CORS
from weasyprint import HTML
import os
import tempfile

app = Flask(__name__)
# Permite cereri de la Svelte (de pe alt port/domeniu)
CORS(app, resources={r"/api/*": {"origins": "*"}}) 

DATABASE = 'date.db'

def get_db_conn():
    """ Functie helper pentru conexiunea la DB """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# --- ENDPOINTS PENTRU ADMIN ---
@app.route('/api/admin/init-db', methods=['POST'])
def init_db():
    try:
        conn = sqlite3.connect(DATABASE)
        script_dir = os.path.dirname(__file__)
        schema_path = os.path.join(script_dir, 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.close()
        return jsonify({"success": True, "message": "Database initialized successfully."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/admin/backup-db', methods=['GET'])
def backup_db():
    try:
        # Create a temporary backup file
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            temp_db_path = tmp_file.name

        conn = sqlite3.connect(DATABASE)
        backup_conn = sqlite3.connect(temp_db_path)
        with backup_conn: 
            conn.backup(backup_conn)
        backup_conn.close()
        conn.close()

        # Send the file and then delete it
        response = send_file(temp_db_path, as_attachment=True, download_name='date.db')
        os.remove(temp_db_path) # Clean up the temporary file
        return response

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# --- ENDPOINTS PENTRU AUTACOMPLETE ---

@app.route('/api/search/clienti', methods=['GET'])
def search_clienti():
    """ Cauta clienti pentru autocomplete """
    query = request.args.get('q', '')
    if len(query) < 1:
        return jsonify([])
        
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nume FROM Clienti WHERE nume LIKE ? LIMIT 10", (f'%{query}%',))
    clienti = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(clienti)

@app.route('/api/search/piese', methods=['GET'])
def search_piese():
    """ Cauta piese (P/N sau descriere) pentru autocomplete """
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
        
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT pn, descriere FROM PieseMaster WHERE pn LIKE ? OR descriere LIKE ? LIMIT 10", 
                   (f'%{query}%', f'%{query}%'))
    piese = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(piese)

@app.route('/api/client/<int:client_id>/details', methods=['GET'])
def get_client_details(client_id):
    """ Returneaza ultimele date folosite pentru un client (locatie, utilaj, etc.) """
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT locatie
        FROM Rapoarte 
        WHERE client_id = ? 
        ORDER BY id DESC 
        LIMIT 1
    """, (client_id,))
    details = cursor.fetchone()
    conn.close()
    
    if details:
        return jsonify(dict(details))
    else:
        return jsonify({})

# --- ENDPOINT PENTRU CREARE RAPORT ---

@app.route('/api/raport', methods=['POST'])
def create_raport():
    """ Salveaza un raport nou in baza de date """
    data = request.json
    raport = data['raport']
    piese_inlocuite = data['pieseInlocuite']
    piese_necesare = data['pieseNecesare']
    
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        # Pas 1: Gestioneaza clientul. Daca e nou, il adaugam.
        client_id = raport.get('client_id')
        client_nume = raport.get('client')
        
        if not client_id and client_nume:
            # Incearca sa gasesti clientul dupa nume
            cursor.execute("SELECT id FROM Clienti WHERE nume = ?", (client_nume,))
            row = cursor.fetchone()
            if row:
                client_id = row['id']
            else:
                # Daca nu exista, creeaza-l
                cursor.execute("INSERT OR IGNORE INTO Clienti (nume) VALUES (?)", (client_nume,))
                client_id = cursor.lastrowid
                if not client_id:
                    cursor.execute("SELECT id FROM Clienti WHERE nume = ?", (client_nume,))
                    client_id = cursor.fetchone()['id']
        
        # Pas 2: Insereaza raportul principal
        cursor.execute("""
            INSERT INTO Rapoarte (
                numar_raport, tehnician, data, este_revizie, este_reparatie, este_constatare, este_garantie,
                client_id, client_nume_text, locatie, solicitare_client, utilaj, serie_utilaj, ore_funct,
                operatii_efectuate, observatii, manopera_ore, km_efectuati, nume_semnatura_client
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            raport.get('numar'), raport.get('tehnician'), raport.get('data'),
            raport.get('este_revizie', 0), raport.get('este_reparatie', 0),
            raport.get('este_constatare', 0), raport.get('este_garantie', 0),
            client_id, client_nume, raport.get('locatie'), raport.get('solicitare_client'),
            raport.get('utilaj'), raport.get('serie'), raport.get('ore_funct'),
            raport.get('operatii_efectuate'), raport.get('observatii'),
            raport.get('manopera_ore'), raport.get('km_efectuati'),
            raport.get('nume_semnatura_client')
        ))
        
        raport_id = cursor.lastrowid # Aflam ID-ul raportului proaspat creat
        
        # Pas 3: Insereaza piesele inlocuite
        for piesa in piese_inlocuite:
            if piesa.get('pn') or piesa.get('descriere'): # Adauga doar daca e ceva completat
                cursor.execute("""
                    INSERT INTO PieseInlocuite (raport_id, pn, descriere, buc)
                    VALUES (?, ?, ?, ?)
                """, (raport_id, piesa.get('pn'), piesa.get('descriere'), piesa.get('buc')))
        
        # Pas 4: Insereaza piesele necesare
        for piesa in piese_necesare:
             if piesa.get('pn') or piesa.get('descriere'):
                cursor.execute("""
                    INSERT INTO PieseNecesare (raport_id, pn, descriere, buc)
                    VALUES (?, ?, ?, ?)
                """, (raport_id, piesa.get('pn'), piesa.get('descriere'), piesa.get('buc')))

        conn.commit()
        return jsonify({"success": True, "raport_id": raport_id, "message": "Raport salvat cu succes"}), 201
        
    except Exception as e:
        conn.rollback() # Anuleaza tranzactia daca a aparut o eroare
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# --- ENDPOINT PENTRU GENERARE PDF ---
@app.route('/api/raport/<int:raport_id>/pdf')
def get_report_pdf(raport_id):
    # 1. Extrage datele din DB pentru raport_id
    conn = get_db_conn()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Rapoarte WHERE id = ?", (raport_id,))
    raport_data = cursor.fetchone()
    
    if not raport_data:
        return "Raport negasit", 404
        
    cursor.execute("SELECT * FROM PieseInlocuite WHERE raport_id = ?", (raport_id,))
    piese_inlocuite_data = cursor.fetchall()
    
    cursor.execute("SELECT * FROM PieseNecesare WHERE raport_id = ?", (raport_id,))
    piese_necesare_data = cursor.fetchall()
    conn.close()

    # Convert data to dictionaries for easier use in template
    raport = dict(raport_data)
    piese_inlocuite = [dict(p) for p in piese_inlocuite_data]
    piese_necesare = [dict(p) for p in piese_necesare_data]

    # 2. Genereaza PDF-ul din HTML
    try:
        # Incarca template-ul HTML
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'report_template.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            template_str = f.read()

        # Randare HTML cu date
        html_rendered = render_template_string(
            template_str, 
            raport=raport, 
            piese_inlocuite=piese_inlocuite, 
            piese_necesare=piese_necesare
        )

        # Genereaza PDF
        pdf_bytes = HTML(string=html_rendered).write_pdf()

        # 3. Returneaza PDF-ul
        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={'Content-Disposition': f'inline; filename=Raport_{raport_id}.pdf'}
        )

    except Exception as e:
        # Log the exception for debugging
        print(f"Error generating PDF: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/search/utilaje', methods=['GET'])
def search_utilaje():
    query = request.args.get('q', '')
    if len(query) < 1:
        return jsonify([])
        
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT utilaj FROM Rapoarte WHERE utilaj LIKE ? LIMIT 10", (f'%{query}%',))
    utilaje = [row['utilaj'] for row in cursor.fetchall()]
    conn.close()
    return jsonify(utilaje)

@app.route('/api/search/serii', methods=['GET'])
def search_serii():
    query = request.args.get('q', '')
    utilaj = request.args.get('utilaj', '')
    if len(query) < 1:
        return jsonify([])
        
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT serie_utilaj FROM Rapoarte WHERE serie_utilaj LIKE ? AND utilaj = ? LIMIT 10", (f'%{query}%', utilaj))
    serii = [row['serie_utilaj'] for row in cursor.fetchall()]
    conn.close()
    return jsonify(serii)

@app.route('/api/search/ore-funct', methods=['GET'])
def search_ore_funct():
    utilaj = request.args.get('utilaj', '')
    serie = request.args.get('serie', '')
    
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT ore_funct FROM Rapoarte WHERE utilaj = ? AND serie_utilaj = ? ORDER BY id DESC LIMIT 1", (utilaj, serie))
    ore_funct = cursor.fetchone()
    conn.close()
    
    if ore_funct:
        return jsonify(ore_funct['ore_funct'])
    else:
        return jsonify(None)

@app.route('/api/client/<int:client_id>/contact', methods=['GET'])
def get_client_contact(client_id):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT nume_semnatura_client FROM Rapoarte WHERE client_id = ? ORDER BY id DESC LIMIT 1", (client_id,))
    contact = cursor.fetchone()
    conn.close()
    
    if contact:
        return jsonify(contact['nume_semnatura_client'])
    else:
        return jsonify(None)

@app.route('/api/client', methods=['POST'])
def create_client():
    data = request.json
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Clienti (nume, cui, nr_reg_com, iban, adresa)
            VALUES (?, ?, ?, ?, ?)
        """, (data.get('nume'), data.get('cui'), data.get('nr_reg_com'), data.get('iban'), data.get('adresa')))
        client_id = cursor.lastrowid
        conn.commit()
        return jsonify({"success": True, "client_id": client_id, "message": "Client created successfully"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/client/<int:client_id>/utilaje', methods=['GET'])
def get_client_utilaje(client_id):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Utilaje WHERE client_id = ?", (client_id,))
    utilaje = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(utilaje)

@app.route('/api/utilaj/<int:utilaj_id>/history', methods=['GET'])
def get_utilaj_history(utilaj_id):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM OreFunctHistory WHERE utilaj_id = ? ORDER BY data DESC", (utilaj_id,))
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(history)

if __name__ == '__main__':
    app.run(debug=True, port=5000)