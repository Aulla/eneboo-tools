"""Dumps module."""

from typing import Optional, TYPE_CHECKING
from enebootools.assembler.kobjects import ObjectIndex
from enebootools.packager import pkgjoiner
import os

if TYPE_CHECKING:
    from enebootools import assembler

def build_dump(iface : 'assembler.AssemblerInterface', feat: str, dest_file: Optional[str] = None, exec_name: Optional[str] = None):
    """Builds a dump."""

    iface.info("Generando dump de: %s" % feat)
    oi = ObjectIndex(iface)
    oi.analyze_objects()
    build_instructions = oi.get_build_actions("final", feat, None)
    if build_instructions is None:
        iface.warn("No se pudo generar el dump")
        return False
    dest_path = os.path.join(build_instructions.get("path"), "build")
    src_dir = os.path.join(dest_path, "final")
    final_dir = os.path.dirname(dest_file) if dest_file else src_dir
    pkg_file = build_package(iface, feat, src_dir, final_dir)
    if not pkg_file:
        iface.warn("No se generó el package")
        return False
    
        
    if not run_command(iface, feat, pkg_file, exec_name):
        iface.warn("No se puedo ejecutar el comando")
        return False

    dst_file = dest_file if dest_file else os.path.join(dest_path, "%s.sqlite3" % feat)
    if not move_dump(iface, feat, dst_file):
        iface.warn("No se puedo mover el dump")
        return False

    iface.info("Dump generado en: %s" % dst_file)
    return True

def elimina_bd_previa(feat: str):
    home_folder = os.path.expanduser("~")
    src_file_utf8 = os.path.join(home_folder,".eneboocache", "UTF-8", "%s.s3db" % feat)
    src_file_iso = os.path.join(home_folder,".eneboocache", "ISO-8859-15", "%s.s3db" % feat)
    for fichero in [src_file_utf8, src_file_iso]:
        if os.path.exists(fichero):
            os.remove(fichero)


def build_package(iface : 'assembler.AssemblerInterface', feat: str, src_dir:str, final_dir: str):

    pkg_file = os.path.join(final_dir, "%s.eneboopkg" % feat)

    if os.path.exists(pkg_file):
        iface.warn("El dump ya existe, se borrará")
        iface.warn("Borrando %s" % pkg_file)
        
        os.remove(pkg_file)
    
    
    pkgjoiner.createpkg(iface, src_dir, pkg_file, False)

    if not os.path.exists(pkg_file):
        iface.warn("No se pudo crear el dump")
        return False
    
    return pkg_file


def run_command(iface, feat, pkg_file, exec_name: Optional[str] = None):
    """Runs the command."""
    exec_name = exec_name or "eneboo"
    elimina_bd_previa(feat)
    iface.debug("Usando ejecutable: %s" % exec_name)
    cmd = "%s -silentconn '%s.s3db:yeboyebo:SQLite3:nogui' -c 'sys.loadAbanQPackage' -a '%s:' -q" % (exec_name, feat, pkg_file)
    if os.system(cmd):
        iface.warn("No se pudo ejecutar el comando.Comprueba que eneboo está en el path")
        return False 

    return True

def move_dump(iface, feat, dst_file):
    """Moves the dump."""
    home_folder = os.path.expanduser("~")
    src_file_utf8 = os.path.join(home_folder,".eneboocache", "UTF-8", "%s.s3db" % feat)
    src_file_iso = os.path.join(home_folder,".eneboocache", "ISO-8859-15", "%s.s3db" % feat)
    
    src_file = None
    if os.path.isfile(src_file_utf8):
        src_file = src_file_utf8
    elif os.path.isfile(src_file_iso):
        src_file = src_file_iso
    
    if not src_file:
        iface.warn("No se pudo encontrar el dump de %s en %s" % (feat, src_file))
        return False
    
    if os.path.exists(dst_file):
        os.remove(dst_file)

    iface.debug("Moviendo %s a %s" % (src_file, dst_file))
    os.rename(src_file, dst_file)

    return True
    
    