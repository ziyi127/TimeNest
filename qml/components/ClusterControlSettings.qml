import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import RinUI

// 集群控制设置组件
Item {
    id: clusterControlSettings
    
    // 属性
    property bool clusterEnabled: false
    property string clusterId: ""
    property string managerUrl: ""
    
    // 信号
    signal clusterEnabledChanged(bool enabled)
    signal managerUrlChanged(string url)
    
    // 初始化
    Component.onCompleted: {
        // 从后端获取集群控制状态
        clusterEnabled = bridge.isClusterControlEnabled()
        clusterId = bridge.getClusterId()
        managerUrl = bridge.getClusterManagerUrl()
    }
    
    ColumnLayout {
        anchors.fill: parent
        spacing: 10
        
        // 标题
        Text {
            text: "集群控制设置"
            font.pixelSize: 18
            font.bold: true
            Layout.fillWidth: true
        }
        
        // 分割线
        Rectangle {
            height: 1
            color: "#e0e0e0"
            Layout.fillWidth: true
        }
        
        // 启用开关
        RowLayout {
            Layout.fillWidth: true
            spacing: 10
            
            Text {
                text: "启用集群控制"
                Layout.fillWidth: true
            }
            
            Switch {
                id: enableSwitch
                checked: clusterControlSettings.clusterEnabled
                onCheckedChanged: {
                    // 更新后端状态
                    if (bridge.setClusterControlEnabled(checked)) {
                        clusterControlSettings.clusterEnabled = checked
                        clusterControlSettings.clusterEnabledChanged(checked)
                    } else {
                        // 如果设置失败，恢复开关状态
                        checked = clusterControlSettings.clusterEnabled
                    }
                }
            }
        }
        
        // 集群ID显示
        RowLayout {
            Layout.fillWidth: true
            spacing: 10
            enabled: clusterControlSettings.clusterEnabled
            opacity: enabled ? 1.0 : 0.5
            
            Text {
                text: "集群ID"
                Layout.fillWidth: true
            }
            
            TextField {
                id: clusterIdField
                text: clusterControlSettings.clusterId
                readOnly: true
                Layout.preferredWidth: 250
                selectByMouse: true
                
                // 复制按钮
                Button {
                    anchors.right: parent.right
                    anchors.rightMargin: 5
                    anchors.verticalCenter: parent.verticalCenter
                    width: 24
                    height: 24
                    text: "📋"
                    
                    onClicked: {
                        clusterIdField.selectAll()
                        clusterIdField.copy()
                        clusterIdField.deselect()
                        
                        // 显示复制成功提示
                        copyTooltip.visible = true
                        copyTimer.restart()
                    }
                    
                    // 复制成功提示
                    ToolTip {
                        id: copyTooltip
                        text: "已复制到剪贴板"
                        visible: false
                        timeout: 2000
                    }
                    
                    // 自动隐藏计时器
                    Timer {
                        id: copyTimer
                        interval: 2000
                        onTriggered: copyTooltip.visible = false
                    }
                }
            }
        }
        
        // 管理器URL设置
        RowLayout {
            Layout.fillWidth: true
            spacing: 10
            enabled: clusterControlSettings.clusterEnabled
            opacity: enabled ? 1.0 : 0.5
            
            Text {
                text: "管理器URL"
                Layout.fillWidth: true
            }
            
            TextField {
                id: managerUrlField
                text: clusterControlSettings.managerUrl
                placeholderText: "ws://localhost:8765"
                Layout.preferredWidth: 250
                selectByMouse: true
                
                onEditingFinished: {
                    if (text !== clusterControlSettings.managerUrl) {
                        // 更新后端状态
                        if (bridge.setClusterManagerUrl(text)) {
                            clusterControlSettings.managerUrl = text
                            clusterControlSettings.managerUrlChanged(text)
                        } else {
                            // 如果设置失败，恢复文本
                            text = clusterControlSettings.managerUrl
                        }
                    }
                }
            }
        }
        
        // 状态信息
        GroupBox {
            title: "集群状态"
            Layout.fillWidth: true
            enabled: clusterControlSettings.clusterEnabled
            opacity: enabled ? 1.0 : 0.5
            
            ColumnLayout {
                anchors.fill: parent
                spacing: 5
                
                // 状态信息
                Text {
                    text: clusterControlSettings.clusterEnabled ? 
                          "集群控制已启用" : "集群控制已禁用"
                    color: clusterControlSettings.clusterEnabled ? "green" : "gray"
                    font.bold: true
                }
                
                // 连接状态
                Text {
                    text: "连接状态: " + (clusterControlSettings.clusterEnabled ? "已预留接口" : "未连接")
                    color: clusterControlSettings.clusterEnabled ? "blue" : "gray"
                }
                
                // 说明文本
                Text {
                    text: "集群控制功能允许多个TimeNest实例连接到中央管理系统，实现统一管理和监控。"
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
                
                // 文档链接
                Text {
                    text: "<a href='https://github.com/ziyi127/TimeNest/blob/main/cluster_interface.py'>查看集群控制接口文档</a>"
                    onLinkActivated: Qt.openUrlExternally(link)
                    color: "blue"
                    MouseArea {
                        anchors.fill: parent
                        acceptedButtons: Qt.NoButton
                        cursorShape: parent.hoveredLink ? Qt.PointingHandCursor : Qt.ArrowCursor
                    }
                }
            }
        }
        
        // 填充空间
        Item {
            Layout.fillHeight: true
        }
    }
}
