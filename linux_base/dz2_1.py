import os
import subprocess
from datetime import datetime, timedelta

DIR_NAME = "dz1"


def get_current_user() -> str:
    current_user, _ = execute_cmd("whoami")
    return current_user


def get_current_path() -> str:
    current_path, _ = execute_cmd("pwd")
    return current_path


def execute_cmd(cmd: str) -> tuple:
    result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip()


def locate_existing_path(current_path: str, name: str) -> str | None:
    path = os.path.join(current_path, name)

    if os.path.exists(path):
        return path
    else:
        return


def create_dir(dir_name: str) -> None:
    execute_cmd(f"mkdir {dir_name}")


def create_empty_file(file_name: str) -> None:
    execute_cmd(f"touch {file_name}")


def generate_daily_logs(dir_path) -> None:
    today = datetime.today().date()
    first_day_current_month = today.replace(day=1)
    days_in_month = (today.replace(month=today.month + 1, day=1) - timedelta(days=1)).day

    for day in range(1, days_in_month + 1):
        date_file = first_day_current_month.replace(day=day).strftime("%d-%m-%Y")
        file_name = f"{date_file}.log"
        create_empty_file(os.path.join(dir_path, file_name))


def remove_random_files(dir_path, *, limit=0) -> None:
    all_files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]

    import random; random.shuffle(all_files)
    files_to_remove = all_files[:limit] if limit > 0 else all_files

    for file_path in files_to_remove:
        os.remove(file_path)


def main() -> None:
    current_user = get_current_user()
    print(f"{current_user=}")
    current_path = get_current_path()
    print(f"{current_path=}")

    # remove directory if it exists
    if dir_path := locate_existing_path(current_path, DIR_NAME):
        execute_cmd(f"rm -r {dir_path}")

    create_dir(DIR_NAME)
    dir_path = locate_existing_path(current_path, DIR_NAME)

    generate_daily_logs(dir_path)
    remove_random_files(dir_path, limit=5)


if __name__ == '__main__':
    main()
