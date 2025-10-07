@echo off
echo === Stage 4 Testing ===

echo Creating test VFS...
python create_test_files.py

echo Running Stage 4 tests...
python 1_4.py test_vfs.zip stage_4_test.txt

pause