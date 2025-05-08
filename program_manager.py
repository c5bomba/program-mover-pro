import os
import sys
import winreg
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Menu
from typing import Dict, List, Tuple, Optional, Any
from locale_strings import get_text, set_language, DEFAULT_LANG
import ctypes
import re
from pathlib import Path
try:
    import pylnk3 
    PYLNK_AVAILABLE = True
except ImportError:
    PYLNK_AVAILABLE = False
    print("[ProgramManager] Warning: pylnk3 library not found. Shortcut functionality will be limited.")
import threading
import queue

from locale_strings import get_text, set_language, DEFAULT_LANG

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class ProgramInfo:
    def __init__(self, name: str, version: str = "", install_location: str = "",
                 install_date: str = "", size: str = "Unknown", publisher: str = ""):
        self.name = name
        self.version = version
        self.install_location = install_location
        self.install_date = install_date
        self.size = size
        self.publisher = publisher
        self.files: List[str] = []
        self.registry_keys: List[str] = []
        self.shortcuts: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'version': self.version,
            'install_location': self.install_location,
            'install_date': self.install_date,
            'size': self.size,
            'publisher': self.publisher,
            'files': list(self.files),
            'registry_keys': list(self.registry_keys),
            'shortcuts': list(self.shortcuts)
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ProgramInfo':
        return ProgramInfo(
            name=data.get('name', ''),
            version=data.get('version', ''),
            install_location=data.get('install_location', ''),
            install_date=data.get('install_date', ''),
            size=data.get('size', 'Unknown'),
            publisher=data.get('publisher', '')
        )

