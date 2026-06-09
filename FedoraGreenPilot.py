# ==========================================
# VERSION DE L'APPLICATION  ← À MODIFIER ICI
# ==========================================
APP_VERSION = "1.2.1 | 09.06.2026"
# ==========================================

import sys
# --- Bibliothèque standard ---
import json
import logging
import os
import platform
import re
import shlex
import shutil
import socket
import subprocess
import tempfile

# --- Interface graphique (PyQt6) ---
from PyQt6.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QWidget,
                             QVBoxLayout, QHBoxLayout, QGroupBox, QRadioButton,
                             QPushButton, QMessageBox, QInputDialog, QLineEdit,
                             QDialog, QTextEdit, QLabel, QProgressBar,
                             QTreeWidget, QTreeWidgetItem, QHeaderView, QCheckBox,
                             QScrollArea, QFrame, QSizePolicy, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QLocale, QDir, QEvent
from PyQt6.QtGui import QFont, QIcon, QTextCursor, QPalette, QColor, QPixmap

QDir.addSearchPath("icons", "/usr/share/icons")
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# ==========================================
# UTILITAIRE CHEMIN DE RESSOURCES (POUR APPIMAGE)
# ==========================================
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ==========================================
# VÉRIFICATION DE LA CONNEXION INTERNET
# ==========================================
def check_internet():
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=2)
        return True
    except OSError:
        pass
    return False

# ==========================================
# TRADUCTIONS ET TEXTES CENTRALISÉS
# ==========================================
TR = {
    'fr': {
        'app_title': "Fedora GreenPilot",
        'sidebar_title': "Assistant",
        'welcome': "Prêt à optimiser votre PC",
        'welcome_sub': "Mode Standard : Laissez l'assistant tout faire pour vous.",
        'version_info': f"Version: {APP_VERSION} | Auteur : By$ePpi",
        'autopilot_btn': "🚀 Lancer le Pilote Automatique",
        'autopilot_desc': "Un clic pour tout faire : Mises à jour, pilotes graphiques, vidéos, et codecs.",
        'prog_title': "Opération en cours...",
        'autopilot_step_mok': "1/5 - Préparation de la sécurité matérielle...",
        'autopilot_step_update': "2/5 - Mise à jour du système...",
        'autopilot_step_rpm': "3/5 - Déblocage du catalogue logiciel...",
        'autopilot_step_gpu': "4/5 - Installation des pilotes graphiques...",
        'autopilot_step_codecs': "5/5 - Installation des codecs vidéos...",
        'autopilot_done': "Installation terminée ! PC prêt.",
        'close': "Fermer",
        'toggle_terminal': "Détails techniques",
        'nav_home': "🏠 Accueil",
        'nav_drivers': "🎮 Pilotes & Matériel",
        'nav_softs': "🎬 Logiciels & Vidéos",
        'nav_tpm': "🔐 Déverrouillage Disque",
        'nav_sb': "🛡️ Outils Secure Boot",
        'expert_on': "🧠 Mode Expert : ON",
        'expert_off': "🧠 Mode Expert : OFF",
        'expert_dash_title': "Rapport d'État du Système",
        'luks_alert_text': "<b>Disque chiffré (LUKS) détecté sur ce PC !</b><br>Configurez la puce TPM pour ne plus taper de mot de passe au démarrage.",
        'btn_config_tpm': "Configurer TPM2",
        'title_drivers': "Gestionnaire de Pilotes",
        'title_softs': "Logiciels et Codecs",
        'refresh': "Actualiser",
        'install': "Installer",
        'uninstall': "Désinstaller",
        'installed': "Installé",
        'missing': "Manquant",
        'task_rpmfusion': "Dépôts RPM Fusion",
        'desc_rpmfusion': "Catalogue de logiciels tiers (nécessaire pour NVIDIA et codecs).",
        'task_nvidia': "Pilotes NVIDIA",
        'desc_nvidia': "Pilotes propriétaires pour cartes graphiques NVIDIA.",
        'task_intel': "Pilotes Intel",
        'desc_intel': "Accélération matérielle pour IGP /GPU Intel.",
        'task_radeon': "Pilotes Radeon",
        'desc_radeon': "Accélération matérielle pour IGP /GPU AMD Radeon.",
        'hw_radeon_card': "🔴 Carte Radeon :",
        'task_codecs': "Codecs Multimédias",
        'desc_codecs': "FFmpeg, GStreamer, support HEIC, support complet audio/vidéo.",
        'task_chrome': "Google Chrome",
        'desc_chrome': "Navigateur web de Google.",
        'task_onlyoffice': "OnlyOffice",
        'desc_onlyoffice': "Suite bureautique très compatible MS Office.",
        'task_libreoffice': "LibreOffice",
        'desc_libreoffice': "La suite bureautique libre (installée par défaut).",
        'task_kdepim': "KDE PIM Suite",
        'desc_kdepim': "Suite d'outils personnels KDE (Kontact, Kmail, Calendrier...).",
        'tpm_title': "Gestion LUKS & TPM2",
        'tpm_desc': "Configurez le déverrouillage automatique de votre partition chiffrée.",
        'sb_title': "Outils Avancés (NVIDIA & Boot)",
        'sb_desc': "Gérez les clés MOK et forcez la recompilation des modules noyau.",
        'mok_opt1_title': "Option 1 : Puissance maximale (Jeux, 3D & Écrans externes)",
        'mok_opt1_desc': "<b>Installe NVIDIA.</b> L'assistant gère la sécurité et a généré un mot de passe universel : <b style='color:#2980b9;'>linux</b>.<br>Au prochain redémarrage (sur l'écran bleu), suivez ces 4 étapes simples :",
        'mok_opt2_title': "Option 2 : Mode Basique (Bureautique & Internet)",
        'mok_opt2_desc': "<b>Ignore NVIDIA.</b> Aucun écran bleu au redémarrage, l'installation est 100% invisible.<br>Votre ordinateur utilisera la puce graphique de base (largement suffisant pour le web et les films).",
        'mok_btn_opt1': "Choisir l'Option 1 (Recommandé)",
        'mok_btn_opt2': "Choisir l'Option 2 (Installation Simplifiée)",
        'net_err_title': "Pas de connexion Internet",
        'net_err_desc': "L'assistant a besoin d'une connexion Internet pour télécharger les composants.\nVeuillez vous connecter au Wi-Fi ou brancher un câble réseau.",
        'hw_scanning': "Scan du matériel en cours...",
        'hw_unknown': "Inconnue",
        'status_analyzing': "⏳ Analyse...",
        'hw_nvidia_card': "🎮 Carte NVIDIA :",
        'hw_architecture': "↳ Architecture :",
        'hw_driver': "↳ Pilote :",
        'hw_intel_chip': "🖥️ Puce Intel :",
        'hw_generation': "↳ Génération :",
        'hw_sb_active': "🛡️ Sécurité Secure Boot : <b style='color:#e67e22;'>Active</b><br>",
        'hw_sb_inactive': "🛡️ Sécurité Secure Boot : <b style='color:#e74c3c;'>Désactivée</b><br>",
        'tpm_group_disks': "Disques LUKS détectés",
        'tpm_col_path': "Chemin", 'tpm_col_type': "Type", 'tpm_col_mount': "Montage", 'tpm_col_label': "Label", 'tpm_col_size': "Taille",
        'tpm_group_options': "Options Avancées TPM",
        'tpm_radio_auto': "Auto (Recommandé)",
        'tpm_radio_pin': "Auto + Code PIN",
        'tpm_check_wipe': "Effacer les anciens slots TPM",
        'tpm_check_nopcr': "Ignorer vérification Secure Boot (PCRs)",
        'tpm_btn_wipe': "Désactiver le déverrouillage automatique",
        'tpm_btn_enroll': "Activer TPM2",
        'tpm_diag_auth_title': "Autorisation",
        'tpm_diag_auth_desc': "Mot de passe LUKS actuel :",
        'tpm_diag_pin_title': "PIN",
        'tpm_diag_pin_desc': "Nouveau Code PIN :",
        'tpm_diag_config_title': "Configuration LUKS",
        'tpm_err_sb_title': "Secure Boot inactif",
        'tpm_err_sb_desc': "Le Secure Boot doit être activé pour enrôler le TPM en mode sécurisé.\nCochez l'option 'Ignorer vérification Secure Boot (PCRs)' si vous souhaitez forcer l'installation.",
        'sb_btn_mok': "Générer une clé MOK (NVIDIA)",
        'sb_btn_akmods': "Forcer la compilation Akmods (akmods --force)",
        'sb_btn_dracut': "Régénérer l'image de démarrage (dracut -v --force)",
        'sb_diag_exec_title': "Exécution Avancée",
        'sb_diag_mok_title': "MOK",
        'sb_diag_mok_desc': "Mot de passe temporaire pour Enroll MOK :",
        'prog_prep': "Préparation...",
        'prog_done': "✅ Opération terminée",
        'prog_reboot_req': "⚠️ REDÉMARRAGE REQUIS",
        'prog_reboot_desc': "<b>Tout est installé !</b><br>Redémarrez maintenant. L'écran bleu demandera le mot de passe : <b>linux</b>",
        'prog_ready': "Votre ordinateur est prêt et à jour.",
        'prog_err': "❌ Erreur lors de l'installation",
        'status_done': "Terminé",
        'status_err': "Erreur",
        'status_sys_err': "Erreur système",
        'mok_diag_title': "Choix du mode d'installation",
        'mok_diag_header': "Autorisation de la carte graphique",
        'mok_diag_desc': "Votre PC est hautement sécurisé (Secure Boot). Pour que votre carte NVIDIA fonctionne, choisissez une option ci-dessous :",
        'mok_step1': "<b>1.</b> Choisissez<br><i>Enroll MOK</i>",
        'mok_step2': "<b>2.</b> Choisissez<br><i>Continue</i>",
        'mok_step3': "<b>3.</b> Choisissez<br><i>Yes</i>",
        'mok_step4': "<b>4.</b> Tapez :<br><b style='color:#2980b9; font-size:14pt;'>linux</b>",
        'mok_img_click': "🖼️\n(Cliquez)",
        'car_title': "Visionneuse",
        'car_img_not_found': "❌ Image introuvable\n",
        'msg_success': "Succès",
        'msg_error': "Erreur",
        'btn_install_appimage': "📥 Installer l'application (Menu GNOME/KDE)",
        'btn_uninstall_appimage': "🗑️ Désinstaller l'application",
        'appimage_install_success': "Application copiée et intégrée avec succès !\nVous pouvez la lancer depuis le menu des applications.",
        'appimage_uninstall_success': "L'application a été désinstallée de votre système avec succès.",
        'appimage_err': "Erreur :",
        'pkg_remove_shared': "Les paquets restants sont requis par d'autres pilotes. Aucune suppression nécessaire.",
    },
    'en': {
        'app_title': "Fedora GreenPilot",
        'sidebar_title': "Assistant",
        'welcome': "Ready to optimize your PC",
        'welcome_sub': "Standard Mode: Let the assistant do everything for you.",
        'version_info': f"Version: {APP_VERSION} | Author: By$ePpi",
        'autopilot_btn': "🚀 Run AutoPilot",
        'autopilot_desc': "One click to do everything: Updates, graphics drivers, videos, and codecs.",
        'prog_title': "Operation in progress...",
        'autopilot_step_mok': "1/5 - Preparing hardware security...",
        'autopilot_step_update': "2/5 - Updating system...",
        'autopilot_step_rpm': "3/5 - Unlocking software catalog...",
        'autopilot_step_gpu': "4/5 - Installing graphics drivers...",
        'autopilot_step_codecs': "5/5 - Installing video codecs...",
        'autopilot_done': "Installation complete! PC ready.",
        'close': "Close",
        'toggle_terminal': "Technical details",
        'nav_home': "🏠 Home",
        'nav_drivers': "🎮 Drivers & Hardware",
        'nav_softs': "🎬 Software & Videos",
        'nav_tpm': "🔐 Disk Unlock",
        'nav_sb': "🛡️ Secure Boot Tools",
        'expert_on': "🧠 Expert Mode: ON",
        'expert_off': "🧠 Expert Mode: OFF",
        'expert_dash_title': "System Status Report",
        'luks_alert_text': "<b>Encrypted disk (LUKS) detected!</b><br>Configure the TPM chip to stop typing your password at boot.",
        'btn_config_tpm': "Configure TPM2",
        'title_drivers': "Drivers Manager",
        'title_softs': "Software and Codecs",
        'refresh': "Refresh",
        'install': "Install",
        'uninstall': "Uninstall",
        'installed': "Installed",
        'missing': "Missing",
        'task_rpmfusion': "RPM Fusion Repositories",
        'desc_rpmfusion': "Third-party software catalog (required for NVIDIA and codecs).",
        'task_nvidia': "NVIDIA Drivers",
        'desc_nvidia': "Proprietary drivers for NVIDIA graphics cards. (Gaming optimized, includes 32-bit libs and Gamemode)",
        'task_intel': "Intel Drivers",
        'desc_intel': "Hardware acceleration for INTEL IGP /GPU..",
        'task_radeon': "Radeon Drivers",
        'desc_radeon': "Hardware acceleration for for AMD Radeon IGP /GPU.",
        'hw_radeon_card': "🔴 Radeon Card:",
        'task_codecs': "Multimedia Codecs",
        'desc_codecs': "FFmpeg, GStreamer, HEIC support, full audio/video support.",
        'task_chrome': "Google Chrome",
        'desc_chrome': "Google's web browser.",
        'task_onlyoffice': "OnlyOffice",
        'desc_onlyoffice': "Highly MS Office compatible suite.",
        'task_libreoffice': "LibreOffice",
        'desc_libreoffice': "The free office suite (installed by default).",
        'task_kdepim': "KDE PIM Suite",
        'desc_kdepim': "KDE personal tools suite (Kontact, Kmail, Calendar...).",
        'tpm_title': "LUKS & TPM2 Management",
        'tpm_desc': "Configure automatic unlocking of your encrypted partition.",
        'sb_title': "Advanced Tools (NVIDIA & Boot)",
        'sb_desc': "Manage MOK keys and force kernel modules recompilation.",
        'mok_opt1_title': "Option 1: Maximum Power (Gaming, 3D & External screens)",
        'mok_opt1_desc': "<b>Installs NVIDIA.</b> The assistant manages security and generated a universal password: <b style='color:#2980b9;'>linux</b>.<br>On the next reboot (blue screen), follow these 4 simple steps:",
        'mok_opt2_title': "Option 2: Basic Mode (Office & Internet)",
        'mok_opt2_desc': "<b>Ignores NVIDIA.</b> No blue screen on reboot, installation is 100% invisible.<br>Your PC will use basic graphics (plenty for web and movies).",
        'mok_btn_opt1': "Choose Option 1 (Recommended)",
        'mok_btn_opt2': "Choose Option 2 (Simplified Install)",
        'net_err_title': "No Internet Connection",
        'net_err_desc': "The assistant needs an internet connection to download components.\nPlease connect to Wi-Fi or plug in a network cable.",
        'hw_scanning': "Hardware scan in progress...",
        'hw_unknown': "Unknown",
        'status_analyzing': "⏳ Analyzing...",
        'hw_nvidia_card': "🎮 NVIDIA Card:",
        'hw_architecture': "↳ Architecture:",
        'hw_driver': "↳ Driver:",
        'hw_intel_chip': "🖥️ Intel Chip:",
        'hw_generation': "↳ Generation:",
        'hw_sb_active': "🛡️ Secure Boot Security: <b style='color:#e67e22;'>Active</b><br>",
        'hw_sb_inactive': "🛡️ Secure Boot Security: <b style='color:#e74c3c;'>Disabled</b><br>",
        'tpm_group_disks': "Detected LUKS Disks",
        'tpm_col_path': "Path", 'tpm_col_type': "Type", 'tpm_col_mount': "Mount", 'tpm_col_label': "Label", 'tpm_col_size': "Size",
        'tpm_group_options': "Advanced TPM Options",
        'tpm_radio_auto': "Auto (Recommended)",
        'tpm_radio_pin': "Auto + PIN Code",
        'tpm_check_wipe': "Wipe previous TPM slots",
        'tpm_check_nopcr': "Ignore Secure Boot checks (PCRs)",
        'tpm_btn_wipe': "Disable automatic unlocking",
        'tpm_btn_enroll': "Enable TPM2",
        'tpm_diag_auth_title': "Authorization",
        'tpm_diag_auth_desc': "Current LUKS password:",
        'tpm_diag_pin_title': "PIN",
        'tpm_diag_pin_desc': "New PIN Code:",
        'tpm_diag_config_title': "LUKS Configuration",
        'tpm_err_sb_title': "Secure Boot disabled",
        'tpm_err_sb_desc': "Secure Boot must be enabled to enroll the TPM in secure mode.\nCheck the 'Ignore Secure Boot checks (PCRs)' option if you wish to force the installation.",
        'sb_btn_mok': "Generate MOK key (NVIDIA)",
        'sb_btn_akmods': "Force Akmods compilation (akmods --force)",
        'sb_btn_dracut': "Regenerate boot image (dracut -v --force)",
        'sb_diag_exec_title': "Advanced Execution",
        'sb_diag_mok_title': "MOK",
        'sb_diag_mok_desc': "Temporary password for Enroll MOK:",
        'prog_prep': "Preparing...",
        'prog_done': "✅ Operation completed",
        'prog_reboot_req': "⚠️ REBOOT REQUIRED",
        'prog_reboot_desc': "<b>Everything is installed!</b><br>Reboot now. The blue screen will ask for the password: <b>linux</b>",
        'prog_ready': "Your computer is ready and up to date.",
        'prog_err': "❌ Installation error",
        'status_done': "Done",
        'status_err': "Error",
        'status_sys_err': "System Error",
        'mok_diag_title': "Installation Mode Choice",
        'mok_diag_header': "Graphics Card Authorization",
        'mok_diag_desc': "Your PC is highly secured (Secure Boot). For your NVIDIA card to work, choose an option below:",
        'mok_step1': "<b>1.</b> Choose<br><i>Enroll MOK</i>",
        'mok_step2': "<b>2.</b> Choose<br><i>Continue</i>",
        'mok_step3': "<b>3.</b> Choose<br><i>Yes</i>",
        'mok_step4': "<b>4.</b> Type:<br><b style='color:#2980b9; font-size:14pt;'>linux</b>",
        'mok_img_click': "🖼️\n(Click)",
        'car_title': "Viewer",
        'car_img_not_found': "❌ Image not found\n",
        'msg_success': "Success",
        'msg_error': "Error",
        'btn_install_appimage': "📥 Install App (GNOME/KDE Menu)",
        'btn_uninstall_appimage': "🗑️ Uninstall App",
        'appimage_install_success': "Application copied and integrated successfully!\nYou can now launch it from the applications menu.",
        'appimage_uninstall_success': "Application uninstalled from your system successfully.",
        'appimage_err': "Error:",
        'pkg_remove_shared': "Remaining packages are required by other drivers. No removal needed.",
    }
}

