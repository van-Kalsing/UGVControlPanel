from threading           import RLock
from utilities.singleton import Singleton







class Machine(Singleton):
	"""
	Класс, абстрагирующий аппарат, предоставляет методы для низкоуровнего
	управления роботом. Класс применяет паттерн Singleton во избежание ошибок,
	связанных с параллельным доступом к исполнительным механизмам робота
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		
		self.__machine_lock = RLock()
		
		
		
		
		
	def get_steering_angle(self):
		"""
		Метод, позволяющий считывать угол поворота руля с соответствующего
		датчика робота.
		
		Результат - float, угол поворота руля
		"""
		with self.__machine_lock:
			#!!!!! Реализовать получение угла поворота руля
			return 0.0
			
			
			
	def set_steering_angle(self, steering_angle):
		"""
		Метод, позволяющий устанавливать угол поворота руля в заданное значение
		
		Аргументы:
			steering_angle - float, угол поворота руля
		"""
		with self.__machine_lock:
			#!!!!! Реализовать установку угла поворота руля
			pass
			