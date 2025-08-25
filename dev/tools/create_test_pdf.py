#!/usr/bin/env python3
"""
Create a simple test PDF for entity extraction testing
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

def create_test_pdf():
    """Create a simple test PDF with known entities"""
    
    # Create PDF file
    pdf_file = "test_data/simple_test.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']
    heading_style = styles['Heading2']
    
    # Add title
    elements.append(Paragraph("Technology Industry Leaders", title_style))
    elements.append(Spacer(1, 0.5*inch))
    
    # Add content with clear entities and relationships
    content_sections = [
        ("Apple Inc.", """
        Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in 1976. 
        The company is headquartered in Cupertino, California. Tim Cook became CEO in 2011,
        succeeding Steve Jobs. Apple designs and manufactures consumer electronics, computer 
        software, and online services. The iPhone, introduced in 2007, revolutionized the 
        smartphone industry.
        """),
        
        ("Microsoft Corporation", """
        Microsoft was founded by Bill Gates and Paul Allen in 1975. The company is based in 
        Redmond, Washington. Satya Nadella has served as CEO since 2014, replacing Steve Ballmer.
        Microsoft develops, manufactures, licenses, supports, and sells computer software, 
        consumer electronics, and personal computers. Windows operating system and Office suite 
        are among its flagship products.
        """),
        
        ("Google LLC", """
        Google was founded by Larry Page and Sergey Brin in 1998 while they were Ph.D. students
        at Stanford University. The company is headquartered in Mountain View, California. 
        Sundar Pichai became CEO of Google in 2015 and later CEO of Alphabet Inc. in 2019.
        Google specializes in Internet-related services and products, including search engines,
        online advertising, cloud computing, and software.
        """),
        
        ("Amazon.com Inc.", """
        Amazon was founded by Jeff Bezos in 1994, initially as an online bookstore. The company
        is headquartered in Seattle, Washington. Andy Jassy became CEO in 2021, succeeding 
        founder Jeff Bezos. Amazon is a multinational technology company focusing on e-commerce,
        cloud computing (AWS), digital streaming, and artificial intelligence.
        """),
        
        ("Tesla Inc.", """
        Tesla was founded by Martin Eberhard and Marc Tarpenning in 2003. Elon Musk joined
        the company in 2004 and became CEO in 2008. Tesla is headquartered in Austin, Texas.
        The company specializes in electric vehicles, energy storage, and solar panel 
        manufacturing. The Model S, introduced in 2012, established Tesla as a leader in 
        electric vehicle technology.
        """)
    ]
    
    # Add each section
    for heading, content in content_sections:
        elements.append(Paragraph(heading, heading_style))
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(content.strip(), normal_style))
        elements.append(Spacer(1, 0.3*inch))
    
    # Add summary section
    elements.append(Paragraph("Industry Connections", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("""
    These technology giants have numerous interconnections. Apple and Microsoft were early 
    competitors in the personal computer market. Google and Apple compete in mobile operating 
    systems with Android and iOS. Amazon Web Services competes with Microsoft Azure and 
    Google Cloud Platform. Tesla, under Elon Musk's leadership, has pushed traditional 
    automakers and tech companies to invest in electric and autonomous vehicles.
    """, normal_style))
    
    # Build PDF
    doc.build(elements)
    print(f"Test PDF created: {pdf_file}")
    
    # Return expected entities for verification
    expected_entities = {
        'PERSON': [
            'Steve Jobs', 'Steve Wozniak', 'Ronald Wayne', 'Tim Cook',
            'Bill Gates', 'Paul Allen', 'Satya Nadella', 'Steve Ballmer',
            'Larry Page', 'Sergey Brin', 'Sundar Pichai',
            'Jeff Bezos', 'Andy Jassy',
            'Martin Eberhard', 'Marc Tarpenning', 'Elon Musk'
        ],
        'ORGANIZATION': [
            'Apple Inc.', 'Microsoft', 'Google', 'Amazon', 'Tesla',
            'Stanford University', 'Alphabet Inc.'
        ],
        'LOCATION': [
            'Cupertino', 'California', 'Redmond', 'Washington',
            'Mountain View', 'Seattle', 'Austin', 'Texas'
        ],
        'PRODUCT': [
            'iPhone', 'Windows', 'Office', 'Android', 'iOS',
            'AWS', 'Azure', 'Google Cloud Platform', 'Model S'
        ]
    }
    
    print(f"\nExpected entities in PDF:")
    for entity_type, entities in expected_entities.items():
        print(f"  {entity_type}: {len(entities)} entities")
    
    return pdf_file, expected_entities

if __name__ == "__main__":
    try:
        import reportlab
        pdf_file, entities = create_test_pdf()
        print(f"\n✓ Success! PDF created with {sum(len(e) for e in entities.values())} expected entities")
    except ImportError:
        print("Error: reportlab not installed. Installing...")
        import subprocess
        subprocess.check_call(["pip", "install", "reportlab"])
        print("Installed reportlab. Please run the script again.")
    except Exception as e:
        print(f"Error creating PDF: {e}")
        import traceback
        traceback.print_exc()