"""
20241031-02
抖音视频/图文下载

    requests
    DrissionPage
    json
    re
    selenium
    webdriver-manager
    undetected-chromedriver

"""

import os
import requests
import re
from urllib.parse import unquote
import json
from pprint import pprint

from DrissionPage import ChromiumPage

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options as EdgeOptions

import undetected_chromedriver as uc


class DouyinVideoDownloader:
    def __init__(self, url='', use_method='chromium'):
        """
        初始化

        :param url: 抖音URL
        :param use_method: 自动化 (chromium, selenium, undetected)
        """
        self.url = url
        # 默认下载位置
        self.download_folder = 'douyin'
        # 用户字典
        self.user_info = {}

        if use_method == 'selenium':
            edge_options = EdgeOptions()
            edge_options.use_chromium = True
            edge_options.add_argument('--headless')

            edge_service = Service(
                executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
            )

            self.driver = webdriver.Edge(service=edge_service, options=edge_options)
        elif use_method == 'undetected':
            options = uc.ChromeOptions()
            options.add_argument('--headless')

            self.driver = uc.Chrome(options=options)
        else:
            self.driver = ChromiumPage()

    def get_user_info(self):
        """
        获取用户信息
        https://www.douyin.com/aweme/v1/web/user/profile/other/
        """
        try:
            # 获取用户主页信息
            headers = self.setup_headers()

            self.driver.listen.start('user/profile/other/')
            self.driver.get(self.url)

            # 等待相应
            resp = self.driver.listen.wait()
            dp_json = resp.response.body
            user_data = dp_json['user']
            # 提取用户信息
            self.user_info = {
                'nickname': user_data.get('nickname', '未知用户'),
                'sec_uid': user_data.get('sec_uid', ''),
                'uid': user_data.get('uid', ''),
                'unique_id': user_data.get('unique_id', ''),
                'signature': user_data.get('signature', ''),
                'ip_location': user_data.get('ip_location', '').replace('IP属地：', '').strip(),
                'user_age': user_data.get('user_age', -1),
            }
            # 使用昵称作为下载文件夹名
            safe_nickname = re.sub(r'[<>:"/\\|?*]', '', self.user_info['nickname'])
            self.download_folder = f'douyin_{safe_nickname}'
            return self.user_info
        except Exception as e:
            print(f"获取用户信息时发生错误: {e}")
            return None

    def ensure_download_folder(self):
        """
        创建文件夹
        """
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
            print(f"{self.download_folder} OK")

    def setup_headers(self):
        """
        请求头

        :return: 请求头字典
        """
        return {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'max-age=0',
            'cookie': 'douyin.com; __ac_referer=__ac_blank; ttwid=1%7ClTa64fQKVtC1EdiQXom-ib9ORL8hvogaUW1i9I1wFqA%7C1725238278%7C59b5fe06c7cbd6fcd8f7a03cd8e48ae4bcd7c2a3a5661d0d1f6aad85ddf262a9; UIFID_TEMP=c3109cf8eab4507640f022360c5ce002c7035d0857c7085fdeb180d1661fca195ccc1d70fab31e5cbb299b8b39623e7541fd8fcf40d6d549c7ed6ae92488c341b7ed3b84e2563424a5d319a1dec897fe; hevc_supported=true; s_v_web_id=verify_m0kabuyf_ou23hgQ7_9i2A_4yG1_AERR_p6pTjwLzxQVF; passport_csrf_token=598381047a396bdde5319e6e82566410; passport_csrf_token_default=598381047a396bdde5319e6e82566410; bd_ticket_guard_client_web_domain=2; fpk1=U2FsdGVkX1+bqHyPsIbhvDZ5beMgjC/KhpMmQPjcGV/k6+5y/B7Tt7MMF1mwIzC2NGk0jjUpKG7qnel3VjqdpA==; fpk2=a565ccc5e7018c4ec7bec64e38db2966; odin_tt=6a71e94a9f9a908d2e6eeb0150855252f9759de2ab8d5bfbd2b6ee09380aa0c34dcad9e73075d9198c04bc7d6a90dc0f85344e2c55b0bc4a38c51031dad5c462148d21dda794d2f6200e8dceb4fa536f; UIFID=c3109cf8eab4507640f022360c5ce002c7035d0857c7085fdeb180d1661fca195ccc1d70fab31e5cbb299b8b39623e751794a142694bf360abd185aa572a862f9f5d871b191cbbab242ae0452cf73bab9620df2edcada9fa19a580685bbc92481405af82ad47ef5ae90252fdcd67f7c990f2a48bea1e2ac29ce42ce56989d66aa48da3f9b62e432a848d37be69eae14bde8c83ff7aa548e887029c3e85477088; SEARCH_RESULT_LIST_TYPE=%22single%22; __ac_signature=_02B4Z6wo00f01.ils4AAAIDDcvG9S2NxP3.4hbcAAJkT7b; dy_swidth=1707; dy_sheight=1067; strategyABtestKey=%221730374407.972%22; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%7D; xgplayer_user_id=729057910733; h265ErrorNum=-1; download_guide=%223%2F20241031%2F0%22; pwa2=%220%7C0%7C3%7C0%22; douyin.com; xg_device_score=7.90435294117647; device_web_cpu_core=16; device_web_memory_size=8; architecture=amd64; csrf_session_id=c7ac0598778076e425bfc420358120bf; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A1%7D; webcast_leading_last_show_time=1730376123189; webcast_leading_total_show_times=1; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A1%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22; __ac_nonce=06723721500d1c3c47a91; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1707%2C%5C%22screen_height%5C%22%3A1067%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A16%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A100%7D%22; home_can_add_dy_2_desktop=%221%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCTm5HUkFuclgrb3FLOUR2emV3RWlpM1RwQUxZSXIyVVRSOFk4QVpuUlJRaWo1ZzY1d0JtTDNYdDk4SERwbXFLcmExN2RLc05rWWk3K2I3ZW0vTm9pZGs9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; biz_trace_id=a40be505; gulu_source_res=eyJwX2luIjoiODM1N2RkNmJkNjU0Y2IwMGU1NzMzZjg5Y2RjNTM1OGM1ODg3YjY4ODI2MjY0OWM5N2E4Yzk2MTE0ZmJhMmIwYSJ9; sdk_source_info=7e276470716a68645a606960273f276364697660272927676c715a6d6069756077273f276364697660272927666d776a68605a607d71606b766c6a6b5a7666776c7571273f275e5927666d776a686028607d71606b766c6a6b3f2a2a6e6e6068626c63636f616b616c6e6a6e6d756a60666a696a606762606c6761602a666a6b71606b715a7666776c7571762a666a757c2b6f765927295927666d776a686028607d71606b766c6a6b3f2a2a6860686d6466646f66636d686c67626267626c696c6d69686c6c61616062626a2a6476766071762a68646c6b28726a7769612b7176283160613c3c3666322b6f765927295927666d776a686028607d71606b766c6a6b3f2a2a6c616f676d63666a616a6360696761676d64606e6266606664756d66626a6d6d2a6f762a6160716066716a772b6f765927295927666d776a686028607d71606b766c6a6b3f2a2a66616b6962626760676467606a6b606062696d646175646260626863696867662a666a6b71606b712a76716477715a7666776c75714770762b6f765927295927666d776a686028607d71606b766c6a6b3f2a2a66616b6962626760676467606a6b606062696d646175646260626863696867662a666a6b71606b712a7666776c75714770762b6f76592758272927666a6b766a69605a696c6061273f27636469766027292762696a6764695a7364776c6467696076273f275e5827292771273f27323634313d3333323635363234272927676c715a75776a716a666a69273f2763646976602778; bit_env=_3fo7HWP7rhB-XN3CGFwjjoyhpXeL0ZKxYH-O4nKUEaskVl2ks3iJakNVzxJ-asWnltF5Q1vFhCMHkchkzNTA3PyS-SHyEyJDwzy2qV-QlT4WQV5Se6iP8w8DGeEEL7NcjjKZbbD0clyHgmjLaTE4sQxvu-5MIwoEIt_C-wyf6X342nN-DaZHBUwtVqVEIkmd4wm6Vtq7kFVyWkb41aRdTpzRZ0r4ypiUFn2FSS5vcmttZlb4Mvp-X2L3VGx0tYkVE08QEVFED45Xh0o59_p_BXo3zwZVIWM7wDOGHYrLW5n5FYAnI7f8muM6OpbEICundXmSfQmzqWH7rc-VJGzNVQsyn_LqwawlYG0weqE1qRdwsBpToSnycktEb60Q8zDZaQDs3-HJIxFzyKlKFfmeGGrHtIMS1ps54dZe_d9DuKsDKLS4drByYnwC6VyIRzv-Mak28q7frbUJeqT6JGC1Sj0V4HavETXr5rlCCnC9v89cm6F_4g1bAXqvr3kzHfyIOty7s76iB8car_5OXD75eafEvt4yzQTYuTE1tWKyDE%3D; passport_auth_mix_state=4fkv9ecs4by9g6rjpekdhg0hljhr3hds; IsDouyinActive=false',
            'priority': 'u=0, i',
            'referer': self.url,
            'sec-ch-ua': '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
        }

    def get_video_details(self, video_id, headers):
        """
        从响应中提取视频和图片信息

        :param video_id: 视频ID
        :param headers: 请求头
        :return: 视频/图片详细信息字典
        """
        params = {'modal_id': video_id}

        response = requests.get(url=self.url, params=params, headers=headers)

        # 提取JSON信息
        info = re.findall('<script id="RENDER_DATA" type="application/json">(.*?)</script>', response.text)[0]
        json_data = json.loads(unquote(info))

        # 提取视频URL和详细信息
        video_detail = json_data['app']['videoDetail']
        title = video_detail['desc']

        # 尝试获取视频URL
        video_url = None
        if video_detail.get('video') and video_detail['video'].get('bitRateList'):
            video_url = 'https:' + video_detail['video']['bitRateList'][0]['playAddr'][-1]['src']

        # 获取图片URL列表
        images_urls = []
        if video_detail.get('images'):
            for image in video_detail['images']:
                if image.get('urlList'):
                    images_urls.append(image['urlList'][0])

        return {
            'video_url': video_url,
            'images_urls': images_urls,
            'title': title
        }

    def download_video(self, video_id, headers):
        """
        下载视频或图片到本地

        :param video_id: 视频ID
        :param headers: 请求头
        :return: 下载成功为True, 反之False
        """
        try:
            # 获取视频/图片信息
            content_info = self.get_video_details(video_id, headers)

            # 清理文件名
            safe_title = re.sub(r'[<>:"/\\|?*]', '', content_info['title'])

            # 如果有视频URL, 下载视频
            if content_info['video_url']:
                video_content = requests.get(
                    url=content_info['video_url'],
                    headers=headers
                ).content

                filename = f"{video_id} {safe_title}.mp4"
                filepath = os.path.join(self.download_folder, filename)

                with open(filepath, 'wb') as f:
                    f.write(video_content)
                print(f"{filename} OK")
                return True

            # 如果有图片URL, 下载图片
            elif content_info['images_urls']:
                for idx, img_url in enumerate(content_info['images_urls']):
                    img_content = requests.get(
                        url=img_url,
                        headers=headers
                    ).content

                    filename = f"{video_id} {safe_title} {idx}.png"
                    filepath = os.path.join(self.download_folder, filename)

                    with open(filepath, 'wb') as f:
                        f.write(img_content)
                    print(f"{filename} OK")
                return True

            else:
                print(f"下载失败: {video_id} - 没有可用的视频或图片URL")
                return False

        except Exception as e:
            print(f"下载失败 {video_id}: {e}")
            return False

    def download_videos(self):
        """
        抖音视频下载
        https://www.douyin.com/aweme/v1/web/aweme/post/
        """
        # 获取用户信息
        user_info = self.get_user_info()
        if not user_info:
            print(f"无法获取用户信息, 使用默认下载文件夹: {self.download_folder}")

        # 检测文件夹存在
        self.ensure_download_folder()

        headers = self.setup_headers()

        try:
            self.driver.listen.start('aweme/post/')
            self.driver.get(self.url)
            has_more = True
            while has_more:
                # 等待相应
                resp = self.driver.listen.wait()
                dp_json = resp.response.body
                # 处理响应中的每个视频
                for index in dp_json['aweme_list']:
                    video_id = index['aweme_id']
                    # 下载视频
                    self.download_video(video_id, headers)
                # 查看是否还有更多视频
                has_more = dp_json.get('has_more', 0) != 0
                if not has_more:
                    break
                # 滚动到底部加载更多
                self.driver.scroll.to_bottom()
        except Exception as e:
            print(f"下载过程中发生错误: {e}")
        finally:
            # 关闭浏览器
            if hasattr(self.driver, 'quit'):
                self.driver.quit()
            elif hasattr(self.driver, 'close'):
                self.driver.close()

    def __del__(self):
        """
        确保浏览器关闭
        """
        try:
            if hasattr(self.driver, 'quit'):
                self.driver.quit()
            elif hasattr(self.driver, 'close'):
                self.driver.close()
        except:
            pass