class ProgramManager:
    def __init__(self):
        self.programs: Dict[str, ProgramInfo] = {}
        self.last_error = ""

    def get_installed_programs_threaded(self, progress_queue: queue.Queue) -> Dict[str, ProgramInfo]:
        progress_queue.put(("status", "Program bilgileri aliniyor..."))
        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        ]
        self.programs.clear()
        processed_count = 0

        for root_key, subkey_path in registry_paths:
            try:
                key = winreg.OpenKey(root_key, subkey_path)
                self._process_registry_key(key, root_key, subkey_path, progress_queue, processed_count)
            except WindowsError:
                continue

        progress_queue.put(("status", "Program boyutlari hesaplaniyor..."))
        self._get_program_sizes(progress_queue)

        progress_queue.put(("status", "Kisayollar bulunuyor..."))
        self._find_program_shortcuts(progress_queue)

        progress_queue.put(("finished_load", self.programs))
        return self.programs

    def _process_registry_key(self, key: Any, root_key: Any, subkey_path: str, progress_queue: queue.Queue, processed_count: int):
        index = 0
        while True:
            try:
                subkey_name = winreg.EnumKey(key, index)
                subkey_full_path = f"{subkey_path}\{subkey_name}"
                subkey = winreg.OpenKey(root_key, subkey_full_path)

                try:
                    name = ""
                    try: name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                    except (WindowsError, IndexError):
                        index += 1; winreg.CloseKey(subkey); continue

                    if not name or name.strip() == "":
                        index += 1; winreg.CloseKey(subkey); continue

                    is_system_component = False
                    try: is_system_component = winreg.QueryValueEx(subkey, "SystemComponent")[0] == 1
                    except (WindowsError, IndexError): pass
                    if is_system_component:
                        index += 1; winreg.CloseKey(subkey); continue

                    release_type = ""
                    try: release_type = winreg.QueryValueEx(subkey, "ReleaseType")[0].lower()
                    except (WindowsError, IndexError): pass
                    if release_type in ["security update", "update rollup", "hotfix"]:
                         index += 1; winreg.CloseKey(subkey); continue

                    program_info = ProgramInfo(name)
                    try: program_info.version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                    except (WindowsError, IndexError): pass
                    try: program_info.publisher = winreg.QueryValueEx(subkey, "Publisher")[0]
                    except (WindowsError, IndexError): pass

                    install_location = ""
                    try: install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                    except (WindowsError, IndexError):
                        try: install_location = winreg.QueryValueEx(subkey, "InstallPath")[0]
                        except (WindowsError, IndexError):
                            try:
                                display_icon_path = winreg.QueryValueEx(subkey, "DisplayIcon")[0]
                                cleaned_path = display_icon_path.split(',')[0].strip('"')
                                if cleaned_path.lower().endswith(".exe") and os.path.exists(cleaned_path):
                                    install_location = os.path.dirname(cleaned_path)
                            except (WindowsError, IndexError):
                                try:
                                     uninstall_string = winreg.QueryValueEx(subkey, "UninstallString")[0]
                                     match = re.search(r'"?(.*?\w+\.exe)"?', uninstall_string, re.IGNORECASE)
                                     if match:
                                         exe_path = match.group(1).strip('"')
                                         if os.path.exists(exe_path):
                                              install_location = os.path.dirname(exe_path)
                                except (WindowsError, IndexError, TypeError): pass

                    if install_location:
                         program_info.install_location = os.path.normpath(install_location.strip('"'))

                    try:
                        date_str = winreg.QueryValueEx(subkey, "InstallDate")[0]
                        if date_str and len(date_str) == 8:
                            program_info.install_date = f"{date_str[0:4]}-{date_str[4:6]}-{date_str[6:8]}"
                    except (WindowsError, IndexError): pass

                    root_name = "HKEY_LOCAL_MACHINE" if root_key == winreg.HKEY_LOCAL_MACHINE else "HKEY_CURRENT_USER"
                    program_info.registry_keys.append(f"{root_name}\{subkey_full_path}")

                    if name in self.programs:
                        if not self.programs[name].install_location and program_info.install_location:
                            self.programs[name] = program_info
                        self.programs[name].registry_keys = list(set(self.programs[name].registry_keys + program_info.registry_keys))
                    else:
                        self.programs[name] = program_info

                    processed_count += 1
                    if processed_count % 20 == 0: progress_queue.put(("progress_programs", processed_count))
                except Exception as e:
                    print(f"[_process_registry_key] Error reading values for key {subkey_full_path}: {e}")
                finally:
                     try: winreg.CloseKey(subkey)
                     except OSError: pass
                index += 1
            except WindowsError: break
            except Exception as e:
                print(f"[_process_registry_key] Unexpected error processing registry index {index} in {subkey_path}: {e}")
                index += 1
        progress_queue.put(("progress_programs", processed_count))

    def _get_program_sizes(self, progress_queue: queue.Queue):
        total_programs = len(self.programs)
        processed_count = 0
        for name, info in self.programs.items():
            if info.install_location and os.path.exists(info.install_location):
                try:
                    total_size_bytes = 0
                    file_list_for_program = []
                    for dirpath, _, filenames in os.walk(info.install_location):
                        for f in filenames:
                            fp = os.path.join(dirpath, f)
                            if os.path.exists(fp):
                                try:
                                    total_size_bytes += os.path.getsize(fp)
                                    file_list_for_program.append(fp)
                                except OSError: pass
                    info.size = self._format_size(total_size_bytes)
                    info.files = file_list_for_program
                except Exception: info.size = "Error calculating"
            processed_count += 1
            if processed_count % 5 == 0 or processed_count == total_programs:
                 progress_queue.put(("progress_sizes", processed_count, total_programs))

    def _format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0: return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

    def _find_program_shortcuts(self, progress_queue: queue.Queue):
        shortcut_locations = [
            os.path.join(os.environ.get("USERPROFILE", ""), "Desktop"),
            os.path.join(os.environ.get("ALLUSERSPROFILE", ""), "Desktop"),
            os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu"),
            os.path.join(os.environ.get("PROGRAMDATA", ""), "Microsoft", "Windows", "Start Menu"),
            os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs"),
            os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), ""),
            os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "")
        ]
        all_lnk_files = []
        for location in shortcut_locations:
            loc_path = Path(location)
            if loc_path.exists() and loc_path.is_dir():
                max_depth = 3 if "Program Files" in location else -1
                try:
                    for root, dirs, files in os.walk(location, topdown=True):
                        if max_depth != -1:
                            current_depth = root[len(str(loc_path)):].count(os.sep)
                            if current_depth >= max_depth:
                                dirs[:] = []
                        for file in files:
                            if file.lower().endswith(".lnk"):
                                full_path = os.path.join(root, file)
                                if full_path not in all_lnk_files:
                                    all_lnk_files.append(full_path)
                except OSError as e:
                     print(f"[_find_program_shortcuts] Error walking {location}: {e}")

        total_shortcuts_to_check = len(all_lnk_files)
        processed_shortcuts = 0
        for program_info in self.programs.values(): program_info.shortcuts.clear()

        if not PYLNK_AVAILABLE:
            progress_queue.put(("warning", get_text("pylnk3_not_available_error")))
            progress_queue.put(("progress_shortcuts", total_shortcuts_to_check, total_shortcuts_to_check))
            return

        for shortcut_path in all_lnk_files:
            target_path = None
            try:
                lnk = pylnk3.Lnk(shortcut_path)
                target_path = lnk.path

                if not target_path:
                    processed_shortcuts += 1; continue

                target_path_lower = target_path.lower()
                for program_name, info in self.programs.items():
                    if info.install_location and target_path_lower.startswith(info.install_location.lower()):
                        if shortcut_path not in info.shortcuts:
                            info.shortcuts.append(shortcut_path)
                        break
            except Exception as e:
                 pass
            finally:
                 processed_shortcuts +=1
                 if processed_shortcuts % 20 == 0 or processed_shortcuts == total_shortcuts_to_check:
                     progress_queue.put(("progress_shortcuts", processed_shortcuts, total_shortcuts_to_check))

    def _pre_scan_for_copy(self, src_path: str) -> int:
        file_count = 0
        try:
            for item in os.listdir(src_path):
                item_path = os.path.join(src_path, item)
                if os.path.isfile(item_path):
                    file_count += 1
                elif os.path.isdir(item_path):
                    file_count += self._pre_scan_for_copy(item_path)
        except OSError as e:
            print(f"[_pre_scan_for_copy] Error scanning {src_path}: {e}")
        return file_count

    def _copy_directory(self, src: str, dst: str, progress_queue: queue.Queue, overall_progress_tracker: List[int]):
        os.makedirs(dst, exist_ok=True)
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                self._copy_directory(s, d, progress_queue, overall_progress_tracker)
            else:
                try:
                    if not os.path.exists(d) or os.path.getsize(s) != os.path.getsize(d):
                        shutil.copy2(s, d)
                    overall_progress_tracker[0] += 1
                    progress_queue.put(("progress_copy", overall_progress_tracker[0], overall_progress_tracker[1], os.path.basename(s)))
                except (PermissionError, OSError, shutil.Error) as e:
                    print(f"[_copy_directory] Skipping file {s}: {e}")
                    overall_progress_tracker[0] += 1
                    progress_queue.put(("progress_copy", overall_progress_tracker[0], overall_progress_tracker[1], f"{os.path.basename(s)} (Hata: {e})"))

    def _update_shortcuts(self, program_info_shortcuts: List[str], old_location: str, new_location: str, progress_queue: queue.Queue) -> Tuple[int, List[str]]:
        updated_count = 0
        updated_shortcut_paths = []
        total_shortcuts_to_update = len(program_info_shortcuts)
        processed_count = 0

        if not PYLNK_AVAILABLE:
            progress_queue.put(("warning", get_text("pylnk3_not_available_error_update")))
            progress_queue.put(("progress_update_shortcuts", total_shortcuts_to_update, total_shortcuts_to_update))
            return 0, []

        for shortcut_path in program_info_shortcuts:
            try:
                lnk = pylnk3.Lnk(shortcut_path)
                old_target = lnk.path

                if old_target and old_target.lower().startswith(old_location.lower()):
                    new_target_corrected = new_location + old_target[len(old_location):]

                    if os.path.exists(new_target_corrected):
                        lnk.path = new_target_corrected
                        lnk.work_dir = os.path.dirname(new_target_corrected)
                        lnk.save()

                        updated_count += 1
                        updated_shortcut_paths.append(shortcut_path)
                    else:
                        print(f"[_update_shortcuts] Target {new_target_corrected} doesn't exist for {shortcut_path}")
            except PermissionError as pe:
                print(f"[_update_shortcuts] Permission error saving shortcut {shortcut_path}: {pe}")
                progress_queue.put(("warning", get_text("shortcut_update_permission_error", shortcut=shortcut_path)))
            except Exception as e:
                print(f"[_update_shortcuts] Error: {e} for {shortcut_path}")
                progress_queue.put(("warning", get_text("shortcut_update_generic_error", shortcut=shortcut_path, error=str(e))))
            processed_count +=1
            progress_queue.put(("progress_update_shortcuts", processed_count, total_shortcuts_to_update))
        return updated_count, updated_shortcut_paths

    def _delete_directory(self, path: str, progress_queue: queue.Queue) -> bool:
        all_items_to_delete = []
        for root, dirs, files in os.walk(path, topdown=False):
            for f_name in files: all_items_to_delete.append(os.path.join(root, f_name))
            for d_name in dirs: all_items_to_delete.append(os.path.join(root, d_name))
        if os.path.exists(path) and os.path.isdir(path): all_items_to_delete.append(path)

        deleted_count = 0
        total_to_delete = len(all_items_to_delete)
        if total_to_delete == 0: return True

        for item_path in all_items_to_delete:
            base_name = os.path.basename(item_path)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    os.rmdir(item_path)
                deleted_count += 1
                progress_queue.put(("progress_delete", deleted_count, total_to_delete, base_name))
            except PermissionError as pe:
                print(f"[_delete_directory] Permission Failed: {item_path}: {pe}")
                progress_queue.put(("delete_error", base_name, get_text("delete_permission_error")))
            except OSError as oe:
                print(f"[_delete_directory] OS Error: {item_path}: {oe}")
                error_detail = str(oe)
                if "not empty" in error_detail.lower(): error_detail = get_text("delete_not_empty_error")
                progress_queue.put(("delete_error", base_name, error_detail))
            except Exception as e:
                print(f"[_delete_directory] Generic Error: {item_path}: {e}")
                progress_queue.put(("delete_error", base_name, str(e)))

        if os.path.exists(path):
             self.last_error = get_text("delete_root_failed_error", path=path)
             return False
        return True

    def _update_registry_location(self, registry_keys: List[str], new_location: str, progress_queue: queue.Queue) -> bool:
        updated_at_least_one = False
        if not is_admin():
            progress_queue.put(("warning", get_text("registry_update_requires_admin")))
            return False

        for key_path_str in registry_keys:
            try:
                root_str, sub_path = key_path_str.split('\\', 1)
                root_hkey = None
                if root_str == "HKEY_LOCAL_MACHINE": root_hkey = winreg.HKEY_LOCAL_MACHINE
                elif root_str == "HKEY_CURRENT_USER": root_hkey = winreg.HKEY_CURRENT_USER
                else:
                    print(f"[_update_registry_location] Unknown root key in path: {key_path_str}"); continue

                key = winreg.OpenKey(root_hkey, sub_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, new_location)
                winreg.CloseKey(key)
            except FileNotFoundError:
                print(f"[_update_registry_location] Registry key not found (continuing): {key_path_str}")
            except PermissionError:
                print(f"[_update_registry_location] Permission denied for key: {key_path_str}")
                progress_queue.put(("warning", get_text("registry_permission_denied", key=key_path_str)))
            except Exception as e:
                print(f"[_update_registry_location] Error updating registry key {key_path_str}: {e}")
                progress_queue.put(("warning", get_text("registry_update_error", key=key_path_str, error=str(e))))

        if not updated_at_least_one:
             progress_queue.put(("warning", get_text("registry_update_failed_all")))
        return updated_at_least_one

    def move_program_threaded(self, program_info: ProgramInfo, target_path_input: str, delete_source: bool, progress_queue: queue.Queue):
        self.last_error = ""
        shortcuts_updated_count = 0
        updated_shortcut_paths_for_revert = []

        original_location = program_info.install_location
        if not original_location or not os.path.exists(original_location):
            self.last_error = "Program konumu bulunamadi veya geçerli değil"; progress_queue.put(("error", self.last_error)); return
        if not original_location.startswith(("C:", "c:")):
            self.last_error = "Program C sürücüsünde değil"; progress_queue.put(("error", self.last_error)); return
        if original_location.strip().upper() in ("C:", "C:\\"):
            self.last_error = "Geçersiz program konumu"; progress_queue.put(("error", self.last_error)); return

        new_location = ""
        if len(target_path_input) == 2 and target_path_input[1] == ':':
            relative_path = original_location[len(Path(original_location).drive) + 1:]
            new_location = os.path.join(target_path_input.upper(), relative_path.lstrip('\\/'))
        else:
            new_location = target_path_input

        if not new_location: self.last_error = "Hedef yol belirlenemedi."; progress_queue.put(("error", self.last_error)); return
        if new_location.lower() == original_location.lower(): self.last_error = "Kaynak ve hedef yollar ayni."; progress_queue.put(("error", self.last_error)); return

        try:
            progress_queue.put(("status", f"Kopyalama için ön tarama: {program_info.name}"))
            total_files_to_copy = self._pre_scan_for_copy(original_location)
            overall_copy_progress_tracker = [0, total_files_to_copy if total_files_to_copy > 0 else 1]

            progress_queue.put(("status", f"{program_info.name} kopyalaniyor: {original_location} -> {new_location}"))
            self._copy_directory(original_location, new_location, progress_queue, overall_copy_progress_tracker)

            if not os.path.exists(new_location) or not os.path.isdir(new_location):
                self.last_error = "Kopyalama sonrasi doğrulama başarisiz."; progress_queue.put(("error", self.last_error)); return

            progress_queue.put(("status", "Kisayollar güncelleniyor..."))
            shortcuts_updated_count, updated_shortcut_paths_for_revert = self._update_shortcuts(list(program_info.shortcuts), original_location, new_location, progress_queue)

            progress_queue.put(("status", get_text("status_updating_registry")))
            registry_updated = self._update_registry_location(program_info.registry_keys, new_location, progress_queue)

            source_deletion_warning = None
            if delete_source:
                progress_queue.put(("status", get_text("status_deleting_source")))
                if not self._delete_directory(original_location, progress_queue):
                    source_deletion_warning = self.last_error

            last_move_details = {
                'program_name': program_info.name,
                'original_location': original_location,
                'new_location': new_location,
                'registry_keys': list(program_info.registry_keys),
                'program_info_snapshot_dict': program_info.to_dict(),
                'source_deleted_during_move': delete_source,
                'source_actually_deleted': delete_source and not os.path.exists(original_location),
                'updated_shortcut_paths_during_move': updated_shortcut_paths_for_revert,
                'registry_updated_during_move': registry_updated
            }
            progress_queue.put(("finished_move", True, shortcuts_updated_count, registry_updated, source_deletion_warning, last_move_details))

        except Exception as e:
            error_msg = str(e)
            print(f"[move_program_threaded] Error: {error_msg}")
            self.last_error = f"Taşima sirasinda hata: {error_msg}"
            progress_queue.put(("error", self.last_error))

    def revert_move_threaded(self, last_move_info: Dict[str, Any], progress_queue: queue.Queue):
        self.last_error = ""
        program_name = last_move_info['program_name']
        original_loc = last_move_info['original_location']
        current_loc = last_move_info['new_location']
        shortcuts_to_revert = last_move_info['updated_shortcut_paths_during_move']
        source_actually_deleted_during_move = last_move_info['source_actually_deleted']
        registry_updated_during_move = last_move_info.get('registry_updated_during_move', False)
        registry_keys_to_revert = last_move_info.get('registry_keys', [])

        self.progress_queue.put(("status", get_text("status_reverting_move_prep", program_name=program_name)))

        try:
            progress_queue.put(("status", f"Dosyalar geri kopyalaniyor: {current_loc} -> {original_loc}"))
            total_files_to_copy_back = self._pre_scan_for_copy(current_loc)
            overall_copy_back_tracker = [0, total_files_to_copy_back if total_files_to_copy_back > 0 else 1]
            self._copy_directory(current_loc, original_loc, progress_queue, overall_copy_back_tracker)

            if not os.path.exists(original_loc) or not os.path.isdir(original_loc):
                self.last_error = "Geri kopyalama sonrasi doğrulama başarisiz."
                progress_queue.put(("error", self.last_error)); return

            progress_queue.put(("status", get_text("status_reverting_shortcuts")))
            reverted_shortcuts_count, _ = self._update_shortcuts(list(shortcuts_to_revert), current_loc, original_loc, progress_queue)

            registry_reverted = False
            if registry_updated_during_move:
                progress_queue.put(("status", get_text("status_reverting_registry")))
                registry_reverted = self._update_registry_location(registry_keys_to_revert, original_loc, progress_queue)
            else:
                registry_reverted = True

            delete_current_loc_warning = None
            if source_actually_deleted_during_move:
                progress_queue.put(("status", get_text("status_deleting_reverted_source", location=current_loc)))
                if not self._delete_directory(current_loc, progress_queue):
                    delete_current_loc_warning = self.last_error

            progress_queue.put(("finished_revert", True, reverted_shortcuts_count, registry_reverted, delete_current_loc_warning))

        except Exception as e:
            error_msg = str(e)
            print(f"[revert_move_threaded] Error: {error_msg}")
            self.last_error = f"Geri alma sirasinda hata: {error_msg}"
            progress_queue.put(("error", self.last_error))

    def get_last_error(self) -> str:
        return self.last_error

