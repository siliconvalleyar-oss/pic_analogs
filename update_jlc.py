#!/usr/bin/env python3
"""
Actualiza archivos .kicad_sch agregando campo JLCImport con part number de JLCPCB.
"""

import re
import sys

JLC_MAPPING = {
    "Device:R_US|10K": "C25804",
    "Device:R_US|10k": "C25804",
    "Device:R_US|2k2": "C25808",
    "Device:R_US|100": "C25797",
    "Device:R_US|27": "C25790",
    "Device:R_US|4K7": "C25802",
    "Device:R_US|1K": "C25800",
    "Device:R_Small_US|100": "C25797",
    "Device:R_Small_US|10k": "C25804",
    "Device:R_Small_US|1k": "C25800",
    "Device:R|100": "C25797",
    "Device:R|10K": "C25804",
    "Device:R|1K5": "C25801",
    "Device:R|27": "C25790",
    "Device:R|4K7": "C25802",
    "Device:C|100n": "C115188",
    "Device:C|100nf": "C115188",
    "Device:C|10n": "C115184",
    "Device:C|15p": "C115174",
    "Device:C|15pf": "C115174",
    "Device:C|33nf": "C115182",
    "MCU_Microchip_PIC18:PIC18F4550-IPT|PIC18F4550-IPT": "C420477",
    "Interface_USB:FT232BM|FT232BM": "C2882209",
    "Regulator_Linear:LM1117DT-3.3|LM1117DT-3.3": "C17654",
    "RF_ZigBee:MRF24J40MA|MRF24J40MA": "C423125",
    "Memory_EEPROM:25LCxxx|25LCxxx": "C173228",
    "FDN306P:FDN306P|FDN306P": "C436776",
    "Transistor_FET:2N7002|2N7002": "C436786",
    "Diode:1N4148W|1N4148W": "C423142",
    "Device:D_Shockley|ss2040": "C423158",
    "Device:LED|LED": "C423170",
    "Device:LED|LED_RD0": "C423170",
    "Device:LED|LED_RD1": "C423170",
    "Device:LED|LED_RD2": "C423170",
    "Device:LED|LED_RD3": "C423170",
    "Device:LED_Small|DBG": "C423170",
    "Device:LED_Small|RX": "C423170",
    "Device:FerriteBead|10M": "C173206",
    "Device:L|100mh": "C173214",
    "Device:L|L": "C173214",
    "Device:Crystal|6Mhz": "C423192",
    "Device:Crystal_GND24_Small|Crystal_GND24_Small": "C423192",
    "Switch:SW_Push_Dual_x2|mclr": "C423200",
    "Switch:SW_Push_Dual_x2|ra4": "C423200",
    "Switch:SW_Push_Dual_x2|ra5": "C423200",
    "Switch:SW_Push_Dual_x2|rb4": "C423200",
}

EXCLUDED = {
    "Connector:Conn_01x01_Pin", "Connector:Conn_01x04_Pin", 
    "Connector:Conn_01x06_Pin", "Connector:Conn_01x07_Pin",
    "Connector:Conn_01x14_Pin", "Connector:Conn_Coaxial",
    "Connector:F32R-1A7H1-11024", "Connector:Micro_SD_Card",
    "Connector:Raspberry_Pi_zero_2w", "Connector:USB_A",
    "Connector:USB_B_Mini", "Connector_Generic:Conn_01x02",
    "Connector_Generic:Conn_01x06",
    "Jumper:Jumper_2_Open", "Jumper:SolderJumper_2_Open",
    "Simulation_SPICE:PMOS",
    "power:+3.3V", "power:+3V3", "power:+5F", "power:+5V", "power:GND"
}

def get_jlc_part(lib_id, value):
    key = f"{lib_id}|{value}"
    if key in JLC_MAPPING:
        return JLC_MAPPING[key]
    if lib_id in EXCLUDED:
        return None
    return None

def add_jlc_field(content):
    """Agrega propiedad JLCImport a cada symbol instance que tenga mapeo."""
    
    # Pattern para encontrar cada symbol instance con sus propiedades
    # Buscamos: (symbol (lib_id "...") ... (property "Reference" "...") ... (property "Value" "...") ... )
    
    def replace_symbol(match):
        symbol_block = match.group(0)
        
        # Extraer lib_id
        lib_id_match = re.search(r'\(lib_id\s+"([^"]+)"\)', symbol_block)
        if not lib_id_match:
            return symbol_block
        lib_id = lib_id_match.group(1)
        
        # Extraer Value
        value_match = re.search(r'\(property\s+"Value"\s+"([^"]+)"', symbol_block)
        if not value_match:
            return symbol_block
        value = value_match.group(1)
        
        # Verificar si ya tiene JLCImport
        if 'JLCImport' in symbol_block:
            return symbol_block
        
        # Buscar JLC part
        jlc_part = get_jlc_part(lib_id, value)
        if not jlc_part:
            return symbol_block
        
        # Insertar propiedad JLCImport después de Value
        jlc_property = f'''		(property "JLCImport" "{jlc_part}"
			(at 0 0 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)'''
        
        # Insertar después de la propiedad Value
        symbol_block = re.sub(
            r'(\(property\s+"Value"\s+"[^"]+".*?\n\s+\))',
            r'\1\n' + jlc_property,
            symbol_block,
            flags=re.DOTALL
        )
        
        return symbol_block
    
    # Aplicar a cada symbol instance (no a definiciones de librería)
    # Las instancias están en la raíz del archivo, no dentro de lib_symbols
    # Pattern: (symbol (lib_id "...") ... ) que NO esté dentro de lib_symbols
    
    # Mejor: procesar solo la parte después de lib_symbols
    parts = content.split('(lib_symbols')
    if len(parts) < 2:
        return content
    
    header = parts[0]
    rest = '(lib_symbols' + '(lib_symbols'.join(parts[1:])
    
    # Procesar solo las instancias (después del cierre de lib_symbols)
    lib_end = rest.find(')\n)')
    if lib_end == -1:
        lib_end = rest.find(')')
    
    # Buscar el cierre real de lib_symbols
    paren_count = 0
    lib_end_pos = -1
    for i, ch in enumerate(rest):
        if ch == '(':
            paren_count += 1
        elif ch == ')':
            paren_count -= 1
            if paren_count == 0:
                lib_end_pos = i
                break
    
    if lib_end_pos == -1:
        return content
    
    lib_symbols_part = rest[:lib_end_pos+1]
    instances_part = rest[lib_end_pos+1:]
    
    # Procesar instancias
    # Cada instancia empieza con (symbol y tiene lib_id
    instance_pattern = r'\(symbol\s+\(lib_id\s+"[^"]+"\).*?\n\s+\)'
    instances_part = re.sub(instance_pattern, replace_symbol, instances_part, flags=re.DOTALL)
    
    return header + lib_symbols_part + instances_part

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    new_content = add_jlc_field(content)
    
    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Updated: {filepath}")
        return True
    else:
        print(f"No changes: {filepath}")
        return False

if __name__ == "__main__":
    files = [
        'ads1115.kicad_sch', 'buttons_rpi.kicad_sch', 'display_oled.kicad_sch',
        'epaper.kicad_sch', 'ft232.kicad_sch', 'magnetics.kicad_sch', 'mcu_pic.kicad_sch',
        'memory_spi.kicad_sch', 'micro_sd_card.kicad_sch', 'mrf24j40.kicad_sch',
        'oled_mcu.kicad_sch', 'rpi.kicad_sch', 'SWR_meter.kicad_sch'
    ]
    
    for f in files:
        process_file(f)
