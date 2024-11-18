import argparse
import zipfile
import os
import datetime
import xml.etree.ElementTree as ET

class ShellEmulator:
    def __init__(self, user, vfs_path, log_path, startup_script):
        self.user = user
        self.vfs = self.load_vfs(vfs_path)
        self.current_dir = self.vfs
        self.current_path = []  # Путь от корня к текущей директории
        self.history = []
        self.log_path = log_path
        self.log_root = ET.Element("session")
        
        # Выполнение стартового скрипта, если он указан
        if startup_script:
            self.run_script(startup_script)

    def get_current_dir_content(self):
        # Проверяем, что текущая директория - это словарь с содержимым
        if isinstance(self.current_dir, dict):
            return self.current_dir
        else:
            # Если текущая директория пустая или None
            return {}

    def load_vfs(self, vfs_path):
        # Загрузка виртуальной файловой системы из zip-файла
        vfs = {}

        with zipfile.ZipFile(vfs_path, 'r') as zip_file:
            for file in zip_file.namelist():
                parts = file.strip('/').split('/')
                current = vfs

                # Проходим по всем частям пути
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]

                # Последняя часть пути - это файл или папка
                if parts[-1]:
                    current[parts[-1]] = {}

        return vfs

    def log_command(self, command, output):
        # Логирование команды в XML-файл
        cmd_elem = ET.SubElement(self.log_root, "command")
        user_elem = ET.SubElement(cmd_elem, "user")
        user_elem.text = self.user
        time_elem = ET.SubElement(cmd_elem, "time")
        time_elem.text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        input_elem = ET.SubElement(cmd_elem, "input")
        input_elem.text = command
        output_elem = ET.SubElement(cmd_elem, "output")
        output_elem.text = output

    def run_script(self, script_path):
        # Выполнение команд из стартового скрипта
        with open(script_path, 'r') as file:
            commands = file.readlines()
        for command in commands:
            self.process_command(command.strip())

    def process_command(self, command):
        # Обработка команды пользователя
        output = None  # Добавляем переменную для хранения результата выполнения команды
        
        if command == 'exit':
            self.save_log()
            exit()
        elif command.startswith('ls'):
            # Обработка команды `ls`
            output = self.list_dir()
        elif command.startswith('cd'):
            # Обработка команды `cd`
            path = command.split(maxsplit=1)[1] if len(command.split()) > 1 else '/'
            output = self.change_dir(path)
        elif command == 'who':
            output = self.user
        elif command == 'history':
            output = '\n'.join(self.history)
        elif command == 'date':
            output = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            output = "Unknown command"
        
        # Добавление команды в историю и логирование
        self.history.append(command)
        self.log_command(command, output)
        print(output)  # Печать результата для CLI

        return output  # Возвращаем результат выполнения команды

    def list_dir(self):
        current_dir_content = self.get_current_dir_content()
        if current_dir_content:
            # Возвращаем имена файлов и директорий
            return '\n'.join(current_dir_content.keys())
        else:
            return "Directory is empty."

    def change_dir(self, path):
        # Пример реализации команды `cd`
        if path == '/':
            self.current_dir = self.vfs  # Переход к корневой директории
            return "Changed to root directory"
        
        parts = path.strip('/').split('/')
        current = self.current_dir

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return f"Directory not found: {path}"
        
        self.current_dir = current
        return f"Changed directory to /{'/'.join(parts)}"


    def navigate_to_dir(self, path_parts):
        # Навигация по виртуальной файловой системе по частям пути
        current = self.vfs
        for part in path_parts:
            current = current.get(part, {})
        return current

    def save_log(self):
        # Сохранение XML-лога
        tree = ET.ElementTree(self.log_root)
        tree.write(self.log_path)

# Главная точка входа в программу
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Эмулятор UNIX-подобной оболочки")
    parser.add_argument("-u", "--user", required=True, help="Имя пользователя")
    parser.add_argument("-v", "--vfs", required=True, help="Путь к архиву виртуальной файловой системы")
    parser.add_argument("-l", "--logfile", required=True, help="Путь к XML лог-файлу")
    parser.add_argument("-s", "--startup", help="Путь к стартовому скрипту", required=False)

    args = parser.parse_args()
    emulator = ShellEmulator(args.user, args.vfs, args.logfile, args.startup)

    while True:
        try:
            command = input(f"{args.user}@emulator:~{'/'.join(emulator.current_path) or '/'}$ ")
            emulator.process_command(command)
        except KeyboardInterrupt:
            print("\nSession ended.")
            emulator.save_log()
            break
