# *******************************************************/
# Nom ......... : ex42streamlit.py
# Rôle ........ : Création d'une page HTML avec Streamlit
#				  Lecture et modification de données EXIF d'une photo
#				  Ajout de carte interactive Folium
# Auteur ...... : David Boivin
# Version ..... : V1 du 09/06/2024
# Licence ..... : réalisé dans le cadre du cours OC
# 
# Usage : streamlit run ex42streamlit.py
#********************************************************/


import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from exif import Image as ExifImage

# types de quelques données EXIF
EXIF_TAGS = {
    'make' : 'str' ,
    'model' : 'str' ,
    'datetime_original' : 'str' ,
    'exposure_time' : 'float' ,
	'f_number' : 'float' ,
    'brightness_value' : 'float' ,
    'focal_length' : 'float' ,
    'pixel_x_dimension' : 'int' ,
    'pixel_y_dimension' : 'int'}


# coefficient multiplicateur pour lal latitude et la longitude
gps_ref = {'N' : 1, 'S' : -1, 'W' : -1, 'E' : 1}
new_tags = {}
tags = {}

# nom du fichier image
image_path = 'home.jpg'

#
# Définition de fonctions de conversion d'angle
#
# conversion (degré,minute,seconde) -> degrés décimaux
def convert_DMS2DD(angle):
	if angle is None:
		return None
	else:
		return angle[0] + angle[1]/60 + angle[2]/3600

# conversion degrés décimaux -> (degré,minute,seconde)
def convert_DD2DMS(angle):
	dd = float(angle)
	d = int(dd)
	m_tmp = (dd - d) * 60
	m = int(m_tmp)
	s = (m_tmp - m) * 60
	return (d,m,s)

#
# PROGRAMME PRINCIPAL
#
# ouverture photo	
with open(image_path, 'rb') as img_file:
	img = ExifImage(img_file)
	
	# récupération des tags
	for tag in EXIF_TAGS.keys(): # on aurait pu utiliser tous les tags avec img.all_tags()
		value =  img.get(tag)

		tags[tag] = value
		new_tags[tag] = str(value)
		new_gps_lat = gps_lat = convert_DMS2DD(img.get('gps_latitude'))
		new_gps_lat_ref = gps_lat_ref = img.get('gps_latitude_ref')
		new_gps_lon = gps_lon = convert_DMS2DD(img.get('gps_longitude'))
		new_gps_lon_ref = gps_lon_ref = img.get('gps_longitude_ref')
		new_gps_alt = gps_alt = img.get('gps_altitude')


st.title("La photo et ses données EXIF")

## affichage image sur la page
st.image(image_path, caption='Photo')

## affichage des tags et input pour modification
for tag in EXIF_TAGS.keys():
	new_tags[tag] = st.text_input(tag+' ('+EXIF_TAGS[tag]+') : '+str(tags[tag]), value=tags[tag])
new_gps_lat = st.text_input('gps_latitude (float) : '+str(gps_lat), value=gps_lat)
new_gps_lat_ref = st.text_input('gps_latitude_ref (str) : '+str(gps_lat_ref), value=gps_lat_ref)
new_gps_lon = st.text_input('gps_longitude (float) : '+str(gps_lon), value=gps_lon)
new_gps_lon_ref = st.text_input('gps_longitude_ref (str) : '+str(gps_lon_ref), value=gps_lon_ref)
new_gps_alt = st.text_input('gps_altitude (float) ; '+str(gps_alt), value=gps_alt)

## Bouton 'Enregistrer' : écriture des tags      
if st.button('Enregistrer'):
	for tag in EXIF_TAGS.keys():
		if new_tags[tag] is not None:
			if EXIF_TAGS[tag] == 'float':
				tags[tag] = float(new_tags[tag])
				img.set(tag,float(new_tags[tag])) 
			elif EXIF_TAGS[tag] == 'int':
				tags[tag] = int(new_tags[tag])
				img.set(tag,int(new_tags[tag])) 
			elif EXIF_TAGS[tag] == 'str':
				tags[tag] = new_tags[tag]
				img.set(tag,new_tags[tag]) 
	if new_gps_lat is not None:
		img.set('gps_latitude',convert_DD2DMS(new_gps_lat))
	if new_gps_lat_ref is not None:
		img.set('gps_latitude_ref',new_gps_lat_ref)
	if new_gps_lon is not None:
		img.set('gps_longitude',convert_DD2DMS(new_gps_lon))
	if new_gps_lon_ref is not None:
		img.set('gps_longitude_ref',new_gps_lon_ref)
	if new_gps_alt is not None:
		img.set('gps_altitude',float(new_gps_alt))
	# Enregistrement image avec nouveaux tags	
	with open(image_path, 'wb') as new_image_file:
		new_image_file.write(img.get_file())

	# rafraichissement de la page
	st.rerun()


## LA CARTE AVEC LOCALISATION (coord GPS EXIF)
lst_lat = [gps_lat*gps_ref[gps_lat_ref]]
lst_lon = [gps_lon*gps_ref[gps_lon_ref]]

data = pd.DataFrame({
    'latitude': lst_lat,
    'longitude': lst_lon
})

st.title("Localisation de la photo")
st.write("(d'après les coordonnées GPS)")

# création carte avec localisation coord GPS EXIF
st.map(data, zoom=4.5)


## LES VILLES VISITÉES
st.title("Les capitales visitées")

# récupération des informations (nom de ville et coord GPS
# depuis fichier CSV
lieux_df = pd.read_csv("villes.csv",usecols=['Ville', 'Latitude', 'Longitude'])

# affichage du tableau des villes
st.table(lieux_df)

locations = lieux_df[['Latitude', 'Longitude']]
locationlist = locations.values.tolist()

# création de la carte folium centrer en (0,0)
map = folium.Map(location=[0, 0], zoom_start=1.5)

# placement des markers
for point in range(0, len(locationlist)):
	folium.Marker(locationlist[point], popup=lieux_df['Ville'][point]).add_to(map)

# liaison des point par une ligne
folium.PolyLine(locationlist, color='green', weight=2).add_to(map)

# affichage une carte Folium
st_map = st_folium(map, width=700, height=450)

