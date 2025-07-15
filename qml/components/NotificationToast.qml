import QtQuick
import QtQuick.Controls
import Qt5Compat.GraphicalEffects

Rectangle {
    id: toast
    
    property string title: ""
    property string message: ""
    property int duration: 3000
    property bool isDarkMode: true
    
    width: Math.max(300, contentColumn.implicitWidth + 40)
    height: contentColumn.implicitHeight + 30
    color: isDarkMode ? "#2d2d2d" : "#ffffff"
    border.color: isDarkMode ? "#404040" : "#e0e0e0"
    border.width: 1
    radius: 8
    
    // 阴影效果
    layer.enabled: true
    layer.effect: DropShadow {
        horizontalOffset: 0
        verticalOffset: 2
        radius: 8
        samples: 16
        color: "#40000000"
    }
    
    // 初始状态：不可见
    opacity: 0
    scale: 0.8
    
    // 动画
    Behavior on opacity {
        NumberAnimation { duration: 200 }
    }
    
    Behavior on scale {
        NumberAnimation { duration: 200 }
    }
    
    Column {
        id: contentColumn
        anchors.centerIn: parent
        spacing: 8
        width: parent.width - 40
        
        Text {
            text: toast.title
            font.pixelSize: 16
            font.bold: true
            color: isDarkMode ? "#ffffff" : "#000000"
            wrapMode: Text.WordWrap
            width: parent.width
            visible: text.length > 0
        }
        
        Text {
            text: toast.message
            font.pixelSize: 14
            color: isDarkMode ? "#cccccc" : "#666666"
            wrapMode: Text.WordWrap
            width: parent.width
            visible: text.length > 0
        }
    }
    
    // 关闭按钮
    Button {
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 8
        width: 20
        height: 20
        flat: true
        text: "×"
        font.pixelSize: 16
        
        onClicked: toast.hide()
    }
    
    // 自动隐藏定时器
    Timer {
        id: hideTimer
        interval: toast.duration
        onTriggered: toast.hide()
    }
    
    // 鼠标悬停暂停自动隐藏
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        
        onEntered: hideTimer.stop()
        onExited: {
            if (toast.opacity > 0) {
                hideTimer.restart()
            }
        }
    }
    
    function show() {
        opacity = 1
        scale = 1
        hideTimer.start()
    }
    
    function hide() {
        opacity = 0
        scale = 0.8
        hideTimer.stop()
        
        // 延迟销毁
        Qt.callLater(function() {
            if (parent) {
                parent.removeChild(toast)
            }
            toast.destroy()
        })
    }
    
    Component.onCompleted: {
        // 延迟显示，确保组件完全加载
        Qt.callLater(show)
    }
}
