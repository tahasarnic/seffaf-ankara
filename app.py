# Paketler
from cProfile import label
from turtle import width
import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import geopandas as gpd
import folium
import plotly.express as px

# Sayfa konfigürasyonu
st.set_page_config(layout="wide")

## DB
# Veri setleri
sosyal_yardim = pd.read_csv('data/stats/sosyal_yardim.csv')
sosyal = pd.read_csv('data/stats/sosyal.csv')
halk_ekmek = pd.read_csv('data/stats/halk_ekmek.csv')
kent_konsey = pd.read_csv('data/stats/kent_konsey.csv')
ulasim = pd.read_csv('data/stats/ulasim.csv')
demografik = pd.read_csv('data/stats/demografi.csv')
# Geojson
sosyal_yardim_geo = gpd.read_file('data/geojson/sosyal_yardim.json')
sosyal_geo = gpd.read_file('data/geojson/sosyal.json')
halk_ekmek_geo = gpd.read_file('data/geojson/halk_ekmek.json')
kent_konsey_geo = gpd.read_file('data/geojson/kent_konsey.json')
ulasim_geo = gpd.read_file('data/geojson/ulasim.json')
demografik_geo = gpd.read_file('data/geojson/demografi.json')


## Web app giriş
ank_col1, ank_col2, ank_col3 = st.columns([1,3,1])
with ank_col1:
    st.write("")
with ank_col2:
    st.image('img/ankara.png')
with ank_col3:
    st.write("")

#st.markdown("<h1 style='text-align: center; color: black; padding: 0px'>Şeffaf Ankara</h1>", unsafe_allow_html=True)

st.markdown("<br></br>", unsafe_allow_html = True)
st.markdown("<p style='text-align: left; color: black;'>Bu aplikasyonda kullanılan istatistiksel ve coğrafi verilerin tamamı <strong>Şeffaf Ankara</strong> web platformundan alınmıştır. Veriler için 👉 <a href='https://seffaf.ankara.bel.tr'>https://seffaf.ankara.bel.tr</a></p>", unsafe_allow_html=True)
st.markdown("## Proje Amacı")
st.markdown("Proje kapsamında Ankara Büyükşehir Belediyesi tarafından ilçe bazında yapılan sosyal yardımlar analiz edilecektir. Aplikasyonda bulunan filtreleme araçları kullanılarak, sosyal yardımlar ile belediyenin önemli noktaları ilçe ve mahalle seviyesidnde ilişkilendirilebilmektedir. Ayrıca, sosyal yardımlar bazında birbirine benzer ilçelerin de aplikasyonun son bölümünde incelenebilmektedir.")

## Haritalama
st.markdown('## Sosyal Yardımlar Analizi')

# Harialama düzeni
col1, col2 = st.columns([1, 3])

# Yardım türü seçimi
yardim_turu_dict = {'Toplam Yardım':'toplam_sosyal_yardim_10k',
                    'Gıda Yardımı':'gida_olumlu_10k',
                    'Kömür Yardımı':'komur_olumlu_10k',
                    'Giysi Yardımı':'giysi_olumlu_10k',
                    'Başkent Kart Yardımı':'baskent_kart_olumlu_10k',
                    'Süt Yardımı':'sut_olumlu_10k'}
with col1:
    yardim_turu = st.radio(label  = 'Yardım türü seçiniz:', options = ['Toplam Yardım', 'Gıda Yardımı', 'Kömür Yardımı', 'Giysi Yardımı', 'Başkent Kart Yardımı', 'Süt Yardımı'])

with col2:
    sosyal_yardim_geo = sosyal_yardim_geo.merge(sosyal_yardim, how = 'left', on = 'adi')
    m = folium.Map(location=[39.925018, 32.836956], zoom_start=8)
    my_map = folium.Choropleth(
    geo_data = sosyal_yardim_geo,
    name = 'choropleth',
    data = sosyal_yardim,
    bins = 8,
    columns = ['adi', yardim_turu_dict[yardim_turu]],
    key_on = 'feature.properties.adi',
    fill_color = 'YlGn',
    fill_opacity = 0.7,
    line_opacity = 0.2,
    highlight = True,
    legend_name = "10000 kişi başına düşen" + ' ' + yardim_turu.lower()
    ).add_to(m)
    my_map.geojson.add_child(folium.features.GeoJsonTooltip(
        fields=['adi', yardim_turu_dict[yardim_turu]],
        aliases=['İlçe: ', '10000 kişi başına düşen' + ' ' + yardim_turu.lower()],
        style=('background-color: grey; color: white;')
        ))
    folium.LayerControl().add_to(m)
    folium_static(m)

