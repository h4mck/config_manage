import tkinter as tk
import sys
import os
import zipfile
import hashlib
import base64
import io
from collections import OrderedDict
import shutil

KNOWN_COMMANDS = ["ls", "cd", "exit", "vfs-info", "cat", "pwd", "tail", "head", "uniq", "cp", "chown"]


class VFS:
    def __init__(self):
        self.zip_file = None
        self.vfs_name = ""
        self.sha256_hash = ""
        self.current_path = "/"
        self.modified_files = {}  # Хранит измененные файлы в памяти
        self.file_ownership = {}  # Хранит информацию о владельцах файлов
        self.default_owner = "user"  # Владелец по умолчанию

    def load_vfs(self, vfs_path):
        """Загружает VFS из ZIP-архива"""
        try:
            if not os.path.exists(vfs_path):
                return False, f"VFS file not found: {vfs_path}"

            self.zip_file = zipfile.ZipFile(vfs_path, 'r')
            self.vfs_name = os.path.basename(vfs_path)

            # Вычисляем SHA-256 хеш
            with open(vfs_path, 'rb') as f:
                file_data = f.read()
                self.sha256_hash = hashlib.sha256(file_data).hexdigest()

            # Инициализируем информацию о владельцах
            self._initialize_ownership()

            return True, "VFS loaded successfully"

        except zipfile.BadZipFile:
            return False, f"Invalid VFS format: {vfs_path}"
        except Exception as e:
            return False, f"Error loading VFS: {str(e)}"

    def _initialize_ownership(self):
        """Инициализирует информацию о владельцах для всех файлов"""
        for file_path in self.zip_file.namelist():
            self.file_ownership[file_path] = self.default_owner

    def _get_full_path(self, filename):
        """Возвращает полный путь к файлу в VFS"""
        if filename.startswith('/'):
            return filename.lstrip('/')
        else:
            return (self.current_path.lstrip('/') + filename).lstrip('/')

    def _file_exists(self, file_path):
        """Проверяет существование файла (оригинального или измененного)"""
        return file_path in self.modified_files or file_path in self.zip_file.namelist()

    def get_info(self):
        """Возвращает информацию о VFS"""
        if not self.zip_file:
            return "No VFS loaded"

        modified_count = len(self.modified_files)
        return f"VFS Name: {self.vfs_name}\nSHA-256: {self.sha256_hash}\nModified files: {modified_count}"

    def list_directory(self, path=None, show_all=False, long_format=False):
        """Список содержимого директории"""
        if not self.zip_file:
            return "No VFS loaded"

        if path is None:
            path = self.current_path

        # Нормализуем путь
        if not path.startswith('/'):
            path = '/' + path
        if not path.endswith('/'):
            path += '/'

        items = set()
        item_details = {}

        # Проверяем оригинальные файлы из ZIP
        for file_path in self.zip_file.namelist():
            # Убираем ведущий слеш если есть
            clean_path = file_path.lstrip('/')

            if path == '/':
                # Корневая директория - берем первый элемент пути
                first_sep = clean_path.find('/')
                if first_sep == -1:
                    items.add(clean_path)
                    item_details[clean_path] = {
                        'type': 'file',
                        'owner': self.file_ownership.get(file_path, self.default_owner),
                        'modified': file_path in self.modified_files
                    }
                else:
                    dir_name = clean_path[:first_sep] + '/'
                    items.add(dir_name)
                    if dir_name not in item_details:
                        item_details[dir_name] = {
                            'type': 'dir',
                            'owner': self.default_owner,
                            'modified': False
                        }
            else:
                # Проверяем, находится ли файл в запрошенной директории
                search_path = path.lstrip('/')
                if clean_path.startswith(search_path):
                    relative_path = clean_path[len(search_path):]
                    if relative_path:
                        first_sep = relative_path.find('/')
                        if first_sep == -1:
                            items.add(relative_path)
                            item_details[relative_path] = {
                                'type': 'file',
                                'owner': self.file_ownership.get(file_path, self.default_owner),
                                'modified': file_path in self.modified_files
                            }
                        else:
                            dir_name = relative_path[:first_sep] + '/'
                            items.add(dir_name)
                            if dir_name not in item_details:
                                item_details[dir_name] = {
                                    'type': 'dir',
                                    'owner': self.default_owner,
                                    'modified': False
                                }

        # Проверяем измененные файлы
        for file_path in self.modified_files.keys():
            clean_path = file_path.lstrip('/')

            if path == '/':
                first_sep = clean_path.find('/')
                if first_sep == -1:
                    items.add(clean_path)
                    item_details[clean_path] = {
                        'type': 'file',
                        'owner': self.file_ownership.get(file_path, self.default_owner),
                        'modified': True
                    }
                else:
                    dir_name = clean_path[:first_sep] + '/'
                    items.add(dir_name)
                    if dir_name not in item_details:
                        item_details[dir_name] = {
                            'type': 'dir',
                            'owner': self.default_owner,
                            'modified': False
                        }
            else:
                search_path = path.lstrip('/')
                if clean_path.startswith(search_path):
                    relative_path = clean_path[len(search_path):]
                    if relative_path:
                        first_sep = relative_path.find('/')
                        if first_sep == -1:
                            items.add(relative_path)
                            item_details[relative_path] = {
                                'type': 'file',
                                'owner': self.file_ownership.get(file_path, self.default_owner),
                                'modified': True
                            }

        # Фильтруем скрытые файлы (начинающиеся с .) если не указан show_all
        if not show_all:
            items = {item for item in items if not item.startswith('.')}

        sorted_items = sorted(list(items))

        if long_format:
            result = []
            for item in sorted_items:
                details = item_details.get(item, {'type': 'file', 'owner': self.default_owner, 'modified': False})
                item_type = 'd' if details['type'] == 'dir' else '-'
                modified_flag = '*' if details['modified'] else ' '
                result.append(f"{item_type}{modified_flag} {details['owner']:8} {item}")
            return result
        else:
            return sorted_items

    def change_directory(self, path):
        """Изменяет текущую директорию"""
        if not self.zip_file:
            return False, "No VFS loaded"

        if path == "..":
            # Переход на уровень выше
            if self.current_path == "/":
                return True, "Already at root"
            parts = self.current_path.rstrip('/').split('/')
            if len(parts) <= 1:
                self.current_path = "/"
            else:
                self.current_path = '/' + '/'.join(parts[:-1])
                if self.current_path != "/":
                    self.current_path += '/'
            return True, f"Changed to {self.current_path}"

        if path == "/":
            self.current_path = "/"
            return True, "Changed to root"

        if path == ".":
            return True, f"Current directory: {self.current_path}"

        # Абсолютный или относительный путь
        if path.startswith('/'):
            new_path = path
        else:
            new_path = self.current_path.rstrip('/') + '/' + path

        # Нормализуем путь
        if not new_path.endswith('/'):
            new_path += '/'

        # Проверяем существование директории
        search_path = new_path.lstrip('/')
        dir_exists = False
        all_files = list(self.zip_file.namelist()) + list(self.modified_files.keys())
        for file_path in all_files:
            clean_path = file_path.lstrip('/')
            if clean_path.startswith(search_path) or search_path == "":
                dir_exists = True
                break

        if dir_exists:
            self.current_path = new_path
            return True, f"Changed to {self.current_path}"
        else:
            return False, f"Directory not found: {path}"

    def read_file(self, filename, lines_limit=None):
        """Читает содержимое файла с опциональным ограничением по строкам"""
        if not self.zip_file:
            return False, "No VFS loaded"

        file_path = self._get_full_path(filename)

        # Проверяем измененную версию first
        if file_path in self.modified_files:
            content = self.modified_files[file_path]
        else:
            try:
                with self.zip_file.open(file_path) as f:
                    content = f.read()

                # Декодируем как текст
                try:
                    content = content.decode('utf-8')
                except UnicodeDecodeError:
                    # Если не текстовый файл, возвращаем как base64
                    return True, f"[Binary file - base64 encoded]\n{base64.b64encode(content).decode('utf-8')}"
            except KeyError:
                return False, f"File not found: {filename}"
            except Exception as e:
                return False, f"Error reading file: {str(e)}"

        # Применяем ограничение по строкам если нужно
        if lines_limit is not None and isinstance(content, str):
            lines = content.split('\n')
            if lines_limit > 0:
                limited_lines = lines[:lines_limit]
            else:
                limited_lines = lines[lines_limit:]
            content = '\n'.join(limited_lines)

        return True, content

    def copy_file(self, source, destination):
        """Копирует файл внутри VFS (в памяти)"""
        if not self.zip_file:
            return False, "No VFS loaded"

        source_path = self._get_full_path(source)
        dest_path = self._get_full_path(destination)

        # Проверяем существование исходного файла
        if not self._file_exists(source_path):
            return False, f"Source file not found: {source}"

        # Читаем содержимое исходного файла
        success, content = self.read_file(source)
        if not success:
            return False, content  # content содержит сообщение об ошибке

        # Сохраняем копию в памяти
        self.modified_files[dest_path] = content
        self.file_ownership[dest_path] = self.file_ownership.get(source_path, self.default_owner)

        return True, f"Copied {source} to {destination}"

    def change_owner(self, filename, new_owner):
        """Изменяет владельца файла"""
        if not self.zip_file:
            return False, "No VFS loaded"

        file_path = self._get_full_path(filename)

        # Проверяем существование файла
        if not self._file_exists(file_path):
            return False, f"File not found: {filename}"

        # Обновляем владельца
        self.file_ownership[file_path] = new_owner

        # Если файл был изменен, помечаем его
        if file_path not in self.modified_files and file_path in self.zip_file.namelist():
            # Создаем запись в modified_files чтобы отслеживать изменение владельца
            with self.zip_file.open(file_path) as f:
                content = f.read()
                try:
                    self.modified_files[file_path] = content.decode('utf-8')
                except UnicodeDecodeError:
                    self.modified_files[file_path] = content

        return True, f"Changed owner of {filename} to {new_owner}"

    def get_file_owner(self, filename):
        """Возвращает владельца файла"""
        file_path = self._get_full_path(filename)
        return self.file_ownership.get(file_path, self.default_owner)


