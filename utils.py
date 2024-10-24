from colorama import Fore, Style, init
import filetype
import requests
from mutagen.easyid3 import EasyID3
from mutagen.id3 import USLT, APIC, ID3
from mutagen.flac import FLAC, Picture
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
        print(f"{ErrTip}HTTP错误: {http_err}")  # 打印HTTP错误信息
    except requests.exceptions.RequestException as req_err:
        print(f"{ErrTip}请求错误: {req_err}")  # 打印请求相关的错误
    except Exception as e:
        print(f"{ErrTip}其他错误: {e}")  # 打印其他类型的错误
    return None  # 如果出错，返回None


def search_cover_image(params):
    """
    从指定URL获取专辑封面图片。
    参数:
    url (str): API URL。
    params (dict): 查询参数。
    返回:
    bytes: 图片的二进制数据。
    """
    try:
        response = requests.get("https://api.lrc.cx/api/v1/cover/album?", params=params, stream=True)
        if response.status_code == 200 and response.headers['content-type'].startswith('image/'):
            return response.content
        else:
            raise ValueError("API返回的不是一个有效的图片文件。")
    except requests.exceptions.HTTPError as http_err:
        print(f"{ErrTip}音乐封面HTTP错误: {http_err}")  # 打印HTTP错误信息
    except requests.exceptions.RequestException as req_err:
        print(f"{ErrTip}音乐封面请求错误: {req_err}")  # 打印请求相关的错误
    except Exception as e:
        print(f"{ErrTip}音乐封面其他错误: {e}")  # 打印其他类型的错误
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
        print(f"{ErrTip}: 读取文件属性时出错: {e}")
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
    print(f'{InfoTip}音频属性信息写入成功')


def set_lyrics(lyrics, path):
    """
    设置歌词信息到音频文件中。
    参数:
    lyrics (str): 歌词文本。
    """
    file_extension = get_file_type(path)['file_type']
    try:
        # MP3
        if file_extension == 'mp3':
            audio = MP3(path)
            if audio.tags is None:
                audio.add_tags()
            if audio.tags is not None:
                audio.tags.add(USLT(encoding=3, lang='eng', text=lyrics))
                audio.save()
                print(f"{InfoTip} MP3歌词写入成功")
            else:
                print(f"{ErrTip} 无法将歌词标签写入到MP3文件")
        # Flac
        elif file_extension == 'flac':
            audio = FLAC(path)
            if "LYRICS" in audio:
                print(f"{InfoTip}该FLAC文件已包含歌词，更新歌词...")
                audio["LYRICS"] = lyrics
            else:
                # 如果没有歌词，添加新的歌词标签
                print(f"${InfoTip}为该FLAC文件添加歌词...")
                audio["LYRICS"] = lyrics
            audio.save()
            print(f"{InfoTip}Flac歌词写入成功")
        else:
            print(f"{ErrTip} 无法将歌词标签写入到文件")
    except FileNotFoundError:
        print(f"{ErrTip} 文件未找到")
    except PermissionError:
        print(f"{ErrTip} 权限不足，无法写入文件")
    except Exception as e:
        print(f"{ErrTip} 写入歌词时出错: {e}")

def embed_cover_in_flac(path, cover_data):
    """
    将封面图片嵌入到音频文件中。
    参数:
    path (str): 音频文件路径。
    cover_data (bytes): 图片的二进制数据。
    """
    file_info = get_file_type(path)
    file_extension = file_info['file_type']

    if file_extension == 'mp3':
        audio = MP3(path, ID3=ID3)
        if audio.tags is None:
            audio.add_tags()

        audio.tags.add(
            APIC(
                encoding=3,  # UTF-8
                mime='image/jpeg',  # MIME类型
                type=3,  # COVER_FRONT
                desc='Cover',
                data=cover_data
            )
        )
        audio.save()
        print(f"{InfoTip} MP3封面写入成功")
    elif file_extension == 'flac':
        audio = FLAC(path)
        if audio.tags is None:
            audio.add_tags()

        picture = Picture()
        picture.type = 3  # 文件类型 3 表示封面
        picture.mime = 'image/jpeg'
        picture.desc = 'Cover'
        picture.data = cover_data

        audio.clear_pictures()  # 清除旧的图片标签
        audio.add_picture(picture)
        audio.save()
        print(f"{InfoTip} FLAC封面写入成功")
    else:
        print(f"{ErrTip} 不支持的文件类型")

ErrTip = f'{Fore.RED}[ERROR]: {Style.RESET_ALL}'
WarnTip = f'{Fore.YELLOW}[WARNNING]: {Style.RESET_ALL}'
InfoTip = f'{Fore.GREEN}[INFO]: {Style.RESET_ALL}'
