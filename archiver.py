import argparse
import os
import sys
import time
import tarfile
import bz2
import compression.zstd as zstd
from pathlib import Path


def compress(input, output, benchmark=False):
    start = time.time()
    temp_tar = None

    temp_tar = output.with_suffix('.tar')
    with tarfile.open(temp_tar, 'w') as tar:
        tar.add(input, arcname=os.path.basename(input))
    input = temp_tar

    if output.suffix == '.bz2':
        with open(input, 'rb') as f_in, bz2.open(output, 'wb') as f_out:
            copy_stream(f_in, f_out)
    elif output.suffix == '.zst':
        with open(input, 'rb') as f_in, zstd.open(output, 'wb') as f_out:
            copy_stream(f_in, f_out)
    else:
        print("Неподдерживаемое расширение целевого файла. Используйте .bz2 или .zst.")
        sys.exit(1)

    if temp_tar and temp_tar.exists():
        temp_tar.unlink()

    if benchmark:
        print(f"Архивирование завершено за {time.time() - start:.2f} секунд")


def decompress(input, output_dir, benchmark=False):
    start = time.time()
    temp_tar = output_dir / 'temp.tar'

    if input.suffix == '.bz2':
        with bz2.open(input, 'rb') as f_in, open(temp_tar, 'wb') as f_out:
            copy_stream(f_in, f_out)
    elif input.suffix == '.zst':
        with zstd.open(input, 'rb') as f_in, open(temp_tar, 'wb') as f_out:
            copy_stream(f_in, f_out)
    else:
        print("Неподдерживаемое расширение входного файла. Используйте .bz2 или .zst.")
        sys.exit(1)

    with tarfile.open(temp_tar, 'r') as tar:
        tar.extractall(path=output_dir)
    temp_tar.unlink()

    if benchmark:
        print(f"Разорхивирование завершено за {time.time() - start:.2f} секунд")


def copy_stream(f_in, f_out):
    total = 0
    while True:
        chunk = f_in.read(1024 * 1024)
        if not chunk:
            break
        f_out.write(chunk)
        total += len(chunk)


def auto_detect_mode(input, output):
    input_path = Path(input)
    output_path = Path(output)
    
    if output_path.suffix in ['.bz2', '.zst']:
        return 'compress', output_path
    elif input_path.suffix in ['.bz2', '.zst']:
        return 'decompress', output_path
    else:
        return 'compress', output_path.with_suffix('.zst')


def main():
    parser = argparse.ArgumentParser(
        description="Архиватор/распаковщик с поддержкой zstd и bz2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Автоматическое определение режима
  python archiver.py file.txt archive.zst          -> сжатие в zstd
  python archiver.py directory/ archive.bz2        -> сжатие в bz2
  
  python archiver.py archive.zst output/           -> распаковка
  python archiver.py archive.bz2 output/           -> распаковка
  
  python archiver.py file.txt output/              -> сжатие в zstd
  
  # Явное указание режима
  python archiver.py compress file.txt archive.zst
  python archiver.py decompress archive.zst output/
  
  # С измерением времени
  python archiver.py --benchmark file.txt archive.zst
  python archiver.py -b directory/ archive.bz2
        """
    )
    
    parser.add_argument(
        "mode",
        nargs='?',
        choices=["compress", "decompress"],
        help="Режим: compress или decompress (опционально, определяется автоматически)"
    )
    parser.add_argument(
        "input",
        help="Исходный файл или директория"
    )
    parser.add_argument(
        "output",
        help="Целевой файл или директория"
    )
    parser.add_argument(
        "-b", "--benchmark",
        action="store_true",
        help="Вывод времени выполнения"
    )

    args = parser.parse_args()
    input = Path(args.input)
    
    if args.mode:
        mode = args.mode
        output = Path(args.output)
    else:
        mode, output = auto_detect_mode(args.input, args.output)
        print(f"Автоматически определен режим: {mode}")
        print(f"Целевой путь: {output}")

    if mode == "compress":
        compress(input, output, args.benchmark)
    else:
        decompress(input, output, args.benchmark)


if __name__ == "__main__":
    main()