def parse_command(command_str):
    parts = command_str.strip().split()
    if not parts:
        return None, []
    return parts[0], parts[1:]


class VFSEmulator:
    def __init__(self):
        self.vfs = VFS()
        self.vfs_path = ""
        self.script_path = ""
        self.is_running_script = False
        self.script_commands = []
        self.current_script_command = 0
        self.root = None
        self.output = None
        self.entry = None

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title(self.get_window_title())

        # Frame для приглашения и поля ввода
        input_frame = tk.Frame(self.root)
        input_frame.pack(padx=10, pady=10, fill='x')

        # Неподвижный текст-приглашение (Label)
        prompt_label = tk.Label(input_frame, text="vfs_invitation$> ", font=("Courier", 12))
        prompt_label.pack(side='left')

        # Поле ввода команд
        self.entry = tk.Entry(input_frame, width=75, font=("Courier", 12))
        self.entry.pack(side='left', fill='x', expand=True)
        self.entry.bind("<Return>", lambda event: self.run_command())

        run_button = tk.Button(self.root, text="Run", command=self.run_command)
        run_button.pack(pady=5)

        self.output = tk.Text(self.root, height=15, width=80, font=("Courier", 12))
        self.output.pack(padx=10, pady=10)

        # Отладочный вывод параметров
        self.debug_output()

        if self.script_path:
            # Запускаем выполнение скрипта после небольшой задержки, чтобы GUI успел инициализироваться
            self.root.after(100, self.start_script_execution)

    def get_window_title(self):
        """Формирует заголовок окна с именем VFS"""
        title = "VFS"
        if self.vfs_path:
            title = f"VFS - {os.path.basename(self.vfs_path)}"
        return title

    def debug_output(self):
        """Выводит отладочную информацию о параметрах"""
        self.output.insert(tk.END, "=== Debug Information ===\n")
        self.output.insert(tk.END, f"VFS Path: {self.vfs_path}\n")
        self.output.insert(tk.END, f"Script Path: {self.script_path}\n")

        if self.vfs_path:
            success, message = self.vfs.load_vfs(self.vfs_path)
            if success:
                self.output.insert(tk.END, f"VFS loaded: {message}\n")
                self.output.insert(tk.END, f"{self.vfs.get_info()}\n")
            else:
                self.output.insert(tk.END, f"VFS load error: {message}\n")
        else:
            self.output.insert(tk.END, "No VFS specified\n")

        self.output.insert(tk.END, "=======================\n\n")
        self.safe_see_end()

    def safe_see_end(self):
        """Безопасная прокрутка к концу (с проверкой существования виджета)"""
        try:
            if self.output and self.output.winfo_exists():
                self.output.see(tk.END)
        except tk.TclError:
            pass  # Виджет уже уничтожен

    def safe_update(self):
        """Безопасное обновление GUI"""
        try:
            if self.root and self.root.winfo_exists():
                self.root.update()
        except tk.TclError:
            pass  # Окно уже уничтожено

    def execute_command_directly(self, command_str):
        """Выполняет команду напрямую, без использования поля ввода"""
        # Проверяем, существует ли еще окно
        if not self.root or not self.root.winfo_exists():
            return

        cmd_input = command_str
        command, args = parse_command(cmd_input)
        comment = ""

        # Обработка комментариев
        for arg in args:
            if arg.startswith("#"):
                comment = args[args.index(arg):]
                args = args[:args.index(arg)]
                comment = " ".join(comment)
                break

        if not command:
            self.output.insert(tk.END, "No command entered.\n")
            self.safe_see_end()
            return

        # Выводим приглашение и команду
        self.output.insert(tk.END, f"vfs_invitation$> {cmd_input}\n")

        if command not in KNOWN_COMMANDS:
            self.output.insert(tk.END, f"Unknown command: {command}\n")
        elif command == "exit":
            if args:
                self.output.insert(tk.END, f"Unknown arguments: {args}\n")
                self.safe_see_end()
            else:
                # Останавливаем выполнение скрипта перед выходом
                self.is_running_script = False
                self.root.after(100, self.root.destroy)
                return
        elif command == "vfs-info":
            if args:
                self.output.insert(tk.END, f"vfs-info doesn't take arguments: {args}\n")
            else:
                self.output.insert(tk.END, f"{self.vfs.get_info()}\n")
        elif command == "ls":
            show_all = '-a' in args or '-all' in args
            long_format = '-l' in args
            path = None
            for arg in args:
                if not arg.startswith('-'):
                    path = arg
                    break

            items = self.vfs.list_directory(path, show_all, long_format)
            if isinstance(items, str):
                self.output.insert(tk.END, f"{items}\n")
            else:
                for item in items:
                    self.output.insert(tk.END, f"{item}\n")
        elif command == "cd":
            if len(args) > 1:
                self.output.insert(tk.END, f"cd takes 0 or 1 arguments, got {len(args)}\n")
            else:
                path = args[0] if args else "/"
                success, message = self.vfs.change_directory(path)
                self.output.insert(tk.END, f"{message}\n")
        elif command == "pwd":
            if args:
                self.output.insert(tk.END, f"pwd doesn't take arguments: {args}\n")
            else:
                self.output.insert(tk.END, f"{self.vfs.current_path}\n")
        elif command == "cat":
            if len(args) != 1:
                self.output.insert(tk.END, f"cat takes exactly 1 argument, got {len(args)}\n")
            else:
                success, content = self.vfs.read_file(args[0])
                self.output.insert(tk.END, f"{content}\n")
        elif command == "head":
            if len(args) < 1 or len(args) > 2:
                self.output.insert(tk.END, "Usage: head [-n LINES] FILE\n")
            else:
                lines = 10  # default
                filename = args[-1]

                if len(args) == 2:
                    if args[0] == '-n' and args[1].isdigit():
                        lines = int(args[1])
                        filename = args[2] if len(args) > 2 else None
                    else:
                        self.output.insert(tk.END, "Usage: head [-n LINES] FILE\n")
                        self.safe_see_end()
                        return

                if not filename:
                    self.output.insert(tk.END, "Filename required\n")
                else:
                    success, content = self.vfs.read_file(filename, lines)
                    self.output.insert(tk.END, f"{content}\n")
        elif command == "tail":
            if len(args) < 1 or len(args) > 2:
                self.output.insert(tk.END, "Usage: tail [-n LINES] FILE\n")
            else:
                lines = 10  # default
                filename = args[-1]

                if len(args) == 2:
                    if args[0] == '-n' and args[1].isdigit():
                        lines = int(args[1])
                        filename = args[2] if len(args) > 2 else None
                    else:
                        self.output.insert(tk.END, "Usage: tail [-n LINES] FILE\n")
                        self.safe_see_end()
                        return

                if not filename:
                    self.output.insert(tk.END, "Filename required\n")
                else:
                    success, content = self.vfs.read_file(filename, -lines)
                    self.output.insert(tk.END, f"{content}\n")
        elif command == "uniq":
            if len(args) < 1 or len(args) > 2:
                self.output.insert(tk.END, "Usage: uniq [FILE] or uniq -c [FILE]\n")
            else:
                count_mode = False
                filename = args[-1]

                if len(args) == 2:
                    if args[0] == '-c':
                        count_mode = True
                    else:
                        self.output.insert(tk.END, "Usage: uniq [FILE] or uniq -c [FILE]\n")
                        self.safe_see_end()
                        return

                success, content = self.vfs.read_file(filename)
                if success:
                    lines = content.split('\n')
                    unique_lines = []
                    line_counts = OrderedDict()

                    for line in lines:
                        if line in line_counts:
                            line_counts[line] += 1
                        else:
                            line_counts[line] = 1

                    if count_mode:
                        for line, count in line_counts.items():
                            unique_lines.append(f"{count:>4} {line}")
                    else:
                        unique_lines = list(line_counts.keys())

                    self.output.insert(tk.END, '\n'.join(unique_lines) + '\n')
                else:
                    self.output.insert(tk.END, f"{content}\n")
        elif command == "cp":
            if len(args) != 2:
                self.output.insert(tk.END, "Usage: cp SOURCE DESTINATION\n")
            else:
                source, destination = args
                success, message = self.vfs.copy_file(source, destination)
                self.output.insert(tk.END, f"{message}\n")
        elif command == "chown":
            if len(args) != 2:
                self.output.insert(tk.END, "Usage: chown OWNER FILE\n")
            else:
                owner, filename = args
                success, message = self.vfs.change_owner(filename, owner)
                self.output.insert(tk.END, f"{message}\n")
        else:
            self.output.insert(tk.END, f"{command} {args} {comment}\n")

        self.safe_see_end()
        self.safe_update()

    def run_command(self):
        """Выполняет команду из поля ввода (для ручного ввода)"""
        if not self.root or not self.root.winfo_exists():
            return

        cmd_input = self.entry.get()
        self.entry.delete(0, tk.END)
        self.execute_command_directly(cmd_input)

    def start_script_execution(self):
        """Начинает выполнение скрипта"""
        if not os.path.exists(self.script_path):
            self.output.insert(tk.END, f"Script file not found: {self.script_path}\n")
            self.safe_see_end()
            return

        try:
            with open(self.script_path, 'r', encoding='utf-8') as f:
                self.script_commands = [line.strip() for line in f.readlines()]
        except Exception as e:
            self.output.insert(tk.END, f"Error reading script: {str(e)}\n")
            self.safe_see_end()
            return

        self.is_running_script = True
        self.current_script_command = 0
        self.execute_next_script_command()

    def execute_next_script_command(self):
        """Выполняет следующую команду из скрипта"""
        # Проверяем, существует ли еще окно и не завершен ли скрипт
        if not self.is_running_script or not self.root or not self.root.winfo_exists():
            self.is_running_script = False
            return

        if self.current_script_command >= len(self.script_commands):
            self.is_running_script = False
            return

        cmd = self.script_commands[self.current_script_command]
        self.current_script_command += 1

        if not cmd:
            # Пустая строка - переходим к следующей
            self.root.after(100, self.execute_next_script_command)
            return

        if cmd.lstrip().startswith("#"):
            # Комментарий - просто выводим
            self.output.insert(tk.END, f"{cmd}\n")
            self.safe_see_end()
            self.root.after(100, self.execute_next_script_command)
        else:
            # Команда - выполняем
            self.execute_command_directly(cmd)
            # Запускаем следующую команду после небольшой задержки
            self.root.after(300, self.execute_next_script_command)

    def parse_arguments(self):
        """Парсит аргументы командной строки"""
        # sys.argv[0] - имя скрипта
        if len(sys.argv) >= 2:
            self.vfs_path = sys.argv[1]
        if len(sys.argv) >= 3:
            self.script_path = sys.argv[2]

    def run(self):
        self.parse_arguments()
        self.setup_gui()
        self.root.mainloop()


if __name__ == "__main__":
    emulator = VFSEmulator()
    emulator.run()