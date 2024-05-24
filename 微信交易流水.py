"""
微信交易流水

    pip install pandas
    pip install openpyxl
"""

import os
import csv
import re
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

# 充值/提现/理财通购买/零钱通存取/信用卡还款等交易，将计入中性交易

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


# 提取 基本信息
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


# 提取 交易明细列表
def extract_transaction_details(row):
    # 所有列存在
    # 去除每列的\t字符
    row = [col.strip('\t') for col in row]
    if len(row) >= 10:
        transaction = {
            '交易时间': row[0],
            '交易类型': row[1],
            '交易对方': row[2],
            '商品': row[3],
            '收支类型': row[4],
            '金额(元)': float(row[5][1:]) if row[5].startswith('¥') else float(row[5]),  # 去除金额前的符号
            '支付方式': row[6],
            '当前状态': row[7],
            '交易单号': row[8],
            '商户单号': row[9],
            '备注': row[10] if len(row) > 10 else ""
        }
        transactions.append(transaction)


# 解析
def parse_csv_file(file_path):
    # 标记, 是否跳过基本统计信息
    header_passed = False

    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            # 处理基本信息
            if not header_passed:
                # 当遇到交易时间列时，表明基本信息结束
                if row and '交易时间' in row[0]:
                    header_passed = True
                else:
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
            # 处理交易明细列表
            else:
                extract_transaction_details(row)


# 解析 多个csv
def parse_csv_files(directory_path):
    for filename in os.listdir(directory_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory_path, filename)
            parse_csv_file(file_path)
            print(f"读取 '{file_path}' OK")


# 使用多线程解析CSV文件
def parse_csv_files_multithreaded(directory_path):
    files = [os.path.join(directory_path, filename) for filename in os.listdir(directory_path) if
             filename.endswith('.csv')]
    with ThreadPoolExecutor() as executor:
        executor.map(parse_csv_file, files)
    print("CSV文件读取 OK")


# 去重
def deduplicate_transactions(transactions):
    # 使用DataFrame进行去重
    df = pd.DataFrame(transactions)
    df.drop_duplicates(inplace=True, ignore_index=True)
    return df.to_dict('records')


# 将交易记录保存到CSV文件
def save_transactions_to_csv(transactions, output_file):
    """
    将交易记录列表保存到指定的CSV文件中

    :param transactions: 交易记录的列表
    :param output_file: 输出的CSV文件路径
    """
    with open(output_file, mode='w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['交易时间', '交易类型', '交易对方', '商品', '收支类型',
                      '金额(元)', '支付方式', '当前状态', '交易单号', '商户单号', '备注']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for transaction in transactions:
            writer.writerow(transaction)
    print(f"交易记录 '{output_file}' OK")


# 将交易记录保存到Excel文件
def save_transactions_to_excel(transactions, output_file):
    """
    将交易记录列表保存到指定的Excel文件中

    :param transactions: 交易记录的列表
    :param output_file: 输出的Excel文件路径
    """
    df = pd.DataFrame(transactions)
    df.to_excel(output_file, index=False, engine='openpyxl')
    print(f"交易记录 '{output_file}' OK")


# 根据微信昵称创建目录并返回目录路径
def create_wechat_directory(nickname):
    directory_path = os.path.join('.', nickname)
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
def post_process_all_files():
    global transactions
    transactions = deduplicate_transactions(transactions)
    print("交易记录去重 OK")

    nickname = data['微信昵称']

    # 写入统计信息
    directory_path = create_wechat_directory(nickname)
    write_data_to_txt(nickname, data, directory_path)

    # 写入csv文件
    nickname_output_csv = os.path.join(directory_path, f"{nickname}_交易流水.csv")
    save_transactions_to_csv(transactions, nickname_output_csv)

    # 写入excel文件
    nickname_output_excel = os.path.join(directory_path, f"{nickname}_交易流水.xlsx")
    save_transactions_to_excel(transactions, nickname_output_excel)

    print(f"'{nickname}' 的数据 OK")


# 倒计时
def countdown(seconds):
    print(" " * 10 + "\n", end='', flush=True)
    for i in range(seconds, 0, -1):
        # '\r'回到行首, end=''防止换行, flush=True确保立即输出
        print(f"剩余时间: {i} 秒", end='\r', flush=True)
        time.sleep(1)


def test():
    # CSV文件路径
    # csv_file_path = '微信支付账单(20230701-20231001).csv'
    csv_file_paths = './'
    csv_file_paths = input("请输入CSV文件所在目录的路径（直接回车默认为当前目录）: ")
    csv_file_paths = csv_file_paths if csv_file_paths else './'
    print(f"正在处理目录 '{csv_file_paths}' 下的CSV文件...")

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

if __name__ == '__main__':
    test()
    countdown(5)
