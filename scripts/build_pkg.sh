#!/bin/bash
# Shela Package Builder
# Usage: ./scripts/build_pkg.sh

VERSION="1.3.0"
PKG_DIR="dist/staging"

echo "[Build] Starting package build v$VERSION..."

# Ensure we are in root
if [ ! -d "desktop" ]; then
    echo "Error: Run from project root"
    exit 1
fi

# 1. Build Flutter App
cd desktop
flutter build linux
cd ..

# 2. Prepare Staging
mkdir -p $PKG_DIR/DEBIAN
mkdir -p $PKG_DIR/usr/bin
mkdir -p $PKG_DIR/usr/lib/shela
mkdir -p $PKG_DIR/usr/share/applications
mkdir -p $PKG_DIR/usr/share/icons/hicolor/512x512/apps

# 3. Copy Flutter Release
cp -r desktop/build/linux/x64/release/bundle/* $PKG_DIR/usr/lib/shela/

# 4. Copy Core Logic
mkdir -p $PKG_DIR/usr/lib/shela/lib
cp core/duo.py $PKG_DIR/usr/lib/shela/lib/
cp core/trie.py $PKG_DIR/usr/lib/shela/lib/

# 5. Create Control File
cat << EOF > $PKG_DIR/DEBIAN/control
Package: shela-ide
Version: $VERSION
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Noam <noam@coherences.io>
Depends: libgtk-3-0, liblzma5, python3, python3-pip, curl
Description: Shela IDE - An AI-integrated, autonomous terminal and workspace.
 An IDE designed for continuous autonomous execution using the WTLTTILTRLTBR kata.
 Includes multi-agent support (Mozart, Q, EXE, Loki, Betzalel) and deep cloud integrations.
EOF

# 6. Create Wrapper
cat << EOF > $PKG_DIR/usr/bin/shela
#!/bin/bash
# Shela IDE Wrapper
/usr/lib/shela/shela "\$@"
EOF
chmod +x $PKG_DIR/usr/bin/shela

# 7. Assets
cp desktop/assets/shela_icon.png $PKG_DIR/usr/share/icons/hicolor/512x512/apps/shela.png

# 8. Desktop Entry
cat << EOF > $PKG_DIR/usr/share/applications/shela.desktop
[Desktop Entry]
Name=Shela IDE
Comment=AI-integrated, autonomous terminal and workspace
Exec=shela
Icon=shela
Terminal=false
Type=Application
Categories=Development;IDE;
Keywords=AI;Terminal;Autonomous;
EOF

# 9. Build Deb
dpkg-deb --build $PKG_DIR dist/shela_${VERSION}_amd64.deb

echo "[Build] Package ready at dist/shela_${VERSION}_amd64.deb"
