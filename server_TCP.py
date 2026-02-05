import socket
import datetime
import threading
from logger import log_message, generate_html_log
import os

class Colori:
    RESET = "\033[0m"
    ROSSO = "\033[91m"
    VERDE = "\033[92m"
    GIALLO = "\033[93m"
    BLU = "\033[94m"
    ROSA = "\033[95m"
    CELESTE = "\033[96m"

os.system("") # Abilita i colori

def broadcast_server_presence(server_ip, tcp_port):
    """Trasmette in broadcast l'IP del server sulla rete locale"""
    BROADCAST_PORT = 37020
    TCP_PORT = tcp_port
    
    # Crea socket UDP per broadcast
    broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    print(f"{Colori.BLU}Servizio di broadcast attivo (UDP porta {BROADCAST_PORT}){Colori.RESET}")
    print(f"{Colori.CELESTE}    Trasmetto: {server_ip}:{TCP_PORT}{Colori.RESET}\n")
    
    while True:
        try:
            # Messaggio di broadcast con formato: SERVER_DISCOVERY:IP:PORTA
            message = f"SERVER_DISCOVERY:{server_ip}:{TCP_PORT}"
            broadcast_sock.sendto(message.encode(), ('<broadcast>', BROADCAST_PORT))
            threading.Event().wait(2)  # Invia ogni 2 secondi
        except Exception as e:
            print(f"{Colori.ROSSO}[ERRORE]{Colori.RESET} Errore broadcast: {e}")
            break

def gestisci_client(client_socket, client_address):
    """Funzione che gestisce la comunicazione con UN SINGOLO client"""
    print(f"{Colori.VERDE}[THREAD] Nuovo client connesso: {client_address}{Colori.RESET}")

    global client_counter
    with lock_counter:
        client_counter += 1
    
    try:
        while True:
            data = client_socket.recv(1024).decode()
            parti = data.strip().split()

            comando = parti[0]
            parametro = parti[1] if len(parti) == 2 else None
            

            if not data:
                break
                
            print(f"{Colori.CELESTE}[{client_address}]{Colori.RESET} Messaggio ricevuto: {data}")
            log_message(mittente="CLIENT", ip=f'{client_address[0]}:{client_address[1]}', contenuto=data)
            generate_html_log()
            
            if comando.upper() == "EXIT":
                risposta = "-1"
                client_socket.send(risposta.encode())
                log_message(mittente="SERVER", ip=client_address[0], contenuto=risposta)
                generate_html_log()
                break
                
            elif comando.upper() == "TIME":
                time = datetime.datetime.now()
                risposta = f"{time.hour}:{time.minute}:{time.second}"
                client_socket.send(risposta.encode())
                log_message(mittente="SERVER", ip=client_address[0], contenuto=risposta)
                generate_html_log()

            elif comando.upper() == "NAME":
                risposta = f"Sono il server: {socket.gethostname()}"
                client_socket.send(risposta.encode())
                log_message(mittente="SERVER", ip=client_address[0], contenuto=risposta)
                generate_html_log()

            elif comando.upper() == "INFO":
                risposta = []

                if (parametro == "1" or parametro == None):
                    risposta.append(f"Client connessi: {client_counter}")
                
                if (parametro == "2" or parametro == None): # TODO: DA IMPLEMENTARE PRIMA LE CHAT
                    risposta.append("TODO: SIMULATO")
                
                if (parametro == "3" or parametro == None):
                    risposta.append(f"IP: {local_ip} | Porta: 12345")
                
                if (parametro == "4" or parametro == None):
                    risposta.append(f"IP/Porta del tuo client: {client_address[0]}:{client_address[1]}")
                
                if (parametro == "5" or parametro == None): # TODO: DA IMPLEMENTARE PRIMA LE CHAT
                    risposta.append("TODO: SIMULATO")

                risposta = "\n".join(risposta)
                client_socket.send(risposta.encode())
                log_message(mittente="SERVER", ip=client_address[0], contenuto=risposta)
                generate_html_log()
                
                
                
            else: 
                risposta = f"Ciao {client_address[0]}, ho ricevuto: '{data}'"
                client_socket.send(risposta.encode())
                log_message(mittente="SERVER", ip=client_address[0], contenuto=risposta)
                generate_html_log()
    
    except Exception as e:
        print(f"{Colori.ROSSO}[ERRORE]{Colori.RESET} Generato da {client_address}: {e}")
    
    finally:
        client_socket.close()
        print(f"{Colori.GIALLO}[THREAD]{Colori.GIALLO} Client {client_address} disconnesso")

# ========== AVVIO SERVER ==========

# Ottieni e mostra l'IP del server
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
except:
    local_ip = "127.0.0.1"
finally:
    s.close()


print(f'{Colori.CELESTE}' + "=" * 60)
print(f"{Colori.BLU}SERVER TCP CON AUTO-DISCOVERY{Colori.RESET}")
print(f'{Colori.CELESTE}' + "=" * 60)
print(f"{Colori.BLU}IP del server:{Colori.RESET} {local_ip}")
print(f"{Colori.BLU}Porta TCP:{Colori.RESET} 12345")
print(f"{Colori.BLU}Porta Broadcast:{Colori.RESET} 37020")
print(f'{Colori.CELESTE}' + "=" * 60)
print()

# Avvia thread per il broadcast
broadcast_thread = threading.Thread(target=broadcast_server_presence, args=(local_ip, 12345), daemon=True)
broadcast_thread.start()

# Creazione del socket TCP
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SERVER.bind((local_ip, 12345))
SERVER.listen(5)

client_counter = 0
lock_counter = threading.Lock()
print(f"{Colori.VERDE}Server TCP in ascolto sulla porta 12345...{Colori.RESET}")
print(f" {Colori.CELESTE}In attesa di client...{Colori.RESET}\n")

try:
    while True:
        client_socket, client_address = SERVER.accept()
        client_thread = threading.Thread(target=gestisci_client, args=(client_socket, client_address))
        client_thread.daemon = True
        client_thread.start()   
        print(f"{Colori.GIALLO}Thread avviato per {client_address}\n")

except KeyboardInterrupt:
    print(f"\n\n{Colori.GIALLO}Server interrotto dall'utente.{Colori.RESET}")
finally:
    SERVER.close()
    print(f"{Colori.VERDE}Server chiuso correttamente.{Colori.RESET}")