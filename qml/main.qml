import QtQuick
import QtQuick.Controls
import QtQuick.Window
import QtQuick.Layouts
import QtQuick.Dialogs
import RinUI

Window {
    id: mainWindow
    width: 1200
    height: 800
    visible: true
    title: qsTr("TimeNest - 智能时间管理助手")

    property bool isDarkMode: false
    property string currentView: "dashboard"
    property bool showingAboutDialog: false
    property bool showingNewCourseDialog: false
    property bool showingNewTaskDialog: false

    Rectangle {
        anchors.fill: parent
        color: isDarkMode ? "#1e1e1e" : "#f5f5f5"

        Rectangle {
            id: sidebar
            width: 280
            height: parent.height
            color: isDarkMode ? "#2d2d2d" : "#ffffff"
            border.color: isDarkMode ? "#404040" : "#e0e0e0"
            border.width: 1

            Column {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 16

                Text {
                    text: qsTr("TimeNest")
                    font.pixelSize: 24
                    font.bold: true
                    color: isDarkMode ? "#ffffff" : "#000000"
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                Rectangle {
                    width: parent.width
                    height: 1
                    color: isDarkMode ? "#404040" : "#e0e0e0"
                    radius: 0.5
                }

                Text {
                    text: qsTr("核心功能")
                    font.pixelSize: 14
                    font.bold: true
                    color: isDarkMode ? "#cccccc" : "#666666"
                    leftPadding: 8
                }

                ListView {
                    width: parent.width
                    height: 240
                    model: ListModel {
                        ListElement {
                            itemName: qsTr("仪表板")
                            iconEmoji: "📊"
                            viewName: "dashboard"
                            description: qsTr("概览和统计")
                        }
                        ListElement {
                            itemName: qsTr("课程表")
                            iconEmoji: "📅"
                            viewName: "schedule"
                            description: qsTr("课程安排管理")
                        }
                        ListElement {
                            itemName: qsTr("任务管理")
                            iconEmoji: "✅"
                            viewName: "tasks"
                            description: qsTr("任务和提醒")
                        }
                        ListElement {
                            itemName: qsTr("悬浮窗")
                            iconEmoji: "🪟"
                            viewName: "floating"
                            description: qsTr("桌面悬浮显示")
                        }
                        ListElement {
                            itemName: qsTr("插件管理")
                            iconEmoji: "🧩"
                            viewName: "plugins"
                            description: qsTr("扩展功能")
                        }
                        ListElement {
                            itemName: qsTr("设置")
                            iconEmoji: "⚙️"
                            viewName: "settings"
                            description: qsTr("应用配置")
                        }
                    }

                    delegate: Item {
                        width: ListView.view.width
                        height: 48

                        property bool isSelected: currentView === model.viewName
                        property bool isHovered: mouseArea.containsMouse

                        Rectangle {
                            anchors.fill: parent
                            anchors.margins: 2
                            color: {
                                if (isSelected) return isDarkMode ? "#3d5afe" : "#2196f3"
                                if (isHovered) return isDarkMode ? "#404040" : "#f0f0f0"
                                return "transparent"
                            }
                            radius: 8

                            // 选中状态的左侧指示条
                            Rectangle {
                                width: 4
                                height: parent.height - 8
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                anchors.verticalCenter: parent.verticalCenter
                                color: isSelected ? "#ffffff" : "transparent"
                                radius: 2
                                visible: isSelected
                            }

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 12

                                Text {
                                    text: model.iconEmoji
                                    font.pixelSize: 20
                                    Layout.alignment: Qt.AlignVCenter
                                }

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 2

                                    Text {
                                        text: model.itemName
                                        font.pixelSize: 14
                                        font.bold: isSelected
                                        color: {
                                            if (isSelected) return "#ffffff"
                                            return isDarkMode ? "#ffffff" : "#000000"
                                        }
                                        Layout.fillWidth: true
                                    }

                                    Text {
                                        text: model.description
                                        font.pixelSize: 11
                                        color: {
                                            if (isSelected) return "#e3f2fd"
                                            return isDarkMode ? "#cccccc" : "#666666"
                                        }
                                        Layout.fillWidth: true
                                        visible: isSelected || isHovered
                                    }
                                }
                            }

                            MouseArea {
                                id: mouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                onClicked: currentView = model.viewName
                            }
                        }
                    }
                }

                Rectangle {
                    width: parent.width
                    height: 1
                    color: isDarkMode ? "#404040" : "#e0e0e0"
                    radius: 0.5
                }

                Text {
                    text: qsTr("快捷操作")
                    font.pixelSize: 14
                    font.bold: true
                    color: isDarkMode ? "#cccccc" : "#666666"
                    leftPadding: 8
                }

                ColumnLayout {
                    width: parent.width
                    spacing: 8

                    // 新建操作
                    Rectangle {
                        Layout.fillWidth: true
                        height: 80
                        color: isDarkMode ? "#333333" : "#f8f9fa"
                        radius: 8
                        border.color: isDarkMode ? "#404040" : "#e0e0e0"
                        border.width: 1

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 8

                            Text {
                                text: qsTr("创建新内容")
                                font.pixelSize: 12
                                font.bold: true
                                color: isDarkMode ? "#ffffff" : "#000000"
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8

                                Button {
                                    text: "📚 课程"
                                    Layout.fillWidth: true
                                    flat: true
                                    font.pixelSize: 11
                                    onClicked: {
                                        if (typeof timeNestBridge !== 'undefined') {
                                            timeNestBridge.showNewCourseDialog()
                                        }
                                    }
                                }

                                Button {
                                    text: "✅ 任务"
                                    Layout.fillWidth: true
                                    flat: true
                                    font.pixelSize: 11
                                    onClicked: {
                                        if (typeof timeNestBridge !== 'undefined') {
                                            timeNestBridge.showNewTaskDialog()
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // 悬浮窗控制
                    Rectangle {
                        Layout.fillWidth: true
                        height: 60
                        color: isDarkMode ? "#333333" : "#f8f9fa"
                        radius: 8
                        border.color: isDarkMode ? "#404040" : "#e0e0e0"
                        border.width: 1

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 12

                            Text {
                                text: "🪟"
                                font.pixelSize: 20
                            }

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2

                                Text {
                                    text: qsTr("悬浮窗")
                                    font.pixelSize: 12
                                    font.bold: true
                                    color: isDarkMode ? "#ffffff" : "#000000"
                                }

                                Text {
                                    text: qsTr("桌面时间显示")
                                    font.pixelSize: 10
                                    color: isDarkMode ? "#cccccc" : "#666666"
                                }
                            }

                            Switch {
                                checked: typeof timeNestBridge !== 'undefined' ? timeNestBridge.isFloatingWindowVisible() : false
                                onToggled: {
                                    if (typeof timeNestBridge !== 'undefined') {
                                        // 修复逻辑：根据checked状态直接显示或隐藏悬浮窗
                                        if (checked) {
                                            timeNestBridge.showFloatingWindow()
                                        } else {
                                            timeNestBridge.hideFloatingWindow()
                                        }
                                    }
                                }

                                // 定时更新状态
                                Timer {
                                    interval: 1000
                                    running: true
                                    repeat: true
                                    onTriggered: {
                                        if (typeof timeNestBridge !== 'undefined') {
                                            parent.checked = timeNestBridge.isFloatingWindowVisible()
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                Rectangle {
                    width: parent.width
                    height: 1
                    color: isDarkMode ? "#404040" : "#e0e0e0"
                    radius: 0.5
                }

                Text {
                    text: qsTr("系统控制")
                    font.pixelSize: 14
                    font.bold: true
                    color: isDarkMode ? "#cccccc" : "#666666"
                    leftPadding: 8
                }

                ColumnLayout {
                    width: parent.width
                    spacing: 8

                    // 主题切换
                    Rectangle {
                        Layout.fillWidth: true
                        height: 50
                        color: isDarkMode ? "#333333" : "#f8f9fa"
                        radius: 8
                        border.color: isDarkMode ? "#404040" : "#e0e0e0"
                        border.width: 1

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 12

                            Text {
                                text: isDarkMode ? "🌙" : "☀️"
                                font.pixelSize: 18
                            }

                            Text {
                                text: isDarkMode ? qsTr("深色模式") : qsTr("浅色模式")
                                font.pixelSize: 12
                                color: isDarkMode ? "#ffffff" : "#000000"
                                Layout.fillWidth: true
                            }

                            Switch {
                                checked: isDarkMode
                                onToggled: isDarkMode = !isDarkMode
                            }
                        }
                    }

                    // 应用信息和控制
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        Button {
                            text: "ℹ️ 关于"
                            Layout.fillWidth: true
                            flat: true
                            font.pixelSize: 11
                            onClicked: {
                                if (typeof timeNestBridge !== 'undefined') {
                                    timeNestBridge.showAboutDialog()
                                }
                            }
                        }

                        Button {
                            text: "🚪 退出"
                            Layout.fillWidth: true
                            flat: true
                            font.pixelSize: 11
                            palette.button: "#d32f2f"
                            palette.buttonText: "#ffffff"
                            onClicked: {
                                if (typeof timeNestBridge !== 'undefined') {
                                    timeNestBridge.exitApplication()
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // 主内容区域
        Rectangle {
            anchors.left: sidebar.right
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            color: "transparent"
            
            // 内容加载器
            Loader {
                id: contentLoader
                anchors.fill: parent
                anchors.margins: 16
                
                source: {
                    switch(currentView) {
                        case "dashboard": return "views/DashboardView.qml"
                        case "schedule": return "views/ScheduleView.qml"
                        case "tasks": return "views/TasksView.qml"
                        case "floating": return "views/FloatingView.qml"
                        case "plugins": return "views/PluginsView.qml"
                        case "settings": return "views/SettingsView.qml"
                        default: return "views/DashboardView.qml"
                    }
                }
                
                onLoaded: {
                    if (item) {
                        item.isDarkMode = Qt.binding(function() { return mainWindow.isDarkMode })
                    }
                }
            }
        }
    }
    
    // 状态栏
    Rectangle {
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: 30
        color: isDarkMode ? "#2d2d2d" : "#f0f0f0"
        border.color: isDarkMode ? "#404040" : "#d0d0d0"
        border.width: 1
        
        Row {
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            anchors.leftMargin: 16
            spacing: 16
            
            Text {
                text: qsTr("就绪")
                color: isDarkMode ? "#ffffff" : "#000000"
                font.pixelSize: 12
            }
            
            Text {
                text: Qt.formatDateTime(new Date(), "yyyy-MM-dd hh:mm:ss")
                color: isDarkMode ? "#cccccc" : "#666666"
                font.pixelSize: 12
                
                Timer {
                    interval: 1000
                    running: true
                    repeat: true
                    onTriggered: parent.text = Qt.formatDateTime(new Date(), "yyyy-MM-dd hh:mm:ss")
                }
            }
        }
        
        Text {
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            anchors.rightMargin: 16
            text: qsTr("TimeNest v2.1.0 Preview")
            color: isDarkMode ? "#cccccc" : "#666666"
            font.pixelSize: 12
        }
    }

    // 关于对话框 - 暂时注释掉
    /*
    AboutDialog {
        id: aboutDialog
        isDarkMode: mainWindow.isDarkMode
        anchors.centerIn: parent
    }
    */

    // 通知容器
    Item {
        id: notificationContainer
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 20
        width: 350
        height: parent.height
        z: 1000

        property var notifications: []

        function showNotification(title, message) {
            var component = Qt.createComponent("components/NotificationToast.qml")
            if (component.status === Component.Ready) {
                var notification = component.createObject(notificationContainer, {
                    "title": title,
                    "message": message,
                    "isDarkMode": mainWindow.isDarkMode,
                    "y": notifications.length * 80
                })

                notifications.push(notification)

                // 重新排列通知位置
                for (var i = 0; i < notifications.length; i++) {
                    notifications[i].y = i * 80
                }
            }
        }
    }

    // 连接桥接信号
    Connections {
        target: typeof timeNestBridge !== 'undefined' ? timeNestBridge : null

        function onNotificationReceived(title, message) {
            notificationContainer.showNotification(title, message)
        }

        function onScheduleChanged() {
            // 刷新课程表相关视图
            console.log("课程表数据已更新")
        }

        function onTasksChanged() {
            // 刷新任务相关视图
            console.log("任务数据已更新")
        }

        function onThemeChanged(themeName) {
            // 处理主题变更
            console.log("主题已切换到:", themeName)
        }

        function onSystemTrayClicked() {
            // 系统托盘点击事件
            mainWindow.show()
            mainWindow.raise()
            mainWindow.requestActivate()
        }

        function onViewChangeRequested(viewName) {
            // 处理视图切换请求
            currentView = viewName
        }
    }



    Dialog {
        id: newCourseDialog
        title: qsTr("新建课程")
        width: 400
        height: 500
        modal: true
        anchors.centerIn: parent
        visible: showingNewCourseDialog

        Item {
            anchors.fill: parent
            anchors.margins: 20

            ColumnLayout {
                anchors.fill: parent
                spacing: 15

            Text {
                text: qsTr("课程信息")
                font.pixelSize: 16
                font.bold: true
                color: isDarkMode ? "#ffffff" : "#000000"
                Layout.fillWidth: true
            }

            TextField {
                id: courseNameField
                Layout.fillWidth: true
                placeholderText: qsTr("课程名称")
            }

            TextField {
                id: courseTeacherField
                Layout.fillWidth: true
                placeholderText: qsTr("任课教师")
            }

            TextField {
                id: courseLocationField
                Layout.fillWidth: true
                placeholderText: qsTr("上课地点")
            }

            TextField {
                id: courseTimeField
                Layout.fillWidth: true
                placeholderText: qsTr("上课时间 (如: 08:00-09:40)")
            }

            ComboBox {
                id: courseWeekdayCombo
                Layout.fillWidth: true
                model: [qsTr("周一"), qsTr("周二"), qsTr("周三"), qsTr("周四"), qsTr("周五"), qsTr("周六"), qsTr("周日")]
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                TextField {
                    id: startWeekField
                    Layout.preferredWidth: 80
                    placeholderText: qsTr("开始周")
                    validator: IntValidator { bottom: 1; top: 30 }
                }

                Text {
                    text: qsTr("到")
                    Layout.alignment: Qt.AlignVCenter
                    color: isDarkMode ? "#ffffff" : "#000000"
                }

                TextField {
                    id: endWeekField
                    Layout.preferredWidth: 80
                    placeholderText: qsTr("结束周")
                    validator: IntValidator { bottom: 1; top: 30 }
                }
            }

            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                spacing: 10

                Button {
                    text: qsTr("确定")
                    onClicked: {
                        createNewCourse()
                        newCourseDialog.close()
                    }
                }

                Button {
                    text: qsTr("取消")
                    onClicked: newCourseDialog.close()
                }
            }
            }
        }

        onClosed: {
            showingNewCourseDialog = false
            clearCourseFields()
        }
    }

    Dialog {
        id: newTaskDialog
        title: qsTr("新建任务")
        width: 400
        height: 400
        modal: true
        anchors.centerIn: parent
        visible: showingNewTaskDialog

        Item {
            anchors.fill: parent
            anchors.margins: 20

            ColumnLayout {
                anchors.fill: parent
                spacing: 15

            Text {
                text: qsTr("任务信息")
                font.pixelSize: 16
                font.bold: true
                color: isDarkMode ? "#ffffff" : "#000000"
                Layout.fillWidth: true
            }

            TextField {
                id: taskTitleField
                Layout.fillWidth: true
                placeholderText: qsTr("任务标题")
            }

            ScrollView {
                Layout.fillWidth: true
                Layout.preferredHeight: 100

                TextArea {
                    id: taskDescriptionArea
                    placeholderText: qsTr("任务描述")
                    wrapMode: TextArea.Wrap
                }
            }

            ComboBox {
                id: taskPriorityCombo
                Layout.fillWidth: true
                model: [qsTr("低优先级"), qsTr("中优先级"), qsTr("高优先级"), qsTr("紧急")]
            }

            TextField {
                id: taskDueDateField
                Layout.fillWidth: true
                placeholderText: qsTr("截止日期 (YYYY-MM-DD)")
            }

            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                spacing: 10

                Button {
                    text: qsTr("确定")
                    onClicked: {
                        createNewTask()
                        newTaskDialog.close()
                    }
                }

                Button {
                    text: qsTr("取消")
                    onClicked: newTaskDialog.close()
                }
            }
            }
        }

        onClosed: {
            showingNewTaskDialog = false
            clearTaskFields()
        }
    }

    // 全局函数
    /*
    function showAboutDialog() {
        aboutDialog.open()
    }
    */

    function showNewCourseDialog() {
        showingNewCourseDialog = true
    }

    function showNewTaskDialog() {
        showingNewTaskDialog = true
    }

    function createNewCourse() {
        if (typeof timeNestBridge !== 'undefined') {
            var weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            var success = timeNestBridge.addCourse(
                courseNameField.text,
                courseTeacherField.text,
                courseLocationField.text,
                courseTimeField.text,
                parseInt(startWeekField.text) || 1,
                parseInt(endWeekField.text) || 16,
                weekdays[courseWeekdayCombo.currentIndex]
            )
            if (success) {
                notificationContainer.showNotification("成功", "课程已创建")
            } else {
                notificationContainer.showNotification("失败", "课程创建失败")
            }
        }
    }

    function createNewTask() {
        if (typeof timeNestBridge !== 'undefined') {
            var priorities = ["low", "medium", "high", "urgent"]
            var success = timeNestBridge.addTask(
                taskTitleField.text,
                taskDescriptionArea.text,
                priorities[taskPriorityCombo.currentIndex],
                taskDueDateField.text
            )
            if (success) {
                notificationContainer.showNotification("成功", "任务已创建")
            } else {
                notificationContainer.showNotification("失败", "任务创建失败")
            }
        }
    }

    function clearCourseFields() {
        courseNameField.text = ""
        courseTeacherField.text = ""
        courseLocationField.text = ""
        courseTimeField.text = ""
        startWeekField.text = ""
        endWeekField.text = ""
        courseWeekdayCombo.currentIndex = 0
    }

    function clearTaskFields() {
        taskTitleField.text = ""
        taskDescriptionArea.text = ""
        taskDueDateField.text = ""
        taskPriorityCombo.currentIndex = 0
    }

    // 简化的功能函数，只保留核心功能

    function switchToView(viewName) {
        currentView = viewName
    }
}
