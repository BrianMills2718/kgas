"""Debug trend detection for AI safety"""

import asyncio
from datetime import datetime
from src.temporal.trend_detector import TrendDetector

async def debug_trends():
    detector = TrendDetector()
    
    # Create test documents
    documents = []
    for year in range(2020, 2025):
        for month in [1, 6, 12]:
            date = datetime(year, month, 1)
            
            # Evolving concept: AI Safety
            if year <= 2021:
                ai_content = "AI research focuses on performance and accuracy improvements."
            elif year <= 2022:
                ai_content = "AI safety concerns are emerging alongside performance gains."
            else:
                ai_content = "AI safety and alignment are now primary research priorities."
            
            # Emerging trend: Quantum Computing
            if year < 2022:
                quantum_content = "Quantum computing remains largely theoretical."
            elif year == 2022:
                quantum_content = "Quantum supremacy achieved in specific domains."
            else:
                quantum_content = "Practical quantum applications are being deployed."
            
            documents.append({
                "id": f"doc_{year}_{month}",
                "content": f"{ai_content} {quantum_content}",
                "timestamp": date.isoformat(),
                "metadata": {
                    "year": year,
                    "month": month,
                    "topics": ["AI", "Quantum Computing"]
                }
            })
    
    trends = await detector.detect_trends(documents, min_support=0.2)
    
    print(f"Found {len(trends)} trends:")
    for trend in trends:
        print(f"  - {trend.concept}: {trend.trend_type}")
        print(f"    Start: {trend.start_date}, End: {trend.end_date}")
        print(f"    Strength: {trend.strength:.2f}, Confidence: {trend.confidence:.2f}")
    
    emerging_trends = [t for t in trends if t.trend_type == "emerging"]
    print(f"\nEmerging trends: {[t.concept for t in emerging_trends]}")
    
    # Check specifically for safety
    safety_in_emerging = any("safety" in t.concept.lower() for t in emerging_trends)
    print(f"Safety in emerging trends: {safety_in_emerging}")

if __name__ == "__main__":
    asyncio.run(debug_trends())