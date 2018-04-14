import unittest

tests = unittest.TestLoader().discover('tests', pattern='test*.py')
result = unittest.TextTestRunner(verbosity=2).run(tests)
if result.wasSuccessful():
    print("Success")
else:
	print("Failure")