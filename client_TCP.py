import socket
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

def discover_server(timeout=10):
    """Cerca il server sulla rete locale tramite broadcast UDP"""
    BROADCAST_PORT = 37020
    
    print(f"{Colori.CELESTE}Ricerca del server sulla rete locale...{Colori.RESET}")
    print(f"{Colori.CELESTE}    Ascolto broadcast sulla porta {BROADCAST_PORT}{Colori.RESET}")
    print(f"{Colori.GIALLO}    Timeout: {timeout} secondi{Colori.RESET}\n")
    
    # Crea socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", BROADCAST_PORT))
    sock.settimeout(timeout)
    
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            message = data.decode()
            
            # Verifica che il messaggio sia dal server
            if message.startswith("SERVER_DISCOVERY:"):
                parts = message.split(":")
                if len(parts) == 3:
                    server_ip = parts[1]
                    server_port = int(parts[2])
                    
                    print(f"{Colori.VERDE}Server trovato!{Colori.RESET}")
                    print(f"{Colori.BLU}    IP:{Colori.RESET} {server_ip}")
                    print(f"{Colori.BLU}    Porta:{Colori.RESET} {server_port}\n")
                    
                    sock.close()
                    return server_ip, server_port
    
    except socket.timeout:
        print(f"{Colori.GIALLO}Timeout: Nessun server trovato sulla rete.")
        sock.close()
        return None, None
    except Exception as e:
        print(f"{Colori.ROSSO}[ERRORE]{Colori.RESET} Errore durante la ricerca: {e}")
        sock.close()
        return None, None

# ========== AVVIO CLIENT ==========

print(f'{Colori.CELESTE}' + "=" * 60)
print(f"{Colori.BLU}CLIENT TCP CON AUTO-DISCOVERY{Colori.RESET}")
print(f'{Colori.CELESTE}' + "=" * 60)
print()

# Chiedi all'utente se vuole cercare automaticamente o inserire manualmente
SERVER_IP, SERVER_PORT = discover_server(timeout=10)
    
if SERVER_IP is None:
    print(f"{Colori.GIALLO}Discovery fallita: inserisci manualmente IP e porta del server")
    SERVER_IP = input(f"{Colori.ROSA}IP server: {Colori.RESET}").strip()
    port_input = input(f"{Colori.ROSA}Porta server (default 12345): {Colori.RESET}").strip()
    SERVER_PORT = int(port_input) if port_input else 12345

print(f"\n{Colori.BLU}Connessione a {SERVER_IP}:{SERVER_PORT}...{Colori.RESET}")

# Creazione del socket client
CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    CLIENT.connect((SERVER_IP, SERVER_PORT))
    print(f"{Colori.VERDE}Connesso al server!{Colori.RESET}\n")

    while True:
        mess = input(f"{Colori.BLU}[CLIENT]{Colori.RESET} --> Inserisci un messaggio da inviare: ")
        CLIENT.send(mess.encode())
        
        data = CLIENT.recv(1024).decode()

        if data == "-1":
            print(f"{Colori.GIALLO}[SERVER]{Colori.RESET} --> Disconnessione richiesta dal server")
            CLIENT.close()
            break

        print(f"{Colori.VERDE}[SERVER]{Colori.RESET} --> {data}")

except ConnectionRefusedError:
    print(f"{Colori.ROSSO}[ERRORE]{Colori.RESET} Impossibile connettersi a {SERVER_IP}:{SERVER_PORT}")
    print(f"{Colori.BLU}Verifica che:")
    print(f"{Colori.CELESTE}    1. Il server sia in esecuzione")
    print(f"{Colori.CELESTE}    2. Il firewall permetta la connessione")
except Exception as e:
    print(f"{Colori.ROSSO}[ERRORE] {e}{Colori.RESET}")
finally:
    CLIENT.close()
    print(f"\n{Colori.GIALLO}Client chiuso.{Colori.RESET}")