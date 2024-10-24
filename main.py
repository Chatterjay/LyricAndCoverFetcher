import os.path
import sys

from utils import read_file_stats, search_request_mse, write_audio_tags, set_lyrics


def main():
    if len(sys.argv) < 2:
        return

    # 遍历文件夹获取文件mp3文件路径存储到map
    # 遍历map完成一套循环
    list = ('.mp3', 'flac')
    input_path = sys.argv[1]
    if os.path.isdir(input_path):
        # 如果是目录，遍历目录中的所有MP3/FLAC文件
        for root, dirs, files in os.walk(input_path):
            for file in files:
                if file.endswith(list):
                    path = os.path.join(root, file)
                    process_audio_file(path)
    elif os.path.isfile(input_path):
        # 如果是单个文件，直接处理
        if input_path.endswith(list):
            process_audio_file(input_path)
    else:
        print("提供的路径不是有效的文件或目录。")


def process_audio_file(path):
    # 读取文件的属性
    stats = read_file_stats(path)
    print(stats)
    # 请求查找
    res = search_request_mse(stats)[0]
    # 将歌曲和对应属性写入进去
    write_audio_tags(path, album=res['album'], title=res["title"], artist=res['artist'])
    # # 把歌词写入
    set_lyrics(res['lyrics'], path)


if __name__ == '__main__':
    main()
