#===========================================
#     CLASSES AND FUNCTIONS ARE HERE 
#===========================================
from pathlib import Path
import hashlib
import json
import shutil


'''-----1. Scanning Target Directory-----'''
class FileScanner:
    def __init__(self, target_dir):
        self.target_path = Path(target_dir) #convert user given string path to path object
        if not self.target_path.exists() or not self.target_path.is_dir(): 
            raise ValueError("Path is Not Valid OR Not a Directory!")

    '''---Directory Scanner---'''
    def scan_directory(self):
        file_list = []
        print("Please Wait Scanner is Working...")
        for item in self.target_path.rglob('*'): #scan all the folder and their subfolders and files 
            if item.is_file():
                file_list.append(item)
        return file_list
        

'''-----2. Find Duplicate Files-----'''
class DuplicateFinder:
    def __init__(self):
        self.duplicates = {}
        print("Finding Duplicate Be Patient It Can Take a While !")

    '''---Separating Files Based On Size---'''
    def group_by_size(self, file_list):
        size_map = {}   
        for path in file_list:
            file_size = path.stat().st_size
            if file_size not in size_map:
                size_map[file_size] = [path]
            else:
                size_map[file_size].append(path)
        filtered_size_map = {}
        for size, paths in size_map.items():
            if len(paths) > 1:
                filtered_size_map[size] = paths
        return filtered_size_map

    '''---To Get The Hash Of File----'''
    def calculate_hash(self, file_path):
        hash_obj = hashlib.sha256()
        with open(file_path, 'rb')as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                hash_obj.update(chunk)
        return hash_obj.hexdigest()       

    '''---Find Duplicates---'''
    def find_duplicates(self, file_list):
        potential_duplicates = self.group_by_size(file_list)
        
        hash_map = {}
        for size, paths in potential_duplicates.items():
            for path in paths:
                file_hash = self.calculate_hash(path)              
                if file_hash not in hash_map:
                    hash_map[file_hash] = [path]
                else:
                    hash_map[file_hash].append(path)
                    
        for file_hash, paths in hash_map.items():
            if len(paths) > 1:
                self.duplicates[file_hash] = paths
                
        return self.duplicates

'''-----3. File Organinig System-----'''
class Organizer:
    def __init__(self, categories):
        self.categories = categories

    '''---File Moving Functions---'''
    def move_file(self, file_path, base_dir, history_manager):
        file_path = Path(file_path)
        base_dir = Path(base_dir)
        ext = file_path.suffix.lower()
        category_name = "Others"  # Default category
        for category, extensions in self.categories.items():
            if ext in extensions:
                category_name = category
                break
        target_folder = base_dir / category_name
        target_folder.mkdir(parents=True, exist_ok=True)
        dest_path = target_folder / file_path.name
        safe_path = self.resolve_collision(dest_path)
        shutil.move(str(file_path), str(safe_path))
        print(f"Moved: {file_path.name} -> {category_name}/")
        history_manager.log_action(file_path, safe_path)

    '''---Generating New Name For Duplicate Files---'''
    def resolve_collision(self, dest_path):
        if not dest_path.exists():
            return dest_path
        counter = 1
        name = dest_path.stem       # File ka naam (e.g., "resume")
        suffix = dest_path.suffix   # File ki extension (e.g., ".pdf")
        parent = dest_path.parent   # Folder ka rasta
        
        while True:
            new_name = f"{name}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1

    '''---Moving Duplicate files---'''
    def move_duplicates(self, duplicate_map, base_dir, history_manager):      
        dup_folder = Path(base_dir) / "Duplicates"
        dup_folder.mkdir(parents=True, exist_ok=True)      
        moved_count = 0
        for file_hash, paths in duplicate_map.items():
            if len(paths) > 1:
                for duplicate_path in paths[1:]:
                    old_path = Path(duplicate_path)
                    
                    if old_path.exists():
                        dest_path = dup_folder / old_path.name
                        safe_path = self.resolve_collision(dest_path)
                        shutil.move(str(old_path), str(safe_path))
                        history_manager.log_action(old_path, safe_path)
                        
                        print(f"Moved Duplicate: {old_path.name} -> Duplicates/")
                        moved_count += 1
                        
        return moved_count

'''-----4. Log Of Files Management-----'''
class HistoryManager:
    def __init__(self, history_file='history.json'):
        self.history_path = Path(history_file)        
        if not self.history_path.exists():
            with open(self.history_path, 'w') as f:
                json.dump([], f)

    '''---Record Of All Moving Files---'''
    def log_action(self, original_path, new_path):
        with open(self.history_path, 'r') as f:
            history_data = json.load(f)
            
        history_data.append({
            "old": str(original_path),
            "new": str(new_path)
        })
        
        with open(self.history_path, 'w') as f:
            json.dump(history_data, f, indent=4)

    '''---Undo Last Action---'''
    def undo_last(self):
        with open(self.history_path, 'r') as f:
            history_data = json.load(f)
        if history_data:
            last_action = history_data.pop()           
            old_path = Path(last_action["old"])
            new_path = Path(last_action["new"])           
            if new_path.exists():
                shutil.move(src=str(new_path), dst=str(old_path))
                print(f"Undo: Moved back {new_path.name} to {old_path.parent}")
            else:
                print(f"Error: File not found at {new_path} to undo.")
            with open(self.history_path, 'w') as f:
                json.dump(history_data, f, indent=4)
        else:
            print("Nothing to undo! History is empty.")


'''-----5. Report Of All Activity-----'''
class ReportGenerator:
    def __init__(self):
        pass

    '''---Summary Generator---'''
    def generate_summary(self):
        pass