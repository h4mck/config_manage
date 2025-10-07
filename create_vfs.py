import zipfile

def create_stage5_vfs():
    """Создает VFS для тестирования команд Этапа 5"""
    
    with zipfile.ZipFile('stage5_vfs.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Файлы для копирования
        zipf.writestr('original.txt', 
                     'This is the original file content.\n'
                     'It has multiple lines.\n'
                     'Line 3 of original file.\n'
                     'Line 4 of original file.\n')
        
        zipf.writestr('config.cfg', 
                     '# Configuration file\n'
                     'setting1=value1\n'
                     'setting2=value2\n'
                     'setting3=value3\n')
        
        zipf.writestr('data/sample.dat', 
                     'Sample data file\n'
                     'This file is in a subdirectory\n'
                     'It can be copied to other locations\n')
        
        # Файлы с разным содержимым для демонстрации
        zipf.writestr('readonly.txt', 
                     'This file starts as owned by "user"\n'
                     'We will change its owner later\n')
        
        zipf.writestr('system/file.sys', 
                     'System file content\n'
                     'Important system data\n')
        
        # Лог файл для демонстрации
        log_content = '\n'.join([f"Log entry {i:03d}" for i in range(1, 21)])
        zipf.writestr('app.log', log_content)

if __name__ == "__main__":
    create_stage5_vfs()
    print("Created stage5_vfs.zip for Stage 5 testing")
