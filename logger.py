import datetime
import xml.etree.ElementTree as ET
import os
import threading

# Lock per garantire che più thread non scrivano contemporaneamente sul file
log_lock = threading.Lock()

def log_message(mittente, ip, contenuto, filename="utils/log.xml"):
    """
    Funzione per loggare messaggi in formato XML in un file unificato.
    
    Parametri:
    - mittente: "CLIENT" o "SERVER" (chi ha inviato il messaggio)
    - ip: indirizzo IP dell'interlocutore
    - contenuto: il messaggio/comando inviato
    - filename: percorso del file XML di log (default: utils/log.xml)
    
    Il lock garantisce la thread-safety: se più client sono connessi, 
    i loro log non si sovrascrivono.
    """
    with log_lock:  # Blocca l'accesso al file fino al completamento
        os.makedirs("utils", exist_ok=True)
        
        # Se il file non esiste o è vuoto, crea la struttura base
        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            root = ET.Element("logs")
            tree = ET.ElementTree(root)
            tree.write(filename, encoding="utf-8", xml_declaration=True)

        # Leggi il file XML esistente
        tree = ET.parse(filename)
        root = tree.getroot()
        
        # Crea un nuovo elemento message con tutti i dati
        message = ET.SubElement(root, "message")
        ET.SubElement(message, "timestamp").text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ET.SubElement(message, "sender").text = mittente
        ET.SubElement(message, "ip").text = ip
        ET.SubElement(message, "contenuto").text = contenuto
        
        # Formatta l'XML con indentazione leggibile
        ET.indent(tree, space="    ", level=0)
        tree.write(filename, encoding="utf-8", xml_declaration=True)


