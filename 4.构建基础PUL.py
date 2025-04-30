import os
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
        for line in file:
            annotations.append(line.strip().split('\t'))
    return annotations

# 步骤3：读取SusC和SusD成对基因
def read_sus_pairs(file_path):
    sus_pairs = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过标题行
        pair = []
        for line in reader:
            if line:  # 忽略空行
                pair.append(line)
                if len(pair) == 2:
                    sus_pairs.append([pair[0][0], pair[1][0]])
                    pair = []
    return sus_pairs

# 步骤4：构建PUL
def build_pul(sus_pairs, annotations):
    pul_clusters = []
    for pair in sus_pairs:
        sus_c, sus_d = pair
        pul = [sus_c, sus_d]
        for annotation in annotations:
            if annotation[0] not in pul and annotation[1].startswith('CAZy'):
                pul.append(annotation[0])
        pul_clusters.append(pul)
    return pul_clusters

# 步骤5：提取菌种名并跳过没有SusCD的文件
def extract_species_name(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        try:
            next(reader)  # 跳过标题行
            second_line = next(reader)  # 尝试读取第二行
        except StopIteration:
            # 没有第二行，直接跳过
            print(f"文件 {file_path} 没有第二行，跳过该文件")
            return None  # 返回 None 来表示没有可用的数据
        
        # 提取菌种名
        full_name = second_line[0]
        parts = full_name.split('_')
        if len(parts) >= 2:
            species_name = '_'.join(parts[:2])
            return species_name
        else:
            raise ValueError(f"文件 {file_path} 的第二行数据格式不正确，无法提取菌种名")

# 获取当前脚本所在的文件夹
current_folder = os.path.dirname(os.path.abspath(__file__))

# 查找符合条件的文件
faa_files = []
dbcan3_files = []
sus_pairs_files = []

for file_name in os.listdir(current_folder):
    if file_name.endswith('.faa'):
        faa_files.append(os.path.join(current_folder, file_name))
    elif file_name.endswith('.out'):
        dbcan3_files.append(os.path.join(current_folder, file_name))
    elif 'sus_pairs.csv' in file_name:
        sus_pairs_files.append(os.path.join(current_folder, file_name))

# 确保找到所有匹配文件
if not faa_files or not dbcan3_files or not sus_pairs_files:
    raise FileNotFoundError("未找到 .faa、.out 或 sus_pairs.csv 文件")

# 逐个文件对进行处理
for faa_file, dbcan3_file, sus_pairs_file in zip(faa_files, dbcan3_files, sus_pairs_files):
    # 提取菌种名，如果没有SusCD，跳过该文件
    species_name = extract_species_name(sus_pairs_file)
    if species_name is None:
        continue  # 跳过该文件的处理

    print(f"读取 .faa 文件: {faa_file}")
    print(f"读取 .out 文件: {dbcan3_file}")
    print(f"读取 sus_pairs 文件: {sus_pairs_file}")

    # 读取数据
    proteins = read_faa(faa_file)
    print(f"已读取 {len(proteins)} 个蛋白质序列")

    annotations = read_dbcan3(dbcan3_file)
    print(f"已读取 {len(annotations)} 个注释")

    sus_pairs = read_sus_pairs(sus_pairs_file)
    print(f"已读取 {len(sus_pairs)} 对 SusC 和 SusD 基因")

    # 构建PUL
    puls = build_pul(sus_pairs, annotations)
    print(f"已构建 {len(puls)} 个 PUL")

    # 输出结果到CSV文件
    output_file = os.path.join(current_folder, f'PUL_results_{species_name}.csv')
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
