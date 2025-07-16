import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

ScrollView {
    id: pluginsView

    property bool isDarkMode: false
    property var pluginsModel: ListModel {}
    
    Column {
        width: pluginsView.width
        spacing: 24
        
        Text {
            text: qsTr("插件市场")
            font.pixelSize: 32
            font.bold: true
            color: isDarkMode ? "#ffffff" : "#000000"
        }
        
        RinResponsiveRow {
            width: parent.width
            spacing: 16

            RinCard {
                Layout.fillWidth: true
                Layout.preferredHeight: 100
                radius: 8

                Column {
                    anchors.centerIn: parent
                    spacing: 8

                    RinIcon {
                        icon: "extension"
                        size: 24
                        color: "#2196f3"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: getInstalledPluginsCount().toString()
                        font.pixelSize: 24
                        font.bold: true
                        color: "#2196f3"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: qsTr("已安装插件")
                        font.pixelSize: 14
                        color: isDarkMode ? "#cccccc" : "#666666"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }

            RinCard {
                Layout.fillWidth: true
                Layout.preferredHeight: 100
                radius: 8

                Column {
                    anchors.centerIn: parent
                    spacing: 8

                    RinIcon {
                        icon: "cloud_download"
                        size: 24
                        color: "#4caf50"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: getAvailablePluginsCount().toString()
                        font.pixelSize: 24
                        font.bold: true
                        color: "#4caf50"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: qsTr("可用插件")
                        font.pixelSize: 14
                        color: isDarkMode ? "#cccccc" : "#666666"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }

            RinCard {
                Layout.fillWidth: true
                Layout.preferredHeight: 100
                radius: 8

                Column {
                    anchors.centerIn: parent
                    spacing: 8

                    RinIcon {
                        icon: "update"
                        size: 24
                        color: "#ff9800"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: getEnabledPluginsCount().toString()
                        font.pixelSize: 24
                        font.bold: true
                        color: "#ff9800"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: qsTr("已启用")
                        font.pixelSize: 14
                        color: isDarkMode ? "#cccccc" : "#666666"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }
        }

        // 插件列表
        Rectangle {
            width: parent.width
            height: 400
            color: isDarkMode ? "#2d2d2d" : "#ffffff"
            border.color: isDarkMode ? "#404040" : "#e0e0e0"
            border.width: 1
            radius: 8

            Column {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 16

                Row {
                    width: parent.width
                    spacing: 16

                    Text {
                        text: qsTr("已安装插件")
                        font.pixelSize: 18
                        font.bold: true
                        color: isDarkMode ? "#ffffff" : "#000000"
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Item { Layout.fillWidth: true }

                    Button {
                        text: qsTr("浏览市场")
                        highlighted: true
                        onClicked: {
                            // TODO: 打开插件市场
                        }
                    }

                    Button {
                        text: qsTr("安装本地插件")
                        onClicked: {
                            // TODO: 安装本地插件
                        }
                    }
                }

                ListView {
                    width: parent.width
                    height: parent.height - 60
                    model: ListModel {
                        ListElement {
                            name: "天气插件"
                            description: "显示实时天气信息"
                            version: "1.2.0"
                            author: "TimeNest Team"
                            enabled: true
                            hasUpdate: false
                        }
                        ListElement {
                            name: "番茄钟插件"
                            description: "番茄工作法计时器"
                            version: "2.1.0"
                            author: "Community"
                            enabled: true
                            hasUpdate: true
                        }
                        ListElement {
                            name: "课程提醒插件"
                            description: "智能课程提醒功能"
                            version: "1.0.5"
                            author: "TimeNest Team"
                            enabled: false
                            hasUpdate: false
                        }
                        ListElement {
                            name: "日历同步插件"
                            description: "与系统日历同步"
                            version: "1.3.2"
                            author: "Community"
                            enabled: true
                            hasUpdate: true
                        }
                    }

                    delegate: Rectangle {
                        width: parent.width
                        height: 80
                        color: "transparent"

                        Rectangle {
                            anchors.fill: parent
                            anchors.margins: 4
                            color: isDarkMode ? "#353535" : "#f9f9f9"
                            radius: 6

                            Row {
                                anchors.left: parent.left
                                anchors.verticalCenter: parent.verticalCenter
                                anchors.leftMargin: 16
                                spacing: 16

                                Rectangle {
                                    width: 40
                                    height: 40
                                    color: model.enabled ? "#4caf50" : "#9e9e9e"
                                    radius: 20
                                    anchors.verticalCenter: parent.verticalCenter

                                    Text {
                                        anchors.centerIn: parent
                                        text: "🧩"
                                        font.pixelSize: 20
                                    }
                                }

                                Column {
                                    spacing: 4
                                    anchors.verticalCenter: parent.verticalCenter

                                    Text {
                                        text: model.name
                                        font.pixelSize: 16
                                        font.bold: true
                                        color: isDarkMode ? "#ffffff" : "#000000"
                                    }

                                    Text {
                                        text: model.description
                                        font.pixelSize: 14
                                        color: isDarkMode ? "#cccccc" : "#666666"
                                    }

                                    Text {
                                        text: qsTr("版本 ") + model.version + qsTr(" - ") + model.author
                                        font.pixelSize: 12
                                        color: isDarkMode ? "#999999" : "#888888"
                                    }
                                }
                            }

                            Row {
                                anchors.right: parent.right
                                anchors.verticalCenter: parent.verticalCenter
                                anchors.rightMargin: 16
                                spacing: 8

                                Rectangle {
                                    visible: model.hasUpdate
                                    width: 60
                                    height: 24
                                    color: "#ff9800"
                                    radius: 12

                                    Text {
                                        anchors.centerIn: parent
                                        text: qsTr("更新")
                                        font.pixelSize: 12
                                        color: "#ffffff"
                                    }
                                }

                                Switch {
                                    checked: model.enabled
                                    onClicked: {
                                        togglePlugin(model.id, checked)
                                    }
                                }

                                Button {
                                    text: qsTr("设置")
                                    flat: true
                                    enabled: model.enabled
                                    onClicked: {
                                        openPluginSettings(model.id)
                                    }
                                }

                                Button {
                                    text: qsTr("卸载")
                                    flat: true
                                    onClicked: {
                                        uninstallPlugin(model.id)
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
    function loadPlugins() {
        if (typeof timeNestBridge !== 'undefined') {
            var plugins = timeNestBridge.getPluginsData()
            pluginsModel.clear()
            for (var i = 0; i < plugins.length; i++) {
                pluginsModel.append(plugins[i])
            }
        }
    }

    function getInstalledPluginsCount() {
        return pluginsModel.count
    }

    function getEnabledPluginsCount() {
        var count = 0
        for (var i = 0; i < pluginsModel.count; i++) {
            if (pluginsModel.get(i).enabled) {
                count++
            }
        }
        return count
    }

    function getAvailablePluginsCount() {
        if (typeof timeNestBridge !== 'undefined') {
            try {
                return timeNestBridge.getAvailablePluginsCount()
            } catch (e) {
                console.log("获取可用插件数量失败:", e)
            }
        }
        return 0
    }

    function loadAvailablePlugins() {
        if (typeof timeNestBridge !== 'undefined') {
            try {
                console.log("正在从插件仓库加载插件...")
                var availablePlugins = timeNestBridge.getAvailablePlugins()
                // 这里可以显示可用插件列表
                console.log("可用插件:", availablePlugins)
                return availablePlugins
            } catch (e) {
                console.log("加载可用插件失败:", e)
                // 显示错误提示
                if (typeof timeNestBridge.showNotification !== 'undefined') {
                    timeNestBridge.showNotification("插件管理", "无法连接到插件仓库")
                }
            }
        }
        return []
    }

    function installPlugin(pluginId, pluginUrl) {
        if (typeof timeNestBridge !== 'undefined') {
            try {
                console.log("安装插件:", pluginId, pluginUrl)
                var success = timeNestBridge.installPlugin(pluginId, pluginUrl)
                if (success) {
                    console.log("插件安装成功")
                    loadPlugins()
                    // 显示成功提示
                    if (typeof timeNestBridge.showNotification !== 'undefined') {
                        timeNestBridge.showNotification("插件管理", "插件安装成功")
                    }
                } else {
                    console.log("插件安装失败")
                    // 显示错误提示
                    if (typeof timeNestBridge.showNotification !== 'undefined') {
                        timeNestBridge.showNotification("插件管理", "插件安装失败")
                    }
                }
            } catch (e) {
                console.log("安装插件异常:", e)
            }
        }
    }

    function togglePlugin(pluginId, enabled) {
        if (typeof timeNestBridge !== 'undefined') {
            timeNestBridge.togglePlugin(pluginId, enabled)
            loadPlugins()
        }
    }

    function openPluginSettings(pluginId) {
        if (typeof timeNestBridge !== 'undefined') {
            timeNestBridge.openPluginSettings(pluginId)
        }
    }

    function uninstallPlugin(pluginId) {
        if (typeof timeNestBridge !== 'undefined') {
            timeNestBridge.uninstallPlugin(pluginId)
            loadPlugins()
        }
    }

    function refreshPlugins() {
        loadPlugins()
    }

    // 组件加载完成时加载插件
    Component.onCompleted: {
        loadPlugins()
    }

    // 监听插件变化信号
    Connections {
        target: typeof timeNestBridge !== 'undefined' ? timeNestBridge : null
        function onPluginsChanged() {
            loadPlugins()
        }
    }
}
