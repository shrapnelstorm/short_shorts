import pipe
import unittest

class TestPipe(unittest.TestCase):
	def setUp(self):
		self.pipe = pipe.Pipe(reorder_factor=100)

	def test_reordering(self):
		self.pipe = pipe.Pipe(reorder_factor=100)
		
		msgs = [i for i in range(10)]
		for i in msgs:
			self.pipe.put(i)

		self.pipe.get_msgs() # will handle the reordering
		# ensure no messages are lost
		self.assertTrue( set(self.pipe.prev_msgs) == set(msgs))

		# this should work most of the time
		# odds of original order being preserved are small
		self.assertFalse( self.pipe.prev_msgs == msgs)

	def test_loss(self):
		self.pipe = pipe.Pipe(loss_factor=100)
		
		for i in range(10):
			self.pipe.put(i)
		print len(self.pipe.prev_msgs)
		self.assertTrue(self.pipe.empty())

if __name__ == '__main__':
    unittest.main()
