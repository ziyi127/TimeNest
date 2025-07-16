pragma Singleton
import QtQuick
import RinUI

QtObject {
    id: unifiedComponents
    
    // 统一的Button组件
    component UnifiedButton: RinUI.Button {
        property string variant: "primary" // primary, secondary, outline, text
        property string size: "normal" // small, normal, large
        
        // 根据变体设置样式
        color: {
            switch(variant) {
                case "primary": return UITheme.colors.primary
                case "secondary": return UITheme.colors.secondary
                case "outline": return "transparent"
                case "text": return "transparent"
                default: return UITheme.colors.primary
            }
        }
        
        // 根据大小设置尺寸
        height: {
            switch(size) {
                case "small": return 28
                case "normal": return UITheme.sizes.buttonHeight
                case "large": return 44
                default: return UITheme.sizes.buttonHeight
            }
        }
        
        font.pixelSize: {
            switch(size) {
                case "small": return UITheme.fonts.small
                case "normal": return UITheme.fonts.normal
                case "large": return UITheme.fonts.medium
                default: return UITheme.fonts.normal
            }
        }
    }
    
    // 统一的Switch组件
    component UnifiedSwitch: RinUI.Switch {
        property string size: "normal" // small, normal, large
        
        // 统一样式
        font.pixelSize: UITheme.fonts.normal
        font.family: UITheme.fonts.family
    }
    
    // 统一的CheckBox组件
    component UnifiedCheckBox: RinUI.CheckBox {
        property string size: "normal" // small, normal, large
        
        // 统一样式
        font.pixelSize: UITheme.fonts.normal
        font.family: UITheme.fonts.family
    }
    
    // 统一的TextField组件
    component UnifiedTextField: RinUI.TextField {
        property string variant: "outlined" // filled, outlined
        
        height: UITheme.sizes.inputHeight
        font.pixelSize: UITheme.fonts.normal
        font.family: UITheme.fonts.family
    }
    
    // 统一的ComboBox组件
    component UnifiedComboBox: RinUI.ComboBox {
        height: UITheme.sizes.inputHeight
        font.pixelSize: UITheme.fonts.normal
        font.family: UITheme.fonts.family
    }
    
    // 统一的Card组件
    component UnifiedCard: Rectangle {
        property alias content: contentLoader.sourceComponent
        property string title: ""
        property string subtitle: ""
        property bool elevated: true
        
        color: UITheme.colors.surface
        radius: UITheme.radius.normal
        border.color: UITheme.colors.border
        border.width: elevated ? 0 : 1
        
        // 阴影效果（简化版）
        Rectangle {
            anchors.fill: parent
            anchors.topMargin: elevated ? 2 : 0
            anchors.leftMargin: elevated ? 2 : 0
            color: UITheme.colors.border
            radius: parent.radius
            opacity: elevated ? 0.1 : 0
            z: -1
        }
        
        Column {
            anchors.fill: parent
            anchors.margins: UITheme.spacing.medium
            spacing: UITheme.spacing.small
            
            // 标题区域
            Column {
                width: parent.width
                spacing: UITheme.spacing.xs
                visible: title !== ""
                
                Text {
                    text: title
                    font.pixelSize: UITheme.fonts.medium
                    font.bold: true
                    color: UITheme.colors.onSurface
                    font.family: UITheme.fonts.family
                }
                
                Text {
                    text: subtitle
                    font.pixelSize: UITheme.fonts.small
                    color: UITheme.colors.onSurface
                    opacity: 0.7
                    font.family: UITheme.fonts.family
                    visible: subtitle !== ""
                }
            }
            
            // 内容区域
            Loader {
                id: contentLoader
                width: parent.width
            }
        }
    }
    
    // 统一的SettingCard组件（基于RinUI.SettingCard）
    component UnifiedSettingCard: RinUI.SettingCard {
        // 继承RinUI.SettingCard的所有功能
        // 可以在这里添加统一的样式覆盖
    }
    
    // 统一的Dialog组件
    component UnifiedDialog: RinUI.Dialog {
        // 统一的对话框样式
        width: 400
        height: 300
    }
    
    // 统一的ProgressBar组件
    component UnifiedProgressBar: RinUI.ProgressBar {
        height: 8
        // 统一的进度条样式
    }
    
    // 统一的Slider组件
    component UnifiedSlider: RinUI.Slider {
        height: 20
        // 统一的滑块样式
    }
    
    // 统一的SpinBox组件
    component UnifiedSpinBox: RinUI.SpinBox {
        height: UITheme.sizes.inputHeight
        font.pixelSize: UITheme.fonts.normal
        font.family: UITheme.fonts.family
    }
}
