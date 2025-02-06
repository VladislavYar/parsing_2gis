import subprocess

from settings import CompilationSettings


def start_wrapper() -> None:
    """Обёртка запуска exe файла через GUI."""
    file = (
        CompilationSettings.DIST_PATH / f'{CompilationSettings.FILE_NAME}.exe'
    )
    subprocess.run((file, '-g'))


if __name__ == '__main__':
    start_wrapper()
