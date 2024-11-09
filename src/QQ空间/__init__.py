"""
QQ空间


"""

from pprint import pprint

from PIL import Image
import time
import re
from pathlib import Path
import os
import sys
import numpy as np
import webbrowser
import json
import typing
from dataclasses import dataclass
import requests
from requests.exceptions import RequestException
from typing import Dict, List, Optional, Any, Union
import logging
from abc import ABC, abstractmethod


def configure_logging():
    """
    日志配置
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    return logging.getLogger(__name__)


class QZoneConfig:
    """
    QQ空间相关配置
    """
    BASE_URL: str = "https://user.qzone.qq.com"
    API_URLS: Dict[str, str] = {
        "friends": "/proxy/domain/r.qzone.qq.com/cgi-bin/tfriend/friend_show_qqfriends.cgi",
    }
    QR_CONFIG: Dict[str, Any] = {
        "url": "https://ssl.ptlogin2.qq.com/ptqrshow",
        "check_url": "https://ssl.ptlogin2.qq.com/ptqrlogin",
        "params": {
            "appid": "549000912",
            "e": "2",
            "l": "M",
            "s": "3",
            "d": "72",
            "v": "4",
            "daid": "5",
            "pt_3rd_aid": "0"
        }
    }
    REQUIRED_COOKIES: frozenset = frozenset({'uin', 'skey', 'p_uin', 'pt4_token', 'p_skey'})


class HTTPClient:
    """
    HTTP 请求客户端基类
    """

    def __init__(self, cookies: Dict[str, str], headers: Optional[Dict[str, str]] = None):
        self.cookies = cookies
        self.headers = headers or self._default_headers()
        self.session = requests.Session()
        self.logger = configure_logging()

    def _default_headers(self) -> Dict[str, str]:
        return {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'referer': f'{QZoneConfig.BASE_URL}/',
            'sec-ch-ua': '"Chromium";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def get(self, url: str, params: Optional[Dict] = None,
            cookies: Optional[Dict[str, str]] = None,
            allow_redirects: bool = True) -> requests.Response:
        """
        发送 GET 请求
        """
        try:
            response = self.session.get(
                url,
                params=params,
                cookies=cookies or self.cookies,
                headers=self.headers,
                allow_redirects=allow_redirects,
            )
            response.raise_for_status()
            # self.logger.info(f"请求成功: {response.status_code}")
            return response
        except RequestException as e:
            self.logger.error(f"HTTP请求失败: {e}")
            raise


class QZoneClient(HTTPClient):
    """
    QQ空间客户端
    """

    def make_request(self, url: str, params: Optional[Dict] = None) -> Dict:
        """
        发送请求并处理QQ空间API响应
        """
        try:
            response = self.get(f"{QZoneConfig.BASE_URL}{url}", params)
            text = response.text.strip()
            self.logger.debug(f"收到响应: {text[:200]}")
            json_text = text[text.find('{'):text.rfind('}') + 1]
            return json.loads(json_text)
        except Exception as e:
            self.logger.error(f"API请求失败: {e}")
            return {}


@dataclass
class Friend:
    """
    好友信息数据类
    """
    uin: str
    name: str
    remark: str
    img: str
    group_id: int
    group_name: str
    online: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any], group_name: str) -> 'Friend':
        """
        从字典创建Friend实例
        """
        return cls(
            uin=str(data.get('uin', '')),
            name=data.get('name', ''),
            remark=data.get('remark', ''),
            img=data.get('img', ''),
            group_id=data.get('groupid', 0),
            group_name=group_name,
            online=data.get('online', 0) == 1
        )


@dataclass
class FriendGroup:
    """
    好友分组信息数据类
    """
    id: int
    name: str
    online_count: int = 0
    total_count: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FriendGroup':
        """
        从字典创建FriendGroup实例
        """
        return cls(
            id=data['gpid'],
            name=data.get('gpname', '未命名分组')
        )


class QRManager:
    """
    二维码管理类
    """

    def __init__(self):
        self.logger = configure_logging()
        self.qr_dir = self._initialize_qr_directory()
        self.qr_path = self.qr_dir / "login_qr.png"

    def _initialize_qr_directory(self) -> Path:
        """
        初始化二维码保存目录
        """
        try:
            script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
            temp_dir = script_dir / "temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            return temp_dir
        except Exception as e:
            self.logger.warning(f"无法创建temp目录: {e}, 使用桌面作为备选")
            return Path.home() / "Desktop"

    def save_qr(self, content: bytes) -> bool:
        """
        保存二维码图片
        """
        try:
            with open(self.qr_path, 'wb') as f:
                f.write(content)
            return True
        except Exception as e:
            self.logger.error(f"保存二维码失败: {e}")
            desktop_path = Path.home() / "Desktop" / "login_qr.png"
            try:
                with open(desktop_path, 'wb') as f:
                    f.write(content)
                self.qr_path = desktop_path
                return True
            except Exception as e:
                self.logger.error(f"保存到桌面失败: {e}")
                return False

    def display_qr(self) -> None:
        """
        显示二维码
        """
        try:
            img = Image.open(self.qr_path)
            img = img.resize((350, 350))

            console_width = 50
            self.logger.info("=" * (console_width * 2))
            self.logger.info("正在打开二维码图片, 请使用手机QQ扫描登录".center(console_width * 2))
            self.logger.info(f"二维码保存位置: {self.qr_path}")
            self.logger.info("=" * (console_width * 2))

            try:
                img.show()
            except Exception:
                try:
                    webbrowser.open(str(self.qr_path))
                except Exception:
                    self.logger.error("无法自动打开二维码, 请手动打开图片扫描")
        except Exception as e:
            self.logger.error(f"显示二维码失败: {e}")

    def delete_qr(self) -> bool:
        """
        删除二维码图片
        """
        try:
            if self.qr_path.exists():
                self.qr_path.unlink()  # 删除文件
                self.logger.info("二维码文件已删除")
                return True
            else:
                self.logger.warning("二维码文件不存在")
                return False
        except Exception as e:
            self.logger.error(f"删除二维码失败: {e}")
            return False


class TokenGenerator:
    """
    令牌生成器
    """

    @staticmethod
    def calculate_bkn(p_skey: str) -> str:
        """
        计算bkn值
        """
        hash_value = 5381
        for char in p_skey:
            hash_value += (hash_value << 5) + ord(char)
        return hash_value & 2147483647

    @staticmethod
    def calculate_g_tk(p_skey: str) -> str:
        """
        计算g_tk值
        """
        return TokenGenerator.calculate_bkn(p_skey)

    @staticmethod
    def calculate_ptqr_token(qrsig: str) -> int:
        """
        计算ptqrtoken值
        """
        hash_value = 0
        for char in qrsig:
            hash_value += (hash_value << 5) + ord(char)
        return hash_value & 2147483647


class QLogin:
    """
    QQ登录管理类
    """

    def __init__(self):
        self.logger = configure_logging()
        self.qr_manager = QRManager()
        self.http_client = HTTPClient({})
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.user_info_path = self.data_dir / "user_info.json"

    def _get_qr_code(self) -> Optional[str]:
        """
        获取登录二维码
        """
        try:
            params = {**QZoneConfig.QR_CONFIG['params'], 't': str(time.time())}
            response = self.http_client.get(QZoneConfig.QR_CONFIG['url'], params)
            qrsig = response.cookies.get('qrsig')

            if self.qr_manager.save_qr(response.content):
                self.logger.info("登录二维码获取成功")
                self.qr_manager.display_qr()
                return qrsig
            return None
        except Exception as e:
            self.logger.error(f"获取二维码失败: {e}")
            return None

    def _check_qr_status(self, ptqrtoken: int, cookies: Dict) -> Optional[Union[str, tuple]]:
        """
        检查二维码状态
        """
        check_params = {
            'u1': 'https://qzs.qq.com/qzone/v5/loginsucc.html?para=izone',
            'ptqrtoken': ptqrtoken,
            'ptredirect': '0',
            'h': '1',
            't': '1',
            'g': '1',
            'from_ui': '1',
            'ptlang': '2052',
            'action': f'0-0-{time.time()}',
            'js_ver': '20032614',
            'js_type': '1',
            'login_sig': '',
            'pt_uistyle': '40',
            'aid': '549000912',
            'daid': '5'
        }

        try:
            response = self.http_client.get(QZoneConfig.QR_CONFIG['check_url'], check_params)
            status_match = re.search(r"ptuiCB\('(\d+)'", response.text)
            if not status_match:
                self.logger.error("无法解析登录状态")
                return None

            status = status_match.group(1)
            status_messages = {
                '65': '二维码已失效',
                '66': '二维码未扫描',
                '67': '二维码已扫描, 等待确认',
                '0': '登录成功',
                '68': '登录被取消'
            }

            self.logger.info(status_messages.get(status, '未知状态'))

            if status == '0':
                uin = response.cookies.get('uin')
                sigx = re.findall(r'ptsigx=(.*?)&', response.text)
                if not uin or not sigx:
                    self.logger.error("登录信息获取失败")
                    return None
                return response.cookies, uin, sigx[0]
            elif status in {'68', '65'}:
                return status

            return None

        except Exception as e:
            self.logger.error(f"检查状态失败: {e}")
            return None

    def _save_user_info(self, cookies: Dict, uin: str) -> None:
        """
        保存用户信息到 data 目录
        """
        try:
            user_info = {
                'cookies': cookies,
                'uin': uin,
            }
            with open(self.user_info_path, 'w') as f:
                json.dump(user_info, f)
            self.logger.info("用户信息已保存")
        except Exception as e:
            self.logger.error(f"保存用户信息失败: {e}")

    def logout(self) -> None:
        """
        用户退出登录
        """
        try:
            if self.user_info_path.exists():
                self.user_info_path.unlink()
                self.logger.info("用户信息文件已清空")
            else:
                self.logger.warning("用户信息文件不存在")
        except Exception as e:
            self.logger.error(f"清空用户信息文件失败: {e}")

    def login(self) -> Optional[Dict]:
        """
        执行登录
        """
        qrsig = self._get_qr_code()
        if not qrsig:
            self.logger.error("获取二维码失败")
            return None

        ptqrtoken = TokenGenerator.calculate_ptqr_token(qrsig)
        retry_count = 0
        max_retries = 3

        while retry_count < max_retries:
            result = self._check_qr_status(ptqrtoken, {'qrsig': qrsig})

            if isinstance(result, str):
                self.logger.error(f"登录失败, 状态码: {result}")
                self.qr_manager.delete_qr()
                if input("是否重新获取二维码? (y/n) ").lower() == 'y':
                    return self.login()
                return None

            if not result:
                # self.logger.warning("暂未获取到登录结果, 重试中...")
                time.sleep(3)
                continue

            cookies, uin, sigx = result
            check_sig_url = (
                f'https://ptlogin2.qzone.qq.com/check_sig?pttype=1&uin={uin}'
                f'&service=ptqrlogin&nodirect=0&ptsigx={sigx}'
                f'&s_url=https%3A%2F%2Fqzs.qq.com%2Fqzone%2Fv5%2Floginsucc.html%3Fpara%3Dizone'
                f'&f_url=&ptlang=2052&ptredirect=100&aid=549000912&daid=5&j_later=0'
                f'&low_login_hour=0&regmaster=0&pt_login_type=3&pt_aid=0&pt_aaid=16'
                f'&pt_light=0&pt_3rd_aid=0'
            )

            try:
                response = self.http_client.get(check_sig_url, cookies, allow_redirects=False)
                if response.status_code == 302:
                    self.logger.info("登录成功")
                    self.qr_manager.delete_qr()
                    self._save_user_info(dict(response.cookies), uin)
                    return dict(response.cookies)

                self.logger.warning("登录验证失败, 重试中...")
                retry_count += 1

            except Exception as e:
                self.logger.error(f"获取登录信息失败: {e}")
                retry_count += 1

        self.logger.error("登录失败, 已超过最大重试次数")
        return None


class QZoneUtil:
    """
    QQ空间信息处理工具类
    """

    logger = configure_logging()

    @staticmethod
    def extract_uin(uin: str) -> Optional[str]:
        """
        从uin中提取QQ号

        :uin: 原始uin字符串

        :Returns:
            str: 提取的QQ号
        """
        if not uin:
            return None

        # 匹配o0或0开头的数字序列, 去除前导零
        match = re.search(r'(?:o0+|0+)?(\d+)', uin)
        return match.group(1) if match else None

    @staticmethod
    def validate_cookies(cookies: Dict) -> bool:
        """
        验证cookies是否包含所需的关键字段

        :cookies: cookies字典

        :Returns:
            bool: cookies是否有效
        """
        if not cookies:
            return False

        # 检查必需的cookie字段
        for key in QZoneConfig.REQUIRED_COOKIES:
            if key not in cookies or not cookies[key]:
                return False
        return True

    @staticmethod
    def normalize_cookies(cookies: Dict) -> Dict:
        """
        规范化cookies, 确保包含所有必需字段
        如果缺少字段, 使用空字符串填充

        :cookies: 原始cookies字典

        :Returns:
            Dict: 规范化后的cookies字典
        """
        normalized = cookies.copy()
        for key in QZoneConfig.REQUIRED_COOKIES:
            if key not in normalized:
                normalized[key] = ''
        return normalized

    @staticmethod
    def _initialize_cookies(cookies: Optional[Dict]) -> Dict:
        """
        初始化并验证cookies

        :login_cookies: 可选的登录cookies

        :Returns:
            Dict: 规范化后的cookies字典
        """
        cookies = cookies or QLogin().login()
        if not QZoneUtil.validate_cookies(cookies):
            raise ValueError("登录失败或cookies无效")
        QZoneUtil.logger.info("成功初始化cookies")
        return QZoneUtil.normalize_cookies(cookies)

    @staticmethod
    def _extract_uin(cookies: Dict) -> str:
        """
        提取并验证QQ号

        :Returns:
            str: 提取的QQ号
        """
        uin = QZoneUtil.extract_uin(cookies.get('uin', ''))
        if not uin:
            raise ValueError("无法获取有效的QQ号")
        return uin

    @staticmethod
    def _generate_g_tk(cookies: Dict) -> str:
        """
        生成g_tk值

        :Returns:
            str: 生成的g_tk值
        """
        return TokenGenerator.calculate_g_tk(cookies.get('p_skey', ''))

    @staticmethod
    def load_user_info() -> Optional[Dict]:
        """
        从 data 目录加载用户信息
        """
        data_dir = Path(__file__).parent / "data"
        user_info_path = data_dir / "user_info.json"

        # 读取用户信息文件
        try:
            if user_info_path.exists():
                with open(user_info_path, 'r') as f:
                    user_info = json.load(f)
                    cookies = user_info.get('cookies')
                    if QZoneUtil.validate_cookies(cookies):
                        QZoneUtil.logger.info("成功从文件读取cookies")
                        return QZoneUtil.normalize_cookies(cookies)
        except Exception as e:
            QZoneUtil.logger.error(f"获取用户信息失败: {e}")
            return None

    @staticmethod
    def _load_user_info(cookies: Dict) -> Optional[Dict]:
        """
        从 data 目录加载用户信息
        """
        return QZoneUtil.load_user_info() or QZoneUtil._initialize_cookies(cookies)


class QZoneFriends:
    """
    QQ空间好友管理类
    """

    def __init__(self, client: QZoneClient, uin: str, g_tk: str):
        self.logger = configure_logging()
        self.client = client
        self.uin = uin
        self.g_tk = g_tk
        self._cache = {
            'raw_data': None,
            'groups': {},
            'friends': []
        }

    def _fetch_friends_data(self) -> Dict:
        """
        获取好友数据
        """
        if self._cache['raw_data']:
            return self._cache['raw_data']

        params = {
            'uin': self.uin,
            'follow_flag': '1',
            'groupface_flag': '0',
            'fupdate': '1',
            'g_tk': self.g_tk,
        }

        try:
            response = self.client.make_request(QZoneConfig.API_URLS['friends'], params)
            if not response:
                raise ValueError("获取好友数据失败")
            self.logger.info("成功获取好友数据")
            self._cache['raw_data'] = response
            return response
        except Exception as e:
            self.logger.error(f"获取好友数据失败: {e}")
            return {}

    def get_groups(self) -> Dict[int, FriendGroup]:
        """
        获取好友分组信息
        """
        if self._cache['groups']:
            return self._cache['groups']

        try:
            data = self._fetch_friends_data()
            groups_data = data.get('data', {}).get('gpnames', [])

            # 初始化分组信息
            self._cache['groups'] = {
                group['gpid']: FriendGroup(
                    id=group['gpid'],
                    name=group.get('gpname', '未命名分组')
                ) for group in groups_data if 'gpid' in group
            }

            # 统计分组人数
            for friend in self.get_friends():
                group = self._cache['groups'].get(friend.group_id)
                if group:
                    group.total_count += 1
                    if friend.online:
                        group.online_count += 1

            return self._cache['groups']

        except Exception as e:
            self.logger.error(f"获取好友分组失败: {e}")
            return {}

    def get_friends(self) -> List[Friend]:
        """
        获取好友列表
        """
        if self._cache['friends']:
            return self._cache['friends']

        try:
            data = self._fetch_friends_data()
            friends_data = data.get('data', {}).get('items', [])
            groups = self.get_groups()

            self._cache['friends'] = []
            for item in friends_data:
                group_id = item.get('groupid', 0)
                friend = Friend(
                    uin=str(item.get('uin', '')),
                    name=item.get('name', ''),
                    remark=item.get('remark', ''),
                    img=item.get('img', ''),
                    group_id=group_id,
                    group_name=groups.get(group_id, FriendGroup(0, '默认分组')).name,
                    online=item.get('online', 0) == 1
                )
                self._cache['friends'].append(friend)

            return self._cache['friends']

        except Exception as e:
            self.logger.error(f"获取好友列表失败: {e}")
            return []

    def print_summary(self):
        """
        简单打印好友信息摘要
        """
        try:
            groups = self.get_groups()
            friends = self.get_friends()

            print(f"\n==== 好友统计 (共 {len(friends)} 人) ====")

            # 按分组显示好友
            for group_id, group in sorted(groups.items()):
                # 获取该分组的好友
                group_friends = [f for f in friends if f.group_id == group_id]
                # 按在线状态和名称排序
                group_friends.sort(key=lambda x: (-x.online, x.remark or x.name))

                print(
                    f"\n{group.name} (共 {len(group_friends)} 人, 在线 {sum(1 for f in group_friends if f.online)} 人):")

                # 打印好友信息
                for friend in group_friends:
                    status = "🟢" if friend.online else "⚪"
                    name = friend.remark or friend.name
                    print(f"  {status} {name} ({friend.uin})")

        except Exception as e:
            self.logger.error(f"打印好友信息失败: {e}")


class QZone:
    """
    QQ空间主类
    """

    def __init__(self, login_cookies: Optional[Dict] = None):
        """
        初始化QZone客户端

        :login_cookies: 可选的登录cookies, 如果未提供将自动登录
        """
        self.logger = configure_logging()
        self.cookies = QZoneUtil._load_user_info(login_cookies)

        self.client = QZoneClient(self.cookies)
        self.uin = QZoneUtil._extract_uin(self.cookies)
        self.g_tk = QZoneUtil._generate_g_tk(self.cookies)
        self.friends = QZoneFriends(self.client, self.uin, self.g_tk)


def main():
    logger = configure_logging()
    try:
        qzone = QZone()

        # 基本使用
        qzone.friends.print_summary()
    except Exception as e:
        logger.error(f"程序执行失败: {e}")


if __name__ == '__main__':
    main()
