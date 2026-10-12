"""Storefront display helpers: INR price formatting, discounts and icons.

Everything here is display-only — the figures always come from the database
fields on the models, never from values baked into templates.
"""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django import template
from django.templatetags.static import static


register = template.Library()


@register.filter
def inr(value):
    """Format a price in Indian Rupees with Indian digit grouping.

    Decimal("2499.00") -> "₹2,499", Decimal("24999.00") -> "₹24,999",
    Decimal("100000.00") -> "₹1,00,000". A non-zero paise part is kept.
    """
    try:
        amount = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, TypeError, ValueError):
        return value
    negative = amount < 0
    amount = abs(amount)
    whole = int(amount)
    paise = int(((amount - whole) * 100).to_integral_value(rounding=ROUND_HALF_UP))
    digits = str(whole)
    if len(digits) > 3:
        head, tail = digits[:-3], digits[-3:]
        groups = []
        while head:
            groups.insert(0, head[-2:])
            head = head[:-2]
        grouped = ",".join(groups + [tail])
    else:
        grouped = digits
    result = ("-" if negative else "") + "\u20b9" + grouped
    if paise:
        result += f".{paise:02d}"
    return result


@register.filter
def discount_percent(product):
    """Whole-number percentage saved when a discount price is set, else 0."""
    price = getattr(product, "price", None)
    discount = getattr(product, "discount_price", None)
    if not price or not discount:
        return 0
    try:
        percent = (Decimal(price) - Decimal(discount)) * Decimal(100) / Decimal(price)
        return int(percent.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    except (InvalidOperation, TypeError, ValueError, ZeroDivisionError):
        return 0


@register.filter
def savings_amount(product):
    """Rupees saved when a discount price is set (price − discount), else 0."""
    price = getattr(product, "price", None)
    discount = getattr(product, "discount_price", None)
    if not price or not discount:
        return Decimal("0")
    try:
        return Decimal(price) - Decimal(discount)
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")


# First matching keyword wins; the glyph always stays a Bootstrap Icons class.
_ICON_KEYWORDS = (
    (("electronic", "tech", "gadget"), "bi-cpu"),
    (("game", "gaming", "console"), "bi-controller"),
    (("mobile", "phone", "smartphone"), "bi-phone"),
    (("laptop", "computer", "notebook"), "bi-laptop"),
    (("accessor",), "bi-watch"),
    (("audio", "headphone", "earphone", "earbud", "sound", "speaker"), "bi-headphones"),
    (("camera", "photo"), "bi-camera"),
    (("tv", "television", "monitor", "display"), "bi-tv"),
    (("keyboard",), "bi-keyboard"),
    (("mouse",), "bi-mouse"),
    (("tablet",), "bi-tablet"),
    (("watch", "wearable", "fitness"), "bi-smartwatch"),
    (("home", "kitchen", "appliance"), "bi-house"),
    (("fashion", "cloth", "wear", "apparel"), "bi-bag"),
    (("shoe", "footwear", "sneaker"), "bi-dribbble"),
    (("book", "stationery"), "bi-book"),
    (("sport", "gym", "fitness", "outdoor"), "bi-bicycle"),
    (("beauty", "care", "skin"), "bi-gem"),
    (("toy", "kid", "baby"), "bi-balloon"),
    (("gift",), "bi-gift"),
)


@register.filter
def category_icon(category):
    """Pick a Bootstrap Icons class that matches the category's name/slug."""
    haystack = f"{getattr(category, 'slug', '')} {getattr(category, 'name', '')}".lower()
    for keywords, icon in _ICON_KEYWORDS:
        if any(keyword in haystack for keyword in keywords):
            return icon
    return "bi-grid-3x3-gap"


# Font Awesome icon mapping for the ShopVerse template sections.
_FA_ICON_KEYWORDS = (
    (("electronic", "tech", "gadget"), "fa-microchip"),
    (("game", "gaming", "console"), "fa-gamepad"),
    (("mobile", "phone", "smartphone"), "fa-mobile-alt"),
    (("laptop", "computer", "notebook"), "fa-laptop"),
    (("accessor",), "fa-gem"),
    (("audio", "headphone", "earphone", "earbud", "sound", "speaker"), "fa-headphones-alt"),
    (("camera", "photo"), "fa-camera"),
    (("tv", "television", "monitor", "display"), "fa-tv"),
    (("keyboard",), "fa-keyboard"),
    (("mouse",), "fa-mouse"),
    (("tablet",), "fa-tablet-alt"),
    (("watch", "wearable", "fitness"), "fa-clock"),
    (("home", "kitchen", "appliance"), "fa-couch"),
    (("fashion", "cloth", "wear", "apparel"), "fa-tshirt"),
    (("shoe", "footwear", "sneaker"), "fa-shoe-prints"),
    (("book", "stationery"), "fa-book"),
    (("sport", "gym", "fitness", "outdoor"), "fa-running"),
    (("beauty", "care", "skin"), "fa-spa"),
    (("toy", "kid", "baby"), "fa-puzzle-piece"),
    (("gift",), "fa-gift"),
)


_EMOJI_KEYWORDS = (
    (("electronic", "tech", "gadget", "laptop", "computer"), "\U0001f4bb"),
    (("game", "gaming", "console"), "\U0001f3ae"),
    (("mobile", "phone", "smartphone"), "\U0001f4f1"),
    (("audio", "headphone", "earphone", "earbud", "speaker", "sound"), "\U0001f3a7"),
    (("camera", "photo"), "\U0001f4f7"),
    (("watch", "wearable"), "\u231a"),
    (("fashion", "cloth", "wear", "apparel"), "\U0001f455"),
    (("shoe", "footwear", "sneaker"), "\U0001f45f"),
    (("home", "kitchen", "living", "appliance"), "\U0001f3e0"),
    (("beauty", "care", "skin"), "\U0001f484"),
    (("grocery", "food"), "\U0001f34e"),
    (("sport", "gym", "fitness", "outdoor"), "\u26bd"),
    (("book", "stationery"), "\U0001f4da"),
    (("toy", "kid", "baby"), "\U0001f9f8"),
)


@register.filter
def category_emoji(category):
    """Pick a template-style emoji for a live category name."""
    haystack = f"{getattr(category, 'slug', '')} {getattr(category, 'name', '')}".lower()
    for keywords, emoji in _EMOJI_KEYWORDS:
        if any(keyword in haystack for keyword in keywords):
            return emoji
    return "\U0001f6cd"


@register.filter
def category_fa_icon(category):
    """Pick a Font Awesome icon class that matches the category's name/slug."""
    haystack = f"{getattr(category, 'slug', '')} {getattr(category, 'name', '')}".lower()
    for keywords, icon in _FA_ICON_KEYWORDS:
        if any(keyword in haystack for keyword in keywords):
            return icon
    return "fa-th"


@register.filter
def mul(value, arg):
    """Multiply value by arg. Used for animation delays and progress widths."""
    try:
        return int(value) * int(arg)
    except (TypeError, ValueError):
        return 0


@register.simple_tag(takes_context=True)
def querystring(context, **kwargs):
    """Rebuild the current GET query string with some keys replaced.

    Used by pagination and filter links so they keep the shopper's current
    search, sort and filter choices. Pass ``key=None`` to drop a key.
    """
    request = context.get("request")
    if request is None:
        return ""
    params = request.GET.copy()
    for key, value in kwargs.items():
        if value is None:
            params.pop(key, None)
        else:
            params[key] = value
    return params.urlencode()


# Category-relevant fallback photos for products that have no uploaded image.
# Each entry is (keywords, file under static/store/img/fallback/). The first
# entry whose keyword appears wins; more specific families come first so that,
# for example, "smartwatch" is a watch and "sportswear" is sports.
_FALLBACK_IMAGE_KEYWORDS = (
    (("gaming", "game", "console", "controller"), "gaming.jpg"),
    (("audio", "headphone", "earphone", "earbud", "speaker", "sound"), "audio.jpg"),
    (("watch", "wearable", "fitness band"), "watch.jpg"),
    (("shoe", "footwear", "sneaker", "sandal", "boot"), "footwear.jpg"),
    (("sport", "gym", "fitness", "yoga", "outdoor"), "sports.jpg"),
    (("fashion", "cloth", "apparel", "shirt", "jacket", "dress", "wear"), "fashion.jpg"),
    (("electronic", "tech", "gadget", "laptop", "computer", "phone", "mobile", "tablet", "camera"), "electronics.jpg"),
    (("home", "kitchen", "appliance", "living", "furniture", "decor", "coffee"), "home.jpg"),
    (("beauty", "skin", "cosmetic", "makeup", "perfume"), "beauty.jpg"),
    (("grocery", "food", "fruit", "vegetable", "snack"), "grocery.jpg"),
)
_DEFAULT_FALLBACK_IMAGE = "default.jpg"


def _fallback_file_for(text):
    haystack = text.lower()
    for keywords, filename in _FALLBACK_IMAGE_KEYWORDS:
        if any(keyword in haystack for keyword in keywords):
            return filename
    return None


@register.filter
def product_fallback_image(product):
    """Static URL of a photo that suits a product without an uploaded image.

    The category name is matched first, then the product name, so a product
    still gets a relevant photo when its category is missing or generic.
    Anything unmatched gets the neutral storefront image.
    """
    category = getattr(product, "category", None)
    category_text = f"{getattr(category, 'slug', '')} {getattr(category, 'name', '')}" if category else ""
    filename = _fallback_file_for(category_text) or _fallback_file_for(getattr(product, "name", "") or "")
    return static(f"store/img/fallback/{filename or _DEFAULT_FALLBACK_IMAGE}")
