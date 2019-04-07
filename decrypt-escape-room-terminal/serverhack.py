import random
import string
import os
from termcolor import colored, cprint
import time
import subprocess
import readline
import terminal
import camera
import importlib

IP = '158.24.64.6'
SERVER_PASSWORD = '123'

class VirtualInstance:
    def __init__(self, name):
        self.name = name

    def ls(self):
        raise NotImplementedError()

    def read(self):
        raise NotImplementedError()

    def extract(self, parent):
        raise NotImplementedError()

    def print(self):
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()
    
    @staticmethod
    def list_command(current_directory):
        for f in current_directory.ls():
            if type(f) is VirtualFolder:
                s = "{:>15}\t\tfolder".format(f.name)
            else:
                s = "{:>15}\t\t{} file\t{} bytes".format(
                    f.name, f.name[-3:], f.size)
            print(colored( s,'cyan'))

    @staticmethod
    def read_file_command(current_directory, arg):
        file = current_directory.get_file(arg)
        if file != None:
            print(colored(
                file.read(),
                'white',
                attrs=['dark']
            ))
            print()
        else:
            print("file does not exist:", arg)
    
    @staticmethod
    def download_file_command(current_directory, zip_file, arg):
        print("verifying url...")
        terminal.show_progress(0.001, 100)
        if arg.strip() in ['178.345.235.23/bk.tools.zip',
                            'http://178.345.235.23/bk.tools.zip',
                            'https://178.345.235.23/bk.tools.zip',
                            'ftp://178.345.235.23/bk.tools.zip']:
            print("downloading file...")
            terminal.show_progress(0.08, 100)
            current_directory.files.append(zip_file)
            print(zip_file.name, "successfully downloaded from remote server")
        else:
            print("invalid url:", arg)

    @staticmethod
    def extract_file_command(current_directory, arg):
        file = current_directory.get_file(arg)
        if file != None:
            terminal.show_progress(0.02, 100)
            extracted = file.extract(current_directory)
            current_directory.files.append(extracted)
            print(file.name, "successfully extracted")
        else:
            print("file does not exist:", arg)

    @staticmethod
    def print_file_command(current_directory, arg):
        file = current_directory.get_file(arg)
        if file != None:
            print(file.name, "printing...")
            file.print()
        else:
            print("file does not exist:", arg)

    @staticmethod
    def run_file_command(current_directory, arg):
        importlib.reload(camera)
        file = current_directory.get_file(arg)
        if file != None:
            file.run()
        else:
            print("file does not exist:", arg)

    @staticmethod
    def help_command():
        with open('help.txt', 'r', encoding="utf-8") as f:
            x = f.read().strip()
        print(colored(
            x,
            'white'
        ))


class VirtualFolder(VirtualInstance):
    def __init__(self, name, files, parent):
        super().__init__(name)
        self.parent = parent if parent != None else self
        self.files = files

    def ls(self):
        self.files.sort(key=lambda a: ("0" if type(a) is VirtualFolder else "1") + a.name )
        return self.files

    def path(self):
        if self.parent == None or self.parent == self:
            return ""
        return self.parent.path() + "/" + self.name

    def get_file(self, dir):
        if dir == '.':
            return self
        if dir == '..':
            return self.parent
        for f in self.files:
            if dir == f.name:
                return f
        else:
            return None

    def cd(self, dir):
        f = self.get_file(dir)
        if f is None:
            return self
        else:
            if type(f) == VirtualFolder:
                return f
            else:
                return self


class VirtualFile(VirtualInstance):
    def __init__(self, name, size, content):
        super().__init__(name)
        self.size = size
        self.content = content

    def read(self):
        raise "not a valid executable python file: {}".format(self.name)

    def read(self):
        return self.generateRandomString(len(self.name) + self.size)

    def extract(self, parent):
        raise Exception(
            "CRC Exception - File is not a valid archieve or the file is corrupted.")

    def generateRandomString(self, seed):

        def take_choices(l, n):
            if type(l) is str:
                l = list(l)
            r = []
            for i in range(n):
                r.append(random.choice(l))
            return r

        return ''.join(
            take_choices(
                string.ascii_uppercase + string.digits + 
                string.ascii_lowercase + string.punctuation,
                self.size
            )
        )


class TextFile(VirtualFile):
    def __init__(self, name, content):
        super().__init__(name, len(content), content)

    def read(self):
        return self.content

    def print(self):
        print("text file is not a valid prinatable file")
        return True


class ZipFile(VirtualFile):
    def __init__(self, name, ratio, content):
        full_size = sum(map(lambda x: x.size, content), 0)*ratio + 10
        super().__init__(name, int(full_size), content)

    def extract(self, parent):
        return VirtualFolder(self.name[:-4], self.content, parent)


