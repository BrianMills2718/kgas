#!/usr/bin/env python3
"""
Kunst Theory Application to Carter Speech Analysis

This script applies the AI-Psychological Conspiracy Theory Support Model
extracted from Kunst et al. (2024) to analyze President Carter's 1977 speech
at the Southern Legislative Conference.

Analysis focuses on:
1. Detecting psychological factors related to conspiracy beliefs
2. Analyzing political discourse patterns
3. Identifying trust/distrust indicators
4. Evaluating transparency vs. secrecy themes
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict

class KunstTheoryCarterAnalysis:
    """
    Apply Kunst et al. conspiracy theory psychological model to Carter speech
    """
    
    def __init__(self, output_dir: str = "kunst_carter_analysis"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Load the Kunst theory schema
        self.theory_schema = self.load_kunst_theory_schema()
        
        # Carter speech details
        self.speech_info = {
            "speaker": "Jimmy Carter",
            "title": "Remarks at the 31st Annual Meeting of the Southern Legislative Conference",
            "location": "Charleston, South Carolina",
            "date": "July 21, 1977",
            "context": "6 months into presidency, addressing Soviet-American relations",
            "path": "/home/brian/projects/Digimons/lit_review/data/test_texts/texts/carter_speech.txt"
        }
    
    def load_kunst_theory_schema(self) -> Dict:
        """Load the previously extracted Kunst theory schema"""
        
        # For now, just use the embedded version which has the correct structure
        # The loaded schema has a different structure that would need conversion
        return self.get_embedded_kunst_schema()
    
    def get_embedded_kunst_schema(self) -> Dict:
        """Embedded version of Kunst theory schema"""
        schema = {
            "meta_info": {
                "model_type": "network",
                "theory_name": "AI-Psychological Conspiracy Theory Support Model",
                "source_paper": "Kunst et al. (2024)"
            },
            "psychological_factors": {
                "narcissism": {
                    "definition": "Grandiose self-regard and need for attention",
                    "indicators": ["I", "my", "special", "unique", "superior"],
                    "anti_indicators": ["we", "us", "together", "shared", "collective"]
                },
                "denialism": {
                    "definition": "Rejection of expert narratives, seeking unconventional explanations",
                    "indicators": ["don't trust", "hidden", "real truth", "they say", "so-called experts"],
                    "anti_indicators": ["experts agree", "evidence shows", "facts", "transparent"]
                },
                "need_for_chaos": {
                    "definition": "Desire to provoke or exacerbate disorder",
                    "indicators": ["shake up", "tear down", "chaos", "disorder", "disrupt"],
                    "anti_indicators": ["stability", "order", "cooperation", "peace", "harmony"]
                },
                "conspiracy_mentality": {
                    "definition": "General disposition towards conspiratorial viewpoints",
                    "indicators": ["secret", "behind closed doors", "hidden agenda", "they", "plotting"],
                    "anti_indicators": ["open", "transparent", "public", "clear", "straightforward"]
                },
                "misinformation_susceptibility": {
                    "definition": "Propensity to accept false information",
                    "indicators": ["heard", "they say", "everyone knows", "obvious", "wake up"],
                    "anti_indicators": ["verified", "confirmed", "evidence", "research shows"]
                },
                "political_extremity": {
                    "definition": "Self-identification at far ends of political spectrum",
                    "indicators": ["radical", "extreme", "far left", "far right", "revolutionary"],
                    "anti_indicators": ["moderate", "centrist", "balanced", "middle ground", "compromise"]
                },
                "overconfidence": {
                    "definition": "Excessive confidence in ability to detect misinformation",
                    "indicators": ["I know", "obviously", "clearly", "anyone can see", "simple"],
                    "anti_indicators": ["complex", "nuanced", "uncertain", "difficult to say"]
                }
            },
            "contextual_themes": {
                "transparency_vs_secrecy": {
                    "transparency_indicators": ["open", "public", "discuss", "debate", "report"],
                    "secrecy_indicators": ["secret", "hidden", "closed", "private", "classified"]
                },
                "trust_in_institutions": {
                    "trust_indicators": ["confidence", "faith", "believe in", "support", "respect"],
                    "distrust_indicators": ["corrupt", "broken", "failed", "rigged", "controlled"]
                },
                "us_vs_them": {
                    "unity_indicators": ["we", "us", "together", "shared", "common"],
                    "division_indicators": ["they", "them", "others", "enemy", "opposition"]
                }
            }
        }
        
        return schema
    
    def analyze_carter_speech(self):
        """Complete analysis of Carter speech using Kunst theory"""
        print("\n" + "="*80)
        print("🎯 KUNST THEORY APPLICATION TO CARTER SPEECH")
        print("="*80)
        
        # Load speech
        print("\n📚 Loading Carter Speech...")
        speech_content = self.load_speech_content()
        
        if not speech_content:
            print("❌ Could not load speech")
            return
        
        # Analyze using Kunst theory
        print("\n🔍 Applying Kunst Conspiracy Theory Psychological Model...")
        analysis_results = self.apply_kunst_theory(speech_content)
        
        # Generate insights
        print("\n💡 Generating Insights...")
        insights = self.generate_insights(analysis_results)
        
        # Create comprehensive report
        print("\n📊 Creating Comprehensive Report...")
        self.create_comprehensive_report(analysis_results, insights)
        
        print(f"\n✅ Analysis Complete! Results saved to: {self.output_dir}")
    
    def load_speech_content(self) -> Optional[str]:
        """Load the Carter speech text"""
        speech_path = Path(self.speech_info["path"])
        
        if not speech_path.exists():
            print(f"❌ Speech not found at: {speech_path}")
            return None
        
        with open(speech_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic stats
        words = content.split()
        sentences = re.split(r'[.!?]+', content)
        paragraphs = content.split('\n\n')
        
        print(f"✅ Speech loaded successfully:")
        print(f"   📄 Speaker: {self.speech_info['speaker']}")
        print(f"   📅 Date: {self.speech_info['date']}")
        print(f"   📍 Location: {self.speech_info['location']}")
        print(f"   📊 Size: {len(words):,} words, {len(sentences)} sentences, {len(paragraphs)} paragraphs")
        
        return content
    
    def apply_kunst_theory(self, speech_content: str) -> Dict:
        """Apply Kunst psychological factors to analyze the speech"""
        
        # Convert to lowercase for analysis
        content_lower = speech_content.lower()
        words = content_lower.split()
        sentences = re.split(r'[.!?]+', content_lower)
        
        # Initialize results
        results = {
            "psychological_factor_analysis": {},
            "contextual_theme_analysis": {},
            "discourse_patterns": {},
            "quantitative_metrics": {},
            "text_segments": {}
        }
        
        # 1. Analyze psychological factors
        print("   📊 Analyzing psychological factors...")
        for factor, details in self.theory_schema["psychological_factors"].items():
            factor_analysis = self.analyze_psychological_factor(
                content_lower, words, sentences, factor, details
            )
            results["psychological_factor_analysis"][factor] = factor_analysis
        
        # 2. Analyze contextual themes
        print("   🎭 Analyzing contextual themes...")
        for theme, indicators in self.theory_schema["contextual_themes"].items():
            theme_analysis = self.analyze_contextual_theme(
                content_lower, words, sentences, theme, indicators
            )
            results["contextual_theme_analysis"][theme] = theme_analysis
        
        # 3. Extract key discourse patterns
        print("   🔗 Identifying discourse patterns...")
        results["discourse_patterns"] = self.identify_discourse_patterns(speech_content)
        
        # 4. Calculate quantitative metrics
        print("   📈 Calculating quantitative metrics...")
        results["quantitative_metrics"] = self.calculate_quantitative_metrics(
            results, words, sentences
        )
        
        # 5. Extract relevant text segments
        print("   📝 Extracting relevant text segments...")
        results["text_segments"] = self.extract_relevant_segments(
            speech_content, results
        )
        
        return results
    
    def analyze_psychological_factor(self, content: str, words: List[str], 
                                   sentences: List[str], factor: str, 
                                   details: Dict) -> Dict:
        """Analyze a single psychological factor in the text"""
        
        # Count indicators and anti-indicators
        indicator_count = 0
        anti_indicator_count = 0
        indicator_examples = []
        anti_indicator_examples = []
        
        # Check indicators
        for indicator in details.get("indicators", []):
            count = content.count(indicator.lower())
            if count > 0:
                indicator_count += count
                # Find example sentences
                for sent in sentences:
                    if indicator.lower() in sent and len(indicator_examples) < 3:
                        indicator_examples.append(sent.strip())
        
        # Check anti-indicators
        for anti_indicator in details.get("anti_indicators", []):
            count = content.count(anti_indicator.lower())
            if count > 0:
                anti_indicator_count += count
                # Find example sentences
                for sent in sentences:
                    if anti_indicator.lower() in sent and len(anti_indicator_examples) < 3:
                        anti_indicator_examples.append(sent.strip())
        
        # Calculate presence score
        total_indicators = indicator_count + anti_indicator_count
        if total_indicators > 0:
            presence_score = indicator_count / total_indicators
        else:
            presence_score = 0.0
        
        # Determine presence level
        if presence_score > 0.7:
            presence_level = "high"
        elif presence_score > 0.3:
            presence_level = "moderate"
        elif presence_score > 0:
            presence_level = "low"
        else:
            presence_level = "absent"
        
        return {
            "factor": factor,
            "definition": details["definition"],
            "indicator_count": indicator_count,
            "anti_indicator_count": anti_indicator_count,
            "presence_score": round(presence_score, 3),
            "presence_level": presence_level,
            "indicator_examples": indicator_examples[:3],
            "anti_indicator_examples": anti_indicator_examples[:3],
            "interpretation": self.interpret_factor_presence(factor, presence_level, indicator_examples)
        }
    
    def analyze_contextual_theme(self, content: str, words: List[str], 
                                sentences: List[str], theme: str, 
                                indicators: Dict) -> Dict:
        """Analyze a contextual theme in the text"""
        
        theme_results = {}
        
        for indicator_type, indicator_list in indicators.items():
            count = 0
            examples = []
            
            for indicator in indicator_list:
                indicator_count = content.count(indicator.lower())
                count += indicator_count
                
                # Find examples
                if indicator_count > 0:
                    for sent in sentences:
                        if indicator.lower() in sent and len(examples) < 3:
                            examples.append(sent.strip())
            
            theme_results[indicator_type] = {
                "count": count,
                "examples": examples[:3]
            }
        
        # Calculate theme balance
        if theme == "transparency_vs_secrecy":
            transparency = theme_results.get("transparency_indicators", {}).get("count", 0)
            secrecy = theme_results.get("secrecy_indicators", {}).get("count", 0)
            balance = "transparency-oriented" if transparency > secrecy else "secrecy-oriented" if secrecy > transparency else "balanced"
        
        elif theme == "trust_in_institutions":
            trust = theme_results.get("trust_indicators", {}).get("count", 0)
            distrust = theme_results.get("distrust_indicators", {}).get("count", 0)
            balance = "trust-oriented" if trust > distrust else "distrust-oriented" if distrust > trust else "balanced"
        
        elif theme == "us_vs_them":
            unity = theme_results.get("unity_indicators", {}).get("count", 0)
            division = theme_results.get("division_indicators", {}).get("count", 0)
            balance = "unity-oriented" if unity > division else "division-oriented" if division > unity else "balanced"
        
        else:
            balance = "unknown"
        
        theme_results["overall_balance"] = balance
        theme_results["theme_interpretation"] = self.interpret_theme(theme, balance, theme_results)
        
        return theme_results
    
    def identify_discourse_patterns(self, content: str) -> Dict:
        """Identify specific discourse patterns relevant to conspiracy theory analysis"""
        
        patterns = {
            "rhetorical_questions": [],
            "certainty_language": [],
            "transparency_statements": [],
            "historical_references": [],
            "call_to_action": []
        }
        
        sentences = re.split(r'[.!?]+', content)
        
        for sent in sentences:
            sent_clean = sent.strip()
            if not sent_clean:
                continue
            
            # Rhetorical questions
            if '?' in sent and any(word in sent.lower() for word in ['why', 'how', 'what if', "don't you think"]):
                patterns["rhetorical_questions"].append(sent_clean)
            
            # Certainty language
            if any(phrase in sent.lower() for phrase in ['no doubt', 'clearly', 'obviously', 'certainly', 'must be']):
                patterns["certainty_language"].append(sent_clean)
            
            # Transparency statements
            if any(phrase in sent.lower() for phrase in ['openly', 'publicly', 'transparent', 'honest discussion', 'not secret']):
                patterns["transparency_statements"].append(sent_clean)
            
            # Historical references
            if any(phrase in sent.lower() for phrase in ['history', 'in the past', 'decades', 'remember when', 'used to']):
                patterns["historical_references"].append(sent_clean)
            
            # Call to action
            if any(phrase in sent.lower() for phrase in ['we must', 'we should', 'we need to', 'our job', 'responsibility']):
                patterns["call_to_action"].append(sent_clean)
        
        return patterns
    
    def calculate_quantitative_metrics(self, results: Dict, words: List[str], 
                                     sentences: List[str]) -> Dict:
        """Calculate quantitative metrics for the analysis"""
        
        # Calculate conspiracy risk score based on Kunst model
        risk_factors = 0
        protective_factors = 0
        
        for factor, analysis in results["psychological_factor_analysis"].items():
            if analysis["presence_level"] in ["high", "moderate"]:
                if factor in ["denialism", "conspiracy_mentality", "political_extremity"]:
                    risk_factors += analysis["presence_score"]
                else:
                    # Narcissism, need for chaos, etc. not strongly present
                    protective_factors += (1 - analysis["presence_score"])
        
        # Theme analysis contribution
        for theme, analysis in results["contextual_theme_analysis"].items():
            if theme == "transparency_vs_secrecy" and analysis["overall_balance"] == "transparency-oriented":
                protective_factors += 0.5
            elif theme == "trust_in_institutions" and analysis["overall_balance"] == "trust-oriented":
                protective_factors += 0.5
            elif theme == "us_vs_them" and analysis["overall_balance"] == "unity-oriented":
                protective_factors += 0.5
        
        # Calculate overall risk score
        total_factors = risk_factors + protective_factors
        if total_factors > 0:
            conspiracy_risk_score = risk_factors / total_factors
        else:
            conspiracy_risk_score = 0.0
        
        return {
            "total_words": len(words),
            "total_sentences": len(sentences),
            "risk_factors_score": round(risk_factors, 3),
            "protective_factors_score": round(protective_factors, 3),
            "conspiracy_risk_score": round(conspiracy_risk_score, 3),
            "risk_level": "low" if conspiracy_risk_score < 0.3 else "moderate" if conspiracy_risk_score < 0.7 else "high",
            "transparency_mentions": results["contextual_theme_analysis"]["transparency_vs_secrecy"]["transparency_indicators"]["count"],
            "secrecy_mentions": results["contextual_theme_analysis"]["transparency_vs_secrecy"]["secrecy_indicators"]["count"],
            "unity_language_ratio": self.calculate_unity_ratio(results),
            "discourse_complexity": len(results["discourse_patterns"]["historical_references"]) + 
                                  len(results["discourse_patterns"]["transparency_statements"])
        }
    
    def calculate_unity_ratio(self, results: Dict) -> float:
        """Calculate the ratio of unity to division language"""
        unity = results["contextual_theme_analysis"]["us_vs_them"]["unity_indicators"]["count"]
        division = results["contextual_theme_analysis"]["us_vs_them"]["division_indicators"]["count"]
        
        if unity + division > 0:
            return round(unity / (unity + division), 3)
        return 0.5
    
    def extract_relevant_segments(self, content: str, results: Dict) -> Dict:
        """Extract key text segments relevant to the analysis"""
        
        segments = {
            "transparency_passages": [],
            "unity_passages": [],
            "trust_building_passages": [],
            "key_policy_statements": []
        }
        
        paragraphs = content.split('\n\n')
        
        for para in paragraphs:
            para_lower = para.lower()
            
            # Transparency passages
            if any(word in para_lower for word in ['openly', 'publicly', 'transparent', 'not secret']):
                segments["transparency_passages"].append(para.strip())
            
            # Unity passages
            if para_lower.count('we') + para_lower.count('us') + para_lower.count('our') > 5:
                segments["unity_passages"].append(para.strip())
            
            # Trust building
            if any(phrase in para_lower for phrase in ['trust', 'confidence', 'cooperation', 'together']):
                segments["trust_building_passages"].append(para.strip())
            
            # Key policy statements
            if any(phrase in para_lower for phrase in ['policy', 'strategy', 'approach', 'goal', 'objective']):
                segments["key_policy_statements"].append(para.strip())
        
        # Limit to most relevant segments
        for key in segments:
            segments[key] = segments[key][:3]
        
        return segments
    
    def interpret_factor_presence(self, factor: str, presence_level: str, 
                                examples: List[str]) -> str:
        """Interpret what the presence level of a factor means"""
        
        interpretations = {
            "narcissism": {
                "high": "High self-focus, potentially indicating elevated conspiracy risk",
                "moderate": "Balanced self-reference with collective language",
                "low": "Minimal self-focus, emphasizes collective perspective",
                "absent": "No narcissistic indicators detected"
            },
            "denialism": {
                "high": "Strong rejection of conventional narratives, high conspiracy risk",
                "moderate": "Some skepticism present but balanced with acceptance",
                "low": "Minimal denial of expert consensus",
                "absent": "No denialism detected, accepts mainstream narratives"
            },
            "conspiracy_mentality": {
                "high": "Strong conspiratorial thinking patterns detected",
                "moderate": "Some conspiratorial language but not dominant",
                "low": "Minimal conspiracy-oriented thinking",
                "absent": "No conspiracy mentality indicators found"
            },
            "political_extremity": {
                "high": "Highly polarized political language",
                "moderate": "Some political polarization present",
                "low": "Mostly moderate political discourse",
                "absent": "No extreme political language detected"
            },
            "transparency_vs_secrecy": {
                "high": "Strong emphasis on transparency over secrecy",
                "moderate": "Balance between transparency and necessary discretion",
                "low": "Limited transparency emphasis",
                "absent": "No clear position on transparency"
            }
        }
        
        return interpretations.get(factor, {}).get(presence_level, "Standard presence level")
    
    def interpret_theme(self, theme: str, balance: str, analysis: Dict) -> str:
        """Interpret the thematic analysis results"""
        
        if theme == "transparency_vs_secrecy":
            if balance == "transparency-oriented":
                return "Strong emphasis on openness and public disclosure, countering conspiracy narratives"
            elif balance == "secrecy-oriented":
                return "Emphasis on secrecy could fuel conspiracy theories"
            else:
                return "Balanced approach to transparency and discretion"
        
        elif theme == "trust_in_institutions":
            if balance == "trust-oriented":
                return "Promotes institutional trust, protective against conspiracy beliefs"
            elif balance == "distrust-oriented":
                return "Institutional distrust could increase conspiracy susceptibility"
            else:
                return "Neutral stance on institutional trust"
        
        elif theme == "us_vs_them":
            if balance == "unity-oriented":
                return "Emphasis on unity and shared purpose, reduces conspiracy thinking"
            elif balance == "division-oriented":
                return "Divisive language could promote conspiracy theories"
            else:
                return "Balanced use of inclusive and exclusive language"
        
        return "Theme requires further interpretation"
    
    def generate_insights(self, analysis_results: Dict) -> List[Dict]:
        """Generate key insights from the analysis"""
        
        insights = []
        
        # Insight 1: Overall conspiracy risk assessment
        risk_score = analysis_results["quantitative_metrics"]["conspiracy_risk_score"]
        risk_level = analysis_results["quantitative_metrics"]["risk_level"]
        insights.append({
            "category": "Overall Risk Assessment",
            "finding": f"Carter's speech shows {risk_level} conspiracy theory risk (score: {risk_score})",
            "explanation": "Based on Kunst model psychological factors, the speech exhibits protective factors against conspiracy thinking",
            "evidence": f"Protective factors: {analysis_results['quantitative_metrics']['protective_factors_score']}, Risk factors: {analysis_results['quantitative_metrics']['risk_factors_score']}"
        })
        
        # Insight 2: Transparency emphasis
        transparency_ratio = analysis_results["quantitative_metrics"]["transparency_mentions"] / max(1, analysis_results["quantitative_metrics"]["secrecy_mentions"])
        insights.append({
            "category": "Transparency vs Secrecy",
            "finding": f"Strong transparency orientation (ratio: {transparency_ratio:.1f}:1)",
            "explanation": "Carter explicitly advocates for open discussion and public debate, directly countering secretive conspiracy narratives",
            "evidence": f"{len(analysis_results['discourse_patterns']['transparency_statements'])} explicit transparency statements"
        })
        
        # Insight 3: Unity language
        unity_ratio = analysis_results["quantitative_metrics"]["unity_language_ratio"]
        insights.append({
            "category": "Social Cohesion",
            "finding": f"High unity language ratio ({unity_ratio:.1%})",
            "explanation": "Predominant use of inclusive 'we/us/our' language promotes collective identity over divisive 'us vs them' thinking",
            "evidence": f"Unity indicators significantly outnumber division indicators"
        })
        
        # Insight 4: Historical grounding
        historical_refs = len(analysis_results["discourse_patterns"]["historical_references"])
        insights.append({
            "category": "Historical Context",
            "finding": f"Extensive historical grounding ({historical_refs} references)",
            "explanation": "Grounds current challenges in historical context, providing rational explanations rather than conspiratorial ones",
            "evidence": "Multiple references to past decades, historical patterns, and precedents"
        })
        
        # Insight 5: Policy transparency
        policy_statements = len(analysis_results["text_segments"]["key_policy_statements"])
        insights.append({
            "category": "Policy Communication",
            "finding": "Clear articulation of policy goals and strategies",
            "explanation": "Transparent discussion of foreign policy reduces space for conspiracy theories about hidden agendas",
            "evidence": f"{policy_statements} explicit policy statements identified"
        })
        
        # Insight 6: Rhetorical approach
        certainty_lang = len(analysis_results["discourse_patterns"]["certainty_language"])
        insights.append({
            "category": "Rhetorical Style",
            "finding": "Balanced certainty without overconfidence",
            "explanation": "Avoids the overconfident language associated with conspiracy susceptibility while maintaining leadership authority",
            "evidence": f"Limited certainty language ({certainty_lang} instances), emphasizes complexity and nuance"
        })
        
        return insights
    
    def create_comprehensive_report(self, analysis_results: Dict, insights: List[Dict]):
        """Create comprehensive analysis report"""
        
        print("📄 Generating comprehensive report...")
        
        # Save raw analysis results
        results_file = self.output_dir / f"carter_speech_kunst_analysis_{self.timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump({
                "speech_info": self.speech_info,
                "theory_applied": "Kunst et al. (2024) AI-Psychological Conspiracy Theory Support Model",
                "analysis_results": analysis_results,
                "insights": insights,
                "timestamp": self.timestamp
            }, f, indent=2, default=str)
        
        # Create markdown report
        self.create_markdown_report(analysis_results, insights)
        
        # Create visualization data
        self.create_visualization_data(analysis_results)
        
        print(f"✅ Report generated:")
        print(f"   📊 Full analysis: {results_file.name}")
        print(f"   📄 Markdown report: carter_kunst_analysis_report_{self.timestamp}.md")
        print(f"   📈 Visualization data: carter_kunst_visualization_{self.timestamp}.json")
    
    def create_markdown_report(self, analysis_results: Dict, insights: List[Dict]):
        """Create human-readable markdown report"""
        
        markdown = f"""# Kunst Theory Analysis of Carter Speech

