import os

def mkdir(dir, r=True):
    if not os.path.exists(dir):
        os.makedirs(dir)

def openFile(dir, file, mode, r=False):
    os.path.expanduser(os.path.join(dir, file))