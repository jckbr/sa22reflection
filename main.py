import folium, re, os, base64
from folium import IFrame
from dataclasses import dataclass
from datetime import datetime

# Used for loading data from files into arrays
temp = []

@dataclass
# For train route information array objects
class Route:
    start: str
    end: str
    startLoc: [str]
    endLoc: [str]
    dep: datetime
    arr: datetime
    code: str
routes = []

@dataclass
# For place information array objects
class Place:
    title: str
    loc: [str]
    date: datetime
    pics: [str]
places = []

# Load train information and store in array
for fn in os.listdir('trains'):
    if not fn.startswith('.'): # remove files starting with '.'
        with open(os.path.join('trains', fn), 'r') as f:
            for line in f:
                temp.append(line[:-1])
            routes.append(Route(
                temp[0],
                temp[1],
                [float(x) for x in str.split(re.sub('[°NSEW ]', '', temp[2]), ',')], # remove non-numerical values and convert to float
                [float(x) for x in str.split(re.sub('[°NSEW ]', '', temp[3]), ',')],
                datetime.strptime(temp[6] + ' ' + temp[4], '%B %d %Y %H:%M'), # convert time to datetime objects
                datetime.strptime(temp[6] + ' ' + temp[5], '%B %d %Y %H:%M'),
                temp[7]))
            temp = []
print(routes)

# Load place information and store in array
for fn in os.listdir('places'):
    if not fn.startswith('.'):
        with open(os.path.join('places', fn), 'r') as f:
            for line in f:
                if len(temp) == 3: # append entire line when loading image data
                    temp.append(line)
                else: # append entire line except last character
                    temp.append(line[:-1])

            places.append(Place(
                temp[0],
                [float(x) for x in str.split(re.sub('[°NSEW ]', '', temp[1]), ',')],
                datetime.strptime(temp[2], '%B %d %Y'),
                [str(x) for x in str.split(re.sub(' ', '', temp[3]), ',')])) # remove spaces in image data
            temp = []
print(places)

# Create map object focused on Europe
m = folium.Map(location=[48.85679, 2.35108], zoom_start=5, zoom_control=True)

# Loop through routes, adding start and end points as well as lines connecting them
for route in routes:
    folium.Marker(location=route.startLoc, tooltip=route.code).add_to(m)
    folium.Marker(location=route.endLoc, tooltip=route.code).add_to(m)
    folium.PolyLine(locations=[route.startLoc, route.endLoc]).add_to(m)

# Loop through places, encode images in base 64 then add to IFrame and marker popup
for place in places:
    html = ''
    for img in place.pics:
        encoded = base64.b64encode(open('Images/' + img, 'rb').read()).decode()
        html += f'''<img src="data:image/png;base64,{encoded}" width=350>'''
    iframe = IFrame(html, width=750, height=500)
    popup = folium.Popup(iframe, max_width=750)
    print('Finished', place.title)

    folium.Marker(location=place.loc, tooltip=place.title, popup=popup, icon=folium.Icon(color='green')).add_to(m)

m.save('index.html')