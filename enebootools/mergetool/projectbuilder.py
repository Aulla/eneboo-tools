# encoding: UTF-8
import os
from lxml import etree
from enebootools.lib.utils import one, find_files, get_max_mtime, read_file_list
from enebootools.mergetool import flpatchdir
import shutil


class BuildInstructions(object):
    def __init__(self, iface, instructions):
        self.instructions = instructions
        self.iface = iface
        assert self.instructions.tag in ["BuildInstructions"]
        self.path = self.instructions.get("path")
        self.dstfolder = self.instructions.get("dstfolder")
        self.feature = self.instructions.get("feature")
        self.target = self.instructions.get("target")
        self.dstpath = os.path.join(self.path, self.dstfolder)

    def execute(self, rebuild=True):
        from enebootools import mergetool

        if os.path.exists(self.dstpath):
            if self.instructions[0].tag != "UpdatePatchAction" and not mergetool.ONLY_FILES:
                if not rebuild:
                    return True

                self.iface.info("Borrando carpeta %s . . . " % self.dstpath)
                shutil.rmtree(self.dstpath)

        if not os.path.exists(self.dstpath):
            os.mkdir(self.dstpath)
        for instruction in self.instructions:
            # print("-->", instruction.tag, self.target, self.feature, self.dstpath)
            if instruction.tag == "CopyFolderAction":
                self.copyFolder(**instruction.attrib)
            elif instruction.tag == "ApplyPatchAction":
                self.applyPatch(**instruction.attrib)
            elif instruction.tag == "CreatePatchAction":
                self.createPatch(**instruction.attrib)
            elif instruction.tag == "UpdatePatchAction":
                self.updatePatch(**instruction.attrib)
            elif instruction.tag == "Message":
                self.message(**instruction.attrib)
            else:
                self.iface.warn("Accion %s desconocida" % instruction.tag)

    def message(self, text):
        self.iface.msg(text)

    def copyFolder(self, src, dst, create_dst=False):
        from enebootools import mergetool

        only_files = mergetool.ONLY_FILES

        if create_dst == "yes":
            create_dst = True
        if create_dst == "no":
            create_dst = False
        self.iface.info("Copiando %s : %s -> %s. . . " % (dst, src, self.dstpath))
        dst = os.path.join(self.dstpath, dst)
        if not os.path.exists(src):
            self.iface.error("La carpeta %s no existe" % src)
            return False
        pdst = os.path.dirname(dst)
        if not os.path.exists(pdst):
            if create_dst:
                os.makedirs(pdst)
            else:
                self.iface.error("La carpeta %s no existe" % pdst)
                return False
        if os.path.exists(dst) and not only_files:
            self.iface.error("La carpeta %s ya existe!" % dst)
            return False

        if not only_files:
            shutil.copytree(src, dst)
        else:
            if not os.path.exists(dst):
                raise Exception("No se puede hacer build parcial. La carpeta %s no existe" % dst)
            self.update_files_only(only_files, src, self.dstpath)

    def update_files_only(self, files_only, src, dst):
        files_dir = {}
        for file_ in files_only:
            files_dir[file_[1]] = file_[0]
        files_found = []

        for root, dirs, files in os.walk(src):
            for file_name in files_dir.keys():
                if file_name in files:
                    files_found.append((file_name, os.path.join(root, file_name)))

        for file_found in files_found:
            file_name = file_found[0]
            src_path = file_found[1]
            dst_path = os.path.join(dst, files_dir[file_name], file_name)
            self.iface.info("Update (...)%s - (...)%s . . ." % (src_path[-64:], dst_path[-64:]))
            shutil.copyfile(src_path, dst_path)

    def applyPatch(self, src):
        self.iface.info("Aplicando parche (...)%s . . ." % (src[-64:]))
        flpatchdir.patch_folder_inplace(self.iface, src, self.dstpath)

    def createPatch(self, src, dst):
        self.iface.info("Creando parche (...)%s - (...)%s . . ." % (src[-48:], dst[-48:]))
        flpatchdir.diff_folder(self.iface, src, dst, self.dstpath, inplace=True)

    def updatePatch(self, src, dst):
        self.iface.info("Actualizando parche en %s" % (src))
        flpatchdir.update_patch_folder(self.iface, src, dst, self.dstpath, self.path)


def build_xml_file(iface, xmlfile, rebuild=True):
    parser = etree.XMLParser(
        ns_clean=False,
        encoding="UTF-8",
        remove_blank_text=True,
    )
    bitree = etree.parse(xmlfile, parser)
    build_instructions = bitree.getroot()
    bi = BuildInstructions(iface, build_instructions)
    bi.execute(rebuild)


def build_xml(iface, xml, rebuild=True):
    bi = BuildInstructions(iface, xml)
    bi.execute(rebuild)
