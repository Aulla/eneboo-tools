from typing import Any, List
import os, sys
import xml.etree.ElementTree as ET


class Ar2Kut(object):
    root = None
    iface = None

    def __init__(self, iface):
        self.iface = iface

    def ar2kut(self, contenido: "str") -> "str":
        lineas = []
        self.root = ET.ElementTree(ET.fromstring(contenido)).findall(".//widget")
        lineas.append("<?xml version = '1.0' encoding = 'UTF-8'?>")
        lineas.append('<!DOCTYPE KugarTemplate SYSTEM "kugartemplate.dtd">')
        lineas.append(self.resuelve_template())
        lineas = lineas + self.resuelve_lineas()
        lineas.append("</KugarTemplate>")

        return "\n".join(lineas)

    def resuelve_lineas(self) -> List[str]:
        lineas = []
        section_height = None
        for nodo in self.root:
            linea = []
            nodo_name = nodo.get("class")
            if nodo_name in (
                "rpParamGroup",
                "rpDetailHeader",
                "rpAddOnHeader",
                "rpDetail",
                "repDetail",
                "rpDetailFooter",
                "rpAddOnFooter",
                "rpPageHeader",
                "rpPageFooter",
            ):
                if nodo_name == "rpDetailHeader":
                    linea.append("\n<DetailHeader")
                elif nodo_name == "rpAddOnHeader":
                    linea.append("\n<AddOnHeader")
                elif nodo_name in ("rpDetail", "repDetail"):
                    linea.append("\n<Detail")
                elif nodo_name == "rpDetailFooter":
                    linea.append("\n<DetailFooter")
                elif nodo_name == "rpAddOnFooter":
                    linea.append("\n<AddOnFooter")
                elif nodo_name == "rpPageHeader":
                    linea.append("\n<PageHeader")
                elif nodo_name == "rpPageFooter":
                    linea.append("\n<PageFooter")

            inner_detail = []
            for nodo2 in nodo:
                nodo2_name = nodo2.get("name")
                nodo2_class = nodo2.get("class")
                if nodo2_name in (
                    "Level",
                    "DrawIf",
                    "Rows",
                    "Cols",
                    "PlaceAtBottom",
                    "NewPage",
                    "PrintFrequency",
                ):
                    linea.append('%s="%s"' % (nodo2_name, nodo2[0].text))

                elif nodo2_name == "geometry":
                    for nodo3 in nodo2[0]:
                        nodo3_name = nodo3.tag
                        if nodo3_name == "height":
                            section_height = nodo3.text
                elif nodo2_name == "heightZero":
                    if nodo2[0].text == "true":
                        section_height = "0"

                if nodo2_class in ("rpField", "rpCalculatedField", "rpSpecial", "QLabel"):
                    bg_color_set = False
                    fg_color_set = False
                    xml_field = []

                    if nodo2_class == "rpField":
                        xml_field.append("<Field")
                    elif nodo2_class == "rpCalculatedField":
                        xml_field.append("<CalculatedField")
                    elif nodo2_class == "rpSpecial":
                        xml_field.append("<Special")
                    else:
                        xml_field.append("<Label")

                    for nodo3 in nodo2:
                        nodo3_name = nodo3.get("name")
                        if nodo3_name in ("name", "palette", "frameShadow", "autoFillBackground"):
                            continue
                        elif nodo3_name == "geometry":
                            for nodo4 in nodo3[0]:
                                nodo4_name = nodo4.tag
                                if nodo4_name == "x":
                                    xml_field.append('X="%s"' % nodo4.text)
                                elif nodo4_name == "y":
                                    xml_field.append('Y="%s"' % nodo4.text)
                                elif nodo4_name == "width":
                                    xml_field.append('Width="%s"' % nodo4.text)
                                elif nodo4_name == "height":
                                    xml_field.append('Height="%s"' % nodo4.text)
                        elif nodo3_name == "styleSheet":
                            estilos = nodo3.text.split(";")
                            for estilo in estilos:
                                if "background-color" in estilo:
                                    color = ""
                                    if "TRANSPARENT" in estilo:
                                        color = "NOCOLOR"
                                    else:
                                        color = estilo[
                                            estilo.index("(") : estilo.index(")")
                                        ].replace(" ", "")

                                    xml_field.append('BackgroundColor ="%s"' % color)
                                    bg_color_set = True
                                elif "border-color" in estilo:
                                    color = estilo[estilo.index("(") : estilo.index(")")].replace(
                                        " ", ""
                                    )

                                    xml_field.append('BorderColor ="%s"' % color)
                                    xml_field.append('BorderStyle ="1"')
                                    bg_color_set = True
                                elif "color" in estilo and estilo.index("color") < 2:
                                    color = estilo[estilo.index("(") : estilo.index(")")].replace(
                                        " ", ""
                                    )

                                    xml_field.append('ForegroundColor ="%s"' % color)
                                    fg_color_set = True
                        elif nodo3_name == "text":
                            xml_field.append('Text = "%s"' % nodo3[0].text)
                        elif nodo3_name in ("FunName", "FN"):
                            xml_field.append('FunctionName = "%s"' % nodo3[0].text)
                        elif nodo3_name == "wordWrap":
                            xml_field.append(
                                'WordWrap = "%s"' % ("1" if nodo3[0].text == "true" else "0")
                            )
                        elif nodo3_name == "alignment":
                            alignment_txt = nodo3[0].text
                            if "AlignCenter" in alignment_txt:
                                xml_field.append('HAlignment="1"')
                                xml_field.append('VAlignment="1"')
                            if "AlignHCenter" in alignment_txt:
                                xml_field.append('HAlignment="1"')
                            if "AlignLeft" in alignment_txt:
                                xml_field.append('HAlignment="0"')
                            if "AlignRight" in alignment_txt:
                                xml_field.append('HAlignment="2"')

                            if "AlignVCenter" in alignment_txt:
                                xml_field.append('VAlignment="1"')
                            if "AlignTop" in alignment_txt:
                                xml_field.append('VAlignment="0"')
                            if "AlignBottom" in alignment_txt:
                                xml_field.append('VAlignment="2"')
                        elif nodo3_name == "font":
                            lista_nodos = [nodo4 for nodo4 in nodo3[0]]
                            if not lista_nodos:
                                self.iface.warn(
                                    "Algunos de los campos del informe no tienen correctamente establecida la fuente (tipo de letra)"
                                )
                            for nodo4 in lista_nodos:
                                nodo4_name = nodo4.tag
                                if nodo4_name == "family":
                                    xml_field.append('FontFamily="%s"' % nodo4.text)
                                elif nodo4_name == "pointsize":
                                    xml_field.append('FontSize="%s"' % nodo4.text)
                                elif nodo4_name == "pointsize":
                                    xml_field.append('FontSize="%s"' % nodo4.text)
                                elif nodo4_name == "bold":
                                    xml_field.append(
                                        'FontWeight="%s"' % ("65" if nodo4.text == "true" else "50")
                                    )
                                elif nodo4_name == "italic" and nodo4.text in ("true", "1"):
                                    xml_field.append('FontItalic="1"')
                        else:
                            xml_field.append('%s = "%s"' % (nodo3.get("name"), nodo3[0].text))
                    if not bg_color_set:
                        xml_field.append('BackgroundColor="255,255,255"')
                    if not fg_color_set:
                        xml_field.append('ForegroundColor="0,0,0"')

                    xml_field.append("/>")
                    inner_detail.append(" ".join(xml_field))
                elif nodo2_class == "rpBox":
                    xml_field = ['<Line Style="1"']
                    x1 = None
                    x2 = None
                    y1 = None
                    y2 = None
                    color = "0,0,0"
                    line_width = "1"

                    for nodo3 in nodo2:
                        nodo3_name = nodo3.get("name")
                        if nodo3_name == "geometry":
                            for nodo4 in nodo3[0]:
                                nodo4_name = nodo4.tag
                                if nodo4_name == "x":
                                    x1 = float(nodo4.text)
                                elif nodo4_name == "y":
                                    y1 = float(nodo4.text)
                                elif nodo4_name == "width":
                                    x2 = x1 + float(nodo4.text) - 1
                                elif nodo4_name == "height":
                                    y2 = y1 + float(nodo4.text)
                        elif nodo3_name == "styleSheet":
                            estilos = nodo3.text.split(";")
                            for estilo in estilos:
                                if "color" in estilo and estilo.index("color") < 2:
                                    color = estilo[estilo.find("(") : estilo.find(")")].replace(
                                        " ", ""
                                    )
                        elif nodo3_name == "lineWidth":
                            line_width = nodo3[0].text

                    inner_detail.append(
                        '<Line Style="1" X1="%s" Y1="%s" X2="%s" Y2="%s" Color ="%s" Width="%s"/>'
                        % (x1, y1, x2, y1, color, line_width)
                    )
                    inner_detail.append(
                        '<Line Style="1" X1="%s" Y1="%s" X2="%s" Y2="%s" Color ="%s" Width="%s"/>'
                        % (x1, y2, x2, y2, color, line_width)
                    )
                    inner_detail.append(
                        '<Line Style="1" X1="%s" Y1="%s" X2="%s" Y2="%s" Color ="%s" Width="%s"/>'
                        % (x1, y1, x1, y2, color, line_width)
                    )
                    inner_detail.append(
                        '<Line Style="1" X1="%s" Y1="%s" X2="%s" Y2="%s" Color ="%s" Width="%s"/>'
                        % (x2, y1, x2, y2, color, line_width)
                    )
                elif nodo2_class == "Line":
                    xml_field = ['<Line Style="1"']
                    color_set = False
                    width_set = False
                    for nodo3 in nodo2:
                        nodo3_name = nodo3.get("name")
                        if nodo3_name == "geometry":
                            x1 = None
                            y1 = None
                            x2 = None
                            y2 = None
                            line_width = None
                            line_height = None

                            for nodo4 in nodo3[0]:
                                nodo4_name = nodo4.tag
                                if nodo4_name == "x":
                                    x1 = float(nodo4.text)
                                elif nodo4_name == "y":
                                    y1 = float(nodo4.text)
                                elif nodo4_name == "width":
                                    line_width = float(nodo4.text)
                                    line_width = (
                                        (line_width + 1) if line_width % 2 == 1 else line_width
                                    )
                                elif nodo4_name == "height":
                                    line_height = float(nodo4.text)
                                    line_height = (
                                        (line_height + 1) if line_height % 2 == 1 else line_height
                                    )

                            if line_width > line_height:
                                y1 += float(line_height / 2)
                                y2 = y1
                                x2 = float(x1 + line_width)
                            else:
                                x1 += float(line_width / 2)
                                x2 = x1
                                y2 = y1 + line_height

                            xml_field.append('X1="%s" X2="%s" Y1="%s" Y2="%s"' % (x1, x2, y1, y2))
                        elif nodo3_name == "styleSheet":
                            estilos = nodo3.text.split(";")
                            for estilo in estilos:
                                if "color" in estilo and estilo.find("color") < 2:
                                    color = estilo[estilo.find("(") : estilo.find(")")].replace(
                                        " ", ""
                                    )
                                    xml_field.append('Color = "%s"' % color)
                                    color_set = True
                        elif nodo3_name == "lineWidth":
                            xml_field.append('Width="%s"' % nodo3[0].text)
                            width_set = True

                    if not color_set:
                        xml_field.append('Color="0,0,0"')
                    if not width_set:
                        xml_field.append('Width="1"')

                    xml_field.append("/>")
                    inner_detail.append(" ".join(xml_field))

            if linea:
                linea.append('Height="%s"' % section_height)
            else:
                continue

            linea.append(">")

            if inner_detail:
                linea.append("\n%s" % ("\n".join(inner_detail)))

            if nodo_name == "rpDetailHeader":
                linea.append("\n</DetailHeader>")
            elif nodo_name == "rpAddOnHeader":
                linea.append("\n</AddOnHeader>")
            elif nodo_name in ("rpDetail", "repDetail"):
                linea.append("\n</Detail>")
            elif nodo_name == "rpDetailFooter":
                linea.append("\n</DetailFooter>")
            elif nodo_name == "rpAddOnFooter":
                linea.append("\n</AddOnFooter>")
            elif nodo_name == "rpPageHeader":
                linea.append("\n</PageHeader>")
            elif nodo_name == "rpPageFooter":
                linea.append("\n</PageFooter>")
            lineas.append(" ".join(linea))

        return lineas

    def resuelve_template(self):
        lista = ["<KugarTemplate"]
        for widget in self.root:
            if widget.get("class") == "rpParamGroup":
                for param_node in widget:
                    if param_node.get("class") == "rpParameter":
                        parametro = None
                        valor = None
                        for prop in param_node:
                            if prop.get("name") == "Parametro":
                                parametro = prop[0].text

                            if prop.get("name") == "Valor":
                                valor = prop[0].text

                        if not parametro is None and not valor is None:
                            lista.append('%s="%s"' % (parametro, valor))

        lista.append(">")

        return " ".join(lista)

    def ar2kutCarpeta(self, carpeta):
        comando: Any = "find %s -name *.ar -type f" % carpeta
        resComando: Any = self.ejecutarComando(comando)
        if not resComando["ok"]:
            self.iface.warn(
                "Error al buscar los ficheros ar: '%s'" % resComando["salida"].split("\n")
            )
            return False
        ficheros: Any = resComando["salida"].split("\n")

        for fichero in ficheros:
            self.ar2kutfichero(fichero)

        return carpeta

    def ar2kutfichero(self, fichero):
        if fichero:
            self.iface.debug("AR2KUT: ficheros .ar: %s" % fichero)
            nombre: str = fichero.split("/")[-1]
            nombreBase: str = nombre.split(".")[0]
            ruta: Any = fichero.split("/")[:-1]
            contenidoAR: str = self.read_file(fichero)
            contenidoKut: Any = self.ar2kut(contenidoAR)
            ruta_kut = ["/"] + ruta
            ruta_kut.append("%s.kut" % nombreBase)
            ficheroKut: Any = os.path.join(*ruta_kut)
            self.iface.debug("AR2KUT: fichero kut: %s" % ficheroKut)
            self.write_file(ficheroKut, contenidoKut)

    def read_file(self, file_name) -> str:
        self.iface.debug("AR2KUT: Leyendo %s" % file_name)
        content = ""
        file_ = open(file_name, "r", encoding="ISO-8859-15")
        content = file_.read()
        file_.close()

        return content

    def write_file(self, file_name, content):
        self.iface.info("AR2KUT: Escribiendo %s" % (file_name))
        file_ = open(file_name, "w", encoding="ISO-8859-15")
        content = file_.write(content)
        file_.close()

    def ejecutarComando(self, comando: str):
        import subprocess

        cmd = comando.split(" ")

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        o, e = proc.communicate()
        str_error = e.decode()
        str_output = o.decode()
        return {"ok": not str_error, "salida": str_output if not str_error else str_error}


if __name__ == "__main__":
    obj = Ar2Kut()
    ruta = sys.argv[1]
    print("*", ruta)
    obj.ar2kutCarpeta(ruta)