T = {}
sys_lang = QLocale.system().name()[:2]
current_lang = 'fr' if sys_lang == 'fr' else 'en'
T.update(TR[current_lang])

# ==========================================
# UTILITAIRE SYSTÈME
# ==========================================
def get_sys_info():
    os_name = "Linux"
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    os_name = line.split("=")[1].strip().strip('"')
                    break
    except OSError:
        pass
    kernel = platform.release()
    return f"🖥️ {os_name}   |   🐧 Noyau : {kernel}" if current_lang == 'fr' else f"🖥️ {os_name}   |   🐧 Kernel: {kernel}"

# ==========================================
# UTILITAIRE APPIMAGE (Installation et Raccourci)
# ==========================================
APPIMAGE_DEST_DIR = os.path.expanduser("~/.local/bin")
APPIMAGE_DEST_PATH = os.path.join(APPIMAGE_DEST_DIR, "fedora-GreenPilot.AppImage")
DESKTOP_DIR = os.path.expanduser("~/.local/share/applications")
DESKTOP_PATH = os.path.join(DESKTOP_DIR, "fedora-GreenPilot.desktop")

def is_appimage():
    return 'APPIMAGE' in os.environ

def is_appimage_installed():
    return os.path.exists(APPIMAGE_DEST_PATH) and os.path.exists(DESKTOP_PATH)

def install_appimage_desktop():
    appimage_path = os.environ.get('APPIMAGE')
    if not appimage_path:
        return False, "Not running as AppImage."

    try:
        os.makedirs(APPIMAGE_DEST_DIR, exist_ok=True)
        shutil.copy2(appimage_path, APPIMAGE_DEST_PATH)
        os.chmod(APPIMAGE_DEST_PATH, 0o755)

        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={T['app_title']}
