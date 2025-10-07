@echo off
echo === Testing All VFS Archives ===

echo 1. Testing minimal VFS...
start /wait python 1_3.py minimal_vfs.zip basic_test.txt

echo 2. Testing basic VFS...
start /wait python 1_3.py test_vfs.zip basic_test.txt

echo 3. Testing complex VFS...
start /wait python 1_3.py complex_vfs.zip complex_test.txt

echo 4. Testing error cases...
start /wait python 1_3.py nonexistent.zip error_test.txt
start /wait python 1_3.py invalid_file.txt error_test.txt

echo === All tests completed ===
pause