# encoding: UTF-8
import enebootools
from enebootools import EnebooToolsInterface
import traceback
from . import extractfunctions


from enebootools.mergetool import flpatchqs, flpatchpy, flpatchtest, flpatchmodel, flpatchxml, flpatchlxml, flpatchdir, projectbuilder

"""
    El receptor de las llamadas del parser es una clase. Cada opción
    activada, genera una llamada en una función de la clase y así va 
    configurando la clase con cada llamada consecutiva.
    
    Esta clase está a nivel de módulo (extracttool) y es la interfaz
    de conexión de un módulo a otro.
    
    Una opción --output-file generara una llamada a una función miembro 
    "self.set_output_file(value)", donde "value" sería el valor recibido por
    la opción. 
    
    En el caso de que la opción no lleve valor, se ejecuta la función sin 
    argumentos.
    
    Las opciones cortas se configuran unicamente como alias de opciones 
    largas, de ese modo aprovechamos la configuración de unas cosas para otras.
    Y además, forzamos a que toda opción corta tenga su correspondiente opción 
    larga.
    
    Las acciones serán ejecutadas al final, y se les pasará los parámetros
    indicados con kwargs, de modo que el orden de los parámetros en la función
    es irrelevante, pero deben contar con el mismo nombre. 

    Las listas de ficheros se inicializan en el primer paso recibiendo el 
    array de ficheros, probablemente con una llamada a set_file_list.

    La ejecución de las acciones es prearada en el parse() pero no se ejecutan
    hasta la llamada de una segunda funcion execute_actions() para evitar 
    sobrecargar la pila de llamadas (y que cuando se lance un traceback sea 
    lo más sencillo posible).
    
    NOTAS: 
     * Los parámetros pueden llegar a ser omisibles?
        en tal caso o se omiten los últimos o tiene que poder darles nombre 
        o tiene que haber un argumento de exclusión como "-".
        
     * Múltiples acciones realizadas por ejecución?
        Si los parámetros de la acción se consumen se podría entender que se 
        inicia otra acción o concatenar mediante un separador. Esto generaría 
        problemas y es posible que no sea práctico para ningún caso. Es 
        posible reciclar opciones y parámetros de llamada entre acciones?
        ... de momento se provee de una interfaz interna para esto, pero no se
        va a usar.
    
     * Habrá que agregar un control de excepciones en las llamadas de cada 
        función, para intentar buscar errores en la propia llamada (funcion no 
        existe, argumentos no válidos... etc)
    
"""


