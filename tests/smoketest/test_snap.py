import pytest
import os
import getpass
import subprocess
from helpers import RedisTestMixin
import time

@pytest.mark.snaps
class TestRedisStackServerSnap(RedisTestMixin, object):
    
    @classmethod
    def setup_class(cls):
        if getpass.getuser() != 'root':
            raise AttributeError("snap tests can only be run as root")
        if not os.path.exists("/snap"):
            os.symlink("/var/lib/snapd/snap", "/snap")
        cmd = ['snap', 'install', '--dangerous', '--classic', 'redis-stack/redis-stack-server.snap']
        subprocess.run(cmd, check=True)
        
        # start redis
        p = subprocess.Popen("redis-stack-server")
        cls.PID = p.pid
        time.sleep(3)
    
    @classmethod
    def teardown(cls):
        cmd = ["snap", "remove", "redis-stack-server"]
        subprocess.run(cmd, check=True)