def main():
    """
    处理用户输入并下载视频
    """
    print("欢迎使用抖音视频/图文下载器-谷歌版")
    print("请确保您已安装 Google Chrome, 等待下载中请勿关闭浏览器")
    print("请输入抖音链接(输入0退出): ")

    while True:
        try:
            url = input().strip()

            # 检查是否退出
            if url == '0':
                print("感谢使用, 再见")
                break

            # 检查URL是否为空
            if not url:
                print("URL不能为空, 请重新输入(输入0退出): ")
                continue

            # 检查是否是有效的抖音URL
            # if 'douyin.com' not in url.lower():
            #     print("请输入有效的抖音链接(输入0退出): ")
            #     continue

            # 创建下载器实例并下载视频
            try:
                downloader = DouyinVideoDownloader(url=url)
                downloader.download_videos()
            except Exception as e:
                print(f"下载过程中发生错误: {e}")
            finally:
                # 确保资源被正确释放
                if downloader:
                    del downloader

            print("\n继续下载其他视频? 请输入抖音链接(输入0退出): ")

        except KeyboardInterrupt:
            print("\n检测到退出指令, 正在安全退出...")
            break
        except Exception as e:
            print(f"发生未知错误: {e}")
            print("请重新输入抖音链接(输入0退出): ")


if __name__ == '__main__':
    main()
