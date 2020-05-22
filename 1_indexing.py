# from tkinter import *
import os
import datetime
import sqlite3
# from sqlite3 import Error

# Программа создания и обновления базы файлов Zim на основе его основной базы заметок,
# начало - строка 105
# Чтение основной базы данных и первичное формирование базы данных по Zim-файлам.
# Только для блокнота по умолчанию!

def zim_info(item,i):

# открываем файл
 
	zim_file = open (item, 'r')

# получаем данные файла от ОС и ФС

	date0 = datetime.date.fromtimestamp(os.path.getctime(item)) # дата последней модификации, зависит от ОС и ФС
	fsize = os.path.getsize(item) # размер в байтах

# читаем 1 строку

	line1 = str(zim_file.readline())
 
	if line1 == "Content-Type: text/x-zim-wiki\n" :
		field1 = True
	else:
		field1 = False

# читаем 2 строку

	line2 = str(zim_file.readline())
 
	if line2 == "Wiki-Format: zim 0.4\n" :
		field2 = True
	else:
		field2 = False

# читаем 3 строку

	line3 = str(zim_file.readline())

	if line3[0:15] == "Creation-Date: " :
		year1 = int(line3[15:19])
		month1 = int(line3[20:22])
		day1 = int(line3[23:25])
		date1 = datetime.date(year1, month1, day1)
		field3 = True
	else:
		field3 = False
		date1 = datetime.date(1970,1,1) # обнуляем дату, если строка не та

# читаем 4 строку

	line4 = str(zim_file.readline())
 
	if line4 != "\n" :
		field4 = False
		line5 = line4 # считаем 4 строку как 5 (пропуск пустой строки в файле)
	else:
		field4 = True
		line5 = str(zim_file.readline()) # читаем реальную 5 строку

# работа с 4/5 строкой
 
	if line5[0:7] != "====== " and line5[-8:-0] != " ======\n" :
		field5 = False
		note_title = "!!!!!!"
	else:
		field5 = True
		note_title = line5[7:-8]

# читаем 5/6 строку

	line6 = str(zim_file.readline())

	if line6 == "" : # если строки вообще нет - считаем дату нулевой
		field6 = False
		date2 = datetime.date(1971,1,1)
	elif line6 == "\n" : # если пустая строка - считаем дату нулевой
		field6 = False
		date2 = datetime.date(1972,2,2)
	elif line6[0:8] != "Создано " : # зависит от шаблона, который может изменить пользователь !!!
		field6 = False
		date2 = datetime.date(1973,3,3) # обнуляем дату, если строка не та
	else:
		try:
			year2 = int(line6.split()[-1])
			monthes = {'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8, 'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12}
			month2 = monthes.get(str(line6.split()[3]))
			day2 = int(line6.split()[2])
			date2 = datetime.date(year2, month2, day2)
			field6 = True
		except:
			field6 = False
			date2 = datetime.date(1974,4,4) # обнуляем дату, если ошибка считывания даты

# возврат всех данных

	return date0, fsize, field1, field2, field3, date1, field4, field5, note_title, field6, date2

# закрываем файл

	zim_file.close()

# НАЧАЛО ПРОГРАММЫ

# формируем путь к блокноту по умолчанию !!!!!!!!!!

# берём файл Zim со списком блокнотов
file_list_notebooks = os.path.join(os.path.expanduser('~'), '.config', 'zim', 'notebooks.list')

list_notebooks = open (file_list_notebooks, 'r') # открываем его

notebook1 = str(list_notebooks.readline())
notebook1 = str(list_notebooks.readline()) # читаем строки до блокнота по умолчанию !!!!!!!!!!

list_notebooks.close # закрываем файл списка блокнотов

notebook = notebook1[9:] # отрезаем путь к блокноту от названия опции

path_notebook = os.path.expanduser('~') + notebook # формируем полный путь к данному блокноту

path_notebook1 = path_notebook.replace('/','_') # заменяем слэши на подчёркивания

# получаем полный путь к соответствующему индексу
index_file_full_path = os.path.join(os.path.expanduser('~'), '.cache', 'zim', 'notebook-' + path_notebook1[1:-1], 'index.db')

conn = sqlite3.connect(index_file_full_path) # открываем индексную базу данных
cur = conn.cursor()

# выбираем из базы все заметки - только текст (без папок)
sql = """SELECT id,path
		FROM files
		WHERE node_type = ?
		AND path
		LIKE '%.txt'"""
cur.execute(sql, (2,))

list_all_notes = cur.fetchall() # берём из базы все ID и обрезанные пути (имена) заметок

conn.close() # закрываем основную базу данных

# делаем новую базу - для файлов - или подключаемся к ней, если она уже есть

conn = sqlite3.connect("index_files.db")
cursor = conn.cursor()

# создаём в новой базе таблицу, если её нет

try :
	sql = """CREATE TABLE zim_files
			(z_id INTEGER PRIMARY KEY, date_0, size INTEGER, header_1 INTEGER, header_2 INTEGER, header_3 INTEGER, date_1, empty_line INTEGER, title_yes INTEGER, title, date_yes INTEGER, date_2)"""
	cursor.execute(sql)
except :
	print('Таблица уже есть')

# заносим данные в новую базу

note_id = []
for n in range(len(list_all_notes)):
	note_id.append(list_all_notes[n][0]) # формируем список идентификаторов

# формируем для заметок список файлов с полными путями
list_all_files = []

for m in range(len(list_all_notes)):
	list_all_files.append(path_notebook[:-1] + '/' + list_all_notes[m][1])

i = 0

# заносим всё в базу в цикле

for item in list_all_files:
	note_id_i = note_id[i]
	date0, fsize, field1, field2, field3, date1, field4, field5, note_title, field6, date2 = zim_info(item,i)
	sql = """INSERT INTO zim_files (z_id, date_0, size, header_1, header_2,
									header_3, date_1, empty_line, title_yes, title,
									date_yes, date_2)
									VALUES(?,?,?,?,?,?,?,?,?,?,?,?)"""
	cursor.execute(sql, (note_id_i, date0, fsize, field1, field2, field3, date1, field4, field5, note_title, field6, date2))
	i = i + 1

conn.commit() # записываем вставленные данные в базу данных файлов заметок

# Пробуем создать индекс, если его нет

try :
	sql = """CREATE INDEX z_id ON zim_files (z_id)"""
	cursor.execute(sql)
except :
	print('Индекс уже есть')

conn.close() # закрываем базу данных файлов заметок

print('Проиндексировано ', i+1, ' файлов')
