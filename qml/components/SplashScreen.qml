import QtQuick
import QtQuick.Controls
import QtQuick.Window
import QtQuick.Layouts
import RinUI

Window {
    id: splashWindow
    
    width: 600
    height: 400
    flags: Qt.SplashScreen | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
    color: "transparent"
    
    property string currentStatus: typeof loadingMessage !== 'undefined' ? loadingMessage : "正在启动..."
    property real progress: typeof loadingProgress !== 'undefined' ? loadingProgress : 0.0
    property bool isDarkMode: true
    
    // 背景
    Frame {
        anchors.fill: parent
        radius: 12
        color: isDarkMode ? "#1e1e1e" : "#ffffff"
        borderColor: isDarkMode ? "#404040" : "#e0e0e0"
        borderWidth: 1
        
        Column {
            anchors.centerIn: parent
            spacing: 30
            width: parent.width - 80
            
            // Logo和标题
            Column {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 20
                
                // Logo
                Image {
                    id: logoImage
                    source: "../../resources/icons/app_icon.png"
                    width: 120
                    height: 120
                    anchors.horizontalCenter: parent.horizontalCenter
                    fillMode: Image.PreserveAspectFit
                    
                    // 旋转动画
                    RotationAnimation {
                        target: logoImage
                        from: 0
                        to: 360
                        duration: 3000
                        loops: Animation.Infinite
                        running: true
                    }
                }
                
                // 应用名称
                Text {
                    text: "TimeNest"
                    font.pixelSize: 32
                    font.bold: true
                    color: isDarkMode ? "#ffffff" : "#000000"
                    anchors.horizontalCenter: parent.horizontalCenter
                }
                
                // 版本信息
                Text {
                    text: "2.0.0 Preview"
                    font.pixelSize: 16
                    color: isDarkMode ? "#cccccc" : "#666666"
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }
            
            // 加载状态
            Column {
                width: parent.width
                spacing: 15
                
                // 状态文本
                Text {
                    id: statusText
                    text: currentStatus
                    font.pixelSize: 14
                    color: isDarkMode ? "#ffffff" : "#000000"
                    anchors.horizontalCenter: parent.horizontalCenter
                    
                    // 文本淡入淡出动画
                    Behavior on text {
                        SequentialAnimation {
                            NumberAnimation {
                                target: statusText
                                property: "opacity"
                                to: 0.5
                                duration: 150
                            }
                            NumberAnimation {
                                target: statusText
                                property: "opacity"
                                to: 1.0
                                duration: 150
                            }
                        }
                    }
                }
                
                // 进度条容器
                Rectangle {
                    width: parent.width
                    height: 6
                    color: isDarkMode ? "#404040" : "#e0e0e0"
                    radius: 3
                    anchors.horizontalCenter: parent.horizontalCenter
                    
                    // 进度条
                    Rectangle {
                        id: progressBar
                        width: parent.width * progress
                        height: parent.height
                        color: "#2196f3"
                        radius: 3
                        
                        Behavior on width {
                            NumberAnimation {
                                duration: 300
                                easing.type: Easing.OutCubic
                            }
                        }
                        
                        // 进度条光效
                        Rectangle {
                            anchors.fill: parent
                            gradient: Gradient {
                                GradientStop { position: 0.0; color: "#4fc3f7" }
                                GradientStop { position: 0.5; color: "#2196f3" }
                                GradientStop { position: 1.0; color: "#1976d2" }
                            }
                            radius: 3
                        }
                    }
                }
                
                // 进度百分比
                Text {
                    text: Math.round(progress * 100) + "%"
                    font.pixelSize: 12
                    color: isDarkMode ? "#cccccc" : "#666666"
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }
            
            // 底部信息
            Column {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 8
                
                Text {
                    text: "基于 RinUI 框架构建"
                    font.pixelSize: 12
                    color: isDarkMode ? "#888888" : "#999999"
                    anchors.horizontalCenter: parent.horizontalCenter
                }
                
                Text {
                    text: "© 2025 TimeNest Team"
                    font.pixelSize: 10
                    color: isDarkMode ? "#666666" : "#aaaaaa"
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }
        }
        
        // 背景粒子效果
        Repeater {
            model: 20
            
            Rectangle {
                width: Math.random() * 4 + 2
                height: width
                radius: width / 2
                color: isDarkMode ? "#404040" : "#e0e0e0"
                opacity: Math.random() * 0.5 + 0.1
                
                x: Math.random() * parent.width
                y: Math.random() * parent.height
                
                // 浮动动画
                SequentialAnimation {
                    loops: Animation.Infinite
                    running: true
                    
                    ParallelAnimation {
                        NumberAnimation {
                            target: parent
                            property: "y"
                            to: parent.y - 20
                            duration: 2000 + Math.random() * 1000
                            easing.type: Easing.InOutSine
                        }
                        NumberAnimation {
                            target: parent
                            property: "opacity"
                            to: (parent.opacity + 0.3) > 1 ? 1 : parent.opacity + 0.3
                            duration: 1000
                            easing.type: Easing.InOutSine
                        }
                    }
                    
                    ParallelAnimation {
                        NumberAnimation {
                            target: parent
                            property: "y"
                            to: parent.y + 20
                            duration: 2000 + Math.random() * 1000
                            easing.type: Easing.InOutSine
                        }
                        NumberAnimation {
                            target: parent
                            property: "opacity"
                            to: parent.opacity - 0.3 < 0.1 ? 0.1 : parent.opacity - 0.3
                            duration: 1000
                            easing.type: Easing.InOutSine
                        }
                    }
                }
            }
        }
    }
    
    // 监听进度变化，自动关闭
    onProgressChanged: {
        if (progress >= 1.0) {
            // 启动完成，准备关闭
            closeTimer.start()
        }
    }

    Timer {
        id: closeTimer
        interval: 500
        onTriggered: {
            closeAnimation.start()
        }
    }

    // 关闭动画
    SequentialAnimation {
        id: closeAnimation

        NumberAnimation {
            target: splashWindow
            property: "opacity"
            to: 0
            duration: 500
            easing.type: Easing.OutCubic
        }

        ScriptAction {
            script: splashWindow.close()
        }
    }
}