Comment={T['welcome_sub']}
Exec="{APPIMAGE_DEST_PATH}"
Icon=system-software-install
Terminal=false
Categories=System;Utility;Settings;
"""
        os.makedirs(DESKTOP_DIR, exist_ok=True)
        with open(DESKTOP_PATH, "w") as f:
            f.write(desktop_content)

        if shutil.which("update-desktop-database"):
            subprocess.run(["update-desktop-database", DESKTOP_DIR], capture_output=True)

        return True, ""
    except Exception as e:
        return False, str(e)

def uninstall_appimage_desktop():
    try:
        if os.path.exists(APPIMAGE_DEST_PATH):
            os.remove(APPIMAGE_DEST_PATH)
        if os.path.exists(DESKTOP_PATH):
            os.remove(DESKTOP_PATH)
        if shutil.which("update-desktop-database"):
            subprocess.run(["update-desktop-database", DESKTOP_DIR], capture_output=True)
        return True, ""
    except Exception as e:
        return False, str(e)

# ==========================================
# DONNÉES DU GESTIONNAIRE DE PAQUETS
# ==========================================
def get_drivers_tasks(nvidia_pkg="akmod-nvidia"):
    return {
        T['task_rpmfusion']: {"type": "rpmfusion", "packages": ["rpmfusion-free-release", "rpmfusion-nonfree-release"], "desc_key": "desc_rpmfusion"},
        T['task_nvidia']: {"type": "dnf", "packages": [
            nvidia_pkg, "xorg-x11-drv-nvidia", "xorg-x11-drv-nvidia-cuda", "libva-nvidia-driver",
            "xorg-x11-drv-nvidia-libs.i686", "xorg-x11-drv-nvidia-cuda-libs.i686",
            "gamemode", "gamemode.i686"
        ], "desc_key": "desc_nvidia"},
        T['task_intel']: {"type": "dnf", "packages": ["intel-media-driver", "libva-intel-driver"], "desc_key": "desc_intel"},
        T['task_radeon']: {"type": "radeon", "packages": ["mesa-va-drivers-freeworld", "mesa-vulkan-drivers", "mesa-vulkan-drivers.i686"], "desc_key": "desc_radeon"}
    }

def get_softs_tasks():
    return {
        # Ajout de libheif-freeworld pour le support HEIC
        T['task_codecs']: {"type": "dnf", "packages": ["ffmpeg", "libavcodec-freeworld", "gstreamer1-plugin-libav", "gstreamer1-plugins-bad-freeworld", "libheif-freeworld"], "desc_key": "desc_codecs"},
        T['task_chrome']: {"type": "chrome", "packages": ["google-chrome-stable"], "desc_key": "desc_chrome"},
        T['task_onlyoffice']: {"type": "onlyoffice", "packages": ["onlyoffice-desktopeditors"], "desc_key": "desc_onlyoffice"},
        # Changement du type vers libreoffice pour cibler libreoffice-core afin de garantir la suppression complète
        T['task_libreoffice']: {"type": "libreoffice", "packages": ["libreoffice", "libreoffice-core"], "desc_key": "desc_libreoffice"},
        T['task_kdepim']: {"type": "dnf", "packages": ["kdepim-runtime", "kmail", "kontact", "korganizer", "kaddressbook", "akregator"], "desc_key": "desc_kdepim"}
    }

# ==========================================
# WORKERS
# ==========================================
class SimpleScriptWorker(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    def __init__(self, script_lines):
        super().__init__()
        self.script_lines = script_lines
    def run(self):
        path = None
        try:
            fd, path = tempfile.mkstemp(text=True)
            with os.fdopen(fd, 'w') as f:
                f.write("\n".join(self.script_lines))
            os.chmod(path, 0o755)
            process = subprocess.Popen(["pkexec", path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in iter(process.stdout.readline, ''):
                if line: self.log_signal.emit(line)
            process.wait()
            self.finished_signal.emit(process.returncode == 0, T['status_done'] if process.returncode == 0 else T['status_err'])
        except Exception as e: self.finished_signal.emit(False, str(e))
        finally:
            if path and os.path.exists(path):
                try: os.remove(path)
                except Exception: pass

class AutoPilotSingleScriptWorker(QThread):
    log_signal = pyqtSignal(str)
    step_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    def __init__(self, hw_info, mok_password=None, skip_nvidia=False):
        super().__init__()
        self.hw, self.mok_password, self.skip_nvidia = hw_info, mok_password, skip_nvidia

    def run(self):
        script = ["#!/bin/bash"]
        # On n'utilise pas 'set -e' globalement : certaines commandes réseau peuvent
        # échouer de façon non-critique (ex: dépôts déjà installés, paquets optionnels).
        # Chaque étape critique utilise ses propres || true ou || fallback.

        if self.mok_password and not self.skip_nvidia:
            script.append(f"echo '---AUTOPILOT_STEP---:{T['autopilot_step_mok']}'")
            script.append("dnf5 install -y akmods mokutil expect openssl || dnf install -y akmods mokutil expect openssl")
            script.append("kmodgenca -a || true")
            script.append(f"export MOK_PASS={shlex.quote(self.mok_password)}")
            script.append("expect << 'EOF'")
            script.append("spawn mokutil --import /etc/pki/akmods/certs/public_key.der")
            script.append("expect {")
            script.append("  \"already enrolled\" { exit 0 }")
            script.append("  \"input password:\" {")
            script.append("    send -- \"$env(MOK_PASS)\\r\"")
            script.append("    expect \"input password again:\"")
            script.append("    send -- \"$env(MOK_PASS)\\r\"")
            script.append("    expect eof")
            script.append("  }")
            script.append("}")
            script.append("EOF")

        script.append(f"echo '---AUTOPILOT_STEP---:{T['autopilot_step_update']}'")
        script.append("dnf5 upgrade -y --refresh || dnf upgrade -y --refresh")

        script.append(f"echo '---AUTOPILOT_STEP---:{T['autopilot_step_rpm']}'")
        script.append("VER=$(rpm -E %fedora)")
        script.append("dnf5 install -y https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$VER.noarch.rpm https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$VER.noarch.rpm || true")

        script.append(f"echo '---AUTOPILOT_STEP---:{T['autopilot_step_gpu']}'")
        if self.hw['has_nvidia'] and not self.skip_nvidia:
            pkgs_nv = " ".join(get_drivers_tasks(self.hw.get('nvidia_package', 'akmod-nvidia'))[T['task_nvidia']]['packages'])
            # Utilisation de --allowerasing
            script.append(f"dnf5 install -y --allowerasing {pkgs_nv} || dnf install -y --allowerasing {pkgs_nv} || true")
        if self.hw['has_intel']:
            pkgs_intel = " ".join(get_drivers_tasks()[T['task_intel']]['packages'])
            # Utilisation de --allowerasing
            script.append(f"dnf5 install -y --allowerasing {pkgs_intel} || dnf install -y --allowerasing {pkgs_intel} || true")
        if self.hw.get('has_radeon'):
            pkgs_rad = " ".join(get_drivers_tasks()[T['task_radeon']]['packages'])
            # Utilisation de --allowerasing
            script.append(f"dnf5 install -y --allowerasing {pkgs_rad} || dnf install -y --allowerasing {pkgs_rad} || true")

        script.append(f"echo '---AUTOPILOT_STEP---:{T['autopilot_step_codecs']}'")
        pkgs_codecs = " ".join(get_softs_tasks()[T['task_codecs']]['packages'])
        # Utilisation de --allowerasing
        script.append(f"dnf5 install -y --allowerasing {pkgs_codecs} || dnf install -y --allowerasing {pkgs_codecs} || true")

        path = None
        try:
            fd, path = tempfile.mkstemp(text=True)
            with os.fdopen(fd, 'w') as f: f.write("\n".join(script))
            os.chmod(path, 0o755)
            process = subprocess.Popen(["pkexec", path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in iter(process.stdout.readline, ''):
                if line:
                    if "---AUTOPILOT_STEP---:" in line: self.step_signal.emit(line.split(":", 1)[1].strip())
                    else: self.log_signal.emit(line)
            process.wait()
            self.finished_signal.emit(process.returncode == 0, T['autopilot_done'] if process.returncode == 0 else T['status_sys_err'])
        except Exception as e: self.finished_signal.emit(False, str(e))
        finally:
            if path and os.path.exists(path):
                try: os.remove(path)
                except Exception: pass

class HardwareScanner(QThread):
    result_signal = pyqtSignal(dict)
    def run(self):
        hw = {
            'has_nvidia': False, 'has_intel': False, 'has_radeon': False, 'secure_boot': False, 'has_luks': False,
            'nvidia_model': T['hw_unknown'], 'nvidia_arch': T['hw_unknown'], 'nvidia_package': 'akmod-nvidia',
            'intel_model': T['hw_unknown'], 'intel_arch': T['hw_unknown'],
            'radeon_model': T['hw_unknown'], 'radeon_arch': T['hw_unknown'],
            'nvidia_installed': False, 'intel_installed': False, 'radeon_installed': False
        }
        try:
            res = subprocess.run(["lspci"], capture_output=True, text=True)
            for line in res.stdout.split('\n'):
                line_lower = line.lower()
                if "vga" in line_lower or "3d" in line_lower:
                    if "nvidia" in line_lower:
                        hw['has_nvidia'] = True
                        match = re.search(r'NVIDIA Corporation\s+(.*)', line, re.IGNORECASE)
                        if match:
                            raw = match.group(1).split('(rev')[0].strip()
                            hw['nvidia_model'] = raw

                            arch, pkg = T['hw_unknown'], "akmod-nvidia"
                            if re.search(r'\bAD\d+', raw, re.I) or "rtx 40" in raw.lower(): arch, pkg = "Ada Lovelace", "akmod-nvidia"
                            elif re.search(r'\bGA\d+', raw, re.I) or "rtx 30" in raw.lower(): arch, pkg = "Ampere", "akmod-nvidia"
                            elif re.search(r'\bTU\d+', raw, re.I) or "rtx 20" in raw.lower() or "gtx 16" in raw.lower(): arch, pkg = "Turing", "akmod-nvidia"
                            elif re.search(r'\bGP\d+', raw, re.I) or "gtx 10" in raw.lower() or "mx" in raw.lower(): arch, pkg = "Pascal", "akmod-nvidia-580xx"
                            elif re.search(r'\bGM\d+', raw, re.I) or "gtx 9" in raw.lower() or "gtx 8" in raw.lower(): arch, pkg = "Maxwell", "akmod-nvidia-580xx"
                            elif re.search(r'\bGK\d+', raw, re.I) or "gtx 7" in raw.lower() or "gtx 6" in raw.lower(): arch, pkg = "Kepler", "akmod-nvidia-470xx"

                            hw['nvidia_arch'] = arch
                            hw['nvidia_package'] = pkg

                            try:
                                res_pkg = subprocess.run(["rpm", "-q", pkg], capture_output=True)
                                hw['nvidia_installed'] = (res_pkg.returncode == 0)
                            except Exception:
                                hw['nvidia_installed'] = False

                    elif "intel" in line_lower:
                        hw['has_intel'] = True
                        match = re.search(r'Intel Corporation\s+(.*)', line, re.IGNORECASE)
                        if match:
                            raw = match.group(1).split('(rev')[0].strip()
                            raw_clean = raw.replace("Integrated Graphics Controller", "").replace("VGA compatible controller", "").strip()
                            hw['intel_model'] = raw_clean

                            arch = T['hw_unknown']
                            if "iris" in raw.lower() or "xe" in raw.lower(): arch = "Iris Xe"
                            elif "alder" in raw.lower(): arch = "Alder Lake"
                            elif "meteor" in raw.lower(): arch = "Meteor Lake"
                            elif "raptor" in raw.lower(): arch = "Raptor Lake"
                            elif "rocket" in raw.lower(): arch = "Rocket Lake"
                            elif "tiger" in raw.lower(): arch = "Tiger Lake"
                            elif "ice" in raw.lower(): arch = "Ice Lake"
                            elif "comet" in raw.lower(): arch = "Comet Lake"
                            elif "coffee" in raw.lower(): arch = "Coffee Lake"
                            elif "kaby" in raw.lower(): arch = "Kaby Lake"
                            elif "sky" in raw.lower(): arch = "Skylake"
                            elif "haswell" in raw.lower(): arch = "Haswell"
                            elif "uhd" in raw.lower(): arch = "UHD Graphics"
                            elif "hd" in raw.lower(): arch = "HD Graphics"

                            hw['intel_arch'] = arch

                            try:
                                res_int = subprocess.run(["rpm", "-q", "intel-media-driver"], capture_output=True)
                                hw['intel_installed'] = (res_int.returncode == 0)
                            except Exception:
                                hw['intel_installed'] = False

                    elif "amd" in line_lower or "radeon" in line_lower or "advanced micro devices" in line_lower:
                        hw['has_radeon'] = True
                        match = re.search(r'(?:Advanced Micro Devices.*?|AMD)\s*\[?(.*?)\]?\s*(?:\(rev|$)', line, re.IGNORECASE)
                        if not match:
                            match = re.search(r'Radeon\s+(.*)', line, re.IGNORECASE)
                        if match:
                            raw = match.group(1).split('(rev')[0].strip().strip('[]')
                            hw['radeon_model'] = raw

                            arch = T['hw_unknown']
                            raw_l = raw.lower()
                            if "rx 7" in raw_l or "gfx11" in raw_l or "navi3" in raw_l: arch = "RDNA 3"
                            elif "rx 6" in raw_l or "gfx10" in raw_l or "navi2" in raw_l: arch = "RDNA 2"
                            elif "rx 5" in raw_l or "navi1" in raw_l: arch = "RDNA 1"
                            elif "vega" in raw_l or "gfx9" in raw_l: arch = "Vega (GCN5)"
                            elif "rx 4" in raw_l or "polaris" in raw_l or "rx 470" in raw_l or "rx 480" in raw_l or "rx 580" in raw_l: arch = "Polaris (GCN4)"
                            elif "fury" in raw_l or "fiji" in raw_l: arch = "Fiji (GCN3)"
                            elif "r9" in raw_l or "r7" in raw_l or "r5" in raw_l: arch = "GCN"
                            hw['radeon_arch'] = arch

                        try:
                            res_rad = subprocess.run(["rpm", "-q", "mesa-va-drivers-freeworld"], capture_output=True)
                            hw['radeon_installed'] = (res_rad.returncode == 0)
                        except Exception:
                            hw['radeon_installed'] = False
        except Exception:
            pass

        try:
            if shutil.which("mokutil"):
                res3 = subprocess.run(["mokutil", "--sb-state"], capture_output=True, text=True)
                if "enabled" in res3.stdout.lower(): hw['secure_boot'] = True
        except Exception: pass
        try:
            res4 = subprocess.run(["lsblk", "--json", "-o", "FSTYPE"], capture_output=True, text=True)
            if "crypto_LUKS" in res4.stdout: hw['has_luks'] = True
        except Exception: pass

        self.result_signal.emit(hw)

class FedoraRefreshWorker(QThread):
    status_signal = pyqtSignal(str, bool)
    finished_signal = pyqtSignal()
    def __init__(self, tasks):
        super().__init__()
        self.tasks = tasks
    def run(self):
        for name, info in self.tasks.items():
            is_installed = self.check_is_installed(info.get("packages", []), info.get("type", "dnf"))
            self.status_signal.emit(name, is_installed)
        self.finished_signal.emit()

    def check_is_installed(self, packages, ptype):
        try:
            if ptype == "chrome": return subprocess.run(["rpm", "-q", "google-chrome-stable"], capture_output=True).returncode == 0
            # LibreOffice : cibler libreoffice-core qui est toujours installé si la suite est présente
            if ptype == "libreoffice": return subprocess.run(["rpm", "-q", "libreoffice-core"], capture_output=True).returncode == 0
            if not packages: return False
            for pkg in packages:
                if subprocess.run(["rpm", "-q", pkg], capture_output=True).returncode != 0: return False
            return True
        except Exception: return False

class DiskScanWorker(QThread):
    result_signal = pyqtSignal(list, dict)
    def run(self):
        try:
            res = subprocess.run(["lsblk", "--json", "-o", "PATH,KNAME,PKNAME,TYPE,FSTYPE,SIZE,LABEL,MOUNTPOINTS"], capture_output=True, text=True)
            data = json.loads(res.stdout)
            all_devices = []
            def flatten(devs):
                for d in devs:
                    all_devices.append(d)
                    flatten(d.get("children", []))
            flatten(data.get("blockdevices", []))
            c_map = {}
            for d in all_devices:
                if d.get("pkname"): c_map.setdefault(d.get("pkname"), []).append(d)
            def has_luks(kname):
                dev = next((d for d in all_devices if d.get("kname") == kname), None)
                if not dev: return False
                if dev.get("fstype") == "crypto_LUKS": return True
                return any(has_luks(c.get("kname")) for c in c_map.get(kname, []))
            roots = [d for d in all_devices if d.get("type") == "disk"]
            self.result_signal.emit([r for r in roots if has_luks(r.get("kname"))], c_map)
        except Exception: self.result_signal.emit([], {})

# ==========================================
# UI COMPONENTS : IMAGES & CARROUSEL
# ==========================================
class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

class CarouselDialog(QDialog):
    def __init__(self, images_list, start_index=0, parent=None):
        super().__init__(parent)
        self.images_list = images_list
        self.current_idx = start_index
        self.setWindowTitle(T['car_title'])
        self.setMinimumSize(900, 700)
        self.setModal(True)

        layout = QVBoxLayout(self)

        self.img_display = ClickableLabel()
        self.img_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_display.clicked.connect(self.next_image)
        self.img_display.setCursor(Qt.CursorShape.PointingHandCursor)

        nav_layout = QHBoxLayout()

        self.btn_prev = QPushButton("◀")
        self.btn_prev.setFixedSize(60, 60)
        self.btn_prev.setStyleSheet("font-size: 24pt; font-weight: bold; background: rgba(128,128,128,0.2); color: palette(text); border: none; border-radius: 10px;")
        self.btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev.clicked.connect(self.prev_image)

        self.btn_next = QPushButton("▶")
        self.btn_next.setFixedSize(60, 60)
        self.btn_next.setStyleSheet("font-size: 24pt; font-weight: bold; background: rgba(128,128,128,0.2); color: palette(text); border: none; border-radius: 10px;")
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.clicked.connect(self.next_image)

        nav_layout.addWidget(self.btn_prev)
        nav_layout.addStretch()
        nav_layout.addWidget(self.btn_next)

        overlay_layout = QVBoxLayout()
        overlay_layout.addStretch()
        overlay_layout.addLayout(nav_layout)
        overlay_layout.addStretch()

        main_content_layout = QHBoxLayout()
        main_content_layout.addWidget(self.img_display)

        self.img_display.setLayout(overlay_layout)
        layout.addLayout(main_content_layout, stretch=1)

        self.btn_close = QPushButton(T['close'])
        self.btn_close.setMinimumHeight(50)
        self.btn_close.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; font-size: 14pt; border-radius: 10px;")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(self.accept)
        layout.addWidget(self.btn_close)

        self.update_image()

    def update_image(self):
        filename = self.images_list[self.current_idx]
        pix = QPixmap(filename)
        if not pix.isNull():
            scaled_pix = pix.scaled(800, 550, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.img_display.setPixmap(scaled_pix)
        else:
            self.img_display.setText(T['car_img_not_found'] + f"({filename})")
            self.img_display.setStyleSheet("color: palette(text); font-size: 20pt;")

        self.btn_prev.setVisible(self.current_idx > 0)
        self.btn_next.setText("▶" if self.current_idx < len(self.images_list) - 1 else "✖")

    def next_image(self):
        if self.current_idx < len(self.images_list) - 1:
            self.current_idx += 1
            self.update_image()
        else:
            self.accept()

    def prev_image(self):
        if self.current_idx > 0:
            self.current_idx -= 1
            self.update_image()

# ==========================================
# DIALOGUES CLASSIQUES
# ==========================================
class TerminalDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(800, 500)
        self.setModal(True)
        layout = QVBoxLayout(self)
        self.header = QLabel("⏳ " + title)
        self.header.setStyleSheet("font-size: 14pt; font-weight: bold; color: #2980b9; padding: 10px;")
        layout.addWidget(self.header, alignment=Qt.AlignmentFlag.AlignCenter)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setObjectName("TerminalView")
        self.log_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.log_view)
        self.btn_close = QPushButton(T['close'])
        self.btn_close.setEnabled(False)
        self.btn_close.setObjectName("PrimaryButton")
        self.btn_close.clicked.connect(self.accept)
        layout.addWidget(self.btn_close, alignment=Qt.AlignmentFlag.AlignCenter)

    def append_log(self, text):
        cursor = self.log_view.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self.log_view.setTextCursor(cursor)
        self.log_view.ensureCursorVisible()

    def set_finished(self):
        self.header.setText(T['prog_done'])
        self.header.setStyleSheet("font-size: 14pt; font-weight: bold; color: #27ae60; padding: 10px;")
        self.btn_close.setEnabled(True)

class SmartProgressDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(750, 250)
        self.setModal(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        self.header = QLabel("⏳ " + title)
        self.header.setStyleSheet("font-size: 14pt; font-weight: bold; color: #2980b9;")
        layout.addWidget(self.header, alignment=Qt.AlignmentFlag.AlignCenter)
        self.lbl_step = QLabel(T['prog_prep'])
        self.lbl_step.setStyleSheet("font-size: 11pt; color: gray;")
        layout.addWidget(self.lbl_step, alignment=Qt.AlignmentFlag.AlignCenter)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)
        self.btn_toggle_term = QPushButton(T['toggle_terminal'])
        self.btn_toggle_term.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_term.setStyleSheet("background: transparent; color: #3584e4; border: none; text-decoration: underline;")
        self.btn_toggle_term.clicked.connect(self.toggle_terminal)
        layout.addWidget(self.btn_toggle_term, alignment=Qt.AlignmentFlag.AlignCenter)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setObjectName("TerminalView")
        self.log_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.log_view.hide()
        layout.addWidget(self.log_view)
        self.btn_close = QPushButton(T['close'])
        self.btn_close.setEnabled(False)
        self.btn_close.setObjectName("PrimaryButton")
        self.btn_close.clicked.connect(self.accept)
        layout.addWidget(self.btn_close, alignment=Qt.AlignmentFlag.AlignCenter)

    def set_step(self, text): self.lbl_step.setText(text)

    def append_log(self, text):
        cursor = self.log_view.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self.log_view.setTextCursor(cursor)
        self.log_view.ensureCursorVisible()

    def set_finished(self, success, msg, requires_reboot=False):
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        if success:
            if requires_reboot:
                self.header.setText(T['prog_reboot_req'])
                self.header.setStyleSheet("font-size: 16pt; font-weight: bold; color: #e67e22;")
                self.lbl_step.setText(T['prog_reboot_desc'])
                self.lbl_step.setStyleSheet("font-size: 12pt; color: #e67e22;")
            else:
                self.header.setText("✅ " + T['autopilot_done'])
                self.header.setStyleSheet("font-size: 14pt; font-weight: bold; color: #27ae60;")
                self.lbl_step.setText(T['prog_ready'])
        else:
            self.header.setText(T['prog_err'])
            self.header.setStyleSheet("font-size: 14pt; font-weight: bold; color: #e74c3c;")
            self.log_view.show()
            self.resize(self.width(), 500)
        self.btn_close.setEnabled(True)

    def toggle_terminal(self):
        if self.log_view.isVisible():
            self.log_view.hide()
            self.resize(self.width(), 250)
        else:
            self.log_view.show()
            self.resize(self.width(), 500)

class MokSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T['mok_diag_title'])
        self.setMinimumSize(850, 650)
        self.setModal(True)
        self.password = None
        self.skip_nvidia = False

        self.mok_images = [
            resource_path("mok_step1.png"),
            resource_path("mok_step2.png"),
            resource_path("mok_step3.png"),
            resource_path("mok_step4.png")
        ]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        header_layout = QHBoxLayout()
        icon = QLabel("🛡️")
        icon.setStyleSheet("font-size: 35pt;")
        header_layout.addWidget(icon)

        title_layout = QVBoxLayout()
        title = QLabel(T['mok_diag_header'])
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #2980b9;")
        desc = QLabel(T['mok_diag_desc'])
        desc.setStyleSheet("font-size: 11pt; color: gray;")
        desc.setWordWrap(True)
        title_layout.addWidget(title)
        title_layout.addWidget(desc)
        header_layout.addLayout(title_layout, stretch=1)

        layout.addLayout(header_layout)
        layout.addSpacing(15)

        self.group_ok = QGroupBox(T['mok_opt1_title'])
        self.group_ok.setStyleSheet("QGroupBox { font-weight: bold; color: #27ae60; border: 2px solid #27ae60; border-radius: 8px; padding: 15px; }")
        lo1 = QVBoxLayout(self.group_ok)

        inst_lbl = QLabel(T['mok_opt1_desc'])
        inst_lbl.setStyleSheet("font-size: 11pt; color: palette(text); font-weight: normal;")
        inst_lbl.setWordWrap(True)
        lo1.addWidget(inst_lbl)

        steps_layout = QHBoxLayout()

        def create_step(text_html, image_filename, index):
            w = QWidget()
            vl = QVBoxLayout(w)
            vl.setContentsMargins(5, 5, 5, 5)

            img_lbl = ClickableLabel()
            img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            img_lbl.setCursor(Qt.CursorShape.PointingHandCursor)

            pix = QPixmap(image_filename)
            if not pix.isNull():
                img_lbl.setPixmap(pix.scaled(160, 140, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                img_lbl.setFixedSize(160, 100)
                img_lbl.setText(T['mok_img_click'])
                img_lbl.setStyleSheet("background-color: rgba(128,128,128,0.1); border-radius: 8px; color: gray; text-align: center;")

            img_lbl.clicked.connect(lambda: self.open_carousel(index))

            txt_lbl = QLabel(text_html)
            txt_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            txt_lbl.setStyleSheet("font-size: 10pt; font-weight: normal; color: palette(text);")
            txt_lbl.setWordWrap(True)

            vl.addWidget(img_lbl)
            vl.addWidget(txt_lbl)
            return w

        steps_layout.addWidget(create_step(T['mok_step1'], self.mok_images[0], 0))
        steps_layout.addWidget(create_step(T['mok_step2'], self.mok_images[1], 1))
        steps_layout.addWidget(create_step(T['mok_step3'], self.mok_images[2], 2))
        steps_layout.addWidget(create_step(T['mok_step4'], self.mok_images[3], 3))

        lo1.addLayout(steps_layout)

        self.btn_ok = QPushButton(T['mok_btn_opt1'])
        self.btn_ok.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 12px; border-radius: 6px; font-size: 11pt;")
        self.btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ok.clicked.connect(self.choose_ok)
        lo1.addWidget(self.btn_ok)
        layout.addWidget(self.group_ok)

        self.group_skip = QGroupBox(T['mok_opt2_title'])
        self.group_skip.setStyleSheet("QGroupBox { font-weight: bold; color: #7f8c8d; border: 2px solid #bdc3c7; border-radius: 8px; padding: 15px; margin-top: 10px; }")
        lo2 = QVBoxLayout(self.group_skip)
        skip_lbl = QLabel(T['mok_opt2_desc'])
        skip_lbl.setStyleSheet("font-size: 10pt; color: palette(text); font-weight: normal;")
        skip_lbl.setWordWrap(True)
        lo2.addWidget(skip_lbl)
        self.btn_skip = QPushButton(T['mok_btn_opt2'])
        self.btn_skip.setStyleSheet("background-color: #ecf0f1; color: #2c3e50; font-weight: bold; padding: 10px; border-radius: 6px;")
        self.btn_skip.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_skip.clicked.connect(self.choose_skip)
        lo2.addWidget(self.btn_skip)
        layout.addWidget(self.group_skip)

        layout.addStretch()

    def open_carousel(self, start_idx):
        car = CarouselDialog(self.mok_images, start_idx, self)
        car.exec()

    def choose_ok(self):
        self.password = "linux"
        self.skip_nvidia = False
        self.accept()
    def choose_skip(self):
        self.password = None
        self.skip_nvidia = True
        self.accept()

# ==========================================
# VIEWS (Débutant & Expert)
# ==========================================
class HomeWidget(QWidget):
    request_tab_change = pyqtSignal(int)

    def __init__(self, parent_main):
        super().__init__()
        self.parent_main = parent_main
        self.hw_info = {}

        main_layout = QVBoxLayout(self)
        self.mode_stack = QStackedWidget()

        # --- MODE STANDARD ---
        self.standard_container = QWidget()
        std_layout = QVBoxLayout(self.standard_container)

        self.icon = QLabel("🤖")
        self.icon.setStyleSheet("font-size: 70pt;")
        self.title = QLabel(T['welcome'])
        self.title.setStyleSheet("font-size: 28pt; font-weight: bold;")

        self.version_lbl = QLabel(T['version_info'])
        self.version_lbl.setStyleSheet("font-size: 11pt; color: #7f8c8d; font-style: italic;")

        self.sys_info_lbl = QLabel(get_sys_info())
        self.sys_info_lbl.setStyleSheet("font-size: 12pt; font-weight: bold; color: #2980b9; padding-top: 10px;")

        self.subtitle = QLabel(T['welcome_sub'])
        self.subtitle.setStyleSheet("font-size: 14pt; color: gray; padding-top: 10px;")

        self.appimage_layout = QHBoxLayout()
        if is_appimage():
            self.btn_appimage = QPushButton()
            self.btn_appimage.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_appimage.clicked.connect(self.toggle_appimage_install)
            self.update_appimage_button_ui()

            self.appimage_layout.addStretch()
            self.appimage_layout.addWidget(self.btn_appimage)
            self.appimage_layout.addStretch()

        self.lbl_hw_status = QLabel(T['hw_scanning'])
        self.lbl_hw_status.setObjectName("HomeOSCard")

        self.btn_autopilot = QPushButton(T['autopilot_btn'])
        self.btn_autopilot.setObjectName("PrimaryButton")
        self.btn_autopilot.setMinimumHeight(70)
        self.btn_autopilot.setMinimumWidth(400)
        f = self.btn_autopilot.font()
        f.setPointSize(14)
        f.setBold(True)
        self.btn_autopilot.setFont(f)
        self.btn_autopilot.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_autopilot.clicked.connect(self.run_autopilot)

        self.lbl_autopilot_desc = QLabel(T['autopilot_desc'])
        self.lbl_autopilot_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_autopilot_desc.setStyleSheet("color: gray;")

        std_layout.addStretch()
        std_layout.addWidget(self.icon, alignment=Qt.AlignmentFlag.AlignCenter)
        std_layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        std_layout.addWidget(self.version_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        std_layout.addWidget(self.sys_info_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        if is_appimage():
            std_layout.addSpacing(10)
            std_layout.addLayout(self.appimage_layout)

        std_layout.addSpacing(15)
        std_layout.addWidget(self.subtitle, alignment=Qt.AlignmentFlag.AlignCenter)
        std_layout.addSpacing(30)
        std_layout.addWidget(self.lbl_hw_status, alignment=Qt.AlignmentFlag.AlignCenter)
        std_layout.addSpacing(40)
        std_layout.addWidget(self.btn_autopilot, alignment=Qt.AlignmentFlag.AlignCenter)
        std_layout.addWidget(self.lbl_autopilot_desc)
        std_layout.addStretch()

        # --- MODE EXPERT (DASHBOARD) ---
        self.expert_container = QWidget()
        exp_layout = QVBoxLayout(self.expert_container)
        exp_layout.setContentsMargins(20, 20, 20, 20)

        self.luks_alert_card = QFrame()
        self.luks_alert_card.setStyleSheet("QFrame { background-color: rgba(230, 126, 34, 0.1); border: 2px solid #e67e22; border-radius: 10px; }")
        luks_layout = QHBoxLayout(self.luks_alert_card)
        lbl_icon = QLabel("🔒")
        lbl_icon.setStyleSheet("font-size: 30pt; border: none; background: transparent;")
        lbl_text = QLabel(T['luks_alert_text'])
        lbl_text.setStyleSheet("border: none; background: transparent;")
        self.btn_go_tpm = QPushButton(T['btn_config_tpm'])
        self.btn_go_tpm.setObjectName("PrimaryButton")
        self.btn_go_tpm.clicked.connect(lambda: self.request_tab_change.emit(3))

        luks_layout.addWidget(lbl_icon)
        luks_layout.addWidget(lbl_text, stretch=1)
        luks_layout.addWidget(self.btn_go_tpm)
        self.luks_alert_card.hide()
        exp_layout.addWidget(self.luks_alert_card)

        exp_layout.addSpacing(15)

        self.dash_group = QGroupBox(T['expert_dash_title'])
        self.dash_layout = QVBoxLayout(self.dash_group)
        self.dash_layout.setSpacing(12)
        self.dash_layout.setContentsMargins(20, 25, 20, 20)

        self.status_labels = {}
        all_tasks = {}
        all_tasks.update(get_drivers_tasks())
        all_tasks.update(get_softs_tasks())

        for name in all_tasks.keys():
            row = QHBoxLayout()
            lbl_name = QLabel(name)
            lbl_name.setStyleSheet("font-size: 11pt; font-weight: bold;")

            lbl_status = QLabel(T['status_analyzing'])
            lbl_status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.status_labels[name] = lbl_status

            row.addWidget(lbl_name)
            row.addStretch()
            row.addWidget(lbl_status)

            self.dash_layout.addLayout(row)
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            line.setStyleSheet("background-color: rgba(128,128,128,0.1); border: none; height: 1px;")
            self.dash_layout.addWidget(line)

        exp_layout.addWidget(self.dash_group)
        exp_layout.addStretch()

        self.mode_stack.addWidget(self.standard_container)
        self.mode_stack.addWidget(self.expert_container)
        main_layout.addWidget(self.mode_stack)

    def update_appimage_button_ui(self):
        if is_appimage_installed():
            self.btn_appimage.setText(T['btn_uninstall_appimage'])
            self.btn_appimage.setStyleSheet("background: transparent; border: 1px solid #e74c3c; color: #e74c3c; border-radius: 8px; padding: 6px 15px; font-weight: bold;")
        else:
            self.btn_appimage.setText(T['btn_install_appimage'])
            self.btn_appimage.setStyleSheet("background: transparent; border: 1px solid #27ae60; color: #27ae60; border-radius: 8px; padding: 6px 15px; font-weight: bold;")

    def toggle_appimage_install(self):
        if is_appimage_installed():
            success, error = uninstall_appimage_desktop()
            if success:
                QMessageBox.information(self, T['msg_success'], T['appimage_uninstall_success'])
            else:
                QMessageBox.critical(self, T['msg_error'], f"{T['appimage_err']}\n{error}")
        else:
            success, error = install_appimage_desktop()
            if success:
                QMessageBox.information(self, T['msg_success'], T['appimage_install_success'])
            else:
                QMessageBox.critical(self, T['msg_error'], f"{T['appimage_err']}\n{error}")
        self.update_appimage_button_ui()

    def set_expert_mode(self, is_expert):
        if is_expert:
            self.mode_stack.setCurrentIndex(1)
            self.refresh_dashboard()
        else:
            self.mode_stack.setCurrentIndex(0)

    def refresh_dashboard(self):
        all_tasks = {}
        current_nv_pkg = self.hw_info.get('nvidia_package', 'akmod-nvidia') if self.hw_info else "akmod-nvidia"
        all_tasks.update(get_drivers_tasks(current_nv_pkg))
        all_tasks.update(get_softs_tasks())

        for name in all_tasks.keys():
            if name in self.status_labels:
                self.status_labels[name].setText(T['status_analyzing'])
                self.status_labels[name].setStyleSheet("color: gray; font-weight: bold;")

        self.worker = FedoraRefreshWorker(all_tasks)
        self.worker.status_signal.connect(self.update_dashboard_row)
        self.worker.start()

    def update_dashboard_row(self, name, is_installed):
        if name in self.status_labels:
            if is_installed:
                self.status_labels[name].setText(f"✅ {T['installed']}")
                self.status_labels[name].setStyleSheet("color: #27ae60; font-weight: bold;")
            else:
                self.status_labels[name].setText(f"❌ {T['missing']}")
                self.status_labels[name].setStyleSheet("color: #e74c3c; font-weight: bold;")

    def update_hardware_ui(self, hw):
        self.hw_info = hw
        status = "<span style='font-size:12pt; line-height: 1.5;'>"
        if hw['has_nvidia']:
            status += f"{T['hw_nvidia_card']} <b>{hw.get('nvidia_model', T['hw_unknown'])}</b><br>"
            status += f"&nbsp;&nbsp;&nbsp;&nbsp;{T['hw_architecture']} <i>{hw.get('nvidia_arch', T['hw_unknown'])}</i><br>"
            is_nv_inst = hw.get('nvidia_installed', False)
            nv_status_txt = f"<span style='color:#27ae60;'><b>✅ {T['installed']}</b></span>" if is_nv_inst else f"<span style='color:#e74c3c;'><b>❌ {T['missing']}</b></span>"
            status += f"&nbsp;&nbsp;&nbsp;&nbsp;{T['hw_driver']} <b style='color:#2980b9;'>{hw.get('nvidia_package', 'akmod-nvidia')}</b> ({nv_status_txt})<br>"

        if hw['has_intel']:
            status += f"{T['hw_intel_chip']} <b>{hw.get('intel_model', T['hw_unknown'])}</b><br>"
            status += f"&nbsp;&nbsp;&nbsp;&nbsp;{T['hw_generation']} <i>{hw.get('intel_arch', T['hw_unknown'])}</i><br>"
            is_int_inst = hw.get('intel_installed', False)
            int_status_txt = f"<span style='color:#27ae60;'><b>✅ {T['installed']}</b></span>" if is_int_inst else f"<span style='color:#e74c3c;'><b>❌ {T['missing']}</b></span>"
            status += f"&nbsp;&nbsp;&nbsp;&nbsp;{T['hw_driver']} <b style='color:#2980b9;'>intel-media-driver</b> ({int_status_txt})<br>"

        if hw.get('has_radeon'):
            status += f"{T['hw_radeon_card']} <b>{hw.get('radeon_model', T['hw_unknown'])}</b><br>"
            status += f"&nbsp;&nbsp;&nbsp;&nbsp;{T['hw_architecture']} <i>{hw.get('radeon_arch', T['hw_unknown'])}</i><br>"
            is_rad_inst = hw.get('radeon_installed', False)
            rad_status_txt = f"<span style='color:#27ae60;'><b>✅ {T['installed']}</b></span>" if is_rad_inst else f"<span style='color:#e74c3c;'><b>❌ {T['missing']}</b></span>"
            status += f"&nbsp;&nbsp;&nbsp;&nbsp;{T['hw_driver']} <b style='color:#2980b9;'>mesa-va-drivers-freeworld</b> ({rad_status_txt})<br>"

        if hw['has_nvidia'] or hw['has_intel'] or hw.get('has_radeon'):
            status += "<br>"

        if hw['secure_boot']: status += T['hw_sb_active']
        else: status += T['hw_sb_inactive']
        status += "</span>"
        self.lbl_hw_status.setText(status)

        if hw.get('has_luks'):
            self.luks_alert_card.show()
        else:
            self.luks_alert_card.hide()

    def run_autopilot(self):
        if not check_internet():
            QMessageBox.critical(self, T['net_err_title'], T['net_err_desc'])
            return

        mok_password = None
        skip_nvidia = False
        requires_mok_reboot = False

        if self.hw_info.get('has_nvidia') and self.hw_info.get('secure_boot'):
            dialog = MokSetupDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                if dialog.skip_nvidia: skip_nvidia = True
                else:
                    mok_password = dialog.password
                    requires_mok_reboot = True
            else: return

        self.prog_dialog = SmartProgressDialog(T['prog_title'], self)
        self.worker = AutoPilotSingleScriptWorker(self.hw_info, mok_password, skip_nvidia)
        self.worker.log_signal.connect(self.prog_dialog.append_log)
        self.worker.step_signal.connect(self.prog_dialog.set_step)

        self.requires_mok_reboot = requires_mok_reboot
        self.worker.finished_signal.connect(self.on_autopilot_finished)

        self.worker.start()
        self.prog_dialog.exec()

    def on_autopilot_finished(self, success, msg):
        self.prog_dialog.set_finished(success, msg, getattr(self, 'requires_mok_reboot', False))

class GenericPackageManager(QWidget):
    def __init__(self, title_key, get_tasks_func):
        super().__init__()
        self.tasks = get_tasks_func()
        self.rows = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 10)

        header_layout = QHBoxLayout()
        self.title_lbl = QLabel(T[title_key])
        self.title_lbl.setStyleSheet("font-size: 20pt; font-weight: bold;")
        self.btn_refresh = QPushButton("🔄 " + T['refresh'])
        self.btn_refresh.clicked.connect(self.refresh_all_status)
        header_layout.addWidget(self.title_lbl)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_refresh)
        layout.addLayout(header_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        container = QWidget()
        self.list_layout = QVBoxLayout(container)
        self.list_layout.setSpacing(10)
        scroll.setWidget(container)
        layout.addWidget(scroll)

        for name, info in self.tasks.items():
            row_frame = QFrame()
            row_frame.setObjectName("AppRow")
            row_layout = QHBoxLayout(row_frame)
            text_layout = QVBoxLayout()
            lbl_name = QLabel(name)
            lbl_name.setStyleSheet("font-size: 12pt; font-weight: bold;")

            lbl_desc = QLabel(T[info['desc_key']])
            lbl_desc.setStyleSheet("font-size: 10pt; color: gray;")
            lbl_desc.setWordWrap(True)

            text_layout.addWidget(lbl_name)
            text_layout.addWidget(lbl_desc)

            lbl_status = QLabel()
            lbl_status.setMinimumWidth(100)
            lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn_uninst = QPushButton(T['uninstall'])
            btn_uninst.clicked.connect(lambda checked, n=name: self.execute_pkg(n, "remove"))
            btn_inst = QPushButton(T['install'])
            btn_inst.setObjectName("PrimaryButton")
            btn_inst.clicked.connect(lambda checked, n=name: self.execute_pkg(n, "install"))

            row_layout.addLayout(text_layout, stretch=1)
            row_layout.addWidget(lbl_status)
            row_layout.addWidget(btn_inst)
            row_layout.addWidget(btn_uninst)
            self.list_layout.addWidget(row_frame)
            self.rows[name] = {"status": lbl_status, "btn_uninst": btn_uninst, "btn_inst": btn_inst}

        self.list_layout.addStretch()
        self.refresh_all_status()

    def refresh_all_status(self):
        for r in self.rows.values():
            r["btn_inst"].setEnabled(False)
            r["btn_uninst"].setEnabled(False)
        self.worker = FedoraRefreshWorker(self.tasks)
        self.worker.status_signal.connect(self.update_row)
        self.worker.start()

    def update_row(self, name, is_installed):
        if name not in self.rows: return
        row = self.rows[name]
        if is_installed:
            row["status"].setText(f"✅ {T['installed']}")
            row["status"].setStyleSheet("color: #27ae60; font-weight: bold;")
            row["btn_inst"].hide()
            row["btn_uninst"].show()
            row["btn_uninst"].setEnabled(True)
        else:
            row["status"].setText(f"❌ {T['missing']}")
            row["status"].setStyleSheet("color: #e74c3c; font-weight: bold;")
            row["btn_inst"].show()
            row["btn_inst"].setEnabled(True)
            row["btn_uninst"].hide()

    def update_tasks(self, new_tasks):
        self.tasks = new_tasks
        self.refresh_all_status()

    def execute_pkg(self, name, action):
        if action == "install" and not check_internet():
            QMessageBox.critical(self, T['net_err_title'], T['net_err_desc'])
            return

        # Disable all buttons immediately to prevent double-click race conditions
        for r in self.rows.values():
            r["btn_inst"].setEnabled(False)
            r["btn_uninst"].setEnabled(False)

        info = self.tasks[name]
        script = ["#!/bin/bash", "set -e"]
        pkgs = " ".join(info.get("packages", []))

        if action == "install":
            if info["type"] == "rpmfusion":
                ver = subprocess.run(["rpm", "-E", "%fedora"], capture_output=True, text=True).stdout.strip()
                script.append(f"dnf5 install -y https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-{ver}.noarch.rpm https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-{ver}.noarch.rpm || dnf install -y https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-{ver}.noarch.rpm https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-{ver}.noarch.rpm")
            elif info["type"] == "chrome":
                script.append("dnf5 install -y fedora-workstation-repositories || dnf install -y fedora-workstation-repositories\ndnf5 config-manager setopt google-chrome.enabled=1 || dnf config-manager --set-enabled google-chrome || true")
                script.append(f"dnf5 install -y --allowerasing {pkgs} || dnf install -y --allowerasing {pkgs}")
            elif info["type"] == "onlyoffice":
                script.append("dnf5 install -y https://download.onlyoffice.com/repo/centos/main/noarch/onlyoffice-repo.noarch.rpm || dnf install -y https://download.onlyoffice.com/repo/centos/main/noarch/onlyoffice-repo.noarch.rpm")
                script.append(f"dnf5 install -y --allowerasing {pkgs} || dnf install -y --allowerasing {pkgs}")
            elif info["type"] == "radeon":
                ver = subprocess.run(["rpm", "-E", "%fedora"], capture_output=True, text=True).stdout.strip()
                script.append(f"rpm -q rpmfusion-free-release || (dnf5 install -y https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-{ver}.noarch.rpm || dnf install -y https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-{ver}.noarch.rpm)")
                script.append(f"rpm -q rpmfusion-nonfree-release || (dnf5 install -y https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-{ver}.noarch.rpm || dnf install -y https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-{ver}.noarch.rpm)")
                script.append("dnf5 upgrade -y --refresh || dnf upgrade -y --refresh")
                script.append(f"dnf5 install -y --allowerasing {pkgs} || dnf install -y --allowerasing {pkgs}")
            else:
                # Ajout de --allowerasing pour toutes les autres installations standards
                script.append(f"dnf5 install -y --allowerasing {pkgs} || dnf install -y --allowerasing {pkgs}")
        else:
            safe_to_remove = set(info.get("packages", []))

            # Vérifier les autres paquets pour ne pas supprimer de dépendances communes
            for t_name, t_info in self.tasks.items():
                if t_name != name:
                    # Vérifie si cette autre tâche est actuellement installée
                    is_installed = True
                    for p in t_info.get("packages", []):
                        if subprocess.run(["rpm", "-q", p], capture_output=True).returncode != 0:
                            is_installed = False
                            break

                    # Si elle est installée, on retire ses paquets de la liste de suppression
                    if is_installed:
                        safe_to_remove -= set(t_info.get("packages", []))

            pkgs = " ".join(safe_to_remove)
            if pkgs:
                script.append(f"dnf5 remove -y {pkgs} || dnf remove -y {pkgs}")
            else:
                script.append(f"echo '{T['pkg_remove_shared']}'")

        self.term_dialog = TerminalDialog(f"{action} {name}", self)
        self.worker = SimpleScriptWorker(script)
        self.worker.log_signal.connect(self.term_dialog.append_log)
        self.worker.finished_signal.connect(self.on_execute_finished)

        self.worker.start()
        self.term_dialog.exec()

    def on_execute_finished(self, success, msg):
        self.term_dialog.set_finished()
        self.refresh_all_status()

class CryptEnrollApp(QWidget):
    def __init__(self):
        super().__init__()
        self.secure_boot_active = False
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        self.title_lbl = QLabel(T['tpm_title'])
        self.title_lbl.setStyleSheet("font-size: 20pt; font-weight: bold;")
        self.desc_lbl = QLabel(T['tpm_desc'])
        self.desc_lbl.setStyleSheet("font-size: 11pt; color: gray;")
        layout.addWidget(self.title_lbl)
        layout.addWidget(self.desc_lbl)

        self.disks_group = QGroupBox(T['tpm_group_disks'])
        dl = QVBoxLayout(self.disks_group)
        self.disk_tree = QTreeWidget()
        self.disk_tree.setHeaderLabels([T['tpm_col_path'], T['tpm_col_type'], T['tpm_col_mount'], T['tpm_col_label'], T['tpm_col_size']])

        self.disk_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 5):
            self.disk_tree.header().setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        dl.addWidget(self.disk_tree)
        self.luks_items = []
        layout.addWidget(self.disks_group)

        self.options_group = QGroupBox(T['tpm_group_options'])
        ol = QVBoxLayout(self.options_group)
        self.radio_tpm2_simple = QRadioButton(T['tpm_radio_auto'])
        self.radio_tpm2_simple.setChecked(True)
        self.radio_tpm2_pin = QRadioButton(T['tpm_radio_pin'])
        self.check_wipe = QCheckBox(T['tpm_check_wipe'])
        self.check_wipe.setChecked(True)
        self.check_no_pcr = QCheckBox(T['tpm_check_nopcr'])
        ol.addWidget(self.radio_tpm2_simple)
        ol.addWidget(self.radio_tpm2_pin)
        ol.addWidget(self.check_wipe)
        ol.addWidget(self.check_no_pcr)
        layout.addWidget(self.options_group)

        al = QHBoxLayout()
        self.btn_wipe_only = QPushButton(T['tpm_btn_wipe'])
        self.btn_wipe_only.clicked.connect(lambda: self.process_action("wipe"))
        self.btn_enroll = QPushButton(T['tpm_btn_enroll'])
        self.btn_enroll.setObjectName("PrimaryButton")
        self.btn_enroll.clicked.connect(lambda: self.process_action("enroll"))
        al.addWidget(self.btn_wipe_only)
        al.addStretch()
        al.addWidget(self.btn_enroll)
        layout.addLayout(al)

    def update_hardware_info(self, hw):
        self.secure_boot_active = hw.get('secure_boot', False)

    def start_disk_scan(self):
        self.disk_tree.clear()
        self.luks_items.clear()
        self.scan_worker = DiskScanWorker()
        self.scan_worker.result_signal.connect(self.populate_disks)
        self.scan_worker.start()

    def populate_disks(self, roots, children_map):
        for root in roots:
            p_item = QTreeWidgetItem(self.disk_tree)
            p_item.setText(0, root.get('path', ''))

            def build_tree(pw, pkname):
                for child in children_map.get(pkname, []):
                    item = QTreeWidgetItem(pw)
                    if child.get("fstype") == "crypto_LUKS":
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                        item.setCheckState(0, Qt.CheckState.Checked if not self.luks_items else Qt.CheckState.Unchecked)
                        item.setText(0, child.get("path", ""))
                        item.setData(0, Qt.ItemDataRole.UserRole, child.get("path", ""))
                        self.luks_items.append(item)
                    else: item.setText(0, child.get("path", ""))
                    item.setText(1, child.get("fstype", ""))
                    item.setText(2, str(child.get("mountpoints", "")))
                    item.setText(4, child.get("size", ""))
                    build_tree(item, child.get("kname"))
            build_tree(p_item, root.get("kname"))

        self.disk_tree.expandAll()

    def process_action(self, action="enroll"):
        selected = [i.data(0, Qt.ItemDataRole.UserRole) for i in self.luks_items if i.checkState(0) == Qt.CheckState.Checked]
        if not selected: return

        if action == "enroll" and not self.secure_boot_active and not self.check_no_pcr.isChecked():
            QMessageBox.warning(self, T['tpm_err_sb_title'], T['tpm_err_sb_desc'])
            return

        pwd, ok = QInputDialog.getText(self, T['tpm_diag_auth_title'], T['tpm_diag_auth_desc'], QLineEdit.EchoMode.Password)
        if not ok or not pwd: return
        pin = None
        if action == "enroll" and self.radio_tpm2_pin.isChecked():
            pin, ok = QInputDialog.getText(self, T['tpm_diag_pin_title'], T['tpm_diag_pin_desc'], QLineEdit.EchoMode.Password)
            if not ok or not pin: return

        fd_p, p_path = tempfile.mkstemp(text=True)
        with os.fdopen(fd_p, 'w') as f: f.write(pwd)

        script = ["#!/bin/bash", "set -e", f'trap "rm -f {p_path}" EXIT']
        if pin: script.append(f'export NEWPIN={shlex.quote(pin)}')

        for d in selected:
            script.append(f'LUKS_VER=$(cryptsetup luksDump "{d}" | grep -i "Version:" | awk \'{{print $2}}\')')
            script.append('if [ "$LUKS_VER" != "2" ]; then cryptsetup convert "' + d + '" --type luks2 -q --key-file="' + p_path + '"; fi')
            cmd = f"systemd-cryptenroll --unlock-key-file={p_path} "
            if self.check_wipe.isChecked() or action == "wipe": cmd += "--wipe-slot=tpm2 "
            if action == "enroll": cmd += "--tpm2-device=auto " + ("--tpm2-with-pin=yes " if pin else "") + ('--tpm2-pcrs="" ' if self.check_no_pcr.isChecked() else '--tpm2-pcrs="7" ')
            script.append(cmd + f' "{d}"')

        self.term_dialog = TerminalDialog(T['tpm_diag_config_title'], self)
        self.worker = SimpleScriptWorker(script)
        self.worker.log_signal.connect(self.term_dialog.append_log)
        self.worker.finished_signal.connect(self.on_enroll_finished)

        self.worker.start()
        self.term_dialog.exec()

    def on_enroll_finished(self, success, msg):
        self.term_dialog.set_finished()

class SecureBootApp(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        lbl = QLabel(T['sb_title'])
        lbl.setStyleSheet("font-size: 20pt; font-weight: bold;")
        desc = QLabel(T['sb_desc'])
        desc.setStyleSheet("font-size: 11pt; color: gray;")
        layout.addWidget(lbl)
        layout.addWidget(desc)

        self.btn_mok = QPushButton(T['sb_btn_mok'])
        self.btn_mok.setObjectName("PrimaryButton")
        self.btn_mok.clicked.connect(self.run_mok)
        layout.addWidget(self.btn_mok)

        self.btn_akmods = QPushButton(T['sb_btn_akmods'])
        self.btn_akmods.clicked.connect(lambda: self.run_cmd(["#!/bin/bash", "akmods --force"]))
        layout.addWidget(self.btn_akmods)

        self.btn_dracut = QPushButton(T['sb_btn_dracut'])
        self.btn_dracut.clicked.connect(lambda: self.run_cmd(["#!/bin/bash", "dracut -v --force --kver $(uname -r)"]))
        layout.addWidget(self.btn_dracut)

        layout.addStretch()

    def run_mok(self):
        pwd, ok = QInputDialog.getText(self, T['sb_diag_mok_title'], T['sb_diag_mok_desc'], QLineEdit.EchoMode.Password)
        if not ok or not pwd: return
        script = [
            "#!/bin/bash", "set -e",
            "dnf5 install -y akmods mokutil expect openssl || dnf install -y akmods mokutil expect openssl",
            "kmodgenca -a || true",
            f"export MOK_PASS={shlex.quote(pwd)}",
            "expect << 'EOF'",
            "spawn mokutil --import /etc/pki/akmods/certs/public_key.der",
            "expect {",
            "  \"already enrolled\" { exit 0 }",
            "  \"input password:\" {",
            "    send -- \"$env(MOK_PASS)\\r\"",
            "    expect \"input password again:\"",
            "    send -- \"$env(MOK_PASS)\\r\"",
            "    expect eof",
            "  }",
            "}",
            "EOF"
        ]
        self.run_cmd(script)

    def run_cmd(self, script):
        self.term_dialog = TerminalDialog(T['sb_diag_exec_title'], self)
        self.worker = SimpleScriptWorker(script)
        self.worker.log_signal.connect(self.term_dialog.append_log)
        self.worker.finished_signal.connect(self.on_cmd_finished)

        self.worker.start()
        self.term_dialog.exec()

    def on_cmd_finished(self, success, msg):
        self.term_dialog.set_finished()

# ==========================================
# FENÊTRE PRINCIPALE & SIDEBAR
# ==========================================
class ModernSidebar(QListWidget):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setIconSize(QSize(28, 28))
        self.setSpacing(10)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setFixedWidth(260)
        self.setObjectName("ModernSidebar")

class FedoraGreenPilot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1100, 750)
        self.setWindowTitle(T['app_title'])
        self.expert_mode = False

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = ModernSidebar()
        sc = QWidget()
        sc.setFixedWidth(280)
        sc.setObjectName("SidebarContainer")
        sl = QVBoxLayout(sc)
        self.app_title = QLabel("✨ " + T['sidebar_title'])
        self.app_title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        self.app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sl.addWidget(self.app_title)
        sl.addSpacing(20)
        sl.addWidget(self.sidebar)

        self.btn_expert = QPushButton(T['expert_off'])
        self.btn_expert.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_expert.setStyleSheet("background: transparent; border: 1px solid rgba(128,128,128,0.3); border-radius: 8px; padding: 10px; font-weight: bold;")
        self.btn_expert.clicked.connect(self.toggle_expert_mode)
        sl.addWidget(self.btn_expert)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(sc)
        main_layout.addWidget(self.stacked_widget)

        self.home_w = HomeWidget(self)
        self.home_w.request_tab_change.connect(self.sidebar.setCurrentRow)

        self.drivers_w = GenericPackageManager("title_drivers", get_drivers_tasks)
        self.softs_w = GenericPackageManager("title_softs", get_softs_tasks)
        self.tpm_w = CryptEnrollApp()
        self.sb_w = SecureBootApp()

        self.stacked_widget.addWidget(self.home_w)
        self.stacked_widget.addWidget(self.drivers_w)
        self.stacked_widget.addWidget(self.softs_w)
        self.stacked_widget.addWidget(self.tpm_w)
        self.stacked_widget.addWidget(self.sb_w)

        menu_items = [
            ('nav_home', 0),
            ('nav_drivers', 1),
            ('nav_softs', 2),
            ('nav_tpm', 3),
            ('nav_sb', 4)
        ]
        for text_key, idx in menu_items:
            item = QListWidgetItem(T[text_key])
            item.setData(Qt.ItemDataRole.UserRole, idx)
            self.sidebar.addItem(item)

        self.sidebar.currentRowChanged.connect(self.on_nav_changed)

        self.apply_mode_layout()
        self.sidebar.setCurrentRow(0)

        QTimer.singleShot(100, self.start_hardware_scan)

    def start_hardware_scan(self):
        self.scanner = HardwareScanner()
        self.scanner.result_signal.connect(self.on_hardware_scan_finished)
        self.scanner.start()

    def on_hardware_scan_finished(self, hw):
        self.home_w.update_hardware_ui(hw)
        new_drivers_tasks = get_drivers_tasks(hw.get('nvidia_package', 'akmod-nvidia'))
        self.drivers_w.update_tasks(new_drivers_tasks)
        self.tpm_w.update_hardware_info(hw)

    def toggle_expert_mode(self):
        self.expert_mode = not self.expert_mode
        self.btn_expert.setText(T['expert_on'] if self.expert_mode else T['expert_off'])
        if self.expert_mode:
            self.btn_expert.setStyleSheet("background: transparent; border: 1px solid #e67e22; color: #e67e22; border-radius: 8px; padding: 10px; font-weight: bold;")
        else:
            self.btn_expert.setStyleSheet("background: transparent; border: 1px solid rgba(128,128,128,0.3); border-radius: 8px; padding: 10px; font-weight: bold;")

        self.home_w.set_expert_mode(self.expert_mode)
        self.apply_mode_layout()

    def apply_mode_layout(self):
        for i in range(1, 5):
            self.sidebar.setRowHidden(i, not self.expert_mode)
        if not self.expert_mode and self.sidebar.currentRow() != 0:
            self.sidebar.setCurrentRow(0)

    def on_nav_changed(self, row):
        item = self.sidebar.item(row)
        if not item: return
        idx = item.data(Qt.ItemDataRole.UserRole)
        if idx == 3: self.tpm_w.start_disk_scan()
        self.stacked_widget.setCurrentIndex(idx)

    def changeEvent(self, event):
        """Détecte le changement de thème global du système et l'applique à chaud."""
        if event.type() == QEvent.Type.PaletteChange:
            # Garde anti-réentrance : setPalette() re-déclenche PaletteChange en boucle
            if getattr(self, '_applying_theme', False):
                super().changeEvent(event)
                return
            self._applying_theme = True
            try:
                app = QApplication.instance()
                is_dark = detect_dark_mode()
                apply_theme(app, is_dark, hot_reload=True)
                if self.expert_mode:
                    self.home_w.refresh_dashboard()
            finally:
                self._applying_theme = False

        super().changeEvent(event)