class PrintableFile(VirtualFile):
    def __init__(self, name):
        super().__init__(name, 12241, '')

    def print(self):
        subprocess.call(['lp', 'snapshot.jpeg'])
        return True

class ExecutableFile(VirtualFile):
    def __init__(self, name, file):
        super().__init__(name, 256, '')

    def run(self):
        camera.exit_pressed = False
        print("File is encrypted with a key.")
        x = input("encryption key: ")
        if x == "camera":
            camera.run_image_processor()
            time.sleep(1)
            terminal.clear_terminal()
        else:
            print("Wrong password")
        
        
    

def server_hack_task():
    terminal.clear_terminal()
    with open('head2.txt', 'r', encoding="utf-8") as f:
        msg = colored(f.read().strip(), 'green', attrs=['bold'])
        print(msg)
    print()
    

    # Server log file
    with open('server_log.txt', 'r', encoding="utf-8") as f:
        server_log_text = f.read().strip()
    server_log = TextFile('server.log', server_log_text)

    # Fake files
    fake_file_1 = TextFile('run.txt', '-- nothing --')
    fake_file_2 = TextFile('dconf.txt', '-- empty --')
    fake_file_3 = TextFile('yuri.chr', '-- deleted --')
    fake_file_4 = TextFile('iporf.chr', '-- nothing --')
    fake_file_5 = TextFile('abcd.bin', '-- invalid data --')

    # Zip file
    printable_file = PrintableFile('cr.pdf')
    cam_file = ExecutableFile('camera.shl', 'camera.py')
    zip_file = ZipFile('bk.tools.zip', 0.91, [printable_file, fake_file_1, cam_file])

    # Folders
    folder1 = VirtualFolder('log', [server_log], None)
    folder2 = VirtualFolder('usr', [fake_file_2, fake_file_3], None)
    folder3 = VirtualFolder('lib', [fake_file_5], None)
    root = VirtualFolder('', [folder1, folder2, folder3, fake_file_4], None)
    folder1.parent = root
    folder2.parent = root
    folder3.parent = root

    current_directory = root
    while True:
        try:
            x = input(colored(
                'CE:' + IP + '-BASE:$~{}/ '.format(current_directory.path()),
                'green',
                attrs=['bold'])).strip()
            if x == '':
                continue
            x = x.split()
            command = x.pop(0)
            arg = '.' if len(x) == 0 else x.pop(0)

            if command == 'list':
                VirtualInstance.list_command(current_directory)
            elif command == 'cd':
                current_directory = current_directory.cd(arg)
            elif command == 'read':
                VirtualInstance.read_file_command(current_directory, arg)
            elif command == 'wget':
                VirtualInstance.download_file_command(current_directory, zip_file, arg)
            elif command == 'extract':
                VirtualInstance.extract_file_command(current_directory, arg)
            elif command == 'run':
                VirtualInstance.run_file_command(current_directory, arg)
            elif command == 'clear':
                terminal.clear_terminal()
                with open('head2.txt', 'r', encoding="utf-8") as f:
                    msg = colored(f.read().strip(), 'green', attrs=['bold'])
                    print(msg)
                print()
            elif command == 'print':
                VirtualInstance.print_file_command(current_directory, arg)
            elif command == 'help':
                VirtualInstance.help_command()
            elif command == 'exit':
                terminal.clear_terminal()
                exit(0)
            else:
                print("unknown command:", command)
        except NotImplementedError:
            print("invalid usage of command",command, "with args:", arg)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    terminal.clear_terminal()
    with open('head.txt', 'r', encoding="utf-8") as f:
        msg = colored(terminal.center(f.read()), 'green', attrs=['bold'])
        print(msg)
    while True:
        msg = colored("Enter " + IP + " password: ", 'yellow', attrs=['bold'])
        x = input(msg)
        print("Verifing password...")
        if x == SERVER_PASSWORD:
            terminal.show_progress(0.01, 100)
            print()
            print(colored("Logging in...", 'green'))
            terminal.show_progress(0.08, 100)
            with open('login.txt', 'r', encoding="utf-8") as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if i%50 == 0:
                        time.sleep(0.05)
                    print(line.strip())
                    if i%432==0:
                        terminal.show_progress(0.009, random.randint(1, 75))
            terminal.show_progress(0.005, random.randint(1, 75))
            terminal.clear_terminal()
            time.sleep(2.0)
            server_hack_task()
        else:
            terminal.show_progress(0.01, random.randint(1, 75))
            print(colored("invalid password", 'red', attrs=['bold']))
        print()
    
