#!/bin/bash
set -e

# ==========================================
# CONFIGURATION
# ==========================================
SCRIPT_NAME="FedoraGreenPilot.py"
APP_NAME="FedoraGreenPilot"
OUTPUT_APPIMAGE="${APP_NAME}-x86_64.AppImage"

echo "==========================================="
echo "  Compilation de $APP_NAME en AppImage"
echo "==========================================="

if [ ! -f "$SCRIPT_NAME" ]; then
    echo "❌ Erreur : Le fichier $SCRIPT_NAME est introuvable dans ce dossier."
    exit 1
fi

echo "0. Installation des dépendances natives Fedora (mot de passe sudo requis)..."
# On installe PyQt6 via DNF pour avoir la version 100% Fedora (qui gère les emojis et Wayland)
sudo dnf install -y python3-pyqt6 python3-pip patchelf desktop-file-utils wget file gcc

echo "1. Création d'un environnement virtuel lié au système..."
# L'option --system-site-packages permet à cet environnement de voir le PyQt6 installé par DNF !
python3 -m venv --system-site-packages venv_build
source venv_build/bin/activate

echo "2. Installation de PyInstaller..."
pip install --upgrade pip
pip install pyinstaller

echo "3. Compilation du script Python..."
# L'argument --add-data "*.png:." dit à PyInstaller d'embarquer tes 4 images MOK dans l'exécutable !
pyinstaller --noconfirm --onedir --windowed --add-data "*.png:." --name="$APP_NAME" "$SCRIPT_NAME"

echo "4. Création de la structure AppDir..."
rm -rf AppDir
mkdir -p AppDir/usr/bin
mkdir -p AppDir/usr/share/applications
mkdir -p AppDir/usr/share/icons/hicolor/scalable/apps

cp -r dist/${APP_NAME} AppDir/usr/bin/

echo "5. FIX EMOJIS : Nettoyage des bibliothèques de polices embarquées..."
# On force l'AppImage à utiliser le moteur de polices de l'ordinateur hôte
find AppDir/usr/bin/${APP_NAME} -type f \( -name "libfontconfig.so*" -o -name "libfreetype.so*" -o -name "libharfbuzz.so*" \) -delete

echo "6. Création des fichiers d'intégration de bureau..."

# Création du lanceur AppRun
cat > AppDir/AppRun << 'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin/FedoraGreenPilot:${PATH}"
exec "${HERE}/usr/bin/FedoraGreenPilot/FedoraGreenPilot" "$@"
EOF
chmod +x AppDir/AppRun

# Création d'une icône basique SVG
cat > AppDir/${APP_NAME}.svg << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" rx="20" fill="#294172"/>
  <text x="50%" y="55%" font-size="45" font-family="sans-serif" font-weight="bold" text-anchor="middle" fill="white">FT</text>
</svg>
EOF

cp AppDir/${APP_NAME}.svg AppDir/usr/share/icons/hicolor/scalable/apps/
ln -sf ${APP_NAME}.svg AppDir/.DirIcon

# Création du fichier .desktop
cat > AppDir/${APP_NAME}.desktop << EOF
[Desktop Entry]
Type=Application
Name=Fedora Assistant Pro
Comment=Outil de gestion et post-installation pour Fedora
Exec=FedoraGreenPilot
Icon=$APP_NAME
Categories=System;Utility;
Terminal=false
EOF

cp AppDir/${APP_NAME}.desktop AppDir/usr/share/applications/

echo "7. Téléchargement de AppImageTool..."
APPIMAGETOOL="appimagetool-x86_64.AppImage"
if [ ! -f "$APPIMAGETOOL" ]; then
    wget -q --show-progress "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x "$APPIMAGETOOL"
fi

echo "8. Génération de l'AppImage..."
ARCH=x86_64 ./$APPIMAGETOOL --appimage-extract-and-run AppDir "$OUTPUT_APPIMAGE"

echo "9. Nettoyage de l'environnement..."
deactivate
rm -rf build dist AppDir *.spec venv_build

echo "==========================================="
echo "✅ SUCCÈS ! L'application a été compilée."
echo "📦 Fichier généré : $OUTPUT_APPIMAGE"
echo "==========================================="