# ==========================================
# GESTION INTELLIGENTE DU THÈME ET POINT D'ENTRÉE
# ==========================================

def detect_dark_mode():
    """Détecte automatiquement le thème sombre pour GNOME, KDE, et via XDG Desktop Portal."""

    # 1. Méthode moderne (XDG Desktop Portal) - Idéale pour Wayland / Flatpak / DEs récents
    try:
        res = subprocess.run([
            "dbus-send", "--session", "--print-reply=literal",
            "--dest=org.freedesktop.portal.Desktop",
            "/org/freedesktop/portal/desktop",
            "org.freedesktop.portal.Settings.Read",
            "string:org.freedesktop.appearance",
            "string:color-scheme"
        ], capture_output=True, text=True, timeout=1)
        if "uint32 1" in res.stdout:
            return True
        if "uint32 2" in res.stdout or "uint32 0" in res.stdout:
            return False
    except Exception:
        pass

    # 2. Secours GNOME (gsettings classique)
    try:
        res = subprocess.run(["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"], capture_output=True, text=True, timeout=1)
        if "prefer-dark" in res.stdout:
            return True
    except Exception:
        pass

    # 3. Secours KDE Plasma 5/6
    try:
        for cmd in ["kreadconfig6", "kreadconfig5"]:
            if shutil.which(cmd):
                res = subprocess.run([cmd, "--group", "General", "--key", "ColorScheme"], capture_output=True, text=True, timeout=1)
                if "Dark" in res.stdout or "BreezeDark" in res.stdout:
                    return True
    except Exception:
        pass

    return False

