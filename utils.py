from colorama import Fore, Style, init
import filetype
import requests
from mutagen.easyid3 import EasyID3
from mutagen.id3 import USLT
from mutagen.flac import FLAC
from mutagen.mp3 import MP3

init(autoreset=True)
# 向API发起搜索请求，根据参数和是否为批量请求来获取歌词数据
def search_request_mse(params, is_batch=False):
    """
    根据参数和是否为批量请求，向API发起搜索请求并返回结果。

    参数:
    params (dict): 请求参数字典。
    is_batch (bool): 是否为批量请求，默认为False。

    返回:
    dict: 解析后的JSON数据，如果请求失败则返回None。
    """
    try:
        # 根据是否为批量请求选择不同的URL
        if is_batch:
            res = requests.get('https://api.lrc.cx/api/v1/lyrics/single', params=params)
        else:
            res = requests.get('https://api.lrc.cx/api/v1/lyrics/advance', params=params)

        # 检查响应状态码
        res.raise_for_status()  # 如果状态码不是200，会抛出HTTPError

        return res.json()  # 返回解析后的JSON数据

    except requests.exceptions.HTTPError as http_err:
        print(f"{err_tip}HTTP错误: {http_err}")  # 打印HTTP错误信息
    except requests.exceptions.RequestException as req_err:
        print(f"{err_tip}请求错误: {req_err}")  # 打印请求相关的错误
    except Exception as e:
        print(f"{err_tip}其他错误: {e}")  # 打印其他类型的错误
    return None  # 如果出错，返回None


# 获取文件类型
def get_file_type(paths):
    """
    获取文件的类型信息，包括MIME类型和文件扩展名。

    参数:
    paths (str): 文件路径。

    返回:
    dict: 包含文件类型的字典，包括MIME类型和文件扩展名。
    """
    kind = filetype.guess(paths)
    return {"file_medium": kind.mime, 'file_type': kind.extension}


# 读取音频文件的元数据，如专辑、标题和艺术家
def read_file_stats(paths):
    """
    读取音频文件的元数据，包括专辑、标题和艺术家信息。

    参数:
    paths (str): 文件路径。

    返回:
    dict: 包含音频文件元数据的字典，如果无法读取则返回None。
    """
    file_extension = get_file_type(paths)['file_type']
    album, title, artist = None, None, None

    # 获取音频文件的统计信息
    def get_stats(audio_data):
        nonlocal album, title, artist  # 使用 nonlocal 使得可以修改外部作用域的变量
        album = audio_data.get('album', [None])[0] if audio_data.get('album') else None  # 唱片集
        title = audio_data.get('title', [None])[0] if audio_data.get('title') else None  # 标题
        artist = audio_data.get('artist', [None])[0] if audio_data.get('artist') else None  # 歌者

    try:
        if file_extension == 'mp3':
            audio = EasyID3(paths)
            get_stats(audio)
        elif file_extension == 'flac':
            audio = FLAC(paths)
            get_stats(audio)

        return {"album": album, "title": title, "artist": artist}
    except Exception as e:
        print(f"[error]: 读取文件属性时出错: {e}")
        return {"album": None, "title": None, "artist": None}


def write_audio_tags(paths, album, title, artist):
    """
    写入音频标签信息到指定路径的音频文件中。

    参数:
    paths (str): 音频文件的路径。
    album (str): 唱片集名称。
    title (str): 音频标题。
    artist (str): 演唱者名称。
    """
    # 获取文件类型
    file_extension = get_file_type(paths)['file_type']
    try:
        if file_extension == 'mp3':
            audio = EasyID3(paths)
            set_stats(audio, album, title, artist)  # 设置 MP3 文件的统计信息

        elif file_extension == 'flac':
            audio = FLAC(paths)
            set_stats(audio, album, title, artist)  # 设置 FLAC 文件的统计信息

    except Exception as e:
        print(f"写入文件属性时出错: {e}")


def set_stats(audio_data, album, title, artist):
    """
    设置音频文件的元数据统计信息。

    参数:
    audio_data: 音频文件的数据对象，用于写入元数据。
    album: 唱片集名称。
    title: 音频标题。
    artist: 演唱者名称。
    lyrics: 歌词文本。
    """
    audio_data['album'] = album  # 唱片集
    audio_data['title'] = title  # 标题
    audio_data['artist'] = artist  # 歌者
    audio_data.save()  # 保存更改
    print(f'{info_tip} 音频属性信息写入成功')


def set_lyrics(lyrics, path):
    """
    设置歌词信息到音频文件中。
    参数:
    lyrics (str): 歌词文本。
    """
    try:
        audio = MP3(path)
        if audio.tags is None:
            audio.add_tags()
        print(lyrics)
        audio.tags.add(USLT(encoding=3, lang='eng', text=lyrics))
        audio.save()
        print(f"{info_tip} Mp3歌词写入成功")
    except Exception as e:
        print(f"{err_tip} 设置歌词时出错: {e}")


err_tip = f'{Fore.YELLOW}[error]: {Style.RESET_ALL}'
info_tip = f'{Fore.GREEN}[info]: {Style.RESET_ALL}'
