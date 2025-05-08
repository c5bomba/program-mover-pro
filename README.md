# Program Mover Pro

Program Mover Pro is an advanced Python application for Windows that allows you to list installed programs and move selected ones from your C: drive to another drive or a custom folder. It intelligently updates associated shortcuts and optionally attempts to modify the installation path in the registry.

## Key Features

-   **Language Support:** User interface available in English (default) and Turkish.
-   Comprehensive listing of installed programs from the Windows Registry.
-   Detailed program information:
    -   Name, Publisher, Version
    -   Size (calculated on disk)
    -   Installation Date, Install Location
    -   Associated Registry Keys
    -   Detected Shortcuts
    -   List of program files (first 100)
-   Live filtering of programs by name, publisher, or version.
-   Move programs from C: drive to another drive or a full custom path.
-   Detailed progress and status updates during operations.
-   **Shortcut Updates:** Automatically updates targets of desktop and Start Menu shortcuts after moving, using the `pylnk3` library for reliability.
-   **Registry Updates (Experimental):** Attempts to update the `InstallLocation` entry in the registry for the moved program. (Requires admin rights; may not always succeed).
-   **Optional Source Deletion:** Delete original program files from the C: drive after a successful move.
-   **Revert Last Move:** Undo the last move operation (including file copy, shortcut, and registry changes).
-   Robust file copying and deletion with error handling.
-   Background threading for long operations (listing, moving, reverting) to prevent UI freezes.
-   Sortable program list by clicking column headers.
-   Automatic UAC elevation prompt if not run as administrator.

## Installation

1.  Ensure you have Python 3.7+ installed.
2.  Download or clone this repository.
3.  Install the required libraries. Open your terminal or command prompt and run:
    ```bash
    pip install pywin32 pylnk3
    ```
4.  Navigate to the application folder and run `program_manager.py`:
    ```bash
    python program_manager.py
    ```

## Requirements

-   `tkinter` (Python standard library) - For the GUI.
-   `winreg` (Python standard library) - For registry access.
-   `os`, `sys`, `shutil`, `datetime`, `ctypes`, `re`, `subprocess`, `pathlib`, `glob`, `queue` (Python standard libraries) - For various system operations.
-   `pywin32` - For Windows API access (kept for initial admin rights check and other potential Windows interactions).
-   `pylnk3` - For reading and writing Windows shortcut (.lnk) files. This is a more reliable alternative to the `WScript.Shell` COM object, which can be problematic on some systems.

## How to Use

1.  Run the program. It will request administrator privileges (UAC prompt) if not already elevated. Please approve.
2.  The main window will display a list of your installed programs. Information like size and shortcuts is loaded in the background.
3.  **Program List:**
    *   **Search:** Instantly filter programs using the search box at the top.
    *   **Sort:** Click column headers to sort the list.
    *   **Details:** Select a program and click "Program Details" to view more info (files, shortcuts, registry keys).
4.  **Moving a Program:**
    *   Select the program to move from the list.
    *   **Target Path Configuration:**
        *   **Target Drive:** Choose a drive (e.g., `D:`) from the dropdown. The program will be moved maintaining its relative path from C:.
        *   **Use Custom Path:** Check this to manually enter or browse for a full target folder path (e.g., `D:\Moved Programs\MyGame`). If the final part of your custom path doesn't match the program's original folder name, the program files will be copied *into* this path under their original folder name.
    *   **Delete Source Files:** Check this box if you want to delete the original files from the C: drive after a successful move.
    *   Click "Move Selected Program." A confirmation dialog will appear.
5.  **Revert Last Move:** If you change your mind after a move, the "Revert Last Move" button will be active. Click it to undo the last operation.
6.  **Change Language:** Switch the UI language between English and Turkish via the "Language" menu.
7.  **Status & Progress Bar:** The bottom of the window shows the current application status and progress for long operations.

## Important Notes & Potential Issues

-   **Administrator Rights:** The application **must** be run as an administrator for full functionality (especially registry writing and moving files in system locations).
-   **Registry Updates:** Modifying the registry is risky. While the app attempts to update `InstallLocation`, it might not always succeed or could affect how some programs run. This feature is experimental.
-   **Shortcut Updates (`pylnk3`):** Shortcut handling uses the `pylnk3` library, which is generally more stable than `WScript.Shell`. Ensure `pylnk3` is installed.
-   **File Locks:** If the program you're trying to move (or a related process) is running, file locks might cause the move/delete operation to fail. Close the relevant program before moving.
-   **Permissions:** Rarely, even with admin rights, you might encounter permission issues with specific system files/folders.
-   **Program Sizes:** Sizes are calculated by summing up all files in the installation directory, which might differ from the size shown in the Control Panel.
-   **Antivirus Software:** Some antivirus programs might flag registry access or file moving operations as suspicious. You may need to add an exception.
-   **Post-Move Testing:** Always test a program after moving it to ensure it runs correctly.

## Contributing

Feel free to open an issue on GitHub for bug reports or feature requests. For code contributions, please submit a pull request.

## License

This project is open source, licensed under the MIT License. (Details will be in the `LICENSE` file, to be added). 
