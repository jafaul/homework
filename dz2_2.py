import dz2_1

SOURCE_FILE = "dz2_1.py"
DESTINATION_FILE = "dz1_run.py"


def main():
    # remove file if it exists
    current_path = dz2_1.get_current_path()
    if destination_file_path := dz2_1.locate_existing_path(current_path, DESTINATION_FILE):
        dz2_1.execute_cmd(f"rm {destination_file_path}")

    dz2_1.create_empty_file(DESTINATION_FILE)

    dz2_1.execute_cmd(f"cp ./{SOURCE_FILE} {DESTINATION_FILE}")

    with open(DESTINATION_FILE, "r") as file:
        content = file.readlines()

    with open(DESTINATION_FILE, "w") as file:
        file.write("#!/usr/bin/env python3\n")
        file.writelines(content)

    dz2_1.execute_cmd(f"chmod 700 {DESTINATION_FILE}")
    stdout, _ = dz2_1.execute_cmd(f"python3 {DESTINATION_FILE}")
    print(stdout)

if __name__ == "__main__":
    main()
