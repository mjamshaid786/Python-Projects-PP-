from pathlib import Path
from core import FileScanner, DuplicateFinder, Organizer, HistoryManager
from config import tracked_categories

def display_menu():
    print("\n" + "="*30)
    print("      FILE ORGANIZER PRO      ")
    print("="*30)
    print("1. Scan & Organize Folder")
    print("2. Find Duplicate Files")
    print("3. Undo Last Operation")
    print("4. Exit")
    print("="*30)

def main():
    # Target path initialize (Aap isay dynamic bhi bana sakte hain user input se)
    target_dir = r"" 
    
    # Core components ke objects initialize kar diye
    scanner = FileScanner(target_dir)
    finder = DuplicateFinder()
    organizer = Organizer(tracked_categories)
    history = HistoryManager()

    while True:
        display_menu()
        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            print("\n[+] Scanning directory, please wait...")
            files = scanner.scan_directory()
            print(f"[+] Total Files Found: {len(files)}")
            
            if not files:
                print("[-] No files found to organize.")
                continue
                
            print("[+] Organizing files...")
            for file_path in files:
                organizer.move_file(file_path, scanner.target_path, history)
            print("[*] All files organized successfully!")

        elif choice == "2":
            print("\n[+] Scanning for duplicates, please wait...")
            files = scanner.scan_directory()
            duplicates = finder.find_duplicates(files)
            print(f"[+] Total Duplicate Groups Found: {len(duplicates)}")
            
            if duplicates:
                print("\n[+] Moving duplicate copies to 'Duplicates' folder...")
                # Naye function ko call kiya
                total_moved = organizer.move_duplicates(duplicates, scanner.target_path, history)
                print(f"[*] Done! Total {total_moved} duplicate files moved to 'Duplicates/' folder.")
            else:
                print("[-] No duplicate files found.")

        elif choice == "3":
            print("\n[+] Attempting to undo last operation...")
            try:
                # Agar aapne history.py me success message handle nahi kiya, to yahan print kar sakte hain
                history.undo_last()
            except Exception as e:
                print(f"[-] Undo failed or no history found: {e}")

        elif choice == "4":
            print("\n[*] Thank you for using File Organizer Pro. Goodbye!")
            break

        else:
            print("[-] Invalid choice! Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main()