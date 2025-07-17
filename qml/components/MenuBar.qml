import QtQuick
import QtQuick.Controls

MenuBar {
    id: menuBar
    
    property bool isDarkMode: true
    
    Menu {
        title: qsTr("文件")
        
        MenuItem {
            text: qsTr("新建课程")
            onTriggered: {
                if (typeof timeNestBridge !== 'undefined') {
                    timeNestBridge.showNewCourseDialog()
                }
            }
        }

        MenuItem {
            text: qsTr("新建任务")
            onTriggered: {
                if (typeof timeNestBridge !== 'undefined') {
                    timeNestBridge.showNewTaskDialog()
                }
            }
        }
        
        MenuSeparator {}
        
        MenuItem {
            text: qsTr("导入Excel")
            onTriggered: {
                if (typeof timeNestBridge !== 'undefined') {
                    timeNestBridge.importExcelFile()
                }
            }
        }

        MenuItem {
            text: qsTr("导出Excel")
            onTriggered: {
                if (typeof timeNestBridge !== 'undefined') {
                    timeNestBridge.exportExcelFile()
                }
            }
        }
        
        MenuSeparator {}
        
        MenuItem {
            text: qsTr("退出")
            onTriggered: {
                if (typeof timeNestBridge !== 'undefined') {
                    timeNestBridge.exitApplication()
                }
            }
        }
    }
    
    Menu {
        title: qsTr("编辑")
        
        MenuItem {
            text: qsTr("偏好设置")
            onTriggered: {
                // TODO: 切换到设置页面
            }
        }
        
        MenuSeparator {}
        
        MenuItem {
            text: qsTr("备份数据")
            onTriggered: {
                if (typeof timeNestBridge !== 'undefined') {
                    var success = timeNestBridge.backupData()
                    if (success) {
                        timeNestBridge.showNotification(qsTr("备份成功"), qsTr("数据已成功备份"))
                    } else {
                        timeNestBridge.showNotification(qsTr("备份失败"), qsTr("数据备份失败，请重试"))
                    }
                }
            }
        }
        
        MenuItem {
            text: qsTr("恢复数据")
            onTriggered: {
                if (typeof timeNestBridge !== 'undefined') {
                    var success = timeNestBridge.restoreData()
                    if (success) {
                        timeNestBridge.showNotification(qsTr("恢复成功"), qsTr("数据已成功恢复"))
                    } else {
                        timeNestBridge.showNotification(qsTr("恢复失败"), qsTr("数据恢复失败，请重试"))
                    }
                }
            }
        }
    }
    
    Menu {
        title: qsTr("视图")
        
        MenuItem {
            text: qsTr("显示悬浮窗")
            checkable: true
            checked: typeof timeNestBridge !== 'undefined' ? timeNestBridge.isFloatingWindowVisible() : false
            onTriggered: {
                if (typeof timeNestBridge !== 'undefined') {
                    timeNestBridge.toggleFloatingWindow()
                }
            }
        }
        
        MenuItem {
            text: qsTr("最小化到托盘")
            onTriggered: {
                if (typeof timeNestBridge !== 'undefined') {
                    timeNestBridge.minimizeToTray()
                }
            }
        }
        
        MenuSeparator {}
        
        MenuItem {
            text: qsTr("全屏")
            checkable: true
            onTriggered: {
                if (typeof timeNestBridge !== 'undefined') {
                    timeNestBridge.toggleFullScreen()
                }
            }
        }
    }
    
    Menu {
        title: qsTr("工具")
        
        MenuItem {
            text: qsTr("插件管理")
            onTriggered: {
                if (typeof timeNestBridge !== 'undefined') {
                    timeNestBridge.showPluginManager()
                }
            }
        }

        MenuItem {
            text: qsTr("主题管理")
            onTriggered: {
                if (typeof timeNestBridge !== 'undefined') {
                    timeNestBridge.showThemeManager()
                }
            }
        }
        
        MenuSeparator {}
        
        MenuItem {
            text: qsTr("时间校准")
            onTriggered: {
                if (typeof timeNestBridge !== 'undefined') {
                    timeNestBridge.calibrateTime()
                }
            }
        }

        MenuItem {
            text: qsTr("系统信息")
            onTriggered: {
                if (typeof timeNestBridge !== 'undefined') {
                    timeNestBridge.showSystemInfo()
                }
            }
        }
    }
    
    Menu {
        title: qsTr("帮助")
        
        MenuItem {
            text: qsTr("用户手册")
            onTriggered: {
                if (typeof timeNestBridge !== 'undefined') {
                    timeNestBridge.openUserManual()
                }
            }
        }

        MenuItem {
            text: qsTr("快捷键")
            onTriggered: {
                if (typeof timeNestBridge !== 'undefined') {
                    timeNestBridge.showShortcuts()
                }
            }
        }
        
        MenuSeparator {}
        
        MenuItem {
            text: qsTr("检查更新")
            onTriggered: {
                if (typeof timeNestBridge !== 'undefined') {
                    timeNestBridge.checkForUpdates()
                }
            }
        }
        
        MenuItem {
            text: qsTr("关于 TimeNest")
            onTriggered: {
                if (typeof parent.parent.parent.showAboutDialog === 'function') {
                    parent.parent.parent.showAboutDialog()
                }
            }
        }
    }
}
