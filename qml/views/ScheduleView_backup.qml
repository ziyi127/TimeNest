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
            course_id: 1
            name: "高等数学"
            teacher: "张教授"
            location: "教学楼A101"
            time: "周一 08:00-09:40"
            weeks: "1-16周"
            start_week: 1
            end_week: 16
        }
        ListElement {
            course_id: 2
            name: "大学英语"
            teacher: "李教授"
            location: "外语楼201"
            time: "周二 10:00-11:40"
            weeks: "1-16周"
            start_week: 1
            end_week: 16
        }
        ListElement {
            course_id: 3
            name: "计算机程序设计"
            teacher: "王教授"
            location: "实验楼501"
            time: "周三 14:00-15:40"
            weeks: "2-16周"
            start_week: 2
            end_week: 16
        }
    }

    // 添加课程对话框
    Dialog {
        id: addCourseDialog
        title: qsTr("添加课程")
        width: 400
        height: 450
        modal: true
        anchors.centerIn: parent

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 15

            TextField {
                id: courseNameField
                Layout.fillWidth: true
                placeholderText: qsTr("课程名称")
            }

            TextField {
                id: teacherField
                Layout.fillWidth: true
                placeholderText: qsTr("任课教师")
            }

            TextField {
                id: locationField
                Layout.fillWidth: true
                placeholderText: qsTr("上课地点")
            }

            ComboBox {
                id: dayCombo
                Layout.fillWidth: true
                model: [qsTr("周一"), qsTr("周二"), qsTr("周三"), qsTr("周四"), qsTr("周五"), qsTr("周六"), qsTr("周日")]
            }

            TextField {
                id: timeField
                Layout.fillWidth: true
                placeholderText: qsTr("上课时间 (如: 08:00-09:40)")
            }

            RowLayout {
                Layout.fillWidth: true

                SpinBox {
                    id: startWeekSpin
                    from: 1
                    to: 20
                    value: 1
                }

                Text {
                    text: qsTr("到")
                    color: isDarkMode ? "#ffffff" : "#000000"
                }

                SpinBox {
                    id: endWeekSpin
                    from: 1
                    to: 20
                    value: 16
                }

                Text {
                    text: qsTr("周")
                    color: isDarkMode ? "#ffffff" : "#000000"
                }
            }

            RowLayout {
                Layout.fillWidth: true

                Button {
                    text: qsTr("取消")
                    onClicked: {
                        addCourseDialog.close()
                        clearCourseForm()
                    }
                }

                Button {
                    text: qsTr("添加")
                    enabled: courseNameField.text.trim() !== ""
                    onClicked: {
                        if (addNewCourse()) {
                            addCourseDialog.close()
                            clearCourseForm()
                        }
                    }
                }
            }
        }
    }

    // 编辑课程对话框
    Dialog {
        id: editCourseDialog
        title: qsTr("编辑课程")
        width: 400
        height: 450
        modal: true
        anchors.centerIn: parent

        property int editingCourseId: -1

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 15

            TextField {
                id: editCourseNameField
                Layout.fillWidth: true
                placeholderText: qsTr("课程名称")
            }

            TextField {
                id: editTeacherField
                Layout.fillWidth: true
                placeholderText: qsTr("任课教师")
            }

            TextField {
                id: editLocationField
                Layout.fillWidth: true
                placeholderText: qsTr("上课地点")
            }

            ComboBox {
                id: editDayCombo
                Layout.fillWidth: true
                model: [qsTr("周一"), qsTr("周二"), qsTr("周三"), qsTr("周四"), qsTr("周五"), qsTr("周六"), qsTr("周日")]
            }

            TextField {
                id: editTimeField
                Layout.fillWidth: true
                placeholderText: qsTr("上课时间 (如: 08:00-09:40)")
            }

            RowLayout {
                Layout.fillWidth: true

                SpinBox {
                    id: editStartWeekSpin
                    from: 1
                    to: 20
                    value: 1
                }

                Text {
                    text: qsTr("到")
                    color: isDarkMode ? "#ffffff" : "#000000"
                }

                SpinBox {
                    id: editEndWeekSpin
                    from: 1
                    to: 20
                    value: 16
                }

                Text {
                    text: qsTr("周")
                    color: isDarkMode ? "#ffffff" : "#000000"
                }
            }

            RowLayout {
                Layout.fillWidth: true

                Button {
                    text: qsTr("取消")
                    onClicked: editCourseDialog.close()
                }

                Button {
                    text: qsTr("保存")
                    enabled: editCourseNameField.text.trim() !== ""
                    onClicked: {
                        if (updateCourse()) {
                            editCourseDialog.close()
                        }
                    }
                }
            }
        }
    }

    // Excel导入对话框
    Dialog {
        id: importExcelDialog
        title: qsTr("导入Excel课程表")
        width: 500
        height: 300
        modal: true
        anchors.centerIn: parent

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 15

            Text {
                text: qsTr("请选择要导入的Excel文件")
                font.pixelSize: 14
                color: isDarkMode ? "#ffffff" : "#000000"
            }

            TextField {
                id: importFilePathField
                Layout.fillWidth: true
                placeholderText: qsTr("Excel文件路径")
                readOnly: true
            }

            Button {
                text: qsTr("选择文件")
                onClicked: {
                    // TODO: 实现文件选择对话框
                    importFilePathField.text = "/path/to/schedule.xlsx"
                }
            }

            Text {
                text: qsTr("支持格式：.xlsx, .xls\n请确保Excel文件格式符合模板要求")
                font.pixelSize: 12
                color: isDarkMode ? "#cccccc" : "#666666"
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }

            RowLayout {
                Layout.fillWidth: true

                Button {
                    text: qsTr("取消")
                    onClicked: importExcelDialog.close()
                }

                Button {
                    text: qsTr("导入")
                    highlighted: true
                    enabled: importFilePathField.text.trim() !== ""
                    onClicked: {
                        if (importExcelSchedule()) {
                            importExcelDialog.close()
                        }
                    }
                }
            }
        }
    }

    // Excel导出对话框
    Dialog {
        id: exportExcelDialog
        title: qsTr("导出Excel课程表")
        width: 500
        height: 250
        modal: true
        anchors.centerIn: parent

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 15

            Text {
                text: qsTr("请选择导出位置")
                font.pixelSize: 14
                color: isDarkMode ? "#ffffff" : "#000000"
            }

            TextField {
                id: exportFilePathField
                Layout.fillWidth: true
                placeholderText: qsTr("导出文件路径")
                text: "课程表_" + new Date().toISOString().slice(0,10) + ".xlsx"
            }

            Button {
                text: qsTr("选择位置")
                onClicked: {
                    // TODO: 实现文件保存对话框
                    exportFilePathField.text = "/path/to/export_schedule.xlsx"
                }
            }

            RowLayout {
                Layout.fillWidth: true

                Button {
                    text: qsTr("取消")
                    onClicked: exportExcelDialog.close()
                }

                Button {
                    text: qsTr("导出")
                    highlighted: true
                    enabled: exportFilePathField.text.trim() !== ""
                    onClicked: {
                        if (exportExcelSchedule()) {
                            exportExcelDialog.close()
                        }
                    }
                }
            }
        }
    }

    ScrollView {
        anchors.fill: parent
    
    Column {
        width: scheduleView.width
        spacing: 24
        
        // 页面标题和工具栏
        Row {
            width: parent.width
            spacing: 16
            
            Text {
                text: qsTr("课程表")
                font.pixelSize: 32
                font.bold: true
                color: isDarkMode ? "#ffffff" : "#000000"
                anchors.verticalCenter: parent.verticalCenter
            }
            
            Item { width: parent.width - 400 }
            
            Row {
                spacing: 8
                anchors.verticalCenter: parent.verticalCenter
                
                Button {
                    text: qsTr("添加课程")
                    highlighted: true
                    onClicked: addCourseDialog.open()
                }

                Button {
                    text: qsTr("导入Excel")
                    onClicked: importExcelDialog.open()
                }

                Button {
                    text: qsTr("导出Excel")
                    onClicked: exportExcelDialog.open()
                }

                Button {
                    text: qsTr("创建模板")
                    onClicked: createExcelTemplate()
                }

                Button {
                    text: qsTr("刷新")
                    onClicked: loadCourses()
                }

                Button {
                    text: qsTr("导入课程表")
                    onClicked: {
                        // TODO: 打开导入对话框
                    }
                }

                Button {
                    text: qsTr("导出课程表")
                    onClicked: {
                        // TODO: 导出课程表
                    }
                }
            }
        }
        
        // 周次选择器
        Rectangle {
            width: parent.width
            height: 60
            color: isDarkMode ? "#2d2d2d" : "#ffffff"
            border.color: isDarkMode ? "#404040" : "#e0e0e0"
            border.width: 1
            radius: 8
            
            Row {
                anchors.centerIn: parent
                spacing: 16
                
                Text {
                    text: qsTr("当前周次:")
                    font.pixelSize: 14
                    color: isDarkMode ? "#cccccc" : "#666666"
                    anchors.verticalCenter: parent.verticalCenter
                }
                
                ComboBox {
                    model: {
                        var weeks = []
                        for (var i = 1; i <= 20; i++) {
                            weeks.push(qsTr("第") + i + qsTr("周"))
                        }
                        return weeks
                    }
                    currentIndex: 7 // 第8周
                    width: 120
                }
                
                Text {
                    text: qsTr("学期开始日期:")
                    font.pixelSize: 14
                    color: isDarkMode ? "#cccccc" : "#666666"
                    anchors.verticalCenter: parent.verticalCenter
                }
                
                Button {
                    text: "2025-02-24"
                    flat: true
                    onClicked: {
                        // TODO: 打开日期选择器
                    }
                }
            }
        }
        
        // 课程表网格
        Rectangle {
            width: parent.width
            height: 600
            color: isDarkMode ? "#2d2d2d" : "#ffffff"
            border.color: isDarkMode ? "#404040" : "#e0e0e0"
            border.width: 1
            radius: 8
            
            GridLayout {
                anchors.fill: parent
                anchors.margins: 16
                columns: 8
                rows: 12
                columnSpacing: 1
                rowSpacing: 1
                
                // 表头
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 40
                    color: isDarkMode ? "#404040" : "#f5f5f5"
                    
                    Text {
                        anchors.centerIn: parent
                        text: qsTr("时间")
                        font.pixelSize: 12
                        font.bold: true
                        color: isDarkMode ? "#ffffff" : "#000000"
                    }
                }
                
                Repeater {
                    model: [qsTr("周一"), qsTr("周二"), qsTr("周三"), qsTr("周四"), qsTr("周五"), qsTr("周六"), qsTr("周日")]
                    
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        color: isDarkMode ? "#404040" : "#f5f5f5"
                        
                        Text {
                            anchors.centerIn: parent
                            text: modelData
                            font.pixelSize: 12
                            font.bold: true
                            color: isDarkMode ? "#ffffff" : "#000000"
                        }
                    }
                }
                
                // 时间段和课程
                Repeater {
                    model: [
                        "08:00-08:45", "08:55-09:40", "10:00-10:45", "10:55-11:40",
                        "14:00-14:45", "14:55-15:40", "16:00-16:45", "16:55-17:40",
                        "19:00-19:45", "19:55-20:40", "20:50-21:35"
                    ]
                    
                    Row {
                        // 时间列
                        Rectangle {
                            width: (scheduleView.width - 32) / 8
                            height: 45
                            color: isDarkMode ? "#353535" : "#fafafa"
                            border.color: isDarkMode ? "#404040" : "#e0e0e0"
                            border.width: 1
                            
                            Text {
                                anchors.centerIn: parent
                                text: modelData
                                font.pixelSize: 10
                                color: isDarkMode ? "#cccccc" : "#666666"
                            }
                        }
                        
                        // 课程格子
                        Repeater {
                            model: 7 // 7天
                            
                            Rectangle {
                                width: (scheduleView.width - 32) / 8
                                height: 45
                                color: {
                                    // 示例课程数据
                                    if ((parent.parent.index === 0 || parent.parent.index === 1) && index === 0) {
                                        return isDarkMode ? "#1a472a" : "#e8f5e8" // 高等数学
                                    } else if ((parent.parent.index === 2 || parent.parent.index === 3) && index === 1) {
                                        return isDarkMode ? "#1e3a8a" : "#e0f2fe" // 大学英语
                                    } else if ((parent.parent.index === 4 || parent.parent.index === 5) && index === 2) {
                                        return isDarkMode ? "#7c2d12" : "#fef3e2" // 计算机科学
                                    } else {
                                        return "transparent"
                                    }
                                }
                                border.color: isDarkMode ? "#404040" : "#e0e0e0"
                                border.width: 1
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: {
                                        if ((parent.parent.parent.index === 0 || parent.parent.parent.index === 1) && index === 0) {
                                            return qsTr("高等数学\nA101")
                                        } else if ((parent.parent.parent.index === 2 || parent.parent.parent.index === 3) && index === 1) {
                                            return qsTr("大学英语\nB203")
                                        } else if ((parent.parent.parent.index === 4 || parent.parent.parent.index === 5) && index === 2) {
                                            return qsTr("计算机科学\nC301")
                                        } else {
                                            return ""
                                        }
                                    }
                                    font.pixelSize: 9
                                    color: isDarkMode ? "#ffffff" : "#000000"
                                    horizontalAlignment: Text.AlignHCenter
                                    wrapMode: Text.WordWrap
                                }
                                
                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: {
                                        // TODO: 编辑课程
                                    }
                                    onDoubleClicked: {
                                        // TODO: 添加课程
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // 课程列表
        Rectangle {
            width: parent.width
            height: 200
            color: isDarkMode ? "#2d2d2d" : "#ffffff"
            border.color: isDarkMode ? "#404040" : "#e0e0e0"
            border.width: 1
            radius: 8
            
            Column {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 16
                
                Text {
                    text: qsTr("课程列表")
                    font.pixelSize: 18
                    font.bold: true
                    color: isDarkMode ? "#ffffff" : "#000000"
                }
                
                ListView {
                    width: parent.width
                    height: parent.height - 40
                    model: coursesModel
                    
                    delegate: Rectangle {
                        width: parent.width
                        height: 40
                        color: "transparent"
                        
                        Row {
                            anchors.left: parent.left
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 20
                            
                            Text {
                                text: model.name
                                font.pixelSize: 14
                                font.bold: true
                                color: isDarkMode ? "#ffffff" : "#000000"
                                width: 100
                            }
                            
                            Text {
                                text: model.teacher
                                font.pixelSize: 14
                                color: isDarkMode ? "#cccccc" : "#666666"
                                width: 80
                            }
                            
                            Text {
                                text: model.location
                                font.pixelSize: 14
                                color: isDarkMode ? "#cccccc" : "#666666"
                                width: 100
                            }
                            
                            Text {
                                text: model.time
                                font.pixelSize: 14
                                color: isDarkMode ? "#cccccc" : "#666666"
                                width: 150
                            }
                            
                            Text {
                                text: model.weeks
                                font.pixelSize: 14
                                color: isDarkMode ? "#cccccc" : "#666666"
                                width: 80
                            }
                        }
                        
                        Row {
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 8
                            
                            Button {
                                text: qsTr("编辑")
                                flat: true
                                onClicked: {
                                    openEditCourseDialog(model)
                                }
                            }
                            
                            Button {
                                text: qsTr("删除")
                                flat: true
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

    // JavaScript 函数
    function loadCourses() {
        if (typeof timeNestBridge !== 'undefined') {
            var courses = timeNestBridge.getScheduleData()
            coursesModel.clear()
            for (var i = 0; i < courses.length; i++) {
                coursesModel.append(courses[i])
            }
        } else {
            // 如果桥接对象不可用，添加一些测试数据
            coursesModel.clear()
            coursesModel.append({
                id: 1,
                name: "高等数学",
                teacher: "张教授",
                location: "教学楼A101",
                time: "周一 08:00-09:40",
                weeks: "1-16周",
                start_week: 1,
                end_week: 16
            })
            coursesModel.append({
                id: 2,
                name: "大学英语",
                teacher: "李教授",
                location: "外语楼201",
                time: "周二 10:00-11:40",
                weeks: "1-16周",
                start_week: 1,
                end_week: 16
            })
            coursesModel.append({
                id: 3,
                name: "计算机程序设计",
                teacher: "王教授",
                location: "实验楼501",
                time: "周三 14:00-15:40",
                weeks: "2-16周",
                start_week: 2,
                end_week: 16
            })
        }
    }

    function addNewCourse() {
        if (typeof timeNestBridge !== 'undefined') {
            var success = timeNestBridge.addCourse(
                courseNameField.text.trim(),
                teacherField.text.trim(),
                locationField.text.trim(),
                timeField.text.trim(),
                startWeekSpin.value,
                endWeekSpin.value
            )
            if (success) {
                loadCourses()
                return true
            }
        }
        return false
    }

    function deleteCourse(courseId) {
        if (typeof timeNestBridge !== 'undefined') {
            timeNestBridge.deleteCourse(courseId)
            loadCourses()
        }
    }

    function clearCourseForm() {
        courseNameField.text = ""
        teacherField.text = ""
        locationField.text = ""
        timeField.text = ""
        dayCombo.currentIndex = 0
        startWeekSpin.value = 1
        endWeekSpin.value = 16
    }

    function openEditCourseDialog(course) {
        editCourseDialog.editingCourseId = course.id
        editCourseNameField.text = course.name || ""
        editTeacherField.text = course.teacher || ""
        editLocationField.text = course.location || ""
        editTimeField.text = course.time || ""

        // 设置周次
        editStartWeekSpin.value = course.start_week || 1
        editEndWeekSpin.value = course.end_week || 16

        editCourseDialog.open()
    }

    function updateCourse() {
        if (typeof timeNestBridge !== 'undefined') {
            var success = timeNestBridge.updateCourse(
                editCourseDialog.editingCourseId,
                editCourseNameField.text.trim(),
                editTeacherField.text.trim(),
                editLocationField.text.trim(),
                editTimeField.text.trim(),
                editStartWeekSpin.value,
                editEndWeekSpin.value
            )
            if (success) {
                loadCourses()
                return true
            }
        }
        return false
    }

    function createExcelTemplate() {
        if (typeof timeNestBridge !== 'undefined') {
            var success = timeNestBridge.createExcelTemplate()
            if (success) {
                console.log("Excel模板创建成功")
            }
        }
    }

    function importExcelSchedule() {
        if (typeof timeNestBridge !== 'undefined') {
            var filePath = importFilePathField.text.trim()
            if (filePath === "") {
                return false
            }

            var success = timeNestBridge.importExcelSchedule(filePath)
            if (success) {
                loadCourses()
                return true
            }
        }
        return false
    }

    function exportExcelSchedule() {
        if (typeof timeNestBridge !== 'undefined') {
            var filePath = exportFilePathField.text.trim()
            if (filePath === "") {
                return false
            }

            var success = timeNestBridge.exportExcelSchedule(filePath)
            return success
        }
        return false
    }

    function validateExcelFile(filePath) {
        if (typeof timeNestBridge !== 'undefined') {
            var result = timeNestBridge.validateExcelFile(filePath)
            return result
        }
        return { valid: false, message: "桥接对象未找到" }
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
    }
}
