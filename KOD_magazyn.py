import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Inicjalizacja połączenia z Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.title("📦 System Zarządzania Magazynem")

# --- FUNKCJE POMOCNICZE ---
def get_data(table_name):
    return supabase.table(table_name).select("*").execute()

# --- ZAKŁADKA: KATEGORIE ---
tab1, tab2 = st.tabs(["Kategorie", "Produkty"])

with tab1:
    st.header("Zarządzanie Kategoriami")
    
    # Dodawanie kategorii
    with st.expander("➕ Dodaj nową kategorię"):
        kat_nazwa = st.text_input("Nazwa kategorii")
        kat_opis = st.text_area("Opis")
        if st.button("Zapisz kategorię"):
            res = supabase.table("kategorie").insert({"nazwa": kat_nazwa, "opis": kat_opis}).execute()
            st.success("Dodano kategorię!")
            st.rerun()

    # Wyświetlanie i usuwanie
    kat_data = get_data("kategorie")
    if kat_data.data:
        df_kat = pd.DataFrame(kat_data.data)
        st.dataframe(df_kat, use_container_width=True)
        
        kat_to_delete = st.selectbox("Wybierz kategorię do usunięcia", options=df_kat['id'].tolist(), 
                                    format_func=lambda x: df_kat[df_kat['id'] == x]['nazwa'].values[0])
        if st.button("Usuń kategorię"):
            supabase.table("kategorie").delete().eq("id", kat_to_delete).execute()
            st.warning(f"Usunięto kategorię ID: {kat_to_delete}")
            st.rerun()

# --- ZAKŁADKA: PRODUKTY ---
with tab2:
    st.header("Zarządzanie Produktami")
    
    # Pobranie kategorii do selectboxa
    kat_list = get_data("kategorie").data
    kat_options = {k['nazwa']: k['id'] for k in kat_list} if kat_list else {}

    # Dodawanie produktu
    with st.expander("➕ Dodaj nowy produkt"):
        if not kat_options:
            st.error("Najpierw dodaj przynajmniej jedną kategorię!")
        else:
            p_nazwa = st.text_input("Nazwa produktu")
            p_liczba = st.number_input("Liczba", min_value=0, step=1)
            p_cena = st.number_input("Cena", min_value=0.0, format="%.2f")
            p_kat = st.selectbox("Kategoria", options=list(kat_options.keys()))
            
            if st.button("Zapisz produkt"):
                data = {
                    "nazwa": p_nazwa,
                    "liczba": p_liczba,
                    "cena": p_cena,
                    "kategoria_id": kat_options[p_kat]
                }
                supabase.table("produkty").insert(data).execute()
                st.success("Produkt dodany!")
                st.rerun()

    # Wyświetlanie i usuwanie
    prod_data = get_data("produkty")
    if prod_data.data:
        df_prod = pd.DataFrame(prod_data.data)
        st.dataframe(df_prod, use_container_width=True)
        
        prod_to_delete = st.selectbox("Wybierz produkt do usunięcia", options=df_prod['id'].tolist(),
                                     format_func=lambda x: df_prod[df_prod['id'] == x]['nazwa'].values[0])
        if st.button("Usuń produkt"):
            supabase.table("produkty").delete().eq("id", prod_to_delete).execute()
            st.warning(f"Usunięto produkt ID: {prod_to_delete}")
            st.rerun()