## Belediye Önemli Noktalar
st.markdown('## Belediye Önemli Noktalar')

# Seviye seçme
bel_1, bel_2 = st.columns([1, 3])

veriseti_dict = {'Sosyal':sosyal,
                'Halk Ekmek':halk_ekmek,
                'Kent Konseyi':kent_konsey,
                'Ulaşım':ulasim}

seviye_dict = {'İlçe':'ilce',
               'Mahalle':'mahalle'}

with bel_1:
    seviye = st.radio(label = 'Coğrafi seviye seçiniz:', options = ['İlçe', 'Mahalle'])
    hizmet = st.radio(label = 'Belediye hizmeti seçiniz:', options = ['Sosyal', 'Halk Ekmek', 'Kent Konseyi', 'Ulaşım'])

with bel_2:
    if seviye == 'İlçe':
        sosyal_df = veriseti_dict[hizmet]['ilce'].value_counts().to_frame().rename(columns = {'ilce':'sayi'}).reset_index().rename(columns = {'index':'ilce'}).merge(sosyal_yardim, how = 'left', on = 'ilce').loc[:,['sayi', 'adi', 'toplam_nufus']]
        sosyal_df['katsayi'] = sosyal_df['toplam_nufus'] / 100000
        sosyal_df['sayi_100k'] = round(sosyal_df['sayi'] / sosyal_df['katsayi'])
        m1 = folium.Map(location=[39.925018, 32.836956], zoom_start=8)
        my_map1 = folium.Choropleth(
            geo_data = sosyal_yardim_geo.merge(sosyal_df, on = 'adi', how = 'left'),
            name = 'choropleth',
            data = sosyal_df.merge(sosyal_yardim_geo, on = 'adi', how = 'right').loc[:, ['adi', 'sayi_100k']],
            bins = 8,
            columns = ['adi', 'sayi_100k'],
            key_on = 'feature.properties.adi',
            fill_color = 'YlGn',
            fill_opacity = 0.7,
            line_opacity = 0.2,
            highlight = True,
            legend_name = "100000 kişi başına düşen" + ' ' + hizmet.lower() + ' ile ilgili hizmetler sayısı'
        ).add_to(m1)
        my_map1.geojson.add_child(folium.features.GeoJsonTooltip(
                fields=['adi', 'sayi_100k'],
                aliases=['İlçe: ', '100000 kişi başına düşen' + ' ' + hizmet.lower() + ' ile ilgili hizmetler sayısı'],
                style=('background-color: grey; color: white;')
                ))
        folium.LayerControl().add_to(m1)
        folium_static(m1)
    else:
        dff = veriseti_dict[hizmet].groupby(['ilce'])['mahalle'].value_counts().to_frame().rename(columns = {'mahalle':'sayi'}).reset_index().merge(demografik, how = 'left', on = ['ilce', 'mahalle'])
        dff['katsayi'] = dff['toplam_nufus'] / 100000
        dff['sayi_100k'] = round(dff['sayi'] / dff['katsayi'])
        m2 = folium.Map(location=[39.925018, 32.836956], zoom_start=8)
        my_map2 = folium.Choropleth(
            geo_data = demografik_geo.merge(dff, on = ['ilce', 'mahalle'], how = 'left'),
            name = 'choropleth',
            data = dff.merge(demografik_geo, on = ['ilce', 'mahalle'], how = 'right').loc[:, ['mahalle', 'sayi_100k']],
            bins = 8,
            columns = ['mahalle', 'sayi_100k'],
            key_on = 'feature.properties.mahalle',
            fill_color = 'YlGn',
            fill_opacity = 0.7,
            line_opacity = 0.2,
            highlight = True,
            legend_name = "100000 kişi başına düşen" + ' ' + hizmet.lower() + ' ile ilgili hizmetler sayısı'
            ).add_to(m2)

        my_map2.geojson.add_child(folium.features.GeoJsonTooltip(
            fields=['mahalle', 'sayi_100k'],
            aliases=['Mahalle: ', '100000 kişi başına düşen' + ' ' + hizmet.lower() + ' ile ilgili hizmetler sayısı'],
            style=('background-color: grey; color: white;')
            ))

        folium.LayerControl().add_to(m2)
        folium_static(m2)

