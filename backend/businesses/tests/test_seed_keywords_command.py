"""
Tests for seed_business_keywords management command
Task-18.11: Create Seed Command for Business Type Keywords
"""
import pytest
from io import StringIO
from django.core.management import call_command
from businesses.models import BusinessType, BusinessTypeKeyword


@pytest.fixture
def business_types(db):
    """Ensure all business types exist"""
    types = []
    for code, name in [('pub', 'Pub'), ('restaurant', 'Restaurant'),
                       ('coffee_shop', 'Coffee Shop'), ('bookstore', 'Bookstore')]:
        bt, _ = BusinessType.objects.get_or_create(
            code=code,
            defaults={'display_name': name, 'display_name_es': name}
        )
        types.append(bt)
    return types


@pytest.mark.django_db
class TestSeedBusinessKeywordsCommand:
    """Test seed_business_keywords management command"""

    def test_command_creates_keywords(self, business_types):
        """
        Test that command creates keywords for all business types
        """
        # Clear any existing keywords
        BusinessTypeKeyword.objects.all().delete()

        # Run command
        out = StringIO()
        call_command('seed_business_keywords', stdout=out)

        # Check output
        output = out.getvalue()
        assert 'created' in output.lower()
        assert 'Pub' in output or 'pub' in output.lower()
        assert 'Restaurant' in output or 'restaurant' in output.lower()
        assert 'Coffee Shop' in output or 'coffee' in output.lower()
        assert 'Bookstore' in output or 'bookstore' in output.lower()

        # Check keywords were created
        for bt in business_types:
            keywords = BusinessTypeKeyword.objects.filter(business_type=bt)
            assert keywords.count() > 0, f"No keywords created for {bt.code}"
            assert keywords.count() >= 20, f"Too few keywords for {bt.code}"

    def test_command_idempotent(self, business_types):
        """
        Test that running command multiple times doesn't create duplicates
        """
        # Run command twice
        call_command('seed_business_keywords', stdout=StringIO())
        first_count = BusinessTypeKeyword.objects.count()

        call_command('seed_business_keywords', stdout=StringIO())
        second_count = BusinessTypeKeyword.objects.count()

        # Count should be the same (update_or_create prevents duplicates)
        assert first_count == second_count

    def test_command_clear_flag(self, business_types):
        """
        Test that --clear flag removes existing keywords before seeding
        """
        # Create initial keywords
        call_command('seed_business_keywords', stdout=StringIO())
        initial_count = BusinessTypeKeyword.objects.count()
        assert initial_count > 0

        # Add a custom keyword
        custom_kw = BusinessTypeKeyword.objects.create(
            business_type=business_types[0],
            keyword='custom_test_keyword',
            weight=0.5,
            category='test'
        )

        # Run with --clear
        out = StringIO()
        call_command('seed_business_keywords', '--clear', stdout=out)

        # Check custom keyword was deleted
        assert not BusinessTypeKeyword.objects.filter(keyword='custom_test_keyword').exists()

        # Check output mentions deletion
        output = out.getvalue()
        assert 'Deleted' in output or 'deleted' in output.lower()

    def test_pub_keywords(self, business_types):
        """
        Test that pub business type has appropriate keywords
        """
        pub = BusinessType.objects.get(code='pub')

        # Run command
        call_command('seed_business_keywords', stdout=StringIO())

        # Check for expected keywords
        pub_keywords = BusinessTypeKeyword.objects.filter(business_type=pub)
        keywords_list = list(pub_keywords.values_list('keyword', flat=True))

        # Check for beverages
        assert 'cerveza' in keywords_list or 'beer' in keywords_list

        # Check for sports
        assert 'fútbol' in keywords_list or 'partido' in keywords_list

        # Check for events
        assert any(kw in keywords_list for kw in ['música en vivo', 'live music', 'concierto'])

    def test_restaurant_keywords(self, business_types):
        """
        Test that restaurant business type has appropriate keywords
        """
        restaurant = BusinessType.objects.get(code='restaurant')

        # Run command
        call_command('seed_business_keywords', stdout=StringIO())

        # Check for expected keywords
        rest_keywords = BusinessTypeKeyword.objects.filter(business_type=restaurant)
        keywords_list = list(rest_keywords.values_list('keyword', flat=True))

        # Check for food
        assert 'comida' in keywords_list or 'gastronomía' in keywords_list

        # Check for establishment
        assert 'restaurante' in keywords_list or 'restaurant' in keywords_list

        # Check for cuisine types
        assert any(kw in keywords_list for kw in ['italiana', 'mexicana', 'japonesa'])

    def test_coffee_shop_keywords(self, business_types):
        """
        Test that coffee shop business type has appropriate keywords
        """
        coffee_shop = BusinessType.objects.get(code='coffee_shop')

        # Run command
        call_command('seed_business_keywords', stdout=StringIO())

        # Check for expected keywords
        coffee_keywords = BusinessTypeKeyword.objects.filter(business_type=coffee_shop)
        keywords_list = list(coffee_keywords.values_list('keyword', flat=True))

        # Check for coffee
        assert 'café' in keywords_list or 'coffee' in keywords_list

        # Check for coffee products
        assert any(kw in keywords_list for kw in ['espresso', 'cappuccino', 'latte'])

        # Check for establishment
        assert 'cafetería' in keywords_list or 'coffee shop' in keywords_list

    def test_bookstore_keywords(self, business_types):
        """
        Test that bookstore business type has appropriate keywords
        """
        bookstore = BusinessType.objects.get(code='bookstore')

        # Run command
        call_command('seed_business_keywords', stdout=StringIO())

        # Check for expected keywords
        book_keywords = BusinessTypeKeyword.objects.filter(business_type=bookstore)
        keywords_list = list(book_keywords.values_list('keyword', flat=True))

        # Check for books
        assert 'libro' in keywords_list or 'books' in keywords_list

        # Check for establishment
        assert 'librería' in keywords_list or 'bookstore' in keywords_list

        # Check for events
        assert any(kw in keywords_list for kw in ['autor', 'author', 'presentación'])

    def test_keywords_have_weights(self, business_types):
        """
        Test that all keywords have appropriate weights
        """
        # Run command
        call_command('seed_business_keywords', stdout=StringIO())

        # Check all keywords have weights in valid range
        keywords = BusinessTypeKeyword.objects.all()
        assert keywords.count() > 0

        for kw in keywords:
            assert 0.0 <= kw.weight <= 1.0, f"Invalid weight for keyword {kw.keyword}: {kw.weight}"
            assert kw.weight >= 0.05, f"Weight too low for {kw.keyword}"
            assert kw.weight <= 0.30, f"Weight too high for {kw.keyword}"

    def test_keywords_have_categories(self, business_types):
        """
        Test that all keywords are categorized
        """
        # Run command
        call_command('seed_business_keywords', stdout=StringIO())

        # Check all keywords have categories
        keywords = BusinessTypeKeyword.objects.all()
        assert keywords.count() > 0

        for kw in keywords:
            assert kw.category, f"Keyword {kw.keyword} has no category"
            assert len(kw.category) > 0, f"Keyword {kw.keyword} has empty category"

    def test_keywords_are_active(self, business_types):
        """
        Test that all seeded keywords are active
        """
        # Run command
        call_command('seed_business_keywords', stdout=StringIO())

        # Check all keywords are active
        keywords = BusinessTypeKeyword.objects.all()
        inactive = keywords.filter(is_active=False)
        assert inactive.count() == 0, f"Found {inactive.count()} inactive keywords"

    def test_keywords_are_unique_per_type(self, business_types):
        """
        Test that there are no duplicate keywords within a business type
        """
        # Run command
        call_command('seed_business_keywords', stdout=StringIO())

        # Check for duplicates within each business type
        for bt in business_types:
            keywords = BusinessTypeKeyword.objects.filter(business_type=bt)
            keyword_list = list(keywords.values_list('keyword', flat=True))

            # Check for duplicates
            assert len(keyword_list) == len(set(keyword_list)), \
                f"Duplicate keywords found for {bt.code}: {[k for k in keyword_list if keyword_list.count(k) > 1]}"
