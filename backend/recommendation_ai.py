from typing import List, Dict, Any, Optional
from decimal import Decimal
from backend.pricing_engine import UniversalPricingEngine

class AIEventRecommendationEngine:
    """
    Intelligent Rule-Based Event Recommendation & Optimization Engine.
    Evaluates event category, guest count, budget constraints, venue type,
    and Coimbatore locality specifics to recommend services with transparent reasoning.
    """
    
    @staticmethod
    def generate_recommendations(
        category_code: str,
        attendees: int,
        budget: float,
        venue_type: str,
        locality: str,
        indoor_outdoor: str,
        form_data: Dict[str, Any],
        available_services: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Synthesizes tailored recommendations, cost estimates, budget feasibility,
        and localized Coimbatore planning advice.
        """
        recommended_items = []
        cost_saving_tips = []
        
        # Index services by code for fast rule mapping
        service_map = {s["code"]: s for s in available_services}
        
        # Category specific rule heuristics
        cat = category_code.lower()
        
        if cat in ["wedding", "marriage", "family_ceremonies"]:
            # Rule 1: Stage Decoration
            if "wedding_stage_decor" in service_map:
                s = service_map["wedding_stage_decor"]
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Decoration"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": 1.0,
                    "unit_price": s["base_price"],
                    "estimated_cost": s["base_price"],
                    "priority": "Essential",
                    "reason": f"Grand focal point required for traditional South Indian ceremony and family portraits for {attendees} guests."
                })
            # Rule 2: Catering based on attendees
            if "traditional_banana_leaf_catering" in service_map:
                s = service_map["traditional_banana_leaf_catering"]
                cost = float(UniversalPricingEngine.calculate_item_cost(s["unit_type"], s["base_price"], attendees, attendees))
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Catering"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": float(attendees),
                    "unit_price": s["base_price"],
                    "estimated_cost": cost,
                    "priority": "Essential",
                    "reason": f"Authentic Kongu / Tamil traditional multi-course feast served on plantain leaves for {attendees} attendees."
                })
            # Rule 3: Photography
            if "candid_wedding_photography" in service_map:
                s = service_map["candid_wedding_photography"]
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Photography"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": 1.0,
                    "unit_price": s["base_price"],
                    "estimated_cost": s["base_price"],
                    "priority": "Essential",
                    "reason": "Complete two-day coverage with traditional muhurtham & drone cinematics."
                })
            # Rule 4: Nadaswaram / Live Music
            if "nadaswaram_tavil_troupe" in service_map:
                s = service_map["nadaswaram_tavil_troupe"]
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Entertainment"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": 1.0,
                    "unit_price": s["base_price"],
                    "estimated_cost": s["base_price"],
                    "priority": "Highly Recommended",
                    "reason": "Auspicious Mangala Isai performance during the sacred ceremony rituals."
                })
            # Rule 5: Seating
            if "banquet_cushion_chairs" in service_map:
                s = service_map["banquet_cushion_chairs"]
                cost = float(UniversalPricingEngine.calculate_item_cost(s["unit_type"], s["base_price"], attendees, attendees))
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Seating"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": float(attendees),
                    "unit_price": s["base_price"],
                    "estimated_cost": cost,
                    "priority": "Essential",
                    "reason": f"Comfortable cushioned seating with slipcovers for {attendees} invited guests."
                })

        elif cat in ["birthday", "personal_celebrations"]:
            # Birthday Rules
            age = form_data.get("age", "")
            if "birthday_theme_balloon_decor" in service_map:
                s = service_map["birthday_theme_balloon_decor"]
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Decoration"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": 1.0,
                    "unit_price": s["base_price"],
                    "estimated_cost": s["base_price"],
                    "priority": "Essential",
                    "reason": f"Customized vibrant balloon arch and themed backdrop tailored for {age if age else 'celebrant'}."
                })
            if "designer_custom_cake" in service_map:
                s = service_map["designer_custom_cake"]
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Catering"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": 3.0,  # 3 kg cake
                    "unit_price": s["base_price"],
                    "estimated_cost": s["base_price"] * 3.0,
                    "priority": "Essential",
                    "reason": f"Multi-tier handcrafted fondant cake scaled to serve {attendees} guests."
                })
            if "magic_show_or_mc" in service_map:
                s = service_map["magic_show_or_mc"]
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Entertainment"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": 1.0,
                    "unit_price": s["base_price"],
                    "estimated_cost": s["base_price"],
                    "priority": "Highly Recommended",
                    "reason": "Interactive party host, parlor magic, and party games to engage all age groups."
                })
            if "party_buffet_catering" in service_map:
                s = service_map["party_buffet_catering"]
                cost = float(UniversalPricingEngine.calculate_item_cost(s["unit_type"], s["base_price"], attendees, attendees))
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Catering"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": float(attendees),
                    "unit_price": s["base_price"],
                    "estimated_cost": cost,
                    "priority": "Essential",
                    "reason": f"Delicious party snack & live chat counters with dinner buffet for {attendees} attendees."
                })
            if "portrait_birthday_photography" in service_map:
                s = service_map["portrait_birthday_photography"]
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Photography"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": 1.0,
                    "unit_price": s["base_price"],
                    "estimated_cost": s["base_price"],
                    "priority": "Optional Upgrade",
                    "reason": "4-hour event documentary coverage with edited digital album & reel video."
                })

        elif cat in ["corporate", "corporate_business"]:
            # Corporate Rules
            if "audio_visual_projector_setup" in service_map:
                s = service_map["audio_visual_projector_setup"]
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Conference Equipment"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": 1.0,
                    "unit_price": s["base_price"],
                    "estimated_cost": s["base_price"],
                    "priority": "Essential",
                    "reason": f"High-lumen dual 4K laser projector screens and collar/podium wireless microphones for {attendees} delegates."
                })
            if "corporate_conference_stage" in service_map:
                s = service_map["corporate_conference_stage"]
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Stage"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": 1.0,
                    "unit_price": s["base_price"],
                    "estimated_cost": s["base_price"],
                    "priority": "Essential",
                    "reason": "Executive backdrop, branded lectern, VIP dais seating, and branded standees."
                })
            if "corporate_high_tea_lunch" in service_map:
                s = service_map["corporate_high_tea_lunch"]
                cost = float(UniversalPricingEngine.calculate_item_cost(s["unit_type"], s["base_price"], attendees, attendees))
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Catering"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": float(attendees),
                    "unit_price": s["base_price"],
                    "estimated_cost": cost,
                    "priority": "Essential",
                    "reason": f"2-session executive coffee/tea service plus multi-cuisine executive lunch buffet for {attendees} attendees."
                })
            if "registration_badging_desk" in service_map:
                s = service_map["registration_badging_desk"]
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Registration"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": 2.0,
                    "unit_price": s["base_price"],
                    "estimated_cost": s["base_price"] * 2.0,
                    "priority": "Highly Recommended",
                    "reason": "Streamlined attendee check-in desks with barcode/QR scanning and lanyard distribution."
                })

        elif cat in ["college", "educational_events"]:
            # College Symposium / Festival Rules
            if "symposium_audio_pa_system" in service_map:
                s = service_map["symposium_audio_pa_system"]
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Sound System"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": 1.0,
                    "unit_price": s["base_price"],
                    "estimated_cost": s["base_price"],
                    "priority": "Essential",
                    "reason": f"High-fidelity Line Array audio distribution for auditorium / open amphitheatre holding {attendees} students."
                })
            if "led_video_wall_p3" in service_map:
                s = service_map["led_video_wall_p3"]
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "LED Screens"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": 1.0,
                    "unit_price": s["base_price"],
                    "estimated_cost": s["base_price"],
                    "priority": "Highly Recommended",
                    "reason": "16x10 ft P3 high-res digital stage backdrop for presentations, keynote videos, and event sponsors."
                })
            if "student_refreshments_catering" in service_map:
                s = service_map["student_refreshments_catering"]
                cost = float(UniversalPricingEngine.calculate_item_cost(s["unit_type"], s["base_price"], attendees, attendees))
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Catering"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": float(attendees),
                    "unit_price": s["base_price"],
                    "estimated_cost": cost,
                    "priority": "Essential",
                    "reason": f"Hygienic packed food boxes + welcome refreshments for {attendees} participating students and faculty."
                })
            if "trophies_certificates_pack" in service_map:
                s = service_map["trophies_certificates_pack"]
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Awards"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": 1.0,
                    "unit_price": s["base_price"],
                    "estimated_cost": s["base_price"],
                    "priority": "Essential",
                    "reason": "Customized engraved mementos for chief guests and embossed winner trophies with certificates."
                })

        elif cat in ["cultural", "cultural_community"]:
            # Cultural Events
            if "cultural_dance_stage_setup" in service_map:
                s = service_map["cultural_dance_stage_setup"]
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Stage"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": 1.0,
                    "unit_price": s["base_price"],
                    "estimated_cost": s["base_price"],
                    "priority": "Essential",
                    "reason": "Spring-cushioned wooden platform with green-room partitions for Bharatanatyam and folk dancers."
                })
            if "theatre_lighting_rig" in service_map:
                s = service_map["theatre_lighting_rig"]
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Lighting"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": 1.0,
                    "unit_price": s["base_price"],
                    "estimated_cost": s["base_price"],
                    "priority": "Essential",
                    "reason": "Spotlight focus, ambient RGB washes, and stage warm profiles to accentuate classical performances."
                })
            if "green_room_artist_hospitality" in service_map:
                s = service_map["green_room_artist_hospitality"]
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Artist Management"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": 1.0,
                    "unit_price": s["base_price"],
                    "estimated_cost": s["base_price"],
                    "priority": "Highly Recommended",
                    "reason": "Dedicated artist coordination, makeup mirrors, iron boards, and performance refreshments."
                })

        elif cat in ["sports", "sports_outdoor"]:
            # Sports Events
            if "tournament_ground_marking_equipment" in service_map:
                s = service_map["tournament_ground_marking_equipment"]
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Sports Equipment"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": 1.0,
                    "unit_price": s["base_price"],
                    "estimated_cost": s["base_price"],
                    "priority": "Essential",
                    "reason": "Professional court/turf chalking, boundary ropes, nets, scoreboards, and umpire stands."
                })
            if "first_aid_medic_station" in service_map:
                s = service_map["first_aid_medic_station"]
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "First Aid"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": 1.0,
                    "unit_price": s["base_price"],
                    "estimated_cost": s["base_price"],
                    "priority": "Essential",
                    "reason": "Paramedic personnel equipped with ice packs, stretchers, CPR kits, and emergency physician on call."
                })
            if "hydration_electrolyte_station" in service_map:
                s = service_map["hydration_electrolyte_station"]
                cost = float(UniversalPricingEngine.calculate_item_cost(s["unit_type"], s["base_price"], attendees, attendees))
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Catering"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": float(attendees),
                    "unit_price": s["base_price"],
                    "estimated_cost": cost,
                    "priority": "Essential",
                    "reason": f"Chilled mineral water dispensers, glucose/electrolyte drinks, and energy bananas for {attendees} athletes."
                })
            if "sports_championship_medals" in service_map:
                s = service_map["sports_championship_medals"]
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "Awards"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": 1.0,
                    "unit_price": s["base_price"],
                    "estimated_cost": s["base_price"],
                    "priority": "Highly Recommended",
                    "reason": "Heavy metallic embossed gold/silver/bronze medals with branded Coimbatore tournament ribbons."
                })

        else:
            # Custom / General / Religious / Exhibitions fallback rules
            for s in available_services[:5]:
                cost = float(UniversalPricingEngine.calculate_item_cost(s["unit_type"], s["base_price"], 1.0, attendees))
                recommended_items.append({
                    "service_id": s["id"],
                    "service_name": s["name"],
                    "service_code": s["code"],
                    "category_name": s.get("category_name", "General"),
                    "unit_type": s["unit_type"],
                    "suggested_quantity": 1.0,
                    "unit_price": s["base_price"],
                    "estimated_cost": cost,
                    "priority": "Essential",
                    "reason": f"Core infrastructure selected to ensure smooth setup for your custom {cat.replace('_', ' ')} requirements."
                })

        # Calculate estimated sum with GST
        raw_subtotal = sum(item["estimated_cost"] for item in recommended_items)
        estimated_total = raw_subtotal * 1.18  # including 18% GST
        
        # Budget evaluation
        budget_diff = budget - estimated_total
        is_within_budget = budget_diff >= 0
        
        if budget > 0:
            if is_within_budget:
                feasibility_score = 95.0
                feasibility_status = "Optimal Budget Fit"
                explanation = f"Your budget of ₹{budget:,.2f} comfortably accommodates all essential and recommended services (Estimated: ₹{estimated_total:,.2f})."
            else:
                ratio = budget / estimated_total if estimated_total > 0 else 1.0
                feasibility_score = max(35.0, round(ratio * 100, 1))
                feasibility_status = "Budget Attention Needed"
                shortage = abs(budget_diff)
                explanation = f"The recommended standard setup totals ₹{estimated_total:,.2f}, which is ₹{shortage:,.2f} above your specified budget of ₹{budget:,.2f}."
                
                # Generate cost saving tips
                cost_saving_tips.append("Switch from live buffet counters to structured pre-set dining options to save ~15% on catering.")
                cost_saving_tips.append("Opt for combo sound & lighting packages rather than independent rentals.")
                cost_saving_tips.append(f"Consider hosting during off-peak weekday slots for venue discounts in {locality}.")
                cost_saving_tips.append("Fine-tune photography to prime ceremony hours instead of full 12-hour continuous coverage.")
        else:
            feasibility_score = 90.0
            feasibility_status = "Budget Estimation"
            explanation = f"Estimated baseline costs calculated at ₹{estimated_total:,.2f} based on {attendees} attendees."

        # Coimbatore Locality & Venue Specific Advisory
        venue_advice = f"In {locality}, ensure guest parking clearance with venue management ahead of peak hours. "
        if indoor_outdoor.lower() in ["outdoor", "both"]:
            venue_advice += "Because Coimbatore evenings can experience sudden breezy gusts or monsoon showers near the Western Ghats, ensure a water-resistant canopy cover is on standby."
        else:
            venue_advice += "Verify acoustic insulation and generator backup capacity with the hall manager."
            
        return {
            "feasibility_score": feasibility_score,
            "feasibility_status": feasibility_status,
            "budget_allocated": budget,
            "estimated_total": round(estimated_total, 2),
            "difference": round(budget_diff, 2),
            "is_within_budget": is_within_budget,
            "explanation": explanation,
            "recommendations": recommended_items,
            "cost_saving_tips": cost_saving_tips,
            "coimbatore_venue_advice": venue_advice
        }

recommendation_ai = AIEventRecommendationEngine()
