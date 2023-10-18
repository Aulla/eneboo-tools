"""enebootools package."""
# encoding: UTF-8
import os
import os.path
import sys
import traceback
from pprint import pformat
import enebootools.parseargs as pa


__VERSION__ = "2.1.6"
QS_EXTEND_MODE = "legacy"


def ustr(value):
    """Ustr."""
    if isinstance(value, str):
        return value
    # if isinstance(x, str):
    #    return x.encode("UTF-8", "replace")
    return str(value)


def myprint(*args):
    """My print."""
    txt = " ".join(args) + "\n"
    try:
        sys.stdout.write(str(txt, "UTF-8", "replace"))
    except Exception:
        sys.stdout.write(txt)


class EnebooToolsInterface(object):
    """EnebooToolsInterface class."""

    module_description = "Descripción genérica"

    def __init__(self, setup_parser=True):
        """Initialice."""
        self.action_chain = None
        self.parser = None
        self.verbosity = 0
        self.output_file_name = "STDOUT"
        self.filename_list = []
        self.output = sys.stdout
        if setup_parser:
            self.setup_parser()

    def setup_parser(self):
        """Setup parser."""
        self.parser = pa.ArgParser(
            description=self.module_description,
        )
        self.parser.declare_option(
            name="output-file",
            aliases=["output"],  # sinonimos con los que llamar la opcion
            description="guarda la salida del programa en PATH",
            level="action",  # ( action | parser )
            variable="PATH",  # determina el nombre de la variable en la ayuda.
            # si es None, no hay variable. Esto fuerza también la sintaxis.
            call_function=self.set_output_file,
        )
        self.parser.declare_option(
            name="verbose",
            # opción corta relacionada (si se usa, no puede haber variable)
            short="vV",
            description="Aumenta la cantidad de mensajes",
            level="parser",  # ( action | parser )
            # variable = None  # es omisible, porque None es por defecto.
            call_function=self.set_verbose,
        )
        self.parser.declare_option(
            name="quiet",
            short="q",
            description="Disminuye la cantidad de mensajes",
            level="parser",
            call_function=self.set_quiet,
        )

    def parse_args(self, argv=None):
        """Parse args."""
        self.action_chain = self.parser.parse_args(argv)
        self.filename_list = self.parser.parse.files
        if self.action_chain is None:
            return False
        else:
            return True

    def execute_actions(self):
        """Execute action."""
        # Action chain es la cadena de llamadas. Es una lista que contiene:
        # [
        #  .. (function1_ptr ,  *args, **kwargs),
        #  .. (function2_ptr ,  *args, **kwargs),
        # ]
        # Se lanzan en orden.
        if self.action_chain is None:
            print("Hubo un error al leer los argumentos y no se puede realizar la acción.")
            return
        for function, args, kwargs in self.action_chain:
            if self.verbosity > 4:
                print("DEBUG:", function, args, kwargs)
            ret = function(*args, **kwargs)
            if ret:
                return ret

        self.action_chain = []

    def set_output_file(self, filename):
        """Set Oputput file."""
        self.output_file_name = filename
        self.output = open(filename, "wb", buffering=0)

    def set_verbose(self):
        """Set Verbose."""
        self.verbosity += 1

    def set_quiet(self):
        """Set quiet."""
        self.verbosity -= 1

    def debug2r(self, variable=None, **kwargs):
        """Debug2r."""
        if self.verbosity < 4:
            return

        if variable is not None:
            kwargs["var"] = variable
        print("DEBUG+", end=" ")
        for arg, var in sorted(kwargs.items()):
            prefix = ": %s =" % arg
            print(prefix, end=" ")
            try:
                lines = pformat(var).splitlines()
            except UnicodeEncodeError:
                lines = ["UNICODE ENCODE ERROR"]
            for num, line in enumerate(lines):
                if num > 0:
                    print(" " * (len(prefix) + 0), end=" ")
                print(line, end=" ")
                if num < len(lines) - 1:
                    print()
        print()

    def debug2(self, text):
        """Debug2."""
        if self.verbosity < 4:
            return
        text = ustr(text)
        myprint("DEBUG+:", text)

    def debug(self, text):
        """Debug."""
        if self.verbosity < 3:
            return
        text = ustr(text)
        myprint("DEBUG:", text)

    def info2(self, text):
        """Info2-"""
        if self.verbosity < 2:
            return
        text = ustr(text)
        myprint("INFO:", text)

    def info(self, text):
        """Info."""
        if self.verbosity < 1:
            return
        text = ustr(text)
        myprint(":", text)

    def msg(self, text):
        """Msg."""
        if self.verbosity < 0:
            return
        text = ustr(text)
        myprint(text)

    def warn(self, text):
        """Warn."""
        if self.verbosity < -1:
            return
        text = ustr(text)
        myprint("WARN:", text)

    def error(self, text):
        """Error."""
        if self.verbosity < -2:
            return
        text = ustr(text)
        myprint("ERROR:", text)

    def critical(self, text):
        """Critical."""
        if self.verbosity < -3:
            return
        text = ustr(text)
        myprint("CRITICAL:", text)

    def exception(self, errtype, text=""):
        """Exception."""
        if self.verbosity < -3:
            return
        text = ustr(text)
        txt_exc = traceback.format_exc()

        myprint("UNEXPECTED ERROR %s:" % errtype, text)
        myprint(txt_exc)


# **** CONFIGURACION *****

USER_HOME = os.path.expanduser("~")
CONF_DIR = os.path.join(USER_HOME, ".eneboo-tools")

if not os.path.exists(CONF_DIR):
    os.mkdir(CONF_DIR)
