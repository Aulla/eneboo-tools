

from typing import List, Any
from enebootools.mergetool import flpatchqs, flpatchdir, MergeToolInterface, projectbuilder
from enebootools.assembler.config import cfg
import enebootools

import os
import shutil


def extract_qs(iface: 'enebootools.EnebooToolsInterface', source: str, destination: str, class_list) -> bool:

    iface.debug("Extranyendo de %s hasta %s, las clasess %s" %
                (source, destination, ",".join(class_list)))
    # Setear output

    # Buscar ficheros qs
    file_names = []

    if not os.path.exists(destination):
        os.mkdir(destination)

    for root, folders, files in os.walk(source):
        for file in files:

            if file.endswith(".qs"):
                file_names.append((file, root))

    for class_name in class_list:
        files_array = []
        class_path = os.path.join(destination, class_name)
        if os.path.exists(class_path):
            iface.debug("Borrando carpeta %s" % class_path)
            shutil.rmtree(class_path)
        os.mkdir(class_path)
        iface.info2("Extrayendo clase %s" % (class_name))
        for file_name, folder_name in file_names:
            file_path = os.path.abspath(os.path.join(folder_name, file_name))

            output_file_name = os.path.join(class_path, file_name)
            # Comprueba si la clase existe en el fichero...
            nfinal, flfinal = flpatchqs.file_reader(file_path)
            if flfinal is None:
                iface.warn("No se ha podido abrir el fichero %s" %
                           (file_path))
                continue

            flfinal = [line.replace("\t", "        ") for line in flfinal]
            clfinal = flpatchqs.qsclass_reader(iface, file_path, flfinal)
            if class_name not in list(clfinal['decl'].keys()):
                iface.debug2("La clase %s no se encuentra en el fichero %s" % (
                    class_name, file_path))
                continue

            iface.info2("Procesando fichero %s" %
                        (file_path))

            iface.set_output_file(output_file_name)

            flpatchqs.extract_classes_qs(iface, file_path, class_name)
            iface.output.close()
            if os.stat(output_file_name).st_size == 1:
                os.remove(output_file_name)
                continue

            # File name, partial
            files_array.append([file_path.replace(source, ''), True])

        generate_xml(iface, class_name, files_array, class_path)

    return True


def generate_xml(iface: 'enebootools.EnebooToolsInterface', class_name: str, files_data: List[Any], class_path: str):

    if iface.build_xml:
        iface.patch_name = class_name
        iface.info2("Generando xml en %s.xml" % iface.patch_name)
        xml_generator = flpatchdir.FolderCreatePatch(iface, '', '', class_path)
        for file_name, partial in files_data:
            if partial:
                xml_generator.create_action("patchXml", file_name)
            else:
                xml_generator.create_action("patchXml", file_name)

        xml_generator.create_patch(True)