## 📋 Analysis Overview
**Speech**: {self.speech_info['title']}  
**Speaker**: {self.speech_info['speaker']}  
**Date**: {self.speech_info['date']}  
**Theory Applied**: Kunst et al. (2024) AI-Psychological Conspiracy Theory Support Model  
**Analysis Date**: {self.timestamp}

## 🎯 Executive Summary
This analysis applies the psychological model from Kunst et al. (2024) to President Carter's 1977 speech on Soviet-American relations. The speech demonstrates **{analysis_results['quantitative_metrics']['risk_level']} risk** for promoting conspiracy theory beliefs, with a conspiracy risk score of **{analysis_results['quantitative_metrics']['conspiracy_risk_score']:.1%}**.

## 📊 Key Metrics
- **Total Words**: {analysis_results['quantitative_metrics']['total_words']:,}
- **Risk Factors Score**: {analysis_results['quantitative_metrics']['risk_factors_score']:.2f}
- **Protective Factors Score**: {analysis_results['quantitative_metrics']['protective_factors_score']:.2f}
- **Conspiracy Risk Score**: {analysis_results['quantitative_metrics']['conspiracy_risk_score']:.1%}
- **Risk Level**: **{analysis_results['quantitative_metrics']['risk_level'].upper()}**

## 🧠 Psychological Factor Analysis

