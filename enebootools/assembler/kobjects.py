# encoding: UTF-8
import os

from lxml import etree

from enebootools.lib.utils import one, find_files, get_max_mtime, read_file_list

from .featureconfig import loadFeatureConfig
from .databasemodels import KnownObjects


class BaseObject(object):
    _by_name = {}
    _by_relpath = {}
    _by_formal_name = {}
    _by_abspath = {}

    def __init__(self, iface, obj):
        self.iface = iface
        self.obj = obj
        self.info = {}
        self.all_required_modules = None
        self.all_required_features = None
        self.fullpath = os.path.join(obj.abspath, obj.relpath)
        self.fullfilename = os.path.join(obj.abspath, obj.relpath, obj.filename)
        try:
            self.setup()
        except Exception:
            iface.error(
                "Error al intentar leer y configurar el objeto de base de datos. Se estaba configurando un objeto tipo <%s> y se solicitó el fichero '%s'"
                % (self.__class__.__name__, self.fullfilename)
            )
            raise

        self.__class__._by_name[(self.__class__.__name__, str(self.name))] = self
        self.__class__._by_relpath[(self.__class__.__name__, str(obj.relpath))] = self
        self.__class__._by_formal_name[(self.__class__.__name__, self.formal_name())] = self

        self.__class__._by_abspath[
            (self.__class__.__name__, str(obj.abspath), self.formal_name())
        ] = self

    def get_info(self):
        self.info = {"provides": [], "requires": []}
        return self.info

    def formal_name(self):
        return str(self.obj.relpath)

    @classmethod
    def by_name(self, name):
        result = self._by_name.get((self.__name__, str(name)), None)
        return result

    @classmethod
    def by_formal_name(self, name):
        result = self._by_formal_name.get((self.__name__, str(name)), None)
        return result

    @classmethod
    def by_relpath(self, relpath):
        result = self._by_relpath.get((self.__name__, str(relpath)), None)
        return result

    @classmethod
    def by_abspath(self, relpath):
        result = None
        if "2.4.0" in relpath or "modulos_" in relpath:
            for num, key in enumerate(
                [item for item in self._by_abspath if item[0] == self.__name__]
            ):
                obj = self._by_abspath[key]
                if str(obj.fullpath).endswith("/%s" % relpath):
                    result = obj
                    break
            result = [
                value
                for key, value in self._by_abspath.items()
                if key[0] == self.__name__ and value.fullpath.endswith("/%s" % relpath)
            ]
        return result[0] if result else None

    @classmethod
    def items(self):
        return [v for k, v in list(self._by_name.items()) if k[0] == self.__name__]

    @classmethod
    def find(self, name):
        return (
            self.by_abspath(name)
            or self.by_formal_name(name)
            or self.by_name(name)
            or self.by_relpath(name)
        )

    def setup(self):
        pass

    @classmethod
    def cls_finish_setup(self):
        for k, obj in list(self._by_name.items()):
            cname, name = k
            if cname != self.__name__:
                continue
            obj.finish_setup()

    def _get_full_required_modules(self):
        import enebootools

        modo = enebootools.QS_EXTEND_MODE

        if self.all_required_modules and modo != "yeboyebo":
            return self.all_required_modules

        req = []
        myreq = []

        for modname in self.required_modules:
            obj = ModuleObject.find(modname)
            if obj is None:
                self.iface.info(
                    "Modulo con nombre %s no encontrado (requerido por %s )"
                    % (modname, self.formal_name())
                )
                continue

            new_reqs = []
            if modo == "yeboyebo":
                if obj.type == "mod":
                    for module_def in obj.required_modules:
                        obj2 = ModuleObject.find(module_def)
                        formal_name = obj2.formal_name()
                        if not [
                            mod_name
                            for mod_name in self.required_modules
                            if mod_name.endswith(formal_name)
                        ]:
                            if not formal_name in new_reqs:
                                new_reqs.append(formal_name)
            else:
                new_reqs = [
                    modulename
                    for modulename in obj._get_full_required_modules()
                    if modulename not in req
                ]
                if self.type == "prj":
                    for n in new_reqs:
                        if n in self.required_modules:
                            continue
                        self.iface.debug(
                            "Proyecto %s, se agrega modulo %s solicitado por %s"
                            % (self.formal_name(), n, modname)
                        )

            req += new_reqs
            myreq.append(modname)
        if modo == "yeboyebo":
            req += myreq
        else:
            self.all_required_features = self._get_full_required_features()

            for featname in self.all_required_features:
                obj = FeatureObject.find(featname)
                if obj is None:
                    self.iface.info(
                        "Funcionalidad con nombre %s no encontrada (requerida por %s )"
                        % (featname, self.formal_name())
                    )
                    continue

                new_reqs = [
                    modulename
                    for modulename in obj._get_full_required_modules()
                    if modulename not in req and modulename not in myreq
                ]
                if self.type == "prj":
                    for n in new_reqs:
                        if n in self.required_modules:
                            continue
                        self.iface.debug(
                            "Proyecto %s, se agrega modulo %s solicitado por funcionalidad %s"
                            % (self.formal_name(), n, featname)
                        )

                req += new_reqs

            req += [modulename for modulename in myreq if modulename not in req]
            new_list = []

            for module_name in req:
                if (
                    "/" not in module_name
                ):  # esto filtra dependencias que son añadidas por código de módulo, para evitar que introduzca módulos con versiones incorrectas
                    module_obj = ModuleObject.find(module_name)
                    formal_name = module_obj.formal_name()
                    if formal_name in [
                        formal_name for req_item in req if str(req_item).endswith(formal_name)
                    ]:
                        continue

                new_list.append(module_name)
            req += new_list
        self.all_required_modules = req
        return req

    def _get_full_required_features(self):
        if self.all_required_features:
            return self.all_required_features
        req = []
        myreq = []

        for featname in self.required_features:
            obj = FeatureObject.find(featname)
            if obj is None:
                self.iface.info(
                    "Funcionalidad con nombre %s no encontrada (requerida por %s )"
                    % (featname, self.formal_name())
                )
                continue

            new_reqs = []
            for featurename in obj._get_full_required_features():
                if featurename not in req and "24_%s" % featurename not in req:
                    new_reqs.append(featurename)
            if self.type == "prj":
                for n in new_reqs:
                    self.iface.debug(
                        "Proyecto %s, se agrega funcionalidad %s solicitada por %s"
                        % (self.formal_name(), n, featname)
                    )
            req += new_reqs
            # req += new_reqs
            if obj.formal_name() not in req:
                req.append(obj.formal_name())
        # req += [ featurename for featurename in myreq if featurename not in req ]
        self.all_required_features = req
        return req

    def finish_setup(self):
        self._get_full_required_features()
        self._get_full_required_modules()


