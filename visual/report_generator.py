from fpdf import FPDF
import matplotlib.pyplot as plt
import io
import tempfile
import os
from sim.utils import safe_str

class ReportGenerator:
    def __init__(self, system_stats, orders, clients, routes, node_visit_stats, role_counts, node_roles):
        self.system_stats = system_stats
        self.orders = orders
        self.clients = clients
        self.routes = routes
        self.node_visit_stats = node_visit_stats
        self.role_counts = role_counts
        self.node_roles = node_roles

    def _make_role_visits(self, role_name, bar_color, title):
        items = [
            (safe_str(n), v)
            for n, v in self.node_visit_stats.items()
            if self.node_roles.get(str(n)) == role_name
        ]
        items = sorted(items, key=lambda x: x[1], reverse=True)[:10]
        if not items:
            return None
        nodes = [k for k, _ in items]
        visits = [v for _, v in items]
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.bar(nodes, visits, color=bar_color)
        ax.set_xlabel("Nodo")
        ax.set_ylabel("Visitas")
        ax.set_title(safe_str(title))
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            tmpfile.write(buf.getbuffer())
            tmpfile.flush()
            tmpfile_path = tmpfile.name
        buf.close()
        return tmpfile_path

    def generate_pdf(self, filename="reporte.pdf"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 12, safe_str("Reporte General - Sistema de Drones"), ln=1, align="C")
        pdf.ln(3)
        pdf.set_font("Arial", "", 12)

        # 1. Estadísticas Generales
        pdf.cell(0, 10, safe_str("Estadisticas generales"), ln=1)
        for key, value in self.system_stats.items():
            pdf.cell(0, 8, safe_str(f"{key}: {value}"), ln=1)
        pdf.ln(4)

        # 2. Rutas más frecuentes
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, safe_str("Rutas mas frecuentes"), ln=1)
        pdf.set_font("Arial", "", 12)
        for idx, (ruta, freq) in enumerate(self.routes[:10], 1):
            pdf.cell(0, 8, safe_str(f"{idx}. {ruta}  (Frecuencia: {freq})"), ln=1)
        pdf.ln(4)

        # 3. Clientes con más pedidos
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, safe_str("Clientes mas recurrentes"), ln=1)
        pdf.set_font("Arial", "", 12)
        top_clients = sorted(self.clients, key=lambda c: getattr(c, "total_orders", 0), reverse=True)[:10]
        for c in top_clients:
            name = safe_str(getattr(c, "name", ""))
            client_id = safe_str(getattr(c, "client_id", ""))
            total_orders = getattr(c, "total_orders", 0)
            pdf.cell(0, 8, safe_str(f"{name} (ID: {client_id}) - Pedidos: {total_orders}"), ln=1)
        pdf.ln(4)

        # 4. Ranking de nodos más utilizados
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, safe_str("Nodos mas utilizados"), ln=1)
        pdf.set_font("Arial", "", 12)
        sorted_visits = sorted(self.node_visit_stats.items(), key=lambda x: x[1], reverse=True)
        for idx, (node, visits) in enumerate(sorted_visits[:10], 1):
            pdf.cell(0, 8, safe_str(f"{idx}. Nodo {node} - Visitas: {visits}"), ln=1)
        pdf.ln(4)

        # 5. Tabla de pedidos recientes
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, safe_str("Ordenes recientes"), ln=1)
        pdf.set_font("Arial", "", 10)
        pdf.cell(40, 8, safe_str("ID"), 1)
        pdf.cell(30, 8, safe_str("Cliente"), 1)
        pdf.cell(25, 8, safe_str("Origen"), 1)
        pdf.cell(25, 8, safe_str("Destino"), 1)
        pdf.cell(25, 8, safe_str("Estado"), 1, ln=1)
        for order in self.orders[:15]:
            d = order.to_dict() if hasattr(order, "to_dict") else order
            pdf.cell(40, 8, safe_str(str(d.get("order_id", ""))), 1)
            pdf.cell(30, 8, safe_str(str(d.get("client", ""))), 1)
            pdf.cell(25, 8, safe_str(str(d.get("origin", ""))), 1)
            pdf.cell(25, 8, safe_str(str(d.get("destination", ""))), 1)
            pdf.cell(25, 8, safe_str(str(d.get("status", ""))), 1, ln=1)

        # 6.1 Gráfico de barras: Nodos más visitados
        tempfiles = []
        if self.node_visit_stats:
            fig, ax = plt.subplots(figsize=(7, 3.2))
            items = sorted(self.node_visit_stats.items(), key=lambda x: x[1], reverse=True)[:10]
            nodes = [safe_str(str(k)) for k, _ in items]
            visits = [v for _, v in items]
            ax.bar(nodes, visits, color="steelblue")
            ax.set_xlabel(safe_str("Nodo"))
            ax.set_ylabel(safe_str("Visitas"))
            ax.set_title(safe_str("Top 10 nodos mas visitados"))
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            plt.close(fig)
            buf.seek(0)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
                tmpfile.write(buf.getbuffer())
                tmpfile.flush()
                tmpfile_path = tmpfile.name
            tempfiles.append(tmpfile_path)
            buf.close()
            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, safe_str("Grafico de barras: Nodos mas visitados"), ln=1)
            pdf.image(tmpfile_path, x=10, y=30, w=180)

        # 6.2 Gráfico de torta: Proporción de roles
        if self.role_counts:
            labels = []
            values = []
            colors = []
            role_color_map = {"storage": "orange", "recharge": "green", "client": "skyblue"}
            for k in ["storage", "recharge", "client"]:
                v = self.role_counts.get(k, 0)
                if v > 0:
                    labels.append(safe_str(k.capitalize()))
                    values.append(v)
                    colors.append(role_color_map.get(k, "gray"))
            if sum(values) > 0:
                fig2, ax2 = plt.subplots(figsize=(4.2, 4.2))
                ax2.pie(values, labels=labels, autopct="%1.1f%%", startangle=90, colors=colors)
                ax2.set_title(safe_str("Proporcion de nodos por rol"))
                buf2 = io.BytesIO()
                plt.savefig(buf2, format="png")
                plt.close(fig2)
                buf2.seek(0)
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
                    tmpfile.write(buf2.getbuffer())
                    tmpfile.flush()
                    tmpfile_path = tmpfile.name
                tempfiles.append(tmpfile_path)
                buf2.close()
                pdf.add_page()
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, safe_str("Grafico de torta: Proporcion de nodos"), ln=1)
                pdf.image(tmpfile_path, x=35, y=40, w=130)

        # 6.3 Gráficos de barras por tipo de nodo
        buf_client = self._make_role_visits("client", "skyblue", "Top 10 Clientes mas visitados")
        if buf_client:
            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, safe_str("Grafico de barras: Clientes mas visitados"), ln=1)
            pdf.image(buf_client, x=10, y=30, w=180)
            tempfiles.append(buf_client)
        buf_recharge = self._make_role_visits("recharge", "mediumseagreen", "Top 10 Estaciones de recarga mas visitadas")
        if buf_recharge:
            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, safe_str("Grafico de barras: Estaciones de recarga mas visitadas"), ln=1)
            pdf.image(buf_recharge, x=10, y=30, w=180)
            tempfiles.append(buf_recharge)
        buf_storage = self._make_role_visits("storage", "orange", "Top 10 Almacenes mas visitados")
        if buf_storage:
            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, safe_str("Grafico de barras: Almacenes mas visitados"), ln=1)
            pdf.image(buf_storage, x=10, y=30, w=180)
            tempfiles.append(buf_storage)

        pdf.output(filename)

        # Limpia los archivos temporales
        for tmpfile in tempfiles:
            try:
                os.remove(tmpfile)
            except Exception:
                pass

        return filename

# Ejemplo de uso:
# generator = ReportGenerator(stats, orders, clients, routes, node_visit_stats, role_counts, node_roles)
# generator.generate_pdf("reporte.pdf")
