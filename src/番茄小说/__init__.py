"""
番茄小说

"""

from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import requests
import parsel
import json
import re
import os

cookie = {
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
}

# 字典表
glyf_dict = {
    '58670': '0',
    '58413': '1',
    '58678': '2',
    '58371': '3',
    '58353': '4',
    '58480': '5',
    '58359': '6',
    '58449': '7',
    '58540': '8',
    '58692': '9',
    '58712': 'a',
    '58542': 'b',
    '58575': 'c',
    '58626': 'd',
    '58691': 'e',
    '58561': 'f',
    '58362': 'g',
    '58619': 'h',
    '58430': 'i',
    '58531': 'j',
    '58588': 'k',
    '58440': 'l',
    '58681': 'm',
    '58631': 'n',
    '58376': 'o',
    '58429': 'p',
    '58555': 'q',
    '58498': 'r',
    '58518': 's',
    '58453': 't',
    '58397': 'u',
    '58356': 'v',
    '58435': 'w',
    '58514': 'x',
    '58482': 'y',
    '58529': 'z',
    '58515': 'A',
    '58688': 'B',
    '58709': 'C',
    '58344': 'D',
    '58656': 'E',
    '58381': 'F',
    '58576': 'G',
    '58516': 'H',
    '58463': 'I',
    '58649': 'J',
    '58571': 'K',
    '58558': 'L',
    '58433': 'M',
    '58517': 'N',
    '58387': 'O',
    '58687': 'P',
    '58537': 'Q',
    '58541': 'R',
    '58458': 'S',
    '58390': 'T',
    '58466': 'U',
    '58386': 'V',
    '58697': 'W',
    '58519': 'X',
    '58511': 'Y',
    '58634': 'Z',
    '58611': '的',
    '58590': '一',
    '58398': '是',
    '58422': '了',
    '58657': '我',
    '58666': '不',
    '58562': '人',
    '58345': '在',
    '58510': '他',
    '58496': '有',
    '58654': '这',
    '58441': '个',
    '58493': '上',
    '58714': '们',
    '58618': '来',
    '58528': '到',
    '58620': '时',
    '58403': '大',
    '58461': '地',
    '58481': '为',
    '58700': '子',
    '58708': '中',
    '58503': '你',
    '58442': '说',
    '58639': '生',
    '58506': '国',
    '58663': '年',
    '58436': '着',
    '58563': '就',
    '58391': '那',
    '58357': '和',
    '58354': '要',
    '58695': '她',
    '58372': '出',
    '58696': '也',
    '58551': '得',
    '58445': '里',
    '58408': '后',
    '58599': '自',
    '58424': '以',
    '58394': '会',
    '58348': '家',
    '58426': '可',
    '58673': '下',
    '58417': '而',
    '58556': '过',
    '58603': '天',
    '58565': '去',
    '58604': '能',
    '58522': '对',
    '58632': '小',
    '58622': '多',
    '58350': '然',
    '58605': '于',
    '58617': '心',
    '58401': '学',
    '58637': '么',
    '58684': '之',
    '58382': '都',
    '58464': '好',
    '58487': '看',
    '58693': '起',
    '58608': '发',
    '58392': '当',
    '58474': '没',
    '58601': '成',
    '58355': '只',
    '58573': '如',
    '58499': '事',
    '58469': '把',
    '58361': '还',
    '58698': '用',
    '58489': '第',
    '58711': '样',
    '58457': '道',
    '58635': '想',
    '58492': '作',
    '58647': '种',
    '58623': '开',
    '58521': '美',
    '58609': '总',
    '58530': '从',
    '58665': '无',
    '58652': '情',
    '58676': '己',
    '58456': '面',
    '58581': '最',
    '58509': '女',
    '58488': '但',
    '58363': '现',
    '58685': '前',
    '58396': '些',
    '58523': '所',
    '58471': '同',
    '58485': '日',
    '58613': '手',
    '58533': '又',
    '58589': '行',
    '58527': '意',
    '58593': '动',
    '58699': '方',
    '58707': '期',
    '58414': '它',
    '58596': '头',
    '58570': '经',
    '58660': '长',
    '58364': '儿',
    '58526': '回',
    '58501': '位',
    '58638': '分',
    '58404': '爱',
    '58677': '老',
    '58535': '因',
    '58629': '很',
    '58577': '给',
    '58606': '名',
    '58497': '法',
    '58662': '间',
    '58479': '斯',
    '58532': '知',
    '58380': '世',
    '58385': '什',
    '58405': '两',
    '58644': '次',
    '58578': '使',
    '58505': '身',
    '58564': '者',
    '58412': '被',
    '58686': '高',
    '58624': '已',
    '58667': '亲',
    '58607': '其',
    '58616': '进',
    '58368': '此',
    '58427': '话',
    '58423': '常',
    '58633': '与',
    '58525': '活',
    '58543': '正',
    '58418': '感',
    '58597': '见',
    '58683': '明',
    '58507': '问',
    '58621': '力',
    '58703': '理',
    '58438': '尔',
    '58536': '点',
    '58384': '文',
    '58484': '几',
    '58539': '定',
    '58554': '本',
    '58421': '公',
    '58347': '特',
    '58569': '做',
    '58710': '外',
    '58574': '孩',
    '58375': '相',
    '58645': '西',
    '58592': '果',
    '58572': '走',
    '58388': '将',
    '58370': '月',
    '58399': '十',
    '58651': '实',
    '58546': '向',
    '58504': '声',
    '58419': '车',
    '58407': '全',
    '58672': '信',
    '58675': '重',
    '58538': '三',
    '58465': '机',
    '58374': '工',
    '58579': '物',
    '58402': '气',
    '58702': '每',
    '58553': '并',
    '58360': '别',
    '58389': '真',
    '58560': '打',
    '58690': '太',
    '58473': '新',
    '58512': '比',
    '58653': '才',
    '58704': '便',
    '58545': '夫',
    '58641': '再',
    '58475': '书',
    '58583': '部',
    '58472': '水',
    '58478': '像',
    '58664': '眼',
    '58586': '等',
    '58568': '体',
    '58674': '却',
    '58490': '加',
    '58476': '电',
    '58346': '主',
    '58630': '界',
    '58595': '门',
    '58502': '利',
    '58713': '海',
    '58587': '受',
    '58548': '听',
    '58351': '表',
    '58547': '德',
    '58443': '少',
    '58460': '克',
    '58636': '代',
    '58585': '员',
    '58625': '许',
    '58694': '稜',
    '58428': '先',
    '58640': '口',
    '58628': '由',
    '58612': '死',
    '58446': '安',
    '58468': '写',
    '58410': '性',
    '58508': '马',
    '58594': '光',
    '58483': '白',
    '58544': '或',
    '58495': '住',
    '58450': '难',
    '58643': '望',
    '58486': '教',
    '58406': '命',
    '58447': '花',
    '58669': '结',
    '58415': '乐',
    '58444': '色',
    '58549': '更',
    '58494': '拉',
    '58409': '东',
    '58658': '神',
    '58557': '记',
    '58602': '处',
    '58559': '让',
    '58610': '母',
    '58513': '父',
    '58500': '应',
    '58378': '直',
    '58680': '字',
    '58352': '场',
    '58383': '平',
    '58454': '报',
    '58671': '友',
    '58668': '关',
    '58452': '放',
    '58627': '至',
    '58400': '张',
    '58455': '认',
    '58416': '接',
    '58552': '告',
    '58614': '入',
    '58582': '笑',
    '58534': '内',
    '58701': '英',
    '58349': '军',
    '58491': '候',
    '58467': '民',
    '58365': '岁',
    '58598': '往',
    '58425': '何',
    '58462': '度',
    '58420': '山',
    '58661': '觉',
    '58615': '路',
    '58648': '带',
    '58470': '万',
    '58377': '男',
    '58520': '边',
    '58646': '风',
    '58600': '解',
    '58431': '叫',
    '58715': '任',
    '58524': '金',
    '58439': '快',
    '58566': '原',
    '58477': '吃',
    '58642': '妈',
    '58437': '变',
    '58411': '通',
    '58451': '师',
    '58395': '立',
    '58369': '象',
    '58706': '数',
    '58705': '四',
    '58379': '失',
    '58567': '满',
    '58373': '战',
    '58448': '远',
    '58659': '格',
    '58434': '士',
    '58679': '音',
    '58432': '轻',
    '58689': '目',
    '58591': '条',
    '58682': '呢'
}

