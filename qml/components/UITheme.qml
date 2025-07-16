pragma Singleton
import QtQuick

QtObject {
    id: uiTheme
    
    // 主题模式
    property bool isDarkMode: false
    
    // 颜色配置
    readonly property QtObject colors: QtObject {
        // 主色调
        property color primary: "#2196F3"
        property color primaryVariant: "#1976D2"
        property color secondary: "#FF9800"
        property color secondaryVariant: "#F57C00"
        
        // 背景色
        property color background: isDarkMode ? "#1e1e1e" : "#f5f5f5"
        property color surface: isDarkMode ? "#2d2d2d" : "#ffffff"
        property color card: isDarkMode ? "#333333" : "#ffffff"
        
        // 文本色
        property color onBackground: isDarkMode ? "#ffffff" : "#000000"
        property color onSurface: isDarkMode ? "#ffffff" : "#000000"
        property color onPrimary: "#ffffff"
        property color onSecondary: "#000000"
        
        // 边框色
        property color border: isDarkMode ? "#404040" : "#e0e0e0"
        property color divider: isDarkMode ? "#404040" : "#e0e0e0"
        
        // 状态色
        property color success: "#4CAF50"
        property color warning: "#FF9800"
        property color error: "#F44336"
        property color info: "#2196F3"
        
        // 悬停和选中状态
        property color hover: isDarkMode ? "#404040" : "#f0f0f0"
        property color selected: "#e3f2fd"
        property color pressed: isDarkMode ? "#505050" : "#e0e0e0"
    }
    
    // 字体配置
    readonly property QtObject fonts: QtObject {
        property string family: "MiSans-Light"
        property int small: 12
        property int normal: 14
        property int medium: 16
        property int large: 18
        property int xlarge: 24
        property int xxlarge: 32
    }
    
    // 间距配置
    readonly property QtObject spacing: QtObject {
        property int xs: 4
        property int small: 8
        property int normal: 12
        property int medium: 16
        property int large: 20
        property int xlarge: 24
        property int xxlarge: 32
    }
    
    // 圆角配置
    readonly property QtObject radius: QtObject {
        property int small: 4
        property int normal: 8
        property int medium: 12
        property int large: 16
    }
    
    // 阴影配置
    readonly property QtObject shadow: QtObject {
        property int small: 2
        property int normal: 4
        property int medium: 8
        property int large: 16
    }
    
    // 动画配置
    readonly property QtObject animation: QtObject {
        property int fast: 150
        property int normal: 250
        property int slow: 350
        property int verySlow: 500
    }
    
    // 组件尺寸配置
    readonly property QtObject sizes: QtObject {
        property int buttonHeight: 36
        property int inputHeight: 40
        property int cardMinHeight: 80
        property int sidebarWidth: 280
        property int iconSize: 20
        property int avatarSize: 40
    }
    
    // 切换主题模式
    function toggleTheme() {
        isDarkMode = !isDarkMode
    }
    
    // 设置主题模式
    function setTheme(dark) {
        isDarkMode = dark
    }
    
    // 获取状态颜色
    function getStatusColor(status) {
        switch(status) {
            case "success": return colors.success
            case "warning": return colors.warning
            case "error": return colors.error
            case "info": return colors.info
            default: return colors.primary
        }
    }
    
    // 获取优先级颜色
    function getPriorityColor(priority) {
        switch(priority) {
            case "high": return colors.error
            case "medium": return colors.warning
            case "low": return colors.success
            default: return colors.primary
        }
    }
}
