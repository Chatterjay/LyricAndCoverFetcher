import sys

from utils import read_file_stats, search_request_mse, write_audio_tags, set_lyrics


def main():
    if len(sys.argv) < 2:
        return

# 音频文件拖入
# input_path = sys.argv[1]  # 获取拖入的文件路径
path = r"E:\高嶺のなでしこ - 美しく生きろ.mp3"
# 读取文件的属性
stats = read_file_stats(path)
# 请求查找
res = search_request_mse(stats)[0]
# 将歌曲和对应属性写入进去
write_audio_tags(path, album=res['album'], title=res["title"], artist=res['artist'])
# # 把歌词写入
set_lyrics(res['lyrics'], path)

if __name__ == '__main__':
    main()
