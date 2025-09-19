import tkinter as tk
import sys
import os

KNOWN_COMMANDS = ["ls", "cd", "exit"]

def parse_command(command_str):
    parts = command_str.strip().split()
    if not parts:
        return None, []
    return parts[0], parts[1:]

def run_command():
    cmd_input = entry.get()
    command, args = parse_command(cmd_input)
    comment = ""

    for arg in args:
        if arg.startswith("#"):
            comment = args[args.index(arg):]
            args = args[:args.index(arg)]
            comment = " ".join(comment)

    if not command:
        output.insert(tk.END, "No command entered.\n")
        return

    if command not in KNOWN_COMMANDS:
        output.insert(tk.END, f"Unknown command: {command}\n")
    elif command == "exit":
        if args:
            output.insert(tk.END, f"Unknown arguments: {args}\n")
        else:
            root.destroy()
    else:
        output.insert(tk.END, f"{command} {args} {comment}\n")

    entry.delete(0, tk.END)

def execute_script(script_path):
    """Выполняет команды из файла скрипта"""
    
    if not os.path.exists(script_path):
        output.insert(tk.END, f"Script file not found: {script_path}\n")
        return
    
    with open(script_path, 'r') as f:
        commands = f.readlines()
    
    for cmd in commands:
        if cmd:
            if cmd.lstrip().startswith("#"):
                output.insert(tk.END, f"{str(cmd.lstrip()).rstrip()}\n")
            else:
                entry.delete(0, tk.END)
                entry.insert(0, cmd)
                output.insert(tk.END, f"{str(cmd.lstrip()).rstrip()}\n")
                run_command()
                root.update()

# GUI setup
title = "VFS"
script = ""

if len(sys.argv) > 0 and len(sys.argv) < 3:
    title = sys.argv[0]
    if len(sys.argv) == 2:
        script = sys.argv[1]
else:
    if len(sys.argv) == 0:
        print("Incorrect emulator call! Not enough parameters")
    else:
        print("Incorrect emulator call! Too many parameters")
    sys.exit(1)

root = tk.Tk()
root.title(title)


# Frame для приглашения и поля ввода
input_frame = tk.Frame(root)
input_frame.pack(padx=10, pady=10, fill='x')

# Неподвижный текст-приглашение (Label)
prompt_label = tk.Label(input_frame, text="vfs_invitation$> ", font=("Courier", 12))
prompt_label.pack(side='left')

# Поле ввода команд
entry = tk.Entry(input_frame, width=75, font=("Courier", 12))
entry.pack(side='left', fill='x', expand=True)
entry.bind("<Return>", lambda event: run_command())

run_button = tk.Button(root, text="Run", command=run_command)
run_button.pack(pady=5)

output = tk.Text(root, height=15, width=80, font=("Courier", 12))
output.pack(padx=10, pady=10)

if script:
    # Запускаем выполнение скрипта после небольшой задержки, чтобы GUI успел инициализироваться
    root.after(100, lambda: execute_script(script))

root.mainloop()
