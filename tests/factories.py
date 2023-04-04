import factory
from service.models import Shopcart, Item
from factory import fuzzy
import logging

logger = logging.getLogger("flask.app")

class ShopcartFactory(factory.Factory):
    """Creates fake shopcart that you don't have to feed"""

    class Meta:
        model = Shopcart
    
    id = factory.Sequence(lambda n:n)
    customer_id = fuzzy.FuzzyChoice(choices=[1,2,3,4,5])
    '''
    @factory.post_generation
    def items(self, create, extracted, **kwargs):   # pylint: disable=method-hidden, unused-argument
        """Creates the items list"""
        if not create:
            return

        if extracted:
            self.items = extracted
    '''

class ItemFactory(factory.Factory):
    """Creates fake item that you don't have to feed"""
    class Meta:
        model = Item
    
    id = factory.Sequence(lambda n:n)
    product_id = factory.Faker('random_element', elements=[1,2,3,4,5])
    count = factory.Faker('random_element', elements=[1,5,10,15])
    name = factory.Faker('random_element', elements=["laptop", "monitor", "desk", "mouse","pc"])
    price = factory.Faker('random_element', elements=[2.0,3.5,10,15.9])
    shopcart_id = None
    shopcart = factory.SubFactory(ShopcartFactory)
    