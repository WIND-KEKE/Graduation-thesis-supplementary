import os
import re
import csv

# 步骤1：读取.faa文件
def read_faa(file_path):
    proteins = {}
    with open(file_path, 'r') as file:
        protein_id = ""
        sequence = ""
        for line in file:
            if line.startswith('>'):
                if protein_id:
                    proteins[protein_id] = sequence
                protein_id = line.split()[0][1:]  # Assuming the protein ID is the first word after '>'
                sequence = ""
            else:
                sequence += line.strip()
        if protein_id:
            proteins[protein_id] = sequence
    return proteins

# 步骤2：读取dbCAN3注释结果
def read_dbcan3(file_path):
    annotations = []
    with open(file_path, 'r') as file:
        csvreader = csv.reader(file, delimiter='\t')
        for line in csvreader:
            if len(line) >= 3:  # Ensure there are enough columns
                gene_id = line[2]  # Gene ID is in the third column
                annotations.append(gene_id)
    return annotations

# 步骤3：读取PUL_results.csv文件
def read_pul_results(file_path):
    pul_pairs = []
    with open(file_path, 'r') as file:
        csvreader = csv.reader(file)
        next(csvreader)  # 跳过表头
        for row in csvreader:
            pul_id, sus_c, sus_d, _ = row
            pul_pairs.append((sus_c, sus_d))
    return pul_pairs

# 从蛋白质ID中提取数字部分
def extract_number(protein_id):
    match = re.search(r'(\d+)$', protein_id)
    if match:
        return int(match.group(1))
    else:
        print(f"无法从 {protein_id} 中提取数字")
        return None  # 返回 None 以便在 build_pul 中处理

# 步骤4：构建PUL
def build_pul(pul_pairs, annotations):
    pul_clusters = []
    for pair in pul_pairs:
        sus_c, sus_d = pair
        sus_c_num = extract_number(sus_c)
        sus_d_num = extract_number(sus_d)

        if sus_c_num is None or sus_d_num is None:
            continue  # 如果提取数字失败，则跳过该对

        start = min(sus_c_num, sus_d_num) - 5
        end = max(sus_c_num, sus_d_num) + 5
        pul = [sus_c, sus_d]
        for gene_id in annotations:
            gene_num = extract_number(gene_id)
            if gene_num is not None and start <= gene_num <= end:
                pul.append(gene_id)
        pul_clusters.append(pul)
    return pul_clusters

# 获取当前脚本所在的文件夹
current_folder = os.path.dirname(os.path.abspath(__file__))

# 查找文件
faa_file = None
dbcan3_file = None
pul_results_file = None

for file_name in os.listdir(current_folder):
    if file_name.endswith('.faa'):
        faa_file = os.path.join(current_folder, file_name)
    elif file_name.endswith('.out'):
        dbcan3_file = os.path.join(current_folder, file_name)
    elif 'PUL_results.csv' in file_name:
        pul_results_file = os.path.join(current_folder, file_name)

# 确保找到所需的文件
if not faa_file or not dbcan3_file or not pul_results_file:
    raise FileNotFoundError("未找到 .faa、.out 或 PUL_results.csv 文件")

print(f"读取 .faa 文件: {faa_file}")
print(f"读取 .out 文件: {dbcan3_file}")
print(f"读取 PUL_results 文件: {pul_results_file}")

# 示例使用
proteins = read_faa(faa_file)
print(f"已读取 {len(proteins)} 个蛋白质序列")

annotations = read_dbcan3(dbcan3_file)
print(f"已读取 {len(annotations)} 个注释")

pul_pairs = read_pul_results(pul_results_file)
print(f"已读取 {len(pul_pairs)} 对 SusC 和 SusD 基因")

puls = build_pul(pul_pairs, annotations)
print(f"已构建 {len(puls)} 个 PUL")

# 输出结果到新的CSV文件
output_file = os.path.join(current_folder, 'PUL_results_with_CAZy.csv')
with open(output_file, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['PUL_ID', 'SusC', 'SusD', 'CAZy Proteins'])
    for i, pul in enumerate(puls):
        pul_id = f'PUL_{i+1}'
        sus_c = pul[0]
        sus_d = pul[1]
        cazy_proteins = ', '.join(pul[2:])
        csvwriter.writerow([pul_id, sus_c, sus_d, cazy_proteins])

print(f"结果已输出到 {output_file}")
