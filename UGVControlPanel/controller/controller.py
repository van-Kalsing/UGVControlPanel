import threading
import time

from interface.interface import \
	Interface, \
	RIGHT_KEY, \
	LEFT_KEY, \
	UP_KEY, \
	DOWN_KEY
	
from regulators.manual_steering_regulator import \
	Regulator as ManualSteeringRegulator, \
	NONE_STATE, \
	RIGHT_STATE, \
	LEFT_STATE, \
	BOTH_STATE
	
	
	
	
	
	
	
class ControllerParameters:
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		
		self.__steering_control_period         = None
		self.__velocity_control_period         = None
		self.__manual_control_maximal_downtime = None
		
		self.__manual_steering_regulator_parameters = None
		
		
		
	def copy(self):
		controller_parameters = ControllerParameters()
		
		
		controller_parameters.__steering_control_period = \
			self.__steering_control_period
			
		controller_parameters.__velocity_control_period = \
			self.__velocity_control_period
			
		controller_parameters.__manual_control_maximal_downtime = \
			self.__manual_control_maximal_downtime
			
			
		controller_parameters.__manual_steering_regulator_parameters = \
			self.__manual_steering_regulator_parameters.copy()
			
			
		return controller_parameters
		
		
		
	@property
	def is_correct(self):
		is_correct = True
		
		
		is_correct &= self.__steering_control_period is not None
		is_correct &= self.__velocity_control_period is not None
		is_correct &= self.__manual_control_maximal_downtime is not None
		
		is_correct &= self.__manual_steering_regulator_parameters is not None
		
		
		return is_correct
		
		
		
		
		
	@property
	def steering_control_period(self):
		return self.__steering_control_period
		
		
		
	@steering_control_period.setter
	def steering_control_period(self, period):
		if period <= 0.0:
			# Период должен быть положительным числом
			raise Exception() #!!!!! Создавать хорошие исключения
			
		self.__steering_control_period = period
		
		
		
	@property
	def velocity_control_period(self):
		return self.__velocity_control_period
		
		
		
	@velocity_control_period.setter
	def velocity_control_period(self, period):
		if period <= 0.0:
			# Период должен быть положительным числом
			raise Exception() #!!!!! Создавать хорошие исключения
			
		self.__velocity_control_period = period
		
		
		
	@property
	def manual_control_maximal_downtime(self):
		return self.__manual_control_maximal_downtime
		
		
		
	@manual_control_maximal_downtime.setter
	def manual_control_maximal_downtime(self, maximal_downtime):
		if maximal_downtime <= 0.0:
			# Максимальный простой должен быть положительным числом
			raise Exception() #!!!!! Создавать хорошие исключения
			
		self.__manual_control_maximal_downtime = maximal_downtime
		
		
		
		
		
	@property
	def manual_steering_regulator_parameters(self):
		return self.__manual_steering_regulator_parameters.copy()
		
		
		
	@manual_steering_regulator_parameters.setter
	def manual_steering_regulator_parameters(self, parameters):
		if not parameters.is_correct:
			# Переданы некорректные параметры
			raise Exception() #!!!!! Создавать хорошие исключения
			
		self.__manual_steering_regulator_parameters = parameters.copy()
		
		
		
		
		
		
		
class Controller:
	__steering_keys = {
		RIGHT_KEY,
		LEFT_KEY,
	}
	
	__velocity_keys = {
		UP_KEY,
		DOWN_KEY,
	}
	
	__position_keys = __steering_keys | __velocity_keys
	
	
	
	
	
	def __init__(self, machine, interface, parameters, *args, **kwargs):
		if not parameters.is_correct:
			# Заданы не все параметры
			raise Exception() #!!!!! Создавать хорошие исключения
			
			
			
		super().__init__(*args, **kwargs)
		
		
		
		self._controller_lock = threading.RLock()
		
		self.__machine    = machine
		self.__interface  = interface
		self.__parameters = parameters.copy()
		
		self.__is_started              = False
		self.__is_stopped              = False
		self.__steering_control_thread = None
		self.__velocity_control_thread = None
		
		self.__manual_steering_regulator = \
			ManualSteeringRegulator(
				self.__machine,
				self.__parameters.manual_steering_regulator_parameters
			)
			
			
			
		def steering_keys_events_handler(*args):
			# Во время выполнения обработчика интерфейс является
			# заблокированным, поэтому нового события клавиш не происходит и
			# блокировка не требуется
			
			with self._controller_lock:
				state = NONE_STATE
				
				if self.__interface.is_key_pressed(RIGHT_KEY):
					state |= RIGHT_STATE
					
				if self.__interface.is_key_pressed(LEFT_KEY):
					state |= LEFT_STATE
					
				self.__manual_steering_regulator.set_state(state)
				
				
		self.__interface.add_key_down_handler(
			RIGHT_KEY,
			steering_keys_events_handler
		)
		
		self.__interface.add_key_down_handler(
			LEFT_KEY,
			steering_keys_events_handler
		)
		
		
		self.__interface.add_key_up_handler(
			RIGHT_KEY,
			steering_keys_events_handler
		)
		
		self.__interface.add_key_up_handler(
			LEFT_KEY,
			steering_keys_events_handler
		)
		
		
		
	def _lock_controller(method):
		def result_method(self, *args, **kwargs):
			with self._controller_lock:
				return method(self, *args, **kwargs)
				
		return result_method
		
		
		
		
		
	@property
	def machine(self):
		return self.__machine
		
		
		
	@property
	def interface(self):
		return self.__interface
		
		
		
	@property
	def parameters(self):
		return self.__parameters.copy()
		
		
		
		
		
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
				self.__parameters.steering_control_period
			)
			
		self.__steering_control_thread = \
			threading.Thread(target = control_steering_iterator)
			
			
		control_velocity_iterator = \
			get_iterator(
				self.__control_velocity,
				self.__parameters.velocity_control_period
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
		is_control_automatic = False
		
		#!!!!! Блокировать интерфейс
		maximal_downtime = self.__parameters.manual_control_maximal_downtime
		
		for key in Controller.__position_keys:
			key_state    = self.__interface.is_key_pressed(key)
			key_downtime = self.__interface.get_key_state_time(key)
			
			if key_state or key_downtime <= maximal_downtime:
				break
		else:
			is_control_automatic = True
		#!!!!! Разблокировать интерфейс
		
		return is_control_automatic
		
		
		
	@_lock_controller
	def __control_steering(self):
		if not self.__is_stopped:
			if self.__is_control_automatic():
				self.__interface.add_message("__control_steering auto")
				#!!!!! Запустить автоматическое управление
				pass
			else:
				def write_message(message):
					self.__interface.add_message(
						"Manual steering control: %s" % message
					)
					
				self.__manual_steering_regulator.control(write_message)
				
		return not self.__is_stopped
		
		
		
	@_lock_controller
	def __control_velocity(self):
		if not self.__is_stopped:
			if self.__is_control_automatic():
				self.__interface.add_message("__control_velocity auto")
				#!!!!! Запустить автоматическое управление
				pass
			else:
				self.__interface.add_message("__control_velocity manual")
				#!!!!! Запустить ручное управление
				pass
				
		return not self.__is_stopped
		