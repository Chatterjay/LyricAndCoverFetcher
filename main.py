import os.path
import sys

from utils import read_file_stats, search_request_mse, write_audio_tags, set_lyrics, err_tip, info_tip


def main():
    if len(sys.argv) < 2:
        return

    extensions = ('.mp3', '.flac')
    input_path = sys.argv[1]

    if os.path.isdir(input_path):
        # 计算目录中符合条件的文件总数
        total_files = sum(1 for root, dirs, files in os.walk(input_path) for file in files if file.endswith(extensions))
        processed_files = 0

        # 如果是目录，遍历目录中的所有MP3/FLAC文件
        for root, dirs, files in os.walk(input_path):
            for file in files:
                if file.endswith(extensions):
                    path = os.path.join(root, file)
                    process_audio_file(path)
                    processed_files += 1
                    print(f"{info_tip}处理进度: {processed_files}/{total_files}")
    elif os.path.isfile(input_path):
        # 如果是单个文件，直接处理
        if input_path.endswith(extensions):
            process_audio_file(input_path)
            print(f"{info_tip}处理进度: 1/1")
    else:
        print(f"{err_tip} 提供的路径不是有效的文件或目录。")


def process_audio_file(path):
    try:
        # 读取文件的属性
        stats = read_file_stats(path)
        if stats['title'] is None:
            pass
        # 请求查找
        print(stats)
        res_list = search_request_mse(stats)
        if not res_list or res_list[0] is None:
            print(f"{err_tip} 未能找到匹配的结果: {path}")
            return
        res = res_list[0]
        # 将歌曲和对应属性写入进去
        write_audio_tags(path, album=res['album'], title=res["title"], artist=res['artist'])
        # 把歌词写入
        set_lyrics(res['lyrics'], path)
    except Exception as e:
        print(f"{err_tip} 处理文件 {path} 时发生错误: {e}")


if __name__ == '__main__':
    main()
    input('按任意键退出....')
