import os

def extract_video_ids(input_filename, output_filename):
    with open(input_filename, 'r') as input_file, open(output_filename, 'w') as output_file:
        for line in input_file:
            video_id = line.split(' ')[0]  # Split each line by space and take the first part
            output_file.write(video_id + '\n')  # Write the video id to the output file


text_dir = '/home/alexandrtchk/VSCode/multimodal/data-1000-items/text'
text_dir_files = os.listdir(text_dir)
for txt_file in text_dir_files:
    input_filename = os.path.join(text_dir, txt_file)
    name, rest = txt_file.split('.', 1)
    output_filename = os.path.join(text_dir, f"{name}_id.{rest}")
    extract_video_ids(input_filename, output_filename)



