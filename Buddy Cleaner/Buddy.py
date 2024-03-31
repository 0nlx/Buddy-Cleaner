import os
import sys
import time
import shutil
import clamd
import logging
from colorama import Fore, Style

# Set up logging
logging.basicConfig(filename='buddy.log', level=logging.INFO)

def initialize_clamav():
    try:
        cd = clamd.ClamdUnixSocket()
        cd.ping()  # Test ClamAV connection
        return cd
    except Exception as e:
        print(f"{Fore.RED}Error: Failed to initialize ClamAV: {e}{Style.RESET_ALL}")
        logging.error(f"Error initializing ClamAV: {e}")
        sys.exit(1)

def scan_directory(dir_to_scan, clamav_client):
    infected_files = []
    clean_files = []
    for root, dirs, files in os.walk(dir_to_scan):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                result = clamav_client.scan(file_path)
                if result['stream'] == 'OK':
                    clean_files.append(file_path)
                elif result['stream'] == 'FOUND':
                    infected_files.append(file_path)
            except Exception as e:
                print(f"{Fore.RED}Error scanning {file_path}: {e}{Style.RESET_ALL}")
                logging.error(f"Error scanning {file_path}: {e}")
    return infected_files, clean_files

def quarantine_infected_files(infected_files, quarantine_dir):
    for file_path in infected_files:
        try:
            shutil.move(file_path, os.path.join(quarantine_dir, os.path.basename(file_path)))
            print(f"{Fore.RED}Infected file moved to quarantine: {file_path}{Style.RESET_ALL}")
            logging.info(f"File quarantined: {file_path}")
        except Exception as e:
            print(f"{Fore.RED}Error quarantining {file_path}: {e}{Style.RESET_ALL}")
            logging.error(f"Error quarantining {file_path}: {e}")

def extract_file(file_path):
    print(f"{Fore.YELLOW}Extracting file: {file_path}{Style.RESET_ALL}")
    # Perform file extraction logic here

def monitor_directory(dir_to_monitor, clamav_client, duration):
    start_time = time.time()
    end_time = start_time + duration
    while time.time() < end_time:
        print(f"{Fore.YELLOW}Scanning directory for viruses...{Style.RESET_ALL}")
        infected_files, _ = scan_directory(dir_to_monitor, clamav_client)
        if infected_files:
            print(f"{Fore.RED}Infected file(s) found:{Style.RESET_ALL}")
            for file_path in infected_files:
                print(file_path)
                # Optionally, extract the file before quarantining
                # extract_file(file_path)
            quarantine_infected_files(infected_files, quarantine_dir)
        else:
            print(f"{Fore.GREEN}No infected files found.{Style.RESET_ALL}")
        time.sleep(60)  # Check directory every 60 seconds

def development_mode():
    print(f"{Fore.YELLOW}Entering development mode...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Features coming soon:\n")
    print(f"- Custom plugin integration")
    print(f"- Advanced configuration options")
    print(f"- Interactive debugging tools")
    print(f"- Enhanced monitoring capabilities\n")
    print(f"{Style.RESET_ALL}")

def main():
    args = sys.argv[1:]
    if not args:
        print(f"{Fore.RED}Usage: buddy <command> [options]{Style.RESET_ALL}")
        sys.exit(1)

    command = args[0]
    if command == 'scan':
        if len(args) != 2:
            print(f"{Fore.RED}Usage: buddy scan <directory>{Style.RESET_ALL}")
            sys.exit(1)
        dir_to_scan = args[1]
        clamav_client = initialize_clamav()
        print(f"{Fore.YELLOW}Scanning directory for viruses...{Style.RESET_ALL}")
        infected_files, clean_files = scan_directory(dir_to_scan, clamav_client)
        if infected_files:
            print(f"{Fore.RED}{len(infected_files)} infected file(s) found:{Style.RESET_ALL}")
            for file_path in infected_files:
                print(file_path)
        else:
            print(f"{Fore.GREEN}No infected files found.{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{len(clean_files)} clean file(s) scanned.{Style.RESET_ALL}")

    elif command == 'quarantine':
        if len(args) != 3:
            print(f"{Fore.RED}Usage: buddy quarantine <directory> <quarantine_directory>{Style.RESET_ALL}")
            sys.exit(1)
        dir_to_scan = args[1]
        quarantine_dir = args[2]
        clamav_client = initialize_clamav()
        if not os.path.exists(quarantine_dir):
            os.makedirs(quarantine_dir)
        print(f"{Fore.YELLOW}Scanning directory for viruses...{Style.RESET_ALL}")
        infected_files, clean_files = scan_directory(dir_to_scan, clamav_client)
        if infected_files:
            print(f"{Fore.RED}Quarantining infected files...{Style.RESET_ALL}")
            quarantine_infected_files(infected_files, quarantine_dir)
            print(f"{Fore.GREEN}{len(clean_files)} clean file(s) scanned.{Style.RESET_ALL}")
            logging.info(f"{len(infected_files)} file(s) quarantined.")
        else:
            print(f"{Fore.GREEN}No infected files found.{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{len(clean_files)} clean file(s) scanned.{Style.RESET_ALL}")

    elif command == 'extract':
        if len(args) != 2:
            print(f"{Fore.RED}Usage: buddy extract <file>{Style.RESET_ALL}")
            sys.exit(1)
        file_path = args[1]
        extract_file(file_path)

    elif command == 'monitor':
        if len(args) != 4:
            print(f"{Fore.RED}Usage: buddy monitor <directory> <duration_in_seconds> <quarantine_directory>{Style.RESET_ALL}")
            sys.exit(1)
        dir_to_monitor = args[1]
        duration = int(args[2])
        quarantine_dir = args[3]
        clamav_client = initialize_clamav()
        if not os.path.exists(quarantine_dir):
            os.makedirs(quarantine_dir)
        monitor_directory(dir_to_monitor, clamav_client, duration)

    elif command == 'dev':
        development_mode()

    elif command == 'help':
        print(f"{Fore.YELLOW}Usage:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}buddy scan <directory> - Scan a directory for viruses{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}buddy quarantine <directory> <quarantine_directory> - Quarantine infected files{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}buddy extract <file> - Extract and open a file{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}buddy monitor <directory> <duration_in_seconds> <quarantine_directory> - Monitor a directory for viruses{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}buddy dev - Enter development mode for bot customization{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}buddy help - Show this help message{Style.RESET_ALL}")

    else:
        print(f"{Fore.RED}Unknown command. Use 'buddy help' for usage information.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
