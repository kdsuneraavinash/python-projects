import random
import string
import os
from termcolor import colored, cprint
import progressbar
import time
import subprocess

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


class VirtualFolder(VirtualInstance):
    def __init__(self, name, files, parent):
        super().__init__(name)
        self.parent = parent if parent != None else self
        self.files = files

    def ls(self):
        file_names = map(lambda x: x.name, self.files)
        return '\n'.join(file_names)
    
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
        raise Exception("CRC Exception - File is not a valid archieve or the file is corrupted.")

    def generateRandomString(self, seed):
        return ''.join(
                    random.choices(
                        string.ascii_uppercase + string.digits + string.ascii_lowercase + string.punctuation, 
                        k=self.size
                        )
                    )

class TextFile(VirtualFile):
    def __init__(self, name, content):
        super().__init__(name, len(content), content)
    
    def read(self):
        return self.content
    
    def print(self):
        print("PRINTED TEXT================")
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

def show_progress(wait):
    for i in progressbar.progressbar(range(100)):
        time.sleep(wait)

def main():
    with open('server_log.txt', 'r') as f:
        server_log_text = f.read().strip()
    
    # Importnat Files
    server_log = TextFile('server.log', server_log_text)

    printable_file = PrintableFile('cr.pdf')
    zip_file = ZipFile('hhtgh.zip', 0.91, [printable_file])

    folder = VirtualFolder('log', [server_log], None)
    root = VirtualFolder('', [folder], None)
    folder.parent = root

    current_directory = root
    while True:
        try:
            print(colored(
                'CE:123.23.23.5-BASE:$~{}/ '.format(current_directory.path()), 
                'green',
                attrs=['bold']), end="")
            x = input().strip()
            if x == '':
                continue
            x = x.split()
            command = x.pop(0)
            arg = '.' if len(x) == 0 else x.pop(0)

            if command == 'list':
                print(colored(
                    current_directory.ls(),
                    'cyan'
                ))
            elif command == 'cd':
                current_directory = current_directory.cd(arg)
            elif command == 'read':
                file = current_directory.get_file(arg)
                if file != None:
                    print(colored(
                        file.read(),
                        'white',
                        attrs=['dark']
                    ))
            elif command == 'wget':
                if arg == '178.345.235.23/hhtgh.zip':
                    show_progress(0.08)
                    current_directory.files.append(zip_file)
            elif command == 'extract':
                file = current_directory.get_file(arg)
                if file != None:
                    show_progress(0.02)
                    extracted = file.extract(current_directory)
                    current_directory.files.append(extracted)
            elif command == 'exit':
                break
            elif command == 'clear':
                os.system('clear')
            elif command == 'print':
                file = current_directory.get_file(arg)
                if file != None:
                    file.print()
            elif command == 'help':
                with open('help.txt', 'r') as f:
                    x = f.read().strip()
                print(colored(
                    x,
                    'white'
                ))
        except NotImplementedError:
            print("argument invalid:", arg)
        except Exception as e:
            print(e)

    
if __name__ == "__main__":
    os.system('clear')
    main()
