import os
import shutil

# specify your directories
base_dir = '/home/alexandrtchk/VSCode/multimodal/data-1000-items/not_split'
audio_dir = os.path.join(base_dir, 'audio')
video_dir = os.path.join(base_dir, 'video')

desc_dir = os.path.join(base_dir, 'text', 'desc')
tran_dir = os.path.join(base_dir, 'text', 'tran')


# get list of filenames without extensions in each directory
audio_files = set(os.path.splitext(file)[0] for file in os.listdir(audio_dir))
video_files = set(os.path.splitext(file)[0] for file in os.listdir(video_dir))
desc_files = set(os.path.splitext(file)[0] for file in os.listdir(desc_dir))
tran_files = set(os.path.splitext(file)[0] for file in os.listdir(tran_dir))
# calculate the intersection of filenames
common_files = audio_files & video_files & desc_files & tran_files

print(f'len audio_files initial: {len(audio_files)}')
print(f'len video_files initial: {len(video_files)}')
print(f'len desc_files initial: {len(desc_files)}')
print(f'len tran_files initial: {len(tran_files)}')

print(f'len common_files: {len(common_files)}')

# delete files that are not in the intersection from audio_dir
for file in os.listdir(audio_dir):
    filename = os.path.splitext(file)[0]
    if filename not in common_files:
        os.remove(os.path.join(audio_dir, file))

# delete files that are not in the intersection from video_dir
for file in os.listdir(video_dir):
    filename = os.path.splitext(file)[0]
    if filename not in common_files:
        os.remove(os.path.join(video_dir, file))

# delete files that are not in the intersection from video_dir
for file in os.listdir(desc_dir):
    filename = os.path.splitext(file)[0]
    if filename not in common_files:
        os.remove(os.path.join(desc_dir, file))

# delete files that are not in the intersection from video_dir
for file in os.listdir(tran_dir):
    filename = os.path.splitext(file)[0]
    if filename not in common_files:
        os.remove(os.path.join(tran_dir, file))

# get list of filenames without extensions in each directory
audio_files = set(os.path.splitext(file)[0] for file in os.listdir(audio_dir))
video_files = set(os.path.splitext(file)[0] for file in os.listdir(video_dir))
desc_files = set(os.path.splitext(file)[0] for file in os.listdir(desc_dir))
tran_files = set(os.path.splitext(file)[0] for file in os.listdir(tran_dir))
# calculate the intersection of filenames
common_files = audio_files & video_files & desc_files & tran_files

print(f'len audio_files after removing: {len(audio_files)}')
print(f'len video_files after removing: {len(video_files)}')
print(f'len desc_files after removing: {len(desc_files)}')
print(f'len tran_files after removing: {len(tran_files)}')