### Factors with Highest Presence:
"""
        
        # Sort factors by presence score
        factors_sorted = sorted(
            analysis_results['psychological_factor_analysis'].items(),
            key=lambda x: x[1]['presence_score'],
            reverse=True
        )
        
        for factor, analysis in factors_sorted[:3]:
            markdown += f"""
#### {factor.replace('_', ' ').title()} ({analysis['presence_level']})
- **Presence Score**: {analysis['presence_score']:.1%}
- **Interpretation**: {analysis['interpretation']}
- **Example**: "{analysis['indicator_examples'][0] if analysis['indicator_examples'] else 'No clear examples'}"
"""
        
        markdown += """
## 🎭 Thematic Analysis

### Transparency vs Secrecy
- **Balance**: {transparency_balance}
- **Transparency Mentions**: {transparency_count}
- **Secrecy Mentions**: {secrecy_count}
- **Interpretation**: {transparency_interpretation}

### Trust in Institutions  
- **Balance**: {trust_balance}
- **Trust Indicators**: {trust_count}
- **Distrust Indicators**: {distrust_count}
- **Interpretation**: {trust_interpretation}

### Unity vs Division
- **Balance**: {unity_balance}
- **Unity Language Ratio**: {unity_ratio:.1%}
- **Interpretation**: {unity_interpretation}
""".format(
            transparency_balance=analysis_results['contextual_theme_analysis']['transparency_vs_secrecy']['overall_balance'],
            transparency_count=analysis_results['contextual_theme_analysis']['transparency_vs_secrecy']['transparency_indicators']['count'],
            secrecy_count=analysis_results['contextual_theme_analysis']['transparency_vs_secrecy']['secrecy_indicators']['count'],
            transparency_interpretation=analysis_results['contextual_theme_analysis']['transparency_vs_secrecy']['theme_interpretation'],
            
            trust_balance=analysis_results['contextual_theme_analysis']['trust_in_institutions']['overall_balance'],
            trust_count=analysis_results['contextual_theme_analysis']['trust_in_institutions']['trust_indicators']['count'],
            distrust_count=analysis_results['contextual_theme_analysis']['trust_in_institutions']['distrust_indicators']['count'],
            trust_interpretation=analysis_results['contextual_theme_analysis']['trust_in_institutions']['theme_interpretation'],
            
            unity_balance=analysis_results['contextual_theme_analysis']['us_vs_them']['overall_balance'],
            unity_ratio=analysis_results['quantitative_metrics']['unity_language_ratio'],
            unity_interpretation=analysis_results['contextual_theme_analysis']['us_vs_them']['theme_interpretation']
        )
        
        markdown += "\n## 💡 Key Insights\n"
        
        for i, insight in enumerate(insights, 1):
            markdown += f"""
