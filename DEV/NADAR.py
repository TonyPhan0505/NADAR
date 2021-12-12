from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import time
import os
import getpass
import sqlite3
import urllib.parse
import requests
import webbrowser
import folium
from googlesearch import search

path = str(os.path.dirname(os.path.realpath(__file__))) + "/"

def all_hazards():

	disasters = []

	main_api = "https://gdacs.org/xml/gdacs_archive.geojson"

	json_data = requests.get(main_api).json()

	for item in json_data['features']:

		disaster = {}

		description = item['properties']['htmldescription']

		details = {'eventname':item['properties']['name'],'type':item['properties']['eventtype'], 'coordinates':[round(i,4) for i in item['geometry']['coordinates']][::-1], 'country':item['properties']['country'], 'level':item['properties']['alertlevel'], 'active':item['properties']['iscurrent'], 'geometry':item['properties']['url']['geometry'], 'casualties':item['properties']['severitydata']['severity']}

		disaster[description] = details

		disasters.append(disaster)

	return disasters

def hazards_by_categories():

	disasters = all_hazards()

	earthquakes = []

	cylones = []

	floods = []

	volcanoes = []

	droughts = []

	forestfires = []

	for disaster in disasters:

		name = list(disaster.keys())[0]

		if "Earthquake" in name:

			earthquakes.append(disaster)

		elif "Cylone" in name:

			cylones.append(disaster)

		elif "Flood" in name:

			floods.append(disaster)

		elif "Volcanic" in name:

			volcanoes.append(disaster)

		elif "Drought" in name:

			droughts.append(disaster)

		elif "fires" in name:

			forestfires.append(disaster)

	categories = {"earthquake":earthquakes, "cyclone":cylones, "flood":floods, "volcano":volcanoes, "drought":droughts, "fire":forestfires}

	return categories


def all_hazards_locations():

	locations = []

	disasters = all_hazards()

	for disaster in disasters:

		location = {}

		name = list(disaster.keys())[0]

		coordinates = disaster[name]['coordinates']

		casualties = disaster[name]['casualties']

		location[name] = [coordinates, casualties]

		locations.append(location)

	return locations


def filtered_hazards(country, disasters):

	filtered_disasters = []

	if country:

		for i in range(len(disasters)):

			if country in disasters[i][list(disasters[i].keys())[0]]['country']:

				filtered_disasters.append(disasters[i])

	else:

		filtered_disasters = disasters

	return filtered_disasters


def draw_map():

	disasters_map = folium.Map(
		location = [13.133932434,16.10393872],
		zoom_start = 4
		)

	locations = all_hazards_locations()

	for location in locations:

		name = list(location.keys())[0]

		coordinates = list(location.values())[0][0]

		casualties = list(location.values())[0][1]

		folium.Marker(
			location = coordinates,
			popup = f"{name}. Population exposed: {casualties}",
			tooltip = f"{name}. Population exposed: {casualties}",
			icon = folium.Icon(color=name.split()[0].lower())
		).add_to(disasters_map)

	disasters_map.save(path+"Media/disasters_map.html")

	webbrowser.open_new("file:"+path+"Media/disasters_map.html")


def draw_cyclones():

	messagebox.showinfo("Notice","Please allow roughly a minute for the map to be drawn with care.")

	cyclones_coordinates = []

	for disaster in all_hazards():

		if "Cylone" in list(disaster.keys())[0] and len(cyclones_coordinates) < 10:

			main_api = list(disaster.values())[0]['geometry']

			json_data = requests.get(main_api).json()

			positions = [i[::-1] for i in json_data['features'][1]['geometry']['coordinates'][0]]

			initial_position = positions[0]

			cyclones_coordinates.append({ list(disaster.keys())[0] : {'initial position':initial_position,'positions': positions, 'casualties': list(disaster.values())[0]['casualties']}})

	cyclones_map = folium.Map(location=[13.133932434,16.10393872],
	zoom_start=3)

	colors = ['red', 'blue', 'green', 'purple', 'orange', 'pink','black', 'white', 'lightblue', 'lightgreen']

	for cc in range(len(cyclones_coordinates)):

		name = list(cyclones_coordinates[cc].keys())[0]

		casualties = list(cyclones_coordinates[cc].values())[0]['casualties']

		initial_position = list(cyclones_coordinates[cc].values())[0]['initial position']

		folium.Marker(
			location = initial_position,
			popup = f"{name}. Population exposed: {casualties}",
			tooltip = f"{name}. Population exposed: {casualties}",
			icon = folium.Icon(color=name.split()[0].lower())
		).add_to(cyclones_map)

		positions = list(cyclones_coordinates[cc].values())[0]['positions']

		for p in range(len(positions)):

			if p != len(positions) - 1:

				folium.PolyLine([(positions[p][0],positions[p][1]),(positions[p+1][0],positions[p+1][1])],
					color=colors[cc],
					weight=5,
					opacity=0.8
				).add_to(cyclones_map)

	cyclones_map.save(path + "Media/cyclones_map.html")

	webbrowser.open_new("file:"+path+"Media/cyclones_map.html")

