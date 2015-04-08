import pytest
from pytest_ansible.errors import (AnsibleHostUnreachable, AnsibleNoHostsMatch)


pytest_plugins = 'pytester'


def assert_ping_response_success(data):
    return assert_ping_response(data, failed=False)


def assert_ping_response_failure(data):
    return assert_ping_response(data, failed=True)


def assert_ping_response(data, failed):

    if failed:
        assert 'failed' in data
        assert data['failed']
    else:
        assert 'failed' not in data
        assert 'invocation' in data
        assert 'module_name' in data['invocation']
        assert 'ping' == data['invocation']['module_name']


def test_ping(ansible_module):
    '''Verify the ansible ping module across all inventory
    '''
    exc_info = pytest.raises(AnsibleHostUnreachable, ansible_module.ping)
    (contacted, dark) = exc_info.value.results

    # assert contacted hosts ...
    assert contacted
    assert len(contacted) == len(ansible_module.inventory_manager.list_hosts('!unreachable'))
    for result in contacted.values():
        assert_ping_response_success(result)

    # assert dark hosts ...
    assert dark
    assert len(dark) == len(ansible_module.inventory_manager.list_hosts('unreachable'))
    for result in dark.values():
        assert_ping_response_failure(result)


@pytest.mark.ansible(host_pattern='localhost')
def test_ping_localhost(ansible_module):
    '''Verify the ansible ping module while specifying a host_pattern:localhost
    '''
    result = ansible_module.ping()

    # assert contacted hosts ...
    assert len(result) == 1
    for contacted in result.values():
        assert_ping_response_success(contacted)


@pytest.mark.ansible(host_pattern='localhost')
def test_ping_limit_localhost(ansible_module):
    '''Verify the ansible ping module while specifying a host_pattern:localhost
    '''
    contacted = ansible_module.ping()

    # assert contacted hosts ...
    assert contacted
    assert len(contacted) == 1
    for result in contacted.values():
        assert_ping_response_success(result)


@pytest.mark.ansible(host_pattern='unreachable')
def test_ping_limit_unreachable(ansible_module):
    '''Verify the ansible ping module while specifying a host_pattern:unreachable
    '''
    exc_info = pytest.raises(AnsibleHostUnreachable, ansible_module.ping)
    (contacted, dark) = exc_info.value.results

    # assert no contacted hosts ...
    assert not contacted, "%d hosts were contacted, expected %d" \
        % (len(contacted), 0)

    # assert dark hosts ...
    assert dark
    assert len(dark) == len(ansible_module.inventory_manager.list_hosts('unreachable'))
    for result in dark.values():
        assert_ping_response_failure(result)


@pytest.mark.ansible(host_pattern='!unreachable')
def test_ping_not_unreachable(ansible_module):
    '''Verify the ansible ping module while specifying a host_pattern:!unreachable
    '''
    contacted = ansible_module.ping()

    # assert contacted hosts ...
    assert contacted
    assert len(contacted) == len(ansible_module.inventory_manager.list_hosts('!unreachable'))
    for result in contacted.values():
        assert_ping_response_success(result)


@pytest.mark.ansible(connection='local')
def test_ping_connection_local(ansible_module):
    '''Verify the ansible ping module while specifying a connection:local
    '''
    contacted = ansible_module.ping()

    # assert contacted hosts ...
    assert contacted
    assert len(contacted) == len(ansible_module.inventory_manager.list_hosts('all'))
    for result in contacted.values():
        assert_ping_response_success(result)


@pytest.mark.ansible(inventory='local,', connection='local')
def test_ping_inventory_local(ansible_module):
    '''Verify the ansible ping module while specifying a inventory:local, and connection:local
    '''
    contacted = ansible_module.ping()

    # assert contacted hosts ...
    assert contacted
    assert len(contacted) == 1
    for result in contacted.values():
        assert_ping_response_success(result)


@pytest.mark.ansible(host_pattern='localhost', sudo=True)
def test_ping_sudo(ansible_module):
    '''Verify the ansible ping module while specifying a host_pattern:localhost and sudo:true
    '''
    contacted = ansible_module.ping()

    # assert contacted hosts ...
    assert contacted
    assert len(contacted) == 1
    for result in contacted.values():
        assert_ping_response_failure(result)


@pytest.mark.ansible(host_pattern='random_limit_that_has_no_matches')
def test_ping_limit_no_matching_host(ansible_module):
    '''Verify the ansible ping fails when specifying a host_pattern that does not match
    '''
    with pytest.raises(AnsibleNoHostsMatch):
        ansible_module.ping()


def test_ansible_facts(ansible_facts, ansible_module):
    '''Verify that the ansible_facts fixture behaves as expected
    '''
    # assert contacted hosts ...
    assert ansible_facts
    assert len(ansible_facts) == len(ansible_module.inventory_manager.list_hosts('!unreachable'))
    for host_facts in ansible_facts.values():
        assert 'ansible_facts' in host_facts
        assert 'ansible_os_family' in host_facts['ansible_facts']
        assert 'ansible_distribution' in host_facts['ansible_facts']


def test_ansible_host(ansible_host, ansible_module):
    '''Verify the parameterized fixture ansible_host restricts inventory properly
    '''
    # assert inventory is restricted to a single host matching 'ansible_host'
    assert ansible_module.inventory_manager.list_hosts() == [ansible_host]


def test_ansible_group(ansible_group, ansible_module):
    '''Verify the parameterized fixture ansible_group restricts inventory properly
    '''
    # assert that only hosts from 'ansible_group' were found
    for host in ansible_module.inventory_manager.get_hosts():
        assert ansible_group in [g.name for g in host.get_groups()]


@pytest.mark.ansible(host_pattern='localhost', connection='local')
class Test_Fixture_Scope(object):
    '''Verify that pytest.mark.ansible applies to all class methods
    '''
    def test_ping_single_host(self, ansible_module):
        # ping
        contacted = ansible_module.ping()

        # assert a single contacted host ...
        assert contacted and len(contacted) == 1
        assert 'localhost' in contacted

    def test_ping_single_host_again(self, ansible_module):
        # ping
        contacted = ansible_module.ping()

        # assert a single contacted host ...
        assert contacted and len(contacted) == 1
        assert 'localhost' in contacted


@pytest.mark.ansible(host_pattern='localhost', connection='local')
def test_extra_runner_kwargs(ansible_module, tmpdir):
    '''Extra arguments in _runner_kwargs are passed along to the Runner
    '''
    contacted = ansible_module.file(
        path=tmpdir.strpath, state='absent',
        _runner_kwargs={
            'check': True,
        })

    # Since this was run in check mode, the tmpdir will still exist.
    assert tmpdir.exists()
    localhost = contacted['localhost']
    assert not localhost.get('failed')
    assert localhost.get('changed')
