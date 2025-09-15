import reflex as rx
import re
from typing import Dict, Optional

class PricingState(rx.State):
    """State for the pricing calculator app."""
    
    ingredient_name: str = ""
    quantity_input: str = ""
    price_input: str = ""
    selected_unit: str = "kg"
    results: Dict[str, float] = {}
    error_message: str = ""
    
    def set_ingredient_name(self, name: str):
        self.ingredient_name = name
    
    def set_quantity_input(self, quantity: str):
        self.quantity_input = quantity
    
    def set_price_input(self, price: str):
        self.price_input = price
    
    def set_selected_unit(self, unit: str):
        self.selected_unit = unit
    
    def parse_quantity(self, quantity_str: str) -> Optional[float]:
        """Parse quantity string and return total grams."""
        try:
            # Remove spaces and convert to lowercase
            quantity_str = quantity_str.replace(" ", "").lower()
            
            # Handle multiplication format (e.g., "10x100g", "20*1200g")
            mult_pattern = r'(\d+)[x*](\d+(?:\.\d+)?)([a-z]*)'  
            mult_match = re.match(mult_pattern, quantity_str)
            
            if mult_match:
                count = float(mult_match.group(1))
                weight = float(mult_match.group(2))
                unit = mult_match.group(3) or "g"  # default to grams
                total_weight = count * weight
            else:
                # Handle single quantity format (e.g., "400g", "1.2kg")
                single_pattern = r'(\d+(?:\.\d+)?)([a-z]*)'  
                single_match = re.match(single_pattern, quantity_str)
                
                if single_match:
                    total_weight = float(single_match.group(1))
                    unit = single_match.group(2) or "g"  # default to grams
                else:
                    return None
            
            # Convert to grams
            if unit in ["kg", "kilogram", "kilograms"]:
                return total_weight * 1000
            elif unit in ["g", "gram", "grams", ""]:
                return total_weight
            elif unit in ["mg", "milligram", "milligrams"]:
                return total_weight / 1000
            else:
                return None
                
        except (ValueError, AttributeError):
            return None
    
    def calculate_pricing(self):
        """Calculate pricing per different units."""
        self.error_message = ""
        self.results = {}
        
        if not self.ingredient_name.strip():
            self.error_message = "Please enter an ingredient name."
            return
        
        if not self.quantity_input.strip():
            self.error_message = "Please enter a quantity."
            return
        
        if not self.price_input.strip():
            self.error_message = "Please enter a price."
            return
        
        try:
            price = float(self.price_input)
        except ValueError:
            self.error_message = "Please enter a valid price."
            return
        
        total_grams = self.parse_quantity(self.quantity_input)
        
        if total_grams is None:
            self.error_message = "Invalid quantity format. Use formats like '10x100g', '400g', '1.2kg'."
            return
        
        if total_grams <= 0:
            self.error_message = "Quantity must be greater than zero."
            return
        
        # Calculate price per gram
        price_per_gram = price / total_grams
        
        # Calculate for different units
        self.results = {
            "kg": price_per_gram * 1000,
            "g": price_per_gram,
            "mg": price_per_gram / 1000
        }
    
    def clear_form(self):
        """Clear all form inputs and results."""
        self.ingredient_name = ""
        self.quantity_input = ""
        self.price_input = ""
        self.selected_unit = "kg"
        self.results = {}
        self.error_message = ""

def create_logo():
    """Create Mordor Intelligence logo placeholder."""
    return rx.hstack(
        rx.box(
            rx.text("MI", font_size="2xl", font_weight="bold", color="#1e40af"),
            bg="white",
            border_radius="8px",
            padding="8px",
            border="2px solid #1e40af"
        ),
        rx.vstack(
            rx.text("Mordor Intelligence", font_size="xl", font_weight="bold", color="#1e40af"),
            rx.text("Pricing Calculator", font_size="md", color="#64748b"),
            align_items="start",
            spacing="1"
        ),
        align_items="center",
        spacing="3"
    )

