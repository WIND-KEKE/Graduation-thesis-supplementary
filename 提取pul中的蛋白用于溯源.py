import os
from Bio import SeqIO

def extract_sequences(txt_file, faa_folder, output_fasta):
    # 读取txt文件中的蛋白编号
    with open(txt_file, "r") as f:
        protein_ids = sorted([line.strip() for line in f if line.strip()])  # 按字母顺序排列

    # 存储匹配的序列
    extracted_sequences = []

    # 遍历faa文件夹中的所有文件
    for faa_file in os.listdir(faa_folder):
        if faa_file.endswith(".faa"):
            file_path = os.path.join(faa_folder, faa_file)
            # 解析faa文件中的序列
            for record in SeqIO.parse(file_path, "fasta"):
                if record.id in protein_ids:
                    extracted_sequences.append(record)

    # 按照编号排序
    extracted_sequences.sort(key=lambda x: x.id)

    # 将匹配的序列写入输出的fasta文件
    with open(output_fasta, "w") as output:
        SeqIO.write(extracted_sequences, output, "fasta")

    print(f"提取完成！匹配的序列已保存到 {output_fasta}")

# 使用方法
txt_file = "GH127.txt"  # 替换为你的txt文件名
faa_folder = "/home/caoke/CKK/AnGST/faa"  # 替换为你的faa文件夹路径
output_fasta = "/home/caoke/CKK/AnGST/GH127.fasta"  # 输出fasta文件的路径

extract_sequences(txt_file, faa_folder, output_fasta)
