import factory
from service.models import Shopcart, Item
from factory import fuzzy

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
    product_id = fuzzy.FuzzyChoice(choices=[1,2,3,4,5])
    count = fuzzy.FuzzyInteger(1)
    name = fuzzy.FuzzyChoice(choices=["laptop", "monitor", "desk", "mouse","pc"])
    shopcart_id = fuzzy.FuzzyChoice(choices=[1,2,3,4,5])
    shopcart_id = None
    shopcart = factory.SubFactory(ShopcartFactory)
    