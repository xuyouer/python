"""
类搜狗翻译

    requests
    hashlib
    tkinter
"""
from pprint import pprint
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import hashlib
from PIL import Image, ImageTk
import pygame.mixer
from datetime import datetime
import json
import os


class SoGouTranslator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('类搜狗翻译')
        self._position_window(self.root, 1200, 800)
        self.root.resizable(False, False)

        self.selected_target_lang = tk.StringVar()
        self.input_text = None
        self.output_text = None
        self.history_data = []
        self.window_state = 'normal'

        self.history_enabled = tk.BooleanVar(value=True)
        self.voice_type = tk.StringVar(value="女声")
        self.voice_speed = tk.DoubleVar(value=1.0)

        self._setup_network_config()
        self._init_language()
        self._init_audio()
        self._load_history()

    def _init_audio(self):
        """
        初始化音频系统
        """
        pygame.mixer.init()

    def _init_language(self):
        """
        初始化目标语言
        """
        self.languages = {
            '中文': 'zh-CHS',
            '英语': 'en',
            '俄语': 'ru',
            '日语': 'ja',
            '韩语': 'ko'
        }

    def _setup_network_config(self):
        """
        设置网络请求配置
        """
        self.cookies = {
            'ABTEST': '0|1730624231|v17',
            'SNUID': 'C4016EC7CDCBE933975D9935CD934D72',
            'SUID': '08CCA20B1250A20B0000000067273AE7',
            'wuid': '1730624231660',
            'translate.sess': '8ad19305-7b26-4deb-a31c-4c21ca803c89',
            'SUV': '1730624234211',
            'SGINPUT_UPSCREEN': '1730624234251',
            'FQV': 'ff14ff4d8d5eb23a4b62430dfacd5476',
            'cuid': 'AAHJzOioTwAAAAuiVJfmKQAANgg=',
        }

        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            # 'Cookie': 'ABTEST=0|1730624231|v17; SNUID=C4016EC7CDCBE933975D9935CD934D72; SUID=08CCA20B1250A20B0000000067273AE7; wuid=1730624231660; translate.sess=8ad19305-7b26-4deb-a31c-4c21ca803c89; SUV=1730624234211; SGINPUT_UPSCREEN=1730624234251; FQV=ff14ff4d8d5eb23a4b62430dfacd5476; cuid=AAHJzOioTwAAAAuiVJfmKQAANgg=',
            'Origin': 'https://fanyi.sogou.com',
            'Referer': 'https://fanyi.sogou.com/text?keyword=&transfrom=auto&transto=zh-CHS&model=general',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
            'sec-ch-ua': '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

    def _create_menu(self):
        """
        创建菜单栏
        """
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="新建")
        file_menu.add_command(label="打开")
        file_menu.add_command(label="保存")
        file_menu.add_command(label="另存为")
        file_menu.add_separator()
        file_menu.add_command(label="设置", command=self._show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="本地历史记录", command=self._clear_history)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)

        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="撤销")
        edit_menu.add_command(label="重做")
        edit_menu.add_separator()
        edit_menu.add_command(label="剪切")
        edit_menu.add_command(label="复制")
        edit_menu.add_command(label="粘贴")

        # 视图菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="视图", menu=view_menu)
        view_menu.add_checkbutton(label="显示工具栏")
        view_menu.add_checkbutton(label="显示状态栏")

        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="插件")

        # 窗口菜单
        window_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="窗口", menu=window_menu)
        window_menu.add_command(label="最小化", command=self._minimize_window)
        window_menu.add_command(label="最大化", command=self._maximize_window)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self._show_help_docs)
        help_menu.add_separator()
        help_menu.add_command(label="提交反馈",
                              command=lambda: webbrowser.open('http://xiaomizha.ltd/feedback'))
        help_menu.add_separator()
        help_menu.add_command(label="登录注册", command=self._show_login_register)
        help_menu.add_command(label="检查更新", command=self._show_update_check)
        help_menu.add_command(label="关于", command=self._show_about)
        help_menu.add_separator()
        help_menu.add_command(label="服务协议",
                              command=lambda: webbrowser.open('http://xiaomizha.ltd/terms'))
        help_menu.add_command(label="隐私政策",
                              command=lambda: webbrowser.open('http://xiaomizha.ltd/privacy'))

    def _position_window(self, window, width, height):
        """
        设置窗口位置和大小
        :param window: 需要定位的窗口对象
        :param width: 窗口宽度
        :param height: 窗口高度
        """
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f'{width}x{height}+{x}+{y}')

    def _minimize_window(self):
        """
        最小化窗口
        """
        if self.window_state == 'zoomed':
            self.root.state('normal')
            self.window_state = 'normal'
        self.root.geometry('1200x800')

    def _maximize_window(self):
        """
        最大化窗口
        """
        self.root.state('zoomed')
        self.window_state = 'zoomed'

    def _show_settings(self):
        """
        显示设置窗口
        """
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置")
        self._position_window(settings_window, 800, 600)
        settings_window.resizable(False, False)
        settings_window.transient(self.root)

        # 创建左侧菜单和右侧内容区域
        left_frame = ttk.Frame(settings_window, width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        right_frame = ttk.Frame(settings_window)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 左侧菜单选项
        menu_items = {
            "通用": self._show_general_settings,
            "消息通知": self._show_notification_settings,
            "隐私": self._show_privacy_settings,
            "辅助功能": self._show_accessibility_settings,
            "其它": self._show_other_settings
        }

        for item in menu_items:
            btn = ttk.Button(left_frame, text=item, width=20,
                             command=lambda i=item, f=menu_items[item]: self._switch_settings_view(right_frame, i, f))
            btn.pack(pady=2)

        # 默认显示通用设置
        self._show_general_settings(right_frame)

    def _switch_settings_view(self, container, title, view_func):
        """
        切换设置视图
        """
        for widget in container.winfo_children():
            widget.destroy()

        # 添加标题
        ttk.Label(container, text=title, font=('微软雅黑', 14, 'bold')).pack(pady=10)
        view_func(container)

    def _show_general_settings(self, container):
        """
        通用设置
        """
        # 历史记录设置
        history_frame = ttk.LabelFrame(container, text="历史记录", padding=10)
        history_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Checkbutton(history_frame, text="启用历史记录", variable=self.history_enabled).pack()

        # 语音设置
        voice_frame = ttk.LabelFrame(container, text="语音设置", padding=10)
        voice_frame.pack(fill=tk.X, padx=10, pady=5)
        # 播音人选择
        ttk.Label(voice_frame, text="播音人").pack()
        voice_combo = ttk.Combobox(voice_frame, textvariable=self.voice_type,
                                   values=["女声", "男声"],
                                   state='readonly')
        voice_combo.pack(pady=5)
        # 语速设置
        ttk.Label(voice_frame, text="语速").pack()
        speed_scale = ttk.Scale(voice_frame, from_=0.5, to=2.0,
                                variable=self.voice_speed,
                                orient=tk.HORIZONTAL)
        speed_scale.pack(fill=tk.X, pady=5)

    def _show_notification_settings(self, container):
        """
        消息通知设置
        """
        ttk.Label(container, text="消息通知设置开发中...").pack(pady=20)

    def _show_accessibility_settings(self, container):
        """
        辅助功能设置
        """
        ttk.Label(container, text="辅助功能设置开发中...").pack(pady=20)

    def _show_privacy_settings(self, container):
        """
        隐私设置
        """
        ttk.Label(container, text="隐私设置开发中...").pack(pady=20)

    def _show_other_settings(self, container):
        """
        其他设置
        """
        ttk.Label(container, text="其他设置开发中...").pack(pady=20)

    def _show_help_docs(self):
        """
        显示使用说明
        """
        help_window = tk.Toplevel(self.root)
        help_window.title("使用说明")
        self._position_window(help_window, 600, 400)
        help_window.resizable(False, False)

        text = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True)

        help_text = """
    类搜狗翻译使用说明
    
    1. 基本翻译
       - 在左侧输入框输入需要翻译的文本
       - 选择目标语言
       - 点击"翻译文字"按钮或按回车键进行翻译
    
    2. 语音功能（开发中）
       - 点击"朗读"按钮可以听取文本内容
       - 在设置中可以调整语音类型和语速
    
    3. 历史记录
       - 翻译历史会自动保存
       - 可以在设置中开启/关闭历史记录功能
       - 可以通过"清空历史"按钮清除历史记录
    
    4. 其他功能
       - 支持文档翻译（开发中）
       - 支持图片翻译（开发中）
       - 可以通过设置调整软件配置
        """
        text.insert('1.0', help_text)
        text.config(state='disabled')

    def _show_about(self):
        """
        显示关于信息
        """
        about_window = tk.Toplevel(self.root)
        about_window.title("关于类搜狗翻译")
        self._position_window(about_window, 400, 300)
        about_window.resizable(False, False)

        ttk.Label(about_window, text="LOGO", font=('微软雅黑', 24, 'bold')).pack(pady=20)
        ttk.Label(about_window, text="类搜狗翻译", font=('微软雅黑', 16, 'bold')).pack(pady=10)
        ttk.Label(about_window, text="版本: 1.0.0").pack(pady=5)
        # ttk.Label(about_window, text="开发者: xiaomizha").pack(pady=5)
        # ttk.Label(about_window, text="官网: https://xiaomizha.ltd").pack(pady=5)
        author_link = ttk.Label(about_window, text="开发者: xiaomizha", cursor="hand2",
                                foreground="blue")
        author_link.pack(pady=5)
        author_link.bind("<Button-1>", lambda e: webbrowser.open("http://xiaomizha.ltd/"))
        website_link = ttk.Label(about_window, text="官网: http://xiaomizha.ltd/",
                                 cursor="hand2", foreground="blue")
        website_link.pack(pady=5)
        website_link.bind("<Button-1>", lambda e: webbrowser.open("http://xiaomizha.ltd/"))
        repo_link = ttk.Label(about_window, text="开源仓库: GitHub", cursor="hand2",
                              foreground="blue")
        repo_link.pack(pady=5)
        repo_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/xuyouer/"))
        ttk.Label(about_window, text="© 2024 Xiaomizha Ltd. All rights reserved.").pack(pady=20)

    def _show_update_check(self):
        """
        检查更新
        """
        update_window = tk.Toplevel(self.root)
        update_window.title("检查更新")
        self._position_window(update_window, 400, 300)
        update_window.resizable(False, False)

        ttk.Label(update_window, text="当前版本: 1.0.0", font=('微软雅黑', 12)).pack(pady=10)
        ttk.Label(update_window, text="更新功能开发中...").pack(pady=10)

    def _show_login_register(self):
        """
        显示登录注册窗口
        """
        login_window = tk.Toplevel(self.root)
        login_window.title("登录/注册")
        self._position_window(login_window, 400, 300)
        login_window.resizable(False, False)

        notebook = ttk.Notebook(login_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 登录页面
        login_frame = ttk.Frame(notebook)
        notebook.add(login_frame, text="登录")

        ttk.Label(login_frame, text="登录开发中...").pack(pady=20)

        # 注册页面
        register_frame = ttk.Frame(notebook)
        notebook.add(register_frame, text="注册")

        ttk.Label(register_frame, text="注册开发中...").pack(pady=20)

    def _load_history(self):
        """
        加载翻译历史
        """
        try:
            if os.path.exists('translation_history.json'):
                with open('translation_history.json', 'r', encoding='utf-8') as f:
                    self.history_data = json.load(f)
        except Exception:
            self.history_data = []

    def _save_history(self):
        """
        保存翻译历史
        """
        try:
            with open('translation_history.json', 'w', encoding='utf-8') as f:
                json.dump(self.history_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")

    def _generate_signature(self, text: str) -> str:
        """
        生成签名
        :param text: 待翻译文本
        :return: MD5签名
        """
        string = f'auto{self.selected_target_lang.get()}{text}109984457'
        md5 = hashlib.md5()
        md5.update(string.encode('utf-8'))
        return md5.hexdigest()

    def _copy_text(self, text_widget):
        """
        复制文本内容
        """
        self.root.clipboard_clear()
        self.root.clipboard_append(text_widget.get('1.0', tk.END))
        messagebox.showinfo("提示", "已复制到剪贴板")

    def _clear_text_area(self, text_widget):
        """
        清空文本区域
        """
        text_widget.delete('1.0', tk.END)

    def _play_audio(self, text: str, lang: str):
        """
        播放语音
        """
        try:
            speed = self.voice_speed.get()
            voice_type = self.voice_type.get()
            messagebox.showinfo("提示", "语音朗读功能开发中")
            # messagebox.showerror("错误", "语音获取失败")
        except Exception as e:
            messagebox.showerror("错误", f"播放失败: {str(e)}")

    def _add_to_history(self, source: str, target: str):
        """
        添加到历史记录
        """
        history_item = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': source,
            'target': target,
            'target_lang': self.selected_target_lang.get()
        }
        self.history_data.append(history_item)
        self._save_history()
        self._update_history_display()

    def _update_history_display(self):
        """
        更新历史记录显示
        """
        if not self.history_enabled.get():
            self.history_text.delete('1.0', tk.END)
            return

        self.history_text.delete('1.0', tk.END)
        for item in reversed(self.history_data[-10:]):  # 显示最近10条
            self.history_text.insert('1.0',
                                     f"时间: {item['timestamp']}\n"
                                     f"原文: {item['source']}\n"
                                     f"译文: {item['target']}\n"
                                     f"目标语言: {item['target_lang']}\n"
                                     f"{'=' * 80}\n\n\n"
                                     )

    def _clear_history(self):
        """
        清空历史记录
        """
        if messagebox.askyesno("确认", "确定要清空所有历史记录吗？"):
            self.history_data = []
            self._save_history()
            self._update_history_display()

    def _handle_translation(self):
        """处理翻译请求"""
        try:
            input_text = self.input_text.get('1.0', tk.END).strip()
            if not input_text:
                messagebox.showwarning("提示", "请输入要翻译的文本")
                return

            result = self.translate_text(input_text)
            self.output_text.delete('1.0', tk.END)
            self.output_text.insert(tk.INSERT, result)

            # 添加到历史记录
            self._add_to_history(input_text, result)

        except Exception as e:
            messagebox.showerror("错误", f"翻译失败: {str(e)}")

    def _on_language_change(self, event):
        """
        语言选择
        """
        selected_name = self.selected_target_lang.get()
        self.selected_target_lang.set(self.languages[selected_name])

    def translate_text(self, text: str) -> str:
        """
        翻译文本
        :param text: 待翻译文本
        :return: 翻译结果
        """
        if not text.strip():
            return ""

        try:
            signature = self._generate_signature(text)

            json_data = {
                'from': 'auto',
                'to': self.selected_target_lang.get(),
                'text': text,
                'client': 'pc',
                'fr': 'browser_pc',
                'needQc': 1,
                's': signature,
                'uuid': '8708e162-95ed-4c8d-9e7a-ed4dc7b47e1d',
                'exchange': False,
            }

            response = requests.post(
                'https://fanyi.sogou.com/api/transpc/text/result',
                cookies=self.cookies,
                headers=self.headers,
                json=json_data
            )

            if response.status_code == 200:
                resp_json = response.json()
                return resp_json['data']['translate']['dit']
            else:
                raise Exception(f"翻译请求失败: {response.status_code}")

        except Exception as e:
            messagebox.showerror("错误", f"翻译失败: {str(e)}")
            return ""

    def create_gui(self):
        """
        创建图形界面
        """
        # === 菜单栏 ===
        self._create_menu()

        # === LOGO ===
        logo_frame = tk.Frame(self.root)
        logo_frame.pack(fill=tk.X, pady=10)

        logo_label = tk.Label(logo_frame, text="LOGO", font=('微软雅黑', 24))
        logo_label.pack(side=tk.LEFT, padx=20)

        slogan_label = tk.Label(logo_frame, text="查词好, 翻译快", font=('微软雅黑', 20))
        slogan_label.pack(side=tk.LEFT, padx=20)

        # === 功能按钮 ===
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="翻译文字", command=self._handle_translation).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="翻译文档",
                   command=lambda: messagebox.showinfo("提示", "文档翻译功能开发中")).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="翻译图片",
                   command=lambda: messagebox.showinfo("提示", "图片翻译功能开发中")).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="设置",
                   command=self._show_settings).pack(side=tk.RIGHT, padx=10)

        # === 语言选择 ===
        lang_frame = tk.Frame(self.root)
        lang_frame.pack(fill=tk.X, pady=10)

        self.selected_target_lang.set('en')  # 默认英语
        lang_label = tk.Label(lang_frame, text="目标语言: ", font=('微软雅黑', 12))
        lang_label.pack(side=tk.LEFT, padx=10)

        lang_combo = ttk.Combobox(lang_frame,
                                  textvariable=self.selected_target_lang,
                                  values=list(self.languages.keys()),
                                  state='readonly')
        lang_combo.pack(side=tk.LEFT)
        lang_combo.bind('<<ComboboxSelected>>', self._on_language_change)

        # === 翻译区域 ===
        trans_frame = tk.Frame(self.root)
        trans_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 左侧原文
        left_frame = tk.Frame(trans_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        self.input_text = tk.Text(left_frame, font=('微软雅黑', 12), height=10)
        self.input_text.pack(fill=tk.BOTH, expand=True)

        left_button_frame = tk.Frame(left_frame)
        left_button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(left_button_frame, text="复制",
                   command=lambda: self._copy_text(self.input_text)).pack(side=tk.LEFT, padx=5)
        ttk.Button(left_button_frame, text="朗读",
                   command=lambda: self._play_audio(self.input_text.get('1.0', tk.END), 'auto')).pack(side=tk.LEFT,
                                                                                                      padx=5)
        ttk.Button(left_button_frame, text="清空",
                   command=lambda: self._clear_text_area(self.input_text)).pack(side=tk.LEFT, padx=5)

        # 右侧译文
        right_frame = tk.Frame(trans_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        self.output_text = tk.Text(right_frame, font=('微软雅黑', 12), height=10)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        right_button_frame = tk.Frame(right_frame)
        right_button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(right_button_frame, text="复制",
                   command=lambda: self._copy_text(self.output_text)).pack(side=tk.LEFT, padx=5)
        ttk.Button(right_button_frame, text="朗读",
                   command=lambda: self._play_audio(self.output_text.get('1.0', tk.END),
                                                    self.selected_target_lang.get())).pack(side=tk.LEFT, padx=5)
        ttk.Button(right_button_frame, text="清空",
                   command=lambda: self._clear_text_area(self.output_text)).pack(side=tk.LEFT, padx=5)

        # === 历史记录 ===
        history_frame = tk.Frame(self.root)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        history_label = tk.Label(history_frame, text="翻译历史", font=('微软雅黑', 12))
        history_label.pack()

        self.history_text = tk.Text(history_frame, font=('微软雅黑', 10), height=8)
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=10)

        history_button_frame = tk.Frame(history_frame)
        history_button_frame.pack(fill=tk.X, padx=10)

        ttk.Button(history_button_frame, text="清空历史",
                   command=self._clear_history).pack(side=tk.RIGHT)

        # 更新历史记录显示
        self._update_history_display()

        # 绑定回车键
        self.root.bind('<Return>', lambda event: self._handle_translation())

    def run(self):
        """
        运行应用
        """
        self.create_gui()
        self.root.mainloop()


def main():
    sogou = SoGouTranslator()
    sogou.run()


if __name__ == '__main__':
    main()
