#coding=utf-8

class Study:
	def __init__(self):
		self.name = 'yinshuai'
		self.age = 44
		self.__instance = 'hehda'

	# _instance = 'heheda'

	@classmethod
	def printcls(cls):
		# print hasattr(cls,'name')
		if not hasattr(cls,'_instance'):
			cls._instance = cls()
		return cls._instance


# study = Study()
# Study.printcls()
# print 'first is ' + Study._instance
Study.printcls()
instance = Study._instance
name = instance.name
print 'name is ',name

# print study.name
# print study.__instance
