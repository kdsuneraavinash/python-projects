import random
import string
import os
from termcolor import colored, cprint
import progressbar
import time
import subprocess
import getpass
import signal, os
import readline

DEBUG = True

IP = '158.24.64.6'

def handler(signum, frame):
    pass

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
        show_progress(0.001, 100)
        if arg.strip() in ['178.345.235.23/hhtgh.zip',
                            'http://178.345.235.23/hhtgh.zip',
                            'https://178.345.235.23/hhtgh.zip',
                            'ftp://178.345.235.23/hhtgh.zip']:
            show_progress(0.08, 100)
            current_directory.files.append(zip_file)
            print(zip_file.name, "successfully downloaded from remote server")
        else:
            print("invalid url:", arg)

    @staticmethod
    def extract_file_command(current_directory, arg):
        file = current_directory.get_file(arg)
        if file != None:
            show_progress(0.02, 100)
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
    def help_command():
        with open('help.txt', 'r') as f:
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
        return self.generateRandomString(len(self.name) + self.size)

    def extract(self, parent):
        raise Exception(
            "CRC Exception - File is not a valid archieve or the file is corrupted.")

    def generateRandomString(self, seed):
        return ''.join(
            random.choices(
                string.ascii_uppercase + string.digits +
                string.ascii_lowercase + string.punctuation,
                k=self.size
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


def show_progress(wait, progress):
    for i in progressbar.progressbar(range(100)):
        if i > progress:
            print()
            break
        time.sleep(wait)


def server_hack_task():
    clear_terminal()
    with open('head2.txt', 'r') as f:
        print(f.read().strip())
    print()
    

    # Server log file
    with open('server_log.txt', 'r') as f:
        server_log_text = f.read().strip()
    server_log = TextFile('server.log', server_log_text)

    # Fake files
    fake_file_1 = TextFile('run.txt', '-- nothing --')
    fake_file_2 = TextFile('d.txt', '-- empty --')
    fake_file_3 = TextFile('yuri.chr', '-- deleted --')
    fake_file_4 = TextFile('run.chr', '-- nothing --')
    fake_file_5 = TextFile('abcd.bin', '-- invalid data --')

    # Printable file and zip file
    printable_file = PrintableFile('cr.pdf')
    zip_file = ZipFile('hhtgh.zip', 0.91, [printable_file])

    # Folders
    folder1 = VirtualFolder('log', [server_log, fake_file_1], None)
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
            elif command == 'clear':
                clear_terminal()
                with open('head2.txt', 'r') as f:
                    print(f.read().strip())
                print()
            elif command == 'print':
                VirtualInstance.print_file_command(current_directory, arg)
            elif command == 'help':
                VirtualInstance.help_command()
            else:
                print("unknown command:", command)
        except NotImplementedError:
            print("invalid usage of command",command, "with args:", arg)
        except Exception as e:
            print(e)


def clear_terminal():
    os.system('tput reset')

if __name__ == "__main__":
    if not DEBUG:
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTSTP, handler)

    clear_terminal()
    with open('head.txt', 'r') as f:
        print(f.read())
    while True:
        x = getpass.getpass("Enter " + IP + " password: ")
        print("Verifing password...")
        if x == '123':
            show_progress(0.01, 100)
            print()
            print("Logging in...")
            show_progress(0.08, 100)
            with open('login.txt', 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if i%50 == 0:
                        time.sleep(0.05)
                    print(line.strip())
                    if i%432==0:
                        show_progress(0.009, random.randint(1, 75))
            show_progress(0.005, random.randint(1, 75))
            server_hack_task()
        else:
            show_progress(0.01, random.randint(1, 75))
            print("invalid password")
        print()
    
