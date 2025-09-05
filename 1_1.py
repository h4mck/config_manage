import tkinter as tk

KNOWN_COMMANDS = ["ls", "cd", "exit"]

def parse_command(command_str):
    parts = command_str.strip().split()
    if not parts:
        return None, []
    return parts[0], parts[1:]

def run_command():
    cmd_input = entry.get()
    command, args = parse_command(cmd_input)

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
        output.insert(tk.END, f"{command} {args}\n")

    entry.delete(0, tk.END)

# GUI setup
root = tk.Tk()
root.title("VFS")

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

root.mainloop()
