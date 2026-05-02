# src/tools/program_manager.py
import os
import platform
import subprocess
import psutil
import shutil
from typing import List, Optional

SYSTEM = platform.system()


def _normalize(name: str) -> str:
    return name.strip().lower()


def _search_in_paths(name: str, search_paths: List[str], max_hits: int = 5) -> List[str]:
    """Search for executables containing `name` under given paths (non-exhaustive)."""
    matches = []
    name_lower = name.lower()
    for base in search_paths:
        if not base or not os.path.exists(base):
            continue
        # only check top-level directories and first level files to avoid heavy recursion
        try:
            for root, dirs, files in os.walk(base):
                for f in files:
                    if f.lower().endswith(".exe") and name_lower in f.lower():
                        matches.append(os.path.join(root, f))
                        if len(matches) >= max_hits:
                            return matches
                # limit recursion depth
                # break after checking first level dirs for speed
                for d in dirs:
                    dpath = os.path.join(root, d)
                    # look at directory's files
                    try:
                        for ff in os.listdir(dpath):
                            if ff.lower().endswith(".exe") and name_lower in ff.lower():
                                matches.append(os.path.join(dpath, ff))
                                if len(matches) >= max_hits:
                                    return matches
                    except Exception:
                        continue
                # don't recurse deeply in this helper
                break
        except Exception:
            continue
    return matches


def find_executables(name: str) -> List[str]:
    """
    Try multiple strategies to find executables for 'name':
    - shutil.which (PATH)
    - Program Files and AppData local installs
    - System32 (for built-in apps)
    Returns a list of candidate file paths.
    """
    name = _normalize(name)
    candidates = []

    # 1) PATH
    path_result = shutil.which(name) or shutil.which(name + ".exe")
    if path_result:
        candidates.append(path_result)

    # 2) Common Windows folders
    if SYSTEM == "Windows":
        pf = os.environ.get("ProgramFiles", r"C:\Program Files")
        pf_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        local_prog = os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Local", "Programs")
        sys32 = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "System32")

        search_paths = [pf, pf_x86, local_prog, sys32]
        matches = _search_in_paths(name, search_paths)
        for m in matches:
            if m not in candidates:
                candidates.append(m)

    else:
        # Unix-like: check /usr/bin, /usr/local/bin, /Applications (mac)
        search_paths = ["/usr/bin", "/usr/local/bin", "/Applications"]
        matches = _search_in_paths(name, search_paths)
        for m in matches:
            if m not in candidates:
                candidates.append(m)

    return candidates


def list_programs() -> str:
    """Return a simple list of programs (top-level folders / known executables)."""
    programs = set()
    if SYSTEM == "Windows":
        pf = os.environ.get("ProgramFiles", r"C:\Program Files")
        pf_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        local_prog = os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Local", "Programs")

        for base in [pf, pf_x86, local_prog]:
            if os.path.exists(base):
                try:
                    for item in os.listdir(base):
                        programs.add(item)
                except Exception:
                    continue
        # add some system apps
        programs.update(["Notepad", "Calculator", "Command Prompt"])
    else:
        programs.update(["This tool supports listing on Windows primarily."])

    if not programs:
        return "No programs found."

    # return a readable string
    out = "Programs found (sample):\n" + "\n".join(sorted(list(programs))[:200])
    return out


def open_program(target: str) -> str:
    """
    Try to open a program by name.
    Returns a message describing success/failure.
    """
    target_norm = _normalize(target)

    # quick built-in mappings (friendly names -> executable)
    friendly = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "cmd": "cmd.exe",
        "command prompt": "cmd.exe",
        "powershell": "powershell.exe",
        "chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "edge": "msedge.exe",
        "word": "winword.exe",
        "excel": "excel.exe",
        "whatsapp": "whatsapp.exe",
        "word": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
        "excel": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
        "chrome": "C:\\Program Files\\Google\Chrome\\Application\\chrome.exe",
        "lms": "C:\\Users\\User\\.lmstudio\\bin",
        "vscode": "C:\\Users\\User\\AppData\\Local\\Programs\\Microsoft VS Code",
        "python": "C:\\Users\\User\\AppData\\Local\\Programs\\Python\\Python313"


    }

    # 1) try friendly mapping + PATH
    exe = friendly.get(target_norm)
    if exe:
        path = shutil.which(exe)
        if path:
            try:
                subprocess.Popen([path], shell=False)
                return f"Opening {target}."
            except Exception as e:
                return f"Failed to open {target}: {e}"

    # 2) try shutil.which directly on the target
    path = shutil.which(target_norm) or shutil.which(target_norm + ".exe")
    if path:
        try:
            subprocess.Popen([path], shell=False)
            return f"Opening {target}."
        except Exception as e:
            return f"Failed to open {target}: {e}"

    # 3) search common folders for executables that contain the target name
    candidates = find_executables(target_norm)
    if candidates:
        # pick the first candidate
        try:
            subprocess.Popen([candidates[0]], shell=False)
            return f"Opening {os.path.basename(candidates[0])} (matched for '{target}')."
        except Exception as e:
            return f"Found candidate but failed to open: {e}"

    # 4) last resort: try os.startfile (Windows) or open command on mac
    try:
        if SYSTEM == "Windows":
            # os.startfile may accept a file or .lnk shortcut name if full path provided
            os.startfile(target)
            return f"Attempted to start '{target}'."
        elif SYSTEM == "Darwin":
            subprocess.Popen(["open", "-a", target])
            return f"Attempted to open '{target}'."
        else:
            subprocess.Popen([target], shell=True)
            return f"Attempted to run '{target}'."
    except Exception as e:
        return f"Could not open program '{target}'. Tried common places. Error: {e}\nTip: Try using the exact executable name (e.g., 'chrome' or 'notepad')."


def _terminate_proc(proc: psutil.Process) -> None:
    try:
        proc.terminate()
        proc.wait(timeout=3)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def close_program(target: str) -> str:
    """
    Close processes whose name or executable path contains target.
    Returns summary of closed processes.
    """
    target_norm = _normalize(target)
    closed = []
    not_found = []
    try:
        for proc in list(psutil.process_iter(["pid", "name", "exe", "cmdline"])):
            try:
                name = (proc.info.get("name") or "").lower()
                exe = (proc.info.get("exe") or "") or ""
                cmd = " ".join(proc.info.get("cmdline") or []) if proc.info.get("cmdline") else ""
                if target_norm in name or target_norm in exe.lower() or target_norm in cmd.lower():
                    pid = proc.pid
                    _terminate_proc(proc)
                    closed.append(f"{name} (pid={pid})")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        return f"Error enumerating processes: {e}"

    if not closed:
        return f"No running processes matched '{target}'."
    return f"Closed processes:\n" + "\n".join(closed)


def handle(action: str, params: Optional[str] = None) -> str:
    """
    Unified handle for agent tool-calling.

    action: "list", "open", "close"
    params: program name (required for open/close)
    """
    act = (action or "").strip().lower()
    if act == "list":
        return list_programs()
    if act in {"open", "start", "launch", "run"}:
        if not params:
            return "Please specify the program to open."
        return open_program(params)
    if act in {"close", "kill", "terminate", "stop", "quit"}:
        if not params:
            return "Please specify the program to close."
        return close_program(params)
    return f"Unknown action '{action}'. Valid actions: list, open, close."
