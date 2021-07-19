import os, stat

#THIS FILE CONTAINS
#rmtree

#input: path of top directory to delete
#outputs: none
#removes directory tree

def rmtree(top):
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            filename = os.path.join(root, name)
            os.chmod(filename, stat.S_IWUSR) #potential issue
            os.remove(filename)
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(top)   