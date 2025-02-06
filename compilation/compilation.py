import shutil
import subprocess
import os

from settings import CompilationSettings


CLEAR_FUNC = (
    lambda: shutil.rmtree(CompilationSettings.DIST_PATH),
    lambda: shutil.rmtree(CompilationSettings.BUILD_PATH),
    lambda: CompilationSettings.GUI_PARSER_SPEC_PATH.unlink(),
    lambda: CompilationSettings.PARSER_SPEC_PATH.unlink(),
)


def clear() -> None:
    """Очиска старой компиляции."""
    for func in CLEAR_FUNC:
        try:
            func()
        except Exception:
            continue


def compilation() -> None:
    """Компиляция парсера."""
    clear()
    subprocess.run(
        (
            'pyinstaller',
            f'--icon={CompilationSettings.LOGO_NAME}',
            f'--name={CompilationSettings.FILE_NAME}',
            'main.py',
            *CompilationSettings.ARGS,
        )
    )
    subprocess.run(
        (
            'pyinstaller',
            f'--icon={CompilationSettings.LOGO_NAME}',
            f'--name={CompilationSettings.GUI_FILE_NAME}',
            os.path.join('compilation', 'start_wrapper.py'),
            *CompilationSettings.ARGS,
        )
    )


if __name__ == '__main__':
    compilation()
