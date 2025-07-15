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
                // TODO: 打开新建课程对话框
            }
        }
        
        MenuItem {
            text: qsTr("新建任务")
            onTriggered: {
                // TODO: 打开新建任务对话框
            }
        }
        
        MenuSeparator {}
        
        MenuItem {
            text: qsTr("导入数据")
            onTriggered: {
                if (typeof timeNestBridge !== 'undefined') {
                    // TODO: 打开文件选择对话框
                    // timeNestBridge.importData(filePath)
                }
            }
        }
        
        MenuItem {
            text: qsTr("导出数据")
            onTriggered: {
                if (typeof timeNestBridge !== 'undefined') {
                    // TODO: 打开文件保存对话框
                    // timeNestBridge.exportData(filePath)
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
                // TODO: 切换全屏模式
            }
        }
    }
    
    Menu {
        title: qsTr("工具")
        
        MenuItem {
            text: qsTr("插件管理")
            onTriggered: {
                // TODO: 切换到插件页面
            }
        }
        
        MenuItem {
            text: qsTr("主题管理")
            onTriggered: {
                // TODO: 切换到设置页面的主题部分
            }
        }
        
        MenuSeparator {}
        
        MenuItem {
            text: qsTr("时间校准")
            onTriggered: {
                // TODO: 打开时间校准对话框
            }
        }
        
        MenuItem {
            text: qsTr("系统信息")
            onTriggered: {
                // TODO: 显示系统信息
            }
        }
    }
    
    Menu {
        title: qsTr("帮助")
        
        MenuItem {
            text: qsTr("用户手册")
            onTriggered: {
                // TODO: 打开用户手册
            }
        }
        
        MenuItem {
            text: qsTr("快捷键")
            onTriggered: {
                // TODO: 显示快捷键帮助
            }
        }
        
        MenuSeparator {}
        
        MenuItem {
            text: qsTr("检查更新")
            onTriggered: {
                // TODO: 检查应用更新
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
