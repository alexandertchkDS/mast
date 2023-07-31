import shutil
import os
import heapq


def process_files(n_files, source_video_dir, source_audio_dir, source_tran_dir, source_desc_dir,
                       target_video_dir, target_audio_dir, target_tran_dir, target_desc_dir):
    
    #Crate target dirs
    os.makedirs(target_video_dir, exist_ok=True)
    os.makedirs(target_audio_dir, exist_ok=True)
    os.makedirs(target_tran_dir, exist_ok=True)
    os.makedirs(target_desc_dir, exist_ok=True)

    # Create a list of tuples where each tuple is (filesize, filename)
    video_files_sizes = [(os.path.getsize(os.path.join(source_video_dir, f)), f) for f in os.listdir(source_video_dir)]
    # Get the N smallest files
    smallest_video_files = heapq.nsmallest(n_files, video_files_sizes)
    
    video_ids = [os.path.splitext(video_id)[0] for video_size, video_id in smallest_video_files]

    #Copy video and audio files
    for video_id in video_ids:
        # Copy video and audio files
        shutil.copy(os.path.join(source_video_dir, f'{video_id}.npy'), target_video_dir)
        shutil.copy(os.path.join(source_audio_dir, f'{video_id}.npy'), target_audio_dir)
        #Copy text files
        shutil.copy(os.path.join(source_tran_dir, f'{video_id}.txt'), target_tran_dir)
        shutil.copy(os.path.join(source_desc_dir, f'{video_id}.txt'), target_desc_dir)        




source_video_dir = "/home/alexandrtchk/VSCode/multimodal/mast-300/video_300_npy"
source_audio_dir = "/home/alexandrtchk/VSCode/multimodal/mast-300/audio_300_npy"
source_tran_dir = "/home/alexandrtchk/VSCode/multimodal/mast-300/text/all_separated/tran"
source_desc_dir = "/home/alexandrtchk/VSCode/multimodal/mast-300/text/all_separated/desc"

target_video_dir = "/home/alexandrtchk/VSCode/multimodal/data-1000-items/not_split/video"
target_audio_dir = "/home/alexandrtchk/VSCode/multimodal/data-1000-items/not_split/audio"
target_tran_dir = "/home/alexandrtchk/VSCode/multimodal/data-1000-items/not_split/text/tran"
target_desc_dir = "/home/alexandrtchk/VSCode/multimodal/data-1000-items/not_split/text/desc"

n_files = 220

process_files(n_files, source_video_dir, source_audio_dir, source_tran_dir, source_desc_dir,
                       target_video_dir, target_audio_dir, target_tran_dir, target_desc_dir)
