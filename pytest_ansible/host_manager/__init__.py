"""Fixme."""

import ansible
from pkg_resources import parse_version
from pytest_ansible.logger import get_logger

# conditionally import ansible libraries
has_ansible_v2 = parse_version(ansible.__version__) >= parse_version('2.0.0')
has_ansible_v24 = parse_version(ansible.__version__) >= parse_version('2.4.0')

log = get_logger(__name__)


class BaseHostManager(object):

    """Pass."""

    _required_kwargs = ('inventory',)

    def __init__(self, *args, **kwargs):
        self.options = kwargs

        self.has_required_kwargs(**kwargs)

        # Sub-classes should override this value
        self._dispatcher = None

        # Initialize ansible inventory manager
        self.initialize_inventory()

    def has_required_kwargs(self, **kwargs):
        """Return whether the required kwargs were provided during instantiation."""
        for kwarg in self._required_kwargs:
            assert kwarg in self.options, "Missing required keyword argument '%s'" % kwarg

    def has_matching_inventory(self, host_pattern):
        """Return whether any matching ansible inventory is found for the provided host_pattern."""
        try:
            return len(self.options['inventory_manager'].list_hosts(host_pattern)) > 0 or \
                host_pattern in self.options['inventory_manager'].groups
        except ansible.errors.AnsibleError:
            return False

    def __getitem__(self, item):
        """Return a ModuleDispatcher instance described the provided `item`."""
        # Handle slicing
        if isinstance(item, slice):
            new_item = "all["
            if item.start is not None:
                new_item += str(item.start)
            new_item += '-'
            if item.stop is not None:
                new_item += str(item.stop)
            item = new_item + ']'

        if item in self.__dict__:
            return self.__dict__[item]
        else:
            if not self.has_matching_inventory(item):
                raise KeyError(item)
            else:
                self.options['host_pattern'] = item
                return self._dispatcher(**self.options)

    def __getattr__(self, attr):
        log.debug("BaseHostManager.__getattr__(%s)" % attr)
        """Return a ModuleDispatcher instance described the provided `attr`."""
        if not self.has_matching_inventory(attr):
            raise AttributeError("type HostManager has no attribute '%s'" % attr)
        else:
            self.options['host_pattern'] = attr
            return self._dispatcher(**self.options)

    def keys(self):
        return [h.name for h in self.options['inventory_manager'].list_hosts()]

    def __len__(self):
        """Return the number of inventory hosts."""
        return len(self.options['inventory_manager'].list_hosts())

    def __contains__(self, item):
        """Return whether there is inventory matching the provided `item`."""
        return self.has_matching_inventory(item)

    def initialize_inventory(self):
        raise NotImplementedError("Must be implemented by sub-class")


def get_host_manager(*args, **kwargs):
    """Initialize and return a HostManager instance."""
    log.debug("get_host_manager(%s, %s)" % (args, kwargs))

    if has_ansible_v24:
        from .v24 import HostManagerV24 as HostManager
    elif has_ansible_v2:
        from .v2 import HostManagerV2 as HostManager
    else:
        from .v1 import HostManagerV1 as HostManager

    # TODO - figure out how to surface the parser defaults here too
    return HostManager(*args, **kwargs)


def get_inventory_manager(*args, **kwargs):
    """Return an instance of ansible inventory manager object."""
    if has_ansible_v24:
        from ansible.inventory.manager import InventoryManager
        return InventoryManager(*args, **kwargs)
    else:
        from ansible.inventory import Inventory
        return Inventory(*args, **kwargs)
