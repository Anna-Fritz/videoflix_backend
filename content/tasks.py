import subprocess


def convert_all_resolutions(source):
    resolutions = {
        '480p': 480,
        '720p': 720,
        '1080p': 1080,
    }

    for label, height in resolutions.items():
        target = f"{source}_{label}.mp4"
        cmd = [
            'ffmpeg', '-i', source,
            '-vf', f'scale=-2:{height}',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-movflags', '+faststart',
            target
        ]
        print(f"Converting to {label}...")
        subprocess.run(cmd, check=True)
    print("All conversions done.")