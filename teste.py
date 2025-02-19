import streamlit as st
import folium
import geopandas as gpd
from streamlit_folium import st_folium
from cores import color_mapping

# Carregar dados
entry_file = st.sidebar.file_uploader('Selecione um arquivo de carbono')

entry_desmat = st.sidebar.file_uploader('Selecione um arquivo de desmatamento')

if entry_file and entry_desmat:


    def load_ano():
        soja = gpd.read_parquet(entry_file)
        return soja

    df = load_ano()

    def load_desmat():
        desmat = gpd.read_parquet(entry_desmat)
        return desmat

    dfd = load_desmat()

    
    # Configuração da página
    st.title("📊 Monitoramento de Carbono")

    # Filtro por ano
    years = sorted(df['ano'].unique())

    selected_year = st.sidebar.slider("Selecione o ano", min_value=min(years), max_value=max(years), value=max(years))
    #selected_year = st.sidebar.selectbox("Selecione o ano", years, index=len(years)-1)
    filtered_df = df[df['ano'] == selected_year]

    # Criar mapa
    m = folium.Map(location=[-15.0, -52.0], zoom_start=5,control_scale=True,tiles='Esri World Imagery')

    filtered_df['intervalo'] = filtered_df['val'].apply(lambda x: 'baixo' if 0 <= x <= 10 else
                                        'medio' if 11 <= x <= 20 else
                                        'alto' if 21 <= x <= 35 else
                                        'muito alto')

    def style_function_entrada(feature):
        """Define a cor e estilo de preenchimento com base na classe da feição."""
        classe = feature.get('properties', {}).get('intervalo', '')
        
        return {
            'fillColor': color_mapping.get(classe, (0, 0, 0, 255)),
            'color': 'red',
            'weight': 0,
            'fillOpacity': 0.6
            }

    folium.GeoJson(
        filtered_df,
        style_function=style_function_entrada,
        tooltip=folium.features.GeoJsonTooltip(
        fields=['val'],  # Display the 'val' column in the tooltip
        aliases=['t/ha: '],  # Label for the tooltip
        localize=True)
        ).add_to(m)

    bounds = df.total_bounds
    # Ajusto o mapa para os limites de geometria
    m.fit_bounds([[bounds[1],bounds[0]],[bounds[3],bounds[2]]])
    # Adiciona os controle de camadas no mapa
    folium.LayerControl().add_to(m)

    # Exibir mapa
    st_folium(m,width="100%")

    col_1,col_2,col_3 = st.columns(3)

    with col_2:
        st.subheader("📈 Estatísticas de Uso do Solo")

    total_area = df[df['ano'] == selected_year]['area'].sum()

    total_desmat = dfd[dfd['ano'] == selected_year]['st_area_ha'].sum()

    col1,col2 = st.columns(2)
    with col1:
        # Display the metric for the selected year
        st.metric(label=f"Toneladas de CO2 equivalente no solo ({selected_year})", value=f"{total_area:,}")

        # Gráfico de evolução
        evolucao = df.groupby('ano')[['area']].sum().reset_index()

        # Set 'ano' as the index for proper time series plotting
        evolucao.set_index('ano', inplace=True)

        # Plot time series
        st.line_chart(evolucao)

    with col2:
        # Display the metric for the selected year
        st.metric(label=f"Desmatamento ({selected_year})", value=f"{total_desmat:,}")

        # Gráfico de evolução
        evolucao_desmat = dfd.groupby('ano')[['st_area_ha']].sum().reset_index()

        # Set 'ano' as the index for proper time series plotting
        evolucao_desmat.set_index('ano', inplace=True)

        # Plot time series
        st.line_chart(evolucao_desmat)

    st.sidebar.subheader(total_area/total_desmat)
else:
    st.warning('Suba um arquivo para iniciar')