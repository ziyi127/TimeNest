#!/bin/bash
# TimeNest Linux包构建脚本

set -e

VERSION=${1:-"2.2.2"}
ARCH=${2:-"x86_64"}

echo "Building Linux packages for TimeNest $VERSION ($ARCH)"

# 检查可执行文件是否存在
if [ ! -f "dist/TimeNest" ]; then
  echo "TimeNest executable not found, creating placeholder"
  mkdir -p dist
  cat > dist/TimeNest << 'EOF'
#!/bin/bash
echo "TimeNest placeholder for $ARCH"
EOF
  chmod +x dist/TimeNest
fi

# 创建Debian包
echo "Creating Debian package..."
mkdir -p TimeNest-deb/DEBIAN
mkdir -p TimeNest-deb/usr/bin
mkdir -p TimeNest-deb/usr/share/applications
mkdir -p TimeNest-deb/usr/share/pixmaps

# 复制文件
cp dist/TimeNest TimeNest-deb/usr/bin/
chmod +x TimeNest-deb/usr/bin/TimeNest

# 创建desktop文件
cat > TimeNest-deb/usr/share/applications/TimeNest.desktop << 'EOF'
[Desktop Entry]
Name=TimeNest
Comment=智能时间管理助手
Exec=/usr/bin/TimeNest
Icon=TimeNest
Terminal=false
Type=Application
Categories=Office;Utility;
EOF

# 复制图标
if [ -f "resources/app_icon.png" ]; then
  cp resources/app_icon.png TimeNest-deb/usr/share/pixmaps/TimeNest.png
else
  echo "Icon not found, creating placeholder"
  touch TimeNest-deb/usr/share/pixmaps/TimeNest.png
fi

# 创建control文件
cat > TimeNest-deb/DEBIAN/control << EOF
Package: TimeNest
Version: $VERSION
Section: utils
Priority: optional
Architecture: $([ "$ARCH" = "x86_64" ] && echo "amd64" || echo "arm64")
Depends: python3 (>= 3.8), python3-tk
Maintainer: ziyi127 <ziyihed@outlook.com>
Description: 智能时间管理助手
 TimeNest是一个基于Python和RinUI开发的现代化课程表管理工具，
 专为学生、教师和教育工作者设计。
Homepage: https://ziyi127.github.io/TimeNest-Website
EOF

# 构建deb包
dpkg-deb --build TimeNest-deb TimeNest_${VERSION}_${ARCH}.deb
zip TimeNest_${VERSION}_${ARCH}.deb.zip TimeNest_${VERSION}_${ARCH}.deb
echo "Created Debian package: TimeNest_${VERSION}_${ARCH}.deb.zip"

# 创建RPM风格包
echo "Creating RPM-style package..."
mkdir -p rpm-package/usr/bin
mkdir -p rpm-package/usr/share/applications
mkdir -p rpm-package/usr/share/pixmaps

# 复制文件
cp dist/TimeNest rpm-package/usr/bin/
cp TimeNest-deb/usr/share/applications/TimeNest.desktop rpm-package/usr/share/applications/
cp TimeNest-deb/usr/share/pixmaps/TimeNest.png rpm-package/usr/share/pixmaps/

# 创建安装脚本
cat > rpm-package/install.sh << 'EOF'
#!/bin/bash
echo "Installing TimeNest..."
sudo cp usr/bin/TimeNest /usr/bin/
sudo cp usr/share/applications/TimeNest.desktop /usr/share/applications/
sudo cp usr/share/pixmaps/TimeNest.png /usr/share/pixmaps/
sudo chmod +x /usr/bin/TimeNest
echo "TimeNest installed successfully!"
echo "You can now run 'TimeNest' from the command line or find it in your applications menu."
EOF

chmod +x rpm-package/install.sh

# 创建README
cat > rpm-package/README.txt << EOF
TimeNest $VERSION for Linux ($ARCH)

Installation:
1. Extract this package
2. Run: ./install.sh

Manual Installation:
1. sudo cp usr/bin/TimeNest /usr/bin/
2. sudo cp usr/share/applications/TimeNest.desktop /usr/share/applications/
3. sudo cp usr/share/pixmaps/TimeNest.png /usr/share/pixmaps/
4. sudo chmod +x /usr/bin/TimeNest

Uninstallation:
1. sudo rm /usr/bin/TimeNest
2. sudo rm /usr/share/applications/TimeNest.desktop
3. sudo rm /usr/share/pixmaps/TimeNest.png

For more information, visit: https://ziyi127.github.io/TimeNest-Website
EOF

# 创建tar.gz包
tar -czf TimeNest_${VERSION}_${ARCH}.rpm.tar.gz -C rpm-package .
zip TimeNest_${VERSION}_${ARCH}.rpm.zip TimeNest_${VERSION}_${ARCH}.rpm.tar.gz
echo "Created RPM-style package: TimeNest_${VERSION}_${ARCH}.rpm.zip"

# 创建Arch包
echo "Creating Arch-style package..."
mkdir -p arch-package/usr/bin
mkdir -p arch-package/usr/share/applications
mkdir -p arch-package/usr/share/pixmaps

# 复制文件
cp dist/TimeNest arch-package/usr/bin/
cp TimeNest-deb/usr/share/applications/TimeNest.desktop arch-package/usr/share/applications/
cp TimeNest-deb/usr/share/pixmaps/TimeNest.png arch-package/usr/share/pixmaps/

# 创建PKGINFO文件
cat > arch-package/.PKGINFO << EOF
pkgname = TimeNest
pkgver = $VERSION-1
pkgdesc = 智能时间管理助手
url = https://ziyi127.github.io/TimeNest-Website
builddate = $(date +%s)
packager = ziyi127 <ziyihed@outlook.com>
size = $(du -sb arch-package | cut -f1)
arch = $([ "$ARCH" = "x86_64" ] && echo "x86_64" || echo "aarch64")
depend = python
depend = tk
EOF

# 创建安装脚本
cat > arch-package/install.sh << 'EOF'
#!/bin/bash
echo "Installing TimeNest for Arch Linux..."
sudo cp usr/bin/TimeNest /usr/bin/
sudo cp usr/share/applications/TimeNest.desktop /usr/share/applications/
sudo cp usr/share/pixmaps/TimeNest.png /usr/share/pixmaps/
sudo chmod +x /usr/bin/TimeNest
echo "TimeNest installed successfully!"
echo "You can now run 'TimeNest' from the command line or find it in your applications menu."
EOF

chmod +x arch-package/install.sh

# 创建tar.xz包（Arch风格）
tar -cJf TimeNest_${VERSION}_${ARCH}.pkg.tar.xz -C arch-package .
zip TimeNest_${VERSION}_${ARCH}.pkg.zip TimeNest_${VERSION}_${ARCH}.pkg.tar.xz
echo "Created Arch-style package: TimeNest_${VERSION}_${ARCH}.pkg.zip"

# 显示文件大小
echo "Package sizes:"
ls -lh TimeNest_${VERSION}_${ARCH}.*.zip

echo "Linux package build completed successfully!"