class ExtractToolInterface(EnebooToolsInterface):
    module_description = "Herramientas para la ayuda de extración de clases de una mezcla"

    def __init__(self, setup_parser=True):
        EnebooToolsInterface.__init__(self, False)
        self.patch_qs_rewrite = "warn"
        self.patch_py_rewrite = "warn"
        self.patch_test_rewrite = "warn"
        self.patch_model_rewrite = "warn"
        self.patch_xml_style_name = "legacy1"
        self.patch_qs_style_name = "legacy"
        self.patch_py_style_name = "legacy"
        self.patch_test_style_name = "legacy"
        self.patch_model_style_name = "legacy"
        self.diff_xml_search_move = False
        self.patch_name = None
        self.patch_dest = None
        self.clean_patch = False
        self.build_xml = False
        if setup_parser:
            self.setup_parser()

    def setup_parser(self):
        EnebooToolsInterface.setup_parser(self)
        self.parser.declare_option(
            name="patch-qs-rewrite",
            description="indica si al aplicar un parche de QS se debe sobreescribir o no las clases existentes ( reverse / predelete / yes / warn / no / abort ) ",
            level="action",
            variable="VALUE",
            call_function=self.set_patch_qs_rewrite
        )
        self.parser.declare_option(
            name="patch-py-rewrite",
            description="indica si al aplicar un parche de PY se debe sobreescribir o no las clases existentes ( reverse / predelete / yes / warn / no / abort ) ",
            level="action",
            variable="VALUE",
            call_function=self.set_patch_py_rewrite
        )
        self.parser.declare_option(
            name="patch-test-rewrite",
            description="indica si al aplicar un parche de PY_test se debe sobreescribir o no las clases existentes ( reverse / predelete / yes / warn / no / abort ) ",
            level="action",
            variable="VALUE",
            call_function=self.set_patch_test_rewrite
        )
        self.parser.declare_option(
            name="patch-model-rewrite",
            description="indica si al aplicar un parche de PY_model se debe sobreescribir o no las clases existentes ( reverse / predelete / yes / warn / no / abort ) ",
            level="action",
            variable="VALUE",
            call_function=self.set_patch_model_rewrite
        )
        self.parser.declare_option(
            name="patch-name",
            description="Indica el nombre del parche que se usará en lugar de autodetectarlo.",
            level="action",
            variable="NAME",
            call_function=self.set_patch_name
        )
        self.parser.declare_option(
            name="patch-dest",
            description="Donde guardar un fichero de parche",
            level="action",
            variable="FILENAME",
            call_function=self.set_patch_dest
        )
        self.parser.declare_option(
            name="enable-diff-xml-search-move",
            description="Activa la búsqueda de movimientos de bloques XML. Puede ser un poco más lento y puede generar parches incompatibles con otras herramientas.",
            level="action",
            call_function=self.enable_diff_xml_search_move
        )
        self.parser.declare_option(
            name="patch-xml-style",
            description="Usar otro estilo para generar parches XML (ver mergetools/etc/patch-styles/)",
            variable="NAME",
            level="action",
            call_function=self.set_patch_xml_style
        )
        self.parser.declare_option(
            name="patch-qs-style",
            description="Usar otro estilo para generar parches QS (legacy|qsdir)",
            variable="NAME",
            level="action",
            call_function=self.set_patch_qs_style
        )
        self.parser.declare_option(
            name="patch-py-style",
            description="Usar otro estilo para generar parches PY (legacy|pydir)",
            variable="NAME",
            level="action",
            call_function=self.set_patch_py_style
        )
        self.parser.declare_option(
            name="patch-test-style",
            description="Usar otro estilo para generar parches PY_test (legacy|testdir)",
            variable="NAME",
            level="action",
            call_function=self.set_patch_test_style
        )
        self.parser.declare_option(
            name="patch-model-style",
            description="Usar otro estilo para generar parches PY_model (legacy|modeldir)",
            variable="NAME",
            level="action",
            call_function=self.set_patch_model_style
        )
        self.parser.declare_option(
            name="clean-patch",
            description="provoca que el parche generado sea de tipo limpieza",
            level="action",  # ( action | parser )
            variable=None,
            call_function=self.set_clean_patch
        )

        self.extract_action = self.parser.declare_action(
            name="extract",
            args=["source", "final", "class_list", "mode"],
            description="Extrae de $source a $final las clases indicadas en $class_list",
            options=["build_xml"],
            call_function=self.do_extract,
        )

        self.extract_action.set_help_arg(
            source="Carpeta que contine el proyecto",
            final="Carpeta donde se guardarán los cambios",
            mode="Objetos a extraer (all|qs|ui|mtd|qry|xml)",
            class_list="Lista de clases a extraer, separadas por coma y sin espacios: class1,class2,...",
        )

        self.parser.declare_option(
            name="build_xml",
            description="Genera el xml con los ficheros extraidos",
            level="action",
            variable=None,
            call_function=self.set_build_xml
        )

    def set_patch_name(self, name):
        if name == "":
            name = None
        self.patch_name = name

    def set_patch_dest(self, filename):
        if filename == "":
            filename = None
        self.patch_dest = filename

    def set_patch_xml_style(self, name):
        self.patch_xml_style_name = name

    def set_patch_qs_style(self, name):
        self.patch_qs_style_name = name

    def set_patch_qs_rewrite(self, value):
        if value not in ['reverse', 'predelete', 'yes', 'no', 'warn', 'abort']:
            raise ValueError
        self.patch_qs_rewrite = value

    def set_patch_py_style(self, name):
        self.patch_py_style_name = name

    def set_patch_test_style(self, name):
        self.patch_test_style_name = name

    def set_patch_model_style(self, name):
        self.patch_model_style_name = name

    def set_patch_py_rewrite(self, value):
        if value not in ['reverse', 'predelete', 'yes', 'no', 'warn', 'abort']:
            raise ValueError
        self.patch_py_rewrite = value

    def set_patch_test_rewrite(self, value):
        if value not in ['reverse', 'predelete', 'yes', 'no', 'warn', 'abort']:
            raise ValueError
        self.patch_test_rewrite = value

    def set_patch_model_rewrite(self, value):
        if value not in ['reverse', 'predelete', 'yes', 'no', 'warn', 'abort']:
            raise ValueError
        self.patch_model_rewrite = value

    def enable_diff_xml_search_move(self):
        self.diff_xml_search_move = True

    def set_clean_patch(self):
        self.clean_patch = True

    def set_build_xml(self):
        self.build_xml = True

    # :::: ACTIONS ::::

    def do_extract(self, source, final, class_list, mode):
        try:
            mode = str(mode).lower()
            found = False
            class_array = class_list.split(",")
            if mode in ['qs', 'all']:
                found = True
                extractfunctions.extract_qs(self, source, final, class_array)

            if mode in ['ui', 'all']:
                found = True

            if mode in ['mtd', 'all']:
                found = True

            if mode in ['qry', 'all']:
                found = True

            if mode in ['xml', 'all']:
                found = True

            if not found:
                print("Unknown $mode %s" % (repr(mode)))
        except Exception as e:
            self.exception(type(e).__name__, str(e))
