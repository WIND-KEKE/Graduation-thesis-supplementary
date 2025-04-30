import csv
import re
import os

# 步骤1：从BLAST文件中提取SUL和PRO信息
def extract_sul_and_pro_from_blast(blast_file):
    sul_pro_mapping = {}
    with open(blast_file, 'r') as file:
        for line in file:
            columns = line.strip().split('\t')
            if len(columns) >= 2:
                protein_id = columns[0]
                description = columns[1]
                # 提取所需的pro信息
                match = re.search(r'_(.*?)\|', description)
                pro_info = match.group(1) if match else ''
                sul_pro_mapping[protein_id] = pro_info
    return sul_pro_mapping

# 根据SusC, SusD和CAZy Proteins编号确定范围，并在BLAST文件中查找上下游5个蛋白内的Sul信息
def process_pul_and_blast(pul_file, blast_file, sul_pro_mapping):
    updated_pul_data = []

    # 提取 BLAST 文件中的蛋白质列表，以便进行范围搜索
    blast_proteins = []
    with open(blast_file, 'r') as file:
        for line in file:
            blast_proteins.append(line.strip().split('\t')[0])  # 提取蛋白质ID

    # 读取PUL文件
    with open(pul_file, 'r') as file:
        csvreader = csv.DictReader(file)
        header = csvreader.fieldnames + ['Sul', 'sul-pro']  # 添加Sul和sul-pro列

        for row in csvreader:
            # 提取 SusC、SusD 和 CAZy Proteins 列中的蛋白编号，并将其转为整数
            try:
                sus_c = int(re.sub(r'\D', '', row['SusC']))  # 提取数字
                sus_d = int(re.sub(r'\D', '', row['SusD']))  # 提取数字
                cazy_proteins = [int(re.sub(r'\D', '', protein_id)) for protein_id in row['CAZy Proteins'].split(', ')]
            except ValueError:
                # 如果无法转换为整数，则跳过这一行
                continue

            # 找到最大值和最小值
            max_id = max(sus_c, sus_d, *cazy_proteins)
            min_id = min(sus_c, sus_d, *cazy_proteins)

            # 扩展上下游5个蛋白质的范围
            search_min = min_id - 5
            search_max = max_id + 5

            # 查找在扩展范围内的 Sul 蛋白
            sul_ids = []
            sul_pros = []
            for protein_id in blast_proteins:
                # 提取BLAST文件中的蛋白编号作为整数
                try:
                    protein_num = int(re.sub(r'\D', '', protein_id))
                except ValueError:
                    continue
                
                # 如果蛋白编号在范围内，且在sul_pro_mapping中找到相应的Sul信息
                if search_min <= protein_num <= search_max and protein_id in sul_pro_mapping:
                    sul_ids.append(protein_id)
                    sul_pros.append(sul_pro_mapping[protein_id])

            # 去除与SusC、SusD和CAZy Proteins中编号重复的Sul
            sus_c_d_cazy_ids = {sus_c, sus_d} | set(cazy_proteins)
            filtered_sul_ids = [pid for pid in sul_ids if int(re.sub(r'\D', '', pid)) not in sus_c_d_cazy_ids]
            filtered_sul_pros = [sul_pro_mapping[pid] for pid in filtered_sul_ids]

            # 更新Sul和sul-pro列
            row['Sul'] = ', '.join(filtered_sul_ids)
            row['sul-pro'] = ', '.join(filtered_sul_pros)

            updated_pul_data.append(row)

    return header, updated_pul_data

# 主函数
def main():
    # 获取当前目录
    current_folder = os.path.dirname(os.path.abspath(__file__))
    
    # 查找文件
    pul_file = None
    blast_file = None
    
    for file_name in os.listdir(current_folder):
        if file_name.startswith('PUL_results_with_CAZy_') and file_name.endswith('.csv'):
            pul_file = os.path.join(current_folder, file_name)
        elif file_name.endswith('.blast'):
            blast_file = os.path.join(current_folder, file_name)
    
    if not pul_file or not blast_file:
        raise FileNotFoundError("未找到 PUL_results_with_CAZy.csv 或 .blast 文件")

    # 提取SUL和PRO信息
    sul_pro_mapping = extract_sul_and_pro_from_blast(blast_file)
    
    # 处理PUL文件
    header, updated_pul_data = process_pul_and_blast(pul_file, blast_file, sul_pro_mapping)
    
    # 保存更新后的结果
    output_file = os.path.join(current_folder, f'{os.path.splitext(os.path.basename(pul_file))[0]}_with_Sul_and_sul-pro.csv')
    with open(output_file, 'w', newline='') as csvfile:
        csvwriter = csv.DictWriter(csvfile, fieldnames=header)
        csvwriter.writeheader()
        csvwriter.writerows(updated_pul_data)

    print(f"结果已保存到 {output_file}")

if __name__ == '__main__':
    main()
