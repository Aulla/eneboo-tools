
def main_assembler():
    from enebootools.assembler import config, AssemblerInterface

    iface = AssemblerInterface()

    if iface.parse_args():  # parsea los argumentos de entrada de consola
        # Si el parseo no devuelve error,
        iface.execute_actions()  # ejecuta las acciones detectadas.


def main_crypto():
    from enebootools.crypto import CryptoInterface

    iface = CryptoInterface()

    if iface.parse_args():  # parsea los argumentos de entrada de consola
        # Si el parseo no devuelve error,
        iface.execute_actions()  # ejecuta las acciones detectadas.


def main_merge_tool():
    from enebootools.mergetool import MergeToolInterface

    iface = MergeToolInterface()

    if iface.parse_args():  # parsea los argumentos de entrada de consola
        # Si el parseo no devuelve error,
        iface.execute_actions()  # ejecuta las acciones detectadas.


def main_packages():
    from enebootools.packager import PackagerInterface

    iface = PackagerInterface()

    if iface.parse_args():  # parsea los argumentos de entrada de consola
        # Si el parseo no devuelve error,
        iface.execute_actions()  # ejecuta las acciones detectadas.
        
def main_extract_tool():
    from enebootools.extracttool import ExtractToolInterface

    iface = ExtractToolInterface()

    if iface.parse_args():  # parsea los argumentos de entrada de consola
        # Si el parseo no devuelve error,
        iface.execute_actions()  # ejecuta las acciones detectadas.