def input_form():
    """Create the input form for ingredient pricing."""
    return rx.vstack(
        rx.heading("Ingredient Pricing Calculator", size="6", color="#1e293b", margin_bottom="4"),
        
        # Ingredient Name Input
        rx.vstack(
            rx.text("Ingredient Name", font_weight="medium", color="#374151"),
            rx.input(
                placeholder="e.g., Nat Frozen Whole Chicken Griller Box",
                value=PricingState.ingredient_name,
                on_change=PricingState.set_ingredient_name,
                width="100%",
                padding="12px",
                border="1px solid #d1d5db",
                border_radius="8px",
                _focus={"border_color": "#3b82f6", "box_shadow": "0 0 0 3px rgba(59, 130, 246, 0.1)"}
            ),
            align_items="start",
            spacing="2",
            width="100%"
        ),
        
        # Quantity Input
        rx.vstack(
            rx.text("Quantity", font_weight="medium", color="#374151"),
            rx.input(
                placeholder="e.g., 10x1200g, 400g, 1.2kg",
                value=PricingState.quantity_input,
                on_change=PricingState.set_quantity_input,
                width="100%",
                padding="12px",
                border="1px solid #d1d5db",
                border_radius="8px",
                _focus={"border_color": "#3b82f6", "box_shadow": "0 0 0 3px rgba(59, 130, 246, 0.1)"}
            ),
            align_items="start",
            spacing="2",
            width="100%"
        ),
        
        # Price Input
        rx.vstack(
            rx.text("Price", font_weight="medium", color="#374151"),
            rx.input(
                placeholder="e.g., 132.25",
                value=PricingState.price_input,
                on_change=PricingState.set_price_input,
                width="100%",
                padding="12px",
                border="1px solid #d1d5db",
                border_radius="8px",
                _focus={"border_color": "#3b82f6", "box_shadow": "0 0 0 3px rgba(59, 130, 246, 0.1)"}
            ),
            align_items="start",
            spacing="2",
            width="100%"
        ),
        
        # Unit Selection Dropdown
        rx.vstack(
            rx.text("Output Unit", font_weight="medium", color="#374151"),
            rx.select(
                ["kg", "g", "mg"],
                value=PricingState.selected_unit,
                on_change=PricingState.set_selected_unit,
                width="100%",
                padding="12px",
                border="1px solid #d1d5db",
                border_radius="8px"
            ),
            align_items="start",
            spacing="2",
            width="100%"
        ),
        
        # Buttons
        rx.hstack(
            rx.button(
                "Calculate",
                on_click=PricingState.calculate_pricing,
                bg="#3b82f6",
                color="white",
                padding="12px 24px",
                border_radius="8px",
                font_weight="medium",
                _hover={"bg": "#2563eb"}
            ),
            rx.button(
                "Clear",
                on_click=PricingState.clear_form,
                bg="#6b7280",
                color="white",
                padding="12px 24px",
                border_radius="8px",
                font_weight="medium",
                _hover={"bg": "#4b5563"}
            ),
            spacing="3"
        ),
        
        # Error Message
        rx.cond(
            PricingState.error_message != "",
            rx.text(
                PricingState.error_message,
                color="#dc2626",
                font_weight="medium",
                padding="8px",
                bg="#fef2f2",
                border="1px solid #fecaca",
                border_radius="6px",
                width="100%"
            )
        ),
        
        spacing="4",
        width="100%",
        max_width="500px"
    )

