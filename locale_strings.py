DEFAULT_LANG = "en"

TEXTS = {
    "en": {
        # Window Titles
        "app_title": "Program Mover Pro",
        "details_title": "{program_name} - Details",
        "select_custom_path_dialog_title": "Select Custom Target Path",
        # Menu
        "menu_language": "Language",
        # Buttons
        "refresh_programs": "Refresh Programs",
        "move_selected": "Move Selected Program",
        "delete_source_files": "Delete Source Files",
        "revert_last_move": "Revert Last Move",
        "program_details": "Program Details",
        "exit": "Exit",
        "browse": "Browse...",
        "close": "Close",
        # Labels & Headers
        "search": "Search:",
        "target_path_config": "Target Path Configuration",
        "use_custom_path": "Use Custom Path",
        "target_drive": "Drive:",
        "custom_path": "Custom Path:",
        "status_ready": "Ready",
        "status_loading_programs": "Loading programs...",
        "status_calculating_sizes": "Calculating sizes...",
        "status_finding_shortcuts": "Finding shortcuts...",
        "status_programs_found": "{count} programs found.",
        "status_moving_program": "Moving {program_name}...",
        "status_reverting_move": "Reverting {program_name}...",
        "status_copying_files": "Copying files...",
        "status_updating_shortcuts": "Updating shortcuts...",
        "status_updating_registry": "Updating registry...",
        "status_deleting_source": "Deleting source files...",
        "status_error_occurred": "Error occurred.",
        "status_move_done": "{program_name} moved.",
        "status_revert_done": "Revert for {program_name} done.",
        "program_info_header": "Program Information",
        "shortcuts_header": "Found Shortcuts ({count})",
        "files_header": "Found Files ({count} - showing first 100)",
        "no_file_details": "No file details found for this program.",
        # Treeview Columns
        "col_name": "Name",
        "col_publisher": "Publisher",
        "col_version": "Version",
        "col_size": "Size",
        "col_install_date": "Install Date",
        "col_location": "Location",
        # Messages & Dialogs
        "info": "Information",
        "warning": "Warning",
        "error": "Error",
        "confirmation": "Confirmation",
        "select_program_prompt": "Please select a program.",
        "select_target_drive_prompt": "Please select a target drive.",
        "select_custom_path_prompt": "Invalid custom target path. Please select or create an existing directory.",
        "invalid_custom_path_parent": "Parent directory of custom target path ({parent_dir}) not found.",
        "empty_custom_path": "Custom target path cannot be empty.",
        "target_path_in_source_error": "Target path cannot be inside or same as source path.",
        "source_target_same_error": "Source and target paths cannot be the same.",
        "program_info_not_found": "Program information not found: {program_name}",
        "program_location_not_found": "Program installation location not found: {location}",
        "confirm_delete_source_prompt": "You chose to delete source files ({location}). This action cannot be undone. Continue?",
        "confirm_move_prompt": "Move {program_name} from:\n{source}\n -> to:\n{target}?",
        "confirm_move_with_delete_warning": "Move {program_name} from:\n{source}\n -> to:\n{target}?\n\nWARNING: Source files ({source}) WILL BE DELETED! This action is irreversible.",
        "admin_rights_needed": "Administrator rights may be required for this operation.",
        "admin_rights_crucial_warning": "Administrator rights are crucial for modifying system locations (Registry, Program Files). Operation might fail without them.",
        "ongoing_operation_warning": "There is an ongoing operation. Please wait for it to complete.",
        "move_successful_msg": "{program_name} moved successfully.",
        "shortcuts_updated_msg": "\n{count} shortcuts updated.",
        "source_deleted_msg": "\nSource files deleted.",
        "source_delete_warning_msg": "\nSource file deletion warning: {warning}",
        "registry_update_success_info": "\nRegistry location updated.",
        "registry_update_failed_info": "\nRegistry location could not be updated.",
        "move_failed_msg": "Failed to move {program_name}: {error}",
        "no_revert_operation": "No move operation to revert.",
        "confirm_revert_prompt": "Revert last move for {program_name}?\n{current_loc} -> {original_loc}",
        "confirm_revert_with_delete_warning": "Revert last move for {program_name}?\n{current_loc} -> {original_loc}\n\nWARNING: Files at {current_loc} will be deleted (as source was deleted in original move).",
        "revert_successful_msg": "Revert for {program_name} successful.",
        "reverted_shortcuts_msg": "\n{count} shortcuts reverted.",
        "revert_delete_warning_msg": "WARNING: Some files could not be deleted when restoring the source deleted after the move: {warning}",
        "registry_revert_success_info": "\nRegistry location reverted.",
        "registry_revert_failed_info": "\nRegistry location could not be reverted.",
        "revert_failed_msg": "Failed to revert {program_name}: {error}",
        "admin_error_restart": "This application requires administrator rights. Could not restart: {error}",
        "theme_not_found_warning": "Selected theme not found, using default.",
        "size_error_calculating": "Error calculating",
        "status_copy_scan": "Scanning files to copy: {program_name}",
        "status_copying_file": "Copying ({current}/{total}): {filename}",
        "status_copy_error_file": "{filename} (Error: {error})",
        "status_deleting_file": "Deleting ({current}/{total}): {filename}",
        "status_delete_error_file": "Failed to delete: {filename} - {error}",
        "status_shortcuts_updated": "Shortcuts updated: {current}/{total}",
        "status_programs_scanned": "Programs scanned: {count} found...",
        "status_sizes_calculated": "Sizes calculated: {current}/{total}",
        "status_shortcuts_scanned": "Shortcuts scanned: {current}/{total}",
        "custom_path_validation_error": "Error validating custom path",
        "status_reverting_move_prep": "Preparing to revert move for {program_name}...",
        "status_reverting_shortcuts": "Reverting shortcuts...",
        "status_reverting_registry": "Reverting registry entries...",
        "status_deleting_reverted_source": "Deleting reverted program from its previous location ({location})...",
        "registry_update_requires_admin": "Registry update requires administrator rights.",
        "registry_permission_denied": "Registry update permission denied for: {key}",
        "registry_update_error": "Error updating registry key {key}: {error}",
        "registry_update_failed_all": "Failed to update any registry keys for the program location.",
        "shortcut_scan_init_error": "Could not initialize shortcut scanning (WScript.Shell). Shortcut features disabled.",
        "shortcut_update_permission_error": "Permission denied updating shortcut: {shortcut}",
        "shortcut_update_generic_error": "Error updating shortcut {shortcut}: {error}",
        "delete_permission_error": "Permission Denied",
        "delete_not_empty_error": "Directory not empty",
        "delete_root_failed_error": "Could not delete the main directory ({path}). Files might be locked or permission issues persist.",
        # pylnk3 related errors
        "pylnk3_not_available_error": "pylnk3 library not found. Shortcut scanning functionality will be unavailable. Please install it using 'pip install pylnk3'.",
        "pylnk3_not_available_error_update": "pylnk3 library not found. Shortcut updating functionality will be unavailable. Please install it using 'pip install pylnk3'."
    },
    "tr": {
        # Window Titles
        "app_title": "Program Taşıyıcı Pro",
        "details_title": "{program_name} - Detaylar",
        "select_custom_path_dialog_title": "Özel Hedef Yol Seçin",
        # Menu
        "menu_language": "Dil",
        # Buttons
        "refresh_programs": "Programları Yenile",
        "move_selected": "Seçili Programı Taşı",
        "delete_source_files": "Kaynak Dosyaları Sil",
        "revert_last_move": "Son Taşımayı Geri Al",
        "program_details": "Program Detayları",
        "exit": "Çıkış",
        "browse": "Gözat...",
        "close": "Kapat",
        # Labels & Headers
        "search": "Ara:",
        "target_path_config": "Hedef Yol Yapılandırması",
        "use_custom_path": "Özel Hedef Yol",
        "target_drive": "Sürücü:",
        "custom_path": "Özel Yol:",
        "status_ready": "Hazır",
        "status_loading_programs": "Programlar yükleniyor...",
        "status_calculating_sizes": "Boyutlar hesaplanıyor...",
        "status_finding_shortcuts": "Kısayollar bulunuyor...",
        "status_programs_found": "{count} program bulundu.",
        "status_moving_program": "{program_name} taşınıyor...",
        "status_reverting_move": "{program_name} geri alınıyor...",
        "status_copying_files": "Dosyalar kopyalanıyor...",
        "status_updating_shortcuts": "Kısayollar güncelleniyor...",
        "status_updating_registry": "Kayıt Defteri güncelleniyor...",
        "status_deleting_source": "Kaynak dosyalar siliniyor...",
        "status_error_occurred": "Hata oluştu.",
        "status_move_done": "{program_name} taşındı.",
        "status_revert_done": "{program_name} için geri alma tamamlandı.",
        "program_info_header": "Program Bilgisi",
        "shortcuts_header": "Bulunan Kısayollar ({count})",
        "files_header": "Bulunan Dosyalar ({count} - ilk 100 gösteriliyor)",
        "no_file_details": "Bu program için dosya detayı bulunamadı.",
        # Treeview Columns
        "col_name": "Ad",
        "col_publisher": "Yayıncı",
        "col_version": "Sürüm",
        "col_size": "Boyut",
        "col_install_date": "Kurulum Tarihi",
        "col_location": "Konum",
        # Messages & Dialogs
        "info": "Bilgi",
        "warning": "Uyarı",
        "error": "Hata",
        "confirmation": "Onay",
        "select_program_prompt": "Lütfen bir program seçin.",
        "select_target_drive_prompt": "Lütfen bir hedef sürücü seçin.",
        "select_custom_path_prompt": "Geçersiz özel hedef yol. Lütfen var olan bir dizin seçin veya oluşturun.",
        "invalid_custom_path_parent": "Özel hedef yolun üst dizini ({parent_dir}) bulunamadı.",
        "empty_custom_path": "Özel hedef yol boş olamaz.",
        "target_path_in_source_error": "Hedef yol, kaynak yolun içinde veya aynı olamaz.",
        "source_target_same_error": "Kaynak ve hedef yollar aynı olamaz.",
        "program_info_not_found": "Program bilgisi bulunamadı: {program_name}",
        "program_location_not_found": "Program kurulum konumu bulunamadı: {location}",
        "confirm_delete_source_prompt": "Kaynak dosyaları silmeyi seçtiniz ({location}). Bu işlem geri alınamaz. Devam etmek istiyor musunuz?",
        "confirm_move_prompt": "{program_name} programını şuradan taşı:\n{source}\n -> şuraya:\n{target}?",
        "confirm_move_with_delete_warning": "{program_name} programını şuradan taşı:\n{source}\n -> şuraya:\n{target}?\n\nUYARI: Kaynak dosyalar ({source}) SİLİNECEKTİR! Bu işlem geri alınamaz.",
        "admin_rights_needed": "Bu işlem için yönetici hakları gerekebilir.",
        "admin_rights_crucial_warning": "Sistem konumlarını (Kayıt Defteri, Program Files) değiştirmek için yönetici hakları kritik öneme sahiptir. Haklar olmadan işlem başarısız olabilir.",
        "ongoing_operation_warning": "Devam eden bir işlem var. Lütfen tamamlanmasını bekleyin.",
        "move_successful_msg": "{program_name} başarıyla taşındı.",
        "shortcuts_updated_msg": "\n{count} kısayol güncellendi.",
        "source_deleted_msg": "\nKaynak dosyalar silindi.",
        "source_delete_warning_msg": "\nKaynak dosya silme uyarısı: {warning}",
        "registry_update_success_info": "\nKayıt Defteri konumu güncellendi.",
        "registry_update_failed_info": "\nKayıt Defteri konumu güncellenemedi.",
        "move_failed_msg": "{program_name} taşınamadı: {error}",
        "no_revert_operation": "Geri alınacak bir taşıma işlemi bulunmuyor.",
        "confirm_revert_prompt": "{program_name} için son taşıma işlemi geri alınacak mı?\n{current_loc} -> {original_loc}",
        "confirm_revert_with_delete_warning": "{program_name} için son taşıma işlemi geri alınacak mı?\n{current_loc} -> {original_loc}\n\nUYARI: {current_loc} konumundaki dosyalar silinecektir (çünkü orijinal taşıma sırasında kaynaklar silinmişti).",
        "revert_successful_msg": "{program_name} için geri alma başarılı.",
        "reverted_shortcuts_msg": "\n{count} kısayol geri güncellendi.",
        "revert_delete_warning_msg": "UYARI: Taşıma sonrası silinen kaynak geri yüklenirken bazı dosyalar silinemedi: {warning}",
        "registry_revert_success_info": "\nKayıt Defteri konumu geri alındı.",
        "registry_revert_failed_info": "\nKayıt Defteri konumu geri alınamadı.",
        "revert_failed_msg": "{program_name} geri alınamadı: {error}",
        "admin_error_restart": "Bu uygulama yönetici hakları gerektirir. Yeniden başlatılamadı: {error}",
        "theme_not_found_warning": "Seçilen tema bulunamadı, varsayılan tema kullanılıyor.",
        "size_error_calculating": "Boyut hesaplama hatası",
        "status_copy_scan": "Kopyalanacak dosyalar taranıyor: {program_name}",
        "status_copying_file": "Kopyalanıyor ({current}/{total}): {filename}",
        "status_copy_error_file": "{filename} (Hata: {error})",
        "status_deleting_file": "Siliniyor ({current}/{total}): {filename}",
        "status_delete_error_file": "Silinemedi: {filename} - {error}",
        "status_shortcuts_updated": "Kısayollar güncellendi: {current}/{total}",
        "status_programs_scanned": "Programlar tarandı: {count} bulundu...",
        "status_sizes_calculated": "Boyutlar hesaplandı: {current}/{total}",
        "status_shortcuts_scanned": "Kısayollar tarandı: {current}/{total}",
        "custom_path_validation_error": "Özel hedef yolu doğrulama hatası",
        "status_reverting_move_prep": "{program_name} için geri alma işlemi hazırlanıyor...",
        "status_reverting_shortcuts": "Kısayollar geri alınıyor...",
        "status_reverting_registry": "Kayıt defteri girdileri geri alınıyor...",
        "status_deleting_reverted_source": "Geri alınan programın eski konumu ({location}) siliniyor...",
        "registry_update_requires_admin": "Kayıt Defteri güncellemesi yönetici hakları gerektirir.",
        "registry_permission_denied": "Kayıt Defteri güncelleme izni reddedildi: {key}",
        "registry_update_error": "Kayıt Defteri anahtarı güncellenirken hata: {key}: {error}",
        "registry_update_failed_all": "Program konumu için herhangi bir Kayıt Defteri anahtarı güncellenemedi.",
        "shortcut_scan_init_error": "Kısayol taraması başlatılamadı (WScript.Shell). Kısayol özellikleri devre dışı.",
        "shortcut_update_permission_error": "Kısayol güncellenirken izin reddedildi: {shortcut}",
        "shortcut_update_generic_error": "Kısayol güncellenirken hata: {shortcut}: {error}",
        "delete_permission_error": "İzin Reddedildi",
        "delete_not_empty_error": "Dizin boş değil",
        "delete_root_failed_error": "Ana dizin ({path}) silinemedi. Dosyalar kilitli olabilir veya izin sorunları devam ediyor olabilir.",

        "pylnk3_not_available_error": "pylnk3 kütüphanesi bulunamadı. Kısayol tarama işlevi kullanılamayacak. Lütfen 'pip install pylnk3' ile kurun.",
        "pylnk3_not_available_error_update": "pylnk3 kütüphanesi bulunamadı. Kısayol güncelleme işlevi kullanılamayacak. Lütfen 'pip install pylnk3' ile kurun."
    }
}

# Global variable to hold the current language
current_lang = DEFAULT_LANG

def set_language(lang_code: str):
    """Sets the current language."""
    global current_lang
    if lang_code in TEXTS:
        current_lang = lang_code
    else:
        print(f"Warning: Language code '{lang_code}' not found. Using default '{DEFAULT_LANG}'.")
        current_lang = DEFAULT_LANG

def get_text(key: str, **kwargs) -> str:
    """Gets the text for the given key in the current language, with formatting."""
    try:
        text = TEXTS[current_lang].get(key, f"MISSING_STRING[{key}]")
        if kwargs:
            return text.format(**kwargs)
        return text
    except KeyError:
        # Fallback to default language if current language is missing
        print(f"Warning: Language '{current_lang}' not found in TEXTS for key '{key}'. Falling back to default.")
        text = TEXTS[DEFAULT_LANG].get(key, f"MISSING_STRING[{key}]")
        if kwargs:
            return text.format(**kwargs)
        return text
    except Exception as e:
        print(f"Error getting text for key '{key}': {e}")
        return f"ERROR_STRING[{key}]" 
