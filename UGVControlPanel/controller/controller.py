import threading
import time







class ControllerParameters:
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		
		self.__steering_control_period = None
		self.__velocity_control_period = None
		
		
		
	def copy(self):
		controller_parameters = ControllerParameters()
		
		controller_parameters.__steering_control_period = \
			self.__steering_control_period
			
		controller_parameters.__velocity_control_period = \
			self.__velocity_control_period
			
		return controller_parameters
		
		
		
		
		
	@property
	def is_correct(self):
		is_correct = True
		
		is_correct &= self.__steering_control_period is not None
		is_correct &= self.__velocity_control_period is not None
		
		return is_correct
		
		
		
	@property
	def steering_control_period(self):
		return self.__steering_control_period
		
		
		
	@steering_control_period.setter
	def steering_control_period(self, steering_control_period):
		if steering_control_period <= 0.0:
			# Период должен быть положительным числом
			raise Exception() #!!!!! Создавать хорошие исключения
			
		self.__steering_control_period = steering_control_period
		
		
		
	@property
	def velocity_control_period(self):
		return self.__velocity_control_period
		
		
		
	@velocity_control_period.setter
	def velocity_control_period(self, velocity_control_period):
		if velocity_control_period <= 0.0:
			# Период должен быть положительным числом
			raise Exception() #!!!!! Создавать хорошие исключения
			
		self.__velocity_control_period = velocity_control_period
		
		
		
		
		
		
		
class Controller:
	def __init__(self, machine, controller_parameters, *args, **kwargs):
		if not controller_parameters.is_correct:
			# Заданы не все параметры
			raise Exception() #!!!!! Создавать хорошие исключения
			
			
		super().__init__(*args, **kwargs)
		
		
		self._controller_lock = threading.RLock()
		
		self.__machine               = machine
		self.__controller_parameters = controller_parameters.copy()
		
		self.__is_started              = False
		self.__is_stopped              = False
		self.__steering_control_thread = None
		self.__velocity_control_thread = None
		
		
		
	def _lock_controller(method):
		def result_method(self, *args, **kwargs):
			with self._controller_lock:
				return method(self, *args, **kwargs)
				
		return result_method
		
		
		
		
		
	@property
	def machine(self):
		return self.__machine
		
		
		
	@property
	def controller_parameters(self):
		return self.__controller_parameters.copy()
		
		
		
		
		
	def start_control(self):
		self.__start_control()
		
		self.__steering_control_thread.join()
		self.__velocity_control_thread.join()
		
		
		
	@_lock_controller
	def __start_control(self):
		if self.__is_stopped:
			# Контроллер остановлен
			raise Exception() #!!!!! Создавать хорошие исключения
			
		if self.__is_started:
			# Контроллер уже запущен
			raise Exception() #!!!!! Создавать хорошие исключения
			
			
			
		def get_iterator(function, period):
			def iterator():
				while function():
					time.sleep(period)
					
			return iterator
			
			
		control_steering_iterator = \
			get_iterator(
				self.__control_steering,
				self.__controller_parameters.steering_control_period
			)
			
		self.__steering_control_thread = \
			threading.Thread(target = control_steering_iterator)
			
			
		control_velocity_iterator = \
			get_iterator(
				self.__control_velocity,
				self.__controller_parameters.velocity_control_period
			)
			
		self.__velocity_control_thread = \
			threading.Thread(target = control_velocity_iterator)
			
			
			
		self.__is_started = True
		
		self.__steering_control_thread.start()
		self.__velocity_control_thread.start()
		
		
		
	@_lock_controller
	def stop_control(self):
		if not self.__is_started:
			# Контроллер еще не запущен
			raise Exception() #!!!!! Создавать хорошие исключения
			
		if self.__is_stopped:
			# Контроллер уже остановлен
			raise Exception() #!!!!! Создавать хорошие исключения
			
		self.__is_stopped = True
		
		
		
	@property
	def is_started(self):
		return self.__is_started
		
		
		
	@property
	def is_stopped(self):
		return self.__is_stopped
		
		
		
		
		
	@_lock_controller
	def __is_control_automatic(self):
		#!!!!! Выполнить проверку
		return False
		
		
		
	@_lock_controller
	def __control_steering(self):
		if not self.__is_stopped:
			if self.__is_control_automatic():
				#!!!!! Запустить автоматическое управление
				pass
			else:
				#!!!!! Запустить ручное управление
				pass
				
		return not self.__is_stopped
		
		
		
	@_lock_controller
	def __control_velocity(self):
		if not self.__is_stopped:
			if self.__is_control_automatic():
				#!!!!! Запустить автоматическое управление
				pass
			else:
				#!!!!! Запустить ручное управление
				pass
				
		return not self.__is_stopped
		