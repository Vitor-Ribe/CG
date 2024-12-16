import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as et
from xml.dom import minidom


class Visualizador:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Objetos 2D")

        menu = tk.Menu(root)
        root.config(menu=menu)
        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Abrir", command=self.abrir_arquivo)
        file_menu.add_command(label="Salvar", command=self.salvar_arquivo)

        frame_principal = tk.Frame(root, bg="darkgray")
        frame_principal.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(frame_principal, width=800, height=600, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.minimap = tk.Canvas(frame_principal, width=150, height=120, bg="lightgrey")
        self.minimap.pack(side="right", padx=10, pady=10)

        self.window = (0, 0, 10, 7.5)
        self.viewport = (0, 0, 800, 600)
        self.objetos = []
        self.mover_window = 1

        self.root.bind("<Left>", lambda e: self.mover_window_direcao(-self.mover_window, 0))
        self.root.bind("<Right>", lambda e: self.mover_window_direcao(self.mover_window, 0))
        self.root.bind("<Up>", lambda e: self.mover_window_direcao(0, self.mover_window))
        self.root.bind("<Down>", lambda e: self.mover_window_direcao(0, -self.mover_window))

    def abrir_arquivo(self):
        caminho = filedialog.askopenfilename(filetypes=[("Arquivos XML", "*.xml")])
        if caminho:
            if not self.carregar_arquivo(caminho):
                messagebox.showerror("Erro", "Falha ao carregar o arquivo.")
            else:
                self.desenhar_viewport()
                self.desenhar_minimapa()

    def salvar_arquivo(self):
        caminho = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("Arquivos XML", "*.xml")])
        if caminho:
            self.gerar_arquivo_saida(caminho)

    def carregar_arquivo(self, caminho):
        try:
            self.objetos.clear()
            tree = et.parse(caminho)
            root = tree.getroot()

            self.viewport = self._carregar_viewport(root)
            self.window = self._carregar_window(root)

            self.objetos.extend(self._carregar_objetos(root))

            return True
        except Exception as e:
            print(f"Erro ao carregar o arquivo: {e}")
            return False

    def _carregar_viewport(self, root):
        vpmin = root.find("./viewport/vpmin")
        vpmax = root.find("./viewport/vpmax")
        if vpmin is not None and vpmax is not None:
            return (float(vpmin.get("x")), float(vpmin.get("y")),
                    float(vpmax.get("x")), float(vpmax.get("y")))
        return (0, 0, 800, 600)

    def _carregar_window(self, root):
        wmin = root.find("./window/wmin")
        wmax = root.find("./window/wmax")
        if wmin is not None and wmax is not None:
            return (float(wmin.get("x")), float(wmin.get("y")),
                    float(wmax.get("x")), float(wmax.get("y")))
        return (0, 0, 10, 7.5)

    def _carregar_objetos(self, root):
        objetos = []
        for ponto in root.findall("ponto"):
            x = float(ponto.get("x"))
            y = float(ponto.get("y"))
            objetos.append(("ponto", [(x, y)]))

        for reta in root.findall("reta"):
            pontos_reta = [(float(p.get("x")), float(p.get("y"))) for p in reta.findall("ponto")]
            objetos.append(("reta", pontos_reta))

        for poligono in root.findall("poligono"):
            pontos_poligono = [(float(p.get("x")), float(p.get("y"))) for p in poligono.findall("ponto")]
            objetos.append(("poligono", pontos_poligono))

        return objetos

    def window2viewport(self, ponto):
        x, y = ponto
        wx_min, wy_min, wx_max, wy_max = self.window
        vx_min, vy_min, vx_max, vy_max = self.viewport

        sx = (vx_max - vx_min) / (wx_max - wx_min)
        sy = (vy_max - vy_min) / (wy_max - wy_min)

        vx = vx_min + (x - wx_min) * sx
        vy = vy_min + (wy_max - y) * sy
        return vx, vy

    def desenhar_viewport(self):
        self.canvas.delete("all")
        for tipo, pontos in self.objetos:
            if tipo == "ponto":
                x_vp, y_vp = self.window2viewport(pontos[0])
                self.canvas.create_oval(x_vp - 2, y_vp - 2, x_vp + 2, y_vp + 2, fill="black")
            elif tipo == "reta":
                p1 = self.window2viewport(pontos[0])
                p2 = self.window2viewport(pontos[1])
                self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="blue")
            elif tipo == "poligono":
                pontos_vp = [self.window2viewport(p) for p in pontos]
                self.canvas.create_polygon(pontos_vp, outline="red", fill="", width=2)

    def desenhar_minimapa(self):
        self.minimap.delete("all")

        mini_vp_min_x, mini_vp_min_y, mini_vp_max_x, mini_vp_max_y = 0, 0, 150, 120
        mini_width = mini_vp_max_x - mini_vp_min_x
        mini_height = mini_vp_max_y - mini_vp_min_y

        mundo_min_x, mundo_min_y = 0, 0
        mundo_max_x, mundo_max_y = 25, 18.75

        world_width = mundo_max_x - mundo_min_x
        world_height = mundo_max_y - mundo_min_y
        scale_x = mini_width / world_width
        scale_y = mini_height / world_height

        rect_min_x = mini_vp_min_x + (self.window[0] - mundo_min_x) * scale_x
        rect_min_y = mini_height - (self.window[1] - mundo_min_y) * scale_y
        rect_max_x = mini_vp_min_x + (self.window[2] - mundo_min_x) * scale_x
        rect_max_y = mini_height - (self.window[3] - mundo_min_y) * scale_y

        self.minimap.create_rectangle(
            rect_min_x, rect_min_y, rect_max_x, rect_max_y,
            outline="black", fill="", width=1, dash=(1,2)
        )

        for tipo, pontos in self.objetos:
            pontos_mini = [(mini_vp_min_x + (x - mundo_min_x) * scale_x, mini_height - (y - mundo_min_y) * scale_y) for
                           x, y in pontos]

            if tipo == "ponto":
                x, y = pontos_mini[0]
                self.minimap.create_oval(x - 1, y - 1, x + 1, y + 1, fill="black")
            elif tipo == "reta":
                p1, p2 = pontos_mini
                self.minimap.create_line(p1[0], p1[1], p2[0], p2[1], fill="blue")
            elif tipo == "poligono":
                self.minimap.create_polygon(pontos_mini, outline="red", fill="", width=1)

    def mover_window_direcao(self, dx, dy):
        wx_min, wy_min, wx_max, wy_max = self.window

        nova_wx_min = wx_min + dx
        nova_wy_min = wy_min + dy
        nova_wx_max = wx_max + dx
        nova_wy_max = wy_max + dy

        mundo_min_x, mundo_min_y = 0, 0
        mundo_max_x, mundo_max_y = 25, 18.75

        if nova_wx_min < mundo_min_x:
            nova_wx_min = mundo_min_x
            nova_wx_max = nova_wx_min + (wx_max - wx_min)
        if nova_wy_min < mundo_min_y:
            nova_wy_min = mundo_min_y
            nova_wy_max = nova_wy_min + (wy_max - wy_min)

        if nova_wx_max > mundo_max_x:
            nova_wx_max = mundo_max_x
            nova_wx_min = nova_wx_max - (wx_max - wx_min)
        if nova_wy_max > mundo_max_y:
            nova_wy_max = mundo_max_y
            nova_wy_min = nova_wy_max - (wy_max - wy_min)

        self.window = (nova_wx_min, nova_wy_min, nova_wx_max, nova_wy_max)
        self.desenhar_viewport()
        self.desenhar_minimapa()

    def gerar_arquivo_saida(self, caminho):
        root = et.Element("dados")
        viewport_elem = et.SubElement(root, "viewport")
        vpmin_elem = et.SubElement(viewport_elem, "vpmin", x=str(self.viewport[0]), y=str(self.viewport[1]))
        vpmax_elem = et.SubElement(viewport_elem, "vpmax", x=str(self.viewport[2]), y=str(self.viewport[3]))

        window_elem = et.SubElement(root, "window")
        wmin_elem = et.SubElement(window_elem, "wmin", x=str(self.window[0]), y=str(self.window[1]))
        wmax_elem = et.SubElement(window_elem, "wmax", x=str(self.window[2]), y=str(self.window[3]))

        for tipo, pontos in self.objetos:
            if tipo == "ponto":
                ponto_elem = et.SubElement(root, "ponto", x=str(pontos[0][0]), y=str(pontos[0][1]))
            elif tipo == "reta":
                reta_elem = et.SubElement(root, "reta")
                for ponto in pontos:
                    et.SubElement(reta_elem, "ponto", x=str(ponto[0]), y=str(ponto[1]))
            elif tipo == "poligono":
                poligono_elem = et.SubElement(root, "poligono")
                for ponto in pontos:
                    et.SubElement(poligono_elem, "ponto", x=str(ponto[0]), y=str(ponto[1]))

        tree = et.ElementTree(root)
        tree.write(caminho)

        with open(caminho, "r", encoding="utf-8") as f:
            xml_str = f.read()
            reparado = minidom.parseString(xml_str).toprettyxml(indent="  ")
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(reparado)


if __name__ == "__main__":
    root = tk.Tk()
    app = Visualizador(root)
    root.mainloop()
