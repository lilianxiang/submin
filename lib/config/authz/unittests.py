import unittest
import os
import tempfile
import time

from authz import *

class InitTest(unittest.TestCase):
	"Tests the initializer for the Authz-module"

	def setUp(self):
		tempdir = tempfile.gettempdir()
		self.filename = os.path.join(tempdir, 'authz')
		self.userpropfilename = os.path.join(tempdir, 'userprops')
		# Easier than using tempfile.mkstemp() because I only need a filename.
		self.authz = Authz(self.filename, self.userpropfilename)

	def tearDown(self):
		os.unlink(self.filename)

	def testCreateFile(self):
		self.assert_(os.path.exists(self.filename),
				'File %s does not exist' % self.filename)

	def testCreateGroupsSection(self):
		self.assert_(self.authz.authzParser.has_section('groups'),
				'[groups] section not created')
	
	def testAddGroup(self):
		self.authz.addGroup('foo', ['bar'])
		self.assertEquals(self.authz.members('foo'), ['bar'])
		self.authz.addMember('foo', 'baz')
		self.assertEquals(self.authz.members('foo'), ['bar', 'baz'])

	def testRemoveGroup(self):
		self.authz.addGroup('foo', ['bar', 'baz'])
		self.authz.removeMember('foo', 'baz')
		self.assertEquals(self.authz.members('foo'), ['bar'])
		
	def testDoubleGroupAdd(self):
		self.authz.addGroup('foo', ['bar'])
		self.assertRaises(GroupExistsError, self.authz.addGroup, 'foo')

	def testDoubleMemberAdd(self):
		self.authz.addGroup('foo', ['bar'])
		self.assertRaises(MemberExistsError, self.authz.addMember, 'foo', 'bar')

	def testRemoveUnknownMember(self):
		self.authz.addGroup('foo', ['bar'])
		self.assertRaises(UnknownMemberError, self.authz.removeMember, 'foo', 'baz')

	def testRemoveUnknownGroup(self):
		self.assertRaises(UnknownGroupError, self.authz.removeGroup, 'foo')
		
	def testSetRemovePermission(self):
		self.authz.setPermission('foo', '/', 'bar', 'user', 'rw')
		self.assertEquals(self.authz.permissions('foo', '/'), [{'type': 'user', 'name': 'bar', 'permission': 'rw'}])
		self.authz.removePermission('foo', '/', 'bar', 'user')
		self.assertEquals(self.authz.permissions('foo', '/'), [])

	def testAddPath(self):
		self.authz.addPath('foo', '/')
		self.assertRaises(PathExistsError, self.authz.addPath, 'foo', '/')

	def testRemovePath(self):
		self.authz.removePath('foo', '/')

	def testRemoveAllMembers(self):
		self.authz.addGroup('foo', ['bar', 'baz'])
		self.authz.removeAllMembers('foo')
		self.assertEquals(self.authz.members('foo'), [])

	def testRemoveAllMembersUnknownGroup(self):
		self.assertRaises(UnknownGroupError, self.authz.removeAllMembers, 'foo')

	def testListMembersUnknownGroup(self):
		self.assertRaises(UnknownGroupError, self.authz.members, 'foo')

class SaveTest(unittest.TestCase):
	"Testcase for the save() method on the Authz-objects."

	def testModificationTime(self):
		tempdir = tempfile.gettempdir()
		filename = os.path.join(tempdir, 'authz')
		userpropfilename = os.path.join(tempdir, 'userprops')
		authz = Authz(filename, userpropfilename)
		begin = os.path.getmtime(filename)

		# Testing modification time. This takes at least 1.1 seconds.
		# sleep required to up the modification-time, reported in seconds
		time.sleep(1.1)
		authz.save()
		end = os.path.getmtime(filename)
		self.assert_(end > begin, 'Modification time after save not past ' \
				+ 'modification time before save (begin > end)')

if __name__ == '__main__':
	unittest.main()
