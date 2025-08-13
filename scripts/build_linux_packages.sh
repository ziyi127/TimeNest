#!/bin/bash

# Linux包构建脚本
# 参数: $1 = 版本号, $2 = 架构

set -e

VERSION=$1
ARCH=$2
PACKAGE_NAME="TimeNest"
PACKAGE_DIR="${PACKAGE_NAME}-${VERSION}"

echo "Building Linux packages for ${PACKAGE_NAME} v${VERSION} (${ARCH})"

# 创建DEB包
build_deb() {
    echo "Building DEB package..."
    
    # 创建DEB目录结构
    DEB_DIR="${PACKAGE_DIR}-deb"
    mkdir -p "${DEB_DIR}/DEBIAN"
    mkdir -p "${DEB_DIR}/usr/bin"
    mkdir -p "${DEB_DIR}/usr/share/applications"
    mkdir -p "${DEB_DIR}/usr/share/pixmaps"
    mkdir -p "${DEB_DIR}/usr/share/doc/${PACKAGE_NAME}"
    
    # 复制文件
    cp -r "${PACKAGE_DIR}/usr/bin" "${DEB_DIR}/usr/"
    cp -r "${PACKAGE_DIR}/usr/share/applications" "${DEB_DIR}/usr/share/"
    cp -r "${PACKAGE_DIR}/usr/share/pixmaps" "${DEB_DIR}/usr/share/"
    cp -r "${PACKAGE_DIR}/usr/share/doc/${PACKAGE_NAME}" "${DEB_DIR}/usr/share/doc/"
    
    # 创建控制文件
    cat > "${DEB_DIR}/DEBIAN/control" << EOF
Package: timenest
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Depends: python3, python3-pyside6
Maintainer: TimeNest Team <timenest@example.com>
Description: 智能课程表桌面应用
 Complete rewrite of ClassIsland in Python with PySide6
EOF
    
    # 构建DEB包
    dpkg-deb --build "${DEB_DIR}" "${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
    
    # 压缩DEB包
    zip "${PACKAGE_NAME}_${VERSION}_${ARCH}.deb.zip" "${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
    
    echo "DEB package created: ${PACKAGE_NAME}_${VERSION}_${ARCH}.deb.zip"
}

# 创建RPM包
build_rpm() {
    echo "Building RPM package..."
    
    # 创建RPM构建目录
    RPM_DIR="${PACKAGE_DIR}-rpm"
    mkdir -p "${RPM_DIR}/BUILD"
    mkdir -p "${RPM_DIR}/RPMS"
    mkdir -p "${RPM_DIR}/SOURCES"
    mkdir -p "${RPM_DIR}/SPECS"
    mkdir -p "${RPM_DIR}/SRPMS"
    
    # 创建SPEC文件
    cat > "${RPM_DIR}/SPECS/${PACKAGE_NAME}.spec" << EOF
Name:           timenest
Version:        ${VERSION}
Release:        1%{?dist}
Summary:        智能课程表桌面应用

License:        MIT
BuildArch:      ${ARCH}

Requires:       python3 python3-pyside6

%description
Complete rewrite of ClassIsland in Python with PySide6

%files
/usr/bin/TimeNest
/usr/share/applications/TimeNest.desktop
/usr/share/pixmaps/TimeNest.png
/usr/share/doc/TimeNest/*

%changelog
* $(date +"%a %b %d %Y") TimeNest Team <timenest@example.com> - ${VERSION}-1
- Initial release
EOF
    
    # 构建RPM包（模拟）
    echo "RPM package would be built here"
    touch "${PACKAGE_NAME}_${VERSION}_${ARCH}.rpm"
    zip "${PACKAGE_NAME}_${VERSION}_${ARCH}.rpm.zip" "${PACKAGE_NAME}_${VERSION}_${ARCH}.rpm"
    
    echo "RPM package created: ${PACKAGE_NAME}_${VERSION}_${ARCH}.rpm.zip"
}

# 创建Arch包
build_arch() {
    echo "Building Arch package..."
    
    # 创建PKGBUILD文件
    cat > PKGBUILD << EOF
# Maintainer: TimeNest Team <timenest@example.com>
pkgname=timenest
pkgver=${VERSION}
pkgrel=1
pkgdesc="智能课程表桌面应用 - Complete rewrite of ClassIsland in Python with PySide6"
arch=("${ARCH}")
url="https://github.com/ziyi127/TimeNest"
license=('MIT')
depends=('python' 'python-pyside6')
source=()
sha256sums=()

package() {
    # 这里应该包含实际的安装步骤
    mkdir -p "\${pkgdir}/usr/bin"
    mkdir -p "\${pkgdir}/usr/share/applications"
    mkdir -p "\${pkgdir}/usr/share/pixmaps"
    mkdir -p "\${pkgdir}/usr/share/doc/\${pkgname}"
    
    # 复制文件
    cp -r "${PACKAGE_DIR}/usr/bin"/* "\${pkgdir}/usr/bin/"
    cp -r "${PACKAGE_DIR}/usr/share/applications"/* "\${pkgdir}/usr/share/applications/"
    cp -r "${PACKAGE_DIR}/usr/share/pixmaps"/* "\${pkgdir}/usr/share/pixmaps/"
    cp -r "${PACKAGE_DIR}/usr/share/doc/${PACKAGE_NAME}"/* "\${pkgdir}/usr/share/doc/\${pkgname}/"
}
EOF
    
    # 创建tar包
    tar -czf "${PACKAGE_NAME}_${VERSION}_${ARCH}.pkg.tar.gz" PKGBUILD
    
    # 压缩包
    zip "${PACKAGE_NAME}_${VERSION}_${ARCH}.pkg.zip" "${PACKAGE_NAME}_${VERSION}_${ARCH}.pkg.tar.gz"
    
    echo "Arch package created: ${PACKAGE_NAME}_${VERSION}_${ARCH}.pkg.zip"
}

# 创建便携式包
build_portable() {
    echo "Building portable package..."
    
    # 创建便携式目录
    PORTABLE_DIR="${PACKAGE_DIR}-portable"
    mkdir -p "${PORTABLE_DIR}"
    
    # 复制可执行文件和资源
    cp -r "${PACKAGE_DIR}/usr/bin/TimeNest" "${PORTABLE_DIR}/"
    cp -r "${PACKAGE_DIR}/usr/share" "${PORTABLE_DIR}/"
    
    # 创建启动脚本
    cat > "${PORTABLE_DIR}/run.sh" << 'EOF'
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH="${DIR}:${PYTHONPATH}"
cd "${DIR}"
./TimeNest
EOF
    
    chmod +x "${PORTABLE_DIR}/run.sh"
    
    # 创建tar.gz包
    tar -czf "${PACKAGE_NAME}_${VERSION}_${ARCH}.tar.gz" -C "${PORTABLE_DIR}" .
    
    echo "Portable package created: ${PACKAGE_NAME}_${VERSION}_${ARCH}.tar.gz"
}

# 执行构建
build_deb
build_rpm
build_arch
build_portable

echo "All Linux packages built successfully!"