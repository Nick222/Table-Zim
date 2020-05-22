from tkinter import *
from tkinter import filedialog
from tkinter import Tk
import os
# import datetime
import sqlite3
# from sqlite3 import Error

# Создание таблицы файлов из индексной базы для указанной папки
# Программа запрашивает путь к папке в блокноте Zim и выводит в таблицу все свойства заметок в этой папке

root = Tk() # окно вывода

# формируем путь к блокноту - пока без выбора по умолчанию !!!!!!!!!!

file_list_notebooks = os.path.join(os.path.expanduser('~'), '.config', 'zim', 'notebooks.list') # берём файл Zim со списком блокнотов

list_notebooks = open (file_list_notebooks, 'r') # открываем его

notebook1 = str(list_notebooks.readline())
notebook1 = str(list_notebooks.readline()) # читаем строки до блокнота - пока без выбора по умолчанию !!!!!!!!!!

list_notebooks.close # закрываем файл списка блокнотов

notebook = notebook1[9:] # отрезаем путь к блокноту от названия опции

path_notebook = os.path.expanduser('~') + notebook # формируем полный путь к данному блокноту

path_notebook1 = path_notebook.replace('/','_') # заменяем слэши на подчёркивания

# получаем полный путь к соответствующему индексу
index_file_full_path = os.path.join(os.path.expanduser('~'), '.cache', 'zim', 'notebook-' + path_notebook1[1:-1], 'index.db')

# проверяем - нужно ли обновлять индексную базу файлов

time_stamp_index_db = os.path.getctime(index_file_full_path) # получение времени модификации index.db от ОС

time_stamp_index_files_db = os.path.getctime('index_files.db') # получение времени модификации index_files.db от ОС

# если основная база обновлялась позже базы файлов, то обновляем базу файлов, если нет - уходим

if time_stamp_index_db > time_stamp_index_files_db :
	print('Индексируем...') # ??????????? запустить indexing.py
else :
	print('Индексация базы файлов не требуется')

parent_note_file = filedialog.askdirectory() # запрашиваем нужную папку с заметками - ЗАМЕНИТЬ ПОТОМ НА ДАННЫЕ ОТ ZIM !!!

# отрезаем путь к блокноту и оставляем только путь к анализируемой папке с заметками
lp = len(path_notebook)
parent_note_name = parent_note_file[lp:]

root_title = "Анализ Zim-файлов в папке " + parent_note_name # подготовка вывода
root.title(root_title)

conn = sqlite3.connect(index_file_full_path) # открываем основную индексную базу данных
cur = conn.cursor()

sql = """SELECT id
	FROM files
	WHERE path
	LIKE ?
	AND node_type = ?"""
cur.execute(sql, (parent_note_name, 1)) # ищем в базе заданную выше папку-родителя

parent_id_1 = cur.fetchone() # берём идентификатор родителя

parent_id = parent_id_1[0]

sql = """SELECT id, path
	FROM files
	WHERE parent
	LIKE ?
	AND node_type = ?"""
cur.execute(sql, (parent_id, 2)) # выбираем из базы заметки по родителю

list_of_notes = cur.fetchall() # берём из базы обрезанные пути (имена) заметок

conn.close() # закрываем индексную базу данных

conn = sqlite3.connect("index_files.db") # открываем индексную базу данных по файлам
cur = conn.cursor()

i = 0 # счётчик файлов для числа строк в таблице вывода

bfnw = 0 # начальное значение ширины колонки имени файла
bntw = 0 # начальное значение ширины колонки имени заметки

for item in list_of_notes: # в цикле берём из второй базы информацию по заметкам

	sql = """SELECT title, date_0, date_1, date_2, size
			FROM zim_files
			WHERE z_id
			LIKE ?"""
	cur.execute(sql, (list_of_notes[i][0],))
	result_list_0 = cur.fetchall()
	result_list = result_list_0[0]

# задаём внешний вид строк

	header_number=Label(root, font='Arial 14') # номер строки в таблице вывода
	header_file_name=Label(root, font='Arial 14') # имя файла
	header_note_title=Label(root, font='Arial 14') # имя заметки
	header_date0=Label(root, font='Arial 14') # дата заметки из файла
	header_date1=Label(root, font='Arial 14') # дата заметки из технического заголовка
	header_date2=Label(root, font='Arial 14') # дата заметки из пользовательского заголовка
	header_fsize=Label(root, font='Arial 14') # размер файла заметки

# вывод всей информации построчно

	# отрезаем путь папки
	np = len(parent_note_name)+1
	file_name = list_of_notes[i][1][np:]

	bwcount = len(file_name) # расчёт максимальной ширины колонки имени файла
	if bwcount > bfnw :
		bfnw = bwcount

	bwcount = len(result_list[0]) # расчёт максимальной ширины колонки имени заметки
	if bwcount > bntw :
		bntw = bwcount

	header_number['text'] = i+1
	header_file_name['text'] = file_name
	header_note_title['text'] = result_list[0]
	header_date0['text'] = result_list[1]
	header_date1['text'] = result_list[2]
	header_date2['text'] = result_list[3]
	header_fsize['text'] = result_list[4]

	header_number.grid(row = i+1,column = 0)
	header_file_name.grid(row = i+1,column = 1, sticky=W)
	header_note_title.grid(row = i+1,column = 2, sticky=W)
	header_date0.grid(row = i+1,column = 3)
	header_date1.grid(row = i+1,column = 4)
	header_date2.grid(row = i+1,column = 5)
	header_fsize.grid(row = i+1,column = 6)

	i = i + 1

conn.close() # закрываем индексную базу данных по файлам

# формируем заголовок таблицы

bh=1
bw=1
button_number=Button(root,text='№',width=bw,height=bh,font='Arial 14') # номер строки в таблице вывода
button_file_name=Button(root,text='File Name',width=bfnw,height=bh,font='Arial 14') # имя файла
button_note_title=Button(root,text='Note Title',width=bntw,height=bh,font='Arial 14') # имя заметки
button_date0=Button(root,text='Date File',width=bw*8,height=bh,font='Arial 14') # дата заметки из файла
button_date1=Button(root,text='Date Header',width=bw*8,height=bh,font='Arial 14') # дата заметки из технического заголовка
button_date2=Button(root,text='Date User',width=bw*8,height=bh,font='Arial 14') # дата заметки из пользовательского заголовка
button_fsize=Button(root,text='File Size',width=bw*6,height=bh,font='Arial 14') # размер файла заметки

button_number.grid(row = 0,column = 0)
button_file_name.grid(row = 0,column = 1)
button_note_title.grid(row = 0,column = 2)
button_date0.grid(row = 0,column = 3)
button_date1.grid(row = 0,column = 4)
button_date2.grid(row = 0,column = 5)
button_fsize.grid(row = 0,column = 6)

# запускаем цикл для окна

root.mainloop()
