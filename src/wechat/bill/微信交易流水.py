"""
微信交易流水
    充值/提现/理财通购买/零钱通存取/信用卡还款等交易, 将计入中性交易

    pip install pandas
    pip install openpyxl
"""

import os
import csv
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText

import pandas as pd


def check_and_install(packages):
    """
    检查给定的Python库是否已安装
    如果没有安装, 则尝试使用pip自动安装

    :param packages: 要检查和安装的Python库名
    :return bool: 安装成功返回True, 如果过程中出现错误则返回False
    """
    if isinstance(packages, str):  # 如果参数是单个字符串, 则转换为列表
        packages = [packages]

    for package in packages:
        try:
            # 尝试导入库, 如果导入失败则说明未安装
            __import__(package)
            print(f"库 {package} 已经安装")
        except ImportError:
            print(f"库 {package} 未安装, 正在尝试自动安装...")
            # 构建pip安装命令
            install_command = [sys.executable, "-m", "pip", "install", package]

            # 执行pip安装命令
            try:
                subprocess.check_call(install_command)
                print(f"库 {package} 安装成功")
            except subprocess.CalledProcessError as error:
                print(f"安装 {package} 时发生错误: {error}")


# 初始化
def initial_package():
    packages = ['pandas', 'openpyxl']
    check_and_install(packages)


# 用于存储解析后的数据
data = {
    '微信昵称': '',
    '总笔数': 0,
    '收入': {'笔数': 0, '总额': 0.0},
    '支出': {'笔数': 0, '总额': 0.0},
    '中性交易': {'笔数': 0, '总额': 0.0},
}
# 存储交易明细列表
transactions = []
# 表头行数据
header = None


# 提取 微信昵称
def extract_wechat_nickname(row):
    match = re.search(r'\[(.*?)\]', row[0])
    return match.group(1).strip() if match else '未找到匹配的微信昵称'


# 提取 总笔数
def extract_total_transactions(row):
    match = re.search(r'共(\d+)笔记录', row[0])
    return int(match.group(1)) if match else 0


# 提取 笔数 和 金额
def extract_financial_info(row, key):
    match = re.match(rf'{key}：(\d+)笔\s+(\d+\.\d+)元', row[0])
    return {f'{key}笔数': int(match.group(1)), f'{key}总额': float(match.group(2))} if match else {f'{key}笔数': 0,
                                                                                                   f'{key}总额': 0.0}


# 获取交易明细表头行及其列名
def find_header_row(file_path):
    global header
    if header is not None:
        return header  # 如果表头已找到, 则直接返回
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            if all(col.strip() for col in row):  # 确保这一行非空
                if '交易时间' in row[0]:  # 或其他能标志明细开始的关键字
                    header = [col.strip() for col in row]
                    return header
    return None


