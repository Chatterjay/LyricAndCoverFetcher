import os.path
import sys

from utils import read_file_stats, search_request_mse, write_audio_tags, set_lyrics, ErrTip, InfoTip, \
    search_cover_image, embed_cover_in_flac


def main():
    if len(sys.argv) < 2:
        return

    extensions = ('.mp3', '.flac')
    input_path = sys.argv[1]

    success_count = 0  # 成功处理的文件数
    fail_count = 0  # 失败处理的文件数

    if os.path.isdir(input_path):
        # 计算目录中符合条件的文件总数
        total_files = sum(1 for root, dirs, files in os.walk(input_path) for file in files if file.endswith(extensions))
        processed_files = 0

        # 遍历目录中的所有MP3/FLAC文件
        for root, dirs, files in os.walk(input_path):
            for file in files:
                if file.endswith(extensions):
                    path = os.path.join(root, file)
                    success = process_audio_file(path)  # 返回处理成功或失败的状态
                    processed_files += 1
                    if success:
                        success_count += 1
                    else:
                        fail_count += 1
                    print(f"{InfoTip}处理进度: {processed_files}/{total_files}")

        # 显示成功和失败的文件数量
        print(f"{InfoTip}处理完成。成功: {success_count} 个文件, 失败: {fail_count} 个文件。")

    elif os.path.isfile(input_path):
        # 如果是单个文件，直接处理
        if input_path.endswith(extensions):
            success = process_audio_file(input_path)
            if success:
                success_count += 1
            else:
                fail_count += 1
            print(f"{InfoTip}处理进度: 1/1")
            print(f"{InfoTip}处理完成。成功: {success_count} 个文件, 失败: {fail_count} 个文件。")

    else:
        print(f"{ErrTip} 提供的路径不是有效的文件或目录。")


def process_audio_file(path):
    try:
        # 读取文件的属性
        stats = read_file_stats(path)

        if stats['title'] is None:
            print(f"{ErrTip}文件 {path} 缺少标题信息，跳过...")
            return False  # 标记处理失败

        # 模拟读取操作可能会出错的部分
        print(f"{InfoTip}正在处理文件: {path}")

        # 请求查找资源
        res_list = search_request_mse(stats)
        buffer = search_cover_image(stats)
        if not res_list or res_list[0] is None:
            print(f"{ErrTip}歌词未能找到匹配的结果: {path}")
            return False  # 标记处理失败

        res = res_list[0]
        # 将歌曲和对应属性写入进去
        write_audio_tags(path, album=res['album'], title=res["title"], artist=res['artist'])

        # 写入歌词
        set_lyrics(res['lyrics'], path)
        embed_cover_in_flac(path,buffer)

        print(f"{InfoTip}文件 {path}处理成功。")
        return True  # 标记处理成功

    except Exception as e:
        print(f"{ErrTip}处理文件 {path} 时发生错误: {e}")
        return False  # 标记处理失败


if __name__ == '__main__':
    # 如果想要直接运行并传入路径，可以取消下面注释
    main()

    # 测试用例，替换成实际文件路径
    # path = r"E:\ClariS - アンダンテ.mp3"
    # process_audio_file(path)

    input('按任意键退出....')
