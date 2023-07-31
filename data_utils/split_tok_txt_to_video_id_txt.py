import os

def split_file(source_file, target_path):

    os.makedirs(target_path, exist_ok=True)
    with open(source_file, 'r') as f:
        for line in f:
            # split video_id and text
            video_id, text = line.split(' ', 1)
            
            # Create a full path for the new file
            file_path = os.path.join(target_path, f"{video_id}.txt")

            with open(file_path, 'w') as new_file:
                new_file.write(text)
source_file_lst = ['/home/alexandrtchk/VSCode/multimodal/mast-300/text/all/desc.tok.txt', 
                   '/home/alexandrtchk/VSCode/multimodal/mast-300/text/all/tran.tok.txt']

target_path_lst = ['/home/alexandrtchk/VSCode/multimodal/mast-300/text/all_separated/desc',
                   '/home/alexandrtchk/VSCode/multimodal/mast-300/text/all_separated/tran']

for source_file, target_path, in zip(source_file_lst, target_path_lst):
    split_file(source_file, target_path)
