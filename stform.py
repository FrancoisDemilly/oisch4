import streamlit as st
import os
from PIL import Image
from PIL.ExifTags import TAGS
from exif import Image as ExifImage
import folium
from streamlit_folium import st_folium

image_name = './DSCN0027.jpg'

#open image with pillow to display it on the screen with streamlit
img_display = Image.open(image_name)


with open(image_name, 'rb') as image_file:
    my_image = ExifImage(image_file)

#tilte
st.title("Découverte de la Plateforme Collaborative Streamlit")
#Insérez une photographie

st.divider()
st.header("Insertion d'une photographie")
st.image(img_display, caption='Image avec géolocation')

#vérifions que l'image contient un fichier exif
#st.write(my_image.has_exif)

#https://exif.readthedocs.io/en/latest/api_reference.html#data-types


st.divider()
st.header("Génération du formulaire")
#https://docs.streamlit.io/library/advanced-features/forms

#liste des attributs exif du fichier
lst = my_image.list_all()

with st.form("my_form"):
    #https://stackoverflow.com/questions/76199659/how-access-form-data-as-dict-in-streamlit-app
    for item in lst:
        #impossible de modifier "exif_version"
        if item == "exif_version":
            pass
        elif type(my_image.get(item)) == str:
            st.text_input(f"Modifier la valeur **{my_image[item]}** du champ **{item}** du fichier Exif", key=f"{item}")
        elif type(my_image.get(item)) == tuple:
            st.text_input(f"Modifier la valeur **{my_image[item]}** du champ **{item}** du fichier Exif", key=f"{item}") 
    # Every form must have a submit button.  

    submitted = st.form_submit_button("Submit")
    if submitted:
        for key in st.session_state:   
            if st.session_state[key] != "":
                if key == 'gps_longitude':
                    #https://blender.stackexchange.com/questions/131827/converting-string-int-tuple-to-float-tuple
                    gps_long_string = st.session_state[key]
                    gps_long_tuple = tuple(float(s) for  s in gps_long_string.strip("()").split(','))
                    #st.write(gps_long_tuple)
                    my_image[key] = gps_long_tuple
                elif key == 'gps_latitude':
                    gps_lat_string = st.session_state[key]
                    gps_lat_tuple = tuple(float(s) for  s in gps_lat_string.strip("()").split(','))
                    my_image[key] = gps_lat_tuple
                elif key == 'gps_timestamp':
                    gps_ts_string = st.session_state[key]
                    gps_ts_tuple = tuple(float(s) for  s in gps_ts_string.strip("()").split(','))
                    my_image[key] = gps_ts_tuple
                else:
                    
                    my_image.set( key, st.session_state[key])
        #Save to jpg image
        with open(image_name, 'wb') as new_image_file:
            new_image_file.write(my_image.get_file())
        #reload 
        st.experimental_rerun()


st.divider()
st.header("Modification des données GPS et affichage sur une carte")
#les coordonnées d'Amiens 49°53'44.8"N 2°18'21.7"E
# où je vis actuellement 
#stocker les nouvelles coordonnées dans une variable 
#declare variable and obtain gps Exif data
gps_coord = []
lgd = my_image['gps_longitude_ref']
lg = my_image['gps_longitude']
ltd = my_image['gps_latitude_ref']
lt = my_image['gps_latitude']

#convert gsp degree, min, sec in decimal degree
lg = ((lg[0]+(lg[1]/60)+(lg[2]/3600))*(1 if lgd =="E" else -1))
lt = ((lt[0]+(lt[1]/60)+(lt[2]/3600))*(1 if ltd =="N" else -1))

#append it to the variable lat first
gps_coord.append(lt)
gps_coord.append(lg)





#pip install streamlit-folium
#montre les coordonnées gps de la photo
# center on photo coordonate add marker
if len(gps_coord) > 1:
    m = folium.Map(location=[gps_coord[0], gps_coord[1]], zoom_start=7)
    folium.Marker(
        [gps_coord[0], gps_coord[1]], popup="My Location", tooltip="My Location"
    ).add_to(m)

    # call to render Folium map in Streamlit
    st_data = st_folium(m, width=725)


######################
######################
st.divider()
st.header("POI joints entre eux")
#Montre les points de coordonnées des villes où j'ai habité ou voyagé 
#https://python-visualization.github.io/folium/modules.html#folium.vector_layers.PolyLine
#https://www.youtube.com/watch?v=j8tGVhaciNo
city_gps_coord = [
    ["Saint-Petersbourg", "Russie", 59.939471, 30.314830],
    ["Paris", "France", 48.848454, 2.389320],
    ["Reims", "France", 49.255609, 4.031833],
    ["Kosice", "Slovaquie", 48.709216, 21.245216],
    ["Toronto", "Canada", 43.668630, -79.371911],
    ["Niagara Falls", "Canada", 43.090529, -79.068036],
    ["Chicago", "USA", 41.877141, -87.631835],
    ["Boston", "USA",42.357648, -71.063403],
    ["New York", "USA", 40.748660, -73.985051],
    ["Washington DC", "USA", 38.898745, -77.036473],
    ["Miami", "USA", 25.782622, -80.128619],
    ["Clewiston", "USA", 26.753627, -80.934124],
    ["Pucallpa", "Pérou", -8.383819, -74.532945],
    ["Lima", "Pérou", -12.045526, -77.030263],
    ["La Valette", "Malte", 35.898395, 14.513701],
    ["Rome", "Italie", 41.890042, 12.492449],
    ["Seville", "Espagne", 37.382981, -5.990036]
]

#regrouper uniquement les coordonnées gps sour la forme de liste lat, long
points= []
for arr in city_gps_coord:
    points.append([arr[2], arr[3]])




mp = folium.Map(location=[44.346568, -32.937673], zoom_start=2)
for item in city_gps_coord:
    folium.Marker(
        [item[2], item[3]], popup=f"{item[0]}, {item[1]}", tooltip=f"{item[0]}, {item[1]}"
    ).add_to(mp)
#fournir la liste de point
folium.PolyLine(points , weight=2,
                popup=f"{item[0]}, {item[1]}", color= "red").add_to(mp)


# call to render Folium map in Streamlit
st_data_mp = st_folium(mp, width=725)