# 提取 基本统计信息
def extract_basic_info(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            # 提取微信昵称
            if row and '微信昵称：' in row[0]:
                data['微信昵称'] = extract_wechat_nickname(row)
            # 提取总笔数
            elif row and '共' in row[0] and '笔记录' in row[0]:
                data['总笔数'] += extract_total_transactions(row)
            # 提取收入信息
            elif row and '收入：' in row[0]:
                financial_data = extract_financial_info(row, '收入')
                data['收入']['笔数'] += financial_data['收入笔数']
                data['收入']['总额'] += financial_data['收入总额']
            # 提取支出信息
            elif row and '支出：' in row[0]:
                financial_data = extract_financial_info(row, '支出')
                data['支出']['笔数'] += financial_data['支出笔数']
                data['支出']['总额'] += financial_data['支出总额']
            # 提取中性交易信息
            elif row and '中性交易：' in row[0]:
                financial_data = extract_financial_info(row, '中性交易')
                data['中性交易']['笔数'] += financial_data['中性交易笔数']
                data['中性交易']['总额'] += financial_data['中性交易总额']


# 提取 交易明细列表 动态获取表头
def extract_transaction_details(file_path):
    global header
    header = find_header_row(file_path)
    if header is None:
        print("交易明细表头未找到")
        return

    # transactions.clear()  # 清空之前的交易记录
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header_passed = False  # 标记是否开始读取交易明细

        for row in reader:
            # 当遇到交易时间列时，表明基本信息结束
            if row and '交易时间' in row[0]:
                header_passed = True
                continue  # 跳过此行, 下一行开始读取数据

            if header_passed and header:  # 当找到起始行且表头不为空时开始处理交易明细
                # if len(row) != len(header):  # 检查行长度与表头长度是否一致，避免格式错误
                #     continue

                transaction = dict(zip(header, (col.strip() for col in row)))

                # 处理金额字段
                if '金额(元)' in transaction and transaction['金额(元)'].startswith('¥'):
                    transaction['金额(元)'] = float(transaction['金额(元)'][1:])
                else:
                    transaction['金额(元)'] = float(transaction['金额(元)']) if transaction['金额(元)'] else 0.0

                transactions.append(transaction)


# 调用
def parse_csv_file(file_path):
    # 提取 统计信息
    extract_basic_info(file_path)
    # 提取 交易明细列表
    extract_transaction_details(file_path)


# 解析 多个csv
def parse_csv_files(directory_path):
    for filename in os.listdir(directory_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory_path, filename)
            parse_csv_file(file_path)
            print(f"读取 '{file_path}' OK")
            log_message(f"读取 '{file_path}' OK")


# 使用多线程解析CSV文件
def parse_csv_files_multithreaded(directory_path):
    files = [os.path.join(directory_path, filename) for filename in os.listdir(directory_path) if
             filename.endswith('.csv')]
    with ThreadPoolExecutor() as executor:
        executor.map(parse_csv_file, files)
    print("CSV文件读取 OK")
    log_message("CSV文件读取 OK")


# 去重
def deduplicate_transactions(transactions):
    # 使用DataFrame进行去重
    df = pd.DataFrame(transactions)
    df.drop_duplicates(inplace=True, ignore_index=True)
    return df.to_dict('records')


# 将交易记录保存到CSV文件 动态获取表头
def save_transactions_to_csv(transactions, output_dir):
    """
    将交易记录列表保存到指定的CSV文件中

    :param transactions: 交易记录的列表
    :param output_dir: 输出的CSV文件路径
    """
    if header is None:
        print("交易明细表头未找到")
        return

    with open(output_dir, mode='w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        for transaction in transactions:
            # 仅写入存在的列
            writer.writerow({k: v for k, v in transaction.items() if k in header})
    print(f"交易记录 '{output_dir}' OK")
    log_message(f"交易记录 '{output_dir}' OK")


# 将交易记录保存到Excel文件
def save_transactions_to_excel(transactions, output_dir):
    """
    将交易记录列表保存到指定的Excel文件中

    :param transactions: 交易记录的列表
    :param output_dir: 输出的Excel文件路径
    """
    df = pd.DataFrame(transactions)
    df.to_excel(output_dir, index=False, engine='openpyxl')
    print(f"交易记录 '{output_dir}' OK")
    log_message(f"交易记录 '{output_dir}' OK")


# 根据微信昵称创建目录并返回目录路径
def create_wechat_directory(nickname, output_dir='./'):
    directory_path = os.path.join(output_dir, nickname)
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    return directory_path


# 写入/更新微信昵称的统计信息到txt文件
def write_data_to_txt(nickname, data, directory_path):
    txt_path = os.path.join(directory_path, f'{nickname}.txt')
    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(f"微信昵称: {data['微信昵称']}\n")
        txt_file.write(f"总笔数: {data['总笔数']}\n")
        txt_file.write(f"收入笔数: {data['收入']['笔数']}\n")
        txt_file.write(f"收入总额: {data['收入']['总额']:.2f}\n")
        txt_file.write(f"支出笔数: {data['支出']['笔数']}\n")
        txt_file.write(f"支出总额: {data['支出']['总额']:.2f}\n")
        txt_file.write(f"中性交易笔数: {data['中性交易']['笔数']}\n")
        txt_file.write(f"中性交易总额: {data['中性交易']['总额']:.2f}\n")
        txt_file.write(f"注:\n")
        txt_file.write(f"1. 中性交易: 充值/提现/理财通购买/零钱通存取/信用卡还款等交易\n")
        txt_file.write(f"2. 下载账单时, 选择的起始时间需与前一份账单的终止时间相连, 否则会有重复统计的数据\n"
                       f"\t例如: 第一份账单时间为 20230701-20231001, 第二份账单起始时间则为 20231002\n")
        txt_file.write(f"3. 请以最终的交易流水为准\n")
        txt_file.write(f"4. 账单下载步骤:\n"
                       f"\t微信: 微信 => 我 => 服务 => 钱包 => 账单 => 常见问题 => 下载账单\n"
                       f"\t支付宝: 支付宝 => 我的 => 账单 => 右上角三点 => 开具交易流水证明\n")
        txt_file.write(f"\n")


# 在解析完所有文件后, 对交易明细列表进行去重, 执行后续操作
def post_process_all_files(output_dir='./'):
    global transactions
    transactions = deduplicate_transactions(transactions)
    print("交易记录去重 OK")
    log_message("交易记录去重 OK")

    nickname = data['微信昵称']

    # 写入统计信息
    directory_path = create_wechat_directory(nickname, output_dir)
    write_data_to_txt(nickname, data, directory_path)

    # 写入csv文件
    nickname_output_csv = os.path.join(directory_path, f"{nickname}_交易流水.csv")
    save_transactions_to_csv(transactions, nickname_output_csv)

    # 写入excel文件
    nickname_output_excel = os.path.join(directory_path, f"{nickname}_交易流水.xlsx")
    save_transactions_to_excel(transactions, nickname_output_excel)

    # 重置统计数据
    reset_data()

    print(f"'{nickname}' 的数据 OK")
    log_message(f"'{nickname}' 的数据 OK")


# 倒计时
def countdown(seconds):
    print(" " * 10 + "\n", end='', flush=True)
    for i in range(seconds, 0, -1):
        # '\r'回到行首, end=''防止换行, flush=True确保立即输出
        print(f"剩余时间: {i} 秒", end='\r', flush=True)
        time.sleep(1)


# 重置统计数据
def reset_data():
    data['总笔数'] = 0
    data['收入']['笔数'] = 0
    data['收入']['总额'] = 0.0
    data['支出']['笔数'] = 0
    data['支出']['总额'] = 0.0
    data['中性交易']['笔数'] = 0
    data['中性交易']['总额'] = 0.0


def test():
    # CSV文件路径
    csv_file_path = '微信支付账单(20230701-20231001).csv'
    # csv_file_paths = './'
    csv_file_paths = input("请输入CSV文件所在目录的路径（直接回车默认为当前目录）: ")
    csv_file_paths = csv_file_paths if csv_file_paths else './'
    print(f"开始处理目录 '{csv_file_paths}' 下的CSV文件...")

    # 调用函数解析文件
    # parse_csv_file(csv_file_path)
    # parse_csv_files(csv_file_paths)
    # 使用多线程解析文件
    parse_csv_files_multithreaded(csv_file_paths)

    # 打印基本信息
    # print(data)

    # 打印交易记录
    # for i, transaction in enumerate(transactions[:5]):
    #     print(f"Transaction {i + 1}: {transaction}")

    # 去重交易记录, 执行后续操作
    post_process_all_files()


"""
整理EXCEL表格
    1. CTRL + A 选中表格数据
    2. CTRL + T
    3. 点击确认
"""


# if __name__ == '__main__':
#     test()
#     countdown(5)


# 退出应用程序
def exit_program():
    root.destroy()


# 获取用户选择的输入目录
def on_select_input_directory():
    global input_dir
    input_dir = filedialog.askdirectory()
    if input_dir:
        log_message(f"输入目录: {input_dir}")
    else:
        input_dir = "./"
        log_message("输入目录: 未选择, 默认使用当前目录")


# 获取用户选择的输出目录
def on_select_output_directory():
    global output_dir
    output_dir = filedialog.askdirectory()
    if output_dir:
        log_message(f"输出目录: {output_dir}")
    else:
        output_dir = "./"
        log_message("输出目录: 未选择, 默认使用当前目录")


# 传入用户选择的目录
def process_selected_directory(input_dir='./', output_dir='./'):
    csv_file_paths = input_dir
    log_message(f"开始处理目录 '{csv_file_paths}' 下的CSV文件...")
    # 多线程读取CSV文件
    parse_csv_files_multithreaded(csv_file_paths)
    # 后续处理
    post_process_all_files(output_dir)
    log_message("处理完成\n")


# 开始处理
def process():
    process_selected_directory(input_dir, output_dir)


# 日志打印
def log_message(message):
    log.insert(tk.END, message + "\n")  # 在ScrolledText的末尾插入新消息
    log.see(tk.END)  # 滚动到底部
    root.update_idletasks()  # 更新UI


# 窗口大小和位置设置
def window_setup(root, width=600, height=450):
    window_width = width
    window_height = height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')


# 设置图标
def set_window_icon(root, icon_path):
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)


# 选择目录
def create_directory_selector(root, label_text, cmd_function, button_text):
    frame = tk.Frame(root)
    frame.pack(fill=tk.X, padx=20, pady=(20, 10))
    tk.Label(frame, text=label_text, font=("宋体", 12)).pack(side=tk.LEFT)
    tk.Button(frame, text=button_text,
              command=lambda: cmd_function(),
              font=("宋体", 12),
              borderwidth=1,
              relief='solid',
              padx=5,
              pady=2).pack(side=tk.LEFT, padx=5)


# 日志区域
def setup_log_area(root):
    log_frame = tk.Frame(root)
    log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    global log
    log = ScrolledText(log_frame, height=10)
    log.pack(fill=tk.BOTH, expand=True)


# 默认日志
def log_initial_message():
    log_message("默认输入目录: 当前目录")
    log_message("默认输出目录: 当前目录\n")


def main_gui():
    global root, log, input_dir, output_dir

    # 初始化目录
    input_dir = "./"
    output_dir = "./"

    # 初始化Tkinter应用
    root = tk.Tk()
    root.title("微信交易记录分析工具")

    # 设置窗口大小
    window_setup(root)

    # 设置窗口图标
    set_window_icon(root, "favicon.ico")

    # 输入目录选择
    create_directory_selector(root, "选择CSV文件所在目录:", on_select_input_directory, "浏览")

    # 输出目录选择
    create_directory_selector(root, "选择输出目录:", on_select_output_directory, "浏览")

    # 日志展示区域
    setup_log_area(root)

    # 显示默认目录的日志信息
    log_initial_message()

    # 处理按钮
    tk.Button(root, text="开始处理",
              command=process,
              font=("宋体", 12),
              borderwidth=1,
              relief='solid',
              padx=5,
              pady=2).pack(side=tk.LEFT, padx=20, pady=20)

    # 退出按钮
    tk.Button(root, text="退出",
              command=exit_program,
              font=("宋体", 12),
              borderwidth=1,
              relief='solid',
              padx=5,
              pady=2).pack(side=tk.RIGHT, padx=20, pady=20)

    # 循环
    root.mainloop()


if __name__ == '__main__':
    initial_package()
    main_gui()