def generate_html_log(filename_xml="utils/log.xml", 
                      filename_html="utils/log.html"):
    """
    Genera un file HTML colorato e organizzato che mostra tutti i log
    di comunicazione tra client e server.
    
    Parametri:
    - filename_xml: il file XML da cui leggere i log
    - filename_html: il file HTML da generare
    
    Il colore di ogni entry dipende da chi ha inviato il messaggio:
    - BLU per messaggi dal CLIENT
    - VERDE per messaggi dal SERVER
    
    Include anche un badge che mostra quale applicazione ha registrato il log.
    """
    with log_lock:  # Protegge anche la lettura
        if not os.path.exists(filename_xml):
            return
        
        tree = ET.parse(filename_xml)
        root = tree.getroot()
        
        # Intestazione HTML con stili CSS personalizzati
        html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Log Comunicazioni TCP</title>
    <style>
        body { 
            font-family: 'Courier New', monospace; 
            background-color: #1e1e1e; 
            color: #d4d4d4; 
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 { 
            color: #FFB74D; 
            text-align: center;
            border-bottom: 2px solid #FFB74D;
            padding-bottom: 10px;
        }
        .stats {
            background-color: #2d2d2d;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-around;
        }
        .stat-item {
            text-align: center;
        }
        .stat-number {
            font-size: 24px;
            font-weight: bold;
            color: #4FC3F7;
        }
        .stat-label {
            font-size: 12px;
            color: #888;
        }
        .log-entry { 
            margin: 15px 0; 
            padding: 15px; 
            border-left: 4px solid;
            border-radius: 4px;
            position: relative;
        }
        .log-entry.client-msg { 
            border-color: #4FC3F7; 
            background-color: #1a2a3a; 
        }
        .log-entry.server-msg { 
            border-color: #81C784; 
            background-color: #1a2a1a; 
        }
        .app-badge {
            position: absolute;
            top: 10px;
            right: 10px;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        }
        .app-badge.from-client {
            background-color: #4FC3F7;
            color: #000;
        }
        .app-badge.from-server {
            background-color: #81C784;
            color: #000;
        }
        .field { 
            margin: 8px 0; 
            display: flex;
            align-items: baseline;
        }
        .label { 
            font-weight: bold; 
            color: #FFB74D;
            min-width: 120px;
        }
        .timestamp { color: #CE93D8; }
        .sender { 
            color: #fff;
            font-weight: bold;
        }
        .sender.client { color: #4FC3F7; }
        .sender.server { color: #81C784; }
        .ip { color: #FFB74D; }
        .contenuto { 
            color: #d4d4d4;
            background-color: #2d2d2d;
            padding: 8px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            margin-top: 5px;
        }
        .filter-buttons {
            text-align: center;
            margin: 20px 0;
        }
        .filter-btn {
            background-color: #333;
            color: #fff;
            border: 2px solid #555;
            padding: 8px 16px;
            margin: 0 5px;
            border-radius: 5px;
            cursor: pointer;
            font-family: 'Courier New', monospace;
        }
        .filter-btn:hover {
            background-color: #444;
        }
        .filter-btn.active {
            border-color: #FFB74D;
            background-color: #FFB74D;
            color: #000;
        }
    </style>
    <script>
        function filterLogs(filter) {
            const entries = document.querySelectorAll('.log-entry');
            const buttons = document.querySelectorAll('.filter-btn');
            
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            entries.forEach(entry => {
                if (filter === 'all') {
                    entry.style.display = 'block';
                } else if (filter === 'client') {
                    entry.style.display = entry.classList.contains('client-msg') ? 'block' : 'none';
                } else if (filter === 'server') {
                    entry.style.display = entry.classList.contains('server-msg') ? 'block' : 'none';
                }
            });
        }
    </script>
</head>
<body>
    <h1>📡 Log Comunicazioni TCP Unificato</h1>
"""
        
        # Calcola statistiche
        messages = root.findall("message")
        total_messages = len(messages)
        client_messages = sum(1 for m in messages if m.find("sender").text == "CLIENT")
        server_messages = sum(1 for m in messages if m.find("sender").text == "SERVER")
        
        # Aggiungi pannello statistiche
        html_content += f"""
    <div class="stats">
        <div class="stat-item">
            <div class="stat-number">{total_messages}</div>
            <div class="stat-label">Messaggi Totali</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{client_messages}</div>
            <div class="stat-label">Da Client</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{server_messages}</div>
            <div class="stat-label">Da Server</div>
        </div>
    </div>
    
    <div class="filter-buttons">
        <button class="filter-btn active" onclick="filterLogs('all')">Tutti</button>
        <button class="filter-btn" onclick="filterLogs('client')">Solo Client</button>
        <button class="filter-btn" onclick="filterLogs('server')">Solo Server</button>
    </div>
"""
        
        # Genera ogni entry del log
        for message in messages:
            sender = message.find("sender").text
            tipo_app = message.find("tipo_app").text if message.find("tipo_app") is not None else "N/A"
            
            # Determina la classe CSS in base a chi ha inviato
            status_class = "client-msg" if sender == "CLIENT" else "server-msg"
            sender_class = "client" if sender == "CLIENT" else "server"
            badge_class = "from-client" if tipo_app == "CLIENT" else "from-server"
            
            html_content += f'    <div class="log-entry {status_class}">\n'
            html_content += f'        <div class="field"><span class="label">🕒 TIMESTAMP:</span> <span class="timestamp">{message.find("timestamp").text}</span></div>\n'
            html_content += f'        <div class="field"><span class="label">👤 SENDER:</span> <span class="sender {sender_class}">{sender}</span></div>\n'
            html_content += f'        <div class="field"><span class="label">🌐 IP:</span> <span class="ip">{message.find("ip").text}</span></div>\n'
            html_content += f'        <div class="field"><span class="label">💬 CONTENUTO:</span></div>\n'
            html_content += f'        <div class="contenuto">{message.find("contenuto").text}</div>\n'
            html_content += '    </div>\n'
        
        html_content += """</body>
</html>"""
        
        with open(filename_html, "w", encoding="utf-8") as f:
            f.write(html_content)