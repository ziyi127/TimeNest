import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

ScrollView {
    id: settingsView

    property bool isDarkMode: false

    // 设置项状态
    property bool autoStartEnabled: false
    property bool notificationsEnabled: true
    property bool floatingWindowEnabled: true
    property bool autoHideEnabled: false
    property string currentTheme: "auto"
    
    ScrollView {
        anchors.fill: parent
        anchors.margins: 20

        Column {
            width: settingsView.width - 40
            spacing: 24
        
        Text {
            text: qsTr("设置")
            font.pixelSize: 32
            font.bold: true
            color: isDarkMode ? "#ffffff" : "#000000"
        }
        
        // 外观设置
        SettingCard {
            width: parent.width
            icon: "ic_fluent_design_ideas_20_regular"
            title: qsTr("外观设置")
            description: qsTr("应用主题和界面设置")

            ComboBox {
                id: appThemeComboBox
                model: [qsTr("浅色主题"), qsTr("深色主题"), qsTr("自动")]
                currentIndex: 0
                width: 150
                onCurrentIndexChanged: {
                    if (typeof timeNestBridge !== 'undefined') {
                        timeNestBridge.saveSetting("app_theme", currentIndex)
                    }
                }
            }
        }
        
        // 通知设置
        SettingCard {
            width: parent.width
            icon: "ic_fluent_alert_20_regular"
            title: qsTr("课程提醒")
            description: qsTr("启用课程开始前的提醒通知")

            Switch {
                checked: notificationsEnabled
                onToggled: {
                    notificationsEnabled = checked
                    if (typeof timeNestBridge !== 'undefined') {
                        timeNestBridge.saveSetting("notifications_enabled", checked)
                    }
                }
            }
        }

        SettingCard {
            width: parent.width
            icon: "ic_fluent_task_list_20_regular"
            title: qsTr("任务提醒")
            description: qsTr("启用任务截止日期提醒")

            Switch {
                checked: notificationsEnabled
                onToggled: {
                    if (typeof timeNestBridge !== 'undefined') {
                        timeNestBridge.saveSetting("task_notifications_enabled", checked)
                    }
                }
            }
        }

        SettingCard {
            width: parent.width
            icon: "ic_fluent_window_20_regular"
            title: qsTr("悬浮窗")
            description: qsTr("显示桌面悬浮窗")

            Switch {
                checked: floatingWindowEnabled
                onToggled: {
                    floatingWindowEnabled = checked
                    if (typeof timeNestBridge !== 'undefined') {
                        timeNestBridge.saveSetting("floating_window_enabled", checked)
                        if (checked) {
                            timeNestBridge.showFloatingWindow()
                        } else {
                            timeNestBridge.hideFloatingWindow()
                        }
                    }
                }
            }
        }

        SettingCard {
            width: parent.width
            icon: "ic_fluent_eye_hide_20_regular"
            title: qsTr("悬浮窗自动隐藏")
            description: qsTr("鼠标离开时自动隐藏悬浮窗")

            Switch {
                checked: autoHideEnabled
                onToggled: {
                    autoHideEnabled = checked
                    if (typeof timeNestBridge !== 'undefined') {
                        timeNestBridge.saveSetting("floating_window_auto_hide", checked)
                    }
                }
            }
        }

        // 天气设置
        SettingCard {
            width: parent.width
            icon: "ic_fluent_weather_sunny_20_regular"
            title: qsTr("天气城市")
            description: qsTr("设置天气显示的城市")

            TextField {
                id: cityField
                width: 200
                placeholderText: qsTr("请输入城市名称，如：北京")
                text: "北京"  // 默认值，组件加载后再设置

                Component.onCompleted: {
                    if (typeof timeNestBridge !== 'undefined') {
                        text = timeNestBridge.getSetting("weather_city", "北京")
                    }
                }

                onTextChanged: {
                    if (typeof timeNestBridge !== 'undefined') {
                        timeNestBridge.saveSetting("weather_city", text)
                        timeNestBridge.updateWeatherData(text)
                    }
                }
            }
        }

        SettingCard {
            width: parent.width
            icon: "ic_fluent_weather_cloudy_20_regular"
            title: qsTr("天气显示")
            description: qsTr("在悬浮窗中显示天气信息")

            Switch {
                id: weatherEnabledCheckBox
                checked: true  // 默认值，组件加载后再设置

                Component.onCompleted: {
                    if (typeof timeNestBridge !== 'undefined') {
                        checked = timeNestBridge.getSetting("weather_enabled", true)
                    }
                }

                onToggled: {
                    if (typeof timeNestBridge !== 'undefined') {
                        timeNestBridge.saveSetting("weather_enabled", checked)
                        timeNestBridge.setWeatherEnabled(checked)
                    }
                }
            }
        }

        // 关于
        SettingCard {
            width: parent.width
            icon: "ic_fluent_info_20_regular"
            title: qsTr("关于 TimeNest")
            description: qsTr("TimeNest v2.0.0 Preview\n基于 RinUI 的现代化时间管理工具")

            Button {
                text: qsTr("查看详细信息")
                icon.name: "ic_fluent_info_20_regular"
                onClicked: {
                    showAboutDialog()
                }
            }
        }

        // 设置操作
        RowLayout {
            width: parent.width
            spacing: 16

            Button {
                text: qsTr("导出设置")
                icon.name: "ic_fluent_arrow_export_20_regular"
                onClicked: exportSettings()
            }

            Button {
                text: qsTr("导入设置")
                icon.name: "ic_fluent_arrow_import_20_regular"
                onClicked: importSettings()
            }

            Button {
                text: qsTr("重置设置")
                icon.name: "ic_fluent_arrow_reset_20_regular"
                onClicked: resetSettings()
            }
            }
        }

    // JavaScript 函数
    function saveSetting(key, value) {
        if (typeof timeNestBridge !== 'undefined') {
            timeNestBridge.saveSetting(key, value)
        }
    }

    function getSetting(key, defaultValue) {
        if (typeof timeNestBridge !== 'undefined') {
            try {
                return timeNestBridge.getSetting(key, defaultValue)
            } catch (e) {
                console.log("获取设置失败:", key, e)
            }
        }
        return defaultValue
    }

    function loadSetting(key, defaultValue) {
        if (typeof timeNestBridge !== 'undefined') {
            var value = timeNestBridge.loadSetting(key)
            return value !== null && value !== undefined ? value : defaultValue
        }
        return defaultValue
    }

    function loadSettings() {
        try {
            var autoStart = loadSetting("auto_start_enabled", false)
            var notifications = loadSetting("notifications_enabled", true)
            var floatingWindow = loadSetting("floating_window_enabled", true)
            var autoHide = loadSetting("floating_window_auto_hide", false)
            var theme = loadSetting("theme_mode", "auto")

            // 安全地设置属性
            autoStartEnabled = typeof autoStart === 'boolean' ? autoStart : false
            notificationsEnabled = typeof notifications === 'boolean' ? notifications : true
            floatingWindowEnabled = typeof floatingWindow === 'boolean' ? floatingWindow : true
            autoHideEnabled = typeof autoHide === 'boolean' ? autoHide : false
            currentTheme = typeof theme === 'string' ? theme : "auto"

            // 更新UI状态
            updateThemeComboBox()
        } catch (e) {
            console.error("加载设置失败:", e)
        }
    }

    function updateThemeComboBox() {
        try {
            if (typeof appThemeComboBox !== 'undefined') {
                switch(currentTheme) {
                    case "dark":
                        appThemeComboBox.currentIndex = 0
                        break
                    case "light":
                        appThemeComboBox.currentIndex = 1
                        break
                    case "auto":
                    default:
                        appThemeComboBox.currentIndex = 2
                        break
                }
            }
        } catch (e) {
            console.error("更新主题ComboBox失败:", e)
        }
    }

    function exportSettings() {
        if (typeof timeNestBridge !== 'undefined') {
            // TODO: 实现设置导出功能
            timeNestBridge.showNotification("导出设置", "设置导出功能待实现")
        }
    }

    function importSettings() {
        if (typeof timeNestBridge !== 'undefined') {
            // TODO: 实现设置导入功能
            timeNestBridge.showNotification("导入设置", "设置导入功能待实现")
        }
    }

    function resetSettings() {
        if (typeof timeNestBridge !== 'undefined') {
            // 重置所有设置为默认值
            autoStartEnabled = false
            notificationsEnabled = true
            floatingWindowEnabled = true
            autoHideEnabled = false
            currentTheme = "auto"

            // 保存重置后的设置
            saveSetting("auto_start_enabled", autoStartEnabled)
            saveSetting("notifications_enabled", notificationsEnabled)
            saveSetting("floating_window_enabled", floatingWindowEnabled)
            saveSetting("floating_window_auto_hide", autoHideEnabled)
            saveSetting("theme_mode", currentTheme)

            // 更新UI
            updateThemeComboBox()

            timeNestBridge.showNotification("重置设置", "所有设置已重置为默认值")
        }
    }

    function showAboutDialog() {
        if (typeof timeNestBridge !== 'undefined') {
            // TODO: 显示关于对话框
            timeNestBridge.showNotification("关于", "TimeNest - 现代化时间管理工具")
        }
    }

    // 组件加载完成时加载设置
    Component.onCompleted: {
        loadSettings()
        }
    }
}
