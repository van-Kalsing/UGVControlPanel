#!!!!! Дополнить документирование - аргументы get_server: host, port_number
#!!!!! Предоставить возможность внешнего блокирования интерфейса
#!!!!! Создать классы исключений и выбрасывать их объекты взамен заглушек

import http.server
import threading
import time
import urllib







# Коды обрабатываемых клавиш интерфейса пользователя
RIGHT_KEY = "68" # Код клавиши "Стрелка вправо"
LEFT_KEY  = "65" # Код клавиши "Стрелка влево"
UP_KEY    = "87" # Код клавиши "Стрелка вверх"
DOWN_KEY  = "83" # Код клавиши "Стрелка вниз"







class Interface():
	"""
	Класс, абстрагирущий интерфейс пользователя. Позволяет получить состояние
	интерфейса, передать сообщение на интерфейс
	"""
	
	# Множество кодов обрабатываемых клавиш интерфейса пользователя,
	# предназначенных для управления положением и скоростью аппарата
	__position_keys = {
		RIGHT_KEY,
		LEFT_KEY,
		UP_KEY,
		DOWN_KEY,
	}
	
	
	
	
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		
		self._interface_lock = threading.RLock()
		
		self.__server                  = None
		# self.__last_ping_time          = None
		self.__keys_states             = dict()
		self.__keys_states_times_marks = dict()
		self.__key_down_handlers       = dict()
		self.__key_up_handlers         = dict()
		self.__messages                = list()
		
		
		current_time = time.time()
		
		for key in Interface.__position_keys:
			self.__keys_states[key]             = False
			self.__keys_states_times_marks[key] = current_time
			self.__key_down_handlers[key]       = list()
			self.__key_up_handlers[key]         = list()
			
			
			
	def _lock_interface(method):
		"""
		Метод-декоратор, предназначенный для блокирования объекта класса
		Interface или его наследников
		"""
		def result_method(self, *args, **kwargs):
			with self._interface_lock:
				return method(self, *args, **kwargs)
				
		return result_method
		
		
		
		
		
	@_lock_interface
	def is_key_pressed(self, key):
		"""
		Метод, возвращающий состояние запрощенной клавиши (нажата, либо нет)
		
		Аргументы:
			key - str; код клавиши
			
		Результат - bool; True - если клавиша нажата, False - иначе
		"""
		if key not in self.__keys_states:
			# Состояние переданной клавиши не отслеживается
			raise Exception() #!!!!! Создавать хорошие исключения
			
			
		is_key_pressed = self.__keys_states[key]
		
		return is_key_pressed
		
		
		
	@_lock_interface
	def get_key_state_time(self, key):
		"""
		Метод, возвращающий время, в течение которого состояние запрошенной
		клавиши не изменялось
		
		Аргументы:
			key - str; код клавиши
			
		Результат - float; время в секундах пребывания клавиши
			в текущем состоянии
		"""
		if key not in self.__keys_states:
			# Состояние переданной клавиши не отслеживается
			raise Exception() #!!!!! Создавать хорошие исключения
			
			
		current_time        = time.time()
		key_state_time_mark = self.__keys_states_times_marks[key]
		key_state_time      = float(current_time - key_state_time_mark)
		
		return key_state_time
		
		
		
	@_lock_interface
	def add_message(self, message):
		"""
		Метод, принимающий сообщения, предназначенные для вывода на графический
		интерфейс пользователя
		
		Аргументы:
			message - сообщение
		"""
		string_message = str(message)
		
		self.__messages.append(string_message)
		
		
		
		
		
	@_lock_interface
	def add_key_down_handler(self, key, handler):
		if key not in self.__key_down_handlers:
			# Состояние переданной клавиши не отслеживается
			raise Exception() #!!!!! Создавать хорошие исключения
			
		self.__key_down_handlers[key].append(handler)
		
		
		
	@_lock_interface
	def add_key_up_handler(self, key, handler):
		if key not in self.__key_up_handlers:
			# Состояние переданной клавиши не отслеживается
			raise Exception() #!!!!! Создавать хорошие исключения
			
		self.__key_up_handlers[key].append(handler)
		
		
		
		
		
	@_lock_interface
	def get_server(self, host, port_number):
		"""
		Метод, возвращающий сервер, посредством которого осуществляется связь
		с клиентской частью интерфейса пользователя
		
		Аргументы:
			host
			port_number
			
		Результат - HTTPServer (пакет http.server); сервер
		"""
		if self.__server is None:
			handle_get_request  = self.__handle_get_request
			handle_post_request = self.__handle_post_request
			
			class RequestHandler(http.server.BaseHTTPRequestHandler):
				def do_GET(handler):
					handle_get_request(handler)
					
				def do_POST(handler):
					handle_post_request(handler)
					
					
			self.__server = \
				http.server.HTTPServer(
					(host, port_number),
					RequestHandler
				)
				
		return self.__server
		
		
		
	def __handle_get_request(self, handler):
		def send_file(file_name):
			if file_name.endswith(".html") or file_name.endswith(".htm"):
				content_type = "text/html"
			elif file_name.endswith(".js"):
				content_type = "application/javascript"
			else:
				raise Exception() #!!!!! Создавать хорошие исключения
				
				
			try:
				with open(file_name, "rb") as file:
					handler.send_response(200)
					handler.send_header("Content-type", content_type)
					handler.end_headers()
					handler.wfile.write(file.read())
			except:
				raise Exception() #!!!!! Создавать хорошие исключения
				
				
				
		if handler.path == "/":
			file_name = "interface/base.html"
		else:
			file_name = "interface/" + handler.path[1:]
			
			
		try:
			send_file(file_name)
		except:
			#!!!!! Отправлять ошибку
			handler.send_response(200)
			handler.end_headers()
			handler.wfile.write(b"")
			
			
			
	@_lock_interface
	def __handle_post_request(self, handler):
		keys_event_handlers           = list()
		keys_event_handlers_parameter = list()
		
		
		data = urllib.parse.parse_qs(
			handler.rfile.read(
				int(handler.headers.get("content-length"))
			).decode("utf-8")
		)
		
		handler.send_response(200)
		handler.end_headers()
		
		if data:
			command = None
			
			for k in data.keys():
				command = k
				break
				
				
			if command in ["key_down", "key_up"]:
				key = data[command][0]
				
				if key in Interface.__position_keys:
					key_state = self.__keys_states[key]
					
					if (command == "key_up") == key_state:
						current_time = time.time()
						
						self.__keys_states[key]             = not key_state
						self.__keys_states_times_marks[key] = current_time
						
						
					if command == "key_down":
						keys_event_handlers = self.__key_down_handlers[key]
					else:
						keys_event_handlers = self.__key_up_handlers[key]
						
					keys_event_handlers_parameter.append(key)
					
				handler.wfile.write(b"ok")
				
			elif command == "ping":
				output          = "\n".join(self.__messages)
				output          = bytes(output, "utf-8")
				self.__messages = list()
				
				handler.wfile.write(output)
				
			else:
				handler.wfile.write(b"ok")
		else:
			handler.wfile.write(b"ok")
			
			
		for handler in keys_event_handlers:
			handler(*keys_event_handlers_parameter)
			