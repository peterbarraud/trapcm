from glob import glob
import os

def main(files_dir):
    f_log = open(f"{files_dir}/files.log", 'w')

    for full_file_path in glob(f"{files_dir}/*jpg"):
        file_name = os.path.basename(full_file_path)
        short_file_name = file_name.replace('Chemistry - JEE Main 2025 January_page-','')
        print(short_file_name)
        print(full_file_path)
        os.rename(full_file_path,f"{files_dir}/{short_file_name}")

        # break

    f_log.close()

if __name__ == '__main__':
    main(r'D:\tech-stuff\trapcm\qanda-files\raw-data\chemistry\2025\jan-mathongo\ilovepdf_pages-to-jpg')