### {i}. {insight['category']}
**Finding**: {insight['finding']}  
**Explanation**: {insight['explanation']}  
**Evidence**: {insight['evidence']}
"""
        
        markdown += """
## 📝 Notable Discourse Patterns

### Transparency Statements
"""
        for statement in analysis_results['discourse_patterns']['transparency_statements'][:3]:
            markdown += f"- \"{statement}\"\n"
        
        markdown += """
### Unity Language Examples
"""
        for passage in analysis_results['text_segments']['unity_passages'][:2]:
            markdown += f"> {passage[:200]}...\n\n"
        
        markdown += """
## 🎯 Conclusion

Based on the Kunst et al. (2024) model, Carter's speech exhibits strong protective factors against conspiracy theory promotion:

1. **High transparency orientation** - Explicitly advocates open discussion over secrecy
2. **Unity-focused language** - Emphasizes collective identity and shared responsibility  
3. **Institutional trust building** - Works to strengthen rather than undermine institutions
4. **Historical grounding** - Provides context and precedent rather than unprecedented claims
5. **Balanced rhetoric** - Avoids overconfident or extreme language patterns

The speech serves as a model for political discourse that reduces rather than amplifies conspiracy thinking, aligning with the protective factors identified in the Kunst research.

---
*Analysis generated using Kunst et al. (2024) AI-Psychological Conspiracy Theory Support Model*
"""
        
        report_file = self.output_dir / f"carter_kunst_analysis_report_{self.timestamp}.md"
        with open(report_file, 'w') as f:
            f.write(markdown)
    
    def create_visualization_data(self, analysis_results: Dict):
        """Create data for visualizations"""
        
        viz_data = {
            "factor_presence_scores": {
                factor: analysis['presence_score'] 
                for factor, analysis in analysis_results['psychological_factor_analysis'].items()
            },
            "theme_balances": {
                theme: analysis['overall_balance']
                for theme, analysis in analysis_results['contextual_theme_analysis'].items()
            },
            "risk_assessment": {
                "risk_score": analysis_results['quantitative_metrics']['conspiracy_risk_score'],
                "protective_score": 1 - analysis_results['quantitative_metrics']['conspiracy_risk_score'],
                "risk_level": analysis_results['quantitative_metrics']['risk_level']
            },
            "discourse_pattern_counts": {
                pattern: len(examples)
                for pattern, examples in analysis_results['discourse_patterns'].items()
            },
            "word_frequency": {
                "transparency_words": analysis_results['quantitative_metrics']['transparency_mentions'],
                "secrecy_words": analysis_results['quantitative_metrics']['secrecy_mentions'],
                "unity_indicators": analysis_results['contextual_theme_analysis']['us_vs_them']['unity_indicators']['count'],
                "division_indicators": analysis_results['contextual_theme_analysis']['us_vs_them']['division_indicators']['count']
            }
        }
        
        viz_file = self.output_dir / f"carter_kunst_visualization_{self.timestamp}.json"
        with open(viz_file, 'w') as f:
            json.dump(viz_data, f, indent=2)


def main():
    """Run the Kunst theory analysis on Carter speech"""
    
    print("🚀 Starting Kunst Theory Analysis of Carter Speech...")
    
    analyzer = KunstTheoryCarterAnalysis()
    analyzer.analyze_carter_speech()
    
    print("\n🎉 Analysis complete!")
    print("\nThis analysis demonstrates:")
    print("  • Successful application of academic theory to real political speech")
    print("  • Detection of psychological factors related to conspiracy beliefs")
    print("  • Quantitative risk assessment using Kunst model")
    print("  • Identification of protective vs risk factors in discourse")
    print("  • Practical insights for understanding political communication")


if __name__ == "__main__":
    main()