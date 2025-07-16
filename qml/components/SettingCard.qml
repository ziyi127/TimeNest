import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

RinCard {
    id: settingCard
    
    property string icon: ""
    property string title: ""
    property string description: ""
    property alias content: contentArea.children
    property bool isDarkMode: false
    
    width: parent.width
    height: Math.max(80, contentColumn.implicitHeight + 32)
    radius: 8
    
    Column {
        id: contentColumn
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12
        
        Row {
            width: parent.width
            spacing: 12
            
            RinIcon {
                icon: settingCard.icon
                size: 24
                color: "#2196f3"
                anchors.verticalCenter: parent.verticalCenter
                visible: settingCard.icon !== ""
            }
            
            Column {
                anchors.verticalCenter: parent.verticalCenter
                spacing: 4
                width: parent.width - (settingCard.icon !== "" ? 48 : 12) - contentArea.width
                
                Text {
                    text: settingCard.title
                    font.pixelSize: 16
                    font.bold: true
                    color: isDarkMode ? "#ffffff" : "#000000"
                    width: parent.width
                    wrapMode: Text.WordWrap
                }
                
                Text {
                    text: settingCard.description
                    font.pixelSize: 14
                    color: isDarkMode ? "#cccccc" : "#666666"
                    width: parent.width
                    wrapMode: Text.WordWrap
                    visible: settingCard.description !== ""
                }
            }
            
            Item {
                Layout.fillWidth: true
            }
            
            Item {
                id: contentArea
                width: childrenRect.width
                height: childrenRect.height
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }
}
