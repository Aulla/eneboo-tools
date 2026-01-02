# encoding: UTF-8
__version__ = "1.0.0"
__PROGRAM__NAME__ = "Eneboo Tools UIImage"
from enebootools.uiimage import uiimage
from enebootools import EnebooToolsInterface

"""
    Packager es una utilidad para Eneboo que realiza paquetes al estilo 
    .eneboopkg o .abanq que luego el motor Eneboo puede leer y cargar
    
    Un paquete .eneboopkg es una serialización de ficheros que contiene los 
    módulos y ficheros a cargar en una base de datos. 

"""


class UIImageInterface(EnebooToolsInterface):
    module_description = "Herramientas para extraer imágenes de los ficheros .UI"

    def __init__(self, setup_parser=True):
        EnebooToolsInterface.__init__(self, False)
        self.packager_mode = None
        self.include_test = False
        if setup_parser:
            self.setup_parser()

    def setup_parser(self):
        EnebooToolsInterface.setup_parser(self)

        self.download_action = self.parser.declare_action(
            name="download",
            args=["filename"],
            options=[],
            description="Extrae las imagenes de un fichero dado",
            call_function=self.do_download,
        )

        self.check_action = self.parser.declare_action(
            name="check",
            args=["filename"],
            options=[],
            description="Comprueba las imagenes de un fichero dado",
            call_function=self.do_check,
        )

        self.upload_action = self.parser.declare_action(
            name="upload",
            args=["filename", "files"],
            options=[],
            description="Inserta las imagenes $files en un fichero dado $filename",
            call_function=self.do_upload,
        )

        self.fix_data_len_action = self.parser.declare_action(
            name="fixdatalen",
            args=["filename"],
            options=[],
            description="Repasa el tamaño de las imagenes que contiene un fichero",
            call_function=self.do_fixdatalen,
        )

        self.theme_action = self.parser.declare_action(
            name="theme",
            args=["filename", "project_path", "method"],
            options=[],
            description="eneboo-uiimage theme [archivo theme] [ruta proyecto] [metodo]. overwrite: sobreescribe el/los archivos, modify: crea un nuevo archivo adjuntando el sufijo -modify",
            call_function=self.do_theme,
        )

    # :::: ACTIONS ::::

    def do_download(self, filename):
        try:

            return uiimage.download_images(filename)
        except Exception as e:
            self.exception(type(e).__name__, str(e))
    
    def do_check(self, filename):
        try:
            return uiimage.check_images(filename)
        except Exception as e:
            self.exception(type(e).__name__, str(e))
    
    def do_upload(self, filename, files):
        try:
            return uiimage.upload_images(filename, files)
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_fixdatalen(self, filename):
        try:
            return uiimage.fix_datalen(filename)
        except Exception as e:
            self.exception(type(e).__name__, str(e))
    def do_theme(self, filename, proyect_path, method):
        try:
            return uiimage.searchFile(filename, proyect_path, method)
        except Exception as e:
            self.exception(type(e).__name__, str(e))


