import vk_api
import time 
import re
import collections

locations = ['гараж', 'склад', 'склад 2', 'дом', 'лес', 'корабль', 'самолет']
cur_location_id = 0
responce = ''
id = -162041941
stat_msg = 'статистика' 
vk = vk_api.VkApi(login = '', password = '')
vk.auth()

def get_statistics():
	vk.method('messages.send', {'user_id': id,'message': stat_msg})
	time.sleep(10)
	responce = vk.method('messages.get', {'count': 1})
	return responce['items'][0]['body']

def get_rem_times(statistics):
	matches = re.findall(r'[ :а-яА-Я0-9]* мин', statistics)
	rem_times = []
	for match in matches:
		match = match.replace('мин', '').strip().split(': ')
		rem_times.append([match[0], int(match[1])])
	return rem_times

def process_rem_times(rem_times):
	rem_times = sorted(rem_times, key=lambda x: x[1])
	for rem_time in rem_times:
		rem_time[1]*=60
		rem_time[1]+=10
	for i in range(len(rem_times)):
		sum = 0
		for k in range(0, i):
			sum += rem_times[k][1]
		rem_times[i][1] -= sum
	return rem_times

def collect_bitcoins(rem_times):
	for rem_time in rem_times:
		time.sleep(rem_time[1])
		vk.method('messages.send', {'user_id': id,'message': rem_time[0]})
		time.sleep(10)
		vk.method('messages.send', {'user_id': id,'message': 'сбор'})
		time.sleep(10)

def get_btc_count(statistics):
	matches = re.findall(r'\d* BTC', statistics)
	return int(matches[0].replace('BTC', '').strip())

def exchange(bitcoins):
	vk.method('messages.send', {'user_id': id,'message': 'обмен {}'.format(bitcoins)})
	time.sleep(10)

def buy_new_location(next_location_id):
	print(next_location_id)
	if next_location_id == 3:
		next_location_id = 4
	elif next_location_id == 7:
		next_location_id = 3
	vk.method('messages.send', {'user_id': id,'message': 'магазин'})
	time.sleep(10)
	vk.method('messages.send', {'user_id': id,'message': str(next_location_id)})
	time.sleep(10)
	responce = vk.method('messages.get', {'count': 1})
	responce = responce['items'][0]['body']
	if 'успешно' in responce:
		global cur_location_id
		cur_location_id = next_location_id
		vk.method('messages.send', {'user_id': id,'message': locations[cur_location_id]})
		time.sleep(10)
		vk.method('messages.send', {'user_id': id,'message': 'купить'})
		time.sleep(10)
		vk.method('messages.send', {'user_id': id,'message': 'сбор'})
		time.sleep(10)
		bitcoins = get_btc_count(get_statistics())
		exchange(bitcoins)
		update_location()

def update_location():
	vk.method('messages.send', {'user_id': id,'message': locations[cur_location_id]})
	time.sleep(10)	
	vk.method('messages.send', {'user_id': id,'message': 'купить'})
	time.sleep(10)
	responce = vk.method('messages.get', {'count': 1})
	responce = responce['items'][0]['body']
	while not ('Недостаточно' in responce or 'полностью' in responce):
		vk.method('messages.send', {'user_id': id,'message': 'купить'})
		time.sleep(10)
		responce = vk.method('messages.get', {'count': 1})
		responce = responce['items'][0]['body']
	if 'полностью' in responce:
		if(cur_location_id == 4):
			print(time.time() - begin_time)
		buy_new_location(cur_location_id + 1)

if __name__ == '__main__':
	while True:
		begin_time = time.time()
		statistics = get_statistics()
		rem_times = get_rem_times(statistics)
		rem_times = process_rem_times(rem_times)
		collect_bitcoins(rem_times)
		bitcoins = get_btc_count(get_statistics())
		exchange(bitcoins)
		update_location()

