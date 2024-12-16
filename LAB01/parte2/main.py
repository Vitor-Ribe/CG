import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as et
from xml.dom import minidom
import math

# Classes para os objetos geométricos
class Ponto:
    def __init__(self, x, y, cor="black"):
        self.coordenadas_mundo = (x, y)  # Coordenadas no mundo
        self.coordenadas_ncs = None  # Coordenadas no NCS (serão calculadas depois)
        self.visivel = True  # Inicialmente, o ponto é visível
        self.cor = cor  # Cor do ponto

class Reta:
    def __init__(self, x1, y1, x2, y2, cor="blue"):
        self.coordenadas_mundo = [(x1, y1), (x2, y2)]  # Coordenadas dos dois pontos da reta
        self.coordenadas_ncs = None  # Coordenadas no NCS
        self.visivel = True  # Inicialmente, a reta é visível
        self.cor = cor  # Cor da reta

class Poligono:
    def __init__(self, vertices, cor="green"):
        self.coordenadas_mundo = vertices  # Lista de vértices do polígono
        self.coordenadas_ncs = None  # Coordenadas no NCS
        self.visivel = True  # Inicialmente, o polígono é visível
        self.cor = cor  # Cor do polígono


class Visualizador:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Objetos 2D")

        self.window_original = (0, 0, 10, 7.5)
        self.window = self.window_original;

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

        self.criar_interface_passo()
        self.criar_interface_rotacao()
        self.criar_interface_zoom()

        self.window = (0, 0, 10, 7.5)
        self.viewport = (0, 0, 800, 600)
        self.objetos = []  # Lista de objetos (Ponto, Reta, Polígono)
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
        
        # Carregar pontos
        for ponto in root.findall("ponto"):
            x = float(ponto.get("x"))
            y = float(ponto.get("y"))
            cor = ponto.get("cor", "black")  # Se não houver cor definida, será "black"
            objetos.append(Ponto(x, y, cor))
        
        # Carregar retas
        for reta in root.findall("reta"):
            pontos_reta = [(float(p.get("x")), float(p.get("y"))) for p in reta.findall("ponto")]
            if len(pontos_reta) == 2:
                cor = reta.get("cor", "blue")  # Se não houver cor definida, será "blue"
                objetos.append(Reta(pontos_reta[0][0], pontos_reta[0][1], pontos_reta[1][0], pontos_reta[1][1], cor))
        
        # Carregar polígonos
        for poligono in root.findall("poligono"):
            pontos_poligono = [(float(p.get("x")), float(p.get("y"))) for p in poligono.findall("ponto")]
            cor = poligono.get("cor", "green")  # Se não houver cor definida, será "green"
            objetos.append(Poligono(pontos_poligono, cor))
        
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
        
        for objeto in self.objetos:
            if not objeto.visivel:
                continue  # Não desenha objetos invisíveis após clipping

            # Desenhar pontos
            if isinstance(objeto, Ponto):
                x_vp, y_vp = self.window2viewport(objeto.coordenadas_mundo)
                self.canvas.create_oval(x_vp - 2, y_vp - 2, x_vp + 2, y_vp + 2, fill=objeto.cor)
            
            # Desenhar retas
            elif isinstance(objeto, Reta):
                p1 = self.window2viewport(objeto.coordenadas_mundo[0])
                p2 = self.window2viewport(objeto.coordenadas_mundo[1])
                self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill=objeto.cor)
            
            # Desenhar polígonos
            elif isinstance(objeto, Poligono):
                pontos_vp = [self.window2viewport(p) for p in objeto.coordenadas_mundo]
                self.canvas.create_polygon(pontos_vp, outline=objeto.cor, fill="", width=2)

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

        for objeto in self.objetos:
            if isinstance(objeto, Ponto):
                # Desenhando ponto no minimapa
                x, y = objeto.coordenadas_mundo
                x_mini = mini_vp_min_x + (x - mundo_min_x) * scale_x
                y_mini = mini_height - (y - mundo_min_y) * scale_y
                self.minimap.create_oval(x_mini - 1, y_mini - 1, x_mini + 1, y_mini + 1, fill="black")
            
            elif isinstance(objeto, Reta):
                # Desenhando reta no minimapa
                p1, p2 = objeto.coordenadas_mundo
                p1_mini = (mini_vp_min_x + (p1[0] - mundo_min_x) * scale_x, mini_height - (p1[1] - mundo_min_y) * scale_y)
                p2_mini = (mini_vp_min_x + (p2[0] - mundo_min_x) * scale_x, mini_height - (p2[1] - mundo_min_y) * scale_y)
                self.minimap.create_line(p1_mini[0], p1_mini[1], p2_mini[0], p2_mini[1], fill="blue")
            
            elif isinstance(objeto, Poligono):
                # Desenhando polígono no minimapa
                pontos_mini = [(mini_vp_min_x + (x - mundo_min_x) * scale_x, mini_height - (y - mundo_min_y) * scale_y) for x, y in objeto.coordenadas_mundo]
                self.minimap.create_polygon(pontos_mini, outline="red", fill="", width=1)


    def definir_passo(self, passo):
        self.mover_window = passo
    
    def criar_interface_passo(self):
        # Frame para entrada do passo de movimentação
        frame_passo = tk.Frame(self.root)
        frame_passo.pack(side="left", pady=10)

        label = tk.Label(frame_passo, text="Tamanho do Passo:")
        label.pack(side="left", padx=(15,0))

        # Caixa de entrada para o valor do passo
        self.entry_passo = tk.Entry(frame_passo, width=5)
        self.entry_passo.pack(side="left")

        # Botão para definir o valor do passo
        botao_definir_passo = tk.Button(frame_passo, text="Definir", command=self.atualizar_passo)
        botao_definir_passo.pack(side="left", padx=5)

    # Função para atualizar o valor do passo de movimentação
    def atualizar_passo(self):
        try:
            novo_passo = float(self.entry_passo.get())  # Pega o valor da caixa de entrada
            self.mover_window = novo_passo  # Atualiza a variável com o novo valor
            print(f"Novo passo de movimentação definido: {self.mover_window}")
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um valor numérico válido.")


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

    def rotacionar_window(self, angulo):
        # Calcula o centro da window
        cx = (self.window[0] + self.window[2]) / 2
        cy = (self.window[1] + self.window[3]) / 2

        # Converte o ângulo para radianos
        angulo_rad = math.radians(angulo)

        # Função para rotacionar um ponto ao redor do centro
        def rotacionar_ponto(x, y, cx, cy, angulo_rad):
            x_rot = cx + (x - cx) * math.cos(angulo_rad) - (y - cy) * math.sin(angulo_rad)
            y_rot = cy + (x - cx) * math.sin(angulo_rad) + (y - cy) * math.cos(angulo_rad)
            return x_rot, y_rot

        # Rotaciona os cantos da window
        x_min_rot, y_min_rot = rotacionar_ponto(self.window[0], self.window[1], cx, cy, angulo_rad)
        x_max_rot, y_max_rot = rotacionar_ponto(self.window[2], self.window[3], cx, cy, angulo_rad)

        # Atualiza as coordenadas da window
        self.window = (x_min_rot, y_min_rot, x_max_rot, y_max_rot)
        self.desenhar_viewport()
        self.desenhar_minimapa()
    
    def rotacionar_esquerda(self):
        try:
            angulo = float(self.entry_rotacao.get())  # Obtém o valor inserido na caixa de entrada
            self.rotacionar_window(-angulo)  # Rotaciona para a esquerda (valor negativo)
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um valor numérico válido para a rotação.")

    def rotacionar_direita(self):
        try:
            angulo = float(self.entry_rotacao.get())  # Obtém o valor inserido na caixa de entrada
            self.rotacionar_window(angulo)  # Rotaciona para a direita (valor positivo)
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um valor numérico válido para a rotação.")
    
    def resetar_transformacoes(self):
        self.window = self.window_original
        self.desenhar_viewport()
        self.desenhar_minimapa()
        print("Restaurado para a posição original.")

    def criar_interface_rotacao(self):
        # Frame para a rotação
        frame_rotacao = tk.Frame(self.root)
        frame_rotacao.pack(side="left", pady=10, padx=10)

        # Rótulo para indicar o campo de rotação
        label_rotacao = tk.Label(frame_rotacao, text="Valor da Rotação:")
        label_rotacao.pack(side="left", padx=(5,0))

        # Caixa de entrada para o valor da rotação
        self.entry_rotacao = tk.Entry(frame_rotacao, width=5)
        self.entry_rotacao.pack(side="left", padx=5)

        # Botão para rotacionar para a esquerda
        botao_rotacao_esquerda = tk.Button(frame_rotacao, text="⟲ Esquerda (L)", command=self.rotacionar_esquerda)
        botao_rotacao_esquerda.pack(side="left")

        # Botão para rotacionar para a direita
        botao_rotacao_direita = tk.Button(frame_rotacao, text="⟳ Direita (R)", command=self.rotacionar_direita)
        botao_rotacao_direita.pack(side="left")


    def aplicar_zoom(self, fator):
        # Calcula o centro da window
        cx = (self.window[0] + self.window[2]) / 2
        cy = (self.window[1] + self.window[3]) / 2

        # Calcula a nova largura e altura da window com o fator de zoom
        largura = (self.window[2] - self.window[0]) * fator
        altura = (self.window[3] - self.window[1]) * fator

        # Atualiza as coordenadas da window com base no zoom centrado
        self.window = (cx - largura / 2, cy - altura / 2, cx + largura / 2, cy + altura / 2)
        self.desenhar_viewport()
        self.desenhar_minimapa()
    
    def zoom_in(self):
        # Aumenta o zoom em 10%
        self.aplicar_zoom(1.1)

    def zoom_out(self):
        # Diminui o zoom em 10%
        self.aplicar_zoom(0.9)

    def criar_interface_zoom(self):
        # Frame para o zoom
        frame_zoom = tk.Frame(self.root)
        frame_zoom.pack(side="left", pady=10, padx=10)

        # Botão para aumentar o zoom
        botao_zoom_in = tk.Button(frame_zoom, text="Zoom (-)", command=self.zoom_in)
        botao_zoom_in.pack(side="left")

        # Botão para diminuir o zoom
        botao_zoom_out = tk.Button(frame_zoom, text="Zoom (+)", command=self.zoom_out)
        botao_zoom_out.pack(side="left")
    
      # Botão para resetar as transformações
        botao_resetar = tk.Button(frame_zoom, text="Resetar Transformações", command=self.resetar_transformacoes)
        botao_resetar.pack(side="left", padx=15)



    def gerar_arquivo_saida(self, caminho):
        root = et.Element("dados")
        viewport_elem = et.SubElement(root, "viewport")
        vpmin_elem = et.SubElement(viewport_elem, "vpmin", x=str(self.viewport[0]), y=str(self.viewport[1]))
        vpmax_elem = et.SubElement(viewport_elem, "vpmax", x=str(self.viewport[2]), y=str(self.viewport[3]))

        window_elem = et.SubElement(root, "window")
        wmin_elem = et.SubElement(window_elem, "wmin", x=str(self.window[0]), y=str(self.window[1]))
        wmax_elem = et.SubElement(window_elem, "wmax", x=str(self.window[2]), y=str(self.window[3]))

        for objeto in self.objetos:
            if isinstance(objeto, Ponto):
                ponto_elem = et.SubElement(root, "ponto", x=str(objeto.coordenadas_mundo[0]), y=str(objeto.coordenadas_mundo[1]), cor=objeto.cor)
            elif isinstance(objeto, Reta):
                reta_elem = et.SubElement(root, "reta", cor=objeto.cor)
                for ponto in objeto.coordenadas_mundo:
                    et.SubElement(reta_elem, "ponto", x=str(ponto[0]), y=str(ponto[1]))
            elif isinstance(objeto, Poligono):
                poligono_elem = et.SubElement(root, "poligono", cor=objeto.cor)
                for ponto in objeto.coordenadas_mundo:
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
