import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import RinUI

Item {
    id: scheduleView

    property bool isDarkMode: false
    property var coursesModel: ListModel {
        // 添加一些默认测试数据，确保页面不为空
        ListElement {
            course_id: "1"  // 使用字符串类型
            name: "高等数学"
            teacher: "张教授"
            location: "教学楼A101"
            time: "周一 08:00-09:40"
            weeks: "1-16周"
            start_week: 1
            end_week: 16
        }
        ListElement {
            course_id: "2"  // 使用字符串类型
            name: "大学英语"
            teacher: "李教授"
            location: "外语楼201"
            time: "周二 10:00-11:40"
            weeks: "1-16周"
            start_week: 1
            end_week: 16
        }
        ListElement {
            course_id: "3"  // 使用字符串类型
            name: "计算机程序设计"
            teacher: "王教授"
            location: "实验楼501"
            time: "周三 14:00-15:40"
            weeks: "2-16周"
            start_week: 2
            end_week: 16
        }
    }

    ColumnLayout {
        id: mainColumn
        anchors.fill: parent
        anchors.margins: 16
        spacing: 16

        // 标题和操作按钮
        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 40

            Text {
                text: qsTr("课程表管理")
                font.pixelSize: 24
                font.bold: true
                color: isDarkMode ? "#ffffff" : "#000000"
                Layout.alignment: Qt.AlignVCenter
            }

            Item { Layout.fillWidth: true }

            Button {
                text: qsTr("新建课程")
                icon.name: "ic_fluent_add_20_regular"
                onClicked: newCourseDialog.open()
            }

            Button {
                text: qsTr("导入Excel")
                icon.name: "ic_fluent_arrow_import_20_regular"
                onClicked: importFileDialog.open()
            }

            Button {
                text: qsTr("导出Excel")
                icon.name: "ic_fluent_arrow_export_20_regular"
                onClicked: exportFileDialog.open()
            }

            Button {
                text: qsTr("创建模板")
                icon.name: "ic_fluent_document_20_regular"
                onClicked: createExcelTemplate()
            }

            Button {
                text: qsTr("刷新")
                icon.name: "ic_fluent_arrow_clockwise_20_regular"
                onClicked: loadCourses()
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 80
            spacing: 20

            Frame {
                Layout.preferredWidth: 150
                Layout.preferredHeight: 80

                Column {
                    anchors.centerIn: parent
                    spacing: 5

                    Text {
                        text: qsTr("总课程数")
                        font.pixelSize: 14
                        color: isDarkMode ? "#cccccc" : "#666666"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: coursesModel.count.toString()
                        font.pixelSize: 20
                        font.bold: true
                        color: "#2196f3"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }

            Frame {
                Layout.preferredWidth: 150
                Layout.preferredHeight: 80

                Column {
                    anchors.centerIn: parent
                    spacing: 5

                    Text {
                        text: qsTr("本周课程")
                        font.pixelSize: 14
                        color: isDarkMode ? "#cccccc" : "#666666"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: "5"
                        font.pixelSize: 20
                        font.bold: true
                        color: "#4caf50"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }
        }

        // 课程列表
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 300
            color: isDarkMode ? "#2d2d2d" : "#ffffff"
            radius: 8
            border.color: isDarkMode ? "#404040" : "#e0e0e0"
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 12

                RowLayout {
                    Layout.fillWidth: true

                    Text {
                        text: qsTr("课程列表")
                        font.pixelSize: 18
                        font.bold: true
                        color: isDarkMode ? "#ffffff" : "#000000"
                        Layout.fillWidth: true
                    }

                    Text {
                        text: qsTr("共 %1 门课程").arg(coursesModel.count)
                        font.pixelSize: 12
                        color: isDarkMode ? "#cccccc" : "#666666"
                        Layout.alignment: Qt.AlignVCenter
                    }
                }

                ListView {
                    id: courseListView
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    model: coursesModel
                    spacing: 8
                    clip: true  // 确保内容不会溢出

                    // 禁用循环滚动
                    boundsBehavior: Flickable.StopAtBounds

                    // 滚动条设置
                    ScrollBar.vertical: ScrollBar {
                        active: true
                        policy: ScrollBar.AsNeeded
                        width: 8
                        anchors.right: parent.right
                        anchors.rightMargin: 2
                    }

                    // 性能优化设置
                    cacheBuffer: 100  // 减少缓存以避免过度渲染
                    reuseItems: true  // 重用列表项

                    // 空状态提示
                    Rectangle {
                        anchors.centerIn: parent
                        width: parent.width - 40
                        height: 120
                        color: "transparent"
                        visible: coursesModel.count === 0

                        Column {
                            anchors.centerIn: parent
                            spacing: 12

                            Text {
                                text: "📚"
                                font.pixelSize: 48
                                anchors.horizontalCenter: parent.horizontalCenter
                            }

                            Text {
                                text: qsTr("暂无课程")
                                font.pixelSize: 16
                                font.bold: true
                                color: isDarkMode ? "#ffffff" : "#000000"
                                anchors.horizontalCenter: parent.horizontalCenter
                            }

                            Text {
                                text: qsTr("点击上方\"新建课程\"按钮添加您的第一门课程")
                                font.pixelSize: 12
                                color: isDarkMode ? "#cccccc" : "#666666"
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                        }
                    }

                    delegate: Rectangle {
                        id: courseItem
                        width: courseListView.width
                        height: 90  // 稍微增加高度以容纳更好的布局

                        // 使用属性绑定减少重复计算
                        property color bgColor: isDarkMode ? "#3d3d3d" : "#f9f9f9"
                        property color borderColor: isDarkMode ? "#505050" : "#e0e0e0"
                        property color hoverColor: isDarkMode ? "#4d4d4d" : "#f0f0f0"

                        color: mouseArea.containsMouse ? hoverColor : bgColor
                        radius: 8
                        border.color: borderColor
                        border.width: 1

                        // 鼠标悬停效果
                        MouseArea {
                            id: mouseArea
                            anchors.fill: parent
                            hoverEnabled: true
                            acceptedButtons: Qt.NoButton  // 不处理点击，只处理悬停
                        }

                        // 主要内容布局
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 12

                            // 课程信息区域
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 4

                                Text {
                                    text: model.name || "未知课程"
                                    font.pixelSize: 16
                                    font.bold: true
                                    color: isDarkMode ? "#ffffff" : "#000000"
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                }

                                Text {
                                    text: qsTr("教师: ") + (model.teacher || "未知")
                                    font.pixelSize: 12
                                    color: isDarkMode ? "#cccccc" : "#666666"
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                }

                                Text {
                                    text: qsTr("地点: ") + (model.location || "未知")
                                    font.pixelSize: 12
                                    color: isDarkMode ? "#cccccc" : "#666666"
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                }

                                Text {
                                    text: qsTr("时间: ") + (model.time || "未知") + qsTr(" | 周次: ") + (model.weeks || "未知")
                                    font.pixelSize: 11
                                    color: isDarkMode ? "#aaaaaa" : "#888888"
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                }
                            }

                            // 操作按钮区域
                            ColumnLayout {
                                Layout.preferredWidth: 80
                                spacing: 6

                                Button {
                                    text: qsTr("编辑")
                                    icon.name: "ic_fluent_edit_20_regular"
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 28
                                    font.pixelSize: 11
                                    onClicked: {
                                        editCourse(model.course_id, model)
                                    }
                                }

                                Button {
                                    text: qsTr("删除")
                                    icon.name: "ic_fluent_delete_20_regular"
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 28
                                    font.pixelSize: 11
                                    // 删除按钮的红色样式
                                    palette.button: "#d32f2f"
                                    palette.buttonText: "#ffffff"
                                    onClicked: {
                                        deleteCourse(model.course_id)
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // 新建课程对话框
    Dialog {
        id: newCourseDialog
        title: qsTr("新建课程")
        width: 400
        height: 300
        modal: true
        anchors.centerIn: parent

        property int editingCourseId: -1  // -1表示新建，其他值表示编辑

        onOpened: {
            if (editingCourseId === -1) {
                title = qsTr("新建课程")
                // 清空表单
                courseNameField.text = ""
                courseTeacherField.text = ""
                courseLocationField.text = ""
                courseTimeField.text = ""
                courseWeeksField.text = ""
            }
        }

        Column {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 15

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
                placeholderText: qsTr("上课时间")
            }

            Row {
                width: parent.width
                spacing: 10

                Button {
                    text: qsTr("取消")
                    onClicked: {
                        newCourseDialog.close()
                    }
                }

                Button {
                    text: newCourseDialog.editingCourseId === -1 ? qsTr("创建") : qsTr("保存")
                    icon.name: newCourseDialog.editingCourseId === -1 ? "ic_fluent_add_20_regular" : "ic_fluent_save_20_regular"
                    enabled: courseNameField.text.trim() !== ""
                    highlighted: true
                    onClicked: {
                        if (newCourseDialog.editingCourseId === -1) {
                            addNewCourse()
                        } else {
                            updateCourse()
                        }
                        newCourseDialog.close()
                    }
                }
            }
        }
    }

    // Excel导入文件对话框
    FileDialog {
        id: importFileDialog
        title: qsTr("选择Excel课程表文件")
        nameFilters: ["Excel files (*.xlsx *.xls)", "All files (*)"]
        fileMode: FileDialog.OpenFile
        onAccepted: {
            var filePath = selectedFile.toString()
            // 移除file://前缀
            if (filePath.startsWith("file://")) {
                filePath = filePath.substring(7)
            }
            importExcelFile(filePath)
        }
    }

    // Excel导出文件对话框
    FileDialog {
        id: exportFileDialog
        title: qsTr("保存Excel课程表文件")
        nameFilters: ["Excel files (*.xlsx)", "All files (*)"]
        fileMode: FileDialog.SaveFile
        defaultSuffix: "xlsx"
        onAccepted: {
            var filePath = selectedFile.toString()
            // 移除file://前缀
            if (filePath.startsWith("file://")) {
                filePath = filePath.substring(7)
            }
            exportExcelFile(filePath)
        }
    }

    // 导入进度对话框
    Dialog {
        id: importProgressDialog
        title: qsTr("导入进度")
        width: 300
        height: 150
        modal: true
        anchors.centerIn: parent

        Column {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 15

            Text {
                id: importStatusText
                text: qsTr("正在导入Excel文件...")
                font.pixelSize: 14
                anchors.horizontalCenter: parent.horizontalCenter
            }

            ProgressBar {
                id: importProgressBar
                width: parent.width
                from: 0
                to: 100
                value: 0
            }

            Button {
                text: qsTr("取消")
                anchors.horizontalCenter: parent.horizontalCenter
                onClicked: importProgressDialog.close()
            }
        }
    }

    // JavaScript 函数
    function loadCourses() {
        if (typeof timeNestBridge !== 'undefined') {
            var courses = timeNestBridge.getScheduleData()
            coursesModel.clear()
            for (var i = 0; i < courses.length; i++) {
                coursesModel.append(courses[i])
            }
        }
    }

    function addNewCourse() {
        if (typeof timeNestBridge !== 'undefined') {
            var success = timeNestBridge.addCourse(
                courseNameField.text.trim(),
                courseTeacherField.text.trim(),
                courseLocationField.text.trim(),
                courseTimeField.text.trim(),
                1, 16
            )
            if (success) {
                loadCourses()
            }
        }
    }



    function createExcelTemplate() {
        if (typeof timeNestBridge !== 'undefined') {
            var success = timeNestBridge.createExcelTemplate()
            if (success) {
                console.log("Excel模板创建成功")
            } else {
                console.log("Excel模板创建失败")
            }
        }
    }

    function importExcelFile(filePath) {
        if (typeof timeNestBridge !== 'undefined') {
            importProgressDialog.open()
            importStatusText.text = qsTr("正在验证Excel文件...")
            importProgressBar.value = 5

            // 先验证文件格式
            var validation = timeNestBridge.validateExcelFile(filePath)
            if (!validation.valid) {
                importProgressDialog.close()
                console.log("Excel文件验证失败:", validation.message)
                return
            }

            // 导入Excel文件
            var success = timeNestBridge.importExcelSchedule(filePath)

            if (success) {
                // 成功时会通过进度信号更新，这里不需要额外处理
                setTimeout(function() {
                    loadCourses() // 重新加载课程列表
                    setTimeout(function() {
                        importProgressDialog.close()
                    }, 1500)
                }, 500)
            } else {
                // 失败时也会通过进度信号更新状态
                setTimeout(function() {
                    importProgressDialog.close()
                }, 3000)
            }
        }
    }

    function exportExcelFile(filePath) {
        if (typeof timeNestBridge !== 'undefined') {
            var success = timeNestBridge.exportExcelSchedule(filePath)
            if (success) {
                console.log("Excel导出成功:", filePath)
            } else {
                console.log("Excel导出失败")
            }
        }
    }

    function editCourse(courseId, courseData) {
        if (typeof timeNestBridge !== 'undefined') {
            try {
                console.log("编辑课程:", courseId, courseData)
                // 填充编辑表单
                courseNameField.text = courseData.name || ""
                courseTeacherField.text = courseData.teacher || ""
                courseLocationField.text = courseData.location || ""
                courseTimeField.text = courseData.time || ""
                courseWeeksField.text = courseData.weeks || ""

                // 设置为编辑模式
                newCourseDialog.title = qsTr("编辑课程")
                newCourseDialog.editingCourseId = courseId
                newCourseDialog.open()
            } catch (e) {
                console.log("编辑课程异常:", e)
            }
        }
    }

    function deleteCourse(courseId) {
        if (typeof timeNestBridge !== 'undefined') {
            try {
                console.log("删除课程:", courseId)
                var success = timeNestBridge.deleteCourse(courseId)
                if (success) {
                    console.log("课程删除成功")
                    loadCourses()
                    // 显示成功提示
                    if (typeof timeNestBridge.showNotification !== 'undefined') {
                        timeNestBridge.showNotification("课程管理", "课程已删除")
                    }
                } else {
                    console.log("课程删除失败")
                    // 显示错误提示
                    if (typeof timeNestBridge.showNotification !== 'undefined') {
                        timeNestBridge.showNotification("课程管理", "删除课程失败")
                    }
                }
            } catch (e) {
                console.log("删除课程异常:", e)
            }
        }
    }

    function updateCourse() {
        if (typeof timeNestBridge !== 'undefined') {
            try {
                var courseData = {
                    course_id: newCourseDialog.editingCourseId,
                    name: courseNameField.text.trim(),
                    teacher: courseTeacherField.text.trim(),
                    location: courseLocationField.text.trim(),
                    time: courseTimeField.text.trim(),
                    weeks: courseWeeksField.text.trim()
                }

                console.log("更新课程:", courseData)
                var success = timeNestBridge.updateCourse(courseData)
                if (success) {
                    console.log("课程更新成功")
                    loadCourses()
                    newCourseDialog.editingCourseId = -1  // 重置编辑状态
                    // 显示成功提示
                    if (typeof timeNestBridge.showNotification !== 'undefined') {
                        timeNestBridge.showNotification("课程管理", "课程已更新")
                    }
                } else {
                    console.log("课程更新失败")
                    // 显示错误提示
                    if (typeof timeNestBridge.showNotification !== 'undefined') {
                        timeNestBridge.showNotification("课程管理", "更新课程失败")
                    }
                }
            } catch (e) {
                console.log("更新课程异常:", e)
            }
        }
    }

    // 组件加载完成时加载课程
    Component.onCompleted: {
        loadCourses()
    }

    // 监听课程变化信号
    Connections {
        target: typeof timeNestBridge !== 'undefined' ? timeNestBridge : null
        function onScheduleChanged() {
            loadCourses()
        }
        function onImportProgress(progress, message) {
            importProgressBar.value = progress
            importStatusText.text = message
        }
    }
}
