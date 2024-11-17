import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account

import json
key_dict = json.loads(st.secrets["texkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="products-project-9fcf3")
# dbName = db.collection("products")

def load_products():
    dbName = db.collection("products")
    docs = dbName.stream()
    data = []
    for doc in docs:
        doc_dict = doc.to_dict()  # Convierte el documento en un diccionario
        # doc_dict["id"] = doc.id  # Agrega el ID del documento (opcional)
        data.append(doc_dict)
        df = pd.DataFrame(data) 
    return df

def loadByName(name):
    dbName = db.collection("products")
    names_ref = dbName.where(u'nombre', u'==',name)
    currentName = None
    for myname in names_ref.stream():
        currentName = myname
    
    return currentName

@st.cache_data
def load_name(data,name):
    filtered_name = data[data['nombre'].str.contains(name, case=False)]
    return filtered_name

st.header("Productos")
sidebar = st.sidebar
sidebar.header('Mantenimiento')
data = load_products()

selected_option = sidebar.radio("Seleccione una opcion", ('Busqueda','Crear','Actualizar','Eliminar'))

if selected_option == 'Busqueda':
    nameSearch = st.text_input("Nombre Producto")
    btnFilter = st.button("Buscar")
    if btnFilter:
        data = load_name(data,nameSearch)

elif selected_option == 'Crear':
    #creacion del producto
    mcodigo = st.text_input("codigo")
    mnombre = st.text_input("nombre")
    mprecio = st.text_input("precio")
    mexistencias = st.text_input("existencias")
    msminimo = st.text_input("stock_minimo")
    msmaximo = st.text_input("stock_maximo")

    submit_crear = st.button("Crear")
    if mcodigo and mnombre and mprecio and mexistencias and msminimo and msmaximo and submit_crear:
        doc_ref = db.collection("products").document(mnombre)
        doc_ref.set({
            "codigo" : mcodigo,
            "nombre" : mnombre,
            "precio" : float(mprecio),
            "existencias" : mexistencias,
            "stock_minimo" : msminimo,
            "stock_maximo" : msmaximo
        })
        data = load_products()
elif selected_option == 'Actualizar':
    mnombre = st.text_input("nombre")
    mprecio = st.text_input("precio")
    mexistencias = st.text_input("existencias")
    msminimo = st.text_input("stock_minimo")
    msmaximo = st.text_input("stock_maximo")

    submit_update = st.button("Actualizar")
    if  mnombre and mprecio and mexistencias and msminimo and msmaximo and submit_update:
        updatename = loadByName(mnombre)
        if updatename is None:
            st.write(f"{mnombre} no existe")
        else:
            dbName = db.collection("products")
            myupdatename = dbName.document(updatename.id)
            myupdatename.update({
                "precio" : float(mprecio),
                "existencias" : mexistencias,
                "stock_minimo" : msminimo,
                "stock_maximo" : msmaximo
            })
            st.write(f"{mnombre} actualizado")
            data = load_products()
elif selected_option == 'Eliminar':
    mnombre = st.text_input("nombre")
    submit_eliminar = st.button("Eliminar")
    if  mnombre and submit_eliminar:
        deletename = loadByName(mnombre)
        if deletename is None:
            st.write(f"{mnombre} no existe")
        else:
            dbName = db.collection("products")
            dbName.document(deletename.id).delete()
            st.write(f"{mnombre} eliminado")
            data = load_products()





st.markdown("____")
# lectura de todos los registros


if data.empty:
    st.write("No hay datos")
else:
    st.dataframe(data)