class ModuleObject(BaseObject):
    def setup(self):
        self.encoding = "ISO-8859-15"
        self.parser = etree.XMLParser(
            ns_clean=False,
            encoding=self.encoding,
            recover=True,  # .. recover funciona y parsea cuasi cualquier cosa.
            remove_blank_text=True,
        )
        self.tree = etree.parse(self.fullfilename, self.parser)
        self.root = self.tree.getroot()

        self.code = None
        self.name = one(self.root.xpath("name/text()"))
        self.description = one(self.root.xpath("description/text()"))
        self.type = "mod"
        self.module_area = one(self.root.xpath("area/text()"))
        self.module_areaname = one(self.root.xpath("areaname/text()"))
        self.required_modules = self.root.xpath("dependencies/dependency/text()")
        self.required_features = []
        self.iface.debug2("Se ha parseado el módulo %s" % self.name)

    def get_info(self):
        if self.info:
            return self.info
        self.info = {
            "provides": [
                os.path.normpath(os.path.join(self.obj.relpath, x))
                for x in find_files(self.fullpath)
            ],
            "requires": [],
        }

        return self.info


class FeatureObject(BaseObject):
    def setup(self):
        cfg = loadFeatureConfig(self.fullfilename)
        self.cfg = cfg
        self.name = cfg.feature.name
        self.code = cfg.feature.code
        self.description = cfg.feature.description
        self.type = cfg.feature.type
        self.dstfolder = None

        self.required_modules = read_file_list(
            self.fullpath, "conf/required_modules", errlog=self.iface.warn
        )
        self.required_features = read_file_list(
            self.fullpath, "conf/required_features", errlog=self.iface.warn
        )

        self.qs_extend_mode = cfg.feature.qs_extend_mode

        self.patch_series = read_file_list(
            self.fullpath, "conf/patch_series", errlog=self.iface.warn
        )

        self.iface.debug2("Se ha parseado la funcionalidad %s" % self.name)

    def get_patch_list(self):
        patch_list = read_file_list(self.fullpath, "conf/patch_series", errlog=self.iface.warn)
        return patch_list

    def set_patch_list(self, patchlist):
        f1 = open(os.path.join(self.fullpath, "conf/patch_series"), "w")
        for patch in patchlist:
            f1.write(patch + "\n")

    def set_dstfolder(self, folder):
        self.dstfolder = folder

    def get_info(self):
        from enebootools.mergetool.flpatchdir import FolderApplyPatch

        if self.info:
            return self.info
        patch_list = self.get_patch_list()
        self.info = {"provides": [], "requires": []}

        for patchdir in patch_list:
            srcpath = os.path.join(self.fullpath, "patches", patchdir)
            fpatch = FolderApplyPatch(self.iface, srcpath)
            info = fpatch.get_patch_info()
            self.info["provides"] += info["provides"]
            self.info["requires"] += info["requires"]
        return self.info

    # * base: compila las dependencias del proyecto (todo lo que necesitamos
    #         para poder aplicar los parches luego)
    def get_base_actions(self):
        dst_folder = os.path.join(self.fullpath, "build/base")
        binstr = etree.Element("BuildInstructions")
        binstr.set("feature", self.formal_name())
        binstr.set("target", "base")
        binstr.set("path", self.fullpath)
        binstr.set("dstfolder", "build/base")
        if self.dstfolder:
            binstr.set("dstfolder", self.dstfolder)
        etree.SubElement(binstr, "Message", text="Copiando módulos . . .")

        lista_modulos = self._get_full_required_modules()
        self.iface.debug("Módulos usando en base: %s" % lista_modulos)
        for modulename in lista_modulos:
            module = ModuleObject.find(modulename)
            if not module:
                self.iface.warn("No encontramos el módulo %s" % modulename)

            cpfolder = etree.SubElement(binstr, "CopyFolderAction")
            cpfolder.set("src", module.fullpath)
            cpfolder.set("dst", module.obj.relpath)
            cpfolder.set("create_dst", "yes")

        for featurename in self._get_full_required_features():
            feature = FeatureObject.find(featurename)
            patch_list = feature.get_patch_list()
            if len(patch_list) == 0:
                self.iface.warn("No encontramos parches para aplicar en %s" % featurename)
            etree.SubElement(binstr, "Message", text="Aplicando extensión %s . . ." % featurename)
            for patchdir in patch_list:
                apatch = etree.SubElement(binstr, "ApplyPatchAction")
                srcpath = os.path.join(feature.fullpath, "patches", patchdir)
                if not os.path.exists(srcpath):
                    self.iface.warn("La ruta %s no existe." % srcpath)

                apatch.set("src", srcpath)

        return binstr

    # * final: todo lo que lleva base, mas los parches que existen para este
    #          proyecto. (esto es lo que se envía al cliente)
    def get_final_actions(self):
        dst_folder = os.path.join(self.fullpath, "build/final")
        dep_folder = os.path.join(self.fullpath, "build/base")
        binstr = etree.Element("BuildInstructions")
        binstr.set("feature", self.formal_name())
        binstr.set("target", "final")
        binstr.set("depends", "base")
        binstr.set("path", self.fullpath)
        binstr.set("dstfolder", "build/final")
        if self.dstfolder:
            binstr.set("dstfolder", self.dstfolder)

        lista_modulos = self._get_full_required_modules()

        for modulename in lista_modulos:
            module = ModuleObject.find(modulename)
            cpfolder = etree.SubElement(binstr, "CopyFolderAction")
            cpfolder.set("src", os.path.join(dep_folder, module.obj.relpath))
            cpfolder.set("dst", module.obj.relpath)
            cpfolder.set("create_dst", "yes")

        featurename = self.formal_name()
        feature = self
        patch_list = feature.get_patch_list()
        if len(patch_list) == 0:
            self.iface.debug("No hay parches para aplicar en %s" % featurename)
        for patchdir in patch_list:
            apatch = etree.SubElement(binstr, "ApplyPatchAction")
            srcpath = os.path.join(feature.fullpath, "patches", patchdir)
            if not os.path.exists(srcpath):
                self.iface.warn("La ruta %s no existe." % srcpath)

            apatch.set("src", srcpath)

        return binstr

    # * src: una copia del target final, donde realizar los
    #        cambios a la extensión
    def get_src_actions(self):
        dst_folder = os.path.join(self.fullpath, "build/src")
        dep_folder = os.path.join(self.fullpath, "build/final")
        binstr = etree.Element("BuildInstructions")
        binstr.set("feature", self.formal_name())
        binstr.set("target", "src")
        binstr.set("depends", "final")
        binstr.set("path", self.fullpath)
        binstr.set("dstfolder", "build/src")
        if self.dstfolder:
            binstr.set("dstfolder", self.dstfolder)
        for modulename in self._get_full_required_modules():
            module = ModuleObject.find(modulename)
            cpfolder = etree.SubElement(binstr, "CopyFolderAction")
            cpfolder.set("src", os.path.join(dep_folder, module.obj.relpath))
            cpfolder.set("dst", module.obj.relpath)
            cpfolder.set("create_dst", "yes")

        return binstr

    # * patch: calcula el parche de las diferencias entre src y final.
    def get_patch_actions(self):
        dst_folder = os.path.join(self.fullpath, "build/patch")
        dep1_folder = os.path.join(self.fullpath, "build/final")
        dep2_folder = os.path.join(self.fullpath, "build/src")
        binstr = etree.Element("BuildInstructions")
        binstr.set("feature", self.formal_name())
        binstr.set("target", "src")
        binstr.set("depends", "final src")
        binstr.set("path", self.fullpath)
        binstr.set("dstfolder", "build/patch")
        if self.dstfolder:
            binstr.set("dstfolder", self.dstfolder)

        cpatch = etree.SubElement(binstr, "CreatePatchAction")
        cpatch.set("src", dep1_folder)
        cpatch.set("dst", dep2_folder)

        return binstr

    # * test-patch: el resultado de aplicar el parche "patch" sobre "final", sirve
    #         para realizar las pruebas convenientes antes de guardar
    #         el nuevo parche
    def get_testpatch_actions(self):
        dst_folder = os.path.join(self.fullpath, "build/test")
        dep1_folder = os.path.join(self.fullpath, "build/final")
        dep2_folder = os.path.join(self.fullpath, "build/patch")
        binstr = etree.Element("BuildInstructions")
        binstr.set("feature", self.formal_name())
        binstr.set("target", "test")
        binstr.set("depends", "final patch")
        binstr.set("path", self.fullpath)
        binstr.set("dstfolder", "build/test-patch")
        if self.dstfolder:
            binstr.set("dstfolder", self.dstfolder)

        for modulename in self.all_required_modules:
            module = ModuleObject.find(modulename)
            cpfolder = etree.SubElement(binstr, "CopyFolderAction")
            cpfolder.set("src", os.path.join(dep1_folder, module.obj.relpath))
            cpfolder.set("dst", module.obj.relpath)
            cpfolder.set("create_dst", "yes")

        apatch = etree.SubElement(binstr, "ApplyPatchAction")
        apatch.set("src", dep2_folder)

        return binstr

    # * fullpatch: calcula el parche de las diferencias entre src y base.
    def get_fullpatch_actions(self):
        dst_folder = os.path.join(self.fullpath, "build/patch")
        dep1_folder = os.path.join(self.fullpath, "build/base")
        dep2_folder = os.path.join(self.fullpath, "build/src")
        binstr = etree.Element("BuildInstructions")
        binstr.set("feature", self.formal_name())
        binstr.set("target", "src")
        binstr.set("depends", "base src")
        binstr.set("path", self.fullpath)
        binstr.set("dstfolder", "build/fullpatch")
        if self.dstfolder:
            binstr.set("dstfolder", self.dstfolder)

        cpatch = etree.SubElement(binstr, "CreatePatchAction")
        cpatch.set("src", dep1_folder)
        cpatch.set("dst", dep2_folder)

        return binstr

    # * fullpatch: calcula el parche de las diferencias entre src y final (los últimos cambios).
    def get_updatepatch_actions(self):
        dst_folder = os.path.join(self.fullpath, "build/patch")
        dep1_folder = os.path.join(self.fullpath, "build/final")
        dep2_folder = os.path.join(self.fullpath, "build/src")
        binstr = etree.Element("BuildInstructions")
        binstr.set("feature", self.formal_name())
        binstr.set("target", "src")
        binstr.set("depends", "base src")
        binstr.set("path", self.fullpath)
        binstr.set("dstfolder", "build/fullpatch")
        if self.dstfolder:
            binstr.set("dstfolder", self.dstfolder)

        cpatch = etree.SubElement(binstr, "UpdatePatchAction")
        cpatch.set("src", dep1_folder)
        cpatch.set("dst", dep2_folder)

        return binstr

    # * revfullpatch: calcula el parche inverso de las diferencias entre src y base.
    def get_revfullpatch_actions(self):
        dst_folder = os.path.join(self.fullpath, "build/patch")
        dep1_folder = os.path.join(self.fullpath, "build/base")
        dep2_folder = os.path.join(self.fullpath, "build/src")
        binstr = etree.Element("BuildInstructions")
        binstr.set("feature", self.formal_name())
        binstr.set("target", "src")
        binstr.set("depends", "base src")
        binstr.set("path", self.fullpath)
        binstr.set("dstfolder", "build/revfullpatch")
        if self.dstfolder:
            binstr.set("dstfolder", self.dstfolder)

        cpatch = etree.SubElement(binstr, "CreatePatchAction")
        cpatch.set("dst", dep1_folder)
        cpatch.set("src", dep2_folder)

        return binstr

    # * test-fullpatch: el resultado de aplicar el parche "patch" sobre "base", sirve
    #         para realizar las pruebas convenientes antes de guardar
    #         el nuevo parche
    def get_testfullpatch_actions(self):
        dst_folder = os.path.join(self.fullpath, "build/test")
        dep1_folder = os.path.join(self.fullpath, "build/base")
        dep2_folder = os.path.join(self.fullpath, "build/fullpatch")
        binstr = etree.Element("BuildInstructions")
        binstr.set("feature", self.formal_name())
        binstr.set("target", "test")
        binstr.set("depends", "base fullpatch")
        binstr.set("path", self.fullpath)
        binstr.set("dstfolder", "build/test-fullpatch")
        if self.dstfolder:
            binstr.set("dstfolder", self.dstfolder)

        for modulename in self.all_required_modules:
            module = ModuleObject.find(modulename)
            cpfolder = etree.SubElement(binstr, "CopyFolderAction")
            cpfolder.set("src", os.path.join(dep1_folder, module.obj.relpath))
            cpfolder.set("dst", module.obj.relpath)
            cpfolder.set("create_dst", "yes")

        apatch = etree.SubElement(binstr, "ApplyPatchAction")
        apatch.set("src", dep2_folder)

        return binstr


