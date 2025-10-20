#!/usr/bin/env python3
"""
Test if improved regex patterns actually extract dates/venues/cities
Uses synthetic test content with clear event information
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'navigate.settings')
django.setup()

from ml_engine.services.feature_extractor import FeatureExtractor

# Test cases with clear event information
test_cases = [
    {
        'name': 'Concert with date and venue',
        'title': 'Shakira en concierto este sábado en Medellín',
        'content': '''
        Shakira se presentará en concierto este sábado 26 de octubre en el Estadio
        Atanasio Girardot de Medellín. El show comenzará a las 8:00 pm y se espera
        la asistencia de más de 40,000 personas. Las boletas están disponibles en
        Tu Boleta desde $150,000. El evento se realizará en El Poblado, Medellín.
        '''
    },
    {
        'name': 'Festival with multiple dates',
        'title': 'Festival Estéreo Picnic 2026',
        'content': '''
        El Festival Estéreo Picnic regresa a Bogotá del 20 al 22 de marzo de 2026.
        Se realizará en el Parque Simón Bolívar con más de 100,000 asistentes esperados.
        Las presentaciones comenzarán a las 2 pm cada día. Entre los artistas confirmados
        están Foo Fighters, The Killers y Arcade Fire.
        '''
    },
    {
        'name': 'Football match',
        'content': '''
        Atlético Nacional enfrentará a Millonarios este domingo 27 de octubre a las 4 pm
        en el estadio Atanasio Girardot de Medellín. Se espera un lleno total con más de
        35,000 hinchas en las tribunas. El partido es válido por la fecha 18 de la Liga BetPlay.
        '''
    },
    {
        'name': 'Cultural event',
        'title': 'Feria de las Flores 2025',
        'content': '''
        La tradicional Feria de las Flores se celebrará en Medellín del 1 al 10 de agosto.
        El evento principal, el Desfile de Silleteros, tendrá lugar el domingo 10 de agosto
        a las 10 am en la Avenida Las Palmas. Se esperan más de 2 millones de visitantes
        durante los 10 días del festival en diferentes puntos de la ciudad como El Poblado,
        Laureles y el Centro.
        '''
    },
]

def main():
    print("="*80)
    print("REGEX PATTERN TESTING")
    print("Testing improved extraction patterns with synthetic event content")
    print("="*80)
    print()

    extractor = FeatureExtractor()

    for i, test in enumerate(test_cases, 1):
        print(f"[{i}/{len(test_cases)}] {test['name']}")
        print(f"  Title: {test.get('title', 'N/A')}")

        # Extract features
        features = extractor.extract_all(
            test['content'],
            test.get('title', '')
        )

        # Show what was extracted
        print("\n  Extracted:")
        key_fields = ['event_type', 'event_subtype', 'city', 'neighborhood',
                     'venue', 'event_date', 'event_end_datetime', 'event_duration_hours',
                     'attendance', 'scale', 'keywords', 'entities']

        populated = 0
        for field in key_fields:
            value = features.get(field)
            if value not in [None, '', [], 0.0]:
                populated += 1
                if isinstance(value, list):
                    val_str = f"[{len(value)} items]"
                else:
                    val_str = str(value)[:60]
                print(f"    {field}: {val_str}")

        print(f"\n  Completeness: {populated}/{len(key_fields)} key fields ({populated/len(key_fields):.0%})")
        print()

    print("="*80)
    print("RESULTS")
    print("="*80)
    print()
    print("If improved patterns work correctly, we should see:")
    print("  ✓ event_date extracted from all test cases")
    print("  ✓ city extracted (Medellín, Bogotá)")
    print("  ✓ venue extracted (Estadio Atanasio Girardot, Parque Simón Bolívar)")
    print("  ✓ attendance numbers extracted")
    print("  ✓ event_scale calculated based on attendance")
    print()
    print("If these aren't being extracted, the patterns need more work.")

if __name__ == '__main__':
    main()
