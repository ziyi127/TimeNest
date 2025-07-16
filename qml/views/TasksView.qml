import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

ScrollView {
    id: tasksView

    property bool isDarkMode: false
    property var tasksModel: ListModel {
        // 添加一些默认测试数据，确保页面不为空
        ListElement {
            task_id: "1"  // 使用字符串类型
            title: "示例任务1"
            description: "这是一个示例任务"
            priority: "高"
            status: "进行中"
            due_date: "2025-01-20"
            completed: false
        }
        ListElement {
            task_id: "2"  // 使用字符串类型
            title: "示例任务2"
            description: "这是另一个示例任务"
            priority: "中"
            status: "已完成"
            due_date: "2025-01-18"
            completed: true
        }
    }

    Column {
        width: tasksView.width
        spacing: 20
        anchors.margins: 20

        // 标题和操作按钮
        Row {
            width: parent.width
            spacing: 10

            Text {
                text: qsTr("任务管理")
                font.pixelSize: 24
                font.bold: true
                color: isDarkMode ? "#ffffff" : "#000000"
                anchors.verticalCenter: parent.verticalCenter
            }

            Item { width: parent.width - 300 }

            RinButton {
                text: qsTr("新建任务")
                icon: "add"
                accentColor: "#2196f3"
                onClicked: newTaskDialog.open()
            }

            RinButton {
                text: qsTr("刷新")
                icon: "refresh"
                onClicked: loadTasks()
            }
        }

        // 任务统计
        Row {
            width: parent.width
            spacing: 20

            RinCard {
                width: 150
                height: 80
                radius: 8

                Column {
                    anchors.centerIn: parent
                    spacing: 5

                    RinIcon {
                        icon: "pending_actions"
                        size: 24
                        color: "#ff9800"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: qsTr("待办任务")
                        font.pixelSize: 14
                        color: isDarkMode ? "#cccccc" : "#666666"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: getPendingTasksCount().toString()
                        font.pixelSize: 20
                        font.bold: true
                        color: isDarkMode ? "#ffffff" : "#000000"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }

            RinCard {
                width: 150
                height: 80
                radius: 8

                Column {
                    anchors.centerIn: parent
                    spacing: 5

                    Text {
                        text: qsTr("已完成")
                        font.pixelSize: 14
                        color: isDarkMode ? "#cccccc" : "#666666"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        id: completedTasksCount
                        text: getCompletedTasksCount().toString()
                        font.pixelSize: 20
                        font.bold: true
                        color: "#4caf50"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }
        }

        // 任务列表
        Rectangle {
            width: parent.width
            height: 400
            color: isDarkMode ? "#2d2d2d" : "#ffffff"
            radius: 8
            border.color: isDarkMode ? "#404040" : "#e0e0e0"
            border.width: 1

            Column {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10

                Text {
                    text: qsTr("任务列表")
                    font.pixelSize: 16
                    font.bold: true
                    color: isDarkMode ? "#ffffff" : "#000000"
                }

                ListView {
                    width: parent.width
                    height: parent.height - 40
                    model: tasksModel
                    spacing: 8

                    delegate: Rectangle {
                        width: ListView.view ? ListView.view.width : 400
                        height: 80
                        color: isDarkMode ? "#3d3d3d" : "#f9f9f9"
                        radius: 6
                        border.color: isDarkMode ? "#505050" : "#e0e0e0"
                        border.width: 1

                        Row {
                            anchors.fill: parent
                            anchors.margins: 15
                            spacing: 15

                            Column {
                                width: parent.width - 120
                                spacing: 5

                                Text {
                                    text: model.title || "未知任务"
                                    font.pixelSize: 16
                                    font.bold: true
                                    color: isDarkMode ? "#ffffff" : "#000000"
                                }

                                Text {
                                    text: model.description || "无描述"
                                    font.pixelSize: 12
                                    color: isDarkMode ? "#cccccc" : "#666666"
                                    wrapMode: Text.WordWrap
                                }

                                Text {
                                    text: qsTr("优先级: ") + (model.priority || "中") + qsTr(" | 截止: ") + (model.due_date || "无")
                                    font.pixelSize: 10
                                    color: isDarkMode ? "#aaaaaa" : "#888888"
                                }
                            }

                            Column {
                                width: 100
                                spacing: 5

                                Button {
                                    text: model.completed ? qsTr("已完成") : qsTr("完成")
                                    width: 80
                                    height: 25
                                    enabled: !model.completed
                                    onClicked: {
                                        toggleTaskStatus(model.task_id, !model.completed)
                                    }
                                }

                                Button {
                                    text: qsTr("删除")
                                    width: 80
                                    height: 25
                                    onClicked: {
                                        deleteTask(model.task_id)
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // 新建任务对话框
    Dialog {
        id: newTaskDialog
        title: qsTr("新建任务")
        width: 400
        height: 350
        modal: true
        anchors.centerIn: parent

        Column {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 15

            TextField {
                id: taskTitleField
                width: parent.width
                placeholderText: qsTr("任务标题")
            }

            ScrollView {
                width: parent.width
                height: 80

                TextArea {
                    id: taskDescriptionField
                    placeholderText: qsTr("任务描述")
                    wrapMode: TextArea.Wrap
                }
            }

            ComboBox {
                id: taskPriorityCombo
                width: parent.width
                model: [qsTr("低"), qsTr("中"), qsTr("高")]
                currentIndex: 1
            }

            TextField {
                id: taskDueDateField
                width: parent.width
                placeholderText: qsTr("截止日期 (YYYY-MM-DD)")
            }

            Row {
                width: parent.width
                spacing: 10

                Button {
                    text: qsTr("取消")
                    onClicked: {
                        newTaskDialog.close()
                        clearTaskForm()
                    }
                }

                Button {
                    text: qsTr("创建")
                    enabled: taskTitleField.text.trim() !== ""
                    onClicked: {
                        if (addNewTask()) {
                            newTaskDialog.close()
                            clearTaskForm()
                        }
                    }
                }
            }
        }
    }

    // JavaScript 函数
    function loadTasks() {
        if (typeof timeNestBridge !== 'undefined') {
            var tasks = timeNestBridge.getTasksData()
            tasksModel.clear()
            for (var i = 0; i < tasks.length; i++) {
                tasksModel.append(tasks[i])
            }
        }
        updateTaskCounts()
    }

    function addNewTask() {
        if (typeof timeNestBridge !== 'undefined') {
            var success = timeNestBridge.addTask(
                taskTitleField.text.trim(),
                taskDescriptionField.text.trim(),
                taskPriorityCombo.currentText,
                taskDueDateField.text.trim()
            )
            if (success) {
                loadTasks()
                return true
            }
        }
        return false
    }

    function toggleTaskStatus(taskId, completed) {
        if (typeof timeNestBridge !== 'undefined') {
            try {
                console.log("切换任务状态:", taskId, completed)
                var success = timeNestBridge.updateTaskStatus(taskId, completed)
                if (success) {
                    console.log("任务状态更新成功")
                    loadTasks()
                    // 显示成功提示
                    if (typeof timeNestBridge.showNotification !== 'undefined') {
                        timeNestBridge.showNotification("任务管理", completed ? "任务已完成" : "任务已重新激活")
                    }
                } else {
                    console.log("任务状态更新失败")
                    // 显示错误提示
                    if (typeof timeNestBridge.showNotification !== 'undefined') {
                        timeNestBridge.showNotification("任务管理", "更新任务状态失败")
                    }
                }
            } catch (e) {
                console.log("切换任务状态异常:", e)
            }
        }
    }

    function deleteTask(taskId) {
        if (typeof timeNestBridge !== 'undefined') {
            try {
                console.log("删除任务:", taskId)
                var success = timeNestBridge.deleteTask(taskId)
                if (success) {
                    console.log("任务删除成功")
                    loadTasks()
                    // 显示成功提示
                    if (typeof timeNestBridge.showNotification !== 'undefined') {
                        timeNestBridge.showNotification("任务管理", "任务已删除")
                    }
                } else {
                    console.log("任务删除失败")
                    // 显示错误提示
                    if (typeof timeNestBridge.showNotification !== 'undefined') {
                        timeNestBridge.showNotification("任务管理", "删除任务失败")
                    }
                }
            } catch (e) {
                console.log("删除任务异常:", e)
            }
        }
    }

    function clearTaskForm() {
        taskTitleField.text = ""
        taskDescriptionField.text = ""
        taskDueDateField.text = ""
        taskPriorityCombo.currentIndex = 1
    }

    function getPendingTasksCount() {
        var count = 0
        for (var i = 0; i < tasksModel.count; i++) {
            if (!tasksModel.get(i).completed) {
                count++
            }
        }
        return count
    }

    function getCompletedTasksCount() {
        var count = 0
        for (var i = 0; i < tasksModel.count; i++) {
            if (tasksModel.get(i).completed) {
                count++
            }
        }
        return count
    }

    function updateTaskCounts() {
        // 任务计数现在通过SettingCard的description属性显示，无需手动更新
    }

    // 组件加载完成时加载任务
    Component.onCompleted: {
        loadTasks()
    }

    // 监听任务变化信号
    Connections {
        target: typeof timeNestBridge !== 'undefined' ? timeNestBridge : null
        function onTasksChanged() {
            loadTasks()
        }
    }
}
