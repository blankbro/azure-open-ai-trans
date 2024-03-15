import tiktoken


def num_tokens_from_string(string: str) -> int:
    encoding = tiktoken.get_encoding("gpt2")
    num_tokens = len(encoding.encode(string))
    return num_tokens


if __name__ == '__main__':
    # 打开文件，使用 'r' 模式来读取内容
    file = open('../output/text', 'r')
    # 按行读取文件内容
    texts = file.readlines()
    # 关闭文件
    file.close()
    # 输出每一行的内容
    line_count = len(texts)
    token_total_num = 0
    for index, text in enumerate(texts):
        token_num = num_tokens_from_string(text)
        token_total_num += token_num
        print(f'进度: {index + 1}/{line_count} 当前Token数: {token_num}, 目前总Token数: {token_total_num} {text}')

    print(f"平均token数: {token_total_num / line_count}")
