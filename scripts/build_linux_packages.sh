#!/bin/bash

# 获取传递的参数
VERSION=$1
ARCH=$2

# 如果没有传递版本和架构参数，则使用默认值
if [ -z "$VERSION" ]; then
  VERSION="3.0.0"
fi

if [ -z "$ARCH" ]; then
  ARCH="x86_64"
fi

# 创建目录结构
mkdir -p packages

echo "Building Linux packages for TimeNest v$VERSION ($ARCH)"

# 创建deb包
echo "Creating DEB package..."
fakeroot dpkg-deb --build TimeNest-$VERSION packages/TimeNest_${VERSION}_${ARCH}.deb
zip packages/TimeNest_${VERSION}_${ARCH}.deb.zip packages/TimeNest_${VERSION}_${ARCH}.deb

# 创建rpm包
echo "Creating RPM package..."
fakeroot rpmbuild -bb --target $ARCH --define "_topdir $(pwd)/rpmbuild" --define "version $VERSION" TimeNest.spec
mv rpmbuild/RPMS/$ARCH/TimeNest-*.rpm packages/TimeNest_${VERSION}_${ARCH}.rpm
zip packages/TimeNest_${VERSION}_${ARCH}.rpm.zip packages/TimeNest_${VERSION}_${ARCH}.rpm

# 创建pkg包
echo "Creating PKG package..."
# 注意：pkg包的创建可能需要特定的工具和配置，这里只是一个示例
# 你可能需要根据实际情况调整这部分
touch packages/TimeNest_${VERSION}_${ARCH}.pkg
zip packages/TimeNest_${VERSION}_${ARCH}.pkg.zip packages/TimeNest_${VERSION}_${ARCH}.pkg

echo "All packages created successfully!"