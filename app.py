import os
import datetime
import webbrowser
import customtkinter as ctk
from PIL import Image, ImageTk
from database import inicializar_bd, Mesa, Producto, PedidoMesa, Venta, Categoria, CierreCaja, Usuario, hash_password
import sys
import ctypes
from PIL import Image, ImageTk

# 1. FORZAR ÍCONO EN LA BARRA DE TAREAS DE WINDOWS
# (Debe ir ANTES de crear cualquier ventana o llamar a ctk.CTk())
if sys.platform.startswith("win"):
    try:
        app_id = "universum.barcontrolpro.sistema.1.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass

# ==========================================
# CONFIGURACIÓN DE TEMA Y ESTILOS GLOBALES
# ==========================================
ctk.set_appearance_mode("Dark")

COLORES = {
    "fondo_oscuro": "#121212",
    "fondo_panel": "#1E1E1E",
    "fondo_card": "#252525",
    "acento": "#00A8E8",          # Azul cian eléctrico (Logo Universum)
    "acento_hover": "#0086B8",    # Azul hover más oscuro
    "texto_principal": "#FFFFFF",
    "texto_secundario": "#AAAAAA",
    "mesa_ocupada": "#E74C3C",       
    "mesa_ocupada_hover": "#C0392B", 
    "mesa_libre": "#2ECC71",         
    "mesa_libre_hover": "#27AE60",   
    "eliminar": "#E74C3C",           
    "eliminar_hover": "#C0392B",
    "advertencia": "#F39C12"
}

FONT_TITULO = ("Segoe UI", 24, "bold")
FONT_SUBTITULO = ("Segoe UI", 18, "bold")
FONT_BOTON = ("Segoe UI", 13, "bold")
FONT_ESTANDAR = ("Segoe UI", 12, "normal")


