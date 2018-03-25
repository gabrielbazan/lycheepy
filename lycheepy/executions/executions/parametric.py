from simplyrestful.settings import configure_from_module
configure_from_module('settings')
from simplyrestful.database import session
from models import ExecutionStatus


objects = [
    ExecutionStatus(name='RUNNING'),
    ExecutionStatus(name='SUCCESS'),
    ExecutionStatus(name='FAILURE')
]


if __name__ == '__main__':
    try:
        session.add_all(objects)
        session.commit()
    except:
        session.rollback()
