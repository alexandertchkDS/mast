import os
import shutil
import random
from split_data import consistency_checking

def split_dataset(base_dir, audio_dir, video_dir, desc_dir, tran_dir, splitted_dir, train_frac=0.7, dev_frac=0.15, test_frac=0.15):
    # Make sure fractions add up to 1
    assert train_frac + dev_frac + test_frac == 1.0, "Split fractions must add up to 1."

    consistency_checking(base_dir)

    video_ids = [os.path.splitext(file)[0] for file in os.listdir(video_dir)]

    # Shuffle and split ids
    random.shuffle(video_ids)
    split1 = int(train_frac * len(video_ids))
    split2 = int((train_frac + dev_frac) * len(video_ids))
    train_ids = video_ids[:split1]
    dev_ids = video_ids[split1:split2]
    test_ids = video_ids[split2:]

    # Create directories
    for split in ['train', 'dev', 'test']:
        for data_type in ['video', 'audio', 'desc', 'tran']:
            os.makedirs(os.path.join(splitted_dir, f'{data_type}_{split}'), exist_ok=True)

    # Split data
    for split, ids in zip(['train', 'dev', 'test'], [train_ids, dev_ids, test_ids]):
        for video_id in ids:
            shutil.copy(os.path.join(audio_dir, f'{video_id}.npy'), os.path.join(splitted_dir, f'audio_{split}', f'{video_id}.npy'))
            shutil.copy(os.path.join(video_dir, f'{video_id}.npy'), os.path.join(splitted_dir, f'video_{split}', f'{video_id}.npy'))
            shutil.copy(os.path.join(desc_dir, f'{video_id}.npy'), os.path.join(splitted_dir, f'desc_{split}', f'{video_id}.npy'))
            shutil.copy(os.path.join(tran_dir, f'{video_id}.npy'), os.path.join(splitted_dir, f'tran_{split}', f'{video_id}.npy'))

# Define paths
base_dir = '/home/alexandrtchk/VSCode/multimodal/data-1000-items/not_split'
splitted_dir = os.path.join('/home/alexandrtchk/VSCode/multimodal/data-1000-items/splitted')

audio_dir = os.path.join(base_dir, 'audio')
video_dir = os.path.join(base_dir, 'video')
desc_dir = os.path.join(base_dir, 'text_npy', 'desc')
tran_dir = os.path.join(base_dir, 'text_npy', 'tran')



# Split dataset with custom fractions
split_dataset(base_dir, audio_dir, video_dir, desc_dir, tran_dir, splitted_dir, train_frac=0.8, dev_frac=0.1, test_frac=0.1)
