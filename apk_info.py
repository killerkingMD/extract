import os
import sys
import subprocess
import zipfile
import re
import threading
import time
import itertools

# Cores ANSI para texto (removidas no final)
class Colors:
    GREEN = "\033[32m"  # Verde ANSI
    RESET = "\033[0m"   # Reset de cor

def extract_apk(apk_path, extract_to):
    """Extrai o conteúdo do APK para o diretório especificado."""
    with zipfile.ZipFile(apk_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def get_apk_info(apk_path):
    """Obtém informações detalhadas sobre o APK usando aapt e o sistema de arquivos."""
    if not os.path.isfile(apk_path):
        print(f"Erro: Arquivo APK '{apk_path}' não encontrado.")
        return None

    # Obtém o tamanho do APK em bytes
    apk_size = os.path.getsize(apk_path)

    # Obtém informações detalhadas do APK usando aapt
    try:
        result = subprocess.run(
            ["aapt", "dump", "badging", apk_path],
            capture_output=True,
            text=True,
            check=True
        )
        aapt_info = result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar aapt: {e}")
        return None

    # Extrai versão e tamanho do APK a partir do resultado do aapt
    version_code = "Desconhecida"
    version_name = "Desconhecida"

    version_code_match = re.search(r"versionCode='(\d+)'", aapt_info)
    version_name_match = re.search(r"versionName='([\w.]+)'", aapt_info)

    if version_code_match:
        version_code = version_code_match.group(1)
    if version_name_match:
        version_name = version_name_match.group(1)

    return {
        "apk_size": apk_size,
        "version_code": version_code,
        "version_name": version_name,
        "aapt_info": aapt_info
    }

def extract_dex_files(apk_path, extract_to):
    """Extrai arquivos .dex do APK para o diretório especificado."""
    extracted_dir = os.path.join(extract_to, "extracted")
    dex_dir = os.path.join(extracted_dir, "dex")
    if not os.path.exists(dex_dir):
        os.makedirs(dex_dir)
    
    extract_apk(apk_path, extracted_dir)
    
    for root, _, files in os.walk(extracted_dir):
        for file in files:
            if file.endswith('.dex'):
                os.rename(os.path.join(root, file), os.path.join(dex_dir, file))

    return dex_dir

def search_links_in_dex_files(dex_dir, output_file):
    """Procura por links em arquivos .dex e salva os resultados em um arquivo de saída."""
    with open(output_file, 'w') as f:
        f.write("░▒▓█►─═ Links encontrados nos arquivos .dex ═─◄█▓▒░\n")
        for filename in os.listdir(dex_dir):
            if filename.endswith('.dex'):
                dex_file = os.path.join(dex_dir, filename)
                try:
                    # Use strings para extrair caracteres imprimíveis e grep para procurar links
                    result = subprocess.run(
                        ["strings", dex_file],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    links = [line for line in result.stdout.splitlines() if "http://" in line or "https://" in line]
                    
                    if links:
                        f.write(f"░▒▓█►─═ Links encontrados em {dex_file} ═─◄█▓▒░\n")
                        for link in links:
                            f.write(f"{link}\n")  # Links sem formatação de cor
                        f.write("░▒▓█►───────────────────────────◄█▓▒░\n")
                    else:
                        f.write(f"░▒▓█►─═ Nenhum link encontrado em {dex_file} ═─◄█▓▒░\n")
                except subprocess.CalledProcessError:
                    f.write(f"░▒▓█►─═ Erro ao processar o arquivo {dex_file} ═─◄█▓▒░\n")
        f.write("░▒▓█►───────────────────────────◄█▓▒░\n")

def show_menu():
    print("***************************************")
    print("1. Informações do desenvolvedor")
    print("2. Link para o canal do Telegram")
    print("3. Continuar com a extração dos links do APK")
    print("4. Sair")
    print("***************************************")

def developer_info():
    print("\033[38;2;255;105;180m***************************************\033[0m")
    print("\033[38;2;255;105;180mDesenvolvedor: [killerkingMD👑]\033[0m")
    print("\033[38;2;255;105;180m***************************************\033[0m")

def telegram_link():
    print("\033[38;2;30;144;255m***************************************\033[0m")
    print("\033[38;2;30;144;255mLink para o canal do Telegram: https://t.me/kingApplicationspremium\033[0m")
    print("\033[38;2;30;144;255m***************************************\033[0m")

def loading_animation(stop_event):
    animation_chars = itertools.cycle('|/-\\')
    while not stop_event.is_set():
        char = next(animation_chars)
        sys.stdout.write(f'\r{char} Aguarde a extração terminar...')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rConcluído!                           \n')

def main():
    while True:
        show_menu()
        choice = input("Escolha uma opção: ")
        
        if choice == '1':
            developer_info()
        elif choice == '2':
            telegram_link()
        elif choice == '3':
            if len(sys.argv) != 2:
                print("Uso: python apk_info.py /caminho/para/apk")
                sys.exit(1)

            apk_path = sys.argv[1]
            apk_info = get_apk_info(apk_path)
            
            if apk_info is None:
                continue

            extracted_dir = os.path.dirname(apk_path)
            dex_dir = extract_dex_files(apk_path, extracted_dir)
            
            output_file = os.path.join(extracted_dir, "apk_info.txt")
            with open(output_file, 'w') as f:
                f.write("░▒▓█►─═ Informações do APK ═─◄█▓▒░\n")
                f.write(f"Tamanho do APK: {apk_info['apk_size']} bytes\n")
                f.write(f"Versão do APK (versionCode): {apk_info['version_code']}\n")
                f.write(f"Versão do APK (versionName): {apk_info['version_name']}\n")
                f.write("░▒▓█►───────────────────────────◄█▓▒░\n")
                f.write("\nInformações do APK:\n")
                f.write(apk_info['aapt_info'])
                f.write("░▒▓█►───────────────────────────◄█▓▒░\n")

            links_file = os.path.join(extracted_dir, "links_info.txt")
            
            stop_event = threading.Event()
            loading_thread = threading.Thread(target=loading_animation, args=(stop_event,))
            
            loading_thread.start()
            
            search_links_in_dex_files(dex_dir, links_file)
            
            stop_event.set()
            loading_thread.join()

            print("Extração concluída!")
            print(f"Informações do APK foram salvas em '{output_file}'.")
            print(f"Links encontrados foram salvos em '{links_file}'.")
        elif choice == '4':
            print("Saindo...")
            sys.exit(0)
        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")

if __name__ == "__main__":
    main()
