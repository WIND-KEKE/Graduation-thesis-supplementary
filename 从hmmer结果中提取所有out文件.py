import os
import shutil

# 获取当前文件夹下的所有文件夹，并按名称排序
folders = sorted([folder for folder in os.listdir() if os.path.isdir(folder)])

# 遍历所有文件夹
for folder in folders:
    # 构建hmmer.out文件的路径
    hmmer_file_path = os.path.join(folder, 'hmmer.out')
    
    # 如果hmmer.out文件存在，则复制到当前文件夹并重命名
    if os.path.exists(hmmer_file_path):
        # 复制文件到当前文件夹
        shutil.copy(hmmer_file_path, os.getcwd())
        
        # 获取来源文件夹的名字作为新文件名
        new_file_name = f'{folder}.out'
        
        # 重命名文件
        os.rename(os.path.join(os.getcwd(), 'hmmer.out'), new_file_name)
