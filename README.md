# Задача 1. Архиватор на Python 3.14
# Выполнил: Титаренко Никита 932220

# Архиватор/распаковщик с поддержкой zstd и bz2

usage: archiver.py [-h] [-b] [{compress,decompress}] input output

positional arguments:
  {compress,decompress}
                        Режим: compress или decompress (опционально, определяется автоматически)
  input                 Исходный файл или директория
  output                Целевой файл или директория

options:
  -h, --help            show this help message and exit
  -b, --benchmark       Вывод времени выполнения

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