def results_display():
    """Display calculation results."""
    return rx.cond(
        PricingState.results != {},
        rx.vstack(
            rx.heading("Results", size="5", color="#1e293b", margin_bottom="3"),
            
            # Main result based on selected unit
            rx.box(
                rx.vstack(
                    rx.text("Price per " + PricingState.selected_unit.upper(), font_weight="bold", color="#374151"),
                    rx.text(
                        rx.cond(
                            PricingState.selected_unit == "kg",
                            f"₹{PricingState.results.get('kg', 0):.2f}",
                            rx.cond(
                                PricingState.selected_unit == "g",
                                f"₹{PricingState.results.get('g', 0):.4f}",
                                f"₹{PricingState.results.get('mg', 0):.6f}"
                            )
                        ),
                        font_size="2xl",
                        font_weight="bold",
                        color="#059669"
                    ),
                    align_items="center",
                    spacing="2"
                ),
                bg="white",
                padding="20px",
                border_radius="12px",
                border="2px solid #10b981",
                width="100%"
            ),
            
            spacing="4",
            width="100%",
            max_width="500px"
        )
    )

def sidebar_results():
    """Display all unit variations in sidebar."""
    return rx.cond(
        PricingState.results != {},
        rx.vstack(
            rx.heading("All Variations", size="4", color="#1e293b", margin_bottom="3"),
            
            # Kilogram
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text("⚖️", font_size="lg"),
                        rx.text("Per KG", font_weight="medium", color="#374151"),
                        justify="start",
                        align_items="center",
                        spacing="2"
                    ),
                    rx.text(f"₹{PricingState.results.get('kg', 0):.2f}", font_weight="bold", color="#059669"),
                    align_items="start",
                    spacing="1"
                ),
                bg="white",
                padding="12px",
                border_radius="8px",
                border="1px solid #e5e7eb",
                width="100%"
            ),
            
            # Gram
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text("📏", font_size="lg"),
                        rx.text("Per Gram", font_weight="medium", color="#374151"),
                        justify="start",
                        align_items="center",
                        spacing="2"
                    ),
                    rx.text(f"₹{PricingState.results.get('g', 0):.4f}", font_weight="bold", color="#059669"),
                    align_items="start",
                    spacing="1"
                ),
                bg="white",
                padding="12px",
                border_radius="8px",
                border="1px solid #e5e7eb",
                width="100%"
            ),
            
            # Milligram
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text("🔬", font_size="lg"),
                        rx.text("Per Milligram", font_weight="medium", color="#374151"),
                        justify="start",
                        align_items="center",
                        spacing="2"
                    ),
                    rx.text(f"₹{PricingState.results.get('mg', 0):.6f}", font_weight="bold", color="#059669"),
                    align_items="start",
                    spacing="1"
                ),
                bg="white",
                padding="12px",
                border_radius="8px",
                border="1px solid #e5e7eb",
                width="100%"
            ),
            
            spacing="3",
            width="100%"
        )
    )

def index():
    """Main page layout."""
    return rx.box(
        rx.vstack(
            # Header with logo
            rx.box(
                create_logo(),
                width="100%",
                padding="20px",
                bg="white",
                border_bottom="1px solid #e5e7eb"
            ),
            
            # Main content
            rx.container(
                rx.hstack(
                    # Left side - Input form and main results
                    rx.vstack(
                        input_form(),
                        results_display(),
                        spacing="6",
                        align_items="start",
                        width="60%"
                    ),
                    
                    # Right side - All variations
                    rx.box(
                        sidebar_results(),
                        width="35%",
                        padding="20px",
                        bg="#f8fafc",
                        border_radius="12px",
                        min_height="400px"
                    ),
                    
                    spacing="5",
                    align_items="start",
                    width="100%"
                ),
                max_width="1200px",
                padding="40px 20px"
            ),
            
            # Footer
            rx.box(
                rx.text(
                    "Created by Sagar Singh | Mordor Intelligence",
                    color="#6b7280",
                    font_size="sm",
                    text_align="center"
                ),
                width="100%",
                padding="20px",
                bg="white",
                border_top="1px solid #e5e7eb"
            ),
            
            spacing="0",
            min_height="100vh",
            width="100%"
        ),
        bg="linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%)",
        min_height="100vh",
        width="100%"
    )

# Create the app
app = rx.App()
app.add_page(index, route="/")