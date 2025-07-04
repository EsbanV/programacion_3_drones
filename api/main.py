# api/main.py

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import os
import sys

# Carga los módulos del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tda.avl import AVL
from tda.hash_map import Map
from domain.client import Client
from domain.order import Order
from visual.report_generator import ReportGenerator

import pickle

app = FastAPI(title="Drone Logistics API")

# Permite acceso desde tu frontend si fuese necesario (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ Estado global de la simulación ------------------
# Usa archivos pickle para "persistir" el estado cuando cambia el dashboard.
# Lo ideal sería tener un módulo de "estado compartido" real (singleton), pero así funciona simple para pruebas locales.
STATE_FILE = "api_sim_state.pickle"
PDF_PATH = "reporte.pdf"

def save_state(state: dict):
    with open(STATE_FILE, "wb") as f:
        pickle.dump(state, f)

def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, "rb") as f:
        return pickle.load(f)

def sim_ready(state):
    # Hay simulación si están los campos esenciales
    required = ["clients", "orders", "routes_avl", "node_visits", "node_roles"]
    return all(k in state for k in required)

# ----------------- ENDPOINTS -----------------

@app.get("/clients/", response_model=List[dict])
def get_clients():
    state = load_state()
    if not sim_ready(state):
        raise HTTPException(status_code=400, detail="No simulation active.")
    return [c.to_dict() for c in state["clients"]]

@app.get("/clients/{client_id}", response_model=dict)
def get_client(client_id: str):
    state = load_state()
    if not sim_ready(state):
        raise HTTPException(status_code=400, detail="No simulation active.")
    client = next((c for c in state["clients"] if c.client_id == client_id), None)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found.")
    return client.to_dict()

@app.get("/orders/", response_model=List[dict])
def get_orders():
    state = load_state()
    if not sim_ready(state):
        raise HTTPException(status_code=400, detail="No simulation active.")
    return [o.to_dict() for o in state["orders"]]

@app.get("/orders/{order_id}", response_model=dict)
def get_order(order_id: str):
    state = load_state()
    if not sim_ready(state):
        raise HTTPException(status_code=400, detail="No simulation active.")
    order = next((o for o in state["orders"] if o.order_id == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    return order.to_dict()

@app.post("/orders/{order_id}/cancel")
def cancel_order(order_id: str):
    state = load_state()
    if not sim_ready(state):
        raise HTTPException(status_code=400, detail="No simulation active.")
    for o in state["orders"]:
        if o.order_id == order_id and o.status in ("pending", "in_progress"):
            o.status = "cancelled"
            save_state(state)
            return {"status": "cancelled", "order_id": order_id}
    raise HTTPException(status_code=400, detail="Order not cancelable or not found.")

@app.post("/orders/{order_id}/complete")
def complete_order(order_id: str):
    state = load_state()
    if not sim_ready(state):
        raise HTTPException(status_code=400, detail="No simulation active.")
    for o in state["orders"]:
        if o.order_id == order_id and o.status in ("pending", "in_progress"):
            o.status = "completed"
            save_state(state)
            return {"status": "completed", "order_id": order_id}
    raise HTTPException(status_code=400, detail="Order not completable or not found.")

@app.get("/reports/pdf")
def get_pdf_report():
    if not os.path.exists(PDF_PATH):
        raise HTTPException(status_code=400, detail="No PDF available. Run simulation and generate report.")
    return FileResponse(PDF_PATH, media_type='application/pdf', filename="reporte.pdf")

@app.get("/info/reports/visits/clients")
def visits_clients():
    state = load_state()
    if not sim_ready(state):
        raise HTTPException(status_code=400, detail="No simulation active.")
    node_roles = state["node_roles"]
    visits = state["node_visits"]

    result = []
    for n in visits.keys():
        n_str = str(n)
        try:
            if node_roles.get(n_str) == "client" and visits[n_str] is not None:
                result.append([n_str, visits[n_str]])
        except Exception:
            continue  # Ignora cualquier KeyError u otro error puntual
    return {"clients": sorted(result, key=lambda x: -x[1])}

@app.get("/info/reports/visits/recharges")
def visits_recharges():
    state = load_state()
    if not sim_ready(state):
        raise HTTPException(status_code=400, detail="No simulation active.")
    node_roles = state["node_roles"]
    visits = state["node_visits"]

    result = []
    for n in visits.keys():
        n_str = str(n)
        try:
            if node_roles.get(n_str) == "recharge" and visits[n_str] is not None:
                result.append([n_str, visits[n_str]])
        except Exception:
            continue
    return {"recharges": sorted(result, key=lambda x: -x[1])}

@app.get("/info/reports/visits/storages")
def visits_storages():
    state = load_state()
    if not sim_ready(state):
        raise HTTPException(status_code=400, detail="No simulation active.")
    node_roles = state["node_roles"]
    visits = state["node_visits"]

    result = []
    for n in visits.keys():
        n_str = str(n)
        try:
            if node_roles.get(n_str) == "storage" and visits[n_str] is not None:
                result.append([n_str, visits[n_str]])
        except Exception:
            continue
    return {"storages": sorted(result, key=lambda x: -x[1])}

@app.get("/info/reports/summary")
def summary():
    state = load_state()
    if not sim_ready(state):
        raise HTTPException(status_code=400, detail="No simulation active.")
    # Puedes personalizar los campos a exponer
    return {
        "n_nodes": state.get("n_nodes"),
        "m_edges": state.get("m_edges"),
        "n_orders": state.get("n_orders"),
        "clients": len(state["clients"]),
        "routes_registradas": len(state["routes_avl"].in_order())
    }

# ------------- Método para sincronizar el estado desde Streamlit (llámalo desde dashboard.py) -------------

def sync_state_from_streamlit():
    """Guarda el estado actual desde Streamlit para que lo lea la API."""
    import streamlit as st
    state = {
        "clients": st.session_state.get("clients", []),
        "orders": st.session_state.get("orders", []),
        "routes_avl": st.session_state.get("routes_avl", AVL()),
        "node_visits": st.session_state.get("node_visits", Map()),
        "node_roles": {str(k): v for k, v in st.session_state.get("node_roles", {}).items()},
        "n_nodes": st.session_state.get("n_nodes", 0),
        "m_edges": st.session_state.get("m_edges", 0),
        "n_orders": st.session_state.get("n_orders", 0),
    }
    save_state(state)

# ------------------ FIN ------------------

# Para correr:
# uvicorn api.main:app --reload

