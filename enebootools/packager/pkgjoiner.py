# encoding: UTF-8
import zlib, os, sys, re, hashlib, pathlib
from enebootools.packager.pkgsplitter import to_uint32
from enebootools.packager import __version__, __PROGRAM__NAME__
from enebootools.lib.utils import find_files

__package_header__ = "%s %s" % (__PROGRAM__NAME__, __version__)


def write_compressed(f1, txt_or_bytes):
    data = txt_or_bytes.encode() if isinstance(txt_or_bytes, str) else txt_or_bytes

    zipped_data = len(data).to_bytes(4, byteorder="big") + zlib.compress(data)
    f1.write(len(zipped_data).to_bytes(4, byteorder="big"))
    f1.write(zipped_data)

    # write_string(f1,zipped_text, binary = True)


def write_string(f1, txt, binary=False):
    if binary:
        text = txt
    else:
        text = txt.rstrip()
        if not text:
            f1.write(int(0).to_bytes(4, byteorder="big"))
            return

    f1.write(len(text).to_bytes(4, byteorder="big"))
    f1.write(text.encode())


def joinpkg(iface, packagefolder):
    if packagefolder.endswith("/"):
        packagefolder = packagefolder[:-1]
    if packagefolder.endswith("\\"):
        packagefolder = packagefolder[:-1]
    iface.info2("Empaquetando carpeta %s . . ." % packagefolder)
    packagename = packagefolder + ".eneboopkg"
    f1 = open(packagename, "w")
    n = 0
    for filename in sorted(os.listdir(packagefolder)):
        n += 1
        format = "string"
        if filename.endswith(".file"):
            format = "compressed"
        contents = open(os.path.join(packagefolder, filename)).read()
        if format == "string":
            sys.stdout.write(".")
            write_string(f1, contents)
        if format == "compressed":
            sys.stdout.write("*")
            write_compressed(f1, contents)
        sys.stdout.flush()
    f1.close()
    print()
    print("Hecho. %d objetos empaquetados en %s" % (n, packagename))


def createpkg(iface, modulefolder, dst_file, emulate_mode):
    global __package_header__
    module_folder_list = []
    if modulefolder.find(",") > -1:
        module_folder_list = modulefolder.split(",")
    else:
        module_folder_list.append(modulefolder)

    current_list = list(module_folder_list)
    module_folder_list = []

    for current_folder in current_list:
        if current_folder.endswith(("/", "\\")):
            current_folder = current_folder[:-1]

        module_folder_list.append(current_folder)

    iface.info2("Creando paquete de módulos de %s . . ." % ", ".join(module_folder_list))
    outputfile = module_folder_list[0] + ".eneboopkg"

    if dst_file:
        outputfile = dst_file

    if emulate_mode:
        __package_header__ = "%s %s" % ("AbanQ Packager", __version__)

    f1 = open(outputfile, "wb")
    # VERSION
    write_string(f1, __package_header__)

    # RESERVADO 1
    write_string(f1, "")

    # RESERVADO 2
    write_string(f1, "")

    # RESERVADO 3
    write_string(f1, "")

    # MODULES
    modules = []
    for modulefolder in module_folder_list:
        modules = modules + find_files(modulefolder, "*.mod", True)

    file_folders = []
    modnames = []
    modlines = []
    for module in modules:
        file_folders.append(os.path.dirname(module))
        modnames.append(os.path.basename(module))
        # comentado para evitar posibles fallos:
        # modlines.append("<!-- Module %s -->\n" % module)
        inittag = False
        for modulefolder in module_folder_list:
            if not os.path.exists(os.path.join(modulefolder, module)):
                continue
            for line in open(
                os.path.join(modulefolder, module), encoding="ISO-8859-15", errors="replace"
            ):
                if line.find("<MODULE>") != -1:
                    inittag = True
                if inittag:
                    modlines.append(line)
                if line.find("</MODULE>") != -1:
                    inittag = False

            break

    modules_def = """<!DOCTYPE modules_def>
<modules>
%s
</modules>""" % (
        "".join(modlines)
    )

    write_compressed(f1, modules_def)
    # FILES XML
    file_list = []
    filelines = []
    shasum = ""
    ignored_ext = set([])
    load_ext = set([".qs", ".mtd", ".ts", ".ar", ".kut", ".qry", ".ui", ".xml", ".xpm", ".py"])
    list_modules = []
    for folder, module in zip(file_folders, modnames):
        fpath = ""
        for modulefolder in module_folder_list:
            if not os.path.exists(modulefolder):
                continue
            fpath = os.path.join(modulefolder, folder)
            if not os.path.exists(fpath):
                continue

            break

        path_dirs_list = pathlib.Path(fpath)
        if "test" in path_dirs_list.parts and not iface.include_test:
            print("carpeta %s incluye carpeta 'test' en path. Ignorado." % (fpath))
            continue

        files = find_files(fpath)
        modulename = re.search("^\w+", module).group(0)
        if modulename in list_modules:
            print("módulo %s (%s) Duplicado. Ignorado." % (modulename, fpath))
            continue

        print("->", fpath, modulename)
        list_modules.append(modulename)
        for filename in files:
            bname, ext = os.path.splitext(filename)

            if bname.startswith("test_") and not iface.include_test:
                # print("Ignorando %s" % bname)
                continue

            if ext not in load_ext:
                ignored_ext.add(ext)
                continue

            file_basename = os.path.basename(filename)
            filepath = os.path.join(fpath, filename)



            sha1text = hashlib.sha1(open(filepath, "rb").read()).hexdigest()
            sha1text = sha1text.upper()
            shasum += sha1text
            file_list.append(filepath)
            filelines.append(
                """  <file>
    <module>%s</module>
    <name>%s</name>
    <text>%s</text>
    %s
    <shatext>%s</shatext>
  </file>
"""
                % (
                    modulename,
                    file_basename,
                    file_basename,
                    "<skip>false</skip>" if emulate_mode else "",
                    sha1text,
                )
            )

    write_compressed(
        f1,
        """<!DOCTYPE files_def>
<files>
%s  <shasum>%s</shasum>
</files>
"""
        % ("".join(filelines), hashlib.sha1(shasum.encode()).hexdigest().upper()),
    )

    # FILE CONTENTS
    for filepath in file_list:
        sys.stdout.write(".")
        sys.stdout.flush()
        write_compressed(f1, open(filepath, "rb").read())
    print()
    # CLOSE
    f1.close()
    print("Paquete %s creado. Extensiones ignoradas: %s " % (outputfile, ignored_ext))