def apply_theme(app, is_dark=None, hot_reload=False):
    # setStyle() au démarrage uniquement : le rappeler à chaud peut crasher
    # car il recrée le moteur de style pendant que des widgets l'utilisent
    if not hot_reload:
        app.setStyle("Fusion")
    if is_dark is None:
        is_dark = detect_dark_mode()

    if is_dark:
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(40, 40, 40))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(53, 132, 228))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(53, 132, 228))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))
        app.setPalette(palette)

        border_color = "rgba(255, 255, 255, 0.15)"
        hover_color = "rgba(255, 255, 255, 0.05)"
        term_bg = "#1e1e1e"
        term_fg = "#f1f1f1"

    else:
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Button, QColor(230, 230, 230))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(53, 132, 228))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(53, 132, 228))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))
        app.setPalette(palette)

        border_color = "rgba(0, 0, 0, 0.15)"
        hover_color = "rgba(0, 0, 0, 0.05)"
        term_bg = "#f5f5f5"
        term_fg = "#2c3e50"

    # Construction dynamique de la feuille de style
    qss = f"""
    QWidget {{ font-family: system-ui, "Segoe UI", sans-serif; font-size: 11pt; }}
    QWidget#SidebarContainer {{ background-color: palette(alternate-base); border-right: 1px solid {border_color}; }}
    QListWidget#ModernSidebar {{ background: transparent; border: none; outline: none; }}
    QListWidget#ModernSidebar::item {{ padding: 12px 15px; border-radius: 10px; margin-bottom: 5px; font-weight: bold; color: palette(text); }}
    QListWidget#ModernSidebar::item:selected {{ background-color: palette(highlight); color: white; }}
    QListWidget#ModernSidebar::item:hover:!selected {{ background-color: {hover_color}; }}
    QLabel#HomeOSCard {{ background-color: palette(base); border: 1px solid {border_color}; border-radius: 12px; padding: 15px; color: palette(text); }}
    QGroupBox {{ background-color: palette(base); border: 1px solid {border_color}; border-radius: 12px; margin-top: 20px; padding-top: 15px; font-weight: bold; color: palette(text); }}
    QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; left: 15px; font-weight: bold; color: palette(highlight); }}
    QFrame#AppRow {{ background-color: palette(base); border: 1px solid {border_color}; border-radius: 12px; padding: 10px; }}
    QPushButton {{ background-color: palette(button); color: palette(button-text); border: 1px solid {border_color}; border-radius: 8px; padding: 8px 15px; font-weight: bold; }}
    QPushButton:hover {{ background-color: {hover_color}; border: 1px solid palette(highlight); }}
    QPushButton#PrimaryButton {{ background-color: #2980b9; color: white; border: none; border-radius: 12px; }}
    QPushButton#PrimaryButton:hover {{ background-color: #3498db; }}
    QTextEdit#TerminalView {{ background-color: {term_bg}; color: {term_fg}; font-family: 'Consolas', monospace; border-radius: 8px; padding: 10px; font-size: 10pt; border: 1px solid {border_color}; }}
    QTreeWidget {{ background-color: palette(base); border-radius: 10px; border: 1px solid {border_color}; outline: none; color: palette(text); }}
    QHeaderView::section {{ background-color: transparent; color: palette(text); padding: 8px 5px; border: none; border-bottom: 2px solid {border_color}; font-weight: bold; font-size: 11pt; }}
    QTreeWidget::item {{ padding: 8px 5px; border-bottom: 1px solid {border_color}; }}
    QTreeWidget::item:selected {{ background-color: palette(highlight); color: white; border-radius: 6px; }}
    """
    app.setStyleSheet(qss)
    # Re-polish différé via QTimer pour éviter tout appel récursif depuis un event handler.
    # Utiliser un délai 0 ms : exécuté dès que la boucle d'événements est libre.
    def do_polish():
        for widget in app.allWidgets():
            try:
                widget.style().unpolish(widget)
                widget.style().polish(widget)
                widget.update()
            except RuntimeError:
                # Widget peut avoir été détruit entre temps
                pass
    QTimer.singleShot(0, do_polish)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Application de la configuration de thème automatique
    apply_theme(app)

    window = FedoraGreenPilot()
    window.show()
    sys.exit(app.exec())
