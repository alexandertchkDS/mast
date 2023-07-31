import os

def consistency_checking(root_dir_path):
    splitted_video_ids = []
    for dirpath, dirnames, filenames in os.walk(root_dir_path):
        if not dirnames:
            dir_list_files = sorted(os.listdir(dirpath))
            files_without_extension = [os.path.splitext(file)[0] for file in dir_list_files]
            if splitted_video_ids == []:
                splitted_video_ids = files_without_extension
            else:
                assert splitted_video_ids == files_without_extension, "Video ids are not consistent among folders"
                splitted_video_ids = files_without_extension
    print(f"All files in folders are consistent!")

if __name__ == '__main__':
    #root_dir_path = '/home/alexandrtchk/VSCode/multimodal/data-1000-items/not_split'
    root_dir_path = '/home/alexandrtchk/VSCode/multimodal/data-1000-items/splitted'
    consistency_checking(root_dir_path)