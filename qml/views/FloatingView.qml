import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

ScrollView {
    id: floatingView

    property bool isDarkMode: false

    // 强制置顶检测定时器
    Timer {
        id: topCheckTimer
        interval: 1000  // 每秒检测一次
        repeat: true
        onTriggered: {
            if (forceTopCheckBox.checked && typeof timeNestBridge !== 'undefined') {
                // 检测悬浮窗是否还在最顶层，如果不是则重新置顶
                if (!timeNestBridge.isFloatingWindowOnTop()) {
                    timeNestBridge.forceFloatingToTop()
                }
            }
        }
    }
    property bool floatingWindowVisible: false
    
    Column {
        width: floatingView.width
        spacing: 24
        
        Text {
            text: qsTr("悬浮窗管理")
            font.pixelSize: 32
            font.bold: true
            color: isDarkMode ? "#ffffff" : "#000000"
        }
        
        RinCard {
            width: parent.width
            radius: 8

            Column {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 16

                Text {
                    text: qsTr("悬浮窗控制")
                    font.pixelSize: 18
                    font.bold: true
                    color: isDarkMode ? "#ffffff" : "#000000"
                }

                Row {
                    spacing: 16

                    RinButton {
                        id: toggleFloatingButton
                        text: floatingWindowVisible ? qsTr("关闭悬浮窗") : qsTr("启动悬浮窗")
                        icon: floatingWindowVisible ? "visibility_off" : "picture_in_picture"
                        accentColor: "#2196f3"
                        onClicked: {
                            toggleFloatingWindow()
                        }
                    }

                    RinButton {
                        text: qsTr("重置位置")
                        icon: "center_focus_strong"
                        onClicked: {
                            resetFloatingPosition()
                        }
                    }

                    RinCheckBox {
                        id: forceTopCheckBox
                        text: qsTr("强制置顶")
                        checked: false
                        onToggled: {
                            if (checked) {
                                forceFloatingToTop()
                                topCheckTimer.start()
                            } else {
                                topCheckTimer.stop()
                            }
                        }
                    }
                }

                Text {
                    text: qsTr("悬浮窗状态: ") + (typeof timeNestBridge !== 'undefined' && timeNestBridge.isFloatingWindowVisible() ? qsTr("显示") : qsTr("隐藏"))
                    font.pixelSize: 14
                    color: isDarkMode ? "#cccccc" : "#666666"
                }
            }
        }

        // 悬浮窗设置面板
        Text {
            text: qsTr("悬浮窗设置")
            font.pixelSize: 18
            font.bold: true
            color: isDarkMode ? "#ffffff" : "#000000"
        }

        // 显示设置
        Rectangle {
            width: parent.width
            height: 160
            color: isDarkMode ? "#353535" : "#f5f5f5"
            border.color: isDarkMode ? "#404040" : "#e0e0e0"
            border.width: 1
            radius: 6

            Column {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 12

                Text {
                    text: qsTr("显示设置")
                    font.pixelSize: 16
                    font.bold: true
                    color: isDarkMode ? "#ffffff" : "#000000"
                }

                CheckBox {
                    id: autoHideCheckBox
                    text: qsTr("自动隐藏 (鼠标离开时自动隐藏悬浮窗)")
                    checked: true
                    onCheckedChanged: {
                        if (typeof timeNestBridge !== 'undefined') {
                            timeNestBridge.setFloatingAutoHide(checked)
                        }
                    }
                }

                CheckBox {
                    id: alwaysOnTopCheckBox
                    text: qsTr("始终置顶 (悬浮窗始终显示在最前面)")
                    checked: true
                    onCheckedChanged: {
                        if (typeof timeNestBridge !== 'undefined') {
                            timeNestBridge.setFloatingAlwaysOnTop(checked)
                        }
                    }
                }

                CheckBox {
                    id: transparentCheckBox
                    text: qsTr("透明背景 (使用透明背景效果)")
                    checked: false
                    onCheckedChanged: {
                        if (typeof timeNestBridge !== 'undefined') {
                            timeNestBridge.setFloatingTransparent(checked)
                        }
                    }
                }
            }
        }

        // 位置设置
        Rectangle {
            width: parent.width
            height: 140
            color: isDarkMode ? "#353535" : "#f5f5f5"
            border.color: isDarkMode ? "#404040" : "#e0e0e0"
            border.width: 1
            radius: 6

            Column {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 12

                Text {
                    text: qsTr("位置设置")
                    font.pixelSize: 16
                    font.bold: true
                    color: isDarkMode ? "#ffffff" : "#000000"
                }

                Row {
                    spacing: 10

                    Text {
                        text: qsTr("X:")
                        font.pixelSize: 14
                        color: isDarkMode ? "#ffffff" : "#000000"
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    SpinBox {
                        id: xPositionSpinBox
                        from: 0
                        to: 9999
                        value: 100
                        width: 80
                        onValueChanged: {
                            if (typeof timeNestBridge !== 'undefined') {
                                timeNestBridge.setFloatingPosition(value, yPositionSpinBox.value)
                            }
                        }
                    }

                    Text {
                        text: qsTr("Y:")
                        font.pixelSize: 14
                        color: isDarkMode ? "#ffffff" : "#000000"
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    SpinBox {
                        id: yPositionSpinBox
                        from: 0
                        to: 9999
                        value: 100
                        width: 80
                        onValueChanged: {
                            if (typeof timeNestBridge !== 'undefined') {
                                timeNestBridge.setFloatingPosition(xPositionSpinBox.value, value)
                            }
                        }
                    }
                }

                Flow {
                    width: parent.width
                    spacing: 8

                    Button {
                        text: qsTr("左上")
                        onClicked: setFloatingPosition("topLeft")
                    }

                    Button {
                        text: qsTr("右上")
                        onClicked: setFloatingPosition("topRight")
                    }

                    Button {
                        text: qsTr("左下")
                        onClicked: setFloatingPosition("bottomLeft")
                    }

                    Button {
                        text: qsTr("右下")
                        onClicked: setFloatingPosition("bottomRight")
                    }

                    Button {
                        text: qsTr("居中")
                        onClicked: setFloatingPosition("center")
                    }
                }
            }
        }

        // 内容设置
        Rectangle {
            width: parent.width
            height: 140
            color: isDarkMode ? "#353535" : "#f5f5f5"
            border.color: isDarkMode ? "#404040" : "#e0e0e0"
            border.width: 1
            radius: 6

            Column {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 8

                Text {
                    text: qsTr("显示内容")
                    font.pixelSize: 16
                    font.bold: true
                    color: isDarkMode ? "#ffffff" : "#000000"
                }

                Row {
                    spacing: 20

                    CheckBox {
                        id: showTimeCheckBox
                        text: qsTr("时间")
                        checked: true
                        onCheckedChanged: {
                            if (typeof timeNestBridge !== 'undefined') {
                                timeNestBridge.setFloatingShowTime(checked)
                            }
                        }
                    }

                    CheckBox {
                        id: showCourseCheckBox
                        text: qsTr("课程")
                        checked: true
                        onCheckedChanged: {
                            if (typeof timeNestBridge !== 'undefined') {
                                timeNestBridge.setFloatingShowCourse(checked)
                            }
                        }
                    }
                }

                Row {
                    spacing: 20

                    CheckBox {
                        id: showWeatherCheckBox
                        text: qsTr("天气")
                        checked: true
                        onCheckedChanged: {
                            if (typeof timeNestBridge !== 'undefined') {
                                timeNestBridge.setFloatingShowWeather(checked)
                            }
                        }
                    }

                    CheckBox {
                        id: showTasksCheckBox
                        text: qsTr("任务")
                        checked: false
                        onCheckedChanged: {
                            if (typeof timeNestBridge !== 'undefined') {
                                timeNestBridge.setFloatingShowTasks(checked)
                            }
                        }
                    }
                }
            }
        }

        // 样式设置
        Rectangle {
            width: parent.width
            height: 140
            color: isDarkMode ? "#353535" : "#f5f5f5"
            border.color: isDarkMode ? "#404040" : "#e0e0e0"
            border.width: 1
            radius: 6

            Column {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 12

                Text {
                    text: qsTr("样式设置")
                    font.pixelSize: 16
                    font.bold: true
                    color: isDarkMode ? "#ffffff" : "#000000"
                }

                Row {
                    spacing: 10
                    width: parent.width

                    Text {
                        text: qsTr("透明度:")
                        font.pixelSize: 14
                        color: isDarkMode ? "#ffffff" : "#000000"
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Slider {
                        id: opacitySlider
                        from: 0.3
                        to: 1.0
                        value: 0.9
                        stepSize: 0.1
                        width: 120
                        onValueChanged: {
                            if (typeof timeNestBridge !== 'undefined') {
                                timeNestBridge.setFloatingOpacity(value)
                            }
                        }
                    }

                    Text {
                        text: Math.round(opacitySlider.value * 100) + "%"
                        font.pixelSize: 14
                        color: isDarkMode ? "#ffffff" : "#000000"
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }

                Row {
                    spacing: 10

                    Text {
                        text: qsTr("字体:")
                        font.pixelSize: 14
                        color: isDarkMode ? "#ffffff" : "#000000"
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    SpinBox {
                        id: fontSizeSpinBox
                        from: 8
                        to: 24
                        value: 12
                        width: 80
                        onValueChanged: {
                            if (typeof timeNestBridge !== 'undefined') {
                                timeNestBridge.setFloatingFontSize(value)
                            }
                        }
                    }

                    Text {
                        text: qsTr("主题:")
                        font.pixelSize: 14
                        color: isDarkMode ? "#ffffff" : "#000000"
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    ComboBox {
                        id: themeComboBox
                        model: [qsTr("自动"), qsTr("浅色"), qsTr("深色")]
                        currentIndex: 0
                        onCurrentIndexChanged: {
                            if (typeof timeNestBridge !== 'undefined') {
                                var themes = ["auto", "light", "dark"]
                                timeNestBridge.setFloatingTheme(themes[currentIndex])
                            }
                        }
                    }
                }
            }
        }
    }

    // JavaScript 函数
    function toggleFloatingWindow() {
        if (typeof timeNestBridge !== 'undefined') {
            var success = timeNestBridge.toggleFloatingWindow()
            if (success) {
                floatingWindowVisible = !floatingWindowVisible
                updateFloatingStatus()
            }
        }
    }

    function openFloatingSettings() {
        // 设置面板已经在页面中显示，无需额外操作
        if (typeof timeNestBridge !== 'undefined') {
            timeNestBridge.showNotification("悬浮窗设置", "请在下方设置面板中调整悬浮窗参数")
        }
    }

    function resetFloatingPosition() {
        if (typeof timeNestBridge !== 'undefined') {
            var success = timeNestBridge.resetFloatingPosition()
            if (success) {
                // 更新UI中的位置值
                xPositionSpinBox.value = 100
                yPositionSpinBox.value = 100
                timeNestBridge.showNotification("重置位置", "悬浮窗位置已重置到默认位置")
            } else {
                timeNestBridge.showNotification("重置失败", "无法重置悬浮窗位置")
            }
        }
    }

    function setFloatingPosition(position) {
        if (typeof timeNestBridge !== 'undefined') {
            var success = timeNestBridge.setFloatingPositionPreset(position)
            if (success) {
                // 获取新的位置并更新UI
                var pos = timeNestBridge.getFloatingPosition()
                if (pos) {
                    xPositionSpinBox.value = pos.x
                    yPositionSpinBox.value = pos.y
                }
                timeNestBridge.showNotification("位置设置", "悬浮窗位置已设置为" + getPositionName(position))
            }
        }
    }

    function getPositionName(position) {
        switch(position) {
            case "topLeft": return "左上角"
            case "topRight": return "右上角"
            case "bottomLeft": return "左下角"
            case "bottomRight": return "右下角"
            case "center": return "居中"
            default: return "自定义位置"
        }
    }

    function loadFloatingSettings() {
        if (typeof timeNestBridge !== 'undefined') {
            // 加载悬浮窗设置
            var settings = timeNestBridge.getFloatingSettings()
            if (settings) {
                // 更新UI控件的值
                autoHideCheckBox.checked = settings.autoHide || true
                alwaysOnTopCheckBox.checked = settings.alwaysOnTop || true
                transparentCheckBox.checked = settings.transparent || false
                showTimeCheckBox.checked = settings.showTime || true
                showCourseCheckBox.checked = settings.showCourse || true
                showWeatherCheckBox.checked = settings.showWeather || true
                showTasksCheckBox.checked = settings.showTasks || false
                opacitySlider.value = settings.opacity || 0.9
                fontSizeSpinBox.value = settings.fontSize || 12

                var themeIndex = 0
                if (settings.theme === "light") themeIndex = 1
                else if (settings.theme === "dark") themeIndex = 2
                themeComboBox.currentIndex = themeIndex

                // 加载位置信息
                var pos = timeNestBridge.getFloatingPosition()
                if (pos) {
                    xPositionSpinBox.value = pos.x
                    yPositionSpinBox.value = pos.y
                }
            }
        }
    }

    function updateFloatingStatus() {
        if (typeof timeNestBridge !== 'undefined') {
            floatingWindowVisible = timeNestBridge.isFloatingWindowVisible()
        }
    }

    function showFloatingWindow() {
        if (typeof timeNestBridge !== 'undefined') {
            var success = timeNestBridge.showFloatingWindow()
            if (success) {
                floatingWindowVisible = true
            }
        }
    }

    function hideFloatingWindow() {
        if (typeof timeNestBridge !== 'undefined') {
            var success = timeNestBridge.hideFloatingWindow()
            if (success) {
                floatingWindowVisible = false
            }
        }
    }

    function forceFloatingToTop() {
        if (typeof timeNestBridge !== 'undefined') {
            var success = timeNestBridge.forceFloatingWindowToTop()
            if (success) {
                console.log("悬浮窗已强制置顶")
            } else {
                console.log("强制置顶失败")
            }
        }
    }

    // 组件加载完成时更新状态
    Component.onCompleted: {
        updateFloatingStatus()
        loadFloatingSettings()
    }

    // 监听悬浮窗状态变化
    Connections {
        target: typeof timeNestBridge !== 'undefined' ? timeNestBridge : null
        function onFloatingWindowToggled(visible) {
            floatingWindowVisible = visible
        }
    }
}
