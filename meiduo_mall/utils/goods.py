from collections import OrderedDict
from apps.goods.models import GoodsCategory
from apps.goods.models import GoodsChannel

"""
Category Data
"""
def get_categories():

    # Define an ordered dictionary object
    categories = OrderedDict()

    # Sort GoodsChannel by group_id and sequence, then get the sorted result
    channels = GoodsChannel.objects.order_by('group_id',
                                             'sequence')

    # Iterate through the sorted results to get all first-level menus (channels)
    for channel in channels:
        # Get the current group ID from the channel
        group_id = channel.group_id

        # If the current group ID is not in the ordered dictionary
        if group_id not in categories:
            # Add the group ID to the ordered dictionary
            # Use it as the key, and {'channels': [], 'sub_cats': []} as the value
            categories[group_id] = {
                'channels': [],
                'sub_cats': []
            }

        # Get the category name of the current channel
        cat1 = channel.category

        # Append detailed information to the dictionary just created
        categories[group_id]['channels'].append({
            'id': cat1.id,
            'name': cat1.name,
            'url': channel.url
        })

        # Retrieve all second-level categories through the reverse foreign key relation
        cat2s = GoodsCategory.objects.filter(parent=cat1)
        # cat1.goodscategory_set.all()

        for cat2 in cat2s:
            # Create a new list
            cat2.sub_cats = []

            cat3s = GoodsCategory.objects.filter(parent=cat2)

            # Retrieve all third-level categories through the reverse foreign key relation
            for cat3 in cat3s:
                # Build a new list: key = second-level category,
                # value = list of third-level categories
                cat2.sub_cats.append(cat3)

            # Add all content to the ordered dictionary generated for the first-level category
            categories[group_id]['sub_cats'].append(cat2)

    return categories


"""
Breadcrumb Navigation
"""
def get_breadcrumb(category):
    """Receive the lowest-level category, obtain all category names, and return them."""

    breadcrumb = {
        'cat1': '',
        'cat2': '',
        'cat3': '',
    }

    if category.parent is None:
        breadcrumb['cat1'] = category.name
    elif category.parent.parent is None:
        breadcrumb['cat2'] = category.name
        breadcrumb['cat1'] = category.parent.name
    else:
        breadcrumb['cat3'] = category.name
        breadcrumb['cat2'] = category.parent.name
        breadcrumb['cat1'] = category.parent.parent.name

    return breadcrumb


"""
Specification Options
"""
def get_goods_specs(sku):

    # Build the specification key for the current product
    sku_specs = sku.specs.order_by('spec_id')

    sku_key = []
    for spec in sku_specs:
        sku_key.append(spec.option.id)

    # Get all SKUs under the current product
    skus = sku.spu.sku_set.all()

    # Build a specification-option-to-SKU mapping dictionary
    spec_sku_map = {}

    for s in skus:

        # Get the SKU's specification parameters
        s_specs = s.specs.order_by('spec_id')

        # Used to build the key of the specification-to-SKU mapping
        key = []

        for spec in s_specs:
            key.append(spec.option.id)

        # Add records to the specification-to-SKU mapping dictionary
        spec_sku_map[tuple(key)] = s.id

    # The following code binds the corresponding sku_id to each option

    # Get the specification information of the current product
    goods_specs = sku.spu.specs.order_by('id')

    # If the current SKU's specification information is incomplete,
    # stop processing
    if len(sku_key) < len(goods_specs):
        return

    for index, spec in enumerate(goods_specs):

        # Copy the current SKU specification key
        key = sku_key[:]

        # Options under the current specification
        spec_options = spec.options.all()

        for option in spec_options:

            # Find the SKU matching the current specification combination
            key[index] = option.id

            option.sku_id = spec_sku_map.get(tuple(key))

        spec.spec_options = spec_options

    return goods_specs