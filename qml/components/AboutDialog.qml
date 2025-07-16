import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

Dialog {
    id: aboutDialog

    property bool isDarkMode: true
    property int logoClickCount: 0
    property bool showingDeviceInfo: false

    title: qsTr("关于 TimeNest")
    modal: true
    width: 600
    height: showingDeviceInfo ? 800 : 600

    // 重置点击计数的定时器
    Timer {
        id: resetClickTimer
        interval: 3000  // 3秒后重置
        onTriggered: logoClickCount = 0
    }
    
    background: Rectangle {
        color: isDarkMode ? "#2d2d2d" : "#ffffff"
        border.color: isDarkMode ? "#404040" : "#e0e0e0"
        border.width: 1
        radius: 8
    }
    
    ScrollView {
        anchors.fill: parent
        anchors.margins: 20
        
        Column {
            width: aboutDialog.width - 40
            spacing: 15
            
            // 应用图标和名称
            Column {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 8
                
                Image {
                    id: appLogo
                    width: 80
                    height: 80
                    source: "../../resources/icons/app_icon.png"
                    anchors.horizontalCenter: parent.horizontalCenter
                    fillMode: Image.PreserveAspectFit

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            logoClickCount++
                            resetClickTimer.restart()  // 重启定时器

                            // 显示点击反馈
                            appLogo.opacity = 0.7
                            logoFeedbackTimer.restart()

                            if (logoClickCount >= 8) {
                                showingDeviceInfo = !showingDeviceInfo
                                logoClickCount = 0
                                if (showingDeviceInfo) {
                                    // 获取设备信息
                                    if (typeof timeNestBridge !== 'undefined') {
                                        timeNestBridge.showNotification("设备信息", "已显示设备信息")
                                    }
                                } else {
                                    if (typeof timeNestBridge !== 'undefined') {
                                        timeNestBridge.showNotification("设备信息", "已隐藏设备信息")
                                    }
                                }
                            }
                        }

                        // 点击反馈定时器
                        Timer {
                            id: logoFeedbackTimer
                            interval: 100
                            onTriggered: appLogo.opacity = 1.0
                        }
                    }
                }
                
                Text {
                    text: typeof timeNestBridge !== 'undefined' ? timeNestBridge.appName : "TimeNest"
                    font.pixelSize: 24
                    font.bold: true
                    color: isDarkMode ? "#ffffff" : "#000000"
                    anchors.horizontalCenter: parent.horizontalCenter
                }
                
                Text {
                    text: qsTr("版本 ") + (typeof timeNestBridge !== 'undefined' ? timeNestBridge.appVersion : "1.1.3 Preview")
                    font.pixelSize: 16
                    color: isDarkMode ? "#cccccc" : "#666666"
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }
            
            Rectangle {
                width: parent.width
                height: 100
                radius: 8
                color: isDarkMode ? "#2d2d2d" : "#ffffff"
                border.color: isDarkMode ? "#404040" : "#e0e0e0"
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: typeof timeNestBridge !== 'undefined' ? timeNestBridge.appDescription : qsTr("智能时间管理助手")
                    font.pixelSize: 14
                    color: isDarkMode ? "#ffffff" : "#000000"
                    wrapMode: Text.WordWrap
                    width: parent.width - 20
                    horizontalAlignment: Text.AlignHCenter
                }
            }
            
            Rectangle {
                width: parent.width
                radius: 8
                color: isDarkMode ? "#2d2d2d" : "#ffffff"
                border.color: isDarkMode ? "#404040" : "#e0e0e0"
                border.width: 1

                Column {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12

                    Text {
                        text: qsTr("版本信息")
                        font.pixelSize: 16
                        font.bold: true
                        color: isDarkMode ? "#ffffff" : "#000000"
                    }
                
                    GridLayout {
                        width: parent.width
                        columns: 2
                        columnSpacing: 16
                        rowSpacing: 8

                        Text {
                            text: qsTr("应用版本:")
                            font.pixelSize: 14
                            color: isDarkMode ? "#cccccc" : "#666666"
                        }

                        Text {
                            text: typeof timeNestBridge !== 'undefined' ? timeNestBridge.appVersion : "2.1.0 Preview"
                            font.pixelSize: 14
                            color: isDarkMode ? "#ffffff" : "#000000"
                        }

                        Text {
                            text: qsTr("构建日期:")
                            font.pixelSize: 14
                            color: isDarkMode ? "#cccccc" : "#666666"
                        }

                        Text {
                            text: "2025-07-15"
                            font.pixelSize: 14
                            color: isDarkMode ? "#ffffff" : "#000000"
                        }

                        Text {
                            text: qsTr("UI框架:")
                            font.pixelSize: 14
                            color: isDarkMode ? "#cccccc" : "#666666"
                        }

                        Text {
                            text: "RinUI + Qt Quick"
                            font.pixelSize: 14
                            color: isDarkMode ? "#ffffff" : "#000000"
                        }
                    }
                }
            }
            
            Rectangle {
                width: parent.width
                radius: 8

                Column {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12

                    Text {
                        text: qsTr("作者信息")
                        font.pixelSize: 16
                        font.bold: true
                        color: isDarkMode ? "#ffffff" : "#000000"
                    }
                
                Column {
                    anchors.fill: parent
                    spacing: 8
                    
                    Text {
                        text: qsTr("主要开发者: ziyi127")
                        font.pixelSize: 14
                        color: isDarkMode ? "#ffffff" : "#000000"
                    }
                    
                    Text {
                        text: qsTr("贡献者: 暂无")
                        font.pixelSize: 14
                        color: isDarkMode ? "#ffffff" : "#000000"
                    }
                    
                    Text {
                        text: qsTr("项目地址: https://github.com/ziyi127/TimeNest")
                        font.pixelSize: 14
                        color: "#2196f3"
                        
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                Qt.openUrlExternally("https://github.com/ziyi127/TimeNest")
                            }
                        }
                    }
                }
            }
            
            // 许可证信息
            GroupBox {
                title: qsTr("许可证")
                width: parent.width
                
                background: Rectangle {
                    color: isDarkMode ? "#353535" : "#f9f9f9"
                    border.color: isDarkMode ? "#404040" : "#e0e0e0"
                    border.width: 1
                    radius: 6
                }
                
                label: Text {
                    text: parent.title
                    font.bold: true
                    color: isDarkMode ? "#ffffff" : "#000000"
                }
                
                Column {
                    anchors.fill: parent
                    spacing: 8
                    
                    Text {
                        text: qsTr("本软件基于 MIT 许可证发布")
                        font.pixelSize: 14
                        color: isDarkMode ? "#ffffff" : "#000000"
                    }
                    
                    Text {
                        text: qsTr("© 2024-2025 ziyi127. All rights reserved.")
                        font.pixelSize: 14
                        color: isDarkMode ? "#cccccc" : "#666666"
                    }
                }
            }
            
            // 致谢
            GroupBox {
                title: qsTr("特别感谢")
                width: parent.width
                
                background: Rectangle {
                    color: isDarkMode ? "#353535" : "#f9f9f9"
                    border.color: isDarkMode ? "#404040" : "#e0e0e0"
                    border.width: 1
                    radius: 6
                }
                
                label: Text {
                    text: parent.title
                    font.bold: true
                    color: isDarkMode ? "#ffffff" : "#000000"
                }
                
                Column {
                    anchors.fill: parent
                    spacing: 8
                    
                    Text {
                        text: "• " + qsTr("感谢 RinUI 团队提供的优秀 UI 框架")
                        font.pixelSize: 14
                        color: isDarkMode ? "#ffffff" : "#000000"
                    }
                    
                    Text {
                        text: "• " + qsTr("感谢 Qt 团队提供的强大开发平台")
                        font.pixelSize: 14
                        color: isDarkMode ? "#ffffff" : "#000000"
                    }
                    
                    Text {
                        text: "• " + qsTr("感谢所有用户的支持和反馈")
                        font.pixelSize: 14
                        color: isDarkMode ? "#ffffff" : "#000000"
                    }
                }
            }

            // 设备信息（隐藏功能）
            Rectangle {
                width: parent.width
                height: deviceInfoColumn.height + 40
                visible: showingDeviceInfo
                color: isDarkMode ? "#353535" : "#f9f9f9"
                border.color: isDarkMode ? "#404040" : "#e0e0e0"
                border.width: 1
                radius: 6

                ScrollView {
                    anchors.fill: parent
                    anchors.margins: 20

                    Column {
                        id: deviceInfoColumn
                        width: parent.width
                        spacing: 20

                        Text {
                            text: qsTr("🖥️ 详细设备信息")
                            font.pixelSize: 18
                            font.bold: true
                            color: isDarkMode ? "#ffffff" : "#000000"
                            anchors.horizontalCenter: parent.horizontalCenter
                        }

                        // 系统信息
                        Frame {
                            width: parent.width

                            Column {
                                width: parent.width
                                spacing: 8

                                Text {
                                    text: qsTr("💻 系统信息")
                                    font.pixelSize: 16
                                    font.bold: true
                                    color: isDarkMode ? "#ffffff" : "#000000"
                                }

                                Text {
                                    width: parent.width
                                    font.pixelSize: 12
                                    color: isDarkMode ? "#cccccc" : "#666666"
                                    wrapMode: Text.WordWrap
                                    text: {
                                        if (typeof timeNestBridge !== 'undefined') {
                                            try {
                                                var sysInfo = timeNestBridge.getSystemInfo()
                                                return qsTr("操作系统: %1\n架构: %2\n主机名: %3\n用户: %4")
                                                    .arg(sysInfo.os || "Unknown")
                                                    .arg(sysInfo.architecture || "Unknown")
                                                    .arg(sysInfo.hostname || "Unknown")
                                                    .arg(sysInfo.user || "Unknown")
                                            } catch (e) {
                                                console.log("获取系统信息失败:", e)
                                                return "获取系统信息失败"
                                            }
                                        }
                                        return "系统信息不可用"
                                    }
                                }
                            }
                        }

                        // 硬件信息
                        Frame {
                            width: parent.width

                            Column {
                                width: parent.width
                                spacing: 8

                                Text {
                                    text: qsTr("🔧 硬件信息")
                                    font.pixelSize: 16
                                    font.bold: true
                                    color: isDarkMode ? "#ffffff" : "#000000"
                                }

                                Text {
                                    width: parent.width
                                    font.pixelSize: 12
                                    color: isDarkMode ? "#cccccc" : "#666666"
                                    wrapMode: Text.WordWrap
                                    text: {
                                        if (typeof timeNestBridge !== 'undefined') {
                                            try {
                                                var sysInfo = timeNestBridge.getSystemInfo()
                                                return qsTr("CPU: %1\n频率: %2\nCPU使用率: %3\n内存: %4\n交换分区: %5\n磁盘: %6")
                                                    .arg(sysInfo.cpu || "Unknown")
                                                    .arg(sysInfo.cpu_frequency || "Unknown")
                                                    .arg(sysInfo.cpu_usage || "Unknown")
                                                    .arg(sysInfo.memory || "Unknown")
                                                    .arg(sysInfo.swap || "Unknown")
                                                    .arg(sysInfo.disk || "Unknown")
                                            } catch (e) {
                                                console.log("获取硬件信息失败:", e)
                                                return "获取硬件信息失败"
                                            }
                                        }
                                        return "硬件信息不可用"
                                    }
                                }
                            }
                        }

                        // 网络信息
                        Frame {
                            width: parent.width

                            Column {
                                width: parent.width
                                spacing: 8

                                Text {
                                    text: qsTr("🌐 网络信息")
                                    font.pixelSize: 16
                                    font.bold: true
                                    color: isDarkMode ? "#ffffff" : "#000000"
                                }

                                Text {
                                    width: parent.width
                                    font.pixelSize: 12
                                    color: isDarkMode ? "#cccccc" : "#666666"
                                    wrapMode: Text.WordWrap
                                    text: {
                                        if (typeof timeNestBridge !== 'undefined') {
                                            try {
                                                var sysInfo = timeNestBridge.getSystemInfo()
                                                return qsTr("主机名: %1\n本地IP: %2\nMAC地址: %3")
                                                    .arg(sysInfo.hostname || "Unknown")
                                                    .arg(sysInfo.local_ip || "Unknown")
                                                    .arg(sysInfo.mac_address || "Unknown")
                                            } catch (e) {
                                                console.log("获取网络信息失败:", e)
                                                return "获取网络信息失败"
                                            }
                                        }
                                        return "网络信息不可用"
                                    }
                                }
                            }
                        }

                        // 软件环境
                        Frame {
                            width: parent.width

                            Column {
                                width: parent.width
                                spacing: 8

                                Text {
                                    text: qsTr("⚙️ 软件环境")
                                    font.pixelSize: 16
                                    font.bold: true
                                    color: isDarkMode ? "#ffffff" : "#000000"
                                }

                                Text {
                                    width: parent.width
                                    font.pixelSize: 12
                                    color: isDarkMode ? "#cccccc" : "#666666"
                                    wrapMode: Text.WordWrap
                                    text: {
                                        if (typeof timeNestBridge !== 'undefined') {
                                            try {
                                                var sysInfo = timeNestBridge.getSystemInfo()
                                                return qsTr("Python版本: %1\nQt版本: %2\nPySide6: %3\nRinUI: %4\n系统运行时间: %5\n时区: %6")
                                                    .arg(sysInfo.python || "Unknown")
                                                    .arg(sysInfo.qt || "Unknown")
                                                    .arg(sysInfo.pyside6 || "Unknown")
                                                    .arg(sysInfo.rinui || "Unknown")
                                                    .arg(sysInfo.uptime || "Unknown")
                                                    .arg(sysInfo.timezone || "Unknown")
                                            } catch (e) {
                                                console.log("获取软件环境信息失败:", e)
                                                return "获取软件环境信息失败"
                                            }
                                        }
                                        return "软件环境信息不可用"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    footer: Row {
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 10

        Button {
            text: qsTr("确定")
            onClicked: aboutDialog.close()
        }
    }
}