class Singleton(type):
    def __init__(cls, name, bases, dct):
        cls.__instance = None
        type.__init__(cls, name, bases, dct)

    def __call__(cls, *args, **kw):
        if cls.__instance is None:
            cls.__instance = type.__call__(cls, *args, **kw)
        return cls.__instance


class ObjectIndex(object, metaclass=Singleton):
    def __init__(self, iface):
        self.iface = iface
        self.analyze_done = False
        self.file_index = None

    def analyze_objects(self):
        if self.analyze_done:
            return True
        for kobj in KnownObjects.select():
            if kobj.objtype == "module":
                self.load_module(kobj)
            elif kobj.objtype == "feature":
                self.load_feature(kobj)
            else:
                self.iface.warn("Unknown object type %s" % kobj.objtype)
                self.iface.warn(kobj.format())
        ModuleObject.cls_finish_setup()
        FeatureObject.cls_finish_setup()
        self.analyze_done = True

    def index_by_file(self):
        if not self.analyze_done:
            self.analyze_objects()
        if self.file_index:
            return self.file_index
        self.file_index = {}

        for kobj in list(ModuleObject.items()) + list(FeatureObject.items()):
            index = kobj.get_info()
            fname = "%s" % (kobj.formal_name())
            ftype = "module" if kobj.type == "mod" else "feature"

            def declare_filename(filename):
                if filename in self.file_index:
                    return
                self.file_index[filename] = {
                    "provided-by-module": [],
                    "provided-by-feature": [],
                    "required-by-module": [],
                    "required-by-feature": [],
                }

            for filename in index["provides"]:
                declare_filename(filename)
                self.file_index[filename]["provided-by-" + ftype].append(fname)

            for filename in index["requires"]:
                declare_filename(filename)
                self.file_index[filename]["required-by-" + ftype].append(fname)

        return self.file_index

    def load_module(self, obj):
        mod = ModuleObject(self.iface, obj)

    def load_feature(self, obj):
        ftr = FeatureObject(self.iface, obj)

    def modules(self):
        return list(ModuleObject.items())

    def features(self):
        return list(FeatureObject.items())

    def get_patch_name(self, func, default=False):
        feature = FeatureObject.find(func)
        if not feature:
            self.iface.error("Funcionalidad %s desconocida." % func)
            return None
        patch_list = feature.get_patch_list()
        if len(patch_list) == 0:
            if default:
                return feature.name
            else:
                return None
        return patch_list[0]

    def set_patch_name(self, func, newname):
        feature = FeatureObject.find(func)
        if not feature:
            self.iface.error("Funcionalidad %s desconocida." % func)
            return None
        feature.set_patch_list([newname])

    def get_build_actions(self, target, func, dstfolder=None):
        import enebootools

        feature = FeatureObject.find(func)

        if not feature:
            self.iface.error("Funcionalidad %s desconocida." % func)
            return None

        enebootools.QS_EXTEND_MODE = feature.qs_extend_mode

        feature.set_dstfolder(dstfolder)

        if target == "base":
            return feature.get_base_actions()

        if target == "final":
            return feature.get_final_actions()

        if target == "src":
            return feature.get_src_actions()

        if target == "patch":
            return feature.get_patch_actions()

        if target == "test-patch":
            return feature.get_testpatch_actions()

        if target == "fullpatch":
            return feature.get_fullpatch_actions()

        if target == "revfullpatch":
            return feature.get_revfullpatch_actions()

        if target == "test-fullpatch":
            return feature.get_testfullpatch_actions()

        if target == "updatepatch":
            return feature.get_updatepatch_actions()

        self.iface.error("Target %s desconocido." % target)
        return None
