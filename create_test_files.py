import zipfile


def create_test_vfs_with_text_files():
    """Создает VFS с текстовыми файлами для тестирования новых команд"""

    with zipfile.ZipFile('test_vfs.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Файл с повторяющимися строками для uniq
        zipf.writestr('duplicates.txt',
                      'apple\napple\nbanana\napple\ncherry\nbanana\ncherry\ncherry\ndate\n')

        # Файл с большим количеством строк для head/tail
        lines = [f"Line {i:03d}: This is test line number {i}" for i in range(1, 51)]
        zipf.writestr('long_file.txt', '\n'.join(lines))

        # Файл с логами
        log_lines = [
            "2024-01-01 10:00:00 INFO: System started",
            "2024-01-01 10:00:01 WARN: Low memory",
            "2024-01-01 10:00:02 ERROR: Disk full",
            "2024-01-01 10:00:03 INFO: Backup started",
            "2024-01-01 10:00:04 INFO: Backup completed",
            "2024-01-01 10:00:05 ERROR: Network timeout",
            "2024-01-01 10:00:06 WARN: High CPU usage",
            "2024-01-01 10:00:07 INFO: User login",
            "2024-01-01 10:00:08 INFO: File uploaded",
            "2024-01-01 10:00:09 ERROR: Permission denied",
            "2024-01-01 10:00:10 INFO: Cache cleared",
            "2024-01-01 10:00:11 WARN: Slow response",
            "2024-01-01 10:00:12 INFO: Database updated",
            "2024-01-01 10:00:13 ERROR: Connection lost",
            "2024-01-01 10:00:14 INFO: Connection restored"
        ]
        zipf.writestr('server.log', '\n'.join(log_lines))

        # Файл с конфигурацией
        zipf.writestr('config.txt',
                      '# Server configuration\n'
                      'host=localhost\n'
                      'port=8080\n'
                      'timeout=30\n'
                      'max_connections=100\n'
                      'cache_size=256\n'
                      'log_level=INFO\n'
                      'backup_enabled=true\n'
                      'backup_interval=24\n')

        # Скрытые файлы
        zipf.writestr('.hidden_file', 'This is a hidden file\n')
        zipf.writestr('.config/secret.txt', 'Secret configuration\n')

        # Обычные файлы и папки
        zipf.writestr('readme.txt', 'Test VFS for command demonstration\n')
        zipf.writestr('data/file1.txt', 'Data file 1\n')
        zipf.writestr('data/file2.txt', 'Data file 2\n')


if __name__ == "__main__":
    create_test_vfs_with_text_files()
    print("Created test_vfs.zip with files for new commands")