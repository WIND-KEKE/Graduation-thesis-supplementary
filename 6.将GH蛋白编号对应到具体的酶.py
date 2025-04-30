import os
import pandas as pd

def add_hmm_profile_to_csv(genus_species):
    # 生成文件名
    csv_filename = f'PUL_results_with_CAZy_{genus_species}.csv'
    out_filename = f'{genus_species}.out'

    # 读取CSV文件
    pul_df = pd.read_csv(csv_filename)
    
    # 读取.out文件，并以制表符分隔
    out_df = pd.read_csv(out_filename, sep='\t')

    # 创建一个新的列用来保存GH (HMM Profile)
    pul_df['GH'] = None

    # 遍历CSV中的每一行
    for i, row in pul_df.iterrows():
        protein_ids = row['CAZy Proteins']
        
        # 检查是否为缺失值（NaN）
        if pd.isna(protein_ids):
            continue  # 如果是NaN，跳过该行

        # 分割蛋白序号
        protein_ids = protein_ids.split(', ')
        gh_profiles = []

        for protein_id in protein_ids:
            # 在.out文件中查找匹配的Gene ID
            matching_row = out_df[out_df['Gene ID'] == protein_id]

            if not matching_row.empty:
                # 如果找到匹配的行，获取HMM Profile
                hmm_profile = matching_row['HMM Profile'].values[0]
                gh_profiles.append(hmm_profile)

        # 将找到的所有GH合并成一个字符串，用逗号分隔
        pul_df.at[i, 'GH'] = ','.join(gh_profiles) if gh_profiles else None

    # 将更新后的数据保存回CSV文件
    pul_df.to_csv(csv_filename, index=False)
    print(f'Updated {csv_filename} with HMM profiles.')

def process_all_csv_files():
    # 获取当前目录下的所有文件
    files = os.listdir()

    # 过滤出所有CSV文件
    csv_files = [f for f in files if f.startswith('PUL_results_with_CAZy_') and f.endswith('.csv')]

    # 对每个CSV文件执行操作
    for csv_file in csv_files:
        # 提取菌种名称
        genus_species = csv_file.replace('PUL_results_with_CAZy_', '').replace('.csv', '')

        # 检查对应的out文件是否存在
        out_file = f'{genus_species}.out'
        if out_file in files:
            add_hmm_profile_to_csv(genus_species)
        else:
            print(f'Skipped {csv_file}: Corresponding .out file not found.')

# 处理当前文件夹下的所有CSV文件
process_all_csv_files()
