import csv
import os
import re

# 检查是否包含目标的PL系列
def has_target_family(gh_families, target_families):
    for gh in gh_families:
        # 检查GH名称中是否包含目标PL家族，且确保目标PL家族后不接数字
        if any(gh.startswith(pl) and not re.search(r'\d$', gh) for pl in target_families):
            return True
    return False

# 筛选满足条件的PUL并生成新文件，返回没有找到结果的菌种名
def filter_and_save_pul(input_file, output_file, no_alg_species):
    target_families = {'PL6', 'PL7', 'PL18', 'PL14', 'PL39'}
    current_species = None
    found_pul = False  # 用于标志是否找到符合条件的PUL

    with open(input_file, 'r') as infile, open(output_file, 'a', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        # 如果文件是新建的，需要写入表头
        if outfile.tell() == 0:
            writer.writeheader()

        for row in reader:
            gh_families = [gh.strip() for gh in row['GH'].split(', ')]  # 提取 GH 列

            # 判断是否含有目标的PL系列
            if has_target_family(gh_families, target_families):
                species_name = input_file.split('PUL_results_with_CAZy_')[-1].split('.csv')[0]

                # 如果遇到新的菌种，增加一行空白
                if current_species and current_species != species_name:
                    writer.writerow({})  # 添加空行

                current_species = species_name
                found_pul = True  # 标记找到符合条件的PUL

                # 保持原文件中的PUL编号
                original_pul_id = row['PUL_ID']
                row['PUL_ID'] = f"{species_name}_{original_pul_id}"

                # 写入符合条件的行
                writer.writerow(row)
                print(f"写入符合条件的PUL: {row['PUL_ID']}")  # 调试信息

        # 如果没有找到符合条件的PUL，则将该菌种名添加到no_alg_species列表
        if not found_pul:
            species_name = input_file.split('PUL_results_with_CAZy_')[-1].split('.csv')[0]
            no_alg_species.append(species_name)

# 主函数，处理所有PUL文件，并生成 noalg.csv 文件
def process_all_pul_files(folder_path):
    output_file = os.path.join(folder_path, 'alg.csv')
    no_alg_file = os.path.join(folder_path, 'noalg.csv')
    no_alg_species = []

    # 遍历文件夹下的所有PUL文件
    for file_name in os.listdir(folder_path):
        if file_name.startswith('PUL_results_with_CAZy_') and file_name.endswith('.csv'):
            input_file = os.path.join(folder_path, file_name)
            print(f"正在处理文件: {input_file}")  # 添加调试信息
            filter_and_save_pul(input_file, output_file, no_alg_species)

    # 将没有找到符合条件的菌种名写入noalg.csv
    if no_alg_species:
        with open(no_alg_file, 'w', newline='') as noalg_outfile:
            writer = csv.writer(noalg_outfile)
            writer.writerow(["Species with no alginate-targeting PULs"])
            for species in no_alg_species:
                writer.writerow([species])

    print(f"筛选后的PUL已保存至 {output_file}")
    if no_alg_species:
        print(f"没有找到符合条件PUL的菌种已保存至 {no_alg_file}")
    else:
        print("所有菌种都找到了符合条件的PUL")

if __name__ == "__main__":
    folder_path = os.path.dirname(os.path.abspath(__file__))  # 当前目录
    process_all_pul_files(folder_path)
