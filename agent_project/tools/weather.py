# tools/weather.py —— 完整版（复用你 agent.py 的 get_weather [2]）
from .base import BaseTool
import json
import urllib.request


class WeatherTool(BaseTool):
    name = "get_weather"
    description = "查天气（按经纬度），返回天气、温度、湿度、日出日落、降雨概率"
    parameters = {
        "type": "object",
        "properties": {
            "latitude": {"type": "number", "description": "纬度"},
            "longitude": {"type": "number", "description": "经度"},
        },
        "required": ["latitude", "longitude"],
    }

    # 天气码字典
    WEATHER_CODE_DESC = {
        0: "晴朗的天空", 1: "主要晴朗", 2: "局部多云", 3: "阴天",
        45: "雾气", 48: "霜雾沉积",
        51: "毛毛雨：轻度", 53: "毛毛雨：中度", 55: "毛毛雨：密集",
        56: "冻毛毛雨：轻微", 57: "冻毛毛雨：强度高",
        61: "降雨：轻度", 63: "降雨：中度", 65: "降雨：强雨",
        66: "冻雨：轻度", 67: "冻雨：强烈",
        71: "降雪量：轻度", 73: "降雪量：中度", 75: "降雪量：重度", 77: "雪粒",
        80: "阵雨：轻度", 81: "阵雨：中度", 82: "阵雨：猛烈",
        85: "雪阵阵：轻微", 86: "雪阵阵：猛烈",
        95: "雷暴：轻度或中度", 96: "雷暴伴轻微冰雹", 99: "雷暴伴强烈冰雹",
    }

    def execute(self, latitude: float, longitude: float) -> str:
        try:
            url = (f"https://api.open-meteo.com/v1/forecast?latitude={latitude}"
                   f"&longitude={longitude}"
                   f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m"
                   f"&daily=weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_probability_max"
                   f"&timezone=Asia%2FShanghai")
            data = json.loads(urllib.request.urlopen(url).read())

            cur = data["current"]
            today = {k: v[0] for k, v in data["daily"].items()}
            return json.dumps({
                "天气": self.WEATHER_CODE_DESC.get(
                    today["weather_code"], f"未知天气码{today['weather_code']}"),
                "当前温度_C": cur["temperature_2m"],
                "湿度_%": cur["relative_humidity_2m"],
                "今日最高_C": today["temperature_2m_max"],
                "今日最低_C": today["temperature_2m_min"],
                "日出": today["sunrise"][11:16],
                "日落": today["sunset"][11:16],
                "降雨概率_%": today["precipitation_probability_max"],
            }, ensure_ascii=False)
        except Exception as e:
            return f"查天气失败: {e}"