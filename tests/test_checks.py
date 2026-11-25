from detector import checks


def test_reply_to_mismatch():
    pts, reasons = checks.check_reply_to({'from': 'a@good.com', 'reply_to': 'b@evil.com'})
    assert pts == 20 and reasons


def test_lookalike_detected():
    pts, _ = checks.check_lookalike({'from': 'x@paypa1.com'})
    assert pts == 25


def test_real_brand_not_flagged():
    pts, _ = checks.check_lookalike({'from': 'x@mail.paypal.com'})
    assert pts == 0


def test_ip_link():
    pts, _ = checks.check_links('<a href="http://192.0.2.10/x">hi</a>')
    assert pts >= 20

