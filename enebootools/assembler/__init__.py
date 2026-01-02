# encoding: UTF-8


from enebootools import EnebooToolsInterface

from enebootools.assembler import copylib, database as asmdb
from enebootools.assembler import save_auto
from enebootools.tools import dumps


class AssemblerInterface(EnebooToolsInterface):
    module_description = "Herramientas de gestión de proyectos de mezcla"

    def __init__(self, setup_parser=True):
        EnebooToolsInterface.__init__(self, False)
        self.short_mode = False
        if setup_parser:
            self.setup_parser()

    def setup_parser(self):
        EnebooToolsInterface.setup_parser(self)

        self.new_action = self.parser.declare_action(
            name="new",
            args=["subfoldername", "description", "patchurl"],
            options=[],
            min_argcount=0,
            description="Crea una nueva plantilla de funcionalidad",
            call_function=self.do_new,
        )

        self.new_action.set_help_arg(
            subfoldername="Nombre de la subcarpeta que será creada. Debe seguir la plantilla extA999-codename.",
            description="Nombre descriptivo para la funcionalidad",
            patchurl="Ruta para importar un parche",
        )

        self.build_action = self.parser.declare_action(
            name="build",
            args=["feat", "target", "only_dep"],
            min_argcount=2,
            options=[],
            description="Construye el objetivo $target de la funcionalidad $feat. Si se especifica $only_dep solo actualiza en el build esa depdencia.",
            call_function=self.do_build,
        )
        self.build_action.set_help_arg(
            target="Objetivo a construir",
            feat="Funcionalidad a construir",
        )

        self.save_fullpatch_action = self.parser.declare_action(
            name="save-fullpatch",
            args=["feat"],
            options=[],
            description="Para la funcionalidad $feat guarda los cambios como parche completo",
            call_function=self.do_save_fullpatch,
        )
        self.build_action.set_help_arg(
            feat="Funcionalidad a construir",
        )

        self.save_recent_action = self.parser.declare_action(
            name="save",
            args=["feat"],
            options=[],
            description="Para la funcionalidad $feat guarda los cambios recientes en al parche actual",
            call_function=self.do_save_recent,
        )

        self.dump_action = self.parser.declare_action(
            name="dump",
            args=["feat", "dest_file", "exec_name"],
            min_argcount=1,
            options=[],
            description="Para la funcionalidad $feat genera un dump con el contenido de final",
            call_function=self.do_dump,
        )

        self.dump_action.set_help_arg(
            feat="Funcionalidad a almacenar el la bd",
            dest_file="Archivo de destino",
            exec_name="Nombre de ejecutable",
        )

        self.build_action.set_help_arg(
            feat="Funcionalidad a construir",
        )

        self.auto_save_action = self.parser.declare_action(
            name="save-auto",
            args=["feat"],
            options=[],
            description="Para la funcionalidad $feat guarda los cambios recientes en al parche actual automáticamente",
            call_function=self.do_save_auto,
        )
        self.build_action.set_help_arg(
            feat="Funcionalidad a construir",
        )

        self.test_deps_action = self.parser.declare_action(
            name="test-deps",
            args=["feat"],
            options=[],
            description="Para la funcionalidad $feat analiza qué dependencias faltan",
            call_function=self.do_test_deps,
        )
        self.test_deps_action.set_help_arg(
            feat="Funcionalidad a analizar",
        )

        self.dbupdate_action = self.parser.declare_action(
            name="dbupdate",
            args=[],
            options=[],
            description="Actualiza la base de datos de módulos y extensiones existentes",
            call_function=self.do_dbupdate,
        )

        self.list_objects_action = self.parser.declare_action(
            name="list-objects",
            args=[],
            options=[],
            description="Lista los objetos (módulos y funcionalidades) en la base de datos",
            call_function=self.do_list_objects,
        )

        self.howto_build_action = self.parser.declare_action(
            name="howto-build",
            args=["feat", "target"],
            options=[],
            description="Explica los pasos a seguir para construir el objetivo $target de la funcionalidad $feat",
            call_function=self.do_howto_build,
        )
        self.howto_build_action.set_help_arg(
            target="Objetivo a construir",
            feat="Funcionalidad a construir",
        )

        self.parser.declare_option(
            name="short",
            short="s",
            description="Usa el modo de definiciones corto",
            level="parser",
            call_function=self.set_short_mode,
        )

        self.copy_action = self.parser.declare_action(
            name="copy",
            args=["ext_name", "folder"],
            description="Copia la $ext_name y dependencias en la carpeta $folder",
            options=[""],
            call_function=self.do_copy_action,
        )
        self.copy_action.set_help_arg(
            ext_name="Nombre de la extensión a copiar",
            classlist="Carpeta donde se va a copiar la extensión y dependencias",
        )

    # :::: ACTIONS ::::

    def do_dbupdate(self):
        try:
            return asmdb.update_database(self)
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_list_objects(self):
        try:
            return asmdb.list_objects(self)
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_howto_build(self, target, feat):
        try:
            return asmdb.do_howto_build(self, target, feat)
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_build(self, target, feat, only_dep=None, rebuild=True, disable_ar2kut = False):
        try:
            return asmdb.do_build(self, target, feat, only_dep=only_dep, rebuild=rebuild)
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_save_fullpatch(self, feat):
        try:
            return asmdb.do_save_fullpatch(self, feat)
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_save_recent(self, feat):
        try:
            asmdb.do_save_recent(self, feat)
            # return self.do_build("final", feat)

        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_dump(self, feat, dest_file=None, exec_name=None):
        try:
            #asmdb.do_dump(self, feat)
            self.do_build("final", feat, rebuild=False)
            dumps.build_dump(self, feat, dest_file, exec_name)
            

        except Exception as e:
            self.exception(type(e).__name__, str(e))
    

    def do_save_auto(self, feat):
        try:
            obs_ = save_auto.ObserverAction(self, feat)
            return obs_.run()
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_test_deps(self, feat):
        try:
            return asmdb.test_deps(self, feat)
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_new(self, subfoldername=None, description=None, patchurl=None):
        try:
            return asmdb.do_new(self, subfoldername, description, patchurl)
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_copy_action(self, ext_name, folder):
        try:
            # 1 Comprobar si la carpeta es valida y existe
            # 2 Sacar depednencias de extensiones y módulos
            # 3 copiar.
            return copylib.do_copy_action(self, ext_name, folder)

        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def set_short_mode(self):
        self.short_mode = True