class ProgramManagerUI:
    def __init__(self, root):
        self.root = root
        set_language(DEFAULT_LANG)
        self.current_language = DEFAULT_LANG

        self.root.title(get_text("app_title"))
        self.root.geometry("1150x750")

        self.program_manager = ProgramManager()
        self.progress_queue = queue.Queue()
        self.active_thread = None
        self.programs_data: Dict[str, ProgramInfo] = {}
        self.last_move_info: Optional[Dict[str, Any]] = None

        self.create_menu()
        self.setup_ui()
        self.check_queue_periodically()

    def create_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        language_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Language", menu=language_menu)

        self.language_var = tk.StringVar(value=self.current_language)
        language_menu.add_radiobutton(label="English", variable=self.language_var, value="en", command=self.change_language)
        language_menu.add_radiobutton(label="Türkçe", variable=self.language_var, value="tr", command=self.change_language)

        self.menubar = menubar

    def change_language(self):
        new_lang = self.language_var.get()
        if new_lang != self.current_language:
            set_language(new_lang)
            self.current_language = new_lang
            self.update_ui_language()

    def update_ui_language(self):
        self.root.title(get_text("app_title"))
        self.menubar.entryconfig(1, label=get_text("menu_language"))

        self.refresh_btn.config(text=get_text("refresh_programs"))
        self.move_btn.config(text=get_text("move_selected"))
        self.delete_source_check.config(text=get_text("delete_source_files"))
        self.revert_btn.config(text=get_text("revert_last_move"))
        self.details_btn.config(text=get_text("program_details"))
        self.browse_custom_path_btn.config(text=get_text("browse"))
        self.exit_btn.config(text=get_text("exit"))

        self.search_label.config(text=get_text("search"))
        self.target_path_frame.config(text=get_text("target_path_config"))
        self.custom_path_check.config(text=get_text("use_custom_path"))
        self.target_drive_label.config(text=get_text("target_drive"))
        self.custom_path_label.config(text=get_text("custom_path"))

        for col_key in self.columns:
            self.tree.heading(col_key, text=get_text(f"col_{col_key}"))
            self.tree.heading(col_key, command=lambda _col=col_key: self.sort_treeview_column(_col, False))

        if not (self.active_thread and self.active_thread.is_alive()):
             self.status_var.set(get_text("status_ready"))

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=5)

        self.refresh_btn = ttk.Button(controls_frame, text=get_text("refresh_programs"), command=self.load_programs_threaded)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        self.search_label = ttk.Label(controls_frame, text=get_text("search"))
        self.search_label.pack(side=tk.LEFT, padx=(10,0))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(controls_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<KeyRelease>", self.filter_programs)

        self.target_path_frame = ttk.LabelFrame(controls_frame, text=get_text("target_path_config"))
        self.target_path_frame.pack(side=tk.RIGHT, padx=5, fill=tk.X)
        self.use_custom_path_var = tk.BooleanVar(value=False)
        self.custom_path_check = ttk.Checkbutton(self.target_path_frame, text=get_text("use_custom_path"), variable=self.use_custom_path_var, command=self.toggle_custom_path_entry)
        self.custom_path_check.grid(row=0, column=0, columnspan=3, padx=5, pady=2, sticky=tk.W)

        self.target_drive_label = ttk.Label(self.target_path_frame, text=get_text("target_drive"))
        self.target_drive_label.grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        available_drives = self.get_available_drives()
        self.target_drive_var = tk.StringVar(value=available_drives[0] if available_drives else "")
        self.target_drive_combo = ttk.Combobox(self.target_path_frame, textvariable=self.target_drive_var, values=available_drives, width=5, state="readonly")
        self.target_drive_combo.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)

        self.custom_path_label = ttk.Label(self.target_path_frame, text=get_text("custom_path"))
        self.custom_path_label.grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        self.custom_target_path_var = tk.StringVar()
        self.custom_target_path_entry = ttk.Entry(self.target_path_frame, textvariable=self.custom_target_path_var, width=35, state=tk.DISABLED)
        self.custom_target_path_entry.grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)
        self.browse_custom_path_btn = ttk.Button(self.target_path_frame, text=get_text("browse"), command=self.browse_custom_target_path, state=tk.DISABLED)
        self.browse_custom_path_btn.grid(row=2, column=2, padx=5, pady=2, sticky=tk.W)

        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.columns = ("name", "publisher", "version", "size", "install_date", "location")
        self.tree = ttk.Treeview(tree_frame, columns=self.columns, show="headings", selectmode="browse")
        for col_key in self.columns:
            self.tree.heading(col_key, text=get_text(f"col_{col_key}"), command=lambda _col=col_key: self.sort_treeview_column(_col, False))
        col_widths = {"name": 280, "publisher": 180, "version": 80, "size": 90, "install_date": 100, "location": 380}
        for col, width in col_widths.items(): self.tree.column(col, width=width, anchor=tk.W if col != 'size' else tk.E)
        self.tree.column("install_date", anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)

        self.move_btn = ttk.Button(buttons_frame, text=get_text("move_selected"), command=self.move_selected_program_threaded)
        self.move_btn.pack(side=tk.LEFT, padx=5)
        self.delete_source_var = tk.BooleanVar(value=False)
        self.delete_source_check = ttk.Checkbutton(buttons_frame, text=get_text("delete_source_files"), variable=self.delete_source_var)
        self.delete_source_check.pack(side=tk.LEFT, padx=5)
        self.revert_btn = ttk.Button(buttons_frame, text=get_text("revert_last_move"), command=self.revert_last_move_threaded, state=tk.DISABLED)
        self.revert_btn.pack(side=tk.LEFT, padx=5)
        self.details_btn = ttk.Button(buttons_frame, text=get_text("program_details"), command=self.show_program_details)
        self.details_btn.pack(side=tk.LEFT, padx=5)

        self.exit_btn = ttk.Button(buttons_frame, text=get_text("exit"), command=self.root.quit)
        self.exit_btn.pack(side=tk.RIGHT, padx=5)

        status_progress_frame = ttk.Frame(self.root)
        status_progress_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=2)
        self.status_var = tk.StringVar(value=get_text("status_ready"))
        status_bar = ttk.Label(status_progress_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.progress_bar = ttk.Progressbar(status_progress_frame, orient=tk.HORIZONTAL, length=250, mode='determinate')
        self.progress_bar.pack(side=tk.RIGHT, padx=5)

        self.load_programs_threaded()

    def sort_treeview_column(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        def get_size_key(item_tuple):
            size_val_str = item_tuple[0]
            parts = size_val_str.split(' ')
            try:
                num = float(parts[0])
                unit = parts[1] if len(parts) > 1 else 'B'
                multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4, 'PB': 1024**5}
                return num * multipliers.get(unit.upper(), 0)
            except (ValueError, IndexError): return -1

        if col == 'size': l.sort(key=get_size_key, reverse=reverse)
        else:
            try: l.sort(key=lambda item: float(item[0]) if item[0] and item[0] != '-' else -float('inf'), reverse=reverse)
            except ValueError: l.sort(key=lambda item: (item[0] or '').lower(), reverse=reverse)
        for index, (val, k) in enumerate(l): self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda _col=col: self.sort_treeview_column(_col, not reverse))

    def toggle_custom_path_entry(self):
        use_custom = self.use_custom_path_var.get()
        self.custom_target_path_entry.config(state=tk.NORMAL if use_custom else tk.DISABLED)
        self.browse_custom_path_btn.config(state=tk.NORMAL if use_custom else tk.DISABLED)
        self.target_drive_combo.config(state=tk.DISABLED if use_custom else "readonly")

    def browse_custom_target_path(self):
        path = filedialog.askdirectory(title=get_text("select_custom_path_dialog_title"), initialdir=self.custom_target_path_var.get() or os.getcwd())
        if path: self.custom_target_path_var.set(os.path.normpath(path))

    def get_available_drives(self) -> List[str]:
        return [f"{chr(d)}:" for d in range(ord('A'), ord('Z')+1) if os.path.exists(f"{chr(d)}:") and f"{chr(d)}:".upper() != "C:"]

    def update_ui_for_long_task(self, is_running: bool, task_name_key: str = "", format_args: dict = None):
        state = tk.DISABLED if is_running else tk.NORMAL
        self.refresh_btn.config(state=state)
        self.move_btn.config(state=state)
        self.revert_btn.config(state=state if self.last_move_info else tk.DISABLED)
        self.tree.config(selectmode="none" if is_running else "browse")

        if is_running:
            task_text = get_text(task_name_key, **(format_args or {})) if task_name_key else "..."
            self.status_var.set(f"{task_text}...")
            self.progress_bar.config(mode='indeterminate')
            self.progress_bar.start(10)
        else:
            self.status_var.set(get_text("status_ready"))
            self.progress_bar.stop()
            self.progress_bar['value'] = 0
            self.progress_bar.config(mode='determinate')

    def load_programs_threaded(self):
        if self.active_thread and self.active_thread.is_alive():
            messagebox.showwarning(get_text("warning"), get_text("ongoing_operation_warning")); return
        self.update_ui_for_long_task(True, "status_loading_programs")
        for item in self.tree.get_children(): self.tree.delete(item)
        self.programs_data.clear()

        self.active_thread = threading.Thread(target=self.program_manager.get_installed_programs_threaded, args=(self.progress_queue,))
        self.active_thread.daemon = True; self.active_thread.start()

    def filter_programs(self, event=None):
        search_text = self.search_var.get().lower()
        for item in self.tree.get_children(): self.tree.delete(item)
        for name, info in self.programs_data.items():
            if (search_text in info.name.lower() or
                search_text in (info.publisher.lower() if info.publisher else "") or
                search_text in (info.version.lower() if info.version else "")):
                self.tree.insert("", tk.END, values=(info.name, info.publisher, info.version, info.size, info.install_date, info.install_location), iid=name)

    def move_selected_program_threaded(self):
        if self.active_thread and self.active_thread.is_alive(): messagebox.showwarning(get_text("warning"), get_text("ongoing_operation_warning")); return
        selected_item_id = self.tree.selection()
        if not selected_item_id: messagebox.showinfo(get_text("info"), get_text("select_program_prompt")); return

        program_name = selected_item_id[0]
        program_info = self.programs_data.get(program_name)

        if not program_info or not program_info.install_location or not os.path.exists(program_info.install_location):
            messagebox.showerror(get_text("error"), get_text("program_location_not_found", location=program_info.install_location if program_info else 'N/A')); return

        target_path_input = ""
        if self.use_custom_path_var.get():
            target_path_input = os.path.normpath(self.custom_target_path_var.get().strip())
            if not target_path_input : messagebox.showerror(get_text("error"), get_text("empty_custom_path")); return
            if os.path.abspath(target_path_input).startswith(os.path.abspath(program_info.install_location)):
                 messagebox.showerror(get_text("error"), get_text("target_path_in_source_error")); return
            try:
                parent_dir = os.path.dirname(target_path_input)
                if os.path.isdir(target_path_input):
                    target_path_input = os.path.join(target_path_input, os.path.basename(program_info.install_location))
                elif not os.path.exists(parent_dir):
                     messagebox.showerror(get_text("error"), get_text("invalid_custom_path_parent", parent_dir=parent_dir)); return
            except Exception as e:
                messagebox.showerror(get_text("error"), f"{get_text('custom_path_validation_error')}: {e}"); return
        else:
            target_drive = self.target_drive_var.get()
            if not target_drive: messagebox.showinfo(get_text("info"), get_text("select_target_drive_prompt")); return
            original_loc_path = Path(program_info.install_location)
            if original_loc_path.drive.upper() == "C:":
                 relative_to_c_root = str(original_loc_path.relative_to(original_loc_path.anchor))
                 target_path_input = os.path.join(target_drive + "\\", relative_to_c_root)
            else:
                 target_path_input = os.path.join(target_drive + "\\", original_loc_path.name)

        if os.path.abspath(target_path_input).lower() == os.path.abspath(program_info.install_location).lower():
            messagebox.showerror(get_text("error"), get_text("source_target_same_error")); return

        delete_source = self.delete_source_var.get()
        confirmation_key = "confirm_move_with_delete_warning" if delete_source else "confirm_move_prompt"
        confirmation_message = get_text(confirmation_key,
                                        program_name=program_name,
                                        source=program_info.install_location,
                                        target=os.path.abspath(target_path_input))
        if not messagebox.askyesno(get_text("confirmation"), confirmation_message, icon=messagebox.WARNING if delete_source else messagebox.QUESTION):
            return

        if not is_admin():
            messagebox.showwarning(get_text("warning"), get_text("admin_rights_crucial_warning"))

        self.update_ui_for_long_task(True, "status_moving_program", format_args={'program_name': program_name})
        self.active_thread = threading.Thread(target=self.program_manager.move_program_threaded,
                                          args=(program_info, os.path.abspath(target_path_input), delete_source, self.progress_queue))
        self.active_thread.daemon = True; self.active_thread.start()

    def revert_last_move_threaded(self):
        if not self.last_move_info:
            messagebox.showinfo(get_text("info"), get_text("no_revert_operation")); return
        if self.active_thread and self.active_thread.is_alive():
            messagebox.showwarning(get_text("warning"), get_text("ongoing_operation_warning")); return

        program_name = self.last_move_info['program_name']
        original_loc = self.last_move_info['original_location']
        current_loc = self.last_move_info['new_location']
        shortcuts_to_revert = self.last_move_info['updated_shortcut_paths_during_move']
        source_actually_deleted_during_move = self.last_move_info['source_actually_deleted']
        registry_updated_during_move = self.last_move_info.get('registry_updated_during_move', False)
        registry_keys_to_revert = self.last_move_info.get('registry_keys', [])

        self.progress_queue.put(("status", get_text("status_reverting_move_prep", program_name=program_name)))

        self.update_ui_for_long_task(True, "status_reverting_move", format_args={'program_name': program_name})
        self.active_thread = threading.Thread(target=self.program_manager.revert_move_threaded,
                                          args=(self.last_move_info, self.progress_queue))
        self.active_thread.daemon = True; self.active_thread.start()

    def check_queue_periodically(self):
        try:
            while True:
                message = self.progress_queue.get_nowait()
                msg_type, *payload = message

                if msg_type == "status":
                    raw_status_text = payload[0]
                    status_args = payload[1] if len(payload) > 1 else {}
                    self.status_var.set(get_text(raw_status_text, **status_args))
                    if not self.progress_bar['mode'] == 'determinate' or self.progress_bar['value'] == 0 :
                        self.progress_bar.config(mode='indeterminate'); self.progress_bar.start(10)
                elif msg_type == "progress_programs":
                    self.status_var.set(get_text("status_programs_scanned", count=payload[0]))
                elif msg_type in ["progress_sizes", "progress_shortcuts", "progress_update_shortcuts"]:
                    current, total = payload
                    key_map = {"progress_sizes": "status_sizes_calculated", "progress_shortcuts": "status_shortcuts_scanned", "progress_update_shortcuts": "status_shortcuts_updated"}
                    self.status_var.set(get_text(key_map.get(msg_type, "unknown_progress"), current=current, total=total))
                    self.progress_bar.config(mode='determinate'); self.progress_bar['value'] = (current / total) * 100 if total > 0 else 0
                elif msg_type in ["progress_copy", "progress_delete"]:
                    current, total, filename = payload
                    status_key = "status_copying_file" if msg_type == "progress_copy" else "status_deleting_file"
                    error_info = ""
                    if "(Hata: " in filename:
                         parts = filename.split("(Hata: ", 1)
                         filename = parts[0].strip()
                         error_info = f" (Hata: {parts[1][:-1]})"
                         status_key = "status_copy_error_file" if msg_type == "progress_copy" else "status_delete_error_file"
                    self.status_var.set(get_text(status_key, current=current, total=total, filename=filename, error=error_info))
                    self.progress_bar.config(mode='determinate'); self.progress_bar['value'] = (current / total) * 100 if total > 0 else 0
                elif msg_type == "delete_error":
                     print(f"[UI] {get_text('status_delete_error_file', filename=payload[0], error=payload[1])}")
                elif msg_type == "finished_load":
                    self.programs_data = payload[0]
                    self.update_ui_for_long_task(False)
                    self.filter_programs()
                    self.status_var.set(get_text("status_programs_found", count=len(self.programs_data)))
                elif msg_type == "finished_move":
                    success, shortcuts_updated, registry_updated, delete_warning, last_move_details = payload
                    self.update_ui_for_long_task(False)
                    program_name_moved = last_move_details['program_name']
                    if success:
                        self.last_move_info = last_move_details
                        self.revert_btn.config(state=tk.NORMAL)
                        try:
                            if self.tree.exists(program_name_moved):
                                new_loc = last_move_details['new_location']
                                self.tree.set(program_name_moved, column="location", value=new_loc)
                                if program_name_moved in self.programs_data:
                                    self.programs_data[program_name_moved].install_location = new_loc
                        except Exception as e: print(f"Error updating treeview after move: {e}")

                        msg = get_text("move_successful_msg", program_name=program_name_moved)
                        if shortcuts_updated > 0: msg += get_text("shortcuts_updated_msg", count=shortcuts_updated)
                        if registry_updated: msg += get_text("registry_update_success_info")
                        else: msg += get_text("registry_update_failed_info")
                        if self.delete_source_var.get() and not delete_warning: msg += get_text("source_deleted_msg")
                        elif delete_warning: msg += get_text("source_delete_warning_msg", warning=delete_warning)
                        messagebox.showinfo(get_text("info"), msg)
                    else: messagebox.showerror(get_text("error"), get_text("move_failed_msg", program_name=program_name_moved, error=self.program_manager.get_last_error()))
                    self.status_var.set(get_text("status_ready"))
                elif msg_type == "finished_revert":
                    success, reverted_shortcuts_count, registry_reverted, delete_current_loc_warning = payload
                    self.update_ui_for_long_task(False)
                    program_name_reverted = self.last_move_info['program_name'] if self.last_move_info else "?"
                    original_location_reverted_to = self.last_move_info['original_location'] if self.last_move_info else "?"
                    if success:
                        try:
                            if self.tree.exists(program_name_reverted):
                                self.tree.set(program_name_reverted, column="location", value=original_location_reverted_to)
                                if program_name_reverted in self.programs_data:
                                    self.programs_data[program_name_reverted].install_location = original_location_reverted_to
                        except Exception as e: print(f"Error updating treeview after revert: {e}")

                        self.last_move_info = None
                        self.revert_btn.config(state=tk.DISABLED)
                        msg = get_text("revert_successful_msg", program_name=program_name_reverted)
                        if reverted_shortcuts_count > 0: msg += get_text("reverted_shortcuts_msg", count=reverted_shortcuts_count)
                        if registry_reverted: msg += get_text("registry_revert_success_info")
                        else: msg += get_text("registry_revert_failed_info")
                        if delete_current_loc_warning: msg += get_text("revert_delete_warning_msg", warning=delete_current_loc_warning)
                        messagebox.showinfo(get_text("info"), msg)
                    else: messagebox.showerror(get_text("error"), get_text("revert_failed_msg", program_name=program_name_reverted, error=self.program_manager.get_last_error()))
                    self.status_var.set(get_text("status_ready"))
                elif msg_type == "error" or msg_type == "warning":
                    self.update_ui_for_long_task(False)
                    title = get_text(msg_type)
                    message_text = payload[0]
                    (messagebox.showerror if msg_type == "error" else messagebox.showwarning)(title, message_text)
                    self.status_var.set(get_text("status_error_occurred"))
        except queue.Empty: pass
        finally: self.root.after(100, self.check_queue_periodically)

    def show_program_details(self):
        selected_item_id = self.tree.selection()
        if not selected_item_id: messagebox.showinfo(get_text("info"), get_text("select_program_prompt")); return
        program_name = selected_item_id[0]
        program_info = self.programs_data.get(program_name)
        if not program_info: messagebox.showerror(get_text("error"), get_text("program_info_not_found", program_name=program_name)); return

        details_window = tk.Toplevel(self.root)
        details_window.title(get_text("details_title", program_name=program_name))
        details_window.geometry("700x600")
        details_window.transient(self.root); details_window.grab_set()

        details_frame = ttk.Frame(details_window, padding="10")
        details_frame.pack(fill=tk.BOTH, expand=True)

        info_frame = ttk.LabelFrame(details_frame, text=get_text("program_info_header"))
        info_frame.pack(fill=tk.X, pady=5)
        fields = [
            (get_text("col_name"), program_info.name), (get_text("col_publisher"), program_info.publisher),
            (get_text("col_version"), program_info.version), (get_text("col_size"), program_info.size),
            (get_text("col_install_date"), program_info.install_date), (get_text("col_location"), program_info.install_location)
        ]
        for i, (label, value) in enumerate(fields):
            ttk.Label(info_frame, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            val_text = value if value else "-"
            val_label = ttk.Label(info_frame, text=val_text, wraplength=500, justify=tk.LEFT)
            val_label.grid(row=i, column=1, sticky=tk.W, padx=5, pady=2)

        if program_info.shortcuts:
            sc_frame = ttk.LabelFrame(details_frame, text=get_text("shortcuts_header", count=len(program_info.shortcuts)))
            sc_frame.pack(fill=tk.X, pady=5)
            sc_text_area = tk.Text(sc_frame, wrap=tk.WORD, height=4, width=80)
            sc_scroll = ttk.Scrollbar(sc_frame, orient=tk.VERTICAL, command=sc_text_area.yview)
            sc_text_area.config(yscrollcommand=sc_scroll.set)
            sc_text_area.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
            sc_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            for sc in program_info.shortcuts: sc_text_area.insert(tk.END, f"{sc}\n")
            sc_text_area.config(state=tk.DISABLED)

        if program_info.files:
            f_frame = ttk.LabelFrame(details_frame, text=get_text("files_header", count=len(program_info.files)))
            f_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            f_text_area = tk.Text(f_frame, wrap=tk.NONE, height=10, width=80)
            f_x_scroll = ttk.Scrollbar(f_frame, orient=tk.HORIZONTAL, command=f_text_area.xview)
            f_y_scroll = ttk.Scrollbar(f_frame, orient=tk.VERTICAL, command=f_text_area.yview)
            f_text_area.config(yscrollcommand=f_y_scroll.set, xscrollcommand=f_x_scroll.set)

            f_text_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
            f_x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
            f_y_scroll.pack(side=tk.RIGHT, fill=tk.Y)

            for f_path in program_info.files[:100]: f_text_area.insert(tk.END, f"{f_path}\n")
            if len(program_info.files) > 100:
                f_text_area.insert(tk.END, f"\n... and {len(program_info.files) - 100} more files.")
            f_text_area.config(state=tk.DISABLED)
        else:
            ttk.Label(details_frame, text=get_text("no_file_details")).pack(pady=5)

        ttk.Button(details_frame, text=get_text("close"), command=details_window.destroy).pack(pady=10, side=tk.RIGHT)

def main():
    if not is_admin():
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        except Exception as e:
            try: messagebox.showerror(get_text("error"), get_text("admin_error_restart", error=e))
            except tk.TclError: print(f"Error: {get_text('admin_error_restart', error=e)}")
        sys.exit(0)

    root = tk.Tk()
    style = ttk.Style()
    try:
        if sys.platform == "win32": style.theme_use('clam')
    except tk.TclError:
        print(get_text("theme_not_found_warning"))

    app = ProgramManagerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
