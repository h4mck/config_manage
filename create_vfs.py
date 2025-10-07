#!/usr/bin/env python3
"""
Скрипт для создания всех тестовых VFS архивов
"""

import zipfile
import os

def create_minimal_vfs():
    """Минимальный VFS"""
    with zipfile.ZipFile('minimal_vfs.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('hello.txt', 'Hello from minimal VFS!')
        zipf.writestr('readme.txt', 'This is a minimal VFS for testing.')

def create_test_vfs():
    """Базовый тестовый VFS"""
    with zipfile.ZipFile('test_vfs.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Корневые файлы
        zipf.writestr('file1.txt', 'This is the content of file1.txt\nLine 2 of file1\nLine 3 of file1')
        zipf.writestr('readme.txt', 'Welcome to VFS Emulator!\nThis is a test virtual file system.')
        zipf.writestr('config.json', '{"version": "1.0", "author": "VFS Emulator"}')
        
        # Бинарный файл
        binary_content = bytes([i % 256 for i in range(100)])
        zipf.writestr('binary_file.bin', binary_content)
        
        # Папки
        zipf.writestr('folder1/file1_1.txt', 'Content of file1_1 in folder1')
        zipf.writestr('folder1/file1_2.txt', 'Content of file1_2 in folder1')
        zipf.writestr('folder2/document.txt', 'Important document in folder2')
        zipf.writestr('folder2/subfolder/deep_file.txt', 'This file is deep in the structure!')

def create_complex_vfs():
    """Сложный VFS с 3+ уровнями вложенности"""
    with zipfile.ZipFile('complex_vfs.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Многоуровневая структура
        zipf.writestr('readme.txt', 'Complex VFS Structure\nMultiple levels of folders')
        
        # Уровни 1-3
        zipf.writestr('level1/file1.txt', 'File in level1')
        zipf.writestr('level1/level2/file2.txt', 'File in level2')
        zipf.writestr('level1/level2/level3/file3.txt', 'File in level3 - deepest level!')
        
        # Другая ветка
        zipf.writestr('apps/app1/src/main.py', 'def main():\n    print("App1 main")')
        zipf.writestr('apps/app2/docs/api.md', '# API Reference')
        
        # Данные
        zipf.writestr('data/raw/dataset1.csv', 'id,name,value\n1,test,100\n2,demo,200')
        zipf.writestr('data/processed/results.json', '{"analysis": "complete"}')

def create_invalid_vfs():
    """Создает файл с неправильным форматом (не ZIP)"""
    with open('invalid_file.txt', 'w') as f:
        f.write('This is not a valid ZIP file!\nJust plain text.')

if __name__ == "__main__":
    print("Creating VFS archives...")
    
    create_minimal_vfs()
    print("Created minimal_vfs.zip")
    
    create_test_vfs()
    print("Created test_vfs.zip")
    
    create_complex_vfs()
    print("Created complex_vfs.zip")
    
    create_invalid_vfs()
    print("Created invalid_file.txt (for error testing)")
    
    print("\nAll VFS archives created successfully!")
    print("\nFiles created:")
    print("- minimal_vfs.zip    (simple test)")
    print("- test_vfs.zip       (basic test)") 
    print("- complex_vfs.zip    (3+ levels)")
    print("- invalid_file.txt   (error test)")
