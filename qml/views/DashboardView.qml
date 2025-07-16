import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

ScrollView {
    id: dashboardView
    
    property bool isDarkMode: false
    
    Column {
        width: dashboardView.width
        spacing: 24
        
        // 页面标题
        Text {
            text: qsTr("仪表板")
            font.pixelSize: 32
            font.bold: true
            color: isDarkMode ? "#ffffff" : "#000000"
        }
        
        RinResponsiveRow {
            width: parent.width
            spacing: 16

            RinCard {
                Layout.fillWidth: true
                Layout.preferredHeight: 120
                radius: 8

                Column {
                    anchors.centerIn: parent
                    spacing: 8

                    RinIcon {
                        icon: "calendar_today"
                        size: 32
                        color: "#2196f3"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: qsTr("今日课程")
                        font.pixelSize: 16
                        color: isDarkMode ? "#cccccc" : "#666666"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        id: todayCoursesCount
                        text: "5"
                        font.pixelSize: 24
                        font.bold: true
                        color: isDarkMode ? "#ffffff" : "#000000"
                        anchors.horizontalCenter: parent.horizontalCenter

                        Component.onCompleted: {
                            if (typeof timeNestBridge !== 'undefined') {
                                var courses = timeNestBridge.getScheduleData()
                                var todayCount = 0
                                var today = new Date()
                                var dayOfWeek = today.getDay()

                                for (var i = 0; i < courses.length; i++) {
                                    if (courses[i].day_of_week === dayOfWeek) {
                                        todayCount++
                                    }
                                }
                                text = todayCount.toString()
                            }
                        }
                    }
                }
            }
            
            RinCard {
                Layout.fillWidth: true
                Layout.preferredHeight: 120
                radius: 8

                Column {
                    anchors.centerIn: parent
                    spacing: 8

                    RinIcon {
                        icon: "task_alt"
                        size: 32
                        color: "#ff9800"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: qsTr("待办任务")
                        font.pixelSize: 16
                        color: isDarkMode ? "#cccccc" : "#666666"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        id: pendingTasksCount
                        text: "12"
                        font.pixelSize: 24
                        font.bold: true
                        color: isDarkMode ? "#ffffff" : "#000000"
                        anchors.horizontalCenter: parent.horizontalCenter

                        Component.onCompleted: {
                            if (typeof timeNestBridge !== 'undefined') {
                                var tasks = timeNestBridge.getTasksData()
                                var pendingCount = 0

                                for (var i = 0; i < tasks.length; i++) {
                                    if (tasks[i].status === "进行中") {
                                        pendingCount++
                                    }
                                }
                                text = pendingCount.toString()
                            }
                        }
                    }
                }
            }
            
            RinCard {
                Layout.fillWidth: true
                Layout.preferredHeight: 120
                radius: 8

                Column {
                    anchors.centerIn: parent
                    spacing: 8

                    RinIcon {
                        icon: "check_circle"
                        size: 32
                        color: "#4caf50"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: qsTr("已完成任务")
                        font.pixelSize: 16
                        color: isDarkMode ? "#cccccc" : "#666666"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        id: completedTasksCount
                        text: "2"
                        font.pixelSize: 24
                        font.bold: true
                        color: isDarkMode ? "#ffffff" : "#000000"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }
        }
        
        RinCard {
            width: parent.width
            height: 300
            radius: 8
            
            Column {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 16
                
                Text {
                    text: qsTr("今日课程安排")
                    font.pixelSize: 18
                    font.bold: true
                    color: isDarkMode ? "#ffffff" : "#000000"
                }
                
                ListView {
                    id: todayClassesListView
                    width: parent.width
                    height: parent.height - 40
                    model: ListModel {
                        id: todayClassesModel
                    }

                    Component.onCompleted: {
                        loadTodayClasses()
                    }
                    
                    delegate: Rectangle {
                        width: parent.width
                        height: 50
                        color: {
                            if (model.status === "current") {
                                return isDarkMode ? "#0d4f3c" : "#e8f5e8"
                            } else {
                                return "transparent"
                            }
                        }
                        radius: 4
                        
                        Row {
                            anchors.left: parent.left
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.leftMargin: 12
                            spacing: 16
                            
                            Text {
                                text: model.time
                                font.pixelSize: 14
                                color: isDarkMode ? "#cccccc" : "#666666"
                                width: 100
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            
                            Text {
                                text: model.subject
                                font.pixelSize: 14
                                font.bold: model.status === "current"
                                color: isDarkMode ? "#ffffff" : "#000000"
                                width: 120
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            
                            Text {
                                text: model.location
                                font.pixelSize: 14
                                color: isDarkMode ? "#cccccc" : "#666666"
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }
                        
                        Rectangle {
                            visible: model.status === "current"
                            width: 4
                            height: parent.height * 0.6
                            anchors.left: parent.left
                            anchors.verticalCenter: parent.verticalCenter
                            color: "#4caf50"
                            radius: 2
                        }
                    }
                }
            }
        }
        
        RinCard {
            width: parent.width
            height: 150
            radius: 8
            
            Column {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 16
                
                Text {
                    text: qsTr("快速操作")
                    font.pixelSize: 18
                    font.bold: true
                    color: isDarkMode ? "#ffffff" : "#000000"
                }
                
                Row {
                    spacing: 16

                    RinButton {
                        text: qsTr("添加课程")
                        accentColor: "#2196f3"
                        icon: "add"
                        onClicked: {
                            if (typeof timeNestBridge !== 'undefined') {
                                timeNestBridge.showNewCourseDialog()
                            }
                        }
                    }

                    RinButton {
                        text: qsTr("创建任务")
                        icon: "add_task"
                        onClicked: {
                            createNewTask()
                        }
                    }

                    RinButton {
                        text: qsTr("打开悬浮窗")
                        icon: "picture_in_picture"
                        onClicked: {
                            toggleFloatingWindow()
                        }
                    }

                    RinButton {
                        text: qsTr("刷新数据")
                        icon: "refresh"
                        onClicked: {
                            refreshDashboard()
                        }
                    }
                }
            }
        }
    }

    // JavaScript 函数
    function getTodayClassesCount() {
        // 返回今日课程数量
        if (typeof timeNestBridge !== 'undefined') {
            try {
                var courses = timeNestBridge.getScheduleData()
                // 这里可以添加过滤今日课程的逻辑
                return Math.min(courses.length, 8) // 限制显示数量
            } catch (e) {
                console.log("获取课程数据失败:", e)
            }
        }
        return 3 // 默认值
    }

    function loadTodayClasses() {
        if (typeof timeNestBridge !== 'undefined') {
            try {
                var courses = timeNestBridge.getScheduleData()
                todayClassesModel.clear()

                var today = new Date()
                var dayOfWeek = today.getDay() // 0=周日, 1=周一, ..., 6=周六
                var currentTime = today.getHours() * 100 + today.getMinutes() // 转换为HHMM格式

                // 过滤今日课程
                for (var i = 0; i < courses.length; i++) {
                    var course = courses[i]
                    if (course.time && course.time.includes(getDayName(dayOfWeek))) {
                        var status = "upcoming"

                        // 解析课程时间，判断状态
                        var timeMatch = course.time.match(/(\d{2}):(\d{2})-(\d{2}):(\d{2})/)
                        if (timeMatch) {
                            var startTime = parseInt(timeMatch[1]) * 100 + parseInt(timeMatch[2])
                            var endTime = parseInt(timeMatch[3]) * 100 + parseInt(timeMatch[4])

                            if (currentTime >= startTime && currentTime <= endTime) {
                                status = "current"
                            } else if (currentTime > endTime) {
                                status = "finished"
                            }
                        }

                        todayClassesModel.append({
                            time: extractTime(course.time),
                            subject: course.name || "未知课程",
                            location: course.location || "未知地点",
                            status: status
                        })
                    }
                }

                // 如果没有今日课程，显示提示
                if (todayClassesModel.count === 0) {
                    todayClassesModel.append({
                        time: "",
                        subject: "今日无课程安排",
                        location: "",
                        status: "none"
                    })
                }
            } catch (e) {
                console.log("加载今日课程失败:", e)
                todayClassesModel.append({
                    time: "",
                    subject: "加载课程失败",
                    location: "",
                    status: "error"
                })
            }
        }
    }

    function getDayName(dayOfWeek) {
        var days = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]
        return days[dayOfWeek] || ""
    }

    function extractTime(timeStr) {
        // 从"周一 08:00-09:40"中提取"08:00-09:40"
        var match = timeStr.match(/(\d{2}:\d{2}-\d{2}:\d{2})/)
        return match ? match[1] : timeStr
    }

    // 定时刷新今日课程
    Timer {
        id: refreshTimer
        interval: 60000 // 每分钟刷新一次
        running: true
        repeat: true
        onTriggered: loadTodayClasses()
    }

    function getPendingTasksCount() {
        // 返回待办任务数量
        if (typeof timeNestBridge !== 'undefined') {
            try {
                var tasks = timeNestBridge.getTasksData()
                var pendingCount = 0
                for (var i = 0; i < tasks.length; i++) {
                    if (!tasks[i].completed) {
                        pendingCount++
                    }
                }
                return pendingCount
            } catch (e) {
                console.log("获取任务数据失败:", e)
            }
        }
        return 5 // 默认值
    }

    function getCompletedTasksCount() {
        // 返回已完成任务数量
        if (typeof timeNestBridge !== 'undefined') {
            try {
                var tasks = timeNestBridge.getTasksData()
                var completedCount = 0
                for (var i = 0; i < tasks.length; i++) {
                    if (tasks[i].completed) {
                        completedCount++
                    }
                }
                return completedCount
            } catch (e) {
                console.log("获取任务数据失败:", e)
            }
        }
        return 2 // 默认值
    }

    function refreshDashboard() {
        // 刷新仪表板数据
        if (typeof timeNestBridge !== 'undefined') {
            // 触发数据重新加载
            todayCoursesCount.text = getTodayClassesCount().toString()
            pendingTasksCount.text = getPendingTasksCount().toString()
            completedTasksCount.text = getCompletedTasksCount().toString()
        }
    }

    function createNewTask() {
        // 创建新任务
        if (typeof timeNestBridge !== 'undefined') {
            // 这里可以打开任务创建对话框或切换到任务页面
            timeNestBridge.showNotification("快速操作", "请前往任务管理页面创建新任务")
        }
    }

    function toggleFloatingWindow() {
        // 切换悬浮窗
        if (typeof timeNestBridge !== 'undefined') {
            var success = timeNestBridge.toggleFloatingWindow()
            if (success) {
                timeNestBridge.showNotification("悬浮窗", "悬浮窗状态已切换")
            }
        }
    }

    // 组件加载完成时刷新数据
    Component.onCompleted: {
        refreshDashboard()
    }
}
