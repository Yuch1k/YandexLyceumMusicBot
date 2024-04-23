import requests
import base64
import random


class REQUEST_SHAZAM:
    def __init__(self, question, chat_id):
        self.url = "https://shazam.p.rapidapi.com/search"

        self.headers = {
            "X-RapidAPI-Key": "ac5d3cd149msh2bbaf92249168efp10d52bjsnf37ba7932f86",
            "X-RapidAPI-Host": "shazam.p.rapidapi.com"
        }

        self.querystring = {"term": question,
                            "locale": "en-US",
                            "offset": "0",
                            "limit": "5"}

        self.response = requests.get(self.url,
                                     headers=self.headers,
                                     params=self.querystring)

        self.chat_id = chat_id

    def get_response_variants(self):
        res = []
        try:
            for track in self.response.json()['tracks']['hits']:
                title = track['track']['title']
                subtitle = track['track']['subtitle']

                res.append(
                    (title, subtitle)
                )
        except KeyError:
            return 'Error'
        return res

    def get_data_from_response(self, response_id):
        track = self.response.json()['tracks']['hits'][response_id]

        title = str(track['track']['title']).capitalize()

        subtitle = track['track']['subtitle']

        img_url = track['track']['share']['image']

        links = {
            'shazam_url': track
            ['track']['share']['snapchat'],

            'applemusic_url': track
            ['track']['hub']['options'][0]['actions'][0]['uri']
        }

        music_preload = track['track']['hub']['actions'][-1]['uri']

        self.data_save(
            title,
            subtitle,
            music_preload,
            img_url,
            links,
            response_id
        )

    def get_data_from_voice_response(self):
        file_patch = f'data/{self.chat_id}/user_voice.wav'

        with open(file_patch, 'rb') as f:
            b = base64.b64encode(bytes(
                str(f.read()), 'utf-16')
            )
            base64_str = b.decode('utf-16')

        url = "https://shazam.p.rapidapi.com/songs/detect"

        headers = {
            "content-type": "text/plain",
            "X-RapidAPI-Key": "ac5d3cd149msh2bbaf92249168efp10d52bjsnf37ba7932f86",
            "X-RapidAPI-Host": "shazam.p.rapidapi.com"
        }

        response = requests.post(
            url,
            data=base64_str,
            headers=headers,
            params=self.querystring
        )

    def data_save(self, title, subtitle, music_preload, img_url, links, response_id):
        img_data = requests.get(img_url).content

        with open(f'data/{self.chat_id}/img_{response_id}.jpg', 'wb') as handler:
            handler.write(img_data)

        with open(f'data/{self.chat_id}/links_{response_id}.txt', 'w') as file:
            file.write(title + '\n')
            file.write(subtitle + '\n')

            file.write(links['shazam_url'] + '\n')
            file.write(links['applemusic_url'])

        music_data = requests.get(music_preload).content
        with open(f'data/{self.chat_id}/music_{response_id}.mp3', 'wb') as handler:
            handler.write(music_data)

    @staticmethod
    def get_charts():
        url = "https://shazam.p.rapidapi.com/charts/list"

        headers = {
            "X-RapidAPI-Key": "ac5d3cd149msh2bbaf92249168efp10d52bjsnf37ba7932f86",
            "X-RapidAPI-Host": "shazam.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers)

        white_list = {
            'RU': None,
            'US': None,
            'DE': None,
            'IN': None,
            'ZA': None,
            'IT': None,
            'MX': None,
            'JP': None
        }

        for country in response.json()['countries']:
            if country['id'] in white_list.keys():
                white_list[country['id']] = country

        return white_list

    @staticmethod
    def get_trak_from_charts(locate_id='RU'):
        try:
            url = "https://shazam.p.rapidapi.com/charts/track"

            querystring = {"locale": locate_id, "pageSize": "1", "startFrom": "0"}

            headers = {
                "X-RapidAPI-Key": "ac5d3cd149msh2bbaf92249168efp10d52bjsnf37ba7932f86",
                "X-RapidAPI-Host": "shazam.p.rapidapi.com"
            }

            response = requests.get(
                url,
                headers=headers,
                params=querystring
            )

            res = ''
            print(response.json())
            for i, track in enumerate(response.json()['tracks']):
                res += f'{i + 1}: {track["title"]}\n'

            return True, res[:-2]
        except Exception:
            return False, None

    @staticmethod
    def get_random_song(name):
        url = "https://shazam.p.rapidapi.com/search"

        headers = {
            "X-RapidAPI-Key": "ac5d3cd149msh2bbaf92249168efp10d52bjsnf37ba7932f86",
            "X-RapidAPI-Host": "shazam.p.rapidapi.com"
        }

        querystring = {"term": name,
                       "locale": "en-US",
                       "offset": "0",
                       "limit": "5"}

        response = requests.get(url, headers=headers, params=querystring)

        try:
            track = response.json()['tracks']['hits'][0]
        except KeyError:
            name = random.choice(['Like dat', 'Morgenstern', 'Влюблино',
                                  'AtomicHurt', 'Plastic', 'Like dat', 'Grow a pear',
                                  'Лесник'])
            querystring = {"term": name,
                           "locale": "en-US",
                           "offset": "0",
                           "limit": "5"}
            response = requests.get(url, headers=headers, params=querystring)
            track = response.json()['tracks']['hits'][0]

        title = str(track['track']['title']).capitalize()

        subtitle = track['track']['subtitle']

        img_url = track['track']['share']['image']

        links = {
            'shazam_url': track
            ['track']['share']['snapchat'],

            'applemusic_url': track
            ['track']['hub']['options'][0]['actions'][0]['uri']
        }

        music_preload = track['track']['hub']['actions'][-1]['uri']

        return [
            title,
            subtitle,
            links,
            img_url,
            music_preload]

    @staticmethod
    def get_artist_id(artist_name):
        url = "https://shazam.p.rapidapi.com/search"

        querystring = {"term": artist_name, "locale": "en-US", "offset": "0", "limit": "5"}

        headers = {
            "X-RapidAPI-Key": "ac5d3cd149msh2bbaf92249168efp10d52bjsnf37ba7932f86",
            "X-RapidAPI-Host": "shazam.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)

        res_str = ''
        for artist in response.json()['artists']['hits']:
            res_str += artist['artist']['name']