def main():

	root = Tk()

	root.title("NADAR")

	root.geometry("1220x650")

	root.resizable(0,0)

	root.configure(bg = "white")

	def press_signup():

		hide_all_frames()

		signup_frame.pack(fill = "both", expand = 1)


	def welcome_frame():

		hide_all_frames()

		welcome.pack(fill = "both", expand = 1)

		welcome_message.config(text = f"Welcome {username_entry.get()} to NADAR. Proceed to Dashboard.")

		username_info.config(text = f"Username: {username_entry.get()}")

		conn = sqlite3.connect(path + "DB_Files/Users.db")

		cursor = conn.cursor()

		cursor.execute("SELECT * FROM Users_Info")

		records = cursor.fetchall()

		conn.commit()

		for record in records:

			if record[0] == username_entry.get():			

				interests_info.config(text = f"Interests: {record[1]}")

				break

		favorites = []

		for record in records:

			if record[0] == username_entry.get():
				favorites = record[1].split(", ")

		conn.close()

		reports = []

		for favorite in favorites:
			
			for item in hazards_by_categories()[favorite][0:(6//len(favorites))+1]:

				if len(reports) < 7:
					name = list(item.keys())[0]
					url = search(name + " news", num_results = 3)[2]
					report = {name:url}
					reports.append(report)

		Y = 5

		for i in range(len(reports)):

			report = reports[i]
			title = list(report.keys())[0]
			url = list(report.values())[0]

			news_canva = Canvas(social_media_canva, width = 1015, height = 60)
			news_canva.place(x = 5, y = Y)
			news_title = Label(news_canva, text = f"Title: {title}",font = ("Avenir", 14))
			news_title.place(x = 5, y = 6)
			news_url = Label(news_canva, text = f"URL: {url}",font = ("Avenir", 14))
			news_url.place(x = 5, y = 27)

			Y += 68

	def lock_frame_error_message():

		messagebox.showinfo("ERROR","Sorry, your username is not found.")


	def press_dashboard():


		try:

			os.remove(path+"Media/map.html")

			os.remove(path+"Media/cyclones.html")

		except:

			pass

		disasters = all_hazards()


		disaster1_name = list(disasters[0].keys())[0]

		disaster1_name_label.config(text = f"Name: {list(disasters[0].values())[0]['eventname']}")

		disaster1_country_label.config(text = f"Country: {disasters[0][disaster1_name]['country']}")

		disaster1_level_label.config(text = f"Level: {disasters[0][disaster1_name]['level']}")


		disaster2_name= list(disasters[1].keys())[0]

		disaster2_name_label.config(text = f"Name: {list(disasters[1].values())[0]['eventname']}")

		disaster2_country_label.config(text = f"Country: {disasters[1][disaster2_name]['country']}")

		disaster2_level_label.config(text = f"Level: {disasters[1][disaster2_name]['level']}")


		disaster3_name= list(disasters[2].keys())[0]

		disaster3_name_label.config(text = f"Name: {list(disasters[2].values())[0]['eventname']}")

		disaster3_country_label.config(text = f"Country: {disasters[2][disaster3_name]['country']}")

		disaster3_level_label.config(text = f"Level: {disasters[2][disaster3_name]['level']}")

		disaster4_name= list(disasters[3].keys())[0]

		disaster4_name_label.config(text = f"Name: {list(disasters[3].values())[0]['eventname']}")

		disaster4_country_label.config(text = f"Country: {disasters[3][disaster4_name]['country']}")

		disaster4_level_label.config(text = f"Level: {disasters[3][disaster4_name]['level']}")

		disaster5_name= list(disasters[4].keys())[0]

		disaster5_name_label.config(text = f"Name: {list(disasters[4].values())[0]['eventname']}")

		disaster5_country_label.config(text = f"Country: {disasters[4][disaster5_name]['country']}")

		disaster5_level_label.config(text = f"Country: {disasters[4][disaster5_name]['level']}")

		disaster6_name= list(disasters[5].keys())[0]

		disaster6_name_label.config(text = f"Name: {list(disasters[5].values())[0]['eventname']}")

		disaster6_country_label.config(text = f"Country: {disasters[5][disaster6_name]['country']}")

		disaster6_level_label.config(text = f"Country: {disasters[5][disaster6_name]['level']}")

		hide_all_frames()

		dashboard_frame.pack(fill="both",expand=1)


	def press_lock_frame():

		hide_all_frames()

		lock_frame.pack(fill="both",expand=1)


	def press_guidance():

		hide_all_frames()

		guidance_frame.pack(fill = "both", expand = 1)

	def press_social_media():

		hide_all_frames()

		social_media_frame.pack(fill = "both", expand = 1)


	def press_users_frame():

		hide_all_frames()

		users_frame.pack(fill = "both", expand = 1)


	def press_show_more_disasters():

		hide_all_frames()

		show_more_disasters_frame.pack(fill = "both", expand = 1)

	def hide_all_frames():

		lock_frame.pack_forget()

		signup_frame.pack_forget()

		dashboard_frame.pack_forget()

		guidance_frame.pack_forget()

		social_media_frame.pack_forget()

		users_frame.pack_forget()

		show_more_disasters_frame.forget()

		welcome.forget()

	def press_login():

		conn = sqlite3.connect(path + "/"+"DB_Files/Users.db")

		conn.commit()

		cursor = conn.cursor()

		cursor.execute("SELECT * FROM Users_Info")

		records = cursor.fetchall()

		if any(record for record in records if username_entry.get() == record[0]):

			welcome_frame()
			

		else:
			lock_frame_error_message()


	welcome = Frame(root, width = 1220, height = 650)

	welcome_message = Label(welcome, font = ("Avenir",20))

	welcome_message.place(relx = 0.5, rely = 0.5, anchor = CENTER)

	Button(welcome, text = "Continue", width = 8, height = 2, highlightbackground = "black", bg = "white", fg = "black", command = press_dashboard).place(relx = 0.5, y = 600, anchor = CENTER)

	lock_frame = Frame(root, width = 1220, height = 650)

	name = Label(lock_frame, text = getpass.getuser(), font = ("Avenir",10))

	name.place(x = 10, y = 5)

	current_time = Label(lock_frame, text = time.ctime(), font = ("Avenir",10))

	current_time.place(x = 1085, y = 10)

	login_text = Label(lock_frame, text = "LOGIN & SIGN UP", font = ("Avenir", 45))

	login_text.place(x = 410, y = 100)

	username_text = Label(lock_frame, text = "Username:", font = ("Avenir", 25))

	username_text.place(x = 300, y = 250)

	username_entry = Entry(lock_frame, width = "20")

	username_entry.place(x = 510, y = 255)

	login_button = Button(lock_frame, text = "Log In", width = 8, height = 2, highlightbackground = "black", bg = "white", fg = "black", command = press_login)

	login_button.place(x = 546, y = 345)

	signup_button = Button(lock_frame, text = "Sign Up", width = 8, height = 2, highlightbackground = "black", bg = "white", fg = "black",command = press_signup)

	signup_button.place(x = 546, y = 400)

	lock_frame.pack(fill = "both", expand = 1)

	def filter_disasters_information():

		disasters = all_hazards()

		country = country_entry.get()

		disasters = filtered_hazards(country, disasters)

		if len(disasters) == 0:

			messagebox.showinfo("Notice", "There is no result found.")

		else:
			if len(disasters) >=1:

				disaster1_name = list(disasters[0].keys())[0]

				disaster1_name_label.config(text = f"Name: {list(disasters[0].values())[0]['eventname']}")

				disaster1_country_label.config(text = f"Country: {disasters[0][disaster1_name]['country']}")

				disaster1_level_label.config(text = f"Level: {disasters[0][disaster1_name]['level']}")


			if len(disasters) >= 2:

				disaster2_name= list(disasters[1].keys())[0]

				disaster2_name_label.config(text = f"Name: {list(disasters[1].values())[0]['eventname']}")

				disaster2_country_label.config(text = f"Country: {disasters[1][disaster2_name]['country']}")

				disaster2_level_label.config(text = f"Level: {disasters[1][disaster2_name]['level']}")

			if len(disasters) >= 3:

				disaster3_name= list(disasters[2].keys())[0]

				disaster3_name_label.config(text = f"Name: {list(disasters[2].values())[0]['eventname']}")

				disaster3_country_label.config(text = f"Country: {disasters[2][disaster3_name]['country']}")

				disaster3_level_label.config(text = f"Level: {disasters[2][disaster3_name]['level']}")

			if len(disasters) >= 4:

				disaster4_name= list(disasters[3].keys())[0]

				disaster4_name_label.config(text = f"Name: {list(disasters[3].values())[0]['eventname']}")

				disaster4_country_label.config(text = f"Country: {disasters[3][disaster4_name]['country']}")

				disaster4_level_label.config(text = f"Level: {disasters[3][disaster4_name]['level']}")

			if len(disasters) >= 5:

				disaster5_name= list(disasters[4].keys())[0]

				disaster5_name_label.config(text = f"Name: {list(disasters[4].values())[0]['eventname']}")

				disaster5_country_label.config(text = f"Country: {disasters[4][disaster5_name]['country']}")

				disaster5_level_label.config(text = f"Country: {disasters[4][disaster5_name]['level']}")

			if len(disasters) >= 6:

				disaster5_name= list(disasters[5].keys())[0]

				disaster5_name_label.config(text = f"Name: {list(disasters[5].values())[0]['eventname']}")

				disaster5_country_label.config(text = f"Country: {disasters[5][disaster5_name]['country']}")

				disaster5_level_label.config(text = f"Country: {disasters[5][disaster5_name]['level']}")

		hide_all_frames()

		dashboard_frame.pack(fill="both",expand=1)

	dashboard_frame = Frame(root, width = 1220, height = 650)

	menu_canva = Canvas(dashboard_frame, bg = "black", width = 100, height = 644)

	menu_canva.place(x = 0, y = 0)

	to_dashboard_icon = PhotoImage(file = path + "Media/to_dashboard_button.png")

	to_dashboard_button = Button(menu_canva, image = to_dashboard_icon, width = 60, height = 60, command = press_dashboard)

	to_dashboard_button.place(x = 17, y = 50)

	to_all_hazards_icon = PhotoImage(file = path + "Media/to_all_hazards_button.png")

	to_all_hazards_button = Button(menu_canva, image = to_all_hazards_icon, width = 60, height = 60, command = press_show_more_disasters)

	to_all_hazards_button.place(x = 17, y = 170)

	to_guidance_icon = PhotoImage(file = path + "Media/to_guidance_button.png")

	to_guidance_button = Button(menu_canva, image = to_guidance_icon, width = 60, height = 60, command = press_guidance)

	to_guidance_button.place(x = 17, y = 290)

	to_social_media_icon = PhotoImage(file = path + "Media/to_social_media_button.png")

	to_social_media_button = Button(menu_canva, image = to_social_media_icon, width = 60, height = 60, command = press_social_media)

	to_social_media_button.place(x = 17, y = 410)

	to_user_info_icon = PhotoImage(file = path + "Media/to_user_info_button.png")

	to_user_info_button = Button(menu_canva, image = to_user_info_icon, width = 60, height = 60, command = press_users_frame)

	to_user_info_button.place(x = 17, y = 530)

	dashboard_title = Label(dashboard_frame, text = "DASHBOARD", font = ("Bold Avenir", 35))

	dashboard_title.place(x = 140, y = 2)

	show_map_button = Button(dashboard_frame, text = "Show Map", width = 10, height = 2, highlightbackground = "black", bg = "white", fg = "black", command = draw_map)

	show_map_button.place(x = 146, y = 72)

	refresh_button = Button(dashboard_frame, text = "Refresh", width = 10, height = 2, highlightbackground = "black", bg = "white", fg = "black", command = press_dashboard)

	refresh_button.place(x = 310, y = 72)

	horizontal_separator_canva = Canvas(dashboard_frame, width = 1030, height = 2, bg = "black")

	horizontal_separator_canva.place(x = 146, y = 140)

	country_title = Label(dashboard_frame, text = "Country:", font = ("Avenir", 20))

	country_title.place(x = 146, y = 160)

	country_entry = Entry(dashboard_frame, width = 20)

	country_entry.place(x = 146, y = 210)

	horizontal_separator_canva6 = Canvas(dashboard_frame, width = 183, height = 2, bg = "gray85")

	horizontal_separator_canva6.place(x = 148, y = 320)

	threat_levels_title = Label(dashboard_frame, text = "Threat Levels", font = ("Avenir", 20))

	threat_levels_title.place(x = 168, y = 350)

	red_threat_level = Label(dashboard_frame, text = "Red", font = ("Avenir",15))

	red_threat_level.place(x = 214, y = 400)

	arrow = Label(dashboard_frame, text = "^", font = ("Avenir", 30))

	arrow.place(x = 215, y = 450)

	orange_threat_level = Label(dashboard_frame, text = "Orange", font = ("Avenir",15))

	orange_threat_level.place(x = 200, y = 500)

	arrow = Label(dashboard_frame, text = "^", font = ("Avenir", 30))

	arrow.place(x = 215, y = 550)

	green_threat_level = Label(dashboard_frame, text = "Green", font = ("Avenir",15))

	green_threat_level.place(x = 204, y = 600)

	vertical_separator_canva = Canvas(dashboard_frame, width = 1, height = 465, bg = "gray80")

	vertical_separator_canva.place(x = 360, y = 160)


	active_hazards_title = Label(dashboard_frame, text = "Alarming Hazards", font = ("Avenir",27))

	active_hazards_title.place(x = 420, y = 160)

	active_hazards_canva = Canvas(dashboard_frame, width = 750, height = 420, bg = "gray86")

	active_hazards_canva.place(x = 420, y = 210)

	disaster1_canva = Canvas(active_hazards_canva, width = 738, height = 60)

	disaster1_canva.place(x = 6, y = 6)

	disaster1_name_label = Label(disaster1_canva, font = ("Avenir",10))

	disaster1_name_label.place(x = 6, y = 3)

	disaster1_country_label = Label(disaster1_canva, font = ("Avenir",10))

	disaster1_country_label.place(x = 6, y = 25)

	disaster1_level_label = Label(disaster1_canva, font = ("Avenir",10))

	disaster1_level_label.place(x = 6, y = 47)


	disaster2_canva = Canvas(active_hazards_canva, width = 738, height = 60)

	disaster2_canva.place(x = 6, y = 75)

	disaster2_name_label = Label(disaster2_canva, font = ("Avenir",10))

	disaster2_name_label.place(x = 6, y = 3)

	disaster2_country_label = Label(disaster2_canva, font = ("Avenir",10))

	disaster2_country_label.place(x = 6, y = 25)

	disaster2_level_label = Label(disaster2_canva, font = ("Avenir",10))

	disaster2_level_label.place(x = 6, y = 47)


	disaster3_canva = Canvas(active_hazards_canva, width = 738, height = 60)

	disaster3_canva.place(x = 6, y = 144)

	disaster3_name_label = Label(disaster3_canva, font = ("Avenir",10))

	disaster3_name_label.place(x = 6, y = 3)

	disaster3_country_label = Label(disaster3_canva, font = ("Avenir",10))

	disaster3_country_label.place(x = 6, y = 25)

	disaster3_level_label = Label(disaster3_canva, font = ("Avenir",10))

	disaster3_level_label.place(x = 6, y = 47)


	disaster4_canva = Canvas(active_hazards_canva, width = 738, height = 60)

	disaster4_canva.place(x = 6, y = 214)

	disaster4_name_label = Label(disaster4_canva, font = ("Avenir",10))

	disaster4_name_label.place(x = 6, y = 3)

	disaster4_country_label = Label(disaster4_canva, font = ("Avenir",10))

	disaster4_country_label.place(x = 6, y = 25)

	disaster4_level_label = Label(disaster4_canva, font = ("Avenir",10))

	disaster4_level_label.place(x = 6, y = 47)


	disaster5_canva = Canvas(active_hazards_canva, width = 738, height = 60)

	disaster5_canva.place(x = 6, y = 283)

	disaster5_name_label = Label(disaster5_canva, font = ("Avenir",10))

	disaster5_name_label.place(x = 6, y = 3)

	disaster5_country_label = Label(disaster5_canva, font = ("Avenir",10))

	disaster5_country_label.place(x = 6, y = 25)

	disaster5_level_label = Label(disaster5_canva, font = ("Avenir",10))

	disaster5_level_label.place(x = 6, y = 47)


	disaster6_canva = Canvas(active_hazards_canva, width = 738, height = 60)

	disaster6_canva.place(x = 6, y = 352)

	disaster6_name_label = Label(disaster6_canva, font = ("Avenir",10))

	disaster6_name_label.place(x = 6, y = 3)

	disaster6_country_label = Label(disaster6_canva, font = ("Avenir",10))

	disaster6_country_label.place(x = 6, y = 25)

	disaster6_level_label = Label(disaster6_canva, font = ("Avenir",10))

	disaster6_level_label.place(x = 6, y = 47)



	filter_button = Button(dashboard_frame, text = "Filter", highlightbackground = "black", bg = "white",fg = "black", width = 8, height = 2, command = filter_disasters_information)

	filter_button.place(x = 148, y = 260)	

	show_more_disasters_frame = Frame(root, width = 1220, height = 650)

	all_active_hazards_title = Label(show_more_disasters_frame, text = "MOST ALARMING HAZARDS", font = ("Bold Avenir",16))

	all_active_hazards_title.place(x = 18, y = 15)

	back_to_dashboard_button = Button(show_more_disasters_frame, text = "Back to Dashboard", highlightbackground = "black", bg = "white", fg = "black", width = 12, height = 2, command = press_dashboard)

	back_to_dashboard_button.place(x = 1040, y = 15)

	horizontal_separator_canva8 = Canvas(show_more_disasters_frame, width = 1170, height = 2, bg = "black")

	horizontal_separator_canva8.place(x = 20, y = 60)

	if len(hazards_by_categories()['earthquake']) > 6:
		top_earthquakes = hazards_by_categories()['earthquake'][0:6]
	else:
		top_earthquakes = hazards_by_categories()['earthquake']

	earthquake_title = Label(show_more_disasters_frame, text = f"Earthquakes ({len(top_earthquakes)})", font = ("Avenir",16))

	earthquake_title.place(x = 20, y = 90)

	earthquake_canva = Canvas(show_more_disasters_frame, bg = "gray90", width = 200, height = 510)

	earthquake_canva.place(x = 20, y = 120)

	v = 5

	for i in range(len(top_earthquakes)):

		earthquake_info_canva = Canvas(earthquake_canva, width = 181, height = 75)
			
		earthquake_info_canva.place(x = 5, y = v)

		earthquake_name = Label(earthquake_info_canva, text = list(top_earthquakes[i].values())[0]['eventname'], font = ("Avenir",10))

		earthquake_name.place(x = 2, y = 7)

		earthquake_country = Label(earthquake_info_canva, text = f"Lon, Lat: {list(top_earthquakes[i].values())[0]['coordinates']}", font = ("Avenir",12))

		earthquake_country.place(x = 2, y = 26)

		earthquake_level = Label(earthquake_info_canva, text = f"Severity: {list(top_earthquakes[i].values())[0]['level']}", font = ("Avenir",12))

		earthquake_level.place(x = 2, y = 45)	

		v += 84


	if len(hazards_by_categories()['cyclone']) > 6:

		top_cylones = hazards_by_categories()['cyclone'][0:6]
	else:
		top_cylones = hazards_by_categories()['cyclone']

	cylones_title = Label(show_more_disasters_frame, text = f"Cyclones ({len(top_cylones)})", font = ("Avenir",16))

	cylones_title.place(x = 215, y = 90)

	cyclones_movement_tracker_button = Button(show_more_disasters_frame, text = "Track", highlightbackground = "black", bg = "white", fg = "black", width = 5, height = 2, command = draw_cyclones)

	cyclones_movement_tracker_button.place(x = 315, y = 77)

	cylones_canva = Canvas(show_more_disasters_frame, bg = "gray90", width = 200, height = 510)

	cylones_canva.place(x = 215, y = 120)

	v = 5

	for i in range(len(top_cylones)):

		cylone_info_canva = Canvas(cylones_canva, width = 181, height = 75)
			
		cylone_info_canva.place(x = 5, y = v)

		cylone_name = Label(cylone_info_canva, text = list(top_cylones[i].values())[0]['eventname'], font = ("Avenir",10))

		cylone_name.place(x = 2, y = 7)

		cylone_country = Label(cylone_info_canva, text = f"Lon, Lat: {list(top_cylones[i].values())[0]['coordinates']}", font = ("Avenir",12))

		cylone_country.place(x = 2, y = 26)

		cylone_level = Label(cylone_info_canva, text = f"Severity: {list(top_cylones[i].values())[0]['level']}", font = ("Avenir",12))

		cylone_level.place(x = 2, y = 45)	

		v += 84



	if len(hazards_by_categories()['flood']) > 6:

		top_floods = hazards_by_categories()['flood'][0:6]

	else:
		top_floods = hazards_by_categories()['flood']

	floods_title = Label(show_more_disasters_frame, text = f"Floods ({len(top_floods)})", font = ("Avenir",16))

	floods_title.place(x = 410, y = 90)

	floods_canva = Canvas(show_more_disasters_frame, bg = "gray90", width = 200, height = 510)

	floods_canva.place(x = 410, y = 120)

	v = 5

	for i in range(len(top_floods)):

		floods_info_canva = Canvas(floods_canva, width = 181, height = 75)
			
		floods_info_canva.place(x = 5, y = v)

		floods_name = Label(floods_info_canva, text = list(top_floods[i].values())[0]['eventname'], font = ("Avenir",10))

		floods_name.place(x = 2, y = 7)

		floods_country = Label(floods_info_canva, text = f"Lon, Lat: {list(top_floods[i].values())[0]['coordinates']}", font = ("Avenir",12))

		floods_country.place(x = 2, y = 26)

		floods_level = Label(floods_info_canva, text = f"Severity: {list(top_floods[i].values())[0]['level']}", font = ("Avenir",12))

		floods_level.place(x = 2, y = 45)	

		v += 84




	if len(hazards_by_categories()['volcano']) > 6:
		top_volcanoes = hazards_by_categories()['volcano'][0:6]
	else:
		top_volcanoes = hazards_by_categories()['volcano']

	volcanoes_title = Label(show_more_disasters_frame, text = f"Volcanoes ({len(top_volcanoes)})", font = ("Avenir",16))

	volcanoes_title.place(x = 605, y = 90)

	volcanoes_canva = Canvas(show_more_disasters_frame, bg = "gray90", width = 200, height = 510)

	volcanoes_canva.place(x = 605, y = 120)

	v = 5

	for i in range(len(top_volcanoes)):

		volcanoes_info_canva = Canvas(volcanoes_canva, width = 181, height = 75)
			
		volcanoes_info_canva.place(x = 5, y = v)

		volcanoes_name = Label(volcanoes_info_canva, text = list(top_volcanoes[i].values())[0]['eventname'], font = ("Avenir",10))

		volcanoes_name.place(x = 2, y = 7)

		volcanoes_country = Label(volcanoes_info_canva, text = f"Lon, Lat: {list(top_volcanoes[i].values())[0]['coordinates']}", font = ("Avenir",12))

		volcanoes_country.place(x = 2, y = 26)

		volcanoes_level = Label(volcanoes_info_canva, text = f"Severity: {list(top_volcanoes[i].values())[0]['level']}", font = ("Avenir",12))

		volcanoes_level.place(x = 2, y = 45)

		v += 84



	if len(hazards_by_categories()['drought']) > 6:

		top_droughts = hazards_by_categories()['drought'][0:6]
	else:
		top_droughts = hazards_by_categories()['drought']

	droughts_title = Label(show_more_disasters_frame, text = f"Droughts ({len(top_droughts)})", font = ("Avenir",16))

	droughts_title.place(x = 800, y = 90)

	droughts_canva = Canvas(show_more_disasters_frame, bg = "gray90", width = 200, height = 510)

	droughts_canva.place(x = 800, y = 120)

	v = 5

	for i in range(len(top_droughts)):

		droughts_info_canva = Canvas(droughts_canva, width = 181, height = 75)
			
		droughts_info_canva.place(x = 5, y = v)

		droughts_name = Label(droughts_info_canva, text = list(top_droughts[i].values())[0]['eventname'], font = ("Avenir",10))

		droughts_name.place(x = 2, y = 7)

		droughts_country = Label(droughts_info_canva, text = f"Lon, Lat: {list(top_droughts[i].values())[0]['coordinates']}", font = ("Avenir",12))

		droughts_country.place(x = 2, y = 26)

		droughts_level = Label(droughts_info_canva, text = f"Severity: {list(top_droughts[i].values())[0]['level']}", font = ("Avenir",12))

		droughts_level.place(x = 2, y = 45)	

		v += 84


	if len(hazards_by_categories()['fire']) > 14:
		top_forestfires = hazards_by_categories()['fire'][0:13]
	else:
		top_forestfires = hazards_by_categories()['fire']

	forestfires_title = Label(show_more_disasters_frame, text = f"Forest Fires ({len(top_forestfires)})", font = ("Avenir",16))

	forestfires_title.place(x = 994, y = 90)

	forestfires_canva = Canvas(show_more_disasters_frame, bg = "gray90", width = 200, height = 510)

	forestfires_canva.place(x = 994, y = 120)

	v = 5

	for i in range(len(top_forestfires)):

		forestfires_info_canva = Canvas(forestfires_canva, width = 190, height = 75)
			
		forestfires_info_canva.place(x = 5, y = v)

		forestfires_name = Label(forestfires_info_canva, text = list(top_forestfires[i].values())[0]['eventname'], font = ("Avenir",10))

		forestfires_name.place(x = 2, y = 7)

		forestfires_country = Label(forestfires_info_canva, text = f"Lon, Lat: {list(top_forestfires[i].values())[0]['coordinates']}", font = ("Avenir",12))

		forestfires_country.place(x = 2, y = 26)

		forestfires_level = Label(forestfires_info_canva, text = f"Severity: {list(top_forestfires[i].values())[0]['level']}", font = ("Avenir",12))

		forestfires_level.place(x = 2, y = 45)	

		v += 84

	users_frame = Frame(root, width = 1220, height = 650)

	menu_canva5 = Canvas(users_frame, bg = "black", width = 100, height = 644)

	menu_canva5.place(x = 0, y = 0)

	to_dashboard_button5 = Button(menu_canva5, image = to_dashboard_icon, width = 60, height = 60, command = press_dashboard)

	to_dashboard_button5.place(x = 17, y = 50)

	to_all_hazards_button5 = Button(menu_canva5, image = to_all_hazards_icon, width = 60, height = 60, command = press_show_more_disasters)

	to_all_hazards_button5.place(x = 17, y = 170)

	to_guidance_button5 = Button(menu_canva5, image = to_guidance_icon, width = 60, height = 60, command = press_guidance)

	to_guidance_button5.place(x = 17, y = 290)

	to_social_media_button5 = Button(menu_canva5, image = to_social_media_icon, width = 60, height = 60, command = press_social_media)

	to_social_media_button5.place(x = 17, y = 410)

	to_user_info_button5 = Button(menu_canva5, image = to_user_info_icon, width = 60, height = 60, command = press_users_frame)

	to_user_info_button5.place(x = 17, y = 530)

	users_title = Label(users_frame, text = "USER INFORMATION", font = ("Bold Avenir",35))

	users_title.place(x = 146, y = 15)

	horizontal_separator_canva5 = Canvas(users_frame, width = 1030, height = 2, bg = "black")

	horizontal_separator_canva5.place(x = 146, y = 90)

	username_info = Label(users_frame, font = ("Avenir",27))

	username_info.place(x = 146, y = 220)

	interests_info = Label(users_frame, font = ("Avenir",27))

	interests_info.place(x = 146, y = 420)


	guidance_frame = Frame(root, width = 1220, height = 650)

	menu_canva3 = Canvas(guidance_frame, bg = "black", width = 100, height = 644)

	menu_canva3.place(x = 0, y = 0)

	to_dashboard_button3 = Button(menu_canva3, image = to_dashboard_icon, width = 60, height = 60, command = press_dashboard)

	to_dashboard_button3.place(x = 17, y = 50)

	to_all_hazards_button3 = Button(menu_canva3, image = to_all_hazards_icon, width = 60, height = 60, command = press_show_more_disasters)

	to_all_hazards_button3.place(x = 17, y = 170)

	to_guidance_button3 = Button(menu_canva3, image = to_guidance_icon, width = 60, height = 60, command = press_guidance)

	to_guidance_button3.place(x = 17, y = 290)

	to_social_media_button3 = Button(menu_canva3, image = to_social_media_icon, width = 60, height = 60, command = press_social_media)

	to_social_media_button3.place(x = 17, y = 410)

	to_user_info_button3 = Button(menu_canva3, image = to_user_info_icon, width = 60, height = 60, command = press_users_frame)

	to_user_info_button3.place(x = 17, y = 530)

	guidance_title = Label(guidance_frame, text = "GUIDANCE FOR DISASTERS", font = ("Bold Avenir", 35))

	guidance_title.place(x = 140, y = 15)

	horizontal_separator_canva3 = Canvas(guidance_frame, width = 1030, height = 2, bg = "black")

	horizontal_separator_canva3.place(x = 146, y = 90)

	def open_earthquake_guide():

		webbrowser.open_new("https://www.fema.gov/flood-maps/products-tools/know-your-risk/homeowners-renters/protect-property")

	earthquake_guidance_button = Button(guidance_frame, text = "Earthquakes Guide", width = 30, height = 10, highlightbackground = "black", bg = "white", fg = "black", command = open_earthquake_guide)

	earthquake_guidance_button.place(x = 250, y = 210)

	def open_cyclone_guide():

		webbrowser.open_new("https://www.fema.gov/flood-maps/products-tools/know-your-risk/homeowners-renters/protect-property")

	cylones_guidance_button = Button(guidance_frame, text = "Cyclones Guide", width = 30, height = 10, highlightbackground = "black", bg = "white", fg = "black", command = open_cyclone_guide)

	cylones_guidance_button.place(x = 550, y = 210)

	def open_flood_guide():

		webbrowser.open_new("https://www.fema.gov/flood-maps/products-tools/know-your-risk/homeowners-renters/protect-property")

	floods_guidance_button = Button(guidance_frame, text = "Floods Guide", width = 30, height = 10, highlightbackground = "black", bg = "white", fg = "black", command = open_flood_guide)

	floods_guidance_button.place(x = 850, y = 210)

	def open_volcano_guide():

		webbrowser.open_new("https://www.fema.gov/flood-maps/products-tools/know-your-risk/homeowners-renters/protect-property")

	volcanoes_guidance_button = Button(guidance_frame, text = "Volcanoes Guide", width = 30, height = 10, highlightbackground = "black", bg = "white", fg = "black", command = open_volcano_guide)

	volcanoes_guidance_button.place(x = 250, y = 410)

	def open_drought_guide():

		webbrowser.open_new("https://www.fema.gov/flood-maps/products-tools/know-your-risk/homeowners-renters/protect-property")

	droughts_guidance_button = Button(guidance_frame, text = "Droughts Guide", width = 30, height = 10, highlightbackground = "black", bg = "white", fg = "black", command = open_drought_guide)

	droughts_guidance_button.place(x = 550, y = 410)

	def open_fire_guide():

		webbrowser.open_new("https://www.fema.gov/flood-maps/products-tools/know-your-risk/homeowners-renters/protect-property")

	forestfires_guidance_button = Button(guidance_frame, text = "Forest Fires Guide", width = 30, height = 10, highlightbackground = "black", bg = "white", fg = "black", command = open_fire_guide)

	forestfires_guidance_button.place(x = 850, y = 410)

	social_media_frame = Frame(root, width = 1220, height = 650)

	menu_canva4 = Canvas(social_media_frame, bg = "black", width = 100, height = 644)
	menu_canva4.place(x = 0, y = 0)

	to_dashboard_button4 = Button(menu_canva4, image = to_dashboard_icon, width = 60, height = 60, command = press_dashboard)
	to_dashboard_button4.place(x = 17, y = 50)

	to_all_hazards_button4 = Button(menu_canva4, image = to_all_hazards_icon, width = 60, height = 60, command = press_show_more_disasters)
	to_all_hazards_button4.place(x = 17, y = 170)

	to_guidance_button4 = Button(menu_canva4, image = to_guidance_icon, width = 60, height = 60, command = press_guidance)
	to_guidance_button4.place(x = 17, y = 290)

	to_social_media_button4 = Button(menu_canva4, image = to_social_media_icon, width = 60, height = 60, command = press_social_media)
	to_social_media_button4.place(x = 17, y = 410)

	to_user_info_button4 = Button(menu_canva4, image = to_user_info_icon, width = 60, height = 60, command = press_users_frame)
	to_user_info_button4.place(x = 17, y = 530)

	social_media_title = Label(social_media_frame, text = "News Feed", font = ("Bold Avenir", 35))
	social_media_title.place(x = 144, y = 15)

	horizontal_separator_canva4 = Canvas(social_media_frame, width = 1030, height = 2, bg = "black")
	horizontal_separator_canva4.place(x = 144, y = 90)

	social_media_canva = Canvas(social_media_frame, width = 1025, height = 410, bg = "gray90")
	social_media_canva.place(x = 146, y = 160)

	signup_frame = Frame(root, width = 1220, height = 650)

	name = Label(signup_frame, text = getpass.getuser(), font = ("Avenir",10))

	name.place(x = 10, y = 5)

	current_time = Label(signup_frame, text = time.ctime(), font = ("Avenir",10))

	current_time.place(x = 1085, y = 10)

	signup_title = Label(signup_frame, text = "SIGN UP", font = ("Avenir", 45))

	signup_title.place(x = 510, y = 65)

	username_text = Label(signup_frame, text = "Username:", font = ("Avenir", 25))

	username_text.place(x = 300, y = 230)

	user_entry = Entry(signup_frame, width = "20")

	user_entry.place(x = 510, y = 235)

	interests_title = Label(signup_frame, text = "Interests (earthquake, cyclone, flood, volcano, drought, fire)", font = ("Avenir", 25))

	interests_title.place(x = 300, y = 330)

	interests_entry = Entry(signup_frame, width = "30")

	interests_entry.place(x = 300, y = 410)


	def add_users_records():

		user = user_entry.get()

		if user:

			conn = sqlite3.connect(str(os.path.dirname(os.path.realpath(__file__))) + "/"+"DB_Files/Users.db")

			cursor = conn.cursor()

			cursor.execute("SELECT * FROM Users_Info")

			records = cursor.fetchall()

			conn.commit()

			conn.close()

			if any(record for record in records if record[0] == user):

				messagebox.showinfo("ERROR","Your username already exists.")

			else:

				conn = sqlite3.connect(path +"DB_Files/Users.db")
				
				cursor = conn.cursor()

				cursor.execute("""
					INSERT INTO Users_Info (Username, Interests) VALUES (?,?)
				""", [user_entry.get(), interests_entry.get().lower()])

				conn.commit()

				conn.close()

				messagebox.showinfo("CONGRATULATIONS",f"It's a pleasure to see you on board, {user_entry.get()}. Now, log in.")

		else:

			messagebox.showinfo("ERROR","Your username is invalid. Please try again.")
			

	submit_button = Button(signup_frame, text = "Submit", width = 8, height = 2, highlightbackground = "black", bg = "white", fg = "black", command = add_users_records)

	submit_button.place(x = 560, y = 460)

	signin_button = Button(signup_frame, text = "Log In", width = 8, height = 2, highlightbackground = "black", bg = "white", fg = "black", command = press_lock_frame)

	signin_button.place(x = 560, y = 520)

	root.mainloop()

main()