def centrar_ventana(ventana, ancho, alto):
    """Centra una ventana de CustomTkinter en la pantalla."""
    ventana.update_idletasks()
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    x = max(0, (pantalla_ancho // 2) - (ancho // 2))
    y = max(0, (pantalla_alto // 2) - (alto // 2) - 30)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")


def generar_e_imprimir_ticket(mesa_num, pedidos, total_cobrado, id_venta, metodo_pago):
    """Genera un ticket formateado en HTML indicando el medio de pago."""
    if not os.path.exists("tickets"):
        os.makedirs("tickets")

    fecha_hora_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    nombre_archivo = f"tickets/Ticket_Mesa_{mesa_num}_Venta_{id_venta}.html"
    path_absoluto = os.path.abspath(nombre_archivo)

    filas_productos = ""
    for p in pedidos:
        subtotal = p.producto.precio * p.cantidad
        filas_productos += f"""
        <tr>
            <td style="text-align: left; padding: 3px 0;">{p.cantidad}x {p.producto.nombre}</td>
            <td style="text-align: right; padding: 3px 0;">${subtotal:.2f}</td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Ticket Mesa {mesa_num}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            width: 280px;
            margin: 0 auto;
            padding: 10px;
            color: #000000;
        }}
        .center {{ text-align: center; }}
        .bold {{ font-weight: bold; }}
        hr {{ border: none; border-top: 1px dashed #000; margin: 8px 0; }}
        table {{ width: 100%; border-collapse: collapse; }}
        td, th {{ font-size: 13px; }}
        .total {{ font-size: 16px; font-weight: bold; margin-top: 5px; }}
        @media print {{
            @page {{ margin: 0; }}
            body {{ width: 100%; padding: 5px; }}
        }}
    </style>
</head>
<body>
    <div class="center bold" style="font-size: 18px;">BAR CONTROL PRO</div>
    <div class="center" style="font-size: 12px;">Ticket de Consumo</div>
    <hr>
    <div style="font-size: 12px;"><b>Ticket N°:</b> {id_venta}</div>
    <div style="font-size: 12px;"><b>Fecha:</b> {fecha_hora_str}</div>
    <div style="font-size: 12px;"><b>Mesa:</b> N° {mesa_num}</div>
    <div style="font-size: 12px;"><b>Pago:</b> {metodo_pago}</div>
    <hr>
    <table>
        <thead>
            <tr>
                <th style="text-align: left;">CANT / PROD</th>
                <th style="text-align: right;">SUBTOTAL</th>
            </tr>
        </thead>
        <tbody>
            {filas_productos}
        </tbody>
    </table>
    <hr>
    <div class="total" style="display: flex; justify-content: space-between;">
        <span>TOTAL:</span>
        <span>${total_cobrado:.2f}</span>
    </div>
    <hr>
    <div class="center" style="font-size: 11px; margin-top: 8px;">
        ¡Gracias por su visita!<br>
        www.barcontrol.com
    </div>

    <script>
        window.onload = function() {{
            window.print();
        }};
    </script>
</body>
</html>
"""

    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(html_content)

    webbrowser.open(f"file://{path_absoluto}")


class LoginWindow(ctk.CTk):
    """Ventana de inicio de sesión antes de entrar al sistema."""
    def __init__(self):
        super().__init__()

        inicializar_bd()

        self.title("Bar Control PRO - Iniciar Sesión 🔐")
        centrar_ventana(self, 420, 520)
        self.resizable(False, False)
        self.configure(fg_color=COLORES["fondo_oscuro"])

        try:
            img_ico = Image.open("assets/universum.jpg")
            self.photo_ico = ImageTk.PhotoImage(img_ico)
            self.iconphoto(False, self.photo_ico)
        except Exception:
            pass

        card = ctk.CTkFrame(self, corner_radius=18, fg_color=COLORES["fondo_panel"])
        card.pack(fill="both", expand=True, padx=25, pady=25)

        try:
            img_logo_pil = Image.open("assets/universum.jpg")
            self.logo_img = ctk.CTkImage(light_image=img_logo_pil, dark_image=img_logo_pil, size=(80, 80))
            lbl_img = ctk.CTkLabel(card, image=self.logo_img, text="")
            lbl_img.pack(pady=(20, 5))
        except Exception:
            pass

        ctk.CTkLabel(card, text="Bar Control PRO", font=FONT_TITULO, text_color=COLORES["acento"]).pack(pady=(5, 0))
        ctk.CTkLabel(card, text="Acceso al Sistema", font=FONT_ESTANDAR, text_color=COLORES["texto_secundario"]).pack(pady=(0, 15))

        self.entry_usuario = ctk.CTkEntry(card, placeholder_text="👤 Usuario", font=FONT_ESTANDAR, height=40, corner_radius=10)
        self.entry_usuario.pack(fill="x", padx=30, pady=8)

        self.entry_pass = ctk.CTkEntry(card, placeholder_text="🔒 Contraseña", font=FONT_ESTANDAR, height=40, corner_radius=10, show="•")
        self.entry_pass.pack(fill="x", padx=30, pady=8)

        self.lbl_error = ctk.CTkLabel(card, text="", font=FONT_ESTANDAR, text_color="#E74C3C")
        self.lbl_error.pack(pady=5)

        btn_ingresar = ctk.CTkButton(
            card, text="INGRESAR", font=FONT_BOTON, height=42, corner_radius=21,
            fg_color=COLORES["acento"], hover_color=COLORES["acento_hover"],
            command=self.validar_login
        )
        btn_ingresar.pack(fill="x", padx=30, pady=(10, 15))

        self.entry_pass.bind("<Return>", lambda event: self.validar_login())

    def validar_login(self):
        user = self.entry_usuario.get().strip()
        password = self.entry_pass.get().strip()

        if not user or not password:
            self.lbl_error.configure(text="⚠️ Complete ambos campos.")
            return

        pass_hashed = hash_password(password)
        usuario_db = Usuario.get_or_none((Usuario.username == user) & (Usuario.password_hash == pass_hashed))

        if usuario_db:
            self.destroy()
            app_principal = BarSystemApp(usuario_db)
            app_principal.mainloop()
        else:
            self.lbl_error.configure(text="❌ Usuario o contraseña incorrectos.")


class DetalleMesaWindow(ctk.CTkToplevel):
    def __init__(self, master, mesa_obj, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        self.master_app = master
        self.mesa = mesa_obj
        self.title(f"Gestión Mesa {self.mesa.numero} 🍽️")
        
        # --- REDUCCIÓN DE TAMAÑO Y CENTRADO REPARADO ---
        centrar_ventana(self, 820, 540)
        self.configure(fg_color=COLORES["fondo_oscuro"])
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)

        try:
            img_ico = Image.open("assets/universum.jpg")
            self.photo_ico = ImageTk.PhotoImage(img_ico)
            self.iconphoto(False, self.photo_ico)
        except Exception:
            pass

        # Ajustamos el ancho mínimo de las columnas para la ventana más chica
        self.grid_columnconfigure(0, weight=1, minsize=360)
        self.grid_columnconfigure(1, weight=1, minsize=400)
        self.grid_rowconfigure(0, weight=1)

        # --- PANEL IZQUIERDO: COMANDA ACTUAL ---
        self.frame_pedido = ctk.CTkFrame(self, corner_radius=15, fg_color=COLORES["fondo_panel"])
        self.frame_pedido.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.frame_pedido.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(self.frame_pedido, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="ew")
        
        ctk.CTkLabel(
            header_frame, text=f"Mesa {self.mesa.numero}", 
            font=FONT_SUBTITULO, text_color=COLORES["texto_principal"]
        ).pack(side="left")
        
        estado_color = COLORES["mesa_libre"] if self.mesa.estado == "Libre" else COLORES["mesa_ocupada"]
        self.lbl_estado = ctk.CTkLabel(
            header_frame, text=f"• {self.mesa.estado}", 
            font=FONT_BOTON, text_color=estado_color
        )
        self.lbl_estado.pack(side="right")

        self.txt_items = ctk.CTkTextbox(
            self.frame_pedido, corner_radius=10,
            fg_color="#141414", text_color="#DDDDDD", font=FONT_ESTANDAR
        )
        self.txt_items.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")

        footer_frame = ctk.CTkFrame(self.frame_pedido, fg_color="transparent")
        footer_frame.grid(row=2, column=0, padx=15, pady=15, sticky="ew")

        self.lbl_total = ctk.CTkLabel(
            footer_frame, text="Total: $0.00", 
            font=("Segoe UI", 22, "bold"), text_color=COLORES["acento"]
        )
        self.lbl_total.pack(pady=(0, 5))

        ctk.CTkLabel(
            footer_frame, text="Forma de Pago:", 
            font=FONT_ESTANDAR, text_color=COLORES["texto_secundario"]
        ).pack(anchor="w", padx=5, pady=(5, 2))

        self.combo_pago = ctk.CTkOptionMenu(
            footer_frame, 
            values=["💵 Efectivo", "📱 Transferencia", "💳 Tarjeta"],
            font=FONT_BOTON, height=35
        )
        self.combo_pago.pack(fill="x", pady=(0, 10))

        self.btn_cobrar = ctk.CTkButton(
            footer_frame, text="💳 CERRAR Y COBRAR (IMPRIMIR)", 
            font=FONT_BOTON, height=45, corner_radius=22,
            fg_color=COLORES["acento"], hover_color=COLORES["acento_hover"],
            command=self.cerrar_y_cobrar
        )
        self.btn_cobrar.pack(fill="x")

        # --- PANEL DERECHO: BUSCADOR Y PRODUCTOS ---
        self.frame_productos = ctk.CTkFrame(self, corner_radius=15, fg_color=COLORES["fondo_panel"])
        self.frame_productos.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew")
        self.frame_productos.grid_rowconfigure(2, weight=1)
        self.frame_productos.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.frame_productos, text="Añadir Producto", 
            font=FONT_SUBTITULO, text_color=COLORES["texto_principal"]
        ).grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        self.entry_buscar = ctk.CTkEntry(
            self.frame_productos, placeholder_text="🔍 Buscar producto...", 
            font=FONT_ESTANDAR, height=38, corner_radius=10
        )
        self.entry_buscar.grid(row=1, column=0, padx=15, pady=(5, 10), sticky="ew")
        self.entry_buscar.bind("<KeyRelease>", lambda event: self.cargar_productos_bd())

        self.grid_items = ctk.CTkScrollableFrame(self.frame_productos, fg_color="transparent")
        self.grid_items.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.grid_items.grid_columnconfigure((0, 1), weight=1)

        self.cargar_productos_bd()
        self.actualizar_comanda_vista()

    def cargar_productos_bd(self):
        for child in self.grid_items.winfo_children():
            child.destroy()

        filtro = self.entry_buscar.get().strip()
        if filtro:
            productos = Producto.select().where(Producto.nombre.contains(filtro))
        else:
            productos = Producto.select()

        for i, prod in enumerate(productos):
            cat_txt = f"[{prod.categoria.nombre}] " if prod.categoria else ""
            btn_prod = ctk.CTkButton(
                self.grid_items, 
                text=f"{cat_txt}{prod.nombre}\n${prod.precio:.2f}", 
                font=FONT_BOTON,
                fg_color="#2A2A2A", hover_color="#3A3A3A",
                height=70, corner_radius=12,
                command=lambda p=prod: self.agregar_producto_a_mesa(p)
            )
            btn_prod.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="nsew")

    def agregar_producto_a_mesa(self, producto):
        if self.mesa.estado == "Libre":
            self.mesa.estado = "Ocupada"
            self.mesa.save()

        pedido_existente = PedidoMesa.get_or_none(mesa=self.mesa, producto=producto)
        if pedido_existente:
            pedido_existente.cantidad += 1
            pedido_existente.save()
        else:
            PedidoMesa.create(mesa=self.mesa, producto=producto, cantidad=1)

        self.actualizar_comanda_vista()

    def actualizar_comanda_vista(self):
        self.txt_items.configure(state="normal")
        self.txt_items.delete("0.0", "end")

        pedidos = PedidoMesa.select().where(PedidoMesa.mesa == self.mesa)
        total = 0.0

        if not pedidos:
            self.txt_items.insert("0.0", "Mesa sin consumo activo.")
        else:
            for p in pedidos:
                subtotal = float(p.producto.precio * p.cantidad)
                total += subtotal
                linea = f"• {p.cantidad}x {p.producto.nombre} - ${subtotal:.2f}\n"
                self.txt_items.insert("end", linea)

        self.txt_items.configure(state="disabled")
        self.lbl_total.configure(text=f"Total: ${total:.2f}")
        
        estado_color = COLORES["mesa_libre"] if self.mesa.estado == "Libre" else COLORES["mesa_ocupada"]
        self.lbl_estado.configure(
            text=f"• {self.mesa.estado}", 
            text_color=estado_color
        )

    def cerrar_y_cobrar(self):
        pedidos = list(PedidoMesa.select().where(PedidoMesa.mesa == self.mesa))
        if not pedidos:
            self.cerrar_ventana()
            return

        total = sum(p.producto.precio * p.cantidad for p in pedidos)
        metodo = self.combo_pago.get()
        
        venta_obj = Venta.create(mesa_numero=self.mesa.numero, total=total, metodo_pago=metodo, cerrado=False)

        generar_e_imprimir_ticket(self.mesa.numero, pedidos, total, venta_obj.id, metodo)

        PedidoMesa.delete().where(PedidoMesa.mesa == self.mesa).execute()
        self.mesa.estado = "Libre"
        self.mesa.save()

        self.cerrar_ventana()

    def cerrar_ventana(self):
        self.master_app.mostrar_mesas()
        self.destroy()


class BarSystemApp(ctk.CTk):
    
    def __init__(self, usuario_actual):
        super().__init__()

        self.usuario = usuario_actual

        self.title(f"Bar Control PRO — Sesión: {self.usuario.username.upper()}")
        centrar_ventana(self, 1250, 720)
        self.minsize(1050, 650)
        self.configure(fg_color=COLORES["fondo_oscuro"])
        

        # --- CONFIGURACIÓN DEL ÍCONO (VENTANA SUPERIOR Y BARRA) ---
        try:
            # 1. Intentamos cargar icono en formato .ico si existe
            self.iconbitmap("assets/universum.ico")
        except Exception:
            try:
                # 2. Si es .jpg o .png, lo cargamos con PIL e iconphoto
                img_icono_pil = Image.open("assets/universum.jpg")
                self.photo_icono = ImageTk.PhotoImage(img_icono_pil)
                self.iconphoto(False, self.photo_icono)
            except Exception as e:
                print(f"No se pudo establecer el icono superior: {e}")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

       # --- CONFIGURACIÓN DEL ÍCONO (VENTANA SUPERIOR Y BARRA) ---
        try:
            # 1. Intentamos cargar icono en formato .ico si existe
            self.iconbitmap("assets/universum.ico")
        except Exception:
            try:
                # 2. Si es .jpg o .png, lo cargamos con PIL e iconphoto
                img_icono_pil = Image.open("assets/universum.jpg")
                self.photo_icono = ImageTk.PhotoImage(img_icono_pil)
                self.iconphoto(False, self.photo_icono)
            except Exception as e:
                print(f"No se pudo establecer el icono superior: {e}")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- SIDEBAR DE NAVEGACIÓN ---
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COLORES["fondo_panel"])
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, text="Bar Control PRO", 
            font=("Segoe UI", 22, "bold"), text_color=COLORES["acento"]
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(25, 5))

        ctk.CTkLabel(
            self.sidebar_frame, text=f"👤 {self.usuario.username} ({self.usuario.rol})", 
            font=FONT_ESTANDAR, text_color=COLORES["texto_secundario"]
        ).grid(row=1, column=0, padx=20, pady=(0, 15))

        self.btn_nav_mesas = self.crear_boton_nav("🏠 Inicio / Mesas", self.mostrar_mesas, 2)
        self.btn_nav_menu = self.crear_boton_nav("🍔 Menú y Categorías", self.mostrar_gestion_productos, 3)
        self.btn_nav_comandas = self.crear_boton_nav("📝 Comandas Activas", self.mostrar_pedidos, 4)
        self.btn_nav_reportes = self.crear_boton_nav("📊 Cierre de Caja", self.mostrar_inventario, 5)
        

        # --- LOGO UNIVERSUM ---
        try:
            imagen_pil = Image.open("assets/universum.jpg")
            self.logo_sidebar_img = ctk.CTkImage(
                light_image=imagen_pil, 
                dark_image=imagen_pil, 
                size=(120, 120)
            )
            self.lbl_logo_sidebar = ctk.CTkLabel(self.sidebar_frame, image=self.logo_sidebar_img, text="")
            self.lbl_logo_sidebar.grid(row=6, column=0, pady=(15, 2))
        except Exception as e:
            print(f"No se pudo cargar el logo lateral: {e}")


        # --- BOTÓN CERRAR SESIÓN ---
        btn_logout = ctk.CTkButton(
            self.sidebar_frame, text="🚪 Cerrar Sesión", font=FONT_ESTANDAR,
            height=32, corner_radius=10, fg_color="#333333", hover_color=COLORES["eliminar_hover"],
            command=self.cerrar_sesion
        )
        btn_logout.grid(row=8, column=0, padx=20, pady=(5, 15), sticky="ew")

        # --- ÁREA PRINCIPAL ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=18, fg_color=COLORES["fondo_panel"])
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.mostrar_mesas()

    def cerrar_sesion(self):
        self.destroy()
        login = LoginWindow()
        login.mainloop()

    def crear_boton_nav(self, texto, comando, fila):
        btn = ctk.CTkButton(
            self.sidebar_frame, text=texto, font=FONT_BOTON,
            height=45, corner_radius=12, fg_color="transparent", 
            text_color=COLORES["texto_secundario"], hover_color="#2A2A2A",
            anchor="w", command=comando
        )
        btn.grid(row=fila, column=0, padx=15, pady=6, sticky="ew")
        return btn

    def limpiar_pantalla(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def agregar_nueva_mesa(self):
        mesas_existentes = list(Mesa.select().order_by(Mesa.numero.desc()))
        siguiente_num = (mesas_existentes[0].numero + 1) if mesas_existentes else 1
        Mesa.create(numero=siguiente_num, estado="Libre")
        self.mostrar_mesas()

    def eliminar_ultima_mesa(self):
        ultima_mesa = Mesa.select().where(Mesa.estado == "Libre").order_by(Mesa.numero.desc()).first()
        if ultima_mesa:
            PedidoMesa.delete().where(PedidoMesa.mesa == ultima_mesa).execute()
            ultima_mesa.delete_instance()
            self.mostrar_mesas()

    def mostrar_mesas(self):
        self.limpiar_pantalla()
        
        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 15))
        
        ctk.CTkLabel(
            header, text="Mapa de Mesas Activas", 
            font=FONT_TITULO, text_color=COLORES["texto_principal"]
        ).pack(side="left")

        btn_agregar = ctk.CTkButton(
            header, text="➕ Agregar Mesa", 
            font=FONT_BOTON, height=38, corner_radius=10,
            fg_color=COLORES["acento"], hover_color=COLORES["acento_hover"],
            command=self.agregar_nueva_mesa
        )
        btn_agregar.pack(side="right")

        btn_eliminar = ctk.CTkButton(
            header, text="🗑️ Eliminar Mesa", 
            font=FONT_BOTON, height=38, corner_radius=10,
            fg_color=COLORES["eliminar"], hover_color=COLORES["eliminar_hover"],
            command=self.eliminar_ultima_mesa
        )
        btn_eliminar.pack(side="right", padx=(0, 10))

        grid_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=20, pady=10)

        mesas_bd = Mesa.select().order_by(Mesa.numero)

        for i, mesa in enumerate(mesas_bd):
            es_ocupada = (mesa.estado == "Ocupada")
            color_fondo = COLORES["mesa_ocupada"] if es_ocupada else COLORES["mesa_libre"]
            hover = COLORES["mesa_ocupada_hover"] if es_ocupada else COLORES["mesa_libre_hover"]

            btn_mesa = ctk.CTkButton(
                grid_frame, 
                text=f"Mesa {mesa.numero}\n\n[{mesa.estado}]", 
                font=("Segoe UI", 14, "bold"),
                width=150, height=120, corner_radius=16,
                fg_color=color_fondo, hover_color=hover,
                command=lambda m=mesa: DetalleMesaWindow(self, m)
            )
            col = i % 4
            row = i // 4
            btn_mesa.grid(row=row, column=col, padx=15, pady=15)
        
        grid_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

    def mostrar_gestion_productos(self):
        self.limpiar_pantalla()

        self.main_frame.grid_columnconfigure((0, 1), weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self.main_frame, text="Gestión de Menú y Productos", 
            font=FONT_TITULO, text_color=COLORES["texto_principal"]
        ).grid(row=0, column=0, columnspan=2, padx=30, pady=(20, 10), sticky="w")

        frame_form = ctk.CTkFrame(self.main_frame, fg_color=COLORES["fondo_card"], corner_radius=15)
        frame_form.grid(row=1, column=0, padx=(20, 10), pady=15, sticky="nsew")

        ctk.CTkLabel(
            frame_form, text="➕ Agregar Producto", 
            font=FONT_SUBTITULO, text_color=COLORES["acento"]
        ).pack(padx=20, pady=(15, 10), anchor="w")

        ctk.CTkLabel(frame_form, text="Nombre del Producto:", font=FONT_ESTANDAR).pack(padx=20, pady=(5, 0), anchor="w")
        entry_nombre = ctk.CTkEntry(frame_form, placeholder_text="Ej: Café / Hamburguesa", font=FONT_ESTANDAR, height=35)
        entry_nombre.pack(padx=20, pady=(0, 8), fill="x")

        ctk.CTkLabel(frame_form, text="Precio ($):", font=FONT_ESTANDAR).pack(padx=20, pady=(5, 0), anchor="w")
        entry_precio = ctk.CTkEntry(frame_form, placeholder_text="Ej: 2500.00", font=FONT_ESTANDAR, height=35)
        entry_precio.pack(padx=20, pady=(0, 8), fill="x")

        ctk.CTkLabel(frame_form, text="Categoría:", font=FONT_ESTANDAR).pack(padx=20, pady=(5, 0), anchor="w")
        cats = [c.nombre for c in Categoria.select()]
        combo_cat = ctk.CTkOptionMenu(frame_form, values=cats if cats else ["General"], font=FONT_ESTANDAR, height=35)
        combo_cat.pack(padx=20, pady=(0, 10), fill="x")

        lbl_mensaje = ctk.CTkLabel(frame_form, text="", font=FONT_ESTANDAR)
        lbl_mensaje.pack(pady=2)

        def guardar_producto():
            nombre = entry_nombre.get().strip()
            precio_raw = entry_precio.get().strip()
            cat_nombre = combo_cat.get()

            if not nombre or not precio_raw:
                lbl_mensaje.configure(text="⚠️ Complete todos los campos.", text_color="#E74C3C")
                return

            try:
                precio = float(precio_raw)
                categoria_obj = Categoria.get_or_none(Categoria.nombre == cat_nombre)
                Producto.create(nombre=nombre, precio=precio, categoria=categoria_obj)

                lbl_mensaje.configure(text="¡Producto guardado exitosamente! ✅", text_color="#2ECC71")
                entry_nombre.delete(0, "end")
                entry_precio.delete(0, "end")
                refrescar_lista_menu()
            except ValueError:
                lbl_mensaje.configure(text="⚠️ El precio debe ser numérico.", text_color="#E74C3C")

        btn_guardar = ctk.CTkButton(
            frame_form, text="💾 Guardar Producto", 
            font=FONT_BOTON, height=40, corner_radius=18,
            fg_color=COLORES["acento"], hover_color=COLORES["acento_hover"],
            command=guardar_producto
        )
        btn_guardar.pack(padx=20, pady=10, fill="x")

        ctk.CTkFrame(frame_form, height=2, fg_color="#333333").pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(frame_form, text="📁 Añadir Nueva Categoría", font=FONT_BOTON, text_color=COLORES["texto_principal"]).pack(padx=20, anchor="w")
        entry_nueva_cat = ctk.CTkEntry(frame_form, placeholder_text="Ej: Tragos / Postres", font=FONT_ESTANDAR, height=35)
        entry_nueva_cat.pack(padx=20, pady=(5, 10), fill="x")

        def agregar_categoria():
            cat_nombre = entry_nueva_cat.get().strip()
            if cat_nombre:
                Categoria.get_or_create(nombre=cat_nombre)
                entry_nueva_cat.delete(0, "end")
                nuevas_cats = [c.nombre for c in Categoria.select()]
                combo_cat.configure(values=nuevas_cats)
                lbl_mensaje.configure(text="Categoría creada! ✅", text_color="#2ECC71")

        ctk.CTkButton(
            frame_form, text="➕ Crear Categoría", font=FONT_BOTON, height=35,
            fg_color="#34495E", hover_color="#2C3E50", command=agregar_categoria
        ).pack(padx=20, pady=(0, 15), fill="x")

        frame_lista = ctk.CTkFrame(self.main_frame, fg_color=COLORES["fondo_card"], corner_radius=15)
        frame_lista.grid(row=1, column=1, padx=(10, 20), pady=15, sticky="nsew")
        frame_lista.grid_rowconfigure(2, weight=1)
        frame_lista.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame_lista, text="📋 Menú Actual", 
            font=FONT_SUBTITULO, text_color=COLORES["texto_principal"]
        ).grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        entry_buscar_menu = ctk.CTkEntry(
            frame_lista, placeholder_text="🔍 Buscar en el menú...", 
            font=FONT_ESTANDAR, height=35
        )
        entry_buscar_menu.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        scroll_menu = ctk.CTkScrollableFrame(frame_lista, fg_color="transparent")
        scroll_menu.grid(row=2, column=0, padx=15, pady=10, sticky="nsew")

        def eliminar_producto_bd(prod_id):
            PedidoMesa.delete().where(PedidoMesa.producto == prod_id).execute()
            Producto.delete_by_id(prod_id)
            refrescar_lista_menu()

        def refrescar_lista_menu(event=None):
            for child in scroll_menu.winfo_children():
                child.destroy()

            filtro = entry_buscar_menu.get().strip()
            prods = Producto.select().where(Producto.nombre.contains(filtro)) if filtro else Producto.select()

            for p in prods:
                item_frame = ctk.CTkFrame(scroll_menu, fg_color="#1E1E1E", corner_radius=8)
                item_frame.pack(fill="x", pady=4, padx=5)

                cat_txt = f"[{p.categoria.nombre}] " if p.categoria else ""
                
                ctk.CTkLabel(
                    item_frame, text=f"{cat_txt}{p.nombre}", 
                    font=FONT_BOTON, text_color=COLORES["texto_principal"]
                ).pack(side="left", padx=15, pady=10)

                btn_eliminar = ctk.CTkButton(
                    item_frame, 
                    text="🗑", 
                    font=("Segoe UI Symbol", 15),
                    width=38, 
                    height=38,
                    anchor="center",
                    fg_color=COLORES["eliminar"], 
                    hover_color=COLORES["eliminar_hover"],
                    corner_radius=8, 
                    command=lambda pid=p.id: eliminar_producto_bd(pid)
                )
                btn_eliminar.pack(side="right", padx=(5, 12), pady=6)

                ctk.CTkLabel(
                    item_frame, text=f"${p.precio:.2f}", 
                    font=FONT_BOTON, text_color=COLORES["acento"]
                ).pack(side="right", padx=10, pady=10)

        entry_buscar_menu.bind("<KeyRelease>", refrescar_lista_menu)
        refrescar_lista_menu()

    def mostrar_pedidos(self):
        self.limpiar_pantalla()

        ctk.CTkLabel(
            self.main_frame, text="📝 Comandas y Pedidos Activos", 
            font=FONT_TITULO, text_color=COLORES["texto_principal"]
        ).pack(padx=30, pady=(25, 15), anchor="w")

        scroll_comandas = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        scroll_comandas.pack(fill="both", expand=True, padx=20, pady=10)

        mesas_ocupadas = Mesa.select().where(Mesa.estado == "Ocupada")

        if not mesas_ocupadas.count():
            ctk.CTkLabel(
                scroll_comandas, text="✨ No hay comandas abiertas en este momento.", 
                font=FONT_SUBTITULO, text_color=COLORES["texto_secundario"]
            ).pack(pady=50)
            return

        for mesa in mesas_ocupadas:
            card = ctk.CTkFrame(scroll_comandas, fg_color=COLORES["fondo_card"], corner_radius=12)
            card.pack(fill="x", pady=8, padx=10)

            header_card = ctk.CTkFrame(card, fg_color="transparent")
            header_card.pack(fill="x", padx=15, pady=10)

            ctk.CTkLabel(header_card, text=f"Mesa {mesa.numero}", font=FONT_SUBTITULO, text_color=COLORES["acento"]).pack(side="left")

            pedidos = PedidoMesa.select().where(PedidoMesa.mesa == mesa)
            items_str = ", ".join([f"{p.cantidad}x {p.producto.nombre}" for p in pedidos])
            total_mesa = sum([p.cantidad * p.producto.precio for p in pedidos])

            ctk.CTkLabel(card, text=items_str, font=FONT_ESTANDAR, text_color="#DDDDDD", wraplength=700, justify="left").pack(padx=15, pady=(0, 10), anchor="w")
            ctk.CTkLabel(header_card, text=f"Total acumulado: ${total_mesa:.2f}", font=FONT_BOTON, text_color=COLORES["texto_principal"]).pack(side="right")

    def obtener_rango_turno(self, turno_nombre):
        """Retorna las horas inicio y fin según el turno seleccionado para el día de hoy."""
        ahora = datetime.datetime.now()
        
        if turno_nombre == "Turno Mañana (07 - 13 hs)":
            inicio = ahora.replace(hour=7, minute=0, second=0, microsecond=0)
            fin = ahora.replace(hour=13, minute=0, second=0, microsecond=0)
        elif turno_nombre == "Turno Tarde (17 - 21 hs)":
            inicio = ahora.replace(hour=17, minute=0, second=0, microsecond=0)
            fin = ahora.replace(hour=21, minute=0, second=0, microsecond=0)
        else:  # Día Completo
            inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
            fin = ahora.replace(hour=23, minute=59, second=59, microsecond=0)
            
        return inicio, fin

    def mostrar_inventario(self):
        self.limpiar_pantalla()

        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))

        ctk.CTkLabel(
            header_frame, text="📊 Cierre de Caja y Reporte por Turno", 
            font=FONT_TITULO, text_color=COLORES["texto_principal"]
        ).pack(side="left")

        hora_actual = datetime.datetime.now().hour
        if 7 <= hora_actual < 13:
            turno_defecto = "Turno Mañana (07 - 13 hs)"
        elif 17 <= hora_actual < 21:
            turno_defecto = "Turno Tarde (17 - 21 hs)"
        else:
            turno_defecto = "Día Completo (00 - 24 hs)"

        self.combo_turno = ctk.CTkOptionMenu(
            header_frame,
            values=[
                "Turno Mañana (07 - 13 hs)",
                "Turno Tarde (17 - 21 hs)",
                "Día Completo (00 - 24 hs)"
            ],
            font=FONT_BOTON, height=38,
            command=lambda val: self.refrescar_reporte_caja()
        )
        self.combo_turno.set(turno_defecto)
        self.combo_turno.pack(side="right")

        self.kpi_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.kpi_frame.pack(fill="x", padx=20, pady=10)
        self.kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        action_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=30, pady=5)

        self.btn_cerrar_caja = ctk.CTkButton(
            action_frame, text="🔒 IMPRIMIR CIERRE DE TURNO",
            font=FONT_BOTON, height=40, corner_radius=10,
            fg_color=COLORES["acento"], hover_color=COLORES["acento_hover"],
            command=self.imprimir_cierre_turno
        )
        self.btn_cerrar_caja.pack(side="right")

        ctk.CTkLabel(
            self.main_frame, text="🕒 Ventas Correspondientes al Turno", 
            font=FONT_SUBTITULO, text_color=COLORES["texto_principal"]
        ).pack(padx=30, pady=(15, 10), anchor="w")

        self.scroll_ventas = ctk.CTkScrollableFrame(self.main_frame, fg_color=COLORES["fondo_card"], corner_radius=12)
        self.scroll_ventas.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.refrescar_reporte_caja()

    def refrescar_reporte_caja(self):
        for child in self.scroll_ventas.winfo_children():
            child.destroy()
        for child in self.kpi_frame.winfo_children():
            child.destroy()

        turno_sel = self.combo_turno.get()
        f_inicio, f_fin = self.obtener_rango_turno(turno_sel)

        ventas_turno = list(
            Venta.select().where(
                (Venta.fecha >= f_inicio) & 
                (Venta.fecha <= f_fin) & 
                ((Venta.cerrado == False) | (Venta.cerrado == None))
            ).order_by(Venta.fecha.desc())
        )

        tot_efectivo = sum(v.total for v in ventas_turno if "Efectivo" in getattr(v, "metodo_pago", ""))
        tot_mp = sum(v.total for v in ventas_turno if "Transferencia" in getattr(v, "metodo_pago", ""))
        tot_tarjeta = sum(v.total for v in ventas_turno if "Tarjeta" in getattr(v, "metodo_pago", ""))
        tot_general = sum(v.total for v in ventas_turno)

        metricas = [
            ("💵 Efectivo Caja", f"${tot_efectivo:.2f}", "#2ECC71"),
            ("📱 Transferencia", f"${tot_mp:.2f}", "#009EE3"),
            ("💳 Tarjetas", f"${tot_tarjeta:.2f}", "#9B59B6"),
            ("💰 Total Recaudado", f"${tot_general:.2f}", COLORES["acento"])
        ]

        for i, (titulo, valor, color) in enumerate(metricas):
            card = ctk.CTkFrame(self.kpi_frame, fg_color=COLORES["fondo_card"], corner_radius=12)
            card.grid(row=0, column=i, padx=5, sticky="ew")
            ctk.CTkLabel(card, text=titulo, font=FONT_ESTANDAR, text_color=COLORES["texto_secundario"]).pack(pady=(12, 0))
            ctk.CTkLabel(card, text=valor, font=("Segoe UI", 20, "bold"), text_color=color).pack(pady=(0, 12))

        if not ventas_turno:
            ctk.CTkLabel(self.scroll_ventas, text="Sin ventas pendientes de cierre en este turno.", font=FONT_ESTANDAR).pack(pady=30)
        else:
            for v in ventas_turno:
                row_item = ctk.CTkFrame(self.scroll_ventas, fg_color="#1E1E1E", corner_radius=8)
                row_item.pack(fill="x", pady=3, padx=5)

                fecha_fmt = v.fecha.strftime("%d/%m/%Y %H:%M hs") if isinstance(v.fecha, datetime.datetime) else str(v.fecha)
                metodo_str = getattr(v, "metodo_pago", "Efectivo")

                ctk.CTkLabel(row_item, text=f"Mesa {v.mesa_numero}", font=FONT_BOTON, text_color=COLORES["texto_principal"]).pack(side="left", padx=15, pady=8)
                ctk.CTkLabel(row_item, text=f"Hora: {fecha_fmt}", font=FONT_ESTANDAR, text_color=COLORES["texto_secundario"]).pack(side="left", padx=15, pady=8)
                ctk.CTkLabel(row_item, text=f"[{metodo_str}]", font=FONT_ESTANDAR, text_color="#F1C40F").pack(side="left", padx=10, pady=8)
                ctk.CTkLabel(row_item, text=f"+ ${v.total:.2f}", font=FONT_BOTON, text_color=COLORES["acento"]).pack(side="right", padx=15, pady=8)

    def imprimir_cierre_turno(self):
        turno_sel = self.combo_turno.get()
        f_inicio, f_fin = self.obtener_rango_turno(turno_sel)
        
        ventas_turno = list(
            Venta.select().where(
                (Venta.fecha >= f_inicio) & 
                (Venta.fecha <= f_fin) & 
                ((Venta.cerrado == False) | (Venta.cerrado == None))
            )
        )

        if not ventas_turno:
            return

        tot_efectivo = sum(v.total for v in ventas_turno if "Efectivo" in getattr(v, "metodo_pago", ""))
        tot_mp = sum(v.total for v in ventas_turno if "Transferencia" in getattr(v, "metodo_pago", ""))
        tot_tarjeta = sum(v.total for v in ventas_turno if "Tarjeta" in getattr(v, "metodo_pago", ""))
        tot_general = sum(v.total for v in ventas_turno)

        CierreCaja.create(
            turno=turno_sel,
            total_efectivo=tot_efectivo,
            total_mp=tot_mp,
            total_tarjeta=tot_tarjeta,
            total_general=tot_general
        )

        for v in ventas_turno:
            v.cerrado = True
            v.save()

        if not os.path.exists("tickets"):
            os.makedirs("tickets")

        fecha_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        nombre_archivo = f"tickets/Cierre_Caja_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        path_absoluto = os.path.abspath(nombre_archivo)

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Cierre de Caja</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; width: 280px; margin: 0 auto; padding: 10px; color: #000; }}
        .center {{ text-align: center; }}
        .bold {{ font-weight: bold; }}
        hr {{ border: none; border-top: 1px dashed #000; margin: 8px 0; }}
        .fila {{ display: flex; justify-content: space-between; font-size: 13px; margin: 4px 0; }}
    </style>
</head>
<body>
    <div class="center bold" style="font-size: 16px;">BAR CONTROL PRO</div>
    <div class="center bold" style="font-size: 14px;">CIERRE DE CAJA</div>
    <div class="center" style="font-size: 12px;">{turno_sel}</div>
    <hr>
    <div style="font-size: 11px;"><b>Fecha Cierre:</b> {fecha_str}</div>
    <div style="font-size: 11px;"><b>Total Cant. Ventas:</b> {len(ventas_turno)}</div>
    <hr>
    <div class="fila"><span>💵 Efectivo:</span><span>${tot_efectivo:.2f}</span></div>
    <div class="fila"><span>📱 Trasnferencia:</span><span>${tot_mp:.2f}</span></div>
    <div class="fila"><span>💳 Tarjeta:</span><span>${tot_tarjeta:.2f}</span></div>
    <hr>
    <div class="fila bold" style="font-size: 15px;"><span>TOTAL GENERAL:</span><span>${tot_general:.2f}</span></div>
    <hr>
    <div class="center" style="font-size: 10px; margin-top: 25px;">
        __________________________________<br>
        Firma Responsable de Caja
    </div>
    <script>window.onload = function() {{ window.print(); }};</script>
</body>
</html>"""

        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(html_content)

        webbrowser.open(f"file://{path_absoluto}")

        self.refrescar_reporte_caja()


if __name__ == "__main__":
    login_app = LoginWindow()
    login_app.mainloop()