# 初始状态
initial_state = {}

# 作者信息
author = {
    'id': '',  # 作者ID
    'name': '',  # 作者名
    'avatarUri': '',  # 作者头像
    'description': '',  # 作者简介
}

# 图书信息
book = {
    'id': '',  # 作品ID
    'name': '',  # 作品名
    'categoryV2': [],  # 作品标签
    'abstract': '',  # 作品简介
    'lastChapterTitle': '',  # 最新章节名
    'lastChapterItemId': '',  # 最新章节ID
    'volumeNameList': [],  # 分卷信息
    'chapterListWithVolume': [],  # 章节信息
    'chaptersByVolume ': {},  # 对 chapterListWithVolume 按 volume_name 分组章节
    'itemIds': [],  # 所有章节ID
}


def extract_initial_state(html_content):
    """
    从HTML中提取初始化状态
    :param html_content
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    # script_tag = soup.find('script', string=re.compile(r'window.__INITIAL_STATE__'))
    script_tag = soup.find('script', string=lambda text: 'window.__INITIAL_STATE__' in str(text))

    if script_tag:
        json_str = re.search(r'window.__INITIAL_STATE__\s*=\s*({.*?});', str(script_tag), re.DOTALL).group(1)
        return json.loads(json_str)
    return None


def get_initial_state(html_content):
    """
    设置初始化信息
    :param html_content
    """
    global initial_state
    initial_state = extract_initial_state(html_content)

    if initial_state:
        page = initial_state['page']

        # 作者信息
        author.update({
            'id': page.get('authorId'),
            'name': page.get('author'),
            'avatarUri': page.get('avatarUri'),
            'description': page.get('description')
        })

        # 图书信息
        book.update({
            'id': page.get('bookId'),
            'name': page.get('bookName'),
            'categoryV2': [item["Name"] for item in json.loads(page.get('categoryV2'))],
            'abstract': page.get('abstract'),
            'lastChapterTitle': page.get('lastChapterTitle'),
            'lastChapterItemId': page.get('lastChapterItemId'),
            'volumeNameList': page.get('volumeNameList'),
            'itemIds': page.get('itemIds'),
            'chapterListWithVolume': [],
            'chaptersByVolume': {},
        })

        # 图书信息
        book['chapterListWithVolume'] = [
            chapter for volume in page.get('chapterListWithVolume', [])
            # for chapter in volume
            for chapter in volume if isinstance(chapter, dict)
        ]

        # 处理章节信息
        for chapter in book['chapterListWithVolume']:
            volume_name = chapter.get('volume_name')
            if volume_name and volume_name not in book['chaptersByVolume']:
                book['chaptersByVolume'][volume_name] = []
            if volume_name:
                book['chaptersByVolume'][volume_name].append({
                    'itemId': chapter.get('itemId'),
                    'title': chapter.get('title')
                })
    else:
        print("No __INITIAL_STATE__ found")


def create_author_dir():
    """
    创建作者名字命名的目录
    """
    author_dir = author['name']
    if not os.path.exists(author_dir):
        os.makedirs(author_dir)
    print(f"{author['name']} DIR CREATED OK")


def fetch_chapter_content(item_id):
    """
    获取章节内容
    :param item_id 章节ID
    """
    url = f'https://fanqienovel.com/reader/{item_id}'
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        select = parsel.Selector(response.text)
        chapter_title = select.xpath('string(//h1[@class="muye-reader-title"])').get()
        content_list = select.xpath('//div[@class="muye-reader-content noselect"]//text()').getall()
        content_list = ['\t' + t.strip() for t in content_list]

        content = '\n'.join(content_list)
        if glyf_dict:
            content = ''.join(glyf_dict.get(str(ord(c)), c) for c in content)

        # content_list = '\n'.join(content_list)
        # content = ''
        # for t in content_list:
        #     # print(ord(t))
        #     try:
        #         t1 = glyf_dict[str(ord(t))]
        #     except:
        #         t1 = t
        #     # print(t1, end='')
        #     content += t1
        
        print(f"{chapter_title} DOWNLOAD OK")
        return content
    return None


def write_book_to_file():
    """
    写入作者和书籍信息
    """
    with open(f'{author["name"]}/{book["name"]}.txt', 'w', encoding='utf-8') as file:
        file.write(f'作者: {author["name"]}\n')
        file.write(f'作者简介: {author["description"]}\n\n')
        file.write(f'书籍: {book["name"]}\n')
        file.write(f"最新章节: {book['lastChapterTitle']}\n")
        file.write(f'书籍简介: \n{book["abstract"]}\n\n')
    print(f"{author["name"]}/{book["name"]}.txt CREATED OK ")


def write_chapter_to_file(volume_name, chapter_title, content):
    """
    写入章节内容到TXT文件
    :param volume_name      分卷名
    :param chapter_title    章节名
    :param content          章节内容
    """
    with open(f'{author["name"]}/{book["name"]}.txt', 'a', encoding='utf-8') as file:
        file.write(f'\n\n\n{volume_name} - ')
        file.write(f'{chapter_title}\n')
        file.write(f'{content}\n')
    print(f"{chapter_title} DOWNLOAD OK")


def write_sorted_chapters_to_file(chapters_data):
    """
    写入排序后的章节内容到TXT文件
    :param chapters_data 所有章节数据
    """
    sorted_chapters = sorted(chapters_data, key=lambda x: x['item_id'])
    with open(f'{author["name"]}/{book["name"]}.txt', 'a', encoding='utf-8') as file:
        for chapter in sorted_chapters:
            file.write(f"\n\n\n{chapter['volume_name']} - ")
            file.write(f"{chapter['chapter_title']}\n")
            file.write(f'{chapter['content']}\n')


def thread_download():
    """
    使用多线程下载章节内容
    """
    with ThreadPoolExecutor(max_workers=10) as executor:
        for volume_name, chapters in book['chaptersByVolume'].items():
            for chapter in chapters:
                item_id = chapter['itemId']
                chapter_title = chapter['title']
                future = executor.submit(fetch_chapter_content, item_id)
                future.add_done_callback(
                    lambda fut, title=chapter_title, vol=volume_name: write_chapter_to_file(vol, title, fut.result()))
    print(f"{author["name"]}/{book["name"]}.txt DOWNLOAD OK")


def thread_sorted_download():
    """
    使用多线程下载排序后的章节内容
    """
    all_chapters = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for volume_name, chapters in book['chaptersByVolume'].items():
            for chapter in chapters:
                future = executor.submit(fetch_chapter_content, chapter['itemId'])
                futures.append((future, chapter['itemId'], chapter['title'], volume_name))
        # 收集所有章节数据
        for future, item_id, chapter_title, volume_name in futures:
            content = future.result()
            if content is not None:
                all_chapters.append({
                    'item_id': item_id,
                    'chapter_title': chapter_title,
                    'volume_name': volume_name,
                    'content': content
                })
    # 写入排序后的章节到文件
    write_sorted_chapters_to_file(all_chapters)
    print(f"{author["name"]}/{book["name"]}.txt DOWNLOAD OK")


def get_book_url(book_id):
    return f"https://fanqienovel.com/page/{book_id}"


# 主函数
def main(url):
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        get_initial_state(response.text)

    create_author_dir()  # 创建作者目录
    write_book_to_file()  # 写入作者和书籍信息
    # thread_download()  # 下载章节内容
    thread_sorted_download()  # 下载章节内容


if __name__ == '__main__':
    url = input("请输入URL: ")
    main(url)
    pass