## Kümeleme Analizi
st.markdown('## Sosyal Yardımlar Kümeleme Analizi')
st.markdown('Gıda, kömür, ekmek, giysi, Başkent Kart ve süt yardımları baz alınıp **K-means Kümeleme** algoritması ile gözetimsiz yapay öğrenme modeli kurulmuştur. Küme-içi varyasyonlara göre optimal küme sayısı 5 olarak bulunmuştur.')
st.markdown("<p style='text-align: left; color: black;'> K-means Kümeleme algoritması için 👉 <a href='https://tr.wikipedia.org/wiki/K-means_kümeleme'>https://tr.wikipedia.org/wiki/K-means_kümeleme</a></p>", unsafe_allow_html=True)
kume_1, kume_2 = st.columns([1, 3])

kume_dict = {'Toplam Nüfus':'toplam_nufus',
             'Gıda Yardımı (10 bin kişi başına)':'gida_olumlu_10k',
             'Kömür Yardımı (10 bin kişi başına)':'komur_olumlu_10k',
             'Ekmek Yardımı (10 bin kişi başına)':'ekmek_olumlu_10k',
             'Giysi Yardımı (10 bin kişi başına)':'giysi_olumlu_10k',
             'Başkent Kart (10 Bin kişi başına)':'baskent_kart_olumlu_10k',
             'Süt Yardımı (10 Bin kişi başına)':'sut_olumlu_10k'}

with kume_1:
    x_ekseni = st.radio(label = 'X ekseni parametresini seçiniz:', options = ['Toplam Nüfus', 'Gıda Yardımı (10 bin kişi başına)', 'Kömür Yardımı (10 bin kişi başına)', 'Ekmek Yardımı (10 bin kişi başına)', 'Giysi Yardımı (10 bin kişi başına)', 'Başkent Kart (10 Bin kişi başına)', 'Süt Yardımı (10 Bin kişi başına)'])
    y_ekseni = st.radio(label = 'Y ekseni parametresini seçiniz:', options = ['Toplam Nüfus', 'Gıda Yardımı (10 bin kişi başına)', 'Kömür Yardımı (10 bin kişi başına)', 'Ekmek Yardımı (10 bin kişi başına)', 'Giysi Yardımı (10 bin kişi başına)', 'Başkent Kart (10 Bin kişi başına)', 'Süt Yardımı (10 Bin kişi başına)'], index = 1)

with kume_2:
    fig = px.scatter(x = kume_dict[x_ekseni], y = kume_dict[y_ekseni], color = 'Küme', data_frame = sosyal_yardim,
                category_orders = {'Küme':['Küme 1', 'Küme 2', 'Küme 3', 'Küme 4', 'Küme 5']},
                hover_name = 'adi',
                size = 'toplam_sosyal_yardim_10k',
                labels={
                     kume_dict[x_ekseni]: x_ekseni,
                     kume_dict[y_ekseni]: y_ekseni,
                     'toplam_sosyal_yardim_10k':'Toplam Sosyal Yardım (10 bin kişi başına)'
                 })
    st.plotly_chart(fig)
    st.markdown("**Yorum:** 10 bin kişi başına düşen en çok yardımların **Haymana** ilçesine yapıldığını ve diğer ilçelerden ayrışıp tek başına bir küme oluşturduğunu görebiliriz. Ayrıca **Küme 5'te** bulunan **Çubuk** ve **Akyurt** ilçelerine yapılan yardımların düşük nüfuslarına rağmen, **Sincan, Mamak ve Keçiören'e** göre 10 bin kişi başına düşen yardım sayılarının birbirine benzer olduğunu söyleyebiliriz.")
