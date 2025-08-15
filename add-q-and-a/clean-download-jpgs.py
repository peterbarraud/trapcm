from glob import glob

def main():
    f_log = open(r'C:\Users\ctl\Documents\trapcm\raw-data\maths\2025\jan\files.log', 'w')
    for f in glob(r'C:\Users\ctl\Documents\trapcm\raw-data\maths\2025\jan\*jpg'):
        dest_file_name = f[-8:]
        f_log.write(f'mv "{f}" {dest_file_name}\n')

    f_log.close()

if __name__ == '__main__':
    main()