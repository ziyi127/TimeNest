import QtQuick
import QtQuick.Controls
import QtQuick.Window
import QtQuick.Layouts
import QtQuick.Dialogs
import RinUI
import "components"

Window {
    id: mainWindow
    width: 1200
    height: 800
    visible: true
    title: qsTr("TimeNest - 智能时间管理助手")

    // 主题设置 - 默认白色主题
    property bool isDarkMode: false

    // 应用状态
    property string currentView: "dashboard"

    // 对话框状态
    property bool showingAboutDialog: false
    property bool showingNewCourseDialog: false
    property bool showingNewTaskDialog: false

    Rectangle {
        anchors.fill: parent
        color: isDarkMode ? "#1e1e1e" : "#f5f5f5"
        
        // 侧边栏
        Frame {
            id: sidebar
            width: 280
            height: parent.height
            radius: 0
            borderWidth: 0
            rightPadding: 0
            leftPadding: 16
            topPadding: 16
            bottomPadding: 16

            Column {
                anchors.fill: parent
                spacing: 16

                // 应用标题
                Text {
                    text: qsTr("TimeNest")
                    font.pixelSize: 24
                    font.bold: true
                    color: isDarkMode ? "#ffffff" : "#000000"
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                // 分隔线
                Rectangle {
                    width: parent.width
                    height: 1
                    color: isDarkMode ? "#404040" : "#e0e0e0"
                    radius: 0.5
                }

                // 核心功能区域
                Text {
                    text: qsTr("核心功能")
                    font.pixelSize: 14
                    font.bold: true
                    color: isDarkMode ? "#cccccc" : "#666666"
                    leftPadding: 8
                }

                ListView {
                    width: parent.width
                    height: 240  // 6个项目 * 40高度
                    model: ListModel {
                        ListElement {
                            itemName: qsTr("仪表板")
                            iconName: "ic_fluent_home_20_regular"
                            viewName: "dashboard"
                        }
                        ListElement {
                            itemName: qsTr("课程表")
                            iconName: "ic_fluent_calendar_20_regular"
                            viewName: "schedule"
                        }
                        ListElement {
                            itemName: qsTr("任务管理")
                            iconName: "ic_fluent_task_list_20_regular"
                            viewName: "tasks"
                        }
                        ListElement {
                            itemName: qsTr("悬浮窗")
                            iconName: "ic_fluent_window_20_regular"
                            viewName: "floating"
                        }
                        ListElement {
                            itemName: qsTr("插件管理")
                            iconName: "ic_fluent_puzzle_20_regular"
                            viewName: "plugins"
                        }
                        ListElement {
                            itemName: qsTr("设置")
                            iconName: "ic_fluent_settings_20_regular"
                            viewName: "settings"
                        }
                    }

                    delegate: ListViewDelegate {
                        width: ListView.view.width
                        height: 40

                        property bool isSelected: currentView === model.viewName

                        leftArea: IconWidget {
                            icon: model.iconName
                            size: 20
                            Layout.alignment: Qt.AlignVCenter
                        }

                        middleArea: Text {
                            text: model.itemName
                            font.pixelSize: 14
                            color: isSelected ? "#2196f3" : (isDarkMode ? "#ffffff" : "#000000")
                            font.bold: isSelected
                            Layout.fillWidth: true
                            Layout.alignment: Qt.AlignVCenter
                        }

                        onClicked: {
                            currentView = model.viewName
                        }

                        // 选中状态的背景
                        Rectangle {
                            anchors.fill: parent
                            color: isSelected ? "#e3f2fd" : "transparent"
                            radius: 4
                            z: -1
                        }
                    }
                }

                    // 分隔线
                // 分隔线
                Rectangle {
                    width: parent.width
                    height: 1
                    color: isDarkMode ? "#404040" : "#e0e0e0"
                    radius: 0.5
                }

                // 快捷操作区域
                Text {
                    text: qsTr("快捷操作")
                    font.pixelSize: 14
                    font.bold: true
                    color: isDarkMode ? "#cccccc" : "#666666"
                    leftPadding: 8
                }

                Column {
                    width: parent.width
                    spacing: 4

                    Button {
                        text: qsTr("新建课程")
                        icon.name: "ic_fluent_add_20_regular"
                        width: parent.width
                        flat: true
                        onClicked: showNewCourseDialog()
                    }

                    Button {
                        text: qsTr("新建任务")
                        icon.name: "ic_fluent_task_list_add_20_regular"
                        width: parent.width
                        flat: true
                        onClicked: showNewTaskDialog()
                    }

                    ToggleButton {
                        text: qsTr("显示悬浮窗")
                        icon.name: "ic_fluent_window_20_regular"
                        width: parent.width
                        checked: typeof timeNestBridge !== 'undefined' ? timeNestBridge.isFloatingWindowVisible() : false
                        onClicked: {
                            if (typeof timeNestBridge !== 'undefined') {
                                timeNestBridge.toggleFloatingWindow()
                            }
                        }
                    }
                }

                    // 分隔线
                // 分隔线
                Rectangle {
                    width: parent.width
                    height: 1
                    color: isDarkMode ? "#404040" : "#e0e0e0"
                    radius: 0.5
                }

                // 系统控制区域
                Text {
                    text: qsTr("系统控制")
                    font.pixelSize: 14
                    font.bold: true
                    color: isDarkMode ? "#cccccc" : "#666666"
                    leftPadding: 8
                }

                Column {
                    width: parent.width
                    spacing: 4

                    Button {
                        text: qsTr("关于")
                        icon.name: "ic_fluent_info_20_regular"
                        width: parent.width
                        flat: true
                        onClicked: showAboutDialog()
                    }

                    // 主题切换
                    Button {
                        text: isDarkMode ? qsTr("浅色模式") : qsTr("深色模式")
                        icon.name: isDarkMode ? "ic_fluent_weather_sunny_20_regular" : "ic_fluent_weather_moon_20_regular"
                        width: parent.width
                        flat: true
                        onClicked: isDarkMode = !isDarkMode
                    }

                    // 退出按钮
                    Button {
                        text: qsTr("退出应用")
                        icon.name: "ic_fluent_power_20_regular"
                        width: parent.width
                        primaryColor: "#d32f2f"  // 红色警告色
                        onClicked: {
                            if (typeof timeNestBridge !== 'undefined') {
                                timeNestBridge.exitApplication()
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
            text: qsTr("TimeNest v1.1.3 Preview")
            color: isDarkMode ? "#cccccc" : "#666666"
            font.pixelSize: 12
        }
    }

    // 关于对话框
    AboutDialog {
        id: aboutDialog
        isDarkMode: mainWindow.isDarkMode
        anchors.centerIn: parent
    }

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



    // 新建课程对话框
    Dialog {
        id: newCourseDialog
        title: qsTr("新建课程")
        width: 400
        height: 500
        modal: true
        anchors.centerIn: parent
        visible: showingNewCourseDialog

        Column {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 15

            Text {
                text: qsTr("课程信息")
                font.pixelSize: 16
                font.bold: true
                color: isDarkMode ? "#ffffff" : "#000000"
            }

            TextField {
                id: courseNameField
                width: parent.width
                placeholderText: qsTr("课程名称")
            }

            TextField {
                id: courseTeacherField
                width: parent.width
                placeholderText: qsTr("任课教师")
            }

            TextField {
                id: courseLocationField
                width: parent.width
                placeholderText: qsTr("上课地点")
            }

            TextField {
                id: courseTimeField
                width: parent.width
                placeholderText: qsTr("上课时间 (如: 08:00-09:40)")
            }

            ComboBox {
                id: courseWeekdayCombo
                width: parent.width
                model: [qsTr("周一"), qsTr("周二"), qsTr("周三"), qsTr("周四"), qsTr("周五"), qsTr("周六"), qsTr("周日")]
            }

            Row {
                spacing: 10

                TextField {
                    id: startWeekField
                    width: 80
                    placeholderText: qsTr("开始周")
                    validator: IntValidator { bottom: 1; top: 30 }
                }

                Text {
                    text: qsTr("到")
                    anchors.verticalCenter: parent.verticalCenter
                    color: isDarkMode ? "#ffffff" : "#000000"
                }

                TextField {
                    id: endWeekField
                    width: 80
                    placeholderText: qsTr("结束周")
                    validator: IntValidator { bottom: 1; top: 30 }
                }
            }

            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 10

                Button {
                    text: qsTr("确定")
                    highlighted: true
                    icon.name: "ic_fluent_checkmark_20_regular"
                    onClicked: {
                        createNewCourse()
                        newCourseDialog.close()
                    }
                }

                Button {
                    text: qsTr("取消")
                    icon.name: "ic_fluent_dismiss_20_regular"
                    onClicked: newCourseDialog.close()
                }
            }
        }

        onClosed: {
            showingNewCourseDialog = false
            clearCourseFields()
        }
    }

    // 新建任务对话框
    Dialog {
        id: newTaskDialog
        title: qsTr("新建任务")
        width: 400
        height: 400
        modal: true
        anchors.centerIn: parent
        visible: showingNewTaskDialog

        Column {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 15

            Text {
                text: qsTr("任务信息")
                font.pixelSize: 16
                font.bold: true
                color: isDarkMode ? "#ffffff" : "#000000"
            }

            TextField {
                id: taskTitleField
                width: parent.width
                placeholderText: qsTr("任务标题")
            }

            ScrollView {
                width: parent.width
                height: 100

                TextArea {
                    id: taskDescriptionArea
                    placeholderText: qsTr("任务描述")
                    wrapMode: TextArea.Wrap
                }
            }

            ComboBox {
                id: taskPriorityCombo
                width: parent.width
                model: [qsTr("低优先级"), qsTr("中优先级"), qsTr("高优先级"), qsTr("紧急")]
            }

            TextField {
                id: taskDueDateField
                width: parent.width
                placeholderText: qsTr("截止日期 (YYYY-MM-DD)")
            }

            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 10

                Button {
                    text: qsTr("确定")
                    highlighted: true
                    icon.name: "ic_fluent_checkmark_20_regular"
                    onClicked: {
                        createNewTask()
                        newTaskDialog.close()
                    }
                }

                Button {
                    text: qsTr("取消")
                    icon.name: "ic_fluent_dismiss_20_regular"
                    onClicked: newTaskDialog.close()
                }
            }
        }

        onClosed: {
            showingNewTaskDialog = false
            clearTaskFields()
        }
    }

    // 全局函数
    function showAboutDialog() {
        aboutDialog.open()
    }

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
