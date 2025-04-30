import os
import pandas as pd

def merge_files(base_df, file_path):
    df = pd.read_csv(file_path, sep='\t')
    merged_df = base_df.copy()
    # 遍历新文件中的每一行
    for index, row in df.iterrows():
        profile = row['HMM Profile']
        count = row['Count']
        # 如果统计项在基础 DataFrame 中已经存在，则添加到相应列中
        if profile in merged_df['HMM Profile'].tolist():
            merged_df.loc[merged_df['HMM Profile'] == profile, file_path] = count
        # 否则，在基础 DataFrame 中添加新的行，并填充对应列的值
        else:
            new_row = pd.Series([profile] + [0] * (len(merged_df.columns) - 1), index=merged_df.columns)
            new_row[file_path] = count
            merged_df = pd.concat([merged_df, pd.DataFrame([new_row], columns=merged_df.columns)], ignore_index=True)
    return merged_df

# 获取所有文件的文件名并按字母顺序排序
folder_path = "/home/caoke/CKK/hmmer-count-test"
all_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.out')])

# 读取第一个文件
base_file = os.path.join(folder_path, all_files[0])
base_df = pd.read_csv(base_file, sep='\t')

# 以第一个文件为基础递归地合并所有文件
merged_df = base_df.copy()
for file_name in all_files[1:]:
    file_path = os.path.join(folder_path, file_name)
    merged_df = merge_files(merged_df, file_path)

# 将合并后的结果保存到CSV文件中
summary_file_path = "/home/caoke/CKK/hmmer-count-test/summary.csv"
merged_df.to_csv(summary_file_path, index=False)

print(f"汇总结果已保存到 {summary_file_path} 文件中。")
