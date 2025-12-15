import csv
import os
import re
import glob
from fw_downloader import download_firmware
from fw_unpacker import unpack_firmware

def sanitize_path(path):
    """清理路径名，移除或替换不安全的字符"""
    # 替换不安全的字符为下划线
    path = re.sub(r'[<>:"/\\|?*]', '_', path)
    # 移除前后空格和点
    path = path.strip(' .')
    return path if path else 'unknown'

def read_firmware_info_from_csv(csv_path):
    """从CSV文件中读取固件信息（包含品牌、型号、URL等）"""
    firmware_list = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                vendor = row.get('vendor', '').strip()
                product = row.get('product', '').strip()
                version = row.get('version', '').strip()
                date = row.get('date', '').strip()
                url = row.get('url', '').strip()
                
                if url:  # 只添加非空的URL
                    firmware_list.append({
                        'vendor': vendor,
                        'product': product,
                        'version': version,
                        'date': date,
                        'url': url
                    })
        print(f"从 {csv_path} 文件中读取了 {len(firmware_list)} 个固件信息")
    except FileNotFoundError:
        print(f"错误：找不到CSV文件 {csv_path}")
    except Exception as e:
        print(f"读取CSV文件 {csv_path} 时出错：{e}")
    return firmware_list

def main(csv_dir, save_path):
    # 查找目录中所有的CSV文件
    csv_files = glob.glob(os.path.join(csv_dir, '*.csv'))
    
    if not csv_files:
        print(f"在目录 {csv_dir} 中没有找到任何CSV文件，程序退出")
        return

    all_firmware_list = []
    for csv_file in csv_files:
        all_firmware_list.extend(read_firmware_info_from_csv(csv_file))

    if not all_firmware_list:
        print("没有找到有效的固件信息，程序退出")
        return
    
    print(f"总共读取了 {len(all_firmware_list)} 个固件信息")
    
    # 按品牌和型号分类下载固件
    for firmware in all_firmware_list:
        vendor = sanitize_path(firmware.get('vendor', 'unknown'))
        product = sanitize_path(firmware.get('product', 'unknown'))
        
        # 构建分类路径: save_path/vendor/product/
        classified_path = os.path.join(save_path, vendor, product)
        
        # 下载固件到分类路径
        download_firmware([firmware['url']], classified_path)
    
    # 解包固件（会在层级目录结构中递归解包）
    # unpack_firmware(save_path)

if __name__ == '__main__':
    # CSV文件所在的目录
    csv_dir = "../routers"
    save_path = "../fws"
    main(csv_dir, save_path)

