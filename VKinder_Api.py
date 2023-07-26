from random import randrange
from datetime import date
import vk_api
from vk_api.longpoll import VkLongPoll
import re

with open('ApiKey.txt', 'r') as file_object:
    token = file_object.read().strip()

with open('TokenUser.txt', 'r') as file_object:
    token_user = file_object.read().strip()

vk_user = vk_api.VkApi(token=token_user)
session_api = vk_user.get_api()

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)

def get_photo(user_id):
    """
        Функция возвращает три последние аватарки в максимальном качестве.
    :param user_id: id пользователя
    """
    photo_info = session_api.photos.get(owner_id=user_id, album_id='profile', photo_sizes=True, extended=True,
                                        access_token=token_user)
    link_all_photo = []
    for photo in photo_info['items'][-3:]:
        max_height = max(dict_h['height'] for dict_h in photo['sizes'])
        max_width = max(dict_w['width'] for dict_w in photo['sizes'])
        for photo_max in photo['sizes']:
            if photo_max['height'] == max_height and photo_max['width'] == max_width:
                link_photo = photo_max['url']
                link_all_photo.append(link_photo)
                break
    return link_all_photo


def write_msg(user_id, message, keyboard=None):
    vk.method('messages.send',
              {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), 'keyboard': keyboard})

def send_photo(user_id, url_link: str):
    vk.method('messages.send', {'user_id': user_id, 'message': "Фото", 'random_id': randrange(10 ** 7), 'attachment': str(url_link)})


def get_info(user_id):
    """
            Функция получается информацию о пользователе ФИ, город, пол и вычисляет возраст
    :param user_id: id пользователя
    """
    user_info = session_api.users.get(user_ids=(user_id), fields=('city', 'sex', 'bdate'))
    user_info = user_info[0]
    birthday = user_info['bdate']
    pattern_age = r'(\d+)\.(\d+)\.(\d{4})'
    if re.match(pattern_age, birthday):
        today = date.today()
        age = today.year - int(re.sub(pattern_age, r'\3', birthday)) - ((today.month, today.day) < (
        int(re.sub(pattern_age, r'\2', birthday)), int(re.sub(pattern_age, r'\1', birthday))))
    else:
        age = None
    gender = ('-', 'Ж', 'М')[user_info['sex']]

    user_info = {
        'first_name': user_info['first_name'],
        'last_name': user_info['last_name'],
        'city': user_info['city'],
        'gender': gender,
        'age': age
    }

    return user_info


def get_search(name_city, age, gender, offset=0):
    """
        Функция производит поиск предложений на основе информации о пользователе и возвращает 5 предложений при дальнейшем поиске offset увеличивается на 5,
    возвращает id предложения, ФИ, ссылку фото, возраст и ссылку на профиль
    :param name_city: Город
    :param age: Возраст
    :param gender: Пол
    :param offset: смещение поиска

    """
    users_info = session_api.users.search(hometown=name_city, sex=gender, status=6, age_from=age - 3, age_to=age + 3,
                                          count=5, offset=offset, fields=('photo_max_orig', 'bdate', 'city', 'sex', 'home_town'))
    profiles_list = []
    for user_info in users_info['items']:
        if user_info['is_closed']:
            continue
        if user_info.get('city') is None:
            city = {'title': user_info['home_town']}
        else:
            city = user_info['city']
        birthday = user_info['bdate']
        pattern_age = r'(\d+)\.(\d+)\.(\d{4})'
        today = date.today()
        age = today.year - int(re.sub(pattern_age, r'\3', birthday)) - ((today.month, today.day) < (
            int(re.sub(pattern_age, r'\2', birthday)), int(re.sub(pattern_age, r'\1', birthday))))
        gender = ('-', 'Ж', 'М')[user_info['sex']]
        id_offer = str(user_info['id'])
        profile_info = {
            'id_offer': id_offer,
            'first_name': user_info['first_name'],
            'last_name': user_info['last_name'],
            'photo_link': user_info['photo_max_orig'],
            'city': city,
            'gender': gender,
            'agе': age,
            'url_profile': 'https://vk.com/id' + id_offer
        }
        profiles_list.append(profile_info)
    return profiles_list

