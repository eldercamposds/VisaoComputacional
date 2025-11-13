import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import plotly.graph_objects as go

def detectar_verde(imagem):
    imagem_np = np.array(imagem)
    imagem_bgr = cv2.cvtColor(imagem_np, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2HSV)
    verde_baixo = np.array([35, 40, 40])
    verde_alto = np.array([85, 255, 255])
    mascara_verde = cv2.inRange(hsv, verde_baixo, verde_alto)
    resultado = cv2.bitwise_and(imagem_bgr, imagem_bgr, mask=mascara_verde)
    resultado_rgb = cv2.cvtColor(resultado, cv2.COLOR_BGR2RGB)
    porcentagem_verde = np.sum(mascara_verde > 0) / mascara_verde.size * 100
    return resultado_rgb, porcentagem_verde

def main():
    st.title("🌿 Comparador de Áreas Verdes em Imagens de Satélite")
    st.write("Faça upload de duas imagens de satélite para comparar a quantidade de verde.")

    col1, col2 = st.columns(2)
    with col1:
        imagem1 = st.file_uploader("Imagem 1", type=["jpg", "jpeg", "png"], key="img1")
    with col2:
        imagem2 = st.file_uploader("Imagem 2", type=["jpg", "jpeg", "png"], key="img2")

    if imagem1 and imagem2:
        img1 = Image.open(imagem1).convert("RGB")
        img2 = Image.open(imagem2).convert("RGB")

        verde1, pct1 = detectar_verde(img1)
        verde2, pct2 = detectar_verde(img2)

        


        # st.subheader("📊 Resultados")
        # st.write(f"**Imagem 1:** {pct1:.2f}% de área verde")
        # st.image(img1, caption="Imagem 1 Original", width='stretch')
        # st.image(verde1, caption="Imagem 1 - Áreas Verdes", width='stretch')

        # st.write(f"**Imagem 2:** {pct2:.2f}% de área verde")
        # st.image(img2, caption="Imagem 2 Original", width='stretch')
        # st.image(verde2, caption="Imagem 2 - Áreas Verdes", width='stretch')
        

        st.markdown("---")
        st.write("🔍 Comparação lado a lado:")
        col3, col4 = st.columns(2)
        with col3:
            st.image(img1, caption="Imagem 1 Original", width='stretch')
            st.image(img2, caption="Imagem 2 Original", width='stretch')
            
        with col4:
            st.image(verde1, caption=f"Imagem 1 Verde ({pct1:.2f}%)", width='stretch')
            st.image(verde2, caption=f"Imagem 2 Verde ({pct2:.2f}%)", width='stretch')

        dados =  {
            "Imagens": ["Imagem1", "Imagem2"],
            "Comparação": [pct1, pct2]
        }

        
        df = pd.DataFrame(dados)

        st.title("Comparação entre imagens")
        st.bar_chart(df.set_index("Imagens"))

        st.title("Gráfico de Rosca imagem 1")
        label_imagem1 = ["area total", "area verde"] 
        valores_imagem1 = [100-pct1, pct1]

        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5)])

if __name__ == "__main__":
    main()
