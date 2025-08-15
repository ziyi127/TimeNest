# TimeNest 天气服务配置与使用文档

## 概述

TimeNest 天气服务允许用户获取实时天气信息，并支持通过配置文件自定义 API 密钥和位置设置。该服务使用中国气象局官方数据，通过接口盒子提供的 API 获取天气信息。

## 配置文件

天气服务的配置存储在 `data/weather_config.json` 文件中。该文件包含以下字段：

```json
{
  "api_id": "your_api_id",
  "api_key": "your_api_key",
  "location": "四川,绵阳",
  "update_interval": 3600,
  "unit": "metric",
  "enabled": true
}
```

### 字段说明

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| api_id | string | 否 | 接口盒子的用户ID，如果未提供则使用公共ID |
| api_key | string | 否 | 接口盒子的API密钥，如果未提供则使用公共KEY |
| location | string | 是 | 天气查询位置，格式为"省份,城市" |
| update_interval | integer | 否 | 天气数据更新间隔（秒），默认3600秒（1小时） |
| unit | string | 否 | 温度单位，"metric"表示摄氏度，"imperial"表示华氏度，默认为"metric" |
| enabled | boolean | 否 | 是否启用天气服务，默认为true |

## 获取接口盒子 API 密钥

1. 访问接口盒子官网：http://www.apihz.cn
2. 注册账户并登录
3. 在用户中心的个人资料页面获取您的 `id` 和 `key`
4. 将获取到的 `id` 和 `key` 分别填入配置文件的 `api_id` 和 `api_key` 字段

## API 接口说明

TimeNest 天气服务支持多种 API 接口以确保高可用性：

### 主要接口

1. **域名接口（推荐）**
   - URL: `https://cn.apihz.cn/api/tianqi/tqyb.php`
   - 特点: 自动分发到集群接口服务器，CC防火墙适中

2. **集群IP接口**
   - URL1: `http://101.35.2.25/api/tianqi/tqybip.php`
   - URL2: `http://124.222.204.22/api/tianqi/tqybip.php`
   - URL3: `http://124.220.49.230/api/tianqi/tqybip.php`
   - 特点: 省去域名解析步骤，速度较快，但容易遭受攻击

3. **彩钻接口（高稳定性）**
   - URL: `https://vip.apihz.cn/api/tianqi/tqyb.php`
   - 特点: 专属集群+普通集群+备用集群，自动负载均衡，自动故障切换，抗攻击，全球智能CDN加速

### 请求参数

| 参数名 | 必填 | 说明 |
|--------|------|------|
| id | 是 | 用户中心的数字ID |
| key | 是 | 用户中心通讯秘钥 |
| sheng | 是 | 要查询的省份名称 |
| place | 是 | 要查询的城市或区县级名称 |

### 返回参数

| 参数名 | 说明 |
|--------|------|
| code | 状态码，200表示成功，400表示错误 |
| msg | 错误信息，当code为400时提供 |
| precipitation | 降水量 |
| temperature | 温度 |
| pressure | 气压 |
| humidity | 湿度 |
| windDirection | 风向 |
| windDirectionDegree | 风向度 |
| windSpeed | 风速 |
| windScale | 风速描述 |
| place | 查询到的地区 |
| weather1 | 当日主要天气 |
| weather2 | 当日次要天气 |
| weather1img | 当日主要天气图标 |
| weather2img | 当日次要天气图标 |
| uptime | 天气数据更新时间 |

## 后端程序接口

天气服务提供以下接口供后端程序调用：

### 1. 更新天气设置

**接口地址**: `/api/weather/settings`

**请求方法**: POST

**请求参数**:
```json
{
  "api_id": "your_api_id",
  "api_key": "your_api_key",
  "location": "四川,绵阳",
  "update_interval": 1800,
  "unit": "metric",
  "enabled": true
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "天气设置更新成功"
}
```

### 2. 获取当前天气数据

**接口地址**: `/api/weather/current`

**请求方法**: GET

**响应示例**:
```json
{
  "location": "中国, 四川, 绵阳",
  "temperature": 26.5,
  "humidity": 87,
  "pressure": 943,
  "wind_speed": 2.4,
  "weather_condition": "中雨转暴雨",
  "forecast": [
    {
      "wind_direction": "西北风",
      "wind_scale": "微风",
      "wind_direction_degree": 338,
      "precipitation": 0,
      "weather1img": "https://rescdn.apihz.cn/resimg/tianqi/zhongyu.png",
      "weather2img": "https://rescdn.apihz.cn/resimg/tianqi/baoyu.png",
      "uptime": "2025/07/18 21:10"
    }
  ],
  "last_updated": "2025-07-18T21:10:00"
}
```

### 3. 手动刷新天气数据

**接口地址**: `/api/weather/refresh`

**请求方法**: POST

**响应示例**:
```json
{
  "success": true,
  "message": "天气数据刷新成功"
}
```

## 使用示例

### Python 示例

```python
from services.weather_service import WeatherService

# 创建天气服务实例
weather_service = WeatherService()

# 更新天气设置
settings_data = {
    "api_id": "your_api_id",
    "api_key": "your_api_key",
    "location": "四川,绵阳",
    "update_interval": 1800,
    "enabled": True
}

# 应用设置
success = weather_service.update_settings(settings_data)

# 获取天气数据
weather_data = weather_service.fetch_weather_data()

if weather_data:
    print(f"位置: {weather_data.location}")
    print(f"温度: {weather_data.temperature}°C")
    print(f"湿度: {weather_data.humidity}%")
    # ... 其他字段
```

## 注意事项

1. **API调用频次**: 公共ID和KEY共享每分钟调用频次限制，建议注册获取自己的ID和KEY以独享调用频次
2. **地名处理**: 如果查询失败，尝试去掉省份或地点的后缀（如"省"、"市"、"区"、"县"等）
3. **数据更新**: 数据来源于中国气象局官方，建议合理设置调用间隔，避免频繁请求
4. **错误处理**: 务必检查返回的code字段，当code为400时，根据msg提示调整请求参数
5. **安全性**: API密钥存储在配置文件中，请确保配置文件的访问权限安全

## 故障排除

1. **无法获取天气数据**:
   - 检查网络连接
   - 验证API ID和KEY是否正确
   - 确认位置信息格式是否正确
   - 尝试使用不同的API接口

2. **API返回错误**:
   - 查看错误信息提示
   - 检查请求参数是否符合要求
   - 确认API调用频次是否超出限制

3. **配置文件问题**:
   - 确保配置文件格式正确（JSON格式）
   - 检查文件权限是否允许读写
   - 确认配置文件路径是否正确