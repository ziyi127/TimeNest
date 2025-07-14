#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 文本转语音模块
提供跨平台的语音合成功能
"""

import logging
import subprocess
import sys
from typing import Optional


class TextToSpeech:
    """
    文本转语音类
    
    提供跨平台的语音合成功能
    """
    
    def __init__(self):
        """初始化TTS"""
        self.logger = logging.getLogger(f'{__name__}.TextToSpeech')
        self.available = self._check_availability()
        
        
        if self.available:
            self.logger.info("TTS初始化成功")
        
            self.logger.info("TTS初始化成功")
        else:
            self.logger.warning("TTS不可用")
    
    def _check_availability(self) -> bool:
        """检查TTS是否可用"""
        try:
            if sys.platform.startswith('linux'):
                # 检查 espeak 或 festival:
                # 检查 espeak 或 festival
                try:
                    subprocess.run(['espeak', '--version'], 
                                 capture_output=True, check=True)
                    self.engine = 'espeak'
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass
                
                try:
                    subprocess.run(['festival', '--version'], 
                                 capture_output=True, check=True)
                    self.engine = 'festival'
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass
                
                # 使用 spd-say (speech-dispatcher)
                try:
                    subprocess.run(['spd-say', '--version'], 
                                 capture_output=True, check=True)
                    self.engine = 'spd-say'
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass
                    
            elif sys.platform == 'darwin':
                # macOS 使用 say 命令
                try:
                    subprocess.run(['say', '--version'], 
                                 capture_output=True, check=True)
                    self.engine = 'say'
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass
                    
            elif sys.platform.startswith('win'):
                # Windows 使用 PowerShell
                self.engine = 'powershell'
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"检查TTS可用性失败: {e}")
            return False
    
    def speak(self, text: str, speed: float = 1.0) -> bool:
        """
        语音播报文本
        
        Args:
            text: 要播报的文本
            speed: 播报速度 (0.5-2.0)
            
        Returns:
            bool: 播报是否成功
        """
        if not self.available:
            self.logger.warning("TTS不可用，跳过语音播报")
            return False
        
        
        if not text.strip():
            return False
        
        try:
            if self.engine == 'espeak':
                # espeak -s 速度 "文本"
                speed_wpm = int(175 * speed)  # 默认175词/分钟
                subprocess.run(['espeak', '-s', str(speed_wpm), text], 
                             check=True)
                
            elif self.engine == 'festival':
                # echo "文本" | festival --tts
                process = subprocess.Popen(['festival', '--tts'], 
                                         stdin=subprocess.PIPE)
                process.communicate(input=text.encode())
                
            elif self.engine == 'spd-say':
                # spd-say -r 速度 "文本"
                rate = int(speed * 50)  # 转换为 spd-say 的速度范围
                subprocess.run(['spd-say', '-r', str(rate), text], 
                             check=True)
                
            elif self.engine == 'say':
                # say -r 速度 "文本"
                rate = int(200 * speed)  # macOS say 的速度范围
                subprocess.run(['say', '-r', str(rate), text], 
                             check=True)
                
            elif self.engine == 'powershell':
                # PowerShell TTS
                ps_script = f'''
                Add-Type -AssemblyName System.Speech
                $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
                $synth.Rate = {int((speed - 1) * 5)}
                $synth.Speak("{text}")
                '''
                subprocess.run(['powershell', '-Command', ps_script], 
                             check=True)
            
            self.logger.debug(f"语音播报成功: {text[:50]}...")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"语音播报失败: {e}")
            return False
        except Exception as e:
            self.logger.error(f"语音播报异常: {e}")
            return False
    
    def is_available(self) -> bool:
        """
        检查TTS是否可用
        
        Returns:
            bool: TTS是否可用
        """
        return self.available
    
    def get_engine(self) -> Optional[str]:
        """
        获取当前使用的TTS引擎
        
        Returns:
            Optional[str]: 引擎名称
        """
        return getattr(self, 'engine', None) if self.available else None
    
    def cleanup(self) -> None:
        """清理资源"""
        try:
            # 停止任何正在进行的语音播报
            if hasattr(self, 'engine'):
                if self.engine == 'espeak':
                    subprocess.run(['pkill', 'espeak'], 
                                 capture_output=True)
                elif self.engine == 'festival':
                    subprocess.run(['pkill', 'festival'], 
                                 capture_output=True)
                elif self.engine == 'spd-say':
                    subprocess.run(['pkill', 'spd-say'], 
                                 capture_output=True)
            
            self.logger.debug("TTS清理完成")
            
        except Exception as e:
            self.logger.warning(f"TTS清理失败: {e}")


# 测试函数
def test_tts():
    """测试TTS功能"""
    print("测试 TimeNest TTS 模块")
    print("=" * 30)
    
    tts = TextToSpeech()
    
    
    if tts.is_available():
        print(f"✓ TTS可用，引擎: {tts.get_engine()}")
        
        # 测试播报
        success = tts.speak("Hello, this is TimeNest TTS test.")
        if success:
            print("✓ 语音播报测试成功")
        else:
            print("✗ 语音播报测试失败")
    else:
        print("✗ TTS不可用")
        print("请安装以下软件之一:")
        print("- Linux: espeak, festival, 或 speech-dispatcher")
        print("- macOS: 系统自带 say 命令")
        print("- Windows: 系统自带 PowerShell")


if __name__ == "__main__":
    test_tts()
