# app.py
import sqlite3
import json
from flask import Flask, request, jsonify, Response, send_file, render_template_string
from flask_cors import CORS
from weasyprint import HTML
import os
import tempfile
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
# Permite cereri de la Svelte (de pe alt port/domeniu)
CORS(app, resources={r"/api/*": {"origins": "*"}}) 

DATABASE = os.path.join(os.path.dirname(__file__), 'date.db')

def get_db_conn():
    """ Functie helper pentru conexiunea la DB """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# --- ENDPOINTS PENTRU ADMIN ---
@app.route('/api/admin/init-db', methods=['POST', 'GET'])
def init_db():
    try:
        print("Initializing database...")
        conn = sqlite3.connect(DATABASE)
        script_dir = os.path.dirname(__file__)
        schema_path = os.path.join(script_dir, 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        print("Executing schema script...")
        conn.executescript(schema_sql)
        print("Schema script executed successfully.")
        conn.close()
        print("Database initialized successfully.")
        return jsonify({"success": True, "message": "Database initialized successfully."}), 200
    except Exception as e:
        print(f"Error initializing database: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# app.py
import sqlite3
import json
from flask import Flask, request, jsonify, Response, send_file, render_template_string
from flask_cors import CORS
from weasyprint import HTML
import os
import tempfile
import logging
import datetime
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
# Permite cereri de la Svelte (de pe alt port/domeniu)
CORS(app, resources={r"/api/*": {"origins": "*"}}) 

DATABASE = os.path.join(os.path.dirname(__file__), 'date.db')
BACKUP_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'backups')

if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# --- SCHEDULER ---
scheduler = BackgroundScheduler()
scheduler.start()
backup_job = None

def job_function():
    """The job function that will be executed by the scheduler."""
    with app.app_context():
        backup_db()

# --- ENDPOINTS PENTRU ADMIN ---
@app.route('/api/admin/init-db', methods=['POST', 'GET'])
def init_db():
    try:
        print("Initializing database...")
        conn = sqlite3.connect(DATABASE)
        script_dir = os.path.dirname(__file__)
        schema_path = os.path.join(script_dir, 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        print("Executing schema script...")
        conn.executescript(schema_sql)
        print("Schema script executed successfully.")
        conn.close()
        print("Database initialized successfully.")
        return jsonify({"success": True, "message": "Database initialized successfully."}), 200
    except Exception as e:
        print(f"Error initializing database: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/admin/backup-db', methods=['GET'])
def backup_db():
    try:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_filename = f'date_{timestamp}.db'
        backup_path = os.path.join(BACKUP_DIR, backup_filename)

        conn = sqlite3.connect(DATABASE)
        backup_conn = sqlite3.connect(backup_path)
        with backup_conn:
            conn.backup(backup_conn)
        backup_conn.close()
        conn.close()

        return jsonify({"success": True, "message": f"Database backed up successfully to /static/backups/{backup_filename}"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/admin/restore-backup', methods=['POST'])
def restore_backup():
    try:
        data = request.get_json()
        filename = data.get('filename')
        if not filename:
            return jsonify({"success": False, "message": "Filename not provided"}), 400

        backup_path = os.path.join(BACKUP_DIR, filename)
        if not os.path.exists(backup_path):
            return jsonify({"success": False, "message": "Backup file not found"}), 404

        # Replace the current database with the backup
        os.remove(DATABASE)
        import shutil
        shutil.copy(backup_path, DATABASE)
        
        return jsonify({"success": True, "message": "Database restored successfully"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/admin/backups', methods=['GET'])
def get_backups():
    try:
        backups = []
        for filename in os.listdir(BACKUP_DIR):
            if filename.endswith('.db'):
                path = os.path.join(BACKUP_DIR, filename)
                size = os.path.getsize(path)
                creation_time = os.path.getctime(path)
                backups.append({
                    'filename': filename,
                    'size': size,
                    'created_at': datetime.datetime.fromtimestamp(creation_time).isoformat()
                })
        return jsonify(backups), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/admin/backups/<path:filename>', methods=['DELETE'])
def delete_backup(filename):
    try:
        path = os.path.join(BACKUP_DIR, filename)
        if os.path.exists(path):
            os.remove(path)
            return jsonify({"success": True, "message": "Backup deleted successfully"}), 200
        else:
            return jsonify({"success": False, "message": "Backup not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/admin/backup-schedule', methods=['GET', 'POST'])
def backup_schedule():
    global backup_job
    if request.method == 'GET':
        if backup_job:
            return jsonify({
                'enabled': True,
                'interval': backup_job.trigger.interval.total_seconds() / 3600 # hours
            }), 200
        else:
            return jsonify({'enabled': False}), 200
            
    if request.method == 'POST':
        data = request.get_json()
        enabled = data.get('enabled')
        interval = data.get('interval') # in hours

        if backup_job:
            backup_job.remove()
            backup_job = None

        if enabled and interval:
            backup_job = scheduler.add_job(job_function, 'interval', hours=int(interval))
            return jsonify({"success": True, "message": f"Backup scheduled every {interval} hours"}), 200
        
        return jsonify({"success": True, "message": "Backup schedule disabled"}), 200


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
        SELECT c.cui, c.adresa, r.locatie
        FROM Clienti c
        LEFT JOIN Rapoarte r ON c.id = r.client_id
        WHERE c.id = ?
        ORDER BY r.id DESC
        LIMIT 1
    """, (client_id,))
    details = cursor.fetchone()
    conn.close()
    
    if details and details['locatie']:
        return jsonify(dict(details))
    else:
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT cui, adresa, locatie FROM Clienti WHERE id = ?", (client_id,))
        client_details = cursor.fetchone()
        conn.close()
        if client_details:
            return jsonify(dict(client_details))
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
    manopera = data['manopera']
    raport_id = raport.get('id')
    
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
        
        if raport_id:
            # Pas 2: Actualizeaza raportul principal
            cursor.execute("""
                UPDATE Rapoarte SET
                    numar_raport = ?, tehnician = ?, data = ?, este_revizie = ?, este_reparatie = ?, este_constatare = ?, este_garantie = ?,
                    client_id = ?, client_nume_text = ?, locatie = ?, solicitare_client = ?, utilaj = ?, serie_utilaj = ?, ore_funct = ?,
                    operatii_efectuate = ?, observatii = ?, manopera_ore = ?, km_efectuati = ?, nume_semnatura_client = ?,
                    plecare = ?, destinatie = ?, retur = ?
                WHERE id = ?
            """, (
                raport.get('numar'), raport.get('tehnician'), raport.get('data'),
                raport.get('este_revizie', 0), raport.get('este_reparatie', 0),
                raport.get('este_constatare', 0), raport.get('este_garantie', 0),
                client_id, client_nume, raport.get('locatie'), raport.get('solicitare_client'),
                raport.get('utilaj'), raport.get('serie'), raport.get('ore_funct'),
                raport.get('operatii_efectuate'), raport.get('observatii'),
                raport.get('manopera_ore'), raport.get('km_efectuati'),
                raport.get('nume_semnatura_client'),
                raport.get('plecare'),
                raport.get('destinatie'),
                raport.get('retur'),
                raport_id
            ))
            # Sterge piesele vechi
            cursor.execute("DELETE FROM PieseInlocuite WHERE raport_id = ?", (raport_id,))
            cursor.execute("DELETE FROM PieseNecesare WHERE raport_id = ?", (raport_id,))
            cursor.execute("DELETE FROM Manopera WHERE raport_id = ?", (raport_id,))
        else:
            # Pas 2: Insereaza raportul principal
            cursor.execute("""
                INSERT INTO Rapoarte (
                    numar_raport, tehnician, data, este_revizie, este_reparatie, este_constatare, este_garantie,
                    client_id, client_nume_text, locatie, solicitare_client, utilaj, serie_utilaj, ore_funct,
                    operatii_efectuate, observatii, manopera_ore, km_efectuati, nume_semnatura_client,
                    plecare, destinatie, retur
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                raport.get('numar'), raport.get('tehnician'), raport.get('data'),
                raport.get('este_revizie', 0), raport.get('este_reparatie', 0),
                raport.get('este_constatare', 0), raport.get('este_garantie', 0),
                client_id, client_nume, raport.get('locatie'), raport.get('solicitare_client'),
                raport.get('utilaj'), raport.get('serie'), raport.get('ore_funct'),
                raport.get('operatii_efectuate'), raport.get('observatii'),
                raport.get('manopera_ore'), raport.get('km_efectuati'),
                raport.get('nume_semnatura_client'),
                raport.get('plecare'),
                raport.get('destinatie'),
                raport.get('retur')
            ))
            raport_id = cursor.lastrowid # Aflam ID-ul raportului proaspat creat
        
        # Pas 3: Insereaza piesele inlocuite
        logging.debug(f"Saving {len(piese_inlocuite)} inlocuite parts for raport {raport_id}")
        for piesa in piese_inlocuite:
            if piesa.get('pn') or piesa.get('descriere'):
                pn = piesa.get('pn')
                descriere = piesa.get('descriere', '')
                if not pn and descriere:
                    # Check if a part with this description exists
                    cursor.execute("SELECT pn FROM PieseMaster WHERE descriere = ?", (descriere,))
                    row = cursor.fetchone()
                    if row:
                        pn = row['pn']
                    else:
                        import time
                        pn = f"NO-{descriere[:10]}-{int(time.time() * 1000)}" # Create a unique PN

                if pn:
                    cursor.execute("INSERT OR IGNORE INTO PieseMaster (pn, descriere) VALUES (?, ?)", 
                                   (pn, descriere))
                    if descriere:
                        cursor.execute("UPDATE PieseMaster SET descriere = ? WHERE pn = ?", 
                                       (descriere, pn))

                cursor.execute("""
                    INSERT INTO PieseInlocuite (raport_id, pn, descriere, buc)
                    VALUES (?, ?, ?, ?)
                """, (raport_id, pn, descriere, piesa.get('buc')))
        
        # Pas 4: Insereaza piesele necesare
        logging.debug(f"Saving {len(piese_necesare)} necesare parts for raport {raport_id}")
        for piesa in piese_necesare:
            logging.debug(f"Saving piesa necesara: {piesa}")
            if piesa.get('pn') or piesa.get('descriere'):
                pn = piesa.get('pn')
                descriere = piesa.get('descriere', '')
                if not pn and descriere:
                    # Check if a part with this description exists
                    cursor.execute("SELECT pn FROM PieseMaster WHERE descriere = ?", (descriere,))
                    row = cursor.fetchone()
                    if row:
                        pn = row['pn']
                    else:
                        import time
                        pn = f"NO-{descriere[:10]}-{int(time.time() * 1000)}" # Create a unique PN

                if pn:
                    cursor.execute("INSERT OR IGNORE INTO PieseMaster (pn, descriere) VALUES (?, ?)", 
                                   (pn, descriere))
                    if descriere:
                        cursor.execute("UPDATE PieseMaster SET descriere = ? WHERE pn = ?", 
                                       (descriere, pn))

                cursor.execute("""
                    INSERT INTO PieseNecesare (raport_id, pn, descriere, buc)
                    VALUES (?, ?, ?, ?)
                """, (raport_id, pn, descriere, piesa.get('buc')))

        # Pas 5: Insereaza manopera
        for item in manopera:
            if item.get('tip') and item.get('ore'):
                cursor.execute("""
                    INSERT INTO Manopera (raport_id, tip, ore)
                    VALUES (?, ?, ?)
                """, (raport_id, item.get('tip'), item.get('ore')))

        # Pas 6: Salveaza noua destinatie
        destinatie = raport.get('destinatie')
        if destinatie:
            cursor.execute("INSERT OR IGNORE INTO Destinatii (nume) VALUES (?)", (destinatie,))

        # Pas 7: Salveaza istoricul orelor de functionare
        try:
            if raport.get('utilaj') and raport.get('serie') and client_id:
                client_id_int = int(client_id)
                cursor.execute("SELECT id FROM Utilaje WHERE nume = ? AND serie = ? AND client_id = ?", (raport.get('utilaj'), raport.get('serie'), client_id_int))
                utilaj_row = cursor.fetchone()
                if utilaj_row:
                    utilaj_id = utilaj_row['id']
                else:
                    cursor.execute("INSERT INTO Utilaje (client_id, nume, serie) VALUES (?, ?, ?)", (client_id_int, raport.get('utilaj'), raport.get('serie')))
                    utilaj_id = cursor.lastrowid

                if raport.get('ore_funct'):
                    cursor.execute("INSERT INTO OreFunctHistory (utilaj_id, ore_funct, data, raport_id) VALUES (?, ?, ?, ?)", (utilaj_id, raport.get('ore_funct'), raport.get('data'), raport_id))
        except Exception as e:
            conn.rollback()
            return jsonify({"success": False, "message": f"Error saving equipment: {e}"}), 500

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

    cursor.execute("SELECT * FROM Manopera WHERE raport_id = ?", (raport_id,))
    manopera_data = cursor.fetchall()

    cursor.execute("SELECT * FROM Companie WHERE id = 1")
    companie_data = cursor.fetchone()

    conn.close()

    # Convert data to dictionaries for easier use in template
    raport = dict(raport_data)
    piese_inlocuite = [dict(p) for p in piese_inlocuite_data]
    piese_necesare = [dict(p) for p in piese_necesare_data]
    manopera = [dict(m) for m in manopera_data]
    companie = dict(companie_data) if companie_data else {}

    # Determine report type
    tip_raport = []
    if raport.get('este_revizie'):
        tip_raport.append('REVIZIE')
    if raport.get('este_reparatie'):
        tip_raport.append('REPARATIE')
    if raport.get('este_constatare'):
        tip_raport.append('CONSTATARE')
    if raport.get('este_garantie'):
        tip_raport.append('GARANTIE')
    tip_raport_str = ', '.join(tip_raport)

    # 2. Genereaza PDF-ul din HTML
    try:
        # Incarca template-ul HTML
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'report_template.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            template_str = f.read()

        # Proceseaza logo-ul
        logo_data_uri = None
        if companie.get('logo'):
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'static', companie['logo'])
            if os.path.exists(logo_path):
                import base64
                with open(logo_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                file_extension = os.path.splitext(companie['logo'])[1][1:]
                logo_data_uri = f"data:image/{file_extension};base64,{encoded_string}"

        # Randare HTML cu date
        html_rendered = render_template_string(
            template_str, 
            raport=raport, 
            piese_inlocuite=piese_inlocuite, 
            piese_necesare=piese_necesare,
            manopera=manopera,
            companie=companie,
            tip_raport=tip_raport_str,
            logo_data_uri=logo_data_uri
        )

        # Genereaza PDF
        pdf_bytes = HTML(string=html_rendered, base_url=os.path.dirname(os.path.abspath(__file__))).write_pdf()


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

@app.route('/api/search/destinatii', methods=['GET'])
def search_destinatii():
    """ Cauta destinatii pentru autocomplete """
    query = request.args.get('q', '')
    conn = get_db_conn()
    cursor = conn.cursor()
    if not query:
        cursor.execute("SELECT nume FROM Destinatii ORDER BY nume LIMIT 20")
    else:
        cursor.execute("SELECT nume FROM Destinatii WHERE nume LIKE ? LIMIT 10", (f'%{query}%',))
    destinatii = [row['nume'] for row in cursor.fetchall()]
    conn.close()
    return jsonify(destinatii)

@app.route('/api/search/utilaje', methods=['GET'])
def search_utilaje():
    query = request.args.get('q', '')
    if len(query) < 1:
        return jsonify([])
        
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT nume FROM Utilaje WHERE nume LIKE ? LIMIT 10", (f'%{query}%',))
    utilaje = [row['nume'] for row in cursor.fetchall()]
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
            INSERT INTO Clienti (nume, cui, nr_reg_com, iban, adresa, locatie)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data.get('nume'), data.get('cui'), data.get('nr_reg_com'), data.get('iban'), data.get('adresa'), data.get('locatie')))
        client_id = cursor.lastrowid
        if not client_id:
            cursor.execute("SELECT id FROM Clienti WHERE nume = ?", (data.get('nume'),))
            client_id = cursor.fetchone()['id']

        # Add a default Utilaj for the new client
        cursor.execute("INSERT INTO Utilaje (client_id, nume, serie) VALUES (?, ?, ?)", (client_id, 'Default Utilaj', '0000'))

        conn.commit()

        cursor.execute("SELECT * FROM Clienti WHERE id = ?", (client_id,))
        new_client_data = cursor.fetchone()

        return jsonify(dict(new_client_data)), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/client/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    data = request.json
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Clienti SET
                nume = ?, cui = ?, nr_reg_com = ?, iban = ?, adresa = ?, locatie = ?
            WHERE id = ?
        """, (data.get('nume'), data.get('cui'), data.get('nr_reg_com'), data.get('iban'), data.get('adresa'), data.get('locatie'), client_id))
        conn.commit()
        return jsonify({"success": True, "message": "Client actualizat cu succes"}), 200
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

@app.route('/api/client/<int:client_id>/full_details', methods=['GET'])
def get_client_full_details(client_id):
    conn = get_db_conn()
    cursor = conn.cursor()

    # Get client details
    cursor.execute("SELECT * FROM Clienti WHERE id = ?", (client_id,))
    client = dict(cursor.fetchone())

    # Get client equipment
    cursor.execute("SELECT * FROM Utilaje WHERE client_id = ?", (client_id,))
    utilaje = [dict(row) for row in cursor.fetchall()]

    # Get equipment history
    for utilaj in utilaje:
        cursor.execute("SELECT * FROM OreFunctHistory WHERE utilaj_id = ? ORDER BY data DESC", (utilaj['id'],))
        utilaj['history'] = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return jsonify({'client': client, 'utilaje': utilaje})

@app.route('/api/utilaj/<int:utilaj_id>/history', methods=['GET'])
def get_utilaj_history(utilaj_id):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM OreFunctHistory WHERE utilaj_id = ? ORDER BY data DESC", (utilaj_id,))
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(history)

@app.route('/api/companie', methods=['GET'])
def get_companie():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Companie WHERE id = 1")
    companie = cursor.fetchone()
    conn.close()
    if companie:
        return jsonify(dict(companie))
    else:
        return jsonify({})

@app.route('/api/companie', methods=['POST'])
def update_companie():
    data = request.json
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Companie SET
                nume = ?, adresa = ?, email = ?, telefon = ?, logo = ?
            WHERE id = 1
        """, (data.get('nume'), data.get('adresa'), data.get('email'), data.get('telefon'), data.get('logo')))
        conn.commit()
        return jsonify({"success": True, "message": "Datele companiei au fost actualizate"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()
@app.route('/api/search/piese-descriere', methods=['GET'])
def search_piese_descriere():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
        
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT descriere FROM PieseMaster WHERE descriere LIKE ? LIMIT 10", (f'%{query}%',))
    piese = [row['descriere'] for row in cursor.fetchall()]
    conn.close()
    return jsonify(piese)

@app.route('/api/raport/last-number', methods=['GET'])
def get_last_report_number():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT numar_raport FROM Rapoarte ORDER BY id DESC LIMIT 1")
    last_number = cursor.fetchone()
    conn.close()
    if last_number:
        return jsonify(last_number['numar_raport'])
    else:
        return jsonify(None)

@app.route('/api/rapoarte', methods=['GET'])
def get_rapoarte():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, numar_raport, client_nume_text, data FROM Rapoarte ORDER BY id DESC")
    rapoarte = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(rapoarte)

@app.route('/api/raport/<int:raport_id>', methods=['GET'])
def get_raport(raport_id):
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

    cursor.execute("SELECT * FROM Manopera WHERE raport_id = ?", (raport_id,))
    manopera_data = cursor.fetchall()
    conn.close()

    raport_dict = dict(raport_data)
    raport = {
        'id': raport_dict.get('id'),
        'numar': raport_dict.get('numar_raport'),
        'tehnician': raport_dict.get('tehnician'),
        'data': raport_dict.get('data'),
        'este_revizie': raport_dict.get('este_revizie'),
        'este_reparatie': raport_dict.get('este_reparatie'),
        'este_constatare': raport_dict.get('este_constatare'),
        'este_garantie': raport_dict.get('este_garantie'),
        'client_id': raport_dict.get('client_id'),
        'client': raport_dict.get('client_nume_text'),
        'locatie': raport_dict.get('locatie'),
        'solicitare_client': raport_dict.get('solicitare_client'),
        'utilaj': raport_dict.get('utilaj'),
        'serie': raport_dict.get('serie_utilaj'),
        'ore_funct': raport_dict.get('ore_funct'),
        'operatii_efectuate': raport_dict.get('operatii_efectuate'),
        'observatii': raport_dict.get('observatii'),
        'manopera_ore': raport_dict.get('manopera_ore'),
        'km_efectuati': raport_dict.get('km_efectuati'),
        'nume_semnatura_client': raport_dict.get('nume_semnatura_client'),
        'plecare': raport_dict.get('plecare', ''),
        'destinatie': raport_dict.get('destinatie', ''),
        'retur': raport_dict.get('retur', False)
    }
    piese_inlocuite = [dict(p) for p in piese_inlocuite_data]
    piese_necesare = [dict(p) for p in piese_necesare_data]
    manopera = [dict(m) for m in manopera_data]

    return jsonify({
        'raport': raport,
        'pieseInlocuite': piese_inlocuite,
        'pieseNecesare': piese_necesare,
        'manopera': manopera
    })

@app.route('/api/clients', methods=['GET'])
def get_clients():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Clienti ORDER BY nume")
    clienti = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(clienti)

@app.route('/api/parts', methods=['GET'])
def get_parts():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM PieseMaster ORDER BY pn")
    piese = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(piese)

@app.route('/api/part/<int:part_id>', methods=['PUT'])
def update_part(part_id):
    data = request.json
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE PieseMaster SET
                pn = ?, descriere = ?
            WHERE id = ?
        """, (data.get('pn'), data.get('descriere'), part_id))
        conn.commit()
        return jsonify({"success": True, "message": "Piesa actualizata cu succes"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/client/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        # Check if client is used in any reports
        cursor.execute("SELECT id FROM Rapoarte WHERE client_id = ?", (client_id,))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "Client cannot be deleted, it is used in reports."}), 400
        
        cursor.execute("DELETE FROM Utilaje WHERE client_id = ?", (client_id,))
        cursor.execute("DELETE FROM Clienti WHERE id = ?", (client_id,))
        conn.commit()
        return jsonify({"success": True, "message": "Client deleted successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/part/<int:part_id>', methods=['DELETE'])
def delete_part(part_id):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        # First get the pn of the part
        cursor.execute("SELECT pn FROM PieseMaster WHERE id = ?", (part_id,))
        part = cursor.fetchone()
        if not part:
            return jsonify({"success": False, "message": "Part not found"}), 404
        
        pn = part['pn']
        
        # Check if part is used in any reports
        cursor.execute("SELECT id FROM PieseInlocuite WHERE pn = ?", (pn,))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "Part cannot be deleted, it is used in reports."}), 400
        
        cursor.execute("SELECT id FROM PieseNecesare WHERE pn = ?", (pn,))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "Part cannot be deleted, it is used in reports."}), 400

        cursor.execute("DELETE FROM PieseMaster WHERE id = ?", (part_id,))
        conn.commit()
        return jsonify({"success": True, "message": "Part deleted successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/raport/<int:raport_id>', methods=['DELETE'])
def delete_raport(raport_id):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Rapoarte WHERE id = ?", (raport_id,))
        cursor.execute("DELETE FROM PieseInlocuite WHERE raport_id = ?", (raport_id,))
        cursor.execute("DELETE FROM PieseNecesare WHERE raport_id = ?", (raport_id,))
        conn.commit()
        return jsonify({"success": True, "message": "Raport sters cu succes"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)