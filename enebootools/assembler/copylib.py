# encoding: UTF-8

import os
import shutil
from enebootools.assembler import database as asmdb

def do_copy_action(iface, ext_name, dest_folder):
    if not check_if_folder_is_valid(dest_folder):
        return False
    
    if os.path.exists(dest_folder):
        shutil.rmtree(dest_folder)
        os.makedirs(dest_folder)

    features, modules = asmdb.deps(iface, ext_name)
    # Copiamos extensiones
    for feat in features:
        copy_dep_to_folder(iface, feat, dest_folder)
    for module in modules:
        copy_dep_to_folder(iface, module, dest_folder)
        
        
    
    return True

def copy_dep_to_folder(iface, feat, dest_folder):
    orig_folder, formal_feat, subfolder = resolve_main_folder(iface, feat)

    dest_folder = os.path.join(dest_folder, subfolder, formal_feat)
    if os.path.exists(dest_folder):
        shutil.rmtree(dest_folder)

    print("Copiando %s desde %s a %s" % (feat, orig_folder, dest_folder))
    shutil.copytree(orig_folder, dest_folder)

def check_if_folder_is_valid(dest_folder):
    if not os.path.exists(dest_folder):
        print("El directorio %s no existe" % dest_folder)
        return False
    if not os.path.isdir(dest_folder):
        print("%s no es un directorio" % dest_folder)
        return False
    return True

def resolve_main_folder(iface, feat):
    from enebootools.assembler.kobjects import ModuleObject, FeatureObject
    orig_folder = asmdb.dep_main_folder(iface, feat)
    obj = ModuleObject.find(feat) or FeatureObject.find(feat)
    formal = obj.formal_name() if obj else feat
    return [orig_folder, formal, str(orig_folder).replace("/%s" % formal, "").split("/")[-1]]
   
