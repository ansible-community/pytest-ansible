## Release History

### 1.2.5 (2015-04-20)

* Add support for ansible-2.0
* Only validate --ansible-* parameters when using pytest-ansible fixture
* Include --ansible-user when running module

### 1.2.4 (2015-03-18)

* Add ansible-1.9 privilege escalation support

### 1.2.3 (2015-03-03)

* Resolve setuptools import failure by migrating from a module to a package

### 1.2.2 (2015-03-03)

* Removed py module dependency
* Add HISTORY.md

### 1.2.1 (2015-03-02)

* Use pandoc to convert existing markdown into pypi friendly rst

### 1.2 (2015-03-02)

* Add `ansible_host` and `ansible_group` parametrized fixture
* Add cls level fixtures for users needing scope=class fixtures
* Updated examples to match new fixture return value
* Alter fixture return data to more closely align with ansible
* Raise `AnsibleHostUnreachable` whenever hosts are ... unreachable
* Set contacted and dark hosts in ConnectionError

### 1.1 (2015-02-16)

* Initial release
