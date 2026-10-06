from bot import get_currency_symbol

def test_get_currency_symbol():
    assert get_currency_symbol({'currency': 'USD'}) == '$'
    assert get_currency_symbol({'currency': 'EUR'}) == '€'
    assert get_currency_symbol({'currency': 'GBP'}) == '£'
    assert get_currency_symbol({'currency': 'UAH'}